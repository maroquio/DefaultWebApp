from fastapi import Request, status
from fastapi.responses import RedirectResponse
from functools import wraps
from typing import List, Optional
from util.logger_config import logger
from util.flash_messages import informar_erro
from model.usuario_logado_model import UsuarioLogado


def criar_sessao(request: Request, usuario_logado: UsuarioLogado):
    """
    Cria sessão de usuário.

    Args:
        request: Objeto Request do FastAPI
        usuario_logado: Instância de UsuarioLogado
    """
    request.session["usuario_logado"] = usuario_logado.to_dict()


def destruir_sessao(request: Request):
    """Destroi sessão de usuário"""
    request.session.clear()


def obter_usuario_logado(request: Request) -> Optional[UsuarioLogado]:
    """
    Obtém usuário logado da sessão.

    Returns:
        Instância de UsuarioLogado ou None se não logado
    """
    dados = request.session.get("usuario_logado")
    return UsuarioLogado.from_dict(dados)


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
                if usuario.perfil not in perfis_permitidos:
                    logger.warning(
                        f"Usuário {usuario.email} tentou acessar {request.url.path} "
                        f"sem permissão (perfil: {usuario.perfil})"
                    )
                    informar_erro(request, "Você não tem permissão para acessar esta página.")
                    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

            # Injetar usuario_logado nos kwargs
            kwargs['usuario_logado'] = usuario
            return await func(*args, **kwargs)

        return wrapper
    return decorator
