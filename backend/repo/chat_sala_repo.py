"""
Repositório para operações com a tabela chat_sala.
"""
from typing import Optional
from sqlite3 import Row

from model.chat_sala_model import ChatSala
from sql.chat_sala_sql import (
    CRIAR_TABELA,
    INSERIR,
    OBTER_POR_ID,
    ATUALIZAR_ULTIMA_ATIVIDADE,
    EXCLUIR
)
from util.db_util import obter_conexao
from util.datetime_util import agora


def _row_to_sala(row: Row) -> ChatSala:
    """Converte uma row do banco em objeto ChatSala."""
    # Acessar campos com verificação de chave
    criada_em = None
    ultima_atividade = None

    if "criada_em" in row.keys():
        criada_em = row["criada_em"]
    if "ultima_atividade" in row.keys():
        ultima_atividade = row["ultima_atividade"]

    return ChatSala(
        id=row["id"],
        criada_em=criada_em,
        ultima_atividade=ultima_atividade
    )


def criar_tabela():
    """Cria a tabela chat_sala se não existir."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def gerar_sala_id(usuario1_id: int, usuario2_id: int) -> str:
    """
    Gera ID único e determinístico para sala entre dois usuários.

    Sempre retorna o mesmo ID independente da ordem dos usuários.

    Examples:
        >>> gerar_sala_id(3, 7)
        '3_7'
        >>> gerar_sala_id(7, 3)
        '3_7'

    Args:
        usuario1_id: ID do primeiro usuário
        usuario2_id: ID do segundo usuário

    Returns:
        String no formato "menor_id_maior_id"
    """
    ids_ordenados = sorted([usuario1_id, usuario2_id])
    return f"{ids_ordenados[0]}_{ids_ordenados[1]}"


def criar_ou_obter_sala(usuario1_id: int, usuario2_id: int) -> ChatSala:
    """
    Cria uma nova sala ou retorna sala existente entre dois usuários.

    Args:
        usuario1_id: ID do primeiro usuário
        usuario2_id: ID do segundo usuário

    Returns:
        Objeto ChatSala (nova ou existente)
    """
    sala_id = gerar_sala_id(usuario1_id, usuario2_id)

    # Verificar se sala já existe
    sala_existente = obter_por_id(sala_id)
    if sala_existente:
        return sala_existente

    # Criar nova sala
    agora_timestamp = agora()

    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (sala_id, agora_timestamp, agora_timestamp))

    # Retornar sala criada
    return ChatSala(
        id=sala_id,
        criada_em=agora_timestamp,
        ultima_atividade=agora_timestamp
    )


def obter_por_id(sala_id: str) -> Optional[ChatSala]:
    """
    Obtém uma sala pelo ID.

    Args:
        sala_id: ID da sala (formato: "menor_id_maior_id")

    Returns:
        Objeto ChatSala ou None se não encontrada
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (sala_id,))
        row = cursor.fetchone()

        if row:
            return _row_to_sala(row)
        return None


def atualizar_ultima_atividade(sala_id: str) -> bool:
    """
    Atualiza o timestamp de última atividade da sala.

    Args:
        sala_id: ID da sala

    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_ULTIMA_ATIVIDADE, (agora(), sala_id))
        return cursor.rowcount > 0


def excluir(sala_id: str) -> bool:
    """
    Exclui uma sala (cascade deleta participantes e mensagens).

    Args:
        sala_id: ID da sala

    Returns:
        True se excluído com sucesso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (sala_id,))
        return cursor.rowcount > 0
