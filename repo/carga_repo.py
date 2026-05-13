import sqlite3
from datetime import datetime
from typing import Optional
from model.carga_model import Carga
from sql.carga_sql import (
    CRIAR_TABELA,
    INSERIR,
    ALTERAR,
    EXCLUIR,
    OBTER_POR_ID,
    OBTER_TODOS,
    OBTER_QUANTIDADE
)
from util.db_util import obter_conexao

def _row_to_carga(row: sqlite3.Row) -> Carga:
    
    return Carga(
        id=row["id"],
        nome=row["nome"],
        email=row["email"],
        senha=row["senha"],
        perfil=row["perfil"]
    )


def criar_tabela() -> bool:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(carga: Carga) -> Optional[int]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            carga.nome,
            carga.email,
            carga.senha,
            carga.perfil
        ))
        carga_id = cursor.lastrowid
        return carga_id if carga_id else None


def alterar(carga: Carga) -> bool:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ALTERAR, (
            carga.nome,
            carga.email,
            carga.perfil,
            carga.id
        ))
        return cursor.rowcount > 0

def excluir(id: int) -> bool:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0


def obter_por_id(id: int) -> Optional[Carga]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_carga(row)
        return None


def obter_todos() -> list[Carga]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_carga(row) for row in rows]


def obter_quantidade() -> int:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_QUANTIDADE)
        row = cursor.fetchone()
        return row["quantidade"] if row else 0