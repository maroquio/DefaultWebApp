"""
Rotas de pagamento (API JSON) para usuários autenticados.

Fluxo SPA (Checkout Pro / multi-provedor):
    1. GET  /pagamentos              → Lista os pagamentos do usuário logado
    2. POST /pagamentos              → Cria checkout e RETORNA {init_point, pagamento_id}
                                       (o React faz window.location — sem redirect no backend)
    3. GET  /pagamentos/{id}         → Status real de um pagamento (do próprio usuário)
    4. POST /pagamentos/webhook/{provedor} → Notificações server-to-server (sem auth/CSRF)

As páginas Jinja de retorno (sucesso/pendente/falha) deixam de existir no backend:
viraram rotas do SPA. A confirmação de status passa a ser responsabilidade do webhook
(fonte da verdade) e do polling em GET /pagamentos/{id}.
"""

# =============================================================================
# Imports
# =============================================================================

from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status

from dtos.pagamento_dto import CriarPagamentoDTO
from dtos.responses.pagamento_response import (
    CriarPagamentoResultadoResponse,
    PagamentoResponse,
)
from model.notificacao_model import TipoNotificacao
from model.pagamento_model import Pagamento, StatusPagamento
from model.usuario_logado_model import UsuarioLogado
from repo import pagamento_repo
from util.api_helpers import checar_rate_limit
from util.auth_decorator import requer_autenticacao
from util.config import BASE_URL
from util.logger_config import logger
from util.notificacao_util import criar_notificacao
from util.payment_service import PaymentService
from util.rate_limiter import DynamicRateLimiter

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/pagamentos")

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
# Rotas do usuário
# =============================================================================


@router.get("", response_model=list[PagamentoResponse])
@requer_autenticacao()
async def listar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Lista todos os pagamentos do usuário logado."""
    assert usuario_logado is not None
    pagamentos = pagamento_repo.obter_por_usuario(usuario_logado.id)
    return [PagamentoResponse.de_pagamento(p) for p in pagamentos]


@router.post(
    "",
    response_model=CriarPagamentoResultadoResponse,
    status_code=status.HTTP_201_CREATED,
)
@requer_autenticacao()
async def criar(
    request: Request,
    dto: CriarPagamentoDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Cria um pagamento e retorna a URL de checkout do provedor ativo.

    O backend NÃO redireciona: devolve ``init_point`` para o SPA executar
    ``window.location``. Em desenvolvimento usa o checkout sandbox; em produção
    usa o checkout real (lógica IS_DEVELOPMENT preservada via adapter).

    Fluxo:
        1. Obtém o provider ativo via PaymentService
        2. Insere o pagamento com status Pendente e provider registrado
        3. Cria o checkout no provedor (preferência MP / Checkout Session Stripe)
        4. Atualiza o pagamento com reference_id e url_checkout
        5. Retorna {init_point, pagamento_id}
    """
    assert usuario_logado is not None
    checar_rate_limit(pagamento_criar_limiter, request)

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar pagamento. Tente novamente.",
        )

    # 2. Criar checkout no provedor. As back_urls apontam para rotas do SPA.
    back_urls = {
        "success": f"{BASE_URL}/pagamentos/sucesso",
        "pending": f"{BASE_URL}/pagamentos/pendente",
        "failure": f"{BASE_URL}/pagamentos/falha",
    }
    webhook_url = f"{BASE_URL}/api/pagamentos/webhook/{provider.chave}"

    resultado = provider.criar_checkout(
        descricao=dto.descricao,
        valor=dto.valor,
        pagamento_id=pagamento_id,
        back_urls=back_urls,
        webhook_url=webhook_url,
    )

    if not resultado:
        logger.error(
            f"Falha ao criar checkout {provider.chave} para pagamento #{pagamento_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                f"Não foi possível conectar com o {provider.nome}. "
                "Verifique as configurações e tente novamente."
            ),
        )

    # 3. Atualizar pagamento com os dados do checkout
    pagamento_repo.atualizar_checkout(
        id=pagamento_id,
        preference_id=resultado["reference_id"],
        url_checkout=resultado["checkout_url"],
    )

    logger.info(
        f"Pagamento #{pagamento_id} criado via {provider.chave} para usuário "
        f"{usuario_logado.id}. Reference: {resultado['reference_id']}"
    )

    # 4. Devolver init_point para o SPA redirecionar
    return CriarPagamentoResultadoResponse(
        init_point=resultado["checkout_url"],
        pagamento_id=pagamento_id,
    )


