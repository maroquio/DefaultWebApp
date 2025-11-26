from typing import Optional
from model.chamado_model import Chamado, StatusChamado, PrioridadeChamado
from sql.chamado_sql import *
from util.db_util import obter_conexao
from util.datetime_util import agora


def _row_to_chamado(row) -> Chamado:
    usuario_nome = row["usuario_nome"] if "usuario_nome" in row.keys() else None
    usuario_email = row["usuario_email"] if "usuario_email" in row.keys() else None

    return Chamado(
        id=row["id"],
        titulo=row["titulo"],
        status=StatusChamado(row["status"]),
        prioridade=PrioridadeChamado(row["prioridade"]),
        usuario_id=row["usuario_id"],
        data_abertura=row["data_abertura"],
        data_fechamento=row["data_fechamento"],
        usuario_nome=usuario_nome,
        usuario_email=usuario_email
    )


def criar_tabela() -> bool:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(chamado: Chamado) -> Optional[int]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            chamado.titulo,
            chamado.prioridade.value,
            chamado.status.value,
            chamado.usuario_id
        ))
        return cursor.lastrowid


def obter_todos(usuario_logado_id: int) -> list[Chamado]:
    from repo import chamado_interacao_repo

    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        chamados = [_row_to_chamado(row) for row in rows]

        # Obter contador de mensagens não lidas (excluindo próprias mensagens)
        contador_nao_lidas = chamado_interacao_repo.obter_contador_nao_lidas(usuario_logado_id)

        # Adicionar contador aos chamados
        for chamado in chamados:
            chamado.mensagens_nao_lidas = contador_nao_lidas.get(chamado.id, 0)

        return chamados


def obter_por_usuario(usuario_id: int) -> list[Chamado]:
    from repo import chamado_interacao_repo

    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_USUARIO, (usuario_id,))
        rows = cursor.fetchall()
        chamados = [_row_to_chamado(row) for row in rows]

        # Obter contador de mensagens não lidas (excluindo próprias mensagens do usuário)
        contador_nao_lidas = chamado_interacao_repo.obter_contador_nao_lidas(usuario_id)

        # Adicionar informações aos chamados
        for chamado in chamados:
            chamado.mensagens_nao_lidas = contador_nao_lidas.get(chamado.id, 0)
            chamado.tem_resposta_admin = chamado_interacao_repo.tem_resposta_admin(chamado.id)

        return chamados


def obter_por_id(id: int) -> Optional[Chamado]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_chamado(row)
        return None


def atualizar_status(
    id: int,
    status: str,
    fechar: bool = False
) -> bool:
    # Passar datetime diretamente (não usar strftime) para preservar timezone
    data_fechamento = agora() if fechar else None

    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_STATUS, (
            status,
            data_fechamento,
            id
        ))
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0


def contar_abertos_por_usuario(usuario_id: int) -> int:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_ABERTOS_POR_USUARIO, (usuario_id,))
        row = cursor.fetchone()
        return row["total"] if row else 0


def contar_pendentes() -> int:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_PENDENTES)
        row = cursor.fetchone()
        return row["total"] if row else 0
