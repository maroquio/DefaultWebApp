import sqlite3
from typing import Optional
from model.chamado_interacao_model import ChamadoInteracao, TipoInteracao
from sql.chamado_interacao_sql import (
    CRIAR_TABELA,
    INSERIR,
    OBTER_POR_CHAMADO,
    OBTER_POR_ID,
    CONTAR_POR_CHAMADO,
    EXCLUIR_POR_CHAMADO,
    MARCAR_COMO_LIDAS,
    CONTAR_NAO_LIDAS_POR_CHAMADO,
    TEM_RESPOSTA_ADMIN,
)
from util.db_util import obter_conexao


def _row_to_interacao(row: sqlite3.Row) -> ChamadoInteracao:
    """
    Converte uma linha do banco de dados em objeto ChamadoInteracao.

    Args:
        row: Linha do cursor SQLite (sqlite3.Row)

    Returns:
        Objeto ChamadoInteracao populado
    """
    # Verificar se os campos do JOIN existem
    usuario_nome = row["usuario_nome"] if "usuario_nome" in row.keys() else None
    usuario_email = row["usuario_email"] if "usuario_email" in row.keys() else None
    data_leitura = row["data_leitura"] if "data_leitura" in row.keys() and row["data_leitura"] else None

    return ChamadoInteracao(
        id=row["id"],
        chamado_id=row["chamado_id"],
        usuario_id=row["usuario_id"],
        mensagem=row["mensagem"],
        tipo=TipoInteracao(row["tipo"]),
        data_interacao=row["data_interacao"],
        status_resultante=row["status_resultante"] if row["status_resultante"] else None,
        data_leitura=data_leitura,
        usuario_nome=usuario_nome,
        usuario_email=usuario_email
    )


def criar_tabela() -> bool:
    """
    Cria a tabela de interações de chamados no banco de dados se não existir.

    Returns:
        True se operação foi bem sucedida
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(interacao: ChamadoInteracao) -> Optional[int]:
    """
    Insere uma nova interação no banco de dados.

    Args:
        interacao: Objeto ChamadoInteracao a ser inserido

    Returns:
        ID da interação inserida ou None em caso de erro
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            interacao.chamado_id,
            interacao.usuario_id,
            interacao.mensagem,
            interacao.tipo.value,
            interacao.status_resultante
        ))
        return cursor.lastrowid


def obter_por_chamado(chamado_id: int) -> list[ChamadoInteracao]:
    """
    Obtém todas as interações de um chamado específico.

    Args:
        chamado_id: ID do chamado

    Returns:
        Lista de objetos ChamadoInteracao ordenados por data
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_CHAMADO, (chamado_id,))
        rows = cursor.fetchall()
        return [_row_to_interacao(row) for row in rows]


def obter_por_id(id: int) -> Optional[ChamadoInteracao]:
    """
    Obtém uma interação específica por ID.

    Args:
        id: ID da interação

    Returns:
        Objeto ChamadoInteracao ou None se não encontrado
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_interacao(row)
        return None


def contar_por_chamado(chamado_id: int) -> int:
    """
    Conta quantas interações um chamado possui.

    Args:
        chamado_id: ID do chamado

    Returns:
        Número de interações
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_POR_CHAMADO, (chamado_id,))
        row = cursor.fetchone()
        return row["total"] if row else 0


def excluir_por_chamado(chamado_id: int) -> bool:
    """
    Exclui todas as interações de um chamado.

    Esta função é chamada automaticamente quando um chamado é excluído
    devido ao ON DELETE CASCADE no banco.

    Args:
        chamado_id: ID do chamado

    Returns:
        True se exclusão foi bem sucedida, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR_POR_CHAMADO, (chamado_id,))
        return cursor.rowcount >= 0  # Pode ser 0 se não havia interações


def marcar_como_lidas(chamado_id: int, usuario_logado_id: int) -> bool:
    """
    Marca como lidas todas as mensagens de um chamado que NÃO foram
    criadas pelo usuário logado.

    Estratégia: Ao visualizar um chamado, marca automaticamente como lidas
    todas as mensagens enviadas por outros usuários (não marca próprias mensagens).

    Args:
        chamado_id: ID do chamado
        usuario_logado_id: ID do usuário que está visualizando

    Returns:
        True se marcação foi bem sucedida
    """
    from util.datetime_util import agora

    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(MARCAR_COMO_LIDAS, (agora(), chamado_id, usuario_logado_id))
        return True


def obter_contador_nao_lidas(usuario_id: int) -> dict[int, int]:
    """
    Obtém um dicionário com a contagem de mensagens não lidas por chamado.

    Conta apenas mensagens de OUTROS usuários (não conta próprias mensagens).

    Args:
        usuario_id: ID do usuário para excluir suas próprias mensagens da contagem

    Returns:
        Dict {chamado_id: quantidade_nao_lidas}
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_NAO_LIDAS_POR_CHAMADO, (usuario_id,))
        rows = cursor.fetchall()

        # Criar dicionário {chamado_id: count}
        resultado = {}
        for row in rows:
            resultado[row["chamado_id"]] = row["nao_lidas"]

        return resultado


def tem_resposta_admin(chamado_id: int) -> bool:
    """
    Verifica se um chamado possui ao menos uma resposta de administrador.

    Args:
        chamado_id: ID do chamado

    Returns:
        True se houver pelo menos uma resposta de admin, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(TEM_RESPOSTA_ADMIN, (chamado_id,))
        row = cursor.fetchone()
        return row["total"] > 0 if row else False
