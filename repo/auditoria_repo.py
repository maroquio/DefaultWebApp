"""
Repositório de Auditoria Estruturada.

Gerencia o registro e consulta de ações realizadas na aplicação,
diferente dos logs de arquivo (que são para erros técnicos),
a auditoria registra AÇÕES DE NEGÓCIO (quem fez o quê, quando).

Uso via decorator (recomendado):
    from util.auditoria_decorator import auditar

    @router.post("/produto/excluir/{id}")
    @auditar(acao='excluir', entidade='produto')
    async def excluir(...):
        ...

Uso direto (para casos específicos):
    from repo import auditoria_repo
    auditoria_repo.registrar(usuario_id=1, acao='criar', entidade='pedido', entidade_id=42)
"""

import sqlite3
from typing import Optional

from model.auditoria_model import RegistroAuditoria, AcaoAuditoria
from sql.auditoria_sql import CRIAR_TABELA, INSERIR, OBTER_COM_FILTROS, CONTAR_COM_FILTROS, OBTER_POR_ID
from util.db_util import obter_conexao
from util.logger_config import logger


def _row_to_auditoria(row: sqlite3.Row) -> RegistroAuditoria:
    """Converte sqlite3.Row em dataclass RegistroAuditoria."""
    try:
        acao = AcaoAuditoria(row["acao"])
    except ValueError:
        acao = AcaoAuditoria.ATUALIZAR

    return RegistroAuditoria(
        id=row["id"],
        usuario_id=row["usuario_id"],
        usuario_nome=row["usuario_nome"] if "usuario_nome" in row.keys() else None,
        acao=acao,
        entidade=row["entidade"],
        entidade_id=row["entidade_id"],
        dados_antes=row["dados_antes"],
        dados_depois=row["dados_depois"],
        ip=row["ip"],
        data=row["data"],
    )


def criar_tabela() -> bool:
    """Cria a tabela de auditoria se não existir."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def registrar(
    acao: str,
    entidade: str,
    usuario_id: Optional[int] = None,
    entidade_id: Optional[int] = None,
    dados_antes: Optional[str] = None,
    dados_depois: Optional[str] = None,
    ip: Optional[str] = None,
) -> Optional[int]:
    """
    Registra uma ação de auditoria no banco de dados.

    Args:
        acao: Tipo da ação (use AcaoAuditoria.VALUE ou string)
        entidade: Nome da entidade afetada (ex: 'usuario', 'produto', 'pedido')
        usuario_id: ID do usuário que realizou a ação (None para ações do sistema)
        entidade_id: ID da entidade afetada (None se não aplicável)
        dados_antes: JSON string com estado anterior (para atualizações/exclusões)
        dados_depois: JSON string com estado posterior (para criações/atualizações)
        ip: Endereço IP do cliente

    Returns:
        ID do registro criado ou None em caso de erro

    Prefira usar o decorator @auditar() para registrar automaticamente nas routes.
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERIR, (
                usuario_id,
                acao,
                entidade,
                entidade_id,
                dados_antes,
                dados_depois,
                ip,
            ))
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Erro ao registrar auditoria [{acao}/{entidade}]: {e}")
        return None


def obter_com_filtros(
    usuario_id: Optional[int] = None,
    acao: Optional[str] = None,
    entidade: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    pagina: int = 1,
    por_pagina: int = 20,
) -> tuple[list[RegistroAuditoria], int]:
    """
    Busca registros de auditoria com filtros opcionais.

    Args:
        usuario_id: Filtrar por usuário específico
        acao: Filtrar por tipo de ação (ex: 'criar', 'excluir')
        entidade: Filtrar por entidade (ex: 'usuario', 'produto')
        data_inicio: Data início no formato YYYY-MM-DD
        data_fim: Data fim no formato YYYY-MM-DD
        pagina: Número da página (1-based)
        por_pagina: Itens por página

    Returns:
        Tupla (lista de registros, total de registros)
    """
    filtros = []
    params: list = []

    if usuario_id:
        filtros.append("AND a.usuario_id = ?")
        params.append(usuario_id)

    if acao:
        filtros.append("AND a.acao = ?")
        params.append(acao)

    if entidade:
        filtros.append("AND a.entidade = ?")
        params.append(entidade)

    if data_inicio:
        filtros.append("AND date(a.data) >= ?")
        params.append(data_inicio)

    if data_fim:
        filtros.append("AND date(a.data) <= ?")
        params.append(data_fim)

    # Os `filtros` contêm APENAS fragmentos SQL literais (ex: "AND col = ?").
    # Valores reais do usuário são passados separadamente em `params` via placeholders ?.
    # NUNCA usar .format() com input do usuário diretamente — isso causaria SQL injection.
    filtros_str = " ".join(filtros)
    sql_count = CONTAR_COM_FILTROS.format(filtros=filtros_str)
    sql_dados = OBTER_COM_FILTROS.format(filtros=filtros_str)

    offset = (pagina - 1) * por_pagina

    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()

            # Contar total
            cursor.execute(sql_count, params)
            row = cursor.fetchone()
            total = row["total"] if row else 0

            # Buscar dados
            cursor.execute(sql_dados, [*params, por_pagina, offset])
            registros = [_row_to_auditoria(r) for r in cursor.fetchall()]

            return registros, total

    except sqlite3.Error as e:
        logger.error(f"Erro ao consultar auditoria: {e}")
        return [], 0
