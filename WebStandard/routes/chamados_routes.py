"""
Rotas para gerenciamento de chamados por usuários não-administradores.

Permite que usuários comuns:
- Listem seus próprios chamados
- Abram novos chamados
- Visualizem detalhes de chamados
- Excluam chamados próprios
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
from dtos.chamado_dto import CriarChamadoDTO
from dtos.chamado_interacao_dto import CriarInteracaoDTO

# Models
from model.chamado_model import Chamado, StatusChamado, PrioridadeChamado
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
from util.permission_helpers import verificar_propriedade
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.repository_helpers import obter_ou_404
from util.template_util import criar_templates

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/chamados")
templates = criar_templates()

# =============================================================================
# Rate Limiters
# =============================================================================

chamado_criar_limiter = DynamicRateLimiter(
    chave_max="rate_limit_chamado_criar_max",
    chave_minutos="rate_limit_chamado_criar_minutos",
    padrao_max=5,
    padrao_minutos=30,
    nome="chamado_criar",
)
chamado_responder_limiter = DynamicRateLimiter(
    chave_max="rate_limit_chamado_responder_max",
    chave_minutos="rate_limit_chamado_responder_minutos",
    padrao_max=10,
    padrao_minutos=10,
    nome="chamado_responder",
)


@router.get("/listar")
@requer_autenticacao()
async def listar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Lista todos os chamados do usuário logado."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    # Passa usuario_id para obter_por_usuario - a função já usa esse ID
    # para contar apenas mensagens de OUTROS usuários
    chamados = chamado_repo.obter_por_usuario(usuario_logado.id)
    return templates.TemplateResponse(
        "chamados/listar.html",
        {"request": request, "chamados": chamados, "usuario_logado": usuario_logado}
    )


@router.get("/cadastrar")
@requer_autenticacao()
async def get_cadastrar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe formulário de abertura de chamado."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "chamados/cadastrar.html",
        {"request": request, "usuario_logado": usuario_logado}
    )


@router.post("/cadastrar")
@requer_autenticacao()
async def post_cadastrar(
    request: Request,
    titulo: str = Form(),
    descricao: str = Form(),
    prioridade: str = Form(default="Média"),
    usuario_logado: Optional[UsuarioLogado] = None
):
    """Cadastra um novo chamado."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not chamado_criar_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas tentativas de criação de chamados. Aguarde alguns minutos.",
        )
        logger.warning(f"Rate limit excedido para criação de chamados - IP: {ip}")
        return templates.TemplateResponse(
            "chamados/cadastrar.html",
            {
                "request": request,
                "erros": {
                    "geral": "Muitas tentativas de criação de chamados. Aguarde alguns minutos."
                },
                "usuario_logado": usuario_logado,
            },
        )

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "titulo": titulo,
        "descricao": descricao,
        "prioridade": prioridade
    }

    try:
        # Validar com DTO
        dto = CriarChamadoDTO(
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade
        )

        # Criar chamado (sem descricao - será armazenada na interacao)
        chamado = Chamado(
            id=0,
            titulo=dto.titulo,
            prioridade=PrioridadeChamado(dto.prioridade),
            status=StatusChamado.ABERTO,
            usuario_id=usuario_logado.id
        )

        chamado_id = chamado_repo.inserir(chamado)

        # Criar interação inicial com a descrição do chamado
        interacao = ChamadoInteracao(
            id=0,
            chamado_id=chamado_id,
            usuario_id=usuario_logado.id,
            mensagem=dto.descricao,
            tipo=TipoInteracao.ABERTURA,
            data_interacao=agora(),
            status_resultante=StatusChamado.ABERTO.value
        )
        chamado_interacao_repo.inserir(interacao)

        logger.info(
            f"Chamado #{chamado_id} '{dto.titulo}' criado por usuário {usuario_logado.id}"
        )

        informar_sucesso(request, "Chamado aberto com sucesso! Em breve responderemos.")
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="chamados/cadastrar.html",
            dados_formulario=dados_formulario,
            campo_padrao="titulo",
        )


