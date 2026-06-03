"""Repositório de Categoria."""

import sqlite3
from typing import Optional

from model.categoria_model import Categoria
from sql.categoria_sql import (
    CRIAR_TABELA,
    INSERIR,
    OBTER_TODOS,
    OBTER_POR_ID,
    ATUALIZAR,
    EXCLUIR,
)
from util.db_util import obter_conexao
from util.logger_config import logger


def _row_to_categoria(row: sqlite3.Row) -> Categoria:
    """Converte sqlite3.Row em dataclass Categoria."""
    return Categoria(
        id=row["id"],
        nome=row["nome"],
        data_criacao=row["data_criacao"],
        data_atualizacao=row["data_atualizacao"],
    )


def criar_tabela() -> bool:
    """Cria a tabela categoria se não existir."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(categoria: Categoria) -> Optional[int]:
    """Insere uma nova categoria e retorna o ID gerado."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (categoria.nome,))
        return cursor.lastrowid


def obter_todos() -> list[Categoria]:
    """Retorna todas as categorias ordenadas por nome."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_categoria(row) for row in cursor.fetchall()]


def obter_por_id(id: int) -> Optional[Categoria]:
    """Retorna uma categoria pelo ID."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        return _row_to_categoria(row) if row else None


def atualizar(categoria: Categoria) -> bool:
    """Atualiza uma categoria existente."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            categoria.nome,
            categoria.id,
        ))
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    """Exclui uma categoria pelo ID."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0
