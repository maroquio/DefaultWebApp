"""
Rotas administrativas para gerenciamento de pagamentos.

Permite que administradores:
- Listem todos os pagamentos do sistema com filtros por status
- Visualizem detalhes completos de qualquer pagamento, incluindo dados do provedor
"""

# =============================================================================
# Imports
# =============================================================================

from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from model.pagamento_model import StatusPagamento
from model.usuario_logado_model import UsuarioLogado
from repo import pagamento_repo
from util.auth_decorator import requer_autenticacao
from util.logger_config import logger
from util.payment_service import PaymentService
from util.perfis import Perfil
from util.repository_helpers import obter_ou_404
from util.template_util import criar_templates

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/admin/pagamentos")
templates = criar_templates()


# =============================================================================
# Rotas
# =============================================================================


@router.get("")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(
    request: Request,
    status_filtro: Optional[str] = None,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Lista todos os pagamentos do sistema com filtro opcional por status.

    Query params:
        status_filtro: Filtrar por status (ex: ?status_filtro=Aprovado)
    """
    assert usuario_logado is not None

    todos_pagamentos = pagamento_repo.obter_todos()

    # Aplicar filtro por status se informado
    if status_filtro and StatusPagamento.existe(status_filtro):
        pagamentos = [p for p in todos_pagamentos if p.status.value == status_filtro]
    else:
        pagamentos = todos_pagamentos
        status_filtro = None

    # Calcular totais por status para o painel de resumo
    totais: dict[str, int] = {}
    for p in todos_pagamentos:
        chave = p.status.value
        totais[chave] = totais.get(chave, 0) + 1

    logger.info(
        f"Admin {usuario_logado.id} listou pagamentos "
        f"(filtro={status_filtro}, total={len(pagamentos)})"
    )

    return templates.TemplateResponse(
        "admin/pagamentos/listar.html",
        {
            "request": request,
            "pagamentos": pagamentos,
            "status_filtro": status_filtro,
            "totais": totais,
            "status_opcoes": StatusPagamento.valores(),
            "usuario_logado": usuario_logado,
        },
    )


@router.get("/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def detalhes(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exibe detalhes completos de um pagamento, incluindo dados do provedor."""
    assert usuario_logado is not None

    pagamento = obter_ou_404(
        pagamento_repo.obter_por_id(id),
        request,
        "Pagamento não encontrado",
        "/admin/pagamentos",
    )
    if isinstance(pagamento, RedirectResponse):
        return pagamento

    # Buscar dados atualizados no provedor se houver payment_id confirmado
    # Usa o adapter do provedor que criou o pagamento (campo provider),
    # não o provedor ativo — preserva histórico ao trocar de provedor.
    dados_provider = None
    if pagamento.payment_id:
        try:
            adapter = PaymentService.obter_provider_por_chave(pagamento.provider)
            dados_provider = adapter.obter_dados_pagamento(pagamento.payment_id)
        except Exception as e:
            logger.warning(
                f"Não foi possível consultar dados do provider {pagamento.provider} "
                f"para pagamento #{pagamento.id}: {e}"
            )

    # Obter nome do provedor para exibição
    provider_nome = PaymentService.obter_provider_por_chave(pagamento.provider).nome

    return templates.TemplateResponse(
        "admin/pagamentos/detalhes.html",
        {
            "request": request,
            "pagamento": pagamento,
            "dados_provider": dados_provider,
            "provider_nome": provider_nome,
            "usuario_logado": usuario_logado,
        },
    )
