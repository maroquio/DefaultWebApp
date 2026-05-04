# Imports
# =============================================================================

# Standard library
from typing import Optional

# Third-party
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

# DTOs

# Models
from model.usuario_logado_model import UsuarioLogado

# Repositories

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
    categorias = [
        {"id": 0, "nome": ""},
        {"id": 1, "nome": "cargas"},
        {"id": 2, "nome": "teste"},
        {"id": 3, "nome": "tesre"},
        {"id": 4, "nome": "trser"},
        {"id": 5, "nome": "ertredss"},
    ]
    return templates.TemplateResponse(
        "admin/cargas/cadastro.html",
        {"request": request, "usuario_logado": usuario_logado, "categorias": categorias},
    )


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "admin/cargas/listar.html",
        {"request": request, "cargas": [], "usuario_logado": usuario_logado},
    )
