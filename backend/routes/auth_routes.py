# =============================================================================
# Rotas de Autenticação (API JSON)
# =============================================================================

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status

# DTOs (entrada)
from dtos.auth_dto import LoginDTO, CadastroDTO, EsqueciSenhaDTO, RedefinirSenhaDTO

# Schemas (saída)
from dtos.responses.comum import MensagemResponse, TokenCsrfResponse
from dtos.responses.usuario_response import UsuarioResponse

# Models
from model.usuario_model import Usuario
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import usuario_repo

# Utilities
from util.api_helpers import checar_rate_limit
from util.auth_decorator import criar_sessao, destruir_sessao, requer_autenticacao
from util.csrf_protection import obter_token_csrf
from util.datetime_util import agora
from util.email_service import servico_email
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import DynamicRateLimiter
from util.security import (
    criar_hash_senha,
    verificar_senha,
    gerar_token_redefinicao,
    obter_data_expiracao_token,
)
from util.validation_helpers import verificar_email_disponivel

TOKEN_EXPIRACAO_HORAS = 1

router = APIRouter()


# =============================================================================
# Rate Limiters
# =============================================================================

login_limiter = DynamicRateLimiter(
    chave_max="rate_limit_login_max",
    chave_minutos="rate_limit_login_minutos",
    padrao_max=5,
    padrao_minutos=5,
    nome="login",
)
cadastro_limiter = DynamicRateLimiter(
    chave_max="rate_limit_cadastro_max",
    chave_minutos="rate_limit_cadastro_minutos",
    padrao_max=3,
    padrao_minutos=10,
    nome="cadastro",
)
esqueci_senha_limiter = DynamicRateLimiter(
    chave_max="rate_limit_esqueci_senha_max",
    chave_minutos="rate_limit_esqueci_senha_minutos",
    padrao_max=1,
    padrao_minutos=1,
    nome="esqueci_senha",
)


# =============================================================================
# CSRF / Sessão
# =============================================================================

@router.get("/csrf-token", response_model=TokenCsrfResponse)
async def get_csrf_token(request: Request):
    """Retorna o token CSRF da sessão (criando a sessão se necessário)."""
    return TokenCsrfResponse(token=obter_token_csrf(request))


@router.get("/me", response_model=UsuarioResponse)
@requer_autenticacao()
async def get_me(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Retorna o usuário autenticado atual (401 se não houver sessão)."""
    assert usuario_logado is not None
    usuario = usuario_repo.obter_por_id(usuario_logado.id)
    if not usuario:
        destruir_sessao(request)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida.")
    return UsuarioResponse.de_usuario(usuario)


# =============================================================================
# Login / Logout
# =============================================================================

@router.post("/login", response_model=UsuarioResponse)
async def post_login(request: Request, dto: LoginDTO):
    """Autentica o usuário e cria a sessão."""
    checar_rate_limit(login_limiter, request)

    usuario = usuario_repo.obter_por_email(dto.email)
    if not usuario or not verificar_senha(dto.senha, usuario.senha):
        logger.warning(f"Login falhou para: {dto.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
        )

    usuario_logado = UsuarioLogado.from_usuario(usuario)
    criar_sessao(request, usuario_logado)
    logger.info(f"Usuário {usuario.email} autenticado")
    return UsuarioResponse.de_usuario(usuario)


@router.post("/logout", response_model=MensagemResponse)
async def post_logout(request: Request):
    """Encerra a sessão do usuário."""
    email = request.session.get("usuario_logado", {}).get("email", "Usuário")
    destruir_sessao(request)
    logger.info(f"Usuário {email} fez logout")
    return MensagemResponse(message="Logout realizado com sucesso.")


# =============================================================================
# Cadastro
# =============================================================================

@router.post(
    "/cadastrar",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_cadastrar(request: Request, dto: CadastroDTO):
    """Cria um novo usuário."""
    checar_rate_limit(cadastro_limiter, request)

    # Guarda anti-escalada de privilégio: o perfil chega do cliente, então o
    # servidor precisa rejeitar qualquer perfil fora da lista de auto-cadastro
    # (que NUNCA inclui ADMIN). Sem isso, um anônimo poderia se registrar como
    # Administrador. A escolha de perfil admin só existe nas rotas de admin.
    perfis_permitidos = {perfil.value for perfil in Perfil.perfis_autocadastro()}
    if dto.perfil not in perfis_permitidos:
        mensagem_perfil = "Perfil não permitido para auto-cadastro."
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "detail": mensagem_perfil,
                "type": "forbidden",
                "errors": {"perfil": [mensagem_perfil]},
            },
        )

    disponivel, mensagem_erro = verificar_email_disponivel(dto.email)
    if not disponivel:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": mensagem_erro,
                "type": "conflict",
                "errors": {"email": [mensagem_erro]},
            },
        )

    usuario = Usuario(
        id=0,
        nome=dto.nome,
        email=dto.email,
        senha=criar_hash_senha(dto.senha),
        perfil=dto.perfil,
    )
    usuario_id = usuario_repo.inserir(usuario)
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao realizar cadastro. Tente novamente.",
        )

    logger.info(f"Novo usuário cadastrado: {usuario.email}")
    servico_email.enviar_boas_vindas(usuario.email, usuario.nome)

    criado = usuario_repo.obter_por_id(usuario_id)
    return UsuarioResponse.de_usuario(criado)


# =============================================================================
# Recuperação de senha
# =============================================================================

@router.post("/esqueci-senha", response_model=MensagemResponse)
async def post_esqueci_senha(request: Request, dto: EsqueciSenhaDTO):
    """Solicita recuperação de senha; e-mail com link para o SPA."""
    checar_rate_limit(esqueci_senha_limiter, request)

    usuario = usuario_repo.obter_por_email(dto.email)
    if usuario:
        token = gerar_token_redefinicao()
        data_expiracao = obter_data_expiracao_token(horas=TOKEN_EXPIRACAO_HORAS)
        usuario_repo.atualizar_token(usuario.email, token, data_expiracao)
        enviado = servico_email.enviar_recuperacao_senha(
            usuario.email, usuario.nome, token
        )
        if enviado:
            logger.info(f"E-mail de recuperação enviado para: {usuario.email}")
        else:
            logger.error(f"Falha ao enviar recuperação para: {usuario.email}")

    # Mesma resposta sempre (evita enumeração de e-mails)
    return MensagemResponse(
        message=(
            "Se o e-mail estiver cadastrado, você receberá instruções "
            "para recuperação de senha."
        )
    )


@router.post("/redefinir-senha", response_model=MensagemResponse)
async def post_redefinir_senha(request: Request, dto: RedefinirSenhaDTO):
    """Redefine a senha a partir do token recebido por e-mail."""
    usuario = usuario_repo.obter_por_token(dto.token)
    if not usuario or not usuario.data_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado.",
        )

    # data_token pode vir como datetime (conversor do SQLite) ou string
    data_token = usuario.data_token
    if isinstance(data_token, str):
        try:
            data_token = datetime.fromisoformat(data_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido."
            )
    if data_token.tzinfo is None:
        data_token = data_token.replace(tzinfo=agora().tzinfo)
    if agora() > data_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado. Solicite uma nova recuperação.",
        )

    senha_hash = criar_hash_senha(dto.senha)
    usuario_repo.atualizar_senha(usuario.id, senha_hash)
    usuario_repo.limpar_token(usuario.id)
    logger.info(f"Senha redefinida para: {usuario.email}")

    return MensagemResponse(message="Senha redefinida com sucesso.")
