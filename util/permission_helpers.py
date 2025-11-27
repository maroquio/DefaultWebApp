"""
Permission Helpers

Funções auxiliares para verificação de permissões e propriedade de entidades,
eliminando código duplicado em rotas.

Este módulo fornece funções para:
- Verificar se um usuário é dono de uma entidade
- Validar permissões de perfis
- Lidar com acessos negados de forma padronizada
"""

from typing import List, Any, TYPE_CHECKING
from fastapi import Request

from util.flash_messages import informar_erro
from util.logger_config import logger
from util.perfis import Perfil

if TYPE_CHECKING:
    from model.usuario_logado_model import UsuarioLogado


def verificar_propriedade(
    entity: Any,
    usuario_id: int,
    request: Request,
    mensagem_erro: str = "Você não tem permissão para acessar este recurso",
    redirect_url: str = "/",
    campo_usuario: str = "usuario_id",
    log_tentativa: bool = True,
) -> bool:
    """
    Verifica se um usuário é proprietário de uma entidade.

    Compara o ID do usuário com o campo de propriedade da entidade.
    Se não for proprietário, exibe erro e redireciona automaticamente.

    Args:
        entity: Entidade a verificar (deve ter atributo com ID do usuário)
        usuario_id: ID do usuário logado
        request: Objeto Request do FastAPI
        mensagem_erro: Mensagem de erro a exibir (default: mensagem genérica)
        redirect_url: URL para redirecionar se acesso negado (default: "/")
        campo_usuario: Nome do atributo que contém o user_id (default: "usuario_id")
        log_tentativa: Se True, registra tentativa de acesso no log (default: True)

    Returns:
        bool: True se usuário é proprietário, False caso contrário

    Note:
        A função retorna bool, mas TEM EFEITO COLATERAL:
        - Exibe flash message de erro
        - Registra no log
        - A rota DEVE checar o retorno e fazer return se False

        Pattern correto:
        ```python
        if not verificar_propriedade(...):
            return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
        ```
    """
    # Verificar se entidade existe
    if entity is None:
        informar_erro(request, "Recurso não encontrado")
        if log_tentativa:
            logger.warning(
                f"Tentativa de acesso a entidade inexistente - "
                f"Usuário ID: {usuario_id} - URL: {request.url.path}"
            )
        return False

    # Obter ID do proprietário da entidade
    try:
        proprietario_id = getattr(entity, campo_usuario)
    except AttributeError:
        logger.error(
            f"Entidade não possui campo '{campo_usuario}' - "
            f"Tipo: {type(entity).__name__}"
        )
        informar_erro(request, "Erro ao verificar permissões")
        return False

    # Verificar se usuário é o proprietário
    if proprietario_id != usuario_id:
        informar_erro(request, mensagem_erro)

        if log_tentativa:
            logger.warning(
                f"Tentativa de acesso negada - "
                f"Usuário ID: {usuario_id} tentou acessar recurso de {proprietario_id} - "
                f"Entidade: {type(entity).__name__} - "
                f"URL: {request.url.path}"
            )

        return False

    # Usuário é proprietário
    return True


def verificar_propriedade_ou_admin(
    entity: Any,
    usuario_logado: 'UsuarioLogado',
    request: Request,
    mensagem_erro: str = "Você não tem permissão para acessar este recurso",
    redirect_url: str = "/",
    campo_usuario: str = "usuario_id",
    log_tentativa: bool = True,
) -> bool:
    """
    Verifica se usuário é proprietário OU administrador.

    Administradores têm acesso a todos os recursos, independente de propriedade.

    Args:
        entity: Entidade a verificar
        usuario_logado: Instância de UsuarioLogado
        request: Objeto Request do FastAPI
        mensagem_erro: Mensagem de erro a exibir
        redirect_url: URL para redirecionar se acesso negado
        campo_usuario: Nome do atributo que contém o user_id
        log_tentativa: Se True, registra tentativa de acesso no log

    Returns:
        bool: True se usuário é proprietário OU admin, False caso contrário
    """
    # Se é admin, permitir acesso
    if usuario_logado.is_admin():
        return True

    # Se não é admin, verificar propriedade normal
    return verificar_propriedade(
        entity,
        usuario_logado.id,
        request,
        mensagem_erro,
        redirect_url,
        campo_usuario,
        log_tentativa,
    )


def verificar_perfil(
    usuario_perfil: str,
    perfis_permitidos: List[str],
    request: Request,
    mensagem_erro: str = "Você não tem permissão para acessar esta funcionalidade",
    redirect_url: str = "/",
    log_tentativa: bool = True,
) -> bool:
    """
    Verifica se o perfil do usuário está na lista de perfis permitidos.

    Args:
        usuario_perfil: Perfil do usuário logado
        perfis_permitidos: Lista de perfis que têm permissão (use Perfil enum)
        request: Objeto Request do FastAPI
        mensagem_erro: Mensagem de erro a exibir
        redirect_url: URL para redirecionar se acesso negado
        log_tentativa: Se True, registra tentativa de acesso no log

    Returns:
        bool: True se perfil permitido, False caso contrário
    """
    if usuario_perfil not in perfis_permitidos:
        informar_erro(request, mensagem_erro)

        if log_tentativa:
            logger.warning(
                f"Tentativa de acesso com perfil não autorizado - "
                f"Perfil: {usuario_perfil} - "
                f"Perfis permitidos: {perfis_permitidos} - "
                f"URL: {request.url.path}"
            )

        return False

    return True


def verificar_multiplas_condicoes(
    condicoes: List[tuple],
    request: Request,
    mensagem_erro_padrao: str = "Você não tem permissão para acessar este recurso",
    redirect_url: str = "/",
    operador: str = "AND",
) -> bool:
    """
    Verifica múltiplas condições de permissão com operador lógico.

    Args:
        condicoes: Lista de tuplas (condicao: bool, mensagem_erro: str)
        request: Objeto Request do FastAPI
        mensagem_erro_padrao: Mensagem de erro se nenhuma mensagem específica fornecida
        redirect_url: URL para redirecionar se acesso negado
        operador: "AND" (todas devem passar) ou "OR" (pelo menos uma deve passar)

    Returns:
        bool: True se condições satisfeitas, False caso contrário
    """
    if operador == "AND":
        # Todas as condições devem ser True
        for condicao, mensagem in condicoes:
            if not condicao:
                informar_erro(request, mensagem or mensagem_erro_padrao)
                return False
        return True

    elif operador == "OR":
        # Pelo menos uma condição deve ser True
        for condicao, mensagem in condicoes:
            if condicao:
                return True

        # Nenhuma condição passou
        # Usar mensagem da primeira condição ou padrão
        mensagem = condicoes[0][1] if condicoes else mensagem_erro_padrao
        informar_erro(request, mensagem_erro_padrao)
        return False

    else:
        raise ValueError(f"Operador inválido: {operador}. Use 'AND' ou 'OR'.")
