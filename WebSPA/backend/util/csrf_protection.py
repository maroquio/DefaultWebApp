"""
Middleware de proteção CSRF para FastAPI.

Implementa validação de tokens CSRF baseada em sessões para proteger
contra ataques Cross-Site Request Forgery.
"""
import secrets
from typing import Callable, Optional
from fastapi import Request
from fastapi.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from util.logger_config import logger


# Nome da chave na sessão onde o token CSRF é armazenado
CSRF_SESSION_KEY = "_csrf_token"

# Nome do header para o token CSRF (o SPA envia o token aqui)
CSRF_HEADER_NAME = "X-CSRF-Token"

# Métodos HTTP que requerem validação CSRF
CSRF_PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Rotas que NÃO requerem CSRF.
# IMPORTANTE: NÃO isentar "/api/" inteiro — as mutações da API são protegidas
# via header X-CSRF-Token. Apenas webhooks externos (server-to-server) são isentos.
CSRF_EXEMPT_PATHS = {
    "/health",
    "/api/pagamentos/webhook",  # Webhooks de pagamento (Mercado Pago / Stripe / PayPal)
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
    Middleware de proteção CSRF para API JSON.

    Em métodos mutantes (POST/PUT/PATCH/DELETE) não isentos, valida o token
    recebido no header ``X-CSRF-Token`` contra o token da sessão. Em caso de
    falha, responde 403 no contrato de erro padronizado.

    Requer que o SessionMiddleware seja externo a este (registrado DEPOIS no
    ``add_middleware``), para que ``request.session`` esteja disponível aqui.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in CSRF_PROTECTED_METHODS and not esta_isento_csrf(
            request.url.path
        ):
            token_header = request.headers.get(CSRF_HEADER_NAME)
            if not validar_token_csrf(request, token_header):
                logger.warning(
                    f"CSRF inválido: {request.method} {request.url.path} - "
                    f"IP: {request.client.host if request.client else 'unknown'}"
                )
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Token CSRF ausente ou inválido.",
                        "type": "forbidden",
                        "errors": None,
                    },
                )

        return await call_next(request)
