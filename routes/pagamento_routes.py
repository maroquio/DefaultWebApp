"""
Rotas de pagamento para usuários autenticados.

Implementa o fluxo completo de Checkout Pro do Mercado Pago:
    1. GET  /pagamentos/listar          → Lista os pagamentos do usuário
    2. GET  /pagamentos/criar           → Formulário de novo pagamento
    3. POST /pagamentos/criar           → Cria preferência no MP e redireciona
    4. GET  /pagamentos/sucesso         → Página de retorno: pagamento aprovado
    5. GET  /pagamentos/pendente        → Página de retorno: pagamento pendente
    6. GET  /pagamentos/falha           → Página de retorno: pagamento recusado
    7. POST /pagamentos/webhook         → IPN do Mercado Pago (sem CSRF)
    8. GET  /pagamentos/{id}/detalhes   → Detalhes de um pagamento específico
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
from util.config import BASE_URL, IS_DEVELOPMENT
from util.datetime_util import agora
from util.exceptions import ErroValidacaoFormulario
from util.flash_messages import informar_erro, informar_sucesso
from util.logger_config import logger
from util.mercadopago_util import criar_preferencia, processar_webhook
from util.notificacao_util import criar_notificacao
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
    return templates.TemplateResponse(
        "pagamentos/criar.html",
        {"request": request, "usuario_logado": usuario_logado},
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
    Cria um novo pagamento e redireciona para o Checkout Pro do Mercado Pago.

    Fluxo:
        1. Valida os dados com CriarPagamentoDTO
        2. Insere pagamento no BD com status Pendente
        3. Cria preferência no Mercado Pago
        4. Atualiza pagamento com preference_id e url_checkout
        5. Redireciona o usuário para init_point (sandbox em dev, produção em prod)
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
        return templates.TemplateResponse(
            "pagamentos/criar.html",
            {"request": request, "dados": dados_formulario, "usuario_logado": usuario_logado},
        )

    # 1. Inserir pagamento com status Pendente
    pagamento = Pagamento(
        id=0,
        usuario_id=usuario_logado.id,
        descricao=dto.descricao,
        valor=dto.valor,
        status=StatusPagamento.PENDENTE,
    )
    pagamento_id = pagamento_repo.inserir(pagamento)

    if not pagamento_id:
        informar_erro(request, "Erro ao registrar pagamento. Tente novamente.")
        return RedirectResponse("/pagamentos/criar", status_code=status.HTTP_303_SEE_OTHER)

    # 2. Criar preferência no Mercado Pago
    back_urls = {
        "success": f"{BASE_URL}/pagamentos/sucesso",
        "pending": f"{BASE_URL}/pagamentos/pendente",
        "failure": f"{BASE_URL}/pagamentos/falha",
    }
    webhook_url = f"{BASE_URL}/pagamentos/webhook"

    resultado = criar_preferencia(
        descricao=dto.descricao,
        valor=dto.valor,
        pagamento_id=pagamento_id,
        back_urls=back_urls,
        webhook_url=webhook_url,
    )

    if not resultado:
        informar_erro(
            request,
            "Não foi possível conectar com o Mercado Pago. Verifique as configurações."
        )
        logger.error(f"Falha ao criar preferência MP para pagamento #{pagamento_id}")
        return RedirectResponse("/pagamentos/listar", status_code=status.HTTP_303_SEE_OTHER)

    # 3. Atualizar pagamento com os dados da preferência
    preference_id = resultado["preference_id"]
    # Em desenvolvimento usa sandbox_init_point; em produção usa init_point
    url_checkout = resultado["sandbox_init_point"] if IS_DEVELOPMENT else resultado["init_point"]

    pagamento_repo.atualizar_preference(
        id=pagamento_id,
        preference_id=preference_id,
        url_checkout=url_checkout,
    )

    logger.info(
        f"Pagamento #{pagamento_id} criado para usuário {usuario_logado.id}. "
        f"Preference: {preference_id}"
    )

    # 4. Redirecionar para o checkout do Mercado Pago
    return RedirectResponse(url_checkout, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/sucesso")
@requer_autenticacao()
async def sucesso(
    request: Request,
    payment_id: Optional[str] = None,
    preference_id: Optional[str] = None,
    external_reference: Optional[str] = None,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Página de retorno para pagamento aprovado.

    O Mercado Pago redireciona para esta URL com os parâmetros:
        ?collection_id=...&collection_status=approved&payment_id=...
        &status=approved&external_reference=...&preference_id=...
    """
    assert usuario_logado is not None

    pagamento = None

    # Tentar localizar o pagamento pelos parâmetros recebidos do MP
    if external_reference:
        pagamento = pagamento_repo.obter_por_external_reference(external_reference)
    elif preference_id:
        pagamento = pagamento_repo.obter_por_preference_id(preference_id)

    # Atualizar status para Aprovado se o pagamento foi encontrado
    if pagamento and pagamento.status != StatusPagamento.APROVADO:
        pagamento_id_bd = pagamento.id
        pagamento_repo.atualizar_status(
            id=pagamento_id_bd,
            status=StatusPagamento.APROVADO,
            payment_id=payment_id,
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
            logger.info(f"Pagamento #{pagamento.id} aprovado via retorno MP")

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
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Página de retorno para pagamento pendente."""
    assert usuario_logado is not None

    pagamento = None
    if external_reference:
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
            logger.info(f"Pagamento #{pagamento.id} em processamento via retorno MP")

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
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Página de retorno para pagamento recusado."""
    assert usuario_logado is not None

    pagamento = None
    if external_reference:
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
            logger.info(f"Pagamento #{pagamento.id} recusado via retorno MP")

    return templates.TemplateResponse(
        "pagamentos/falha.html",
        {"request": request, "pagamento": pagamento, "usuario_logado": usuario_logado},
    )


@router.post("/webhook")
async def webhook(request: Request):
    """
    Endpoint IPN (Instant Payment Notification) do Mercado Pago.

    O MP envia um POST para esta URL sempre que o status de um pagamento muda.
    Este endpoint é isento de CSRF (requisição externa do Mercado Pago).

    Importante:
        - Deve retornar HTTP 200 rapidamente para o MP não reenviar
        - A validação do status é feita consultando a API do MP (não confiamos
          apenas nos dados recebidos no body do webhook por segurança)
        - O external_reference é a chave primária para localizar o pagamento

    Formato do body (IPN v2):
        {"action": "payment.updated", "data": {"id": "1234567890"}, "type": "payment"}
    """
    try:
        dados = await request.json()
    except Exception:
        # Alguns webhooks do MP não enviam JSON, chegam como query params
        dados = dict(request.query_params)

    logger.debug(f"Webhook MP recebido: {dados}")

    resultado = processar_webhook(dados)
    if not resultado:
        # Não é uma notificação de pagamento — retornar 200 mesmo assim
        return {"status": "ignored"}

    external_reference = resultado.get("external_reference")
    payment_id = resultado.get("payment_id")
    status_sistema = resultado.get("status")

    if not external_reference:
        logger.warning(f"Webhook MP sem external_reference: {resultado}")
        return {"status": "ignored"}

    # Localizar o pagamento pela referência externa
    pagamento = pagamento_repo.obter_por_external_reference(external_reference)
    if not pagamento:
        logger.warning(f"Webhook MP: pagamento não encontrado para ref={external_reference}")
        return {"status": "not_found"}

    # Atualizar status no banco de dados
    try:
        novo_status = StatusPagamento(status_sistema)
    except ValueError:
        novo_status = StatusPagamento.PENDENTE
        logger.warning(f"Status desconhecido recebido no webhook: {status_sistema}")

    status_anterior = pagamento.status
    pagamento_repo.atualizar_status(
        id=pagamento.id,
        status=novo_status,
        payment_id=payment_id,
    )

    logger.info(
        f"Webhook MP: pagamento #{pagamento.id} status atualizado "
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
