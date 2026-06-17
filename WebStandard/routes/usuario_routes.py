# =============================================================================
# Imports
# =============================================================================

# Standard library
from typing import Optional

# Third-party
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

# DTOs
from dtos.perfil_dto import EditarPerfilDTO, AlterarSenhaDTO

# Models
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import usuario_repo, chamado_repo

# Utilities
from util.auth_decorator import requer_autenticacao
from util.exceptions import ErroValidacaoFormulario
from util.flash_messages import informar_sucesso, informar_erro
from util.foto_util import salvar_foto_cropada_usuario
from util.logger_config import logger
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.repository_helpers import obter_ou_404
from util.security import criar_hash_senha, verificar_senha
from util.template_util import criar_templates
from util.validation_helpers import verificar_email_disponivel

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter()
templates_usuario = criar_templates()

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
form_get_limiter = DynamicRateLimiter(
    chave_max="rate_limit_form_get_max",
    chave_minutos="rate_limit_form_get_minutos",
    padrao_max=60,
    padrao_minutos=1,
    nome="form_get",
)


@router.get("/usuario")
@requer_autenticacao()
async def dashboard(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """
    Dashboard do usuário (área privada)
    Requer autenticação
    """
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Preparar dados do contexto
    context = {
        "request": request,
        "usuario_logado": usuario_logado
    }

    # Adicionar contador de chamados conforme perfil
    if usuario_logado.is_admin():
        # Admin vê total de chamados pendentes no sistema
        context["chamados_pendentes"] = chamado_repo.contar_pendentes()
    else:
        # Usuário comum vê seus próprios chamados em aberto
        context["chamados_abertos"] = chamado_repo.contar_abertos_por_usuario(usuario_logado.id)

    return templates_usuario.TemplateResponse("dashboard.html", context)


@router.get("/usuario/perfil/visualizar")
@requer_autenticacao()
async def get_visualizar_perfil(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Visualizar perfil do usuário logado"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Obter usuário ou redirecionar para logout
    usuario = obter_ou_404(
        usuario_repo.obter_por_id(usuario_logado.id),
        request,
        "Usuário não encontrado!",
        "/logout"
    )
    if isinstance(usuario, RedirectResponse):
        return usuario

    return templates_usuario.TemplateResponse(
        "perfil/visualizar.html", {"request": request, "usuario": usuario, "usuario_logado": usuario_logado}
    )


@router.get("/usuario/perfil/editar")
@requer_autenticacao()
async def get_editar_perfil(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Formulário para editar dados do perfil"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not form_get_limiter.verificar(ip):
        informar_erro(request, f"Muitas requisições. Aguarde {form_get_limiter.janela_minutos} minuto(s).")
        logger.warning(f"Rate limit excedido para formulário GET - IP: {ip}")
        return RedirectResponse("/usuario", status_code=status.HTTP_303_SEE_OTHER)

    # Obter usuário ou redirecionar para logout
    usuario = obter_ou_404(
        usuario_repo.obter_por_id(usuario_logado.id),
        request,
        "Usuário não encontrado!",
        "/logout"
    )
    if isinstance(usuario, RedirectResponse):
        return usuario

    return templates_usuario.TemplateResponse(
        "perfil/editar.html", {"request": request, "dados": usuario.__dict__, "usuario_logado": usuario_logado}
    )


@router.post("/usuario/perfil/editar")
@requer_autenticacao()
async def post_editar_perfil(
    request: Request,
    nome: str = Form(),
    email: str = Form(),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Processar edição de dados do perfil"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Obter usuário ou redirecionar para logout
    usuario = obter_ou_404(
        usuario_repo.obter_por_id(usuario_logado.id),
        request,
        "Usuário não encontrado!",
        "/logout"
    )
    if isinstance(usuario, RedirectResponse):
        return usuario

    # Armazenar dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {"nome": nome, "email": email}
    try:
        # Validar com DTO
        dto = EditarPerfilDTO(nome=nome, email=email)

        # Verificar se o e-mail já está em uso por outro usuário
        disponivel, mensagem_erro = verificar_email_disponivel(dto.email, usuario_logado.id)
        if not disponivel:
            informar_erro(request, mensagem_erro)
            return templates_usuario.TemplateResponse(
                "perfil/editar.html",
                {
                    "request": request,
                    "dados": dados_formulario,
                    "erros": {
                        "email": mensagem_erro
                    },
                    "usuario_logado": usuario_logado,
                },
            )

        # Atualizar dados
        usuario.nome = dto.nome
        usuario.email = dto.email

        # Salvar no banco
        if usuario_repo.alterar(usuario):
            # Atualizar sessão
            request.session["usuario_logado"]["nome"] = usuario.nome
            request.session["usuario_logado"]["email"] = usuario.email
            logger.info(f"Perfil atualizado para usuário ID: {usuario.id}")
            informar_sucesso(request, "Perfil atualizado com sucesso!")
            return RedirectResponse(
                "/usuario/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            msg_erro = (
                "Ocorreu um erro desconhecido ao atualizar seu perfil. "
                "A equipe de suporte foi notificada. Tente novamente mais tarde."
            )
            informar_erro(request, msg_erro)
            return templates_usuario.TemplateResponse(
                "perfil/editar.html",
                {
                    "request": request,
                    "dados": dados_formulario,
                    "erros": {"geral": msg_erro},
                    "usuario_logado": usuario_logado,
                },
            )

    except ValidationError as e:
        # Incluir dados do usuário para o template
        dados_formulario["usuario"] = usuario
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="perfil/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="email",
            mensagem_flash="Há campos com erros de validação!",
        )
    # Removido except Exception duplicado - global handler cuida disso


@router.get("/usuario/perfil/alterar-senha")
@requer_autenticacao()
async def get_alterar_senha(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Formulário para alterar senha"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not form_get_limiter.verificar(ip):
        informar_erro(request, f"Muitas requisições. Aguarde {form_get_limiter.janela_minutos} minuto(s).")
        logger.warning(f"Rate limit excedido para formulário GET - IP: {ip}")
        return RedirectResponse("/usuario", status_code=status.HTTP_303_SEE_OTHER)

    return templates_usuario.TemplateResponse("perfil/alterar-senha.html", {"request": request, "usuario_logado": usuario_logado})


@router.post("/usuario/perfil/alterar-senha")
@requer_autenticacao()
async def post_alterar_senha(
    request: Request,
    senha_atual: str = Form(),
    senha_nova: str = Form(),
    confirmar_senha: str = Form(),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Processar alteração de senha"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not alterar_senha_limiter.verificar(ip):
        informar_erro(
            request,
            f"Muitas tentativas de alteração de senha. Aguarde {alterar_senha_limiter.janela_minutos} minuto(s).",
        )
        logger.warning(f"Rate limit excedido para alteração de senha - IP: {ip}")
        msg_rate = (
            f"Muitas tentativas de alteração de senha. "
            f"Aguarde {alterar_senha_limiter.janela_minutos} minuto(s)."
        )
        return templates_usuario.TemplateResponse(
            "perfil/alterar-senha.html",
            {"request": request, "erros": {"geral": msg_rate}, "usuario_logado": usuario_logado},
        )

    try:
        # Validar com DTO
        dto = AlterarSenhaDTO(
            senha_atual=senha_atual,
            senha_nova=senha_nova,
            confirmar_senha=confirmar_senha,
        )

        # Obter usuário ou redirecionar para logout
        usuario = obter_ou_404(
            usuario_repo.obter_por_id(usuario_logado.id),
            request,
            "Usuário não encontrado!",
            "/logout"
        )
        if isinstance(usuario, RedirectResponse):
            return usuario

        # Validar senha atual
        if not verificar_senha(dto.senha_atual, usuario.senha):
            informar_erro(request, "Senha atual está incorreta")
            logger.warning(
                f"Tentativa de alteração de senha com senha atual incorreta - Usuário ID: {usuario.id}"
            )
            return templates_usuario.TemplateResponse(
                "perfil/alterar-senha.html",
                {
                    "request": request,
                    "erros": {"senha_atual": "Senha atual está incorreta."},
                    "usuario_logado": usuario_logado,
                },
            )

        # Verificar se a nova senha é diferente da atual
        if verificar_senha(dto.senha_nova, usuario.senha):
            informar_erro(request, "A nova senha deve ser diferente da senha atual.")
            return templates_usuario.TemplateResponse(
                "perfil/alterar-senha.html",
                {
                    "request": request,
                    "erros": {
                        "senha_nova": "A nova senha deve ser diferente da senha atual."
                    },
                    "usuario_logado": usuario_logado,
                },
            )

        # Atualizar senha
        senha_hash = criar_hash_senha(dto.senha_nova)
        if usuario_repo.atualizar_senha(usuario.id, senha_hash):
            logger.info(f"Senha alterada com sucesso - Usuário ID: {usuario.id}")
            informar_sucesso(request, "Senha alterada com sucesso!")
            return RedirectResponse(
                "/usuario/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            msg_erro = (
                "Ocorreu um erro desconhecido ao processar alteração de senha. "
                "A equipe de suporte foi notificada. Tente novamente mais tarde."
            )
            informar_erro(request, "Erro ao alterar senha. Tente novamente.")
            return templates_usuario.TemplateResponse(
                "perfil/alterar-senha.html",
                {"request": request, "erros": {"geral": msg_erro}, "usuario_logado": usuario_logado},
            )

    except ValidationError as e:
        # Não preservar senhas no formulário por segurança
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="perfil/alterar-senha.html",
            dados_formulario={},
            campo_padrao="confirmar_senha",
            mensagem_flash="Há campos com erros de validação!",
        )
    # Removido except Exception duplicado - global handler cuida disso


@router.post("/usuario/perfil/atualizar-foto")
@requer_autenticacao()
async def post_atualizar_foto(
    request: Request,
    foto_base64: str = Form(),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Upload de foto de perfil cropada"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Capturar ID do usuário ANTES do try para garantir disponibilidade no except
    usuario_id = usuario_logado.id

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not upload_foto_limiter.verificar(ip):
        informar_erro(
            request,
            f"Muitas tentativas de upload de foto. Aguarde {upload_foto_limiter.janela_minutos} minuto(s).",
        )
        logger.warning(f"Rate limit excedido para upload de foto - IP: {ip}")
        return RedirectResponse(
            "/usuario/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        # Validação básica
        if not foto_base64 or len(foto_base64) < 100:
            informar_erro(request, "Foto inválida. Por favor, tente novamente.")
            return RedirectResponse(
                "/usuario/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER
            )

        # Validar tamanho aproximado (base64 é ~33% maior que binário)
        tamanho_aproximado = len(foto_base64) * 3 / 4
        max_size = 10 * 1024 * 1024  # 10MB
        if tamanho_aproximado > max_size:
            informar_erro(request, "Imagem muito grande. O tamanho máximo é 10MB.")
            return RedirectResponse(
                "/usuario/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER
            )

        # Salvar foto cropada
        if salvar_foto_cropada_usuario(usuario_id, foto_base64):
            logger.info(f"Foto de perfil atualizada - Usuário ID: {usuario_id}")
            informar_sucesso(request, "Foto de perfil atualizada com sucesso!")
        else:
            msg_erro = (
                "Ocorreu um erro desconhecido ao atualizar foto. "
                "A equipe de suporte foi notificada. Tente novamente mais tarde."
            )
            informar_erro(request, msg_erro)

        return RedirectResponse(
            "/usuario/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER
        )

    except (ValueError, IOError, OSError) as e:
        # Erros de validação de dados (base64 inválido) ou I/O (escrita de arquivo)
        logger.error(f"Erro ao fazer upload de foto - Usuário ID {usuario_id}: {e}")
        msg_erro = (
            "Ocorreu um erro ao processar a imagem. "
            "Verifique se o arquivo é uma imagem válida e tente novamente."
        )
        informar_erro(request, msg_erro)
        return RedirectResponse(
            "/usuario/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER
        )
