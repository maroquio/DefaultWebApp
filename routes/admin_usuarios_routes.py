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
from dtos.usuario_dto import CriarUsuarioDTO, AlterarUsuarioDTO

# Models
from model.usuario_model import Usuario

# Repositories
from repo import usuario_repo

# Utilities
from util.auth_decorator import requer_autenticacao
from util.exceptions import ErroValidacaoFormulario
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.repository_helpers import obter_ou_404
from util.security import criar_hash_senha
from util.template_util import criar_templates
from util.validation_helpers import verificar_email_disponivel

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/admin/usuarios")
templates = criar_templates("templates/admin/usuarios")

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

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de usuários"""
    return RedirectResponse("/admin/usuarios/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os usuários do sistema"""
    usuarios = usuario_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/usuarios/listar.html",
        {"request": request, "usuarios": usuarios}
    )

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de usuário"""
    perfis = Perfil.valores()
    return templates.TemplateResponse(
        "admin/usuarios/cadastro.html",
        {"request": request, "perfis": perfis}
    )

@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    perfil: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Cadastra um novo usuário"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_usuarios_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/usuarios/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {"nome": nome, "email": email, "perfil": perfil}

    try:
        # Validar com DTO
        dto = CriarUsuarioDTO(
            nome=nome,
            email=email,
            senha=senha,
            perfil=perfil
        )

        # Verificar se e-mail já existe
        disponivel, mensagem_erro = verificar_email_disponivel(dto.email)
        if not disponivel:
            informar_erro(request, mensagem_erro)
            perfis = Perfil.valores()
            return templates.TemplateResponse(
                "admin/usuarios/cadastro.html",
                {
                    "request": request,
                    "perfis": perfis,
                    "dados": {"nome": nome, "email": email, "perfil": perfil}
                }
            )

        # Criar hash da senha
        senha_hash = criar_hash_senha(dto.senha)

        # Criar usuário
        usuario = Usuario(
            id=0,
            nome=dto.nome,
            email=dto.email,
            senha=senha_hash,
            perfil=dto.perfil
        )

        usuario_repo.inserir(usuario)
        logger.info(f"Usuário '{dto.email}' cadastrado por admin {usuario_logado['id']}")

        informar_sucesso(request, "Usuário cadastrado com sucesso!")
        return RedirectResponse("/admin/usuarios/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Adicionar perfis aos dados para renderizar o select no template
        dados_formulario["perfis"] = Perfil.valores()
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/usuarios/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="senha",
        )

@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de alteração de usuário"""
    # Obter usuário ou retornar 404
    usuario = obter_ou_404(
        usuario_repo.obter_por_id(id),
        request,
        "Usuário não encontrado",
        "/admin/usuarios/listar"
    )
    if isinstance(usuario, RedirectResponse):
        return usuario

    # Criar cópia dos dados do usuário sem o campo senha (para não expor hash no HTML)
    dados_usuario = usuario.__dict__.copy()
    dados_usuario.pop('senha', None)

    perfis = Perfil.valores()
    return templates.TemplateResponse(
        "admin/usuarios/editar.html",
        {
            "request": request,
            "usuario": usuario,
            "dados": dados_usuario,
            "perfis": perfis
        }
    )

@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    email: str = Form(...),
    perfil: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Altera dados de um usuário"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_usuarios_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/usuarios/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Obter usuário ou retornar 404
    usuario_atual = obter_ou_404(
        usuario_repo.obter_por_id(id),
        request,
        "Usuário não encontrado",
        "/admin/usuarios/listar"
    )
    if isinstance(usuario_atual, RedirectResponse):
        return usuario_atual

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {"id": id, "nome": nome, "email": email, "perfil": perfil}

    try:
        # Validar com DTO
        dto = AlterarUsuarioDTO(
            id=id,
            nome=nome,
            email=email,
            perfil=perfil
        )

        # Verificar se e-mail já existe em outro usuário
        disponivel, mensagem_erro = verificar_email_disponivel(dto.email, id)
        if not disponivel:
            informar_erro(request, mensagem_erro)
            perfis = Perfil.valores()
            return templates.TemplateResponse(
                "admin/usuarios/editar.html",
                {
                    "request": request,
                    "usuario": usuario_atual,
                    "perfis": perfis,
                    "dados": {"id": id, "nome": nome, "email": email, "perfil": perfil}
                }
            )

        # Atualizar usuário
        usuario_atualizado = Usuario(
            id=id,
            nome=dto.nome,
            email=dto.email,
            senha=usuario_atual.senha,  # Mantém senha existente
            perfil=dto.perfil
        )

        usuario_repo.alterar(usuario_atualizado)
        logger.info(f"Usuário {id} alterado por admin {usuario_logado['id']}")

        informar_sucesso(request, "Usuário alterado com sucesso!")
        return RedirectResponse("/admin/usuarios/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Adicionar perfis e usuario aos dados para renderizar o template
        dados_formulario["perfis"] = Perfil.valores()
        dados_formulario["usuario"] = usuario_repo.obter_por_id(id)
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/usuarios/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="email",
        )

@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui um usuário"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_usuarios_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/usuarios/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Obter usuário ou retornar 404
    usuario = obter_ou_404(
        usuario_repo.obter_por_id(id),
        request,
        "Usuário não encontrado",
        "/admin/usuarios/listar"
    )
    if isinstance(usuario, RedirectResponse):
        return usuario

    # Impedir exclusão do próprio usuário
    if usuario.id == usuario_logado["id"]:
        informar_erro(request, "Você não pode excluir seu próprio usuário")
        logger.warning(f"Admin {usuario_logado['id']} tentou excluir a si mesmo")
        return RedirectResponse("/admin/usuarios/listar", status_code=status.HTTP_303_SEE_OTHER)

    usuario_repo.excluir(id)
    logger.info(f"Usuário {id} ({usuario.email}) excluído por admin {usuario_logado['id']}")
    informar_sucesso(request, "Usuário excluído com sucesso!")
    return RedirectResponse("/admin/usuarios/listar", status_code=status.HTTP_303_SEE_OTHER)
