"""
Repositório de Pagamentos.

Gerencia operações CRUD para pagamentos com suporte multi-provedor.
O campo `provider` registra qual gateway foi usado em cada pagamento,
permitindo exibir detalhes corretos mesmo após trocar de provedor.
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
    OBTER_POR_PROVIDER_REFERENCE,
    ATUALIZAR_STATUS,
    ATUALIZAR_CHECKOUT,
    ATUALIZAR_PREFERENCE,
    EXCLUIR,
    ADICIONAR_COLUNA_PROVIDER,
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

    # Lê provider com fallback para 'mercadopago' em bancos antigos
    keys = row.keys()
    provider = row["provider"] if "provider" in keys else "mercadopago"
    if not provider:
        provider = "mercadopago"

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
        provider=provider,
        data_criacao=row["data_criacao"],
        data_atualizacao=row["data_atualizacao"],
        usuario_nome=usuario_nome,
    )


def criar_tabela() -> bool:
    """
    Cria a tabela de pagamentos se não existir.

    Se a tabela já existir mas não tiver a coluna `provider` (banco legado),
    adiciona a coluna automaticamente via migração não-destrutiva.
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)

        # Migração: adicionar coluna provider se não existir (bancos legados)
        try:
            cursor.execute(ADICIONAR_COLUNA_PROVIDER)
            logger.info("Coluna 'provider' adicionada à tabela pagamento (migração).")
        except Exception:
            # Coluna já existe — ignorar erro
            pass

        return True


def inserir(pagamento: Pagamento) -> Optional[int]:
    """
    Insere um novo pagamento no banco de dados.

    Args:
        pagamento: Objeto Pagamento a ser inserido (com campo provider)

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
            pagamento.provider,
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
    Busca um pagamento pelo preference_id (Mercado Pago) ou session_id (Stripe).

    Args:
        preference_id: ID da preferência/sessão gerada no provedor

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

    Usado no webhook do Mercado Pago para identificar o pagamento pelo
    external_reference definido ao criar a preferência.

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


def obter_por_provider_reference(provider: str, reference_id: str) -> Optional[Pagamento]:
    """
    Busca um pagamento por provedor + reference_id (preference_id/session_id).

    Útil para webhooks onde temos o ID do provedor mas não o pagamento_id local.

    Args:
        provider: Chave do provedor ('mercadopago', 'stripe')
        reference_id: ID da sessão/preferência no provedor

    Returns:
        Objeto Pagamento ou None se não encontrado
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_PROVIDER_REFERENCE, (provider, reference_id))
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
        payment_id: ID do pagamento confirmado no provedor (opcional)

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


def atualizar_checkout(
    id: int,
    preference_id: str,
    url_checkout: str,
) -> bool:
    """
    Atualiza os dados de checkout de um pagamento (reference_id e url_checkout).

    Funciona para qualquer provedor — o nome do campo preference_id é mantido
    por compatibilidade, mas pode armazenar session_id do Stripe também.

    Args:
        id: ID do pagamento
        preference_id: ID da preferência/sessão no provedor
        url_checkout: URL de checkout para redirecionar o usuário

    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_CHECKOUT, (
            preference_id,
            url_checkout,
            agora(),
            id,
        ))
        return cursor.rowcount > 0


def atualizar_preference(
    id: int,
    preference_id: str,
    url_checkout: str,
) -> bool:
    """Alias de atualizar_checkout() mantido por compatibilidade."""
    return atualizar_checkout(id, preference_id, url_checkout)


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
