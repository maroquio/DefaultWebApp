"""
Módulo para gerenciamento de mensagens flash.

Mensagens flash são mensagens temporárias exibidas ao usuário uma única vez,
geralmente após uma ação (sucesso, erro, aviso, etc.).
"""

from fastapi import Request
from typing import Literal, TypedDict

TipoMensagem = Literal["sucesso", "erro", "aviso", "info"]


class MensagemFlash(TypedDict):
    """Estrutura de uma mensagem flash."""
    texto: str
    tipo: TipoMensagem


def adicionar_mensagem(
    request: Request,
    mensagem: str,
    tipo: TipoMensagem = "info"
) -> None:
    """
    Adiciona mensagem flash à sessão do usuário.

    Args:
        request: Request object do FastAPI
        mensagem: Texto da mensagem a ser exibida
        tipo: Tipo da mensagem (sucesso, erro, aviso, info)
    """
    if "mensagens" not in request.session:
        request.session["mensagens"] = []

    request.session["mensagens"].append({
        "texto": mensagem,
        "tipo": tipo
    })


def informar_sucesso(request: Request, mensagem: str) -> None:
    """
    Adiciona mensagem de sucesso (verde).

    Args:
        request: Request object do FastAPI
        mensagem: Texto da mensagem de sucesso
    """
    adicionar_mensagem(request, mensagem, "sucesso")


def informar_erro(request: Request, mensagem: str) -> None:
    """
    Adiciona mensagem de erro (vermelho).

    Args:
        request: Request object do FastAPI
        mensagem: Texto da mensagem de erro
    """
    adicionar_mensagem(request, mensagem, "erro")


def informar_aviso(request: Request, mensagem: str) -> None:
    """
    Adiciona mensagem de aviso (amarelo).

    Args:
        request: Request object do FastAPI
        mensagem: Texto da mensagem de aviso
    """
    adicionar_mensagem(request, mensagem, "aviso")


def informar_info(request: Request, mensagem: str) -> None:
    """
    Adiciona mensagem informativa (azul).

    Args:
        request: Request object do FastAPI
        mensagem: Texto da mensagem informativa
    """
    adicionar_mensagem(request, mensagem, "info")


def obter_mensagens(request: Request) -> list[MensagemFlash]:
    """
    Obtém e limpa todas as mensagens flash da sessão.

    Esta função remove as mensagens da sessão após obtê-las,
    garantindo que sejam exibidas apenas uma vez.

    Args:
        request: Request object do FastAPI

    Returns:
        Lista de dicionários com mensagens flash, cada um contendo
        'texto' (str) e 'tipo' (TipoMensagem)
    """
    mensagens: list[MensagemFlash] = request.session.pop("mensagens", [])
    return mensagens
