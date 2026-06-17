"""
Rotas para o sistema de notificações in-app.

Endpoints disponíveis:
- GET  /notificacoes              → Lista todas as notificações do usuário
- GET  /notificacoes/nao-lidas    → JSON com contagem e lista de não lidas (para polling)
- POST /notificacoes/{id}/lida    → Marca notificação como lida
- POST /notificacoes/marcar-todas → Marca todas como lidas
- POST /notificacoes/{id}/excluir → Exclui notificação
- POST /notificacoes/excluir-lidas → Exclui todas as lidas
"""

from typing import Optional

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, RedirectResponse

from model.usuario_logado_model import UsuarioLogado
from repo import notificacao_repo
from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.paginacao_util import paginar
from util.template_util import criar_templates

router = APIRouter(prefix="/notificacoes")
templates = criar_templates()


@router.get("/")
@requer_autenticacao()
async def listar(
    request: Request,
    pagina: int = 1,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Lista todas as notificações do usuário com paginação."""
    assert usuario_logado is not None

    todas = notificacao_repo.obter_por_usuario(usuario_logado.id, limite=100)
    paginacao = paginar(todas, pagina=pagina, por_pagina=15)

    return templates.TemplateResponse(
        "notificacoes/listar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "paginacao": paginacao,
            "notificacoes": paginacao.items,
        },
    )


@router.get("/nao-lidas")
@requer_autenticacao()
async def obter_nao_lidas(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Retorna contagem e últimas notificações não lidas em JSON.

    Usado pelo frontend para polling (atualizar badge do navbar).
    Chamado a cada 30 segundos pelo JavaScript no navbar.

    Resposta:
        {
            "total": 3,
            "notificacoes": [
                {"id": 1, "titulo": "...", "mensagem": "...", "tipo": "sucesso", "url_acao": "/rota"}
            ]
        }
    """
    assert usuario_logado is not None

    total = notificacao_repo.contar_nao_lidas(usuario_logado.id)
    nao_lidas = notificacao_repo.obter_nao_lidas(usuario_logado.id, limite=5)

    return JSONResponse({
        "total": total,
        "notificacoes": [
            {
                "id": n.id,
                "titulo": n.titulo,
                "mensagem": n.mensagem,
                "tipo": n.tipo.value,
                "url_acao": n.url_acao,
                "data_criacao": n.data_criacao.isoformat() if n.data_criacao else None,
            }
            for n in nao_lidas
        ],
    })


@router.post("/{notificacao_id}/lida")
@requer_autenticacao()
async def marcar_lida(
    request: Request,
    notificacao_id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Marca uma notificação específica como lida e redireciona para url_acao se existir."""
    assert usuario_logado is not None

    # Buscar notificação para obter url_acao antes de marcar como lida
    notificacoes = notificacao_repo.obter_por_usuario(usuario_logado.id, limite=100)
    notificacao = next((n for n in notificacoes if n.id == notificacao_id), None)

    notificacao_repo.marcar_como_lida(notificacao_id, usuario_logado.id)

    # Redirecionar para url_acao se existir
    if notificacao and notificacao.url_acao:
        return RedirectResponse(
            url=notificacao.url_acao,
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return RedirectResponse(
        url="/notificacoes",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/marcar-todas")
@requer_autenticacao()
async def marcar_todas_lidas(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Marca todas as notificações do usuário como lidas."""
    assert usuario_logado is not None

    total = notificacao_repo.marcar_todas_como_lidas(usuario_logado.id)
    if total > 0:
        informar_sucesso(request, f"{total} notificação(ões) marcada(s) como lida(s).")
    else:
        informar_sucesso(request, "Não há notificações não lidas.")

    return RedirectResponse(
        url="/notificacoes",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{notificacao_id}/excluir")
@requer_autenticacao()
async def excluir(
    request: Request,
    notificacao_id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exclui uma notificação específica do usuário."""
    assert usuario_logado is not None

    sucesso = notificacao_repo.excluir(notificacao_id, usuario_logado.id)
    if sucesso:
        informar_sucesso(request, "Notificação excluída.")
    else:
        informar_erro(request, "Notificação não encontrada.")

    return RedirectResponse(
        url="/notificacoes",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/excluir-lidas")
@requer_autenticacao()
async def excluir_lidas(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exclui todas as notificações já lidas do usuário."""
    assert usuario_logado is not None

    total = notificacao_repo.excluir_lidas(usuario_logado.id)
    if total > 0:
        informar_sucesso(request, f"{total} notificação(ões) excluída(s).")
    else:
        informar_sucesso(request, "Não há notificações lidas para excluir.")

    return RedirectResponse(
        url="/notificacoes",
        status_code=status.HTTP_303_SEE_OTHER,
    )
