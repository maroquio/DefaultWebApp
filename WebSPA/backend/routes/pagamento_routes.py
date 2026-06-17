"""
Rotas de pagamento para usuários autenticados.

Implementa o fluxo completo de checkout multi-provedor:
    1. GET  /pagamentos/listar                  → Lista os pagamentos do usuário
    2. GET  /pagamentos/criar                   → Formulário de novo pagamento
    3. POST /pagamentos/criar                   → Cria checkout e redireciona
    4. GET  /pagamentos/sucesso                 → Página de retorno: pagamento aprovado
    5. GET  /pagamentos/pendente                → Página de retorno: pagamento pendente
    6. GET  /pagamentos/falha                   → Página de retorno: pagamento recusado
    7. POST /pagamentos/webhook/mercadopago     → IPN do Mercado Pago (sem CSRF)
    8. POST /pagamentos/webhook/stripe          → Webhook Stripe com validação de assinatura
    9. GET  /pagamentos/{id}/detalhes           → Detalhes de um pagamento específico
"""

# =============================================================================
# Imports
# =============================================================================

from typing import Optional

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.pagamento_dto import CriarPagamentoDTO
from model.notificacao_model import TipoNotificacao
from model.pagamento_model import Pagamento, StatusPagamento
from model.usuario_logado_model import UsuarioLogado
from repo import pagamento_repo
from util.auth_decorator import requer_autenticacao
from util.config import BASE_URL
from util.exceptions import ErroValidacaoFormulario
from util.flash_messages import informar_erro, informar_sucesso
from util.logger_config import logger
from util.notificacao_util import criar_notificacao
from util.payment_service import PaymentService
from util.permission_helpers import verificar_propriedade
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.repository_helpers import obter_ou_404
from util.template_util import criar_templates

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/pagamentos")
templates = criar_templates()

# =============================================================================
# Rate Limiters
# =============================================================================

pagamento_criar_limiter = DynamicRateLimiter(
    chave_max="rate_limit_pagamento_criar_max",
    chave_minutos="rate_limit_pagamento_criar_minutos",
    padrao_max=10,
    padrao_minutos=10,
    nome="pagamento_criar",
)


# =============================================================================
# Rotas
# =============================================================================


@router.get("/listar")
@requer_autenticacao()
async def listar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Lista todos os pagamentos do usuário logado."""
    assert usuario_logado is not None
    pagamentos = pagamento_repo.obter_por_usuario(usuario_logado.id)
    return templates.TemplateResponse(
        "pagamentos/listar.html",
        {"request": request, "pagamentos": pagamentos, "usuario_logado": usuario_logado},
    )


@router.get("/criar")
@requer_autenticacao()
async def get_criar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe formulário de criação de pagamento."""
    assert usuario_logado is not None
    provider = PaymentService.obter_provider()
    return templates.TemplateResponse(
        "pagamentos/criar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "provider_nome": provider.nome,
        },
    )


