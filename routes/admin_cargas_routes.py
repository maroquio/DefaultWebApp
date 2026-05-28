# Imports
# =============================================================================

# Standard library
from typing import Optional

# Third-party
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

# DTOs
from dtos.carga_dto import CriarCargaDTO

# Models
from model.carga_model import Carga
from model.usuario_logado_model import UsuarioLogado

# Repositories

# Utilities
from repo import carga_repo
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

router = APIRouter(prefix="/admin/cargas")
templates = criar_templates()

# =============================================================================
# Rate Limiters
# =============================================================================

admin_cargas_limiter = DynamicRateLimiter(
    chave_max="rate_limit_admin_cargas_max",
    chave_minutos="rate_limit_admin_cargas_minutos",
    padrao_max=30,
    padrao_minutos=1,
    nome="admin_cargas",
)


@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def cadastrar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    categorias_carroceria = [
        {"id": 1, "nome": "Baú (Carga Seca)"},
        {"id": 2, "nome": "Sider"},
        {"id": 3, "nome": "Grade Baixa"},
        {"id": 4, "nome": "Graneleiro"},
        {"id": 5, "nome": "Prancha"},
        {"id": 6, "nome": "Frigorífico / Refrigerada"},
        {"id": 7, "nome": "Caçamba"},
        {"id": 8, "nome": "Tanque"},
    ]

    empresas = [
        {"id": 1, "nome": "Empresa A"},
        {"id": 2, "nome": "Empresa B"},
        {"id": 3, "nome": "Empresa C"},
    ]

    return templates.TemplateResponse(
        "admin/cargas/cadastro.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "categorias": categorias_carroceria,
            "empresas": empresas
        },
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    titulo: str = Form(...),
    origem: str = Form(...),
    destino: str = Form(...),
    peso: str = Form(...),
    valor: str = Form(...),
    id_categoria: int = Form(...),
    id_empresa: int = Form(...),
    status_carga: str = Form(...),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_cargas_limiter.verificar(ip):
        informar_erro(
            request, "Muitas operações. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            "/admin/cargas/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {
        "titulo": titulo,
        "origem": origem,
        "destino": destino,
        "peso": peso,
        "valor": valor,
        "id_categoria": id_categoria,
        "id_empresa": id_empresa,
        "status": status_carga,
    }

    try:
        # Validar com DTO
        dto = CriarCargaDTO(
            titulo=titulo,
            origem=origem,
            destino=destino,
            peso=float(peso.replace(",",".")),
            valor=float(valor.replace(",", ".")),
            id_categoria=id_categoria,
            id_empresa=id_empresa,
            status=status_carga,
        )

        # Monta a entidade (passando id=None para banco gerar automaticamente)
        carga = Carga(
            id=None,
            titulo=dto.titulo,
            origem=dto.origem,
            destino=dto.destino,
            peso=dto.peso,
            valor=dto.valor,
            id_categoria=dto.id_categoria,
            id_empresa=dto.id_empresa,
            status=dto.status,
        )

        carga_repo.inserir(carga)
        logger.info(f"Carga '{dto.titulo}' cadastrada por admin {usuario_logado.id}")

        informar_sucesso(request, "Carga cadastrada com sucesso!")
        return RedirectResponse(
            "/admin/cargas/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    except ValidationError as e:
        # Adicionar categorias e empresas aos dados para renderizar os selects no template
        # dados_formulario["categorias"] = categorias_carroceria
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/cargas/cadastrar.html",
            dados_formulario=dados_formulario,
            campo_padrao="titulo",
        )


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    cargas = []
    # Simulando dados da Carga para o front-end
    for i in range(1, 13):
        cargas.append(
            {
                "id": i,
                "titulo": f"Frete de Granito/Mármore {i}",
                "origem": "Cachoeiro de Itapemirim - ES",
                "destino": "São Paulo - SP",
                "peso": 12.5 + i,
                "valor": 3200.00 + (i * 100),
                "id_categoria": 1,
                "id_empresa": 1,
                "status": "Disponível",
            }
        )

    return templates.TemplateResponse(
        "admin/cargas/listar.html",
        # Alterado de "cargas": [] para "cargas": cargas
        {"request": request, "cargas": cargas, "usuario_logado": usuario_logado},
    )
