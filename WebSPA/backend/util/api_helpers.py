"""Helpers transversais para rotas da API JSON."""
from fastapi import HTTPException, Request, status

from util.logger_config import logger
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente


def checar_rate_limit(limiter: DynamicRateLimiter, request: Request) -> None:
    """
    Verifica o rate limit por IP e lança HTTPException 429 (com Retry-After)
    quando o limite é excedido.
    """
    ip = obter_identificador_cliente(request)
    if not limiter.verificar(ip):
        logger.warning(f"Rate limit '{limiter.nome}' excedido para IP: {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas. Aguarde {limiter.janela_minutos} minuto(s).",
            headers={"Retry-After": str(limiter.janela_minutos * 60)},
        )
