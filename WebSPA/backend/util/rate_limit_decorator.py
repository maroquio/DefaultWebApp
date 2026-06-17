"""
Rate Limiting Decorator

Decorator para aplicar rate limiting em rotas FastAPI de forma centralizada,
eliminando código duplicado em múltiplas rotas.

Este módulo fornece um decorator que:
- Verifica automaticamente o rate limit baseado no IP do cliente
- Exibe mensagem de erro padronizada quando o limite é excedido
- Registra no log tentativas bloqueadas
- Redireciona para URL especificada quando bloqueado
"""

from functools import wraps
from typing import Optional, Callable
from fastapi import Request, status
from fastapi.responses import RedirectResponse

from util.rate_limiter import RateLimiter
from util.flash_messages import informar_erro
from util.logger_config import logger


def obter_identificador_cliente(request: Request) -> str:
    """
    Obtém identificador único do cliente para rate limiting.

    Tenta obter o IP real do cliente, considerando proxies reversos.
    Ordem de prioridade:
    1. X-Forwarded-For (primeiro IP da lista)
    2. X-Real-IP
    3. request.client.host (IP direto)

    Args:
        request: Objeto Request do FastAPI

    Returns:
        String com o IP do cliente
    """
    # Verificar header X-Forwarded-For (comum em load balancers/proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Pegar o primeiro IP da lista (IP original do cliente)
        return forwarded_for.split(",")[0].strip()

    # Verificar header X-Real-IP (usado por alguns proxies)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fallback para IP direto
    if request.client and request.client.host:
        return request.client.host

    # Fallback final (não deveria acontecer)
    return "unknown"


def aplicar_rate_limit(
    limiter: RateLimiter,
    mensagem_erro: Optional[str] = None,
    redirect_url: Optional[str] = None,
    log_detalhes: Optional[Callable[[str], str]] = None
) -> Callable:
    """
    Decorator para aplicar rate limiting em rotas FastAPI.

    Este decorator verifica se o cliente excedeu o limite de requisições
    e bloqueia automaticamente a requisição se necessário.

    Args:
        limiter: Instância de RateLimiter configurada
        mensagem_erro: Mensagem customizada de erro (opcional)
                      Default: "Muitas requisições. Aguarde um momento."
        redirect_url: URL para redirecionar quando bloqueado (opcional)
                     Se None, a função original será executada (útil para APIs)
        log_detalhes: Função opcional que recebe o IP e retorna string com
                     detalhes adicionais para o log (ex: user_id, rota, etc)

    Returns:
        Decorator function

    Raises:
        TypeError: Se limiter não for uma instância de RateLimiter
    """
    # Validação do parâmetro
    if not isinstance(limiter, RateLimiter):
        raise TypeError("O parâmetro 'limiter' deve ser uma instância de RateLimiter")

    # Mensagem padrão se não fornecida
    mensagem_padrao = "Muitas requisições. Aguarde um momento antes de tentar novamente."

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Obter identificador do cliente (IP)
            ip = obter_identificador_cliente(request)

            # Verificar rate limit
            if not limiter.verificar(ip):
                # Rate limit excedido - bloquear requisição
                mensagem = mensagem_erro or mensagem_padrao

                # Informar erro ao usuário via flash message
                informar_erro(request, mensagem)

                # Construir log detalhado
                log_msg = f"Rate limit excedido - {limiter.nome} - IP: {ip}"
                if log_detalhes:
                    try:
                        detalhes_extra = log_detalhes(ip)
                        log_msg = f"{log_msg} - {detalhes_extra}"
                    except Exception as e:
                        logger.error(f"Erro ao obter detalhes para log: {e}")

                # Registrar no log
                logger.warning(log_msg)

                # Redirecionar se URL fornecida
                if redirect_url:
                    return RedirectResponse(
                        redirect_url,
                        status_code=status.HTTP_303_SEE_OTHER
                    )

                # Se não houver redirect_url, podemos retornar erro JSON
                # (útil para APIs REST)
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": mensagem,
                        "retry_after": limiter.janela_minutos * 60
                    }
                )

            # Rate limit OK - executar função original
            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


def aplicar_rate_limit_async(
    limiter: RateLimiter,
    mensagem_erro: Optional[str] = None,
    log_detalhes: Optional[Callable[[str], str]] = None
):
    """
    Versão assíncrona do decorator de rate limiting para APIs.

    Retorna JSON ao invés de redirecionar. Útil para endpoints de API REST.

    Args:
        limiter: Instância de RateLimiter configurada
        mensagem_erro: Mensagem customizada de erro (opcional)
        log_detalhes: Função opcional para detalhes adicionais no log

    Returns:
        Decorator function que retorna JSONResponse
    """
    return aplicar_rate_limit(
        limiter=limiter,
        mensagem_erro=mensagem_erro,
        redirect_url=None,  # Força retorno JSON
        log_detalhes=log_detalhes
    )