@router.get("/{id}", response_model=PagamentoResponse)
@requer_autenticacao()
async def obter(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Retorna o status real de um pagamento específico.

    Usado pelo SPA para polling após o retorno do checkout. O dono do
    pagamento (ou um admin) pode consultá-lo; caso contrário, 404.
    """
    assert usuario_logado is not None

    pagamento = pagamento_repo.obter_por_id(id)
    if not pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado.",
        )

    # Permissão: dono do pagamento ou admin (admin vê todos)
    if not usuario_logado.is_admin() and pagamento.usuario_id != usuario_logado.id:
        # 404 para não revelar a existência do recurso a terceiros
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado.",
        )

    return PagamentoResponse.de_pagamento(pagamento)


@router.post("/{id}/paypal/capturar", response_model=PagamentoResponse)
@requer_autenticacao()
async def paypal_capturar(
    request: Request,
    id: int,
    token: str,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Captura uma Order PayPal após o usuário aprová-la.

    Substitui o antigo GET de retorno: no SPA, o PayPal redireciona o usuário
    para uma rota do front com ``?token=ORDER_ID``; o front então chama este
    endpoint para efetivar a cobrança (sem a captura o dinheiro não é transferido).

    ``token`` é o order_id do PayPal. Retorna o pagamento já atualizado.
    """
    assert usuario_logado is not None
    from util.payment_adapters.paypal_adapter import PayPalAdapter

    pagamento = pagamento_repo.obter_por_id(id)
    if not pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado.",
        )

    if not usuario_logado.is_admin() and pagamento.usuario_id != usuario_logado.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado.",
        )

    # Registrar o order_id como preference_id caso ainda não esteja salvo
    if not pagamento.preference_id:
        pagamento_repo.atualizar_checkout(
            id=id,
            preference_id=token,
            url_checkout=pagamento.url_checkout or "",
        )

    adapter = PayPalAdapter()
    resultado = adapter.capturar_ordem(token)

    if resultado and resultado.get("status") in ("COMPLETED", "APPROVED"):
        capture_id = resultado.get("capture_id") or token
        pagamento_repo.atualizar_status(
            id=id,
            status=StatusPagamento.APROVADO,
            payment_id=capture_id,
        )
        criar_notificacao(
            usuario_id=pagamento.usuario_id,
            titulo="Pagamento aprovado!",
            mensagem=(
                f"Seu pagamento de R$ {pagamento.valor:.2f} "
                f"({pagamento.descricao}) foi aprovado via PayPal."
            ),
            tipo=TipoNotificacao.SUCESSO,
            url_acao=f"/pagamentos/{pagamento.id}",
        )
        logger.info(
            f"PayPal: pagamento #{id} capturado com sucesso (capture_id={capture_id})"
        )
        return PagamentoResponse.de_pagamento(pagamento_repo.obter_por_id(id))

    pagamento_repo.atualizar_status(id=id, status=StatusPagamento.RECUSADO)
    logger.warning(f"PayPal: captura falhou para pagamento #{id}: {resultado}")
    raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail="Pagamento não foi concluído no PayPal.",
    )


# =============================================================================
# Webhooks (server-to-server) — SEM auth, SEM response_model, SEM CSRF.
# Os paths sob /api/pagamentos/webhook já estão isentos de CSRF no middleware.
# Sempre retornam HTTP 200 rapidamente para evitar reenvios do provedor.
# =============================================================================


@router.post("/webhook/mercadopago")
async def webhook_mercadopago(request: Request):
    """
    Endpoint IPN (Instant Payment Notification) do Mercado Pago.

    Fonte da verdade do status. Formato do body (IPN v2):
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

    A assinatura é validada com STRIPE_WEBHOOK_SECRET no adapter.

    Testar localmente com Stripe CLI:
        stripe listen --forward-to localhost:8400/api/pagamentos/webhook/stripe
    """
    from util.payment_adapters.stripe_adapter import StripeAdapter

    payload = await request.body()
    logger.debug(f"Webhook Stripe recebido, tamanho={len(payload)} bytes")

    adapter = StripeAdapter()
    resultado = adapter.processar_webhook(payload, dict(request.headers))

    if not resultado:
        return {"status": "ignored"}

    return _processar_resultado_webhook(resultado, "stripe")


@router.post("/webhook/paypal")
async def webhook_paypal(request: Request):
    """
    Endpoint de webhook do PayPal.

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


def _processar_resultado_webhook(resultado: dict, provider: str) -> dict:
    """
    Lógica comum de atualização de status após processar um webhook.

    Localiza o pagamento (por pagamento_id ou reference_id), atualiza o status
    e cria notificação in-app quando aprovado. Sempre retorna um dict simples
    com o resultado da operação (HTTP 200).
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
    if (
        novo_status == StatusPagamento.APROVADO
        and status_anterior != StatusPagamento.APROVADO
    ):
        criar_notificacao(
            usuario_id=pagamento.usuario_id,
            titulo="Pagamento confirmado!",
            mensagem=(
                f"Seu pagamento de R$ {pagamento.valor:.2f} "
                f"({pagamento.descricao}) foi confirmado."
            ),
            tipo=TipoNotificacao.SUCESSO,
            url_acao=f"/pagamentos/{pagamento.id}",
        )

    return {"status": "ok"}