@router.post("/criar")
@requer_autenticacao()
async def post_criar(
    request: Request,
    descricao: str = Form(),
    valor: str = Form(),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Cria um novo pagamento e redireciona para o checkout do provedor configurado.

    Fluxo:
        1. Valida os dados com CriarPagamentoDTO
        2. Obtém o provider ativo via PaymentService
        3. Insere pagamento no BD com status Pendente e provider registrado
        4. Cria checkout no provedor (preferência MP ou Checkout Session Stripe)
        5. Atualiza pagamento com reference_id e url_checkout
        6. Redireciona o usuário para checkout_url
    """
    assert usuario_logado is not None

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not pagamento_criar_limiter.verificar(ip):
        informar_erro(request, "Muitas tentativas. Aguarde alguns minutos.")
        logger.warning(f"Rate limit excedido para criação de pagamento - IP: {ip}")
        return RedirectResponse("/pagamentos/criar", status_code=status.HTTP_303_SEE_OTHER)

    # Converter vírgula para ponto (formato brasileiro → float)
    valor_normalizado = valor.replace(",", ".")
    dados_formulario = {"descricao": descricao, "valor": valor}

    try:
        dto = CriarPagamentoDTO(descricao=descricao, valor=float(valor_normalizado))
    except (ValueError, ValidationError) as e:
        if isinstance(e, ValidationError):
            raise ErroValidacaoFormulario(
                validation_error=e,
                template_path="pagamentos/criar.html",
                dados_formulario=dados_formulario,
                campo_padrao="descricao",
            )
        informar_erro(request, "Valor inválido. Use o formato: 29.90 ou 29,90")
        provider = PaymentService.obter_provider()
        return templates.TemplateResponse(
            "pagamentos/criar.html",
            {
                "request": request,
                "dados": dados_formulario,
                "usuario_logado": usuario_logado,
                "provider_nome": provider.nome,
            },
        )

    # Obter provedor ativo
    provider = PaymentService.obter_provider()

    # 1. Inserir pagamento com status Pendente e provider registrado
    pagamento = Pagamento(
        id=0,
        usuario_id=usuario_logado.id,
        descricao=dto.descricao,
        valor=dto.valor,
        status=StatusPagamento.PENDENTE,
        provider=provider.chave,
    )
    pagamento_id = pagamento_repo.inserir(pagamento)

    if not pagamento_id:
        informar_erro(request, "Erro ao registrar pagamento. Tente novamente.")
        return RedirectResponse("/pagamentos/criar", status_code=status.HTTP_303_SEE_OTHER)

    # 2. Criar checkout no provedor
    back_urls = {
        "success": f"{BASE_URL}/pagamentos/sucesso",
        "pending": f"{BASE_URL}/pagamentos/pendente",
        "failure": f"{BASE_URL}/pagamentos/falha",
    }
    webhook_url = f"{BASE_URL}/pagamentos/webhook/{provider.chave}"

    resultado = provider.criar_checkout(
        descricao=dto.descricao,
        valor=dto.valor,
        pagamento_id=pagamento_id,
        back_urls=back_urls,
        webhook_url=webhook_url,
    )

    if not resultado:
        informar_erro(
            request,
            f"Não foi possível conectar com o {provider.nome}. Verifique as configurações."
        )
        logger.error(f"Falha ao criar checkout {provider.chave} para pagamento #{pagamento_id}")
        return RedirectResponse("/pagamentos/listar", status_code=status.HTTP_303_SEE_OTHER)

    # 3. Atualizar pagamento com os dados do checkout
    pagamento_repo.atualizar_checkout(
        id=pagamento_id,
        preference_id=resultado["reference_id"],
        url_checkout=resultado["checkout_url"],
    )

    logger.info(
        f"Pagamento #{pagamento_id} criado via {provider.chave} para usuário {usuario_logado.id}. "
        f"Reference: {resultado['reference_id']}"
    )

    # 4. Redirecionar para o checkout do provedor
    return RedirectResponse(resultado["checkout_url"], status_code=status.HTTP_303_SEE_OTHER)


@router.get("/sucesso")
@requer_autenticacao()
async def sucesso(
    request: Request,
    # Parâmetros Mercado Pago
    payment_id: Optional[str] = None,
    preference_id: Optional[str] = None,
    external_reference: Optional[str] = None,
    # Parâmetros Stripe
    pagamento_id: Optional[int] = None,
    session_id: Optional[str] = None,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Página de retorno para pagamento aprovado.

    Aceita parâmetros de ambos os provedores:
    - Mercado Pago: ?external_reference=...&preference_id=...&payment_id=...
    - Stripe: ?pagamento_id=...&session_id=...
    """
    assert usuario_logado is not None

    pagamento = None

    # Tentar localizar o pagamento — Stripe passa pagamento_id direto
    if pagamento_id:
        pagamento = pagamento_repo.obter_por_id(pagamento_id)
    elif external_reference:
        pagamento = pagamento_repo.obter_por_external_reference(external_reference)
    elif preference_id:
        pagamento = pagamento_repo.obter_por_preference_id(preference_id)
    elif session_id:
        pagamento = pagamento_repo.obter_por_preference_id(session_id)

    # Atualizar status para Aprovado se o pagamento foi encontrado
    if pagamento and pagamento.status != StatusPagamento.APROVADO:
        pagamento_id_bd = pagamento.id
        pagamento_repo.atualizar_status(
            id=pagamento_id_bd,
            status=StatusPagamento.APROVADO,
            payment_id=payment_id or session_id,
        )
        # Recarregar para exibir status atualizado
        pagamento = pagamento_repo.obter_por_id(pagamento_id_bd)

        if pagamento:
            criar_notificacao(
                usuario_id=pagamento.usuario_id,
                titulo="Pagamento aprovado!",
                mensagem=f"Seu pagamento de R$ {pagamento.valor:.2f} ({pagamento.descricao}) foi aprovado.",
                tipo=TipoNotificacao.SUCESSO,
                url_acao=f"/pagamentos/{pagamento.id}/detalhes",
            )
            logger.info(f"Pagamento #{pagamento.id} aprovado via retorno {pagamento.provider}")

    return templates.TemplateResponse(
        "pagamentos/sucesso.html",
        {"request": request, "pagamento": pagamento, "usuario_logado": usuario_logado},
    )


@router.get("/pendente")
@requer_autenticacao()
async def pendente(
    request: Request,
    payment_id: Optional[str] = None,
    preference_id: Optional[str] = None,
    external_reference: Optional[str] = None,
    pagamento_id: Optional[int] = None,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Página de retorno para pagamento pendente."""
    assert usuario_logado is not None

    pagamento = None
    if pagamento_id:
        pagamento = pagamento_repo.obter_por_id(pagamento_id)
    elif external_reference:
        pagamento = pagamento_repo.obter_por_external_reference(external_reference)
    elif preference_id:
        pagamento = pagamento_repo.obter_por_preference_id(preference_id)

    if pagamento and pagamento.status == StatusPagamento.PENDENTE:
        pagamento_id_bd = pagamento.id
        pagamento_repo.atualizar_status(
            id=pagamento_id_bd,
            status=StatusPagamento.EM_PROCESSAMENTO,
            payment_id=payment_id,
        )
        pagamento = pagamento_repo.obter_por_id(pagamento_id_bd)
        if pagamento:
            logger.info(f"Pagamento #{pagamento.id} em processamento via retorno {pagamento.provider}")

    return templates.TemplateResponse(
        "pagamentos/pendente.html",
        {"request": request, "pagamento": pagamento, "usuario_logado": usuario_logado},
    )


@router.get("/falha")
@requer_autenticacao()
async def falha(
    request: Request,
    payment_id: Optional[str] = None,
    preference_id: Optional[str] = None,
    external_reference: Optional[str] = None,
    pagamento_id: Optional[int] = None,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Página de retorno para pagamento recusado."""
    assert usuario_logado is not None

    pagamento = None
    if pagamento_id:
        pagamento = pagamento_repo.obter_por_id(pagamento_id)
    elif external_reference:
        pagamento = pagamento_repo.obter_por_external_reference(external_reference)
    elif preference_id:
        pagamento = pagamento_repo.obter_por_preference_id(preference_id)

    if pagamento and pagamento.status not in (StatusPagamento.RECUSADO, StatusPagamento.CANCELADO):
        pagamento_id_bd = pagamento.id
        pagamento_repo.atualizar_status(
            id=pagamento_id_bd,
            status=StatusPagamento.RECUSADO,
            payment_id=payment_id,
        )
        pagamento = pagamento_repo.obter_por_id(pagamento_id_bd)

        if pagamento:
            criar_notificacao(
                usuario_id=pagamento.usuario_id,
                titulo="Pagamento não aprovado",
                mensagem=f"Seu pagamento de R$ {pagamento.valor:.2f} não foi aprovado. Tente novamente.",
                tipo=TipoNotificacao.AVISO,
                url_acao=f"/pagamentos/{pagamento.id}/detalhes",
            )
            logger.info(f"Pagamento #{pagamento.id} recusado via retorno {pagamento.provider}")

    return templates.TemplateResponse(
        "pagamentos/falha.html",
        {"request": request, "pagamento": pagamento, "usuario_logado": usuario_logado},
    )


@router.get("/paypal/capturar")
@requer_autenticacao()
async def paypal_capturar(
    request: Request,
    pagamento_id: int,
    token: str,  # PayPal order_id recebido na return_url
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Captura a Order PayPal após o usuário aprovar no site do PayPal.

    PayPal redireciona para esta URL com:
        ?pagamento_id=X&token=ORDER_ID

    O `token` é o order_id do PayPal. Precisamos capturá-lo para confirmar
    o pagamento — sem este passo o dinheiro não é transferido.
    """
    assert usuario_logado is not None
    from util.payment_adapters.paypal_adapter import PayPalAdapter

    pagamento = pagamento_repo.obter_por_id(pagamento_id)
    if not pagamento:
        informar_erro(request, "Pagamento não encontrado.")
        return RedirectResponse("/pagamentos/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Atualizar o order_id como preference_id caso ainda não esteja salvo
    if not pagamento.preference_id:
        pagamento_repo.atualizar_checkout(
            id=pagamento_id,
            preference_id=token,
            url_checkout=pagamento.url_checkout or "",
        )

    adapter = PayPalAdapter()
    resultado = adapter.capturar_ordem(token)

    if resultado and resultado.get("status") in ("COMPLETED", "APPROVED"):
        capture_id = resultado.get("capture_id") or token
        pagamento_repo.atualizar_status(
            id=pagamento_id,
            status=StatusPagamento.APROVADO,
            payment_id=capture_id,
        )
        criar_notificacao(
            usuario_id=pagamento.usuario_id,
            titulo="Pagamento aprovado!",
            mensagem=f"Seu pagamento de R$ {pagamento.valor:.2f} ({pagamento.descricao}) foi aprovado via PayPal.",
            tipo=TipoNotificacao.SUCESSO,
            url_acao=f"/pagamentos/{pagamento.id}/detalhes",
        )
        logger.info(f"PayPal: pagamento #{pagamento_id} capturado com sucesso (capture_id={capture_id})")
        return RedirectResponse(
            f"/pagamentos/sucesso?pagamento_id={pagamento_id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    else:
        pagamento_repo.atualizar_status(id=pagamento_id, status=StatusPagamento.RECUSADO)
        informar_erro(request, "Pagamento não foi concluído no PayPal.")
        logger.warning(f"PayPal: captura falhou para pagamento #{pagamento_id}: {resultado}")
        return RedirectResponse(
            f"/pagamentos/falha?pagamento_id={pagamento_id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )


@router.post("/webhook/mercadopago")
async def webhook_mercadopago(request: Request):
    """
    Endpoint IPN (Instant Payment Notification) do Mercado Pago.

    Isento de CSRF — requisição externa do Mercado Pago.
    Sempre retorna HTTP 200 rapidamente para evitar reenvios.

    Formato do body (IPN v2):
        {"action": "payment.updated", "data": {"id": "1234567890"}, "type": "payment"}
    """
    from util.payment_adapters.mercadopago_adapter import MercadoPagoAdapter

    payload = await request.body()
    logger.debug(f"Webhook MercadoPago recebido: {payload[:200]}")

    adapter = MercadoPagoAdapter()
    resultado = adapter.processar_webhook(payload, dict(request.headers))

    if not resultado:
        return {"status": "ignored"}

    return _processar_resultado_webhook(resultado, "mercadopago")


@router.post("/webhook/stripe")
async def webhook_stripe(request: Request):
    """
    Endpoint de webhook do Stripe com validação de assinatura.

    Isento de CSRF — requisição externa do Stripe.
    A assinatura é validada com STRIPE_WEBHOOK_SECRET no adapter.

    Testar localmente com Stripe CLI:
        stripe listen --forward-to localhost:8400/pagamentos/webhook/stripe
    """
    from util.payment_adapters.stripe_adapter import StripeAdapter

    payload = await request.body()
    logger.debug(f"Webhook Stripe recebido, tamanho={len(payload)} bytes")

    adapter = StripeAdapter()
    resultado = adapter.processar_webhook(payload, dict(request.headers))

    if not resultado:
        return {"status": "ignored"}

    return _processar_resultado_webhook(resultado, "stripe")


def _processar_resultado_webhook(resultado: dict, provider: str) -> dict:
    """
    Lógica comum de atualização de status após processar webhook.

    Localiza o pagamento no banco (por pagamento_id ou reference_id),
    atualiza o status e cria notificação in-app se aprovado.

    Args:
        resultado: Dict retornado pelo adapter.processar_webhook()
        provider: Chave do provedor ('mercadopago', 'stripe')

    Returns:
        Dict com status da operação
    """
    pagamento_id = resultado.get("pagamento_id")
    provider_payment_id = resultado.get("provider_payment_id")
    reference_id = resultado.get("reference_id")
    status_sistema = resultado.get("status")

    # Localizar o pagamento
    pagamento = None

    if pagamento_id:
        pagamento = pagamento_repo.obter_por_id(pagamento_id)
    elif reference_id:
        pagamento = pagamento_repo.obter_por_provider_reference(provider, reference_id)
    elif provider_payment_id:
        pagamento = pagamento_repo.obter_por_preference_id(provider_payment_id)

    if not pagamento:
        logger.warning(
            f"Webhook {provider}: pagamento não encontrado. "
            f"pagamento_id={pagamento_id}, reference_id={reference_id}"
        )
        return {"status": "not_found"}

    # Atualizar status no banco de dados
    try:
        novo_status = StatusPagamento(status_sistema)
    except ValueError:
        novo_status = StatusPagamento.PENDENTE
        logger.warning(f"Webhook {provider}: status desconhecido '{status_sistema}'")

    status_anterior = pagamento.status
    pagamento_repo.atualizar_status(
        id=pagamento.id,
        status=novo_status,
        payment_id=provider_payment_id,
    )

    logger.info(
        f"Webhook {provider}: pagamento #{pagamento.id} "
        f"{status_anterior.value} → {novo_status.value}"
    )

    # Criar notificação in-app quando aprovado via webhook
    if novo_status == StatusPagamento.APROVADO and status_anterior != StatusPagamento.APROVADO:
        criar_notificacao(
            usuario_id=pagamento.usuario_id,
            titulo="Pagamento confirmado!",
            mensagem=f"Seu pagamento de R$ {pagamento.valor:.2f} ({pagamento.descricao}) foi confirmado.",
            tipo=TipoNotificacao.SUCESSO,
            url_acao=f"/pagamentos/{pagamento.id}/detalhes",
        )

    return {"status": "ok"}


@router.post("/webhook/paypal")
async def webhook_paypal(request: Request):
    """
    Endpoint de webhook do PayPal.

    Isento de CSRF — requisição externa do PayPal.
    A assinatura é verificada via API do PayPal se PAYPAL_WEBHOOK_ID estiver configurado.
    """
    from util.payment_adapters.paypal_adapter import PayPalAdapter

    payload = await request.body()
    logger.debug(f"Webhook PayPal recebido, tamanho={len(payload)} bytes")

    adapter = PayPalAdapter()
    resultado = adapter.processar_webhook(payload, dict(request.headers))

    if not resultado:
        return {"status": "ignored"}

    return _processar_resultado_webhook(resultado, "paypal")


@router.get("/{id}/detalhes")
@requer_autenticacao()
async def detalhes(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exibe os detalhes de um pagamento específico do usuário."""
    assert usuario_logado is not None

    pagamento = obter_ou_404(
        pagamento_repo.obter_por_id(id),
        request,
        "Pagamento não encontrado",
        "/pagamentos/listar",
    )
    if isinstance(pagamento, RedirectResponse):
        return pagamento

    # Verificar se o usuário é dono do pagamento (ou admin)
    if not usuario_logado.is_admin():
        if not verificar_propriedade(
            pagamento,
            usuario_logado.id,
            request,
            "Você não tem permissão para ver este pagamento",
            "/pagamentos/listar",
        ):
            return RedirectResponse("/pagamentos/listar", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "pagamentos/detalhes.html",
        {"request": request, "pagamento": pagamento, "usuario_logado": usuario_logado},
    )
