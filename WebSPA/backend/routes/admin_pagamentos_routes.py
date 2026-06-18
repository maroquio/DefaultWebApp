"""
Rotas administrativas de pagamentos (API JSON).

Permite que administradores:
- Listem todos os pagamentos do sistema (paginado, com filtro opcional por status)
- Visualizem detalhes completos de qualquer pagamento, incluindo dados do provedor
"""

# =============================================================================
# Imports
# =============================================================================

from typing import Optional

from fastapi import APIRouter, Request, HTTPException, status

from dtos.responses.comum import PaginaResponse
from dtos.responses.pagamento_response import DadosProviderResponse, PagamentoResponse
from model.pagamento_model import StatusPagamento
from model.usuario_logado_model import UsuarioLogado
from repo import pagamento_repo
from util.auth_decorator import requer_autenticacao
from util.logger_config import logger
from util.paginacao_util import paginar
from util.payment_service import PaymentService
from util.perfis import Perfil

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/admin/pagamentos")


# =============================================================================
# Rotas (admin-only)
# =============================================================================


@router.get("", response_model=PaginaResponse[PagamentoResponse])
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(
    request: Request,
    status_filtro: Optional[str] = None,
    pagina: int = 1,
    por_pagina: int = 10,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Lista todos os pagamentos do sistema (paginado), com filtro opcional por status.

    Query params:
        status_filtro: Filtra por status (ex: ?status_filtro=Aprovado)
        pagina: Página atual (1-based)
        por_pagina: Itens por página
    """
    assert usuario_logado is not None

    todos_pagamentos = pagamento_repo.obter_todos()

    # Aplicar filtro por status se informado
    if status_filtro and StatusPagamento.existe(status_filtro):
        pagamentos = [p for p in todos_pagamentos if p.status.value == status_filtro]
    else:
        pagamentos = todos_pagamentos
        status_filtro = None

    paginacao = paginar(pagamentos, pagina, por_pagina)

    logger.info(
        f"Admin {usuario_logado.id} listou pagamentos "
        f"(filtro={status_filtro}, total={paginacao.total})"
    )

    items = [PagamentoResponse.de_pagamento(p) for p in paginacao.items]
    return PaginaResponse.de_paginacao(paginacao, items)


@router.get("/{id}", response_model=DadosProviderResponse)
@requer_autenticacao([Perfil.ADMIN.value])
async def detalhes(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exibe detalhes completos de um pagamento, incluindo dados do provedor."""
    assert usuario_logado is not None

    pagamento = pagamento_repo.obter_por_id(id)
    if not pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado.",
        )

    # Buscar dados atualizados no provedor que criou o pagamento (campo provider),
    # não no provedor ativo — preserva histórico ao trocar de provedor.
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

    provider_nome = PaymentService.obter_provider_por_chave(pagamento.provider).nome

    return DadosProviderResponse(
        pagamento=PagamentoResponse.de_pagamento(pagamento),
        provider_nome=provider_nome,
        dados_provider=dados_provider,
    )
