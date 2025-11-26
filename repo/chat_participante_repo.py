"""
Repositório para operações com a tabela chat_participante.
"""
from typing import Optional, List
from sqlite3 import Row

from model.chat_participante_model import ChatParticipante
from sql.chat_participante_sql import (
    CRIAR_TABELA,
    INSERIR,
    OBTER_POR_SALA_E_USUARIO,
    LISTAR_POR_SALA,
    LISTAR_POR_USUARIO,
    ATUALIZAR_ULTIMA_LEITURA,
    CONTAR_MENSAGENS_NAO_LIDAS,
    EXCLUIR
)
from util.db_util import obter_conexao
from util.datetime_util import agora


def _row_to_participante(row: Row) -> ChatParticipante:
    """Converte uma row do banco em objeto ChatParticipante."""
    # Tentar acessar com e sem sufixo [timestamp]
    ultima_leitura = None
    if "ultima_leitura" in row.keys():
        ultima_leitura = row["ultima_leitura"]

    return ChatParticipante(
        sala_id=row["sala_id"],
        usuario_id=row["usuario_id"],
        ultima_leitura=ultima_leitura
    )


def criar_tabela():
    """Cria a tabela chat_participante se não existir."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def adicionar_participante(sala_id: str, usuario_id: int) -> ChatParticipante:
    """
    Adiciona um participante a uma sala.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário

    Returns:
        Objeto ChatParticipante criado
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (sala_id, usuario_id, None))

    return ChatParticipante(
        sala_id=sala_id,
        usuario_id=usuario_id,
        ultima_leitura=None
    )


def obter_por_sala_e_usuario(sala_id: str, usuario_id: int) -> Optional[ChatParticipante]:
    """
    Obtém um participante específico de uma sala.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário

    Returns:
        Objeto ChatParticipante ou None se não encontrado
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_SALA_E_USUARIO, (sala_id, usuario_id))
        row = cursor.fetchone()

        if row:
            return _row_to_participante(row)
        return None


def listar_por_sala(sala_id: str) -> List[ChatParticipante]:
    """
    Lista todos os participantes de uma sala.

    Args:
        sala_id: ID da sala

    Returns:
        Lista de objetos ChatParticipante
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(LISTAR_POR_SALA, (sala_id,))
        rows = cursor.fetchall()

        return [_row_to_participante(row) for row in rows]


def listar_por_usuario(usuario_id: int) -> List[ChatParticipante]:
    """
    Lista todas as salas em que um usuário participa.

    Args:
        usuario_id: ID do usuário

    Returns:
        Lista de objetos ChatParticipante
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(LISTAR_POR_USUARIO, (usuario_id,))
        rows = cursor.fetchall()

        return [_row_to_participante(row) for row in rows]


def atualizar_ultima_leitura(sala_id: str, usuario_id: int) -> bool:
    """
    Atualiza o timestamp de última leitura do participante.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário

    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_ULTIMA_LEITURA, (agora(), sala_id, usuario_id))
        return cursor.rowcount > 0


def contar_mensagens_nao_lidas(sala_id: str, usuario_id: int) -> int:
    """
    Conta quantas mensagens não lidas existem para um usuário em uma sala.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário

    Returns:
        Número de mensagens não lidas
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        # Passar usuario_id 3 vezes: para sala_id, usuario_id != ?, e duas vezes na subquery
        cursor.execute(CONTAR_MENSAGENS_NAO_LIDAS, (sala_id, usuario_id, usuario_id, usuario_id))
        row = cursor.fetchone()

        return row["total"] if row else 0


def excluir(sala_id: str, usuario_id: int) -> bool:
    """
    Remove um participante de uma sala.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário

    Returns:
        True se excluído com sucesso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (sala_id, usuario_id))
        return cursor.rowcount > 0
