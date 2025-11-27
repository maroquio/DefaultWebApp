"""
Middleware de proteção CSRF para FastAPI.

Implementa validação de tokens CSRF baseada em sessões para proteger
contra ataques Cross-Site Request Forgery.
"""
import secrets
from typing import Callable, Optional
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from util.logger_config import logger


# Nome da chave na sessão onde o token CSRF é armazenado
CSRF_SESSION_KEY = "_csrf_token"

# Nome do campo no formulário/header para o token CSRF
CSRF_FORM_FIELD = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"

# Métodos HTTP que requerem validação CSRF
CSRF_PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Rotas que NÃO requerem CSRF (API endpoints, health check, etc.)
CSRF_EXEMPT_PATHS = {
    "/health",
    "/api/",  # Endpoints de API podem usar outros métodos de auth
}


def gerar_token_csrf() -> str:
    """
    Gera um token CSRF aleatório e seguro

    Returns:
        String hex aleatória de 32 bytes
    """
    return secrets.token_hex(32)


def obter_token_csrf(request: Request) -> str:
    """
    Obtém ou cria token CSRF da sessão

    Args:
        request: Request object do FastAPI

    Returns:
        Token CSRF da sessão (cria novo se não existir)
    """
    # Obter token existente da sessão
    token = request.session.get(CSRF_SESSION_KEY)

    # Se não existe, criar novo
    if not token:
        token = gerar_token_csrf()
        request.session[CSRF_SESSION_KEY] = token
        logger.debug("Novo token CSRF gerado para sessão")

    return token


def validar_token_csrf(request: Request, token_from_form: Optional[str]) -> bool:
    """
    Valida token CSRF contra o token da sessão

    Args:
        request: Request object do FastAPI
        token_from_form: Token recebido do formulário ou header

    Returns:
        True se token é válido, False caso contrário
    """
    # Obter token esperado da sessão
    expected_token = request.session.get(CSRF_SESSION_KEY)

    # Se não há token na sessão, algo está errado
    if not expected_token:
        logger.warning("Token CSRF não encontrado na sessão")
        return False

    # Se não foi enviado token, inválido
    if not token_from_form:
        logger.warning("Token CSRF não foi enviado no request")
        return False

    # Comparação constant-time para prevenir timing attacks
    return secrets.compare_digest(expected_token, token_from_form)


def esta_isento_csrf(path: str) -> bool:
    """
    Verifica se um caminho está isento de validação CSRF

    Args:
        path: Caminho da URL (ex: "/login", "/api/users")

    Returns:
        True se caminho está isento, False caso contrário
    """
    for exempt_path in CSRF_EXEMPT_PATHS:
        if path.startswith(exempt_path):
            return True
    return False


class MiddlewareProtecaoCSRF(BaseHTTPMiddleware):
    """
    Middleware de proteção CSRF

    Valida tokens CSRF em requests POST/PUT/PATCH/DELETE
    e injeta token no contexto para uso em templates.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processa request e valida CSRF se necessário

        NOTA: Por limitações do Starlette, a validação completa de CSRF
        será feita nos route handlers usando dependency injection.
        Este middleware apenas prepara o contexto.

        Args:
            request: Request object
            call_next: Próximo handler na cadeia

        Returns:
            Response do handler
        """
        # Por enquanto, apenas logar requisições protegidas
        # A validação real será feita via dependency nos handlers
        if request.method in CSRF_PROTECTED_METHODS:
            if not esta_isento_csrf(request.url.path):
                logger.debug(f"CSRF-protected request: {request.method} {request.url.path}")

        # Continuar processamento normalmente
        response = await call_next(request)
        return response


def contexto_token_csrf(request: Request) -> dict:
    """
    Retorna contexto com token CSRF para injeção em templates

    Args:
        request: Request object

    Returns:
        Dict com função csrf_input() e csrf_token
    """
    token = obter_token_csrf(request)

    # Função helper para gerar input HTML
    def csrf_input():
        return f'<input type="hidden" name="{CSRF_FORM_FIELD}" value="{token}">'

    return {
        "csrf_token": token,
        "csrf_input": csrf_input,
        "csrf_form_field": CSRF_FORM_FIELD,
    }
