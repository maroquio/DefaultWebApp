"""
Handlers globais de exceção para a API JSON do WebSPA.

Todos os handlers retornam o contrato de erro padronizado:

    {
        "detail": "<mensagem legível>",
        "type":   "<categoria do erro>",
        "errors": { "campo": ["msg", ...] } | null
    }

Nenhum handler renderiza template — esta é uma API pura.
"""
from typing import Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback

from util.logger_config import logger
from util.config import IS_DEVELOPMENT
from util.validation_util import processar_erros_validacao_lista


# Mapeia status HTTP -> "type" do contrato de erro
_TIPOS_POR_STATUS = {
    status.HTTP_400_BAD_REQUEST: "bad_request",
    status.HTTP_401_UNAUTHORIZED: "unauthorized",
    status.HTTP_403_FORBIDDEN: "forbidden",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_409_CONFLICT: "conflict",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "validation_error",
    status.HTTP_429_TOO_MANY_REQUESTS: "rate_limited",
}


def resposta_erro(
    status_code: int,
    detail: str,
    tipo: Optional[str] = None,
    errors: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> JSONResponse:
    """Monta uma resposta JSON no contrato de erro padronizado."""
    if tipo is None:
        tipo = _TIPOS_POR_STATUS.get(status_code, "error")
        if status_code >= 500:
            tipo = "internal_error"
    corpo = {"detail": detail, "type": tipo, "errors": errors}
    return JSONResponse(status_code=status_code, content=corpo, headers=headers)


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> Response:
    """Handler para HTTPException — converte para o contrato de erro JSON."""
    status_code = exc.status_code

    STATIC_OPTIONAL_EXTENSIONS = (".map", ".ico", ".woff", ".woff2", ".ttf", ".eot")
    path_lower = request.url.path.lower()
    is_optional_static = status_code == 404 and path_lower.endswith(
        STATIC_OPTIONAL_EXTENSIONS
    )

    log_message = (
        f"HTTPException {status_code}: {exc.detail} - "
        f"Path: {request.url.path} - "
        f"IP: {request.client.host if request.client else 'unknown'}"
    )
    if is_optional_static:
        logger.debug(log_message)
    else:
        logger.warning(log_message)

    # exc.detail pode ser dict (quando a rota lança detalhes estruturados) ou str
    detail = exc.detail if isinstance(exc.detail, str) else "Erro ao processar a solicitação."
    errors = exc.detail.get("errors") if isinstance(exc.detail, dict) else None
    tipo = exc.detail.get("type") if isinstance(exc.detail, dict) else None
    if isinstance(exc.detail, dict) and "detail" in exc.detail:
        detail = exc.detail["detail"]

    return resposta_erro(
        status_code,
        detail,
        tipo=tipo,
        errors=errors,
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> Response:
    """Handler para erros de validação do Pydantic (body/query inválidos) -> 422."""
    logger.warning(
        f"Erro de validação: {exc.errors()} - Path: {request.url.path}"
    )

    errors = processar_erros_validacao_lista(exc.errors(), campo_padrao="geral")

    return resposta_erro(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Os dados fornecidos são inválidos.",
        tipo="validation_error",
        errors=errors,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> Response:
    """Handler genérico para exceções não tratadas -> 500."""
    logger.error(
        f"Exceção não tratada: {type(exc).__name__}: {str(exc)} - "
        f"Path: {request.url.path} - "
        f"IP: {request.client.host if request.client else 'unknown'}",
        exc_info=True,
    )

    # `errors` é estritamente {campo: [msgs]} de validação. O traceback de dev
    # NÃO entra nesse espaço (poluiria consumidores genéricos que achatam
    # errors em toast); vai num campo `debug` separado, fora do contrato de erro.
    debug = None
    if IS_DEVELOPMENT:
        detail = f"{type(exc).__name__}: {str(exc)}"
        debug = {"traceback": traceback.format_exc().splitlines()}
    else:
        detail = "Erro interno do servidor. Nossa equipe foi notificada."

    resposta = resposta_erro(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail,
        tipo="internal_error",
        errors=None,
    )
    if debug is not None:
        corpo = {"detail": detail, "type": "internal_error", "errors": None, "debug": debug}
        return JSONResponse(status_code=resposta.status_code, content=corpo)
    return resposta
