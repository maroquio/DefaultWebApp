# =============================================================================
# Imports
# =============================================================================

# Standard library
from datetime import datetime

# Third-party
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

# DTOs
from dtos.auth_dto import LoginDTO, CadastroDTO, EsqueciSenhaDTO, RedefinirSenhaDTO

# Models
from model.usuario_model import Usuario

# Repositories
from repo import usuario_repo

# Utilities
from util.auth_decorator import criar_sessao
from util.datetime_util import agora
from util.email_service import servico_email
from util.exceptions import ErroValidacaoFormulario
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.security import (
    criar_hash_senha,
    verificar_senha,
    gerar_token_redefinicao,
    obter_data_expiracao_token,
)
from util.template_util import criar_templates
from util.validation_helpers import verificar_email_disponivel
from model.usuario_logado_model import UsuarioLogado

# =============================================================================
# Constantes
# =============================================================================

TOKEN_EXPIRACAO_HORAS = 1  # Tempo de expiração do token de redefinição de senha

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter()
templates = criar_templates()


def _validar_url_redirect(url: str, padrao: str = "/usuario") -> str:
    """
    Valida URL de redirect para prevenir Open Redirect.

    Args:
        url: URL a ser validada
        padrao: URL padrão caso a validação falhe

    Returns:
        URL segura (relativa) ou URL padrão
    """
    if not url:
        return padrao

    url = url.strip()

    # Deve começar com "/" (relativa)
    if not url.startswith("/"):
        logger.warning(f"Tentativa de redirect para URL não relativa: {url}")
        return padrao

    # Não pode começar com "//" (protocolo relativo - ex: //evil.com)
    if url.startswith("//"):
        logger.warning(f"Tentativa de redirect com protocolo relativo: {url}")
        return padrao

    # Não pode conter "://" em qualquer posição (URL absoluta)
    if "://" in url:
        logger.warning(f"Tentativa de redirect para URL absoluta: {url}")
        return padrao

    # Não pode ter quebra de linha (CRLF injection)
    if "\n" in url or "\r" in url:
        logger.warning(f"Tentativa de CRLF injection em redirect: {repr(url)}")
        return padrao

    return url

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


@router.get("/login")
async def get_login(request: Request):
    """Exibe formulário de login"""
    # Se já estiver logado, redireciona
    if request.session.get("usuario_logado"):
        return RedirectResponse("/usuario", status_code=status.HTTP_303_SEE_OTHER)

    # Capturar e validar o parâmetro redirect da query string
    redirect_url = _validar_url_redirect(
        request.query_params.get("redirect", "/usuario")
    )

    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "redirect": redirect_url}
    )


@router.post("/login")
async def post_login(
    request: Request,
    email: str = Form(),
    senha: str = Form(),
    redirect: str = Form(default="/usuario"),
):
    """Processa login do usuário"""
    # Validar URL de redirect para prevenir Open Redirect
    redirect = _validar_url_redirect(redirect)

    try:
        # Rate limiting por IP
        ip = obter_identificador_cliente(request)
        if not login_limiter.verificar(ip):
            informar_erro(
                request, "Muitas tentativas de login. Aguarde alguns minutos."
            )
            logger.warning(f"Rate limit excedido para IP: {ip}")
            erros = {
                "geral": f"Muitas tentativas de login. Aguarde {login_limiter.janela_minutos} minuto(s)."
            }
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "dados": {"email": email},
                    "erros": erros,
                    "redirect": redirect,
                },
            )

        # Armazena os dados do formulário para reexibição em caso de erro
        dados_formulario = {"email": email, "redirect": redirect}

        # Validar dados com DTO
        dto = LoginDTO(email=email, senha=senha)

        # Buscar usuário
        usuario = usuario_repo.obter_por_email(dto.email)

        # Verificar credenciais
        if not usuario or not verificar_senha(dto.senha, usuario.senha):
            informar_erro(request, "E-mail ou senha inválidos")
            logger.warning(f"Tentativa de login falhou para: {dto.email}")
            erros = {"geral": "E-mail ou senha inválidos"}
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "dados": dados_formulario,
                    "erros": erros,
                    "redirect": redirect,
                },
            )

        # Salvar sessão
        usuario_logado = UsuarioLogado.from_usuario(usuario)
        criar_sessao(request, usuario_logado)

        logger.info(f"Usuário {usuario.email} autenticado com sucesso")
        informar_sucesso(request, f"Bem-vindo(a), {usuario.nome}!")
        return RedirectResponse(redirect, status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="auth/login.html",
            dados_formulario={**dados_formulario, "redirect": redirect},
            campo_padrao="senha",
        )


