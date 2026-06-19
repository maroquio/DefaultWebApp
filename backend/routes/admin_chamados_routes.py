"""
Rotas administrativas para gerenciamento de chamados (API JSON).

Permite que administradores:
- Listem todos os chamados do sistema (paginado, com filtros)
- Visualizem detalhes de qualquer chamado (com histórico)
- Respondam chamados (interação + alteração de status)
- Alterem o status de chamados (incluindo fechar/reabrir)
"""

# =============================================================================
# Imports
# =============================================================================

# Standard library
from typing import Optional

# Third-party
from fastapi import APIRouter, HTTPException, Request, status

# DTOs (entrada)
from dtos.chamado_dto import AlterarStatusDTO
from dtos.chamado_interacao_dto import CriarInteracaoDTO

# Schemas (saída)
from dtos.responses.chamado_response import ChamadoResponse
from dtos.responses.comum import PaginaResponse

# Models
from model.chamado_model import Chamado, StatusChamado
from model.chamado_interacao_model import ChamadoInteracao, TipoInteracao
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import chamado_repo, chamado_interacao_repo

# Utilities
from util.api_helpers import checar_rate_limit
from util.auth_decorator import requer_autenticacao
from util.datetime_util import agora
from util.logger_config import logger
from util.paginacao_util import paginar
from util.perfis import Perfil
from util.rate_limiter import DynamicRateLimiter

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/admin/chamados")

# =============================================================================
# Rate Limiters
# =============================================================================

admin_chamado_responder_limiter = DynamicRateLimiter(
    chave_max="rate_limit_admin_chamado_responder_max",
    chave_minutos="rate_limit_admin_chamado_responder_minutos",
    padrao_max=20,
    padrao_minutos=5,
    nome="admin_chamado_responder",
)


# =============================================================================
# Helpers
# =============================================================================

def _obter_chamado(id: int) -> Chamado:
    """Carrega o chamado ou lança 404."""
    chamado = chamado_repo.obter_por_id(id)
    if not chamado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chamado não encontrado.",
        )
    return chamado


# =============================================================================
# Listagem
# =============================================================================

@router.get("/", response_model=PaginaResponse[ChamadoResponse])
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(
    request: Request,
    pagina: int = 1,
    por_pagina: int = 10,
    q: Optional[str] = None,
    status_filtro: Optional[str] = None,
    prioridade: Optional[str] = None,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Lista todos os chamados do sistema (paginado, com filtros)."""
    assert usuario_logado is not None

    chamados = chamado_repo.obter_todos(usuario_logado.id)

    # Filtros em memória
    if q:
        termo = q.strip().lower()
        chamados = [
            c
            for c in chamados
            if termo in c.titulo.lower()
            or (c.usuario_nome and termo in c.usuario_nome.lower())
            or (c.usuario_email and termo in c.usuario_email.lower())
        ]
    if status_filtro:
        chamados = [c for c in chamados if c.status.value == status_filtro]
    if prioridade:
        chamados = [c for c in chamados if c.prioridade.value == prioridade]

    paginacao = paginar(chamados, pagina, por_pagina)
    return PaginaResponse.de_paginacao(
        paginacao,
        [ChamadoResponse.de_chamado(c) for c in paginacao.items],
    )


# =============================================================================
# Detalhe
# =============================================================================

@router.get("/{id}", response_model=ChamadoResponse)
@requer_autenticacao([Perfil.ADMIN.value])
async def obter(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Detalhe de qualquer chamado com o histórico de interações."""
    assert usuario_logado is not None
    chamado = _obter_chamado(id)

    # Marcar mensagens de outros usuários como lidas
    chamado_interacao_repo.marcar_como_lidas(id, usuario_logado.id)

    interacoes = chamado_interacao_repo.obter_por_chamado(id)
    return ChamadoResponse.de_chamado(chamado, interacoes)


# =============================================================================
# Interações (resposta do admin + alteração de status)
# =============================================================================

@router.post(
    "/{id}/interacoes",
    response_model=ChamadoResponse,
    status_code=status.HTTP_201_CREATED,
)
@requer_autenticacao([Perfil.ADMIN.value])
async def responder(
    request: Request,
    id: int,
    dto_mensagem: CriarInteracaoDTO,
    dto_status: AlterarStatusDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Salva a resposta do admin e atualiza o status do chamado.

    Como há dois modelos Pydantic no corpo, o FastAPI espera o body aninhado:
    ``{"dto_mensagem": {"mensagem": "..."}, "dto_status": {"status": "..."}}``.
    """
    assert usuario_logado is not None
    checar_rate_limit(admin_chamado_responder_limiter, request)

    _obter_chamado(id)

    interacao = ChamadoInteracao(
        id=0,
        chamado_id=id,
        usuario_id=usuario_logado.id,
        mensagem=dto_mensagem.mensagem,
        tipo=TipoInteracao.RESPOSTA_ADMIN,
        data_interacao=agora(),
        status_resultante=dto_status.status,
    )
    chamado_interacao_repo.inserir(interacao)

    fechar = dto_status.status == StatusChamado.FECHADO.value
    sucesso = chamado_repo.atualizar_status(id=id, status=dto_status.status, fechar=fechar)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar a resposta. Tente novamente.",
        )

    logger.info(
        f"Chamado {id} respondido por admin {usuario_logado.id}, "
        f"status: {dto_status.status}"
    )

    atualizado = chamado_repo.obter_por_id(id)
    interacoes = chamado_interacao_repo.obter_por_chamado(id)
    return ChamadoResponse.de_chamado(atualizado, interacoes)


# =============================================================================
# Alteração de status (fechar / reabrir / qualquer transição)
# =============================================================================

@router.patch("/{id}/status", response_model=ChamadoResponse)
@requer_autenticacao([Perfil.ADMIN.value])
async def alterar_status(
    request: Request,
    id: int,
    dto: AlterarStatusDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Altera o status de um chamado sem adicionar mensagem.

    Cobre o fechamento (status 'Fechado' grava data de fechamento) e a
    reabertura (de 'Fechado' só é permitido sair para 'Em Análise').
    """
    assert usuario_logado is not None
    chamado = _obter_chamado(id)

    novo_status = dto.status

    # Regra de reabertura: chamado fechado só pode ir para 'Em Análise'
    if chamado.status == StatusChamado.FECHADO and novo_status != StatusChamado.FECHADO.value:
        if novo_status != StatusChamado.EM_ANALISE.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "detail": "Chamados fechados só podem ser reabertos como 'Em Análise'.",
                    "type": "conflict",
                    "errors": {"status": ["Reabra o chamado como 'Em Análise'."]},
                },
            )

    fechar = novo_status == StatusChamado.FECHADO.value
    sucesso = chamado_repo.atualizar_status(id=id, status=novo_status, fechar=fechar)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao alterar o status do chamado.",
        )

    logger.info(
        f"Status do chamado {id} alterado para '{novo_status}' "
        f"por admin {usuario_logado.id}"
    )

    atualizado = chamado_repo.obter_por_id(id)
    interacoes = chamado_interacao_repo.obter_por_chamado(id)
    return ChamadoResponse.de_chamado(atualizado, interacoes)
