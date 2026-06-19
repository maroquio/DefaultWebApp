"""
Rotas para gerenciamento de chamados por usuários não-administradores (API JSON).

Permite que usuários comuns:
- Listem seus próprios chamados (paginado, com filtros)
- Abram novos chamados
- Visualizem detalhes de chamados (com histórico de interações)
- Respondam aos próprios chamados
- Excluam chamados próprios (apenas se abertos e sem resposta de admin)
"""

# =============================================================================
# Imports
# =============================================================================

# Standard library
from typing import Optional

# Third-party
from fastapi import APIRouter, HTTPException, Request, Response, status

# DTOs (entrada)
from dtos.chamado_dto import CriarChamadoDTO
from dtos.chamado_interacao_dto import CriarInteracaoDTO

# Schemas (saída)
from dtos.responses.chamado_response import ChamadoResponse
from dtos.responses.comum import MensagemResponse, PaginaResponse

# Models
from model.chamado_model import Chamado, StatusChamado, PrioridadeChamado
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
from util.rate_limiter import DynamicRateLimiter

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/chamados")

# =============================================================================
# Rate Limiters
# =============================================================================

chamado_criar_limiter = DynamicRateLimiter(
    chave_max="rate_limit_chamado_criar_max",
    chave_minutos="rate_limit_chamado_criar_minutos",
    padrao_max=5,
    padrao_minutos=30,
    nome="chamado_criar",
)
chamado_responder_limiter = DynamicRateLimiter(
    chave_max="rate_limit_chamado_responder_max",
    chave_minutos="rate_limit_chamado_responder_minutos",
    padrao_max=10,
    padrao_minutos=10,
    nome="chamado_responder",
)


# =============================================================================
# Helpers
# =============================================================================

def _obter_chamado_do_usuario(id: int, usuario_logado: UsuarioLogado) -> Chamado:
    """Carrega o chamado garantindo propriedade (404/403)."""
    chamado = chamado_repo.obter_por_id(id)
    if not chamado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chamado não encontrado.",
        )
    if chamado.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este chamado.",
        )
    return chamado


# =============================================================================
# Listagem
# =============================================================================

@router.get("/", response_model=PaginaResponse[ChamadoResponse])
@requer_autenticacao()
async def listar(
    request: Request,
    pagina: int = 1,
    por_pagina: int = 10,
    q: Optional[str] = None,
    status_filtro: Optional[str] = None,
    prioridade: Optional[str] = None,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Lista os chamados do usuário logado (paginado, com filtros)."""
    assert usuario_logado is not None

    chamados = chamado_repo.obter_por_usuario(usuario_logado.id)

    # Filtros em memória
    if q:
        termo = q.strip().lower()
        chamados = [c for c in chamados if termo in c.titulo.lower()]
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
# Criação
# =============================================================================

@router.post(
    "/",
    response_model=ChamadoResponse,
    status_code=status.HTTP_201_CREATED,
)
@requer_autenticacao()
async def criar(
    request: Request,
    dto: CriarChamadoDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Abre um novo chamado, criando a interação inicial com a descrição."""
    assert usuario_logado is not None
    checar_rate_limit(chamado_criar_limiter, request)

    chamado = Chamado(
        id=0,
        titulo=dto.titulo,
        prioridade=PrioridadeChamado(dto.prioridade),
        status=StatusChamado.ABERTO,
        usuario_id=usuario_logado.id,
    )
    chamado_id = chamado_repo.inserir(chamado)
    if not chamado_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao abrir o chamado. Tente novamente.",
        )

    # Interação inicial com a descrição do chamado
    interacao = ChamadoInteracao(
        id=0,
        chamado_id=chamado_id,
        usuario_id=usuario_logado.id,
        mensagem=dto.descricao,
        tipo=TipoInteracao.ABERTURA,
        data_interacao=agora(),
        status_resultante=StatusChamado.ABERTO.value,
    )
    chamado_interacao_repo.inserir(interacao)

    logger.info(
        f"Chamado #{chamado_id} '{dto.titulo}' criado por usuário {usuario_logado.id}"
    )

    criado = chamado_repo.obter_por_id(chamado_id)
    interacoes = chamado_interacao_repo.obter_por_chamado(chamado_id)
    return ChamadoResponse.de_chamado(criado, interacoes)


# =============================================================================
# Detalhe
# =============================================================================

@router.get("/{id}", response_model=ChamadoResponse)
@requer_autenticacao()
async def obter(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Detalhe de um chamado do usuário com o histórico de interações."""
    assert usuario_logado is not None
    chamado = _obter_chamado_do_usuario(id, usuario_logado)

    # Marcar mensagens de outros usuários como lidas
    chamado_interacao_repo.marcar_como_lidas(id, usuario_logado.id)

    interacoes = chamado_interacao_repo.obter_por_chamado(id)
    return ChamadoResponse.de_chamado(chamado, interacoes)


# =============================================================================
# Interações (respostas)
# =============================================================================

@router.post(
    "/{id}/interacoes",
    response_model=ChamadoResponse,
    status_code=status.HTTP_201_CREATED,
)
@requer_autenticacao()
async def responder(
    request: Request,
    id: int,
    dto: CriarInteracaoDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Adiciona uma resposta do usuário ao próprio chamado."""
    assert usuario_logado is not None
    checar_rate_limit(chamado_responder_limiter, request)

    chamado = _obter_chamado_do_usuario(id, usuario_logado)

    interacao = ChamadoInteracao(
        id=0,
        chamado_id=id,
        usuario_id=usuario_logado.id,
        mensagem=dto.mensagem,
        tipo=TipoInteracao.RESPOSTA_USUARIO,
        data_interacao=agora(),
        status_resultante=chamado.status.value,  # Mantém status atual
    )
    chamado_interacao_repo.inserir(interacao)

    logger.info(f"Usuário {usuario_logado.id} respondeu ao chamado {id}")

    atualizado = chamado_repo.obter_por_id(id)
    interacoes = chamado_interacao_repo.obter_por_chamado(id)
    return ChamadoResponse.de_chamado(atualizado, interacoes)


# =============================================================================
# Exclusão
# =============================================================================

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@requer_autenticacao()
async def excluir(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exclui um chamado do usuário (apenas se aberto e sem resposta de admin)."""
    assert usuario_logado is not None
    chamado = _obter_chamado_do_usuario(id, usuario_logado)

    if chamado.status != StatusChamado.ABERTO:
        logger.warning(
            f"Usuário {usuario_logado.id} tentou excluir chamado {id} "
            f"com status {chamado.status.value}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Apenas chamados abertos podem ser excluídos.",
        )

    if chamado_interacao_repo.tem_resposta_admin(id):
        logger.warning(
            f"Usuário {usuario_logado.id} tentou excluir chamado {id} "
            f"que possui respostas de admin"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir chamados que já possuem resposta do administrador.",
        )

    chamado_repo.excluir(id)
    logger.info(f"Chamado {id} excluído por usuário {usuario_logado.id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
