"""
Repository Helpers.

Funções auxiliares para operações comuns em repositórios,
eliminando código duplicado em rotas.

Este módulo fornece funções para:
- Verificar existência de entidades e redirecionar em caso de erro
- Validar propriedade de entidades
- Lidar com erros comuns de forma padronizada
"""

from typing import Optional, TypeVar, Union, Any, Callable
from fastapi import Request, status
from fastapi.responses import RedirectResponse

from util.flash_messages import informar_erro
from util.logger_config import logger


# TypeVar genérico para trabalhar com qualquer tipo de entidade
T = TypeVar('T')


def obter_ou_404(
    entity: Optional[T],
    request: Request,
    mensagem: str = "Registro não encontrado",
    redirect_url: str = "/",
    log_erro: bool = True
) -> Union[T, RedirectResponse]:
    """
    Verifica se uma entidade existe e retorna RedirectResponse se não existir.

    Esta função elimina o padrão repetitivo de:
    1. Buscar entidade no repository
    2. Verificar se é None
    3. Mostrar mensagem de erro
    4. Redirecionar

    Args:
        entity: Entidade retornada do repository (pode ser None)
        request: Objeto Request do FastAPI
        mensagem: Mensagem de erro a ser exibida (default: "Registro não encontrado")
        redirect_url: URL para redirecionar em caso de erro (default: "/")
        log_erro: Se True, registra erro no log (default: True)

    Returns:
        T: A entidade se existir
        RedirectResponse: Redirecionamento se entidade não existir

    Note:
        Para uso correto, verifique se o retorno é RedirectResponse:

        entity = obter_ou_404(...)
        if isinstance(entity, RedirectResponse):
            return entity
        # Agora entity é garantido como T
    """
    if entity is None:
        # Informar erro ao usuário
        informar_erro(request, mensagem)

        # Log opcional
        if log_erro:
            logger.warning(f"Entidade não encontrada - {mensagem} - URL: {request.url.path}")

        # Redirecionar
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    # Entidade existe, retornar normalmente
    return entity


def obter_lista_ou_vazia(
    lista: Optional[list],
    request: Optional[Request] = None,
    mensagem_aviso: Optional[str] = None,
    log_aviso: bool = False
) -> list:
    """
    Garante que uma lista nunca seja None, retornando lista vazia se necessário.

    Útil para queries que podem retornar None ao invés de lista vazia.

    Args:
        lista: Lista retornada do repository (pode ser None)
        request: Objeto Request (opcional, para flash message)
        mensagem_aviso: Mensagem de aviso a exibir se lista for None/vazia (opcional)
        log_aviso: Se True, registra aviso no log (default: False)

    Returns:
        list: A lista original ou lista vazia
    """
    # Se lista for None ou não for list, retornar lista vazia
    if lista is None or not isinstance(lista, list):
        lista = []

    # Se lista vazia e mensagem fornecida, informar
    if len(lista) == 0 and mensagem_aviso and request:
        from util.flash_messages import informar_info
        informar_info(request, mensagem_aviso)

        if log_aviso:
            logger.info(f"Lista vazia retornada - {mensagem_aviso}")

    return lista


def validar_inteiro_positivo(
    valor: Any,
    request: Request,
    nome_campo: str = "ID",
    redirect_url: str = "/"
) -> Union[int, RedirectResponse]:
    """
    Valida se um valor é um inteiro positivo válido.

    Útil para validar IDs de URL antes de passar para o repository.

    Args:
        valor: Valor a ser validado
        request: Objeto Request do FastAPI
        nome_campo: Nome do campo para mensagem de erro (default: "ID")
        redirect_url: URL para redirecionar em caso de erro

    Returns:
        int: O valor convertido para inteiro se válido
        RedirectResponse: Redirecionamento se inválido
    """
    try:
        valor_int = int(valor)
        if valor_int <= 0:
            raise ValueError("Valor deve ser positivo")
        return valor_int
    except (ValueError, TypeError):
        informar_erro(request, f"{nome_campo} inválido")
        logger.warning(f"Validação falhou - {nome_campo} inválido: {valor}")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


def executar_operacao_repo(
    operacao: Callable,
    request: Request,
    mensagem_erro: str = "Erro ao executar operação",
    redirect_url: str = "/",
    log_exception: bool = True
) -> Union[Any, RedirectResponse]:
    """
    Executa uma operação de repository com tratamento de erros.

    Captura exceções comuns e trata de forma padronizada.

    Args:
        operacao: Função callable a ser executada (ex: lambda: repo.inserir(entity))
        request: Objeto Request do FastAPI
        mensagem_erro: Mensagem de erro a exibir (default: "Erro ao executar operação")
        redirect_url: URL para redirecionar em caso de erro
        log_exception: Se True, loga a exceção completa (default: True)

    Returns:
        any: Resultado da operação se bem-sucedida
        RedirectResponse: Redirecionamento se houver erro
    """
    try:
        return operacao()
    except Exception as e:
        # Informar erro ao usuário
        informar_erro(request, mensagem_erro)

        # Log da exceção
        if log_exception:
            logger.error(f"{mensagem_erro} - Exceção: {str(e)}", exc_info=True)
        else:
            logger.error(f"{mensagem_erro} - {str(e)}")

        # Redirecionar
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