@router.get("/logout")
async def logout(request: Request):
    """Faz logout do usuário"""
    usuario_email = request.session.get("usuario_logado", {}).get("email", "Usuário")
    request.session.clear()
    logger.info(f"Usuário {usuario_email} fez logout")
    informar_sucesso(request, "Logout realizado com sucesso!")
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/cadastrar")
async def get_cadastrar(request: Request):
    """Exibe formulário de cadastro"""
    # Se já estiver logado, redireciona
    if request.session.get("usuario_logado"):
        return RedirectResponse("/usuario", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("auth/cadastro.html", {"request": request})


@router.post("/cadastrar")
async def post_cadastrar(
    request: Request,
    perfil: str = Form(),
    nome: str = Form(),
    email: str = Form(),
    senha: str = Form(),
    confirmar_senha: str = Form(),
):
    """Processa cadastro de novo usuário"""
    try:
        # Rate limiting por IP
        ip = obter_identificador_cliente(request)
        if not cadastro_limiter.verificar(ip):
            informar_erro(
                request,
                f"Muitas tentativas de cadastro. Aguarde {cadastro_limiter.janela_minutos} minuto(s).",
            )
            logger.warning(f"Rate limit de cadastro excedido para IP: {ip}")
            return RedirectResponse("/cadastrar", status_code=status.HTTP_303_SEE_OTHER)

        # Armazena os dados do formulário para reexibição em caso de erro
        dados_formulario = {"perfil": perfil, "nome": nome, "email": email}

        # Validar dados com DTO
        dto = CadastroDTO(
            perfil=perfil,
            nome=nome,
            email=email,
            senha=senha,
            confirmar_senha=confirmar_senha,
        )

        # Verificar se e-mail já existe
        disponivel, mensagem_erro = verificar_email_disponivel(dto.email)
        if not disponivel:
            informar_erro(request, mensagem_erro)
            return templates.TemplateResponse(
                "auth/cadastro.html", {"request": request, "dados": dados_formulario}
            )

        # Criar usuário com perfil escolhido
        usuario = Usuario(
            id=0,
            nome=dto.nome,
            email=dto.email,
            senha=criar_hash_senha(dto.senha),
            perfil=dto.perfil,
        )

        # Inserir no banco
        usuario_id = usuario_repo.inserir(usuario)

        if usuario_id:
            logger.info(f"Novo usuário cadastrado: {usuario.email}")

            # Enviar e-mail de boas-vindas
            servico_email.enviar_boas_vindas(usuario.email, usuario.nome)

            informar_sucesso(
                request, "Cadastro realizado com sucesso! Faça login para continuar."
            )
            return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
        else:
            informar_erro(request, "Erro ao realizar cadastro. Tente novamente.")
            return templates.TemplateResponse(
                "auth/cadastro.html", {"request": request, "dados": dados_formulario}
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="auth/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="confirmar_senha",
        )


@router.get("/esqueci-senha")
async def get_esqueci_senha(request: Request):
    """Exibe formulário de recuperação de senha"""
    return templates.TemplateResponse("auth/esqueci_senha.html", {"request": request})


@router.post("/esqueci-senha")
async def post_esqueci_senha(request: Request, email: str = Form()):
    """Processa solicitação de recuperação de senha"""
    try:
        # Rate limiting por IP
        ip = obter_identificador_cliente(request)
        if not esqueci_senha_limiter.verificar(ip):
            informar_erro(
                request,
                f"Muitas tentativas de recuperação de senha. Aguarde {esqueci_senha_limiter.janela_minutos} minuto(s).",
            )
            logger.warning(f"Rate limit de recuperação de senha excedido para IP: {ip}")
            return RedirectResponse(
                "/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER
            )

        # Armazena os dados do formulário para reexibição em caso de erro
        dados_formulario = {"email": email}

        # Validar e-mail com DTO
        dto = EsqueciSenhaDTO(email=email)

        # Buscar usuário
        usuario = usuario_repo.obter_por_email(dto.email)

        if usuario:
            # Gerar token de redefinição
            token = gerar_token_redefinicao()
            data_expiracao = obter_data_expiracao_token(horas=TOKEN_EXPIRACAO_HORAS)

            # Salvar token no banco
            usuario_repo.atualizar_token(usuario.email, token, data_expiracao)

            # Enviar e-mail com link de recuperação
            email_enviado = servico_email.enviar_recuperacao_senha(
                usuario.email, usuario.nome, token
            )

            if email_enviado:
                logger.info(f"E-mail de recuperação enviado para: {usuario.email}")
            else:
                logger.error(
                    f"Falha ao enviar e-mail de recuperação para: {usuario.email}"
                )

        # Sempre retornar mesma mensagem (segurança)
        informar_sucesso(
            request,
            "Se o e-mail estiver cadastrado, você receberá instruções para recuperação de senha.",
        )
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="auth/esqueci_senha.html",
            dados_formulario=dados_formulario,
            campo_padrao="email",
        )


