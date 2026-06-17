"""
Repositório de Notificações In-App.

Gerencia criação, leitura e exclusão de notificações persistentes para usuários.

Uso via utilitário (recomendado):
    from util.notificacao_util import criar_notificacao
    criar_notificacao(usuario_id=1, titulo="Aviso", mensagem="Texto da notificação")

Uso direto (para casos específicos):
    from repo import notificacao_repo
    total = notificacao_repo.contar_nao_lidas(usuario_id)
    notificacoes = notificacao_repo.obter_por_usuario(usuario_id, limite=5)
"""

import sqlite3
from typing import Optional

from model.notificacao_model import Notificacao, TipoNotificacao
from sql.notificacao_sql import (
    CRIAR_TABELA,
    INSERIR,
    OBTER_POR_USUARIO,
    OBTER_NAO_LIDAS_POR_USUARIO,
    CONTAR_NAO_LIDAS,
    MARCAR_COMO_LIDA,
    MARCAR_TODAS_COMO_LIDAS,
    EXCLUIR,
    EXCLUIR_LIDAS,
)
from util.db_util import obter_conexao
from util.logger_config import logger


def _row_to_notificacao(row: sqlite3.Row) -> Notificacao:
    """Converte sqlite3.Row em dataclass Notificacao."""
    try:
        tipo = TipoNotificacao(row["tipo"])
    except ValueError:
        tipo = TipoNotificacao.INFO

    return Notificacao(
        id=row["id"],
        usuario_id=row["usuario_id"],
        titulo=row["titulo"],
        mensagem=row["mensagem"],
        tipo=tipo,
        lida=bool(row["lida"]),
        url_acao=row["url_acao"],
        data_criacao=row["data_criacao"],
    )


def criar_tabela() -> bool:
    """Cria a tabela de notificações se não existir."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(
    usuario_id: int,
    titulo: str,
    mensagem: str,
    tipo: TipoNotificacao = TipoNotificacao.INFO,
    url_acao: Optional[str] = None,
) -> Optional[int]:
    """
    Cria uma nova notificação para o usuário.

    Args:
        usuario_id: ID do usuário destinatário
        titulo: Título curto (ex: 'Pedido aprovado')
        mensagem: Texto completo da notificação
        tipo: Tipo visual (TipoNotificacao.INFO, SUCESSO, AVISO, ERRO)
        url_acao: URL opcional para redirecionar ao clicar na notificação

    Returns:
        ID da notificação criada ou None em caso de erro

    Prefira usar util.notificacao_util.criar_notificacao() para uma API mais amigável.
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERIR, (
                usuario_id,
                titulo,
                mensagem,
                tipo.value,
                url_acao,
            ))
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Erro ao inserir notificação para usuário {usuario_id}: {e}")
        return None


def obter_por_usuario(usuario_id: int, limite: int = 20) -> list[Notificacao]:
    """
    Retorna as notificações mais recentes do usuário (lidas e não lidas).

    Args:
        usuario_id: ID do usuário
        limite: Máximo de notificações a retornar (padrão: 20)

    Returns:
        Lista de Notificacao ordenadas por data (mais recentes primeiro)
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_USUARIO, (usuario_id, limite))
        return [_row_to_notificacao(row) for row in cursor.fetchall()]


def obter_nao_lidas(usuario_id: int, limite: int = 10) -> list[Notificacao]:
    """
    Retorna somente as notificações não lidas do usuário.

    Args:
        usuario_id: ID do usuário
        limite: Máximo de notificações a retornar (padrão: 10)

    Returns:
        Lista de Notificacao não lidas
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_NAO_LIDAS_POR_USUARIO, (usuario_id, limite))
        return [_row_to_notificacao(row) for row in cursor.fetchall()]


def contar_nao_lidas(usuario_id: int) -> int:
    """
    Conta quantas notificações não lidas o usuário tem.

    Usado para o badge no navbar.

    Args:
        usuario_id: ID do usuário

    Returns:
        Número de notificações não lidas
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_NAO_LIDAS, (usuario_id,))
        row = cursor.fetchone()
        return row["total"] if row else 0


def marcar_como_lida(notificacao_id: int, usuario_id: int) -> bool:
    """
    Marca uma notificação específica como lida.

    Verifica se a notificação pertence ao usuário antes de marcar.

    Args:
        notificacao_id: ID da notificação
        usuario_id: ID do usuário (verificação de propriedade)

    Returns:
        True se marcou com sucesso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(MARCAR_COMO_LIDA, (notificacao_id, usuario_id))
        return cursor.rowcount > 0


def marcar_todas_como_lidas(usuario_id: int) -> int:
    """
    Marca todas as notificações do usuário como lidas.

    Args:
        usuario_id: ID do usuário

    Returns:
        Número de notificações marcadas como lidas
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(MARCAR_TODAS_COMO_LIDAS, (usuario_id,))
        return cursor.rowcount


def excluir(notificacao_id: int, usuario_id: int) -> bool:
    """
    Exclui uma notificação específica do usuário.

    Verifica se a notificação pertence ao usuário antes de excluir.

    Args:
        notificacao_id: ID da notificação
        usuario_id: ID do usuário (verificação de propriedade)

    Returns:
        True se excluiu com sucesso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (notificacao_id, usuario_id))
        return cursor.rowcount > 0


def excluir_lidas(usuario_id: int) -> int:
    """
    Exclui todas as notificações lidas do usuário.

    Útil para limpar o histórico de notificações antigas já visualizadas.

    Args:
        usuario_id: ID do usuário

    Returns:
        Número de notificações excluídas
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR_LIDAS, (usuario_id,))
        return cursor.rowcount
