"""Rotas administrativas para gerenciamento de Categorias."""

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
from dtos.categoria_dto import CriarCategoriaDTO, AlterarCategoriaDTO

# Models
from model.categoria_model import Categoria
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import categoria_repo

# Utilities
from util.auth_decorator import requer_autenticacao
from util.exceptions import ErroValidacaoFormulario
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.repository_helpers import obter_ou_404
from util.template_util import criar_templates

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/admin/categorias")
templates = criar_templates()

# =============================================================================
# Rate Limiter
# =============================================================================

categoria_limiter = DynamicRateLimiter(
    chave_max="rate_limit_admin_categoria_max",
    chave_minutos="rate_limit_admin_categoria_minutos",
    padrao_max=30,
    padrao_minutos=1,
    nome="admin_categoria",
)


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Lista todas as categorias."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    categorias = categoria_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/categorias/listar.html",
        {"request": request, "categorias": categorias, "usuario_logado": usuario_logado},
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe formulário de cadastro."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "admin/categorias/cadastrar.html",
        {"request": request, "usuario_logado": usuario_logado},
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Cadastra uma nova categoria."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not categoria_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    dados_formulario: dict = {"nome": nome}

    try:
        dto = CriarCategoriaDTO(nome=nome)

        nova = Categoria(
            id=0,
            nome=dto.nome,
        )
        id_criado = categoria_repo.inserir(nova)
        if id_criado:
            informar_sucesso(request, "Categoria cadastrada com sucesso!")
            logger.info(f"Categoria #{id_criado} criada por admin {usuario_logado.id}")
        else:
            informar_erro(request, "Erro ao cadastrar categoria.")

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/categorias/cadastrar.html",
            dados_formulario=dados_formulario,
        )

    return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe formulário de edição."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    item = obter_ou_404(
        categoria_repo.obter_por_id(id),
        request,
        "Categoria não encontrada",
        "/admin/categorias/listar",
    )
    if isinstance(item, RedirectResponse):
        return item

    dados = item.__dict__.copy()
    return templates.TemplateResponse(
        "admin/categorias/editar.html",
        {
            "request": request,
            "categoria": item,
            "dados": dados,
            "usuario_logado": usuario_logado,
        },
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Altera uma categoria."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not categoria_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    item = obter_ou_404(
        categoria_repo.obter_por_id(id),
        request,
        "Categoria não encontrada",
        "/admin/categorias/listar",
    )
    if isinstance(item, RedirectResponse):
        return item

    dados_formulario: dict = {"id": id, "nome": nome}

    try:
        dto = AlterarCategoriaDTO(nome=nome)

        atualizado = Categoria(
            id=id,
            nome=dto.nome,
        )
        if categoria_repo.atualizar(atualizado):
            informar_sucesso(request, "Categoria atualizada com sucesso!")
            logger.info(f"Categoria #{id} alterada por admin {usuario_logado.id}")
        else:
            informar_erro(request, "Erro ao atualizar categoria.")

    except ValidationError as e:
        dados_formulario["categoria"] = item
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/categorias/editar.html",
            dados_formulario=dados_formulario,
        )

    return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    """Exclui uma categoria."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    if categoria_repo.excluir(id):
        informar_sucesso(request, "Categoria excluída com sucesso!")
        logger.info(f"Categoria #{id} excluída por admin {usuario_logado.id}")
    else:
        informar_erro(request, "Erro ao excluir categoria.")

    return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)