@router.get("/redefinir-senha")
async def get_redefinir_senha(request: Request, token: str):
    """Exibe formulário de redefinição de senha"""
    # Validar token
    usuario = usuario_repo.obter_por_token(token)

    if not usuario or not usuario.data_token:
        informar_erro(request, "Token inválido ou expirado")
        return RedirectResponse("/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar expiração
    try:
        data_token = datetime.fromisoformat(usuario.data_token)
        if agora() > data_token:
            informar_erro(
                request, "Token expirado. Solicite uma nova recuperação de senha."
            )
            return RedirectResponse(
                "/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER
            )
    except (ValueError, TypeError):
        # ValueError: formato de data inválido
        # TypeError: data_token é None (já verificado, mas por segurança)
        informar_erro(request, "Token inválido")
        return RedirectResponse("/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "auth/redefinir_senha.html", {"request": request, "token": token}
    )


@router.post("/redefinir-senha")
async def post_redefinir_senha(
    request: Request,
    token: str = Form(),
    senha: str = Form(),
    confirmar_senha: str = Form(),
):
    """Processa redefinição de senha"""
    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario = {"token": token}

    try:
        # Validar dados com DTO
        dto = RedefinirSenhaDTO(
            token=token, senha=senha, confirmar_senha=confirmar_senha
        )

        # Validar token e expiração
        usuario = usuario_repo.obter_por_token(dto.token)

        if not usuario or not usuario.data_token:
            informar_erro(request, "Token inválido")
            return RedirectResponse(
                "/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER
            )

        try:
            data_token = datetime.fromisoformat(usuario.data_token)
            if agora() > data_token:
                informar_erro(request, "Token expirado")
                return RedirectResponse(
                    "/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER
                )
        except (ValueError, TypeError):
            # ValueError: formato de data inválido
            # TypeError: data_token é None (já verificado, mas por segurança)
            informar_erro(request, "Token inválido")
            return RedirectResponse(
                "/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER
            )

        # Atualizar senha
        senha_hash = criar_hash_senha(dto.senha)
        usuario_repo.atualizar_senha(usuario.id, senha_hash)

        # Limpar token
        usuario_repo.limpar_token(usuario.id)

        logger.info(f"Senha redefinida com sucesso para usuário: {usuario.email}")
        informar_sucesso(
            request, "Senha redefinida com sucesso! Faça login com sua nova senha."
        )
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="auth/redefinir_senha.html",
            dados_formulario=dados_formulario,
            campo_padrao="confirmar_senha",
        )
