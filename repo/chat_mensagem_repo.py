"""
Repositório para operações com a tabela chat_mensagem.
"""
from typing import Optional, List
from sqlite3 import Row

from model.chat_mensagem_model import ChatMensagem
from sql.chat_mensagem_sql import (
    CRIAR_TABELA,
    INSERIR,
    OBTER_POR_ID,
    LISTAR_POR_SALA,
    CONTAR_POR_SALA,
    MARCAR_COMO_LIDAS,
    OBTER_ULTIMA_MENSAGEM_SALA,
    EXCLUIR
)
from util.db_util import obter_conexao
from util.datetime_util import agora


def _row_to_mensagem(row: Row) -> ChatMensagem:
    """Converte uma row do banco em objeto ChatMensagem."""
    # Acessar campos com verificação de chave
    data_envio = None
    lida_em = None

    if "data_envio" in row.keys():
        data_envio = row["data_envio"]
    if "lida_em" in row.keys():
        lida_em = row["lida_em"]

    return ChatMensagem(
        id=row["id"],
        sala_id=row["sala_id"],
        usuario_id=row["usuario_id"],
        mensagem=row["mensagem"],
        data_envio=data_envio,
        lida_em=lida_em
    )


def criar_tabela():
    """Cria a tabela chat_mensagem se não existir."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(sala_id: str, usuario_id: int, mensagem: str) -> ChatMensagem:
    """
    Insere uma nova mensagem em uma sala.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário que enviou
        mensagem: Conteúdo da mensagem

    Returns:
        Objeto ChatMensagem criado
    """
    data_envio = agora()

    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (sala_id, usuario_id, mensagem, data_envio, None))
        mensagem_id = cursor.lastrowid

    return ChatMensagem(
        id=mensagem_id,
        sala_id=sala_id,
        usuario_id=usuario_id,
        mensagem=mensagem,
        data_envio=data_envio,
        lida_em=None
    )


def obter_por_id(mensagem_id: int) -> Optional[ChatMensagem]:
    """
    Obtém uma mensagem pelo ID.

    Args:
        mensagem_id: ID da mensagem

    Returns:
        Objeto ChatMensagem ou None se não encontrada
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (mensagem_id,))
        row = cursor.fetchone()

        if row:
            return _row_to_mensagem(row)
        return None


def listar_por_sala(sala_id: str, limit: int = 50, offset: int = 0) -> List[ChatMensagem]:
    """
    Lista mensagens de uma sala com paginação.

    Args:
        sala_id: ID da sala
        limit: Número máximo de mensagens a retornar
        offset: Número de mensagens a pular (para paginação)

    Returns:
        Lista de objetos ChatMensagem (ordenadas por ID crescente - mais antigas primeiro)
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(LISTAR_POR_SALA, (sala_id, limit, offset))
        rows = cursor.fetchall()

        return [_row_to_mensagem(row) for row in rows]


def contar_por_sala(sala_id: str) -> int:
    """
    Conta o total de mensagens em uma sala.

    Args:
        sala_id: ID da sala

    Returns:
        Número total de mensagens
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_POR_SALA, (sala_id,))
        row = cursor.fetchone()

        return row["total"] if row else 0


def marcar_como_lidas(sala_id: str, usuario_id: int) -> bool:
    """
    Marca como lidas todas as mensagens não lidas de outros usuários em uma sala.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário que está marcando como lidas

    Returns:
        True se marcadas com sucesso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(MARCAR_COMO_LIDAS, (agora(), sala_id, usuario_id))
        return cursor.rowcount >= 0  # Retorna True mesmo se nenhuma mensagem foi marcada


def obter_ultima_mensagem_sala(sala_id: str) -> Optional[ChatMensagem]:
    """
    Obtém a última mensagem enviada em uma sala.

    Args:
        sala_id: ID da sala

    Returns:
        Objeto ChatMensagem ou None se não houver mensagens
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_ULTIMA_MENSAGEM_SALA, (sala_id,))
        row = cursor.fetchone()

        if row:
            return _row_to_mensagem(row)
        return None


def excluir(mensagem_id: int) -> bool:
    """
    Exclui uma mensagem.

    Args:
        mensagem_id: ID da mensagem

    Returns:
        True se excluída com sucesso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (mensagem_id,))
        return cursor.rowcount > 0
