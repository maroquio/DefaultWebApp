from typing import Optional

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

# DTOs e modelo
from dtos.categoria_dto import CriarCategoriaDTO, AlterarCategoriaDTO
from model.categoria_model import Categoria
from model.usuario_logado_model import UsuarioLogado

# Repositório
from repo import categoria_repo

# Utilitários
from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.exceptions import ErroValidacaoFormulario
from util.perfis import Perfil
from util.template_util import criar_templates

# ----------------------------------------------------------------------
# Configurações do router e dos templates
# ----------------------------------------------------------------------
router = APIRouter(prefix="/admin/categorias")
templates = criar_templates()

# Rate limiter dinâmico: valores podem ser alterados via configuração
admin_categorias_limiter = DynamicRateLimiter(
    chave_max="rate_limit_admin_categorias_max",
    chave_minutos="rate_limit_admin_categorias_minutos",
    padrao_max=10,
    padrao_minutos=1,
    nome="admin_categorias"
)

# ----------------------------------------------------------------------
# Rotas
# ----------------------------------------------------------------------

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Redireciona a raiz para /listar
    """
    return RedirectResponse(
        url="/admin/categorias/listar",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Lista todas as categorias.
    Acessível em: GET /admin/categorias/listar
    """
    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "admin/categorias/listar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "categorias": categorias,
        },
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Exibe o formulário de cadastro.
    Acessível em: GET /admin/categorias/cadastrar
    """
    return templates.TemplateResponse(
        "admin/categorias/cadastrar.html",
        {"request": request, "usuario_logado": usuario_logado},
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
    nome: str = Form(""),
    descricao: str = Form(""),
):
    """
    Processa o cadastro de uma nova categoria.
    Acessível em: POST /admin/categorias/cadastrar
    """
    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente.",
        )
        return RedirectResponse(
            url="/admin/categorias/cadastrar",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Lógica de criação
    try:
        dto = CriarCategoriaDTO(nome=nome, descricao=descricao)

        # Verifica duplicidade
        categoria_existente = categoria_repo.obter_por_nome(dto.nome)
        if categoria_existente:
            informar_erro(request, "Já existe uma categoria com este nome.")
            return RedirectResponse(
                url="/admin/categorias/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        nova_categoria = Categoria(nome=dto.nome, descricao=dto.descricao)
        categoria_inserida = categoria_repo.inserir(nova_categoria)

        if categoria_inserida:
            informar_sucesso(request, "Categoria cadastrada com sucesso!")
            return RedirectResponse(
                url="/admin/categorias/listar",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            informar_erro(request, "Erro ao cadastrar categoria.")
            return RedirectResponse(
                url="/admin/categorias/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER,
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/categorias/cadastrar.html",
            dados_formulario={"nome": nome, "descricao": descricao},
            campo_padrao="nome",
        )


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Exibe o formulário de edição de uma categoria.
    Acessível em: GET /admin/categorias/editar/<id>
    """
    categoria = categoria_repo.obter_por_id(id)

    if not categoria:
        informar_erro(request, "Categoria não encontrada.")
        return RedirectResponse(
            url="/admin/categorias/listar",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return templates.TemplateResponse(
        "admin/categorias/editar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "categoria": categoria,
        },
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
    nome: str = Form(""),
    descricao: str = Form(""),
):
    """
    Processa a edição de uma categoria.
    Acessível em: POST /admin/categorias/editar/<id>
    """
    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente.",
        )
        return RedirectResponse(
            url=f"/admin/categorias/editar/{id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Busca a categoria
    categoria_atual = categoria_repo.obter_por_id(id)
    if not categoria_atual:
        informar_erro(request, "Categoria não encontrada.")
        return RedirectResponse(
            url="/admin/categorias/listar",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    try:
        dto = AlterarCategoriaDTO(nome=nome, descricao=descricao)

        # Se o nome mudou, verifica duplicidade
        if dto.nome != categoria_atual.nome:
            categoria_existente = categoria_repo.obter_por_nome(dto.nome)
            if categoria_existente:
                informar_erro(request, "Já existe uma categoria com este nome.")
                return RedirectResponse(
                    url=f"/admin/categorias/editar/{id}",
                    status_code=status.HTTP_303_SEE_OTHER,
                )

        # Atualiza os campos
        categoria_atual.nome = dto.nome
        categoria_atual.descricao = dto.descricao

        if categoria_repo.alterar(categoria_atual):
            informar_sucesso(request, "Categoria alterada com sucesso!")
            return RedirectResponse(
                url="/admin/categorias/listar",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            informar_erro(request, "Erro ao alterar categoria.")
            return RedirectResponse(
                url=f"/admin/categorias/editar/{id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/categorias/editar.html",
            dados_formulario={
                "nome": nome,
                "descricao": descricao,
                "id": id,
            },
            campo_padrao="nome",
        )


# ----------------------------------------------------------------------
# Endpoint de Exclusão
# ----------------------------------------------------------------------
@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Exclui uma categoria.
    Acessível em: POST /admin/categorias/excluir/<id>
    """
    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            url="/admin/categorias/listar",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Busca a categoria
    categoria = categoria_repo.obter_por_id(id)
    if not categoria:
        informar_erro(request, "Categoria não encontrada.")
        return RedirectResponse(
            url="/admin/categorias/listar",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Exclui do banco
    if categoria_repo.excluir(id):
        informar_sucesso(request, f"Categoria '{categoria.nome}' excluída com sucesso!")
    else:
        informar_erro(request, "Erro ao excluir categoria.")

    return RedirectResponse(
        url="/admin/categorias/listar",
        status_code=status.HTTP_303_SEE_OTHER,
    )