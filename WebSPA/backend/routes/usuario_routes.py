# =============================================================================
# Rotas de Usuário (API JSON) — dashboard, perfil, senha e foto do próprio usuário
# =============================================================================

from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status

# DTOs (entrada)
from dtos.perfil_dto import EditarPerfilDTO, AlterarSenhaDTO, AtualizarFotoDTO

# Schemas (saída)
from dtos.responses.comum import MensagemResponse
from dtos.responses.usuario_response import UsuarioResponse, DashboardResponse

# Models
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import usuario_repo, chamado_repo

# Utilities
from util.api_helpers import checar_rate_limit
from util.auth_decorator import requer_autenticacao
from util.foto_util import salvar_foto_cropada_usuario
from util.logger_config import logger
from util.rate_limiter import DynamicRateLimiter
from util.security import criar_hash_senha, verificar_senha
from util.validation_helpers import verificar_email_disponivel

router = APIRouter(prefix="/usuario")

# =============================================================================
# Rate Limiters
# =============================================================================

upload_foto_limiter = DynamicRateLimiter(
    chave_max="rate_limit_upload_foto_max",
    chave_minutos="rate_limit_upload_foto_minutos",
    padrao_max=5,
    padrao_minutos=10,
    nome="upload_foto",
)
alterar_senha_limiter = DynamicRateLimiter(
    chave_max="rate_limit_alterar_senha_max",
    chave_minutos="rate_limit_alterar_senha_minutos",
    padrao_max=5,
    padrao_minutos=15,
    nome="alterar_senha",
)


def _obter_usuario_atual(usuario_logado: UsuarioLogado):
    """Carrega a entidade do usuário logado ou lança 404."""
    usuario = usuario_repo.obter_por_id(usuario_logado.id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )
    return usuario


# =============================================================================
# Dashboard
# =============================================================================

@router.get("/dashboard", response_model=DashboardResponse)
@requer_autenticacao()
async def dashboard(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Contadores do painel conforme o perfil do usuário."""
    assert usuario_logado is not None
    if usuario_logado.is_admin():
        return DashboardResponse(chamados_pendentes=chamado_repo.contar_pendentes())
    return DashboardResponse(
        chamados_abertos=chamado_repo.contar_abertos_por_usuario(usuario_logado.id)
    )


# =============================================================================
# Perfil
# =============================================================================

@router.get("/perfil", response_model=UsuarioResponse)
@requer_autenticacao()
async def get_perfil(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Retorna os dados do perfil do usuário logado."""
    assert usuario_logado is not None
    return UsuarioResponse.de_usuario(_obter_usuario_atual(usuario_logado))


@router.put("/perfil", response_model=UsuarioResponse)
@requer_autenticacao()
async def put_perfil(
    request: Request,
    dto: EditarPerfilDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Atualiza nome e e-mail do usuário logado."""
    assert usuario_logado is not None
    usuario = _obter_usuario_atual(usuario_logado)

    disponivel, mensagem_erro = verificar_email_disponivel(dto.email, usuario_logado.id)
    if not disponivel:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": mensagem_erro,
                "type": "conflict",
                "errors": {"email": [mensagem_erro]},
            },
        )

    usuario.nome = dto.nome
    usuario.email = dto.email
    if not usuario_repo.alterar(usuario):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar o perfil. Tente novamente.",
        )

    # Manter sessão sincronizada
    request.session["usuario_logado"]["nome"] = usuario.nome
    request.session["usuario_logado"]["email"] = usuario.email
    logger.info(f"Perfil atualizado - Usuário ID: {usuario.id}")
    return UsuarioResponse.de_usuario(usuario)


# =============================================================================
# Senha
# =============================================================================

@router.put("/senha", response_model=MensagemResponse)
@requer_autenticacao()
async def put_senha(
    request: Request,
    dto: AlterarSenhaDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Altera a senha do usuário logado."""
    assert usuario_logado is not None
    checar_rate_limit(alterar_senha_limiter, request)

    usuario = _obter_usuario_atual(usuario_logado)

    if not verificar_senha(dto.senha_atual, usuario.senha):
        logger.warning(f"Senha atual incorreta - Usuário ID: {usuario.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": "Senha atual está incorreta.",
                "type": "bad_request",
                "errors": {"senha_atual": ["Senha atual está incorreta."]},
            },
        )

    if verificar_senha(dto.senha_nova, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": "A nova senha deve ser diferente da senha atual.",
                "type": "bad_request",
                "errors": {
                    "senha_nova": ["A nova senha deve ser diferente da senha atual."]
                },
            },
        )

    senha_hash = criar_hash_senha(dto.senha_nova)
    if not usuario_repo.atualizar_senha(usuario.id, senha_hash):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao alterar a senha. Tente novamente.",
        )

    logger.info(f"Senha alterada - Usuário ID: {usuario.id}")
    return MensagemResponse(message="Senha alterada com sucesso.")


# =============================================================================
# Foto de perfil
# =============================================================================

@router.put("/foto", response_model=UsuarioResponse)
@requer_autenticacao()
async def put_foto(
    request: Request,
    dto: AtualizarFotoDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Atualiza a foto de perfil (imagem cropada em base64)."""
    assert usuario_logado is not None
    checar_rate_limit(upload_foto_limiter, request)

    usuario_id = usuario_logado.id

    # Validar tamanho aproximado (base64 é ~33% maior que o binário)
    tamanho_aproximado = len(dto.foto_base64) * 3 / 4
    if tamanho_aproximado > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Imagem muito grande. O tamanho máximo é 10MB.",
        )

    # salvar_foto_cropada_usuario captura erros de imagem internamente e
    # retorna False — tratamos isso como entrada inválida (imagem corrompida).
    try:
        sucesso = salvar_foto_cropada_usuario(usuario_id, dto.foto_base64)
    except (ValueError, IOError, OSError) as e:
        logger.error(f"Erro no upload de foto - Usuário ID {usuario_id}: {e}")
        sucesso = False

    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Imagem inválida. Verifique o arquivo e tente novamente.",
        )

    logger.info(f"Foto atualizada - Usuário ID: {usuario_id}")
    return UsuarioResponse.de_usuario(_obter_usuario_atual(usuario_logado))
