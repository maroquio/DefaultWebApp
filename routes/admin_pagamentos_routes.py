"""
Rotas administrativas para gerenciamento de pagamentos.

Permite que administradores:
- Listem todos os pagamentos do sistema com filtros por status
- Visualizem detalhes completos de qualquer pagamento
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
    """Exibe detalhes completos de um pagamento, incluindo dados do Mercado Pago."""
    assert usuario_logado is not None

    pagamento = obter_ou_404(
        pagamento_repo.obter_por_id(id),
        request,
        "Pagamento não encontrado",
        "/admin/pagamentos",
    )
    if isinstance(pagamento, RedirectResponse):
        return pagamento

    # Buscar dados atualizados no Mercado Pago se houver payment_id confirmado
    dados_mp = None
    if pagamento.payment_id:
        from util.mercadopago_util import obter_pagamento_mp
        dados_mp = obter_pagamento_mp(pagamento.payment_id)

    return templates.TemplateResponse(
        "admin/pagamentos/detalhes.html",
        {
            "request": request,
            "pagamento": pagamento,
            "dados_mp": dados_mp,
            "usuario_logado": usuario_logado,
        },
    )
