from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.artigo_dto import CriarArtigoDTO, AlterarArtigoDTO
from model.artigo_model import Artigo, StatusArtigo
from model.usuario_logado_model import UsuarioLogado
from repo import artigo_repo, categoria_repo
from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.exceptions import ErroValidacaoFormulario
from util.perfis import Perfil
from util.template_util import criar_templates
from util.logger_config import logger

router = APIRouter(prefix="/artigos")
templates = criar_templates()

# Rate limiter dinâmico: valores podem ser alterados via configuração
artigos_limiter = DynamicRateLimiter(
    chave_max="rate_limit_artigos_max",
    chave_minutos="rate_limit_artigos_minutos",
    padrao_max=20,
    padrao_minutos=1,
    nome="artigos"
)


@router.get("/meus")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def meus_artigos(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    """Lista os artigos do autor logado."""
    artigos = artigo_repo.obter_por_usuario(usuario_logado.id)

    return templates.TemplateResponse(
        "artigos/listar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "artigos": artigos,
            "status_artigo": StatusArtigo,
        },
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def get_cadastrar(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exibe o formulário de cadastro de artigo."""
    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "artigos/cadastrar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "categorias": categorias,
            "status_artigo": StatusArtigo,
        },
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
    titulo: str = Form(""),
    resumo: str = Form(""),
    conteudo: str = Form(""),
    acao: str = Form("rascunho"),
    categoria_id: int = Form(0),
):
    """Processa o cadastro de um novo artigo."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    ip = obter_identificador_cliente(request)
    if not artigos_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente.",
        )
        return RedirectResponse(
            url="/artigos/cadastrar",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    categorias = categoria_repo.obter_todos()

    # Determina status baseado na ação do botão clicado
    status_artigo = "Rascunho" if acao == "rascunho" else "Finalizado"

    try:
        dto = CriarArtigoDTO(
            titulo=titulo,
            resumo=resumo,
            conteudo=conteudo,
            status=status_artigo,
            categoria_id=categoria_id
        )

        # Verifica se título já existe
        if artigo_repo.titulo_existe(dto.titulo):
            informar_erro(request, "Já existe um artigo com este título.")
            return RedirectResponse(
                url="/artigos/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        novo_artigo = Artigo(
            id=0,
            titulo=dto.titulo,
            resumo=dto.resumo,
            conteudo=dto.conteudo,
            status=dto.status,
            usuario_id=usuario_logado.id,
            categoria_id=dto.categoria_id
        )

        artigo_id = artigo_repo.inserir(novo_artigo)

        if artigo_id:
            logger.info(f"Artigo '{dto.titulo}' criado por usuário {usuario_logado.id}")
            informar_sucesso(request, "Artigo cadastrado com sucesso!")
            return RedirectResponse(
                url="/artigos/meus",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            informar_erro(request, "Erro ao cadastrar artigo.")
            return RedirectResponse(
                url="/artigos/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER,
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="artigos/cadastrar.html",
            dados_formulario={
                "titulo": titulo,
                "resumo": resumo,
                "conteudo": conteudo,
                "categoria_id": categoria_id,
                "categorias": categorias,
            },
            campo_padrao="titulo",
        )


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def get_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exibe o formulário de edição de artigo."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    artigo = artigo_repo.obter_por_id(id)

    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica se o usuário é o autor do artigo ou admin
    if artigo.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
        informar_erro(request, "Você não tem permissão para editar este artigo.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "artigos/editar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "artigo": artigo,
            "categorias": categorias,
            "status_artigo": StatusArtigo,
        },
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
    titulo: str = Form(""),
    resumo: str = Form(""),
    conteudo: str = Form(""),
    acao: str = Form("rascunho"),
    categoria_id: int = Form(0),
):
    """Processa a edição de um artigo."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    ip = obter_identificador_cliente(request)
    if not artigos_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente.",
        )
        return RedirectResponse(
            url=f"/artigos/editar/{id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    artigo_atual = artigo_repo.obter_por_id(id)
    if not artigo_atual:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica permissão
    if artigo_atual.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
        informar_erro(request, "Você não tem permissão para editar este artigo.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    categorias = categoria_repo.obter_todos()

    # Determina status baseado na ação do botão clicado
    status_artigo = "Rascunho" if acao == "rascunho" else "Finalizado"

    try:
        dto = AlterarArtigoDTO(
            id=id,
            titulo=titulo,
            resumo=resumo,
            conteudo=conteudo,
            status=status_artigo,
            categoria_id=categoria_id
        )

        # Verifica duplicidade de título
        if dto.titulo != artigo_atual.titulo and artigo_repo.titulo_existe(dto.titulo, id):
            informar_erro(request, "Já existe um artigo com este título.")
            return RedirectResponse(
                url=f"/artigos/editar/{id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        artigo_atual.titulo = dto.titulo
        artigo_atual.resumo = dto.resumo
        artigo_atual.conteudo = dto.conteudo
        artigo_atual.status = dto.status
        artigo_atual.categoria_id = dto.categoria_id

        if artigo_repo.alterar(artigo_atual):
            logger.info(f"Artigo {id} alterado por usuário {usuario_logado.id}")
            informar_sucesso(request, "Artigo alterado com sucesso!")
            return RedirectResponse(
                url="/artigos/meus",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            informar_erro(request, "Erro ao alterar artigo.")
            return RedirectResponse(
                url=f"/artigos/editar/{id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="artigos/editar.html",
            dados_formulario={
                "titulo": titulo,
                "resumo": resumo,
                "conteudo": conteudo,
                "categoria_id": categoria_id,
                "id": id,
                "artigo": artigo_atual,
                "categorias": categorias,
            },
            campo_padrao="titulo",
        )


@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def post_excluir(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exclui um artigo."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    ip = obter_identificador_cliente(request)
    if not artigos_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    artigo = artigo_repo.obter_por_id(id)
    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica permissão
    if artigo.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
        informar_erro(request, "Você não tem permissão para excluir este artigo.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if artigo_repo.excluir(id):
        logger.info(f"Artigo {id} excluído por usuário {usuario_logado.id}")
        informar_sucesso(request, f"Artigo '{artigo.titulo}' excluído com sucesso!")
    else:
        informar_erro(request, "Erro ao excluir artigo.")

    return RedirectResponse(
        url="/artigos/meus",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/publicar/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def post_publicar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Publica um artigo."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    artigo = artigo_repo.obter_por_id(id)
    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica permissão
    if artigo.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
        informar_erro(request, "Você não tem permissão para publicar este artigo.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if artigo_repo.alterar_status(id, StatusArtigo.PUBLICADO.value):
        logger.info(f"Artigo {id} publicado por usuário {usuario_logado.id}")
        informar_sucesso(request, "Artigo publicado com sucesso!")
    else:
        informar_erro(request, "Erro ao publicar artigo.")

    return RedirectResponse(
        url="/artigos/meus",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/pausar/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def post_pausar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Pausa um artigo publicado."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    artigo = artigo_repo.obter_por_id(id)
    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica permissão
    if artigo.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
        informar_erro(request, "Você não tem permissão para pausar este artigo.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if artigo_repo.alterar_status(id, StatusArtigo.PAUSADO.value):
        logger.info(f"Artigo {id} pausado por usuário {usuario_logado.id}")
        informar_sucesso(request, "Artigo pausado com sucesso!")
    else:
        informar_erro(request, "Erro ao pausar artigo.")

    return RedirectResponse(
        url="/artigos/meus",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# =====================================================
# ROTAS PÚBLICAS (para leitores)
# =====================================================

@router.get("/")
async def listar_artigos(
    request: Request,
    q: str = "",
    categoria: int = 0,
    ordem: str = "recentes",
):
    """Lista artigos publicados com busca e filtros."""
    from util.auth_decorator import obter_usuario_logado
    usuario_logado = obter_usuario_logado(request)

    if q:
        artigos = artigo_repo.buscar_por_titulo(q)
    elif categoria > 0:
        artigos = artigo_repo.obter_por_categoria(categoria)
    else:
        artigos = artigo_repo.obter_publicados()

    # Ordenação
    if ordem == "antigos":
        artigos = sorted(artigos, key=lambda a: a.data_publicacao or a.data_cadastro or datetime.min)
    elif ordem == "visualizacoes":
        artigos = sorted(artigos, key=lambda a: a.qtde_visualizacoes or 0, reverse=True)
    # Default é "recentes" (já vem ordenado do banco)

    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "artigos/buscar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "artigos": artigos,
            "categorias": categorias,
            "termo_busca": q,
            "categoria_selecionada": categoria,
            "ordem_selecionada": ordem,
        },
    )


@router.get("/ler/{id}")
@requer_autenticacao()
async def ler_artigo(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exibe um artigo completo (somente para usuários autenticados)."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    artigo = artigo_repo.obter_por_id(id)

    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(
            url="/artigos",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica se o artigo está publicado ou se o usuário é o autor/admin
    if artigo.status != StatusArtigo.PUBLICADO.value:
        if artigo.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
            informar_erro(request, "Este artigo não está disponível.")
            return RedirectResponse(
                url="/artigos",
                status_code=status.HTTP_303_SEE_OTHER,
            )

    # Incrementa visualizações apenas para artigos publicados
    if artigo.status == StatusArtigo.PUBLICADO.value:
        artigo_repo.incrementar_visualizacoes(id)
        artigo.qtde_visualizacoes = (artigo.qtde_visualizacoes or 0) + 1

    return templates.TemplateResponse(
        "artigos/ler.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "artigo": artigo,
        },
    )