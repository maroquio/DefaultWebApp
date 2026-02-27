"""
Repositório de Pagamentos.

Gerencia operações CRUD para pagamentos integrados ao Mercado Pago,
incluindo busca por preference_id (retorno do MP) e external_reference
(usado no webhook IPN para identificar o pagamento internamente).
"""

import sqlite3
from typing import Optional

from model.pagamento_model import Pagamento, StatusPagamento
from sql.pagamento_sql import (
    CRIAR_TABELA,
    INSERIR,
    OBTER_TODOS,
    OBTER_POR_USUARIO,
    OBTER_POR_ID,
    OBTER_POR_PREFERENCE_ID,
    OBTER_POR_EXTERNAL_REFERENCE,
    ATUALIZAR_STATUS,
    ATUALIZAR_PREFERENCE,
    EXCLUIR,
)
from util.db_util import obter_conexao
from util.datetime_util import agora
from util.logger_config import logger


def _row_to_pagamento(row: sqlite3.Row) -> Pagamento:
    """Converte linha do banco de dados em objeto Pagamento."""
    usuario_nome = row["usuario_nome"] if "usuario_nome" in row.keys() else None

    try:
        status = StatusPagamento(row["status"])
    except ValueError:
        logger.error(f"Status de pagamento inválido: '{row['status']}'. Usando Pendente.")
        status = StatusPagamento.PENDENTE

    return Pagamento(
        id=row["id"],
        usuario_id=row["usuario_id"],
        descricao=row["descricao"],
        valor=row["valor"],
        status=status,
        preference_id=row["preference_id"],
        payment_id=row["payment_id"],
        external_reference=row["external_reference"],
        url_checkout=row["url_checkout"],
        data_criacao=row["data_criacao"],
        data_atualizacao=row["data_atualizacao"],
        usuario_nome=usuario_nome,
    )


def criar_tabela() -> bool:
    """Cria a tabela de pagamentos se não existir."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(pagamento: Pagamento) -> Optional[int]:
    """
    Insere um novo pagamento no banco de dados.

    Args:
        pagamento: Objeto Pagamento a ser inserido

    Returns:
        ID do pagamento inserido ou None em caso de erro
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            pagamento.usuario_id,
            pagamento.descricao,
            pagamento.valor,
            pagamento.status.value,
            pagamento.preference_id,
            pagamento.payment_id,
            pagamento.external_reference,
            pagamento.url_checkout,
            agora(),
            agora(),
        ))
        return cursor.lastrowid


def obter_todos() -> list[Pagamento]:
    """Retorna todos os pagamentos com dados do usuário (para admin)."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_pagamento(row) for row in rows]


def obter_por_usuario(usuario_id: int) -> list[Pagamento]:
    """
    Retorna todos os pagamentos de um usuário específico.

    Args:
        usuario_id: ID do usuário

    Returns:
        Lista de pagamentos do usuário, ordenada por data decrescente
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_USUARIO, (usuario_id,))
        rows = cursor.fetchall()
        return [_row_to_pagamento(row) for row in rows]


def obter_por_id(id: int) -> Optional[Pagamento]:
    """
    Retorna um pagamento pelo seu ID.

    Args:
        id: ID do pagamento

    Returns:
        Objeto Pagamento ou None se não encontrado
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        return _row_to_pagamento(row) if row else None


def obter_por_preference_id(preference_id: str) -> Optional[Pagamento]:
    """
    Busca um pagamento pelo preference_id do Mercado Pago.

    Usado nas páginas de retorno (sucesso/pendente/falha) quando o MP
    redireciona o usuário de volta com o preference_id na URL.

    Args:
        preference_id: ID da preferência gerada no Mercado Pago

    Returns:
        Objeto Pagamento ou None se não encontrado
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_PREFERENCE_ID, (preference_id,))
        row = cursor.fetchone()
        return _row_to_pagamento(row) if row else None


def obter_por_external_reference(external_reference: str) -> Optional[Pagamento]:
    """
    Busca um pagamento pela referência externa.

    Usado no processamento do webhook IPN, onde o MP envia o external_reference
    que foi definido ao criar a preferência. Esse campo é controlado pela
    aplicação e é a forma mais confiável de identificar o pagamento.

    Args:
        external_reference: Referência externa definida ao criar a preferência

    Returns:
        Objeto Pagamento ou None se não encontrado
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_EXTERNAL_REFERENCE, (external_reference,))
        row = cursor.fetchone()
        return _row_to_pagamento(row) if row else None


def atualizar_status(
    id: int,
    status: StatusPagamento,
    payment_id: Optional[str] = None
) -> bool:
    """
    Atualiza o status de um pagamento e opcionalmente o payment_id.

    Args:
        id: ID do pagamento
        status: Novo status do pagamento
        payment_id: ID do pagamento confirmado no Mercado Pago (opcional)

    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_STATUS, (
            status.value,
            payment_id,
            agora(),
            id,
        ))
        return cursor.rowcount > 0


def atualizar_preference(
    id: int,
    preference_id: str,
    url_checkout: str,
) -> bool:
    """
    Atualiza os dados da preferência MP de um pagamento.

    Args:
        id: ID do pagamento
        preference_id: ID da preferência no Mercado Pago
        url_checkout: URL de checkout (init_point) do MP

    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_PREFERENCE, (
            preference_id,
            url_checkout,
            agora(),
            id,
        ))
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    """
    Exclui um pagamento pelo ID.

    Args:
        id: ID do pagamento

    Returns:
        True se excluído com sucesso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0
