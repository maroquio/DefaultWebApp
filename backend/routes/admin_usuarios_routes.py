# =============================================================================
# Rotas de Administração de Usuários (API JSON) — CRUD admin-only
# =============================================================================

from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response, status

# DTOs (entrada)
from dtos.usuario_dto import CriarUsuarioDTO, AlterarUsuarioDTO

# Schemas (saída)
from dtos.responses.comum import PaginaResponse
from dtos.responses.usuario_response import UsuarioResponse

# Models
from model.usuario_model import Usuario
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import usuario_repo

# Utilities
from util.api_helpers import checar_rate_limit
from util.auth_decorator import requer_autenticacao
from util.logger_config import logger
from util.paginacao_util import paginar
from util.perfis import Perfil
from util.rate_limiter import DynamicRateLimiter
from util.security import criar_hash_senha
from util.validation_helpers import verificar_email_disponivel

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/admin/usuarios")

# =============================================================================
# Rate Limiters
# =============================================================================

admin_usuarios_limiter = DynamicRateLimiter(
    chave_max="rate_limit_admin_usuarios_max",
    chave_minutos="rate_limit_admin_usuarios_minutos",
    padrao_max=10,
    padrao_minutos=1,
    nome="admin_usuarios",
)


# =============================================================================
# Helpers
# =============================================================================

def _obter_usuario_ou_404(id: int) -> Usuario:
    """Carrega a entidade do usuário ou lança 404."""
    usuario = usuario_repo.obter_por_id(id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )
    return usuario


def _conflito_email(mensagem_erro: str) -> HTTPException:
    """Monta a HTTPException 409 padronizada para e-mail já em uso."""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "detail": mensagem_erro,
            "type": "conflict",
            "errors": {"email": [mensagem_erro]},
        },
    )


# =============================================================================
# Listagem
# =============================================================================

@router.get("/", response_model=PaginaResponse[UsuarioResponse])
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(
    request: Request,
    pagina: int = 1,
    por_pagina: int = 10,
    perfil: Optional[str] = None,
    q: Optional[str] = None,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Lista usuários de forma paginada, com filtros opcionais por perfil e termo (q)."""
    assert usuario_logado is not None

    termo = (q or "").strip()
    if termo:
        # Busca por nome/email (limite alto para permitir paginação em memória)
        usuarios = usuario_repo.buscar_por_termo(termo, limit=1000)
        if perfil:
            usuarios = [u for u in usuarios if u.perfil == perfil]
    elif perfil:
        usuarios = usuario_repo.obter_todos_por_perfil(perfil)
    else:
        usuarios = usuario_repo.obter_todos()

    paginacao = paginar(usuarios, pagina=pagina, por_pagina=por_pagina)
    items = [UsuarioResponse.de_usuario(u) for u in paginacao.items]
    return PaginaResponse.de_paginacao(paginacao, items)


# =============================================================================
# Detalhe
# =============================================================================

@router.get("/{id}", response_model=UsuarioResponse)
@requer_autenticacao([Perfil.ADMIN.value])
async def obter(
    request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None
):
    """Retorna os dados de um usuário específico (404 se não existir)."""
    assert usuario_logado is not None
    return UsuarioResponse.de_usuario(_obter_usuario_ou_404(id))


# =============================================================================
# Criação
# =============================================================================

@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
@requer_autenticacao([Perfil.ADMIN.value])
async def criar(
    request: Request,
    dto: CriarUsuarioDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Cria um novo usuário. Valida disponibilidade de e-mail (409)."""
    assert usuario_logado is not None
    checar_rate_limit(admin_usuarios_limiter, request)

    disponivel, mensagem_erro = verificar_email_disponivel(dto.email)
    if not disponivel:
        raise _conflito_email(mensagem_erro)

    usuario = Usuario(
        id=0,
        nome=dto.nome,
        email=dto.email,
        senha=criar_hash_senha(dto.senha),
        perfil=dto.perfil,
    )
    # usuario_repo.inserir cria também a foto padrão do usuário.
    usuario_id = usuario_repo.inserir(usuario)
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao cadastrar usuário. Tente novamente.",
        )

    logger.info(f"Usuário '{dto.email}' cadastrado por admin {usuario_logado.id}")
    return UsuarioResponse.de_usuario(_obter_usuario_ou_404(usuario_id))


# =============================================================================
# Alteração
# =============================================================================

@router.put("/{id}", response_model=UsuarioResponse)
@requer_autenticacao([Perfil.ADMIN.value])
async def alterar(
    request: Request,
    id: int,
    dto: AlterarUsuarioDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Altera nome, e-mail e perfil de um usuário. Valida e-mail para outro id (409)."""
    assert usuario_logado is not None
    checar_rate_limit(admin_usuarios_limiter, request)

    if dto.id != id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": "O id do corpo não corresponde ao id da URL.",
                "type": "bad_request",
                "errors": {"id": ["O id do corpo não corresponde ao id da URL."]},
            },
        )

    usuario_atual = _obter_usuario_ou_404(id)

    disponivel, mensagem_erro = verificar_email_disponivel(dto.email, id)
    if not disponivel:
        raise _conflito_email(mensagem_erro)

    usuario_atualizado = Usuario(
        id=id,
        nome=dto.nome,
        email=dto.email,
        senha=usuario_atual.senha,  # Mantém senha existente
        perfil=dto.perfil,
    )
    if not usuario_repo.alterar(usuario_atualizado):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao alterar usuário. Tente novamente.",
        )

    logger.info(f"Usuário {id} alterado por admin {usuario_logado.id}")
    return UsuarioResponse.de_usuario(_obter_usuario_ou_404(id))


# =============================================================================
# Exclusão
# =============================================================================

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@requer_autenticacao([Perfil.ADMIN.value])
async def excluir(
    request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None
):
    """Exclui um usuário. Impede que o admin exclua a si mesmo (403)."""
    assert usuario_logado is not None
    checar_rate_limit(admin_usuarios_limiter, request)

    usuario = _obter_usuario_ou_404(id)

    if usuario.id == usuario_logado.id:
        logger.warning(f"Admin {usuario_logado.id} tentou excluir a si mesmo")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não pode excluir seu próprio usuário.",
        )

    if not usuario_repo.excluir(id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir usuário. Tente novamente.",
        )

    logger.info(
        f"Usuário {id} ({usuario.email}) excluído por admin {usuario_logado.id}"
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
