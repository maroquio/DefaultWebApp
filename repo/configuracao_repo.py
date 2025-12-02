import sqlite3
from typing import Optional
from model.configuracao_model import Configuracao
from sql.configuracao_sql import (
    CRIAR_TABELA,
    INSERIR,
    OBTER_POR_CHAVE,
    OBTER_TODOS,
    ATUALIZAR,
)
from util.db_util import obter_conexao
from util.logger_config import logger


def _row_to_configuracao(row: sqlite3.Row) -> Configuracao:
    """
    Converte uma linha do banco de dados em objeto Configuracao.

    Args:
        row: Linha do cursor SQLite (sqlite3.Row)

    Returns:
        Objeto Configuracao populado
    """
    return Configuracao(
        id=row["id"],
        chave=row["chave"],
        valor=row["valor"],
        descricao=row["descricao"] if "descricao" in row.keys() else None
    )


def criar_tabela() -> bool:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def obter_por_chave(chave: str) -> Optional[Configuracao]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_CHAVE, (chave,))
        row = cursor.fetchone()
        if row:
            return _row_to_configuracao(row)
        return None


def obter_todos() -> list[Configuracao]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_configuracao(row) for row in rows]


def obter_por_categoria() -> dict[str, list[Configuracao]]:
    """
    Obtém todas as configurações agrupadas por categoria.

    A categoria é extraída da descrição no formato "[Categoria] Descrição".
    Configurações sem categoria ficam em "Outras".

    Returns:
        Dicionário {categoria: [configuracoes]}
    """
    import re

    todas = obter_todos()
    agrupadas: dict[str, list[Configuracao]] = {}

    for config in todas:
        # Extrai categoria da descrição usando regex
        categoria = "Outras"
        if config.descricao:
            match = re.match(r'^\[([^\]]+)\]', config.descricao)
            if match:
                categoria = match.group(1)

        if categoria not in agrupadas:
            agrupadas[categoria] = []

        agrupadas[categoria].append(config)

    # Ordena categorias alfabeticamente, mas mantém "Outras" por último
    categorias_ordenadas = sorted(agrupadas.keys())
    if "Outras" in categorias_ordenadas:
        categorias_ordenadas.remove("Outras")
        categorias_ordenadas.append("Outras")

    return {cat: agrupadas[cat] for cat in categorias_ordenadas}


def obter_multiplas(chaves: list[str]) -> dict[str, Optional[Configuracao]]:
    """
    Obtém múltiplas configurações de uma vez.

    Args:
        chaves: Lista de chaves a buscar

    Returns:
        Dicionário {chave: Configuracao ou None}
    """
    resultado = {}
    for chave in chaves:
        resultado[chave] = obter_por_chave(chave)
    return resultado


def atualizar(chave: str, valor: str) -> bool:
    """
    Atualiza o valor de uma configuração existente

    Args:
        chave: Chave da configuração
        valor: Novo valor

    Returns:
        True se atualização foi bem-sucedida, False se configuração não existe
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (valor, chave))
        return cursor.rowcount > 0


def atualizar_multiplas(configs: dict[str, str]) -> tuple[int, list[str]]:
    """
    Atualiza múltiplas configurações de uma vez (operação atômica).

    Todas as atualizações são executadas em uma única transação.
    Se alguma falhar, todas são revertidas (rollback automático).

    Args:
        configs: Dicionário {chave: valor} com as configurações a atualizar

    Returns:
        Tupla (quantidade_atualizada, chaves_nao_encontradas)
    """
    if not configs:
        return (0, [])

    quantidade_atualizada = 0
    chaves_nao_encontradas = []

    with obter_conexao() as conn:
        cursor = conn.cursor()

        for chave, valor in configs.items():
            # Verificar se configuração existe
            cursor.execute(OBTER_POR_CHAVE, (chave,))
            if not cursor.fetchone():
                chaves_nao_encontradas.append(chave)
                logger.warning(f"Configuração '{chave}' não existe, ignorando atualização")
                continue

            # Atualizar configuração
            cursor.execute(ATUALIZAR, (valor, chave))
            if cursor.rowcount > 0:
                quantidade_atualizada += 1
                logger.debug(f"Configuração '{chave}' atualizada para: {valor}")

    logger.info(
        f"Atualização em lote concluída: {quantidade_atualizada} atualizadas, "
        f"{len(chaves_nao_encontradas)} não encontradas"
    )

    return (quantidade_atualizada, chaves_nao_encontradas)


def inserir_ou_atualizar(chave: str, valor: str, descricao: str = "") -> bool:
    """
    Insere ou atualiza uma configuração (operação upsert)

    Se a configuração já existe, atualiza o valor.
    Se não existe, insere nova configuração.

    Args:
        chave: Chave da configuração
        valor: Valor da configuração
        descricao: Descrição da configuração (usado apenas em inserção)

    Returns:
        True se operação foi bem-sucedida, False caso contrário
    """
    try:
        # Verificar se configuração já existe
        config_existente = obter_por_chave(chave)

        if config_existente:
            # Configuração existe - atualizar
            logger.debug(f"Atualizando configuração existente: {chave} = {valor}")
            return atualizar(chave, valor)
        else:
            # Configuração não existe - inserir
            logger.debug(f"Inserindo nova configuração: {chave} = {valor}")
            with obter_conexao() as conn:
                cursor = conn.cursor()
                cursor.execute(INSERIR, (chave, valor, descricao))
                return cursor.rowcount > 0

    except sqlite3.Error as e:
        logger.error(f"Erro ao inserir ou atualizar configuração '{chave}': {e}")
        raise


def inserir_padrao() -> None:
    """Insere configurações padrão se não existirem"""
    configs_padrao = [
        ("nome_sistema", "Sistema Web", "Nome do sistema"),
        ("email_contato", "contato@sistema.com", "E-mail de contato"),
        ("tema_padrao", "claro", "Tema padrão (claro/escuro)"),
        ("theme", "original", "Tema visual da aplicação (Bootswatch)"),
    ]

    with obter_conexao() as conn:
        cursor = conn.cursor()
        for chave, valor, descricao in configs_padrao:
            try:
                cursor.execute(INSERIR, (chave, valor, descricao))
            except sqlite3.IntegrityError:
                # Configuração já existe (violação de UNIQUE constraint)
                logger.debug(f"Configuração '{chave}' já existe, pulando inserção")
            except sqlite3.Error as e:
                # Outro tipo de erro de banco - logar e re-raise para não mascarar problema
                logger.error(f"Erro ao inserir configuração padrão '{chave}': {e}")
                raise
