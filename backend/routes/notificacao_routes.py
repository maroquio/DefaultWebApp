"""
Rotas do sistema de notificações in-app (API JSON).

Endpoints disponíveis:
- GET    /notificacoes               → Lista paginada das notificações do usuário
- GET    /notificacoes/nao-lidas     → Contagem + resumo das não lidas (polling)
- PATCH  /notificacoes/{id}/lida     → Marca uma notificação como lida
- PATCH  /notificacoes/marcar-todas  → Marca todas as notificações como lidas
- DELETE /notificacoes/{id}          → Exclui uma notificação específica
- DELETE /notificacoes/lidas         → Exclui todas as notificações já lidas
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response, status

# Schemas (saída)
from dtos.responses.comum import MensagemResponse, PaginaResponse
from dtos.responses.notificacao_response import (
    NaoLidasResponse,
    NotificacaoResponse,
    NotificacaoResumoResponse,
)

# Models
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import notificacao_repo

# Utilities
from util.auth_decorator import requer_autenticacao
from util.logger_config import logger
from util.paginacao_util import paginar

router = APIRouter(prefix="/notificacoes")


# =============================================================================
# Listagem
# =============================================================================

@router.get("", response_model=PaginaResponse[NotificacaoResponse])
@requer_autenticacao()
async def listar(
    request: Request,
    pagina: int = 1,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Lista as notificações do usuário logado com paginação."""
    assert usuario_logado is not None

    todas = notificacao_repo.obter_por_usuario(usuario_logado.id, limite=100)
    paginacao = paginar(todas, pagina=pagina, por_pagina=15)

    items = [NotificacaoResponse.de_notificacao(n) for n in paginacao.items]
    return PaginaResponse.de_paginacao(paginacao, items)


@router.get("/nao-lidas", response_model=NaoLidasResponse)
@requer_autenticacao()
async def obter_nao_lidas(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Retorna a contagem e um resumo das notificações não lidas.

    Usado pelo frontend para polling (atualizar badge do navbar a cada 30s).
    """
    assert usuario_logado is not None

    total = notificacao_repo.contar_nao_lidas(usuario_logado.id)
    nao_lidas = notificacao_repo.obter_nao_lidas(usuario_logado.id, limite=5)

    return NaoLidasResponse(
        total=total,
        items=[NotificacaoResumoResponse.de_notificacao(n) for n in nao_lidas],
    )


# =============================================================================
# Marcar como lida
# =============================================================================

@router.patch("/marcar-todas", response_model=MensagemResponse)
@requer_autenticacao()
async def marcar_todas_lidas(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Marca todas as notificações do usuário logado como lidas."""
    assert usuario_logado is not None

    total = notificacao_repo.marcar_todas_como_lidas(usuario_logado.id)
    if total > 0:
        return MensagemResponse(
            message=f"{total} notificação(ões) marcada(s) como lida(s)."
        )
    return MensagemResponse(message="Não há notificações não lidas.")


@router.patch("/{notificacao_id}/lida", response_model=NotificacaoResponse)
@requer_autenticacao()
async def marcar_lida(
    request: Request,
    notificacao_id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Marca uma notificação específica do usuário logado como lida."""
    assert usuario_logado is not None

    # Garantir que a notificação pertence ao usuário logado.
    notificacoes = notificacao_repo.obter_por_usuario(usuario_logado.id, limite=100)
    notificacao = next((n for n in notificacoes if n.id == notificacao_id), None)
    if notificacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada.",
        )

    notificacao_repo.marcar_como_lida(notificacao_id, usuario_logado.id)
    notificacao.lida = True
    logger.info(
        f"Notificação {notificacao_id} marcada como lida - Usuário ID: {usuario_logado.id}"
    )
    return NotificacaoResponse.de_notificacao(notificacao)


# =============================================================================
# Exclusão
# =============================================================================

@router.delete("/lidas", response_model=MensagemResponse)
@requer_autenticacao()
async def excluir_lidas(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exclui todas as notificações já lidas do usuário logado."""
    assert usuario_logado is not None

    total = notificacao_repo.excluir_lidas(usuario_logado.id)
    if total > 0:
        return MensagemResponse(message=f"{total} notificação(ões) excluída(s).")
    return MensagemResponse(message="Não há notificações lidas para excluir.")


@router.delete("/{notificacao_id}", status_code=status.HTTP_204_NO_CONTENT)
@requer_autenticacao()
async def excluir(
    request: Request,
    notificacao_id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exclui uma notificação específica do usuário logado."""
    assert usuario_logado is not None

    sucesso = notificacao_repo.excluir(notificacao_id, usuario_logado.id)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada.",
        )

    logger.info(
        f"Notificação {notificacao_id} excluída - Usuário ID: {usuario_logado.id}"
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