@router.get("/{id}/visualizar")
@requer_autenticacao()
async def visualizar(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe detalhes de um chamado específico com histórico de interações."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Obter chamado ou retornar 404
    chamado = obter_ou_404(
        chamado_repo.obter_por_id(id),
        request,
        "Chamado não encontrado",
        "/chamados/listar"
    )
    if isinstance(chamado, RedirectResponse):
        return chamado

    # Verificar se usuário é proprietário do chamado
    if not verificar_propriedade(
        chamado,
        usuario_logado.id,
        request,
        "Você não tem permissão para acessar este chamado",
        "/chamados/listar"
    ):
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Marcar mensagens como lidas (apenas as de outros usuários)
    chamado_interacao_repo.marcar_como_lidas(id, usuario_logado.id)

    # Obter histórico de interações
    interacoes = chamado_interacao_repo.obter_por_chamado(id)

    return templates.TemplateResponse(
        "chamados/visualizar.html",
        {"request": request, "chamado": chamado, "interacoes": interacoes, "usuario_logado": usuario_logado}
    )


@router.post("/{id}/responder")
@requer_autenticacao()
async def post_responder(
    request: Request,
    id: int,
    mensagem: str = Form(),
    usuario_logado: Optional[UsuarioLogado] = None
):
    """Permite que o usuário adicione uma resposta/mensagem ao seu próprio chamado."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not chamado_responder_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas tentativas de resposta em chamados. Aguarde alguns minutos.",
        )
        logger.warning(f"Rate limit excedido para resposta em chamados - IP: {ip}")
        return RedirectResponse(f"/chamados/{id}/visualizar", status_code=status.HTTP_303_SEE_OTHER)

    # Obter chamado ou retornar 404
    chamado = obter_ou_404(
        chamado_repo.obter_por_id(id),
        request,
        "Chamado não encontrado",
        "/chamados/listar"
    )
    if isinstance(chamado, RedirectResponse):
        return chamado

    # Verificar se usuário é proprietário do chamado
    if not verificar_propriedade(
        chamado,
        usuario_logado.id,
        request,
        "Você não tem permissão para responder a este chamado",
        "/chamados/listar"
    ):
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Armazena os dados do formulário para reexibição em caso de erro
    interacoes = chamado_interacao_repo.obter_por_chamado(id)
    dados_formulario: dict = {
        "mensagem": mensagem,
        "chamado": chamado,
        "interacoes": interacoes
    }

    try:
        # Validar com DTO
        dto = CriarInteracaoDTO(mensagem=mensagem)

        # Criar nova interação do usuário
        interacao = ChamadoInteracao(
            id=0,
            chamado_id=id,
            usuario_id=usuario_logado.id,
            mensagem=dto.mensagem,
            tipo=TipoInteracao.RESPOSTA_USUARIO,
            data_interacao=agora(),
            status_resultante=chamado.status.value  # Mantém status atual
        )
        chamado_interacao_repo.inserir(interacao)

        logger.info(
            f"Usuário {usuario_logado.id} respondeu ao chamado {id}"
        )

        informar_sucesso(request, "Resposta adicionada com sucesso!")
        return RedirectResponse(f"/chamados/{id}/visualizar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="chamados/visualizar.html",
            dados_formulario=dados_formulario,
            campo_padrao="mensagem",
        )


@router.post("/{id}/excluir")
@requer_autenticacao()
async def post_excluir(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    """Exclui um chamado do usuário (apenas se aberto e sem respostas de admin)."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Obter chamado ou retornar 404
    chamado = obter_ou_404(
        chamado_repo.obter_por_id(id),
        request,
        "Chamado não encontrado",
        "/chamados/listar"
    )
    if isinstance(chamado, RedirectResponse):
        return chamado

    # Verificar se usuário é proprietário do chamado
    if not verificar_propriedade(
        chamado,
        usuario_logado.id,
        request,
        "Você não tem permissão para excluir este chamado",
        "/chamados/listar"
    ):
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se chamado está aberto
    if chamado.status != StatusChamado.ABERTO:
        informar_erro(request, "Apenas chamados abertos podem ser excluídos")
        logger.warning(
            f"Usuário {usuario_logado.id} tentou excluir chamado {id} com status {chamado.status.value}"
        )
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se há respostas de administrador
    if chamado_interacao_repo.tem_resposta_admin(id):
        informar_erro(request, "Não é possível excluir chamados que já possuem resposta do administrador")
        logger.warning(
            f"Usuário {usuario_logado.id} tentou excluir chamado {id} que possui respostas de admin"
        )
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Tudo OK, pode excluir
    chamado_repo.excluir(id)
    logger.info(f"Chamado {id} excluído por usuário {usuario_logado.id}")
    informar_sucesso(request, "Chamado excluído com sucesso!")

    return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)
