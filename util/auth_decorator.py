from fastapi import Request, status
from fastapi.responses import RedirectResponse
from functools import wraps
from typing import List, Optional
from util.logger_config import logger
from util.flash_messages import informar_erro


def criar_sessao(request: Request, usuario: dict):
    """Cria sessão de usuário"""
    request.session["usuario_logado"] = usuario


def destruir_sessao(request: Request):
    """Destroi sessão de usuário"""
    request.session.clear()


def obter_usuario_logado(request: Request) -> Optional[dict]:
    """Obtém usuário logado da sessão"""
    return request.session.get("usuario_logado")


def esta_logado(request: Request) -> bool:
    """Verifica se usuário está logado"""
    return "usuario_logado" in request.session


def requer_autenticacao(perfis_permitidos: Optional[List[str]] = None):
    """
    Decorator para exigir autenticação e autorização.

    Args:
        perfis_permitidos: Lista de perfis que podem acessar (None = qualquer logado)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request') or args[0]

            # Verificar se está logado
            usuario = obter_usuario_logado(request)
            if not usuario:
                logger.warning(f"Tentativa de acesso não autenticado a {request.url.path}")
                informar_erro(request, "Você precisa estar autenticado para acessar esta página.")
                return RedirectResponse(
                    f"/login?redirect={request.url.path}",
                    status_code=status.HTTP_303_SEE_OTHER
                )

            # Verificar perfil se especificado
            if perfis_permitidos:
                perfil_usuario = usuario.get("perfil")
                if perfil_usuario not in perfis_permitidos:
                    logger.warning(
                        f"Usuário {usuario.get('email')} tentou acessar {request.url.path} "
                        f"sem permissão (perfil: {perfil_usuario})"
                    )
                    informar_erro(request, "Você não tem permissão para acessar esta página.")
                    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

            # Injetar usuario_logado nos kwargs
            kwargs['usuario_logado'] = usuario
            return await func(*args, **kwargs)

        return wrapper
    return decorator
