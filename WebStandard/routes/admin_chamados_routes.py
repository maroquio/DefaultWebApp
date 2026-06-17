"""
Rotas administrativas para gerenciamento de chamados.

Permite que administradores:
- Listem todos os chamados do sistema
- Respondam chamados
- Alterem status de chamados
- Fechem chamados
"""

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
from dtos.chamado_dto import AlterarStatusDTO
from dtos.chamado_interacao_dto import CriarInteracaoDTO

# Models
from model.chamado_model import StatusChamado
from model.chamado_interacao_model import ChamadoInteracao, TipoInteracao
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import chamado_repo, chamado_interacao_repo

# Utilities
from util.auth_decorator import requer_autenticacao
from util.datetime_util import agora
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

router = APIRouter(prefix="/admin/chamados")
templates = criar_templates()

# =============================================================================
# Rate Limiters
# =============================================================================

admin_chamado_responder_limiter = DynamicRateLimiter(
    chave_max="rate_limit_admin_chamado_responder_max",
    chave_minutos="rate_limit_admin_chamado_responder_minutos",
    padrao_max=20,
    padrao_minutos=5,
    nome="admin_chamado_responder",
)


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Lista todos os chamados do sistema (apenas administradores)."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    # Passa ID do admin para contar apenas mensagens de OUTROS usuários
    chamados = chamado_repo.obter_todos(usuario_logado.id)
    return templates.TemplateResponse(
        "admin/chamados/listar.html",
        {"request": request, "chamados": chamados, "usuario_logado": usuario_logado}
    )


@router.get("/{id}/responder")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_responder(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe formulário para responder um chamado com histórico completo."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Obter chamado ou retornar 404
    chamado = obter_ou_404(
        chamado_repo.obter_por_id(id),
        request,
        "Chamado não encontrado",
        "/admin/chamados/listar"
    )
    if isinstance(chamado, RedirectResponse):
        return chamado

    # Marcar mensagens como lidas (apenas as de outros usuários)
    chamado_interacao_repo.marcar_como_lidas(id, usuario_logado.id)

    # Obter histórico de interações
    interacoes = chamado_interacao_repo.obter_por_chamado(id)

    return templates.TemplateResponse(
        "admin/chamados/responder.html",
        {"request": request, "chamado": chamado, "interacoes": interacoes, "usuario_logado": usuario_logado}
    )


@router.post("/{id}/responder")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_responder(
    request: Request,
    id: int,
    mensagem: str = Form(),
    status_chamado: str = Form(),
    usuario_logado: Optional[UsuarioLogado] = None
):
    """Salva resposta do administrador ao chamado e atualiza status."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not admin_chamado_responder_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas tentativas de resposta. Aguarde alguns minutos.",
        )
        logger.warning(f"Rate limit excedido para admin responder chamado - IP: {ip}")
        return RedirectResponse(f"/admin/chamados/{id}/responder", status_code=status.HTTP_303_SEE_OTHER)

    # Obter chamado ou retornar 404
    chamado = obter_ou_404(
        chamado_repo.obter_por_id(id),
        request,
        "Chamado não encontrado",
        "/admin/chamados/listar"
    )
    if isinstance(chamado, RedirectResponse):
        return chamado

    # Obter interações para reexibir em caso de erro
    interacoes = chamado_interacao_repo.obter_por_chamado(id)

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {
        "mensagem": mensagem,
        "status_chamado": status_chamado,
        "chamado": chamado,
        "interacoes": interacoes
    }

    try:
        # Validar mensagem e status
        dto_mensagem = CriarInteracaoDTO(mensagem=mensagem)
        dto_status = AlterarStatusDTO(status=status_chamado)

        # Criar interação do admin
        interacao = ChamadoInteracao(
            id=0,
            chamado_id=id,
            usuario_id=usuario_logado.id,
            mensagem=dto_mensagem.mensagem,
            tipo=TipoInteracao.RESPOSTA_ADMIN,
            data_interacao=agora(),
            status_resultante=dto_status.status
        )
        chamado_interacao_repo.inserir(interacao)

        # Atualizar status do chamado
        fechar = (dto_status.status == StatusChamado.FECHADO.value)
        sucesso = chamado_repo.atualizar_status(
            id=id,
            status=dto_status.status,
            fechar=fechar
        )

        if sucesso:
            logger.info(
                f"Chamado {id} respondido por admin {usuario_logado.id}, status: {dto_status.status}"
            )
            informar_sucesso(request, "Resposta salva com sucesso!")
            return RedirectResponse("/admin/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)
        else:
            informar_erro(request, "Erro ao salvar resposta")
            return RedirectResponse(f"/admin/chamados/{id}/responder", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/chamados/responder.html",
            dados_formulario=dados_formulario,
            campo_padrao="mensagem",
        )


@router.post("/{id}/fechar")
@requer_autenticacao([Perfil.ADMIN.value])
async def fechar(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    """Fecha um chamado alterando apenas o status, sem adicionar mensagem."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Obter chamado ou retornar 404
    chamado = obter_ou_404(
        chamado_repo.obter_por_id(id),
        request,
        "Chamado não encontrado",
        "/admin/chamados/listar"
    )
    if isinstance(chamado, RedirectResponse):
        return chamado

    sucesso = chamado_repo.atualizar_status(
        id=id,
        status=StatusChamado.FECHADO.value,
        fechar=True
    )

    if sucesso:
        logger.info(f"Chamado {id} fechado por admin {usuario_logado.id}")
        informar_sucesso(request, "Chamado fechado com sucesso!")
    else:
        informar_erro(request, "Erro ao fechar chamado")

    return RedirectResponse("/admin/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{id}/reabrir")
@requer_autenticacao([Perfil.ADMIN.value])
async def reabrir(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    """Reabre um chamado fechado, alterando status para 'Em Análise'."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Obter chamado ou retornar 404
    chamado = obter_ou_404(
        chamado_repo.obter_por_id(id),
        request,
        "Chamado não encontrado",
        "/admin/chamados/listar"
    )
    if isinstance(chamado, RedirectResponse):
        return chamado

    # Verificar se o chamado está fechado
    if chamado.status != StatusChamado.FECHADO:
        informar_erro(request, "Apenas chamados fechados podem ser reabertos")
        return RedirectResponse("/admin/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    sucesso = chamado_repo.atualizar_status(
        id=id,
        status=StatusChamado.EM_ANALISE.value,
        fechar=False
    )

    if sucesso:
        logger.info(f"Chamado {id} reaberto por admin {usuario_logado.id}")
        informar_sucesso(request, "Chamado reaberto com sucesso!")
    else:
        informar_erro(request, "Erro ao reabrir chamado")

    return RedirectResponse("/admin/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)
