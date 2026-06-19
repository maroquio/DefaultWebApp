import inspect
from fastapi import Request, status, HTTPException
from functools import wraps
from typing import List, Optional
from util.logger_config import logger
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
    Decorator para exigir autenticação e autorização em rotas de API JSON.

    - Não autenticado  -> HTTPException 401 (o front trata redirecionando p/ login)
    - Perfil insuficiente -> HTTPException 403

    Injeta ``usuario_logado: UsuarioLogado`` nos kwargs da rota.

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
                logger.warning(
                    f"Acesso não autenticado a {request.url.path}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Autenticação necessária.",
                )

            # Verificar perfil se especificado
            if perfis_permitidos and usuario.perfil not in perfis_permitidos:
                logger.warning(
                    f"Usuário {usuario.email} tentou acessar {request.url.path} "
                    f"sem permissão (perfil: {usuario.perfil})"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Você não tem permissão para acessar este recurso.",
                )

            # Injetar usuario_logado nos kwargs
            kwargs['usuario_logado'] = usuario
            return await func(*args, **kwargs)

        # Esconder 'usuario_logado' da assinatura que o FastAPI inspeciona.
        # Caso contrário, como UsuarioLogado é uma dataclass, o FastAPI o
        # interpretaria como um SEGUNDO corpo de requisição (exigindo
        # {"dto": {...}, "usuario_logado": {...}}). O parâmetro é injetado
        # pelo wrapper, não pelo FastAPI.
        try:
            sig = inspect.signature(func)
            wrapper.__signature__ = sig.replace(
                parameters=[
                    p for nome, p in sig.parameters.items()
                    if nome != "usuario_logado"
                ]
            )
        except (ValueError, TypeError):
            pass

        return wrapper
    return decorator
