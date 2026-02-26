"""
Utilitário de Paginação Genérica.

Fornece funções para paginar listas em memória e executar queries paginadas
diretamente no banco de dados via LIMIT/OFFSET.

Uso básico (lista em memória):
    from util.paginacao_util import paginar

    todos = repo.obter_todos()
    paginacao = paginar(todos, pagina=1, por_pagina=10)

    # No template:
    # {{ paginacao.items }}  -> lista da página atual
    # {{ paginacao.total_paginas }}  -> total de páginas

Uso com SQL (eficiente para grandes volumes):
    from util.paginacao_util import obter_paginado

    resultado = obter_paginado(
        sql_count="SELECT COUNT(*) as total FROM produto",
        sql_dados="SELECT * FROM produto ORDER BY nome",
        params=(),
        pagina=1,
        por_pagina=10,
        row_converter=_row_to_produto,
    )
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from util.db_util import obter_conexao
from util.logger_config import logger

# Constante: itens por página padrão
ITENS_POR_PAGINA_PADRAO = 10


@dataclass
class Paginacao:
    """
    Resultado de uma operação de paginação.

    Campos:
        items: Lista dos itens da página atual
        total: Total de itens em todas as páginas
        pagina_atual: Número da página atual (1-based)
        por_pagina: Número de itens por página
        total_paginas: Total de páginas calculado
        tem_anterior: True se existe página anterior
        tem_proxima: True se existe próxima página
        pagina_anterior: Número da página anterior (ou None)
        proxima_pagina: Número da próxima página (ou None)
        inicio: Índice do primeiro item (para exibição "Mostrando X-Y de Z")
        fim: Índice do último item (para exibição "Mostrando X-Y de Z")
        paginas: Lista de números de página para renderizar navegação
    """

    items: list = field(default_factory=list)
    total: int = 0
    pagina_atual: int = 1
    por_pagina: int = ITENS_POR_PAGINA_PADRAO

    # Calculados automaticamente no __post_init__
    total_paginas: int = 0
    tem_anterior: bool = False
    tem_proxima: bool = False
    pagina_anterior: Optional[int] = None
    proxima_pagina: Optional[int] = None
    inicio: int = 0
    fim: int = 0
    paginas: list = field(default_factory=list)

    def __post_init__(self):
        if self.por_pagina <= 0:
            self.por_pagina = ITENS_POR_PAGINA_PADRAO

        self.total_paginas = max(1, (self.total + self.por_pagina - 1) // self.por_pagina)
        self.tem_anterior = self.pagina_atual > 1
        self.tem_proxima = self.pagina_atual < self.total_paginas
        self.pagina_anterior = self.pagina_atual - 1 if self.tem_anterior else None
        self.proxima_pagina = self.pagina_atual + 1 if self.tem_proxima else None

        # Índices para "Mostrando X-Y de Z"
        self.inicio = (self.pagina_atual - 1) * self.por_pagina + 1 if self.total > 0 else 0
        self.fim = min(self.pagina_atual * self.por_pagina, self.total)

        # Gerar lista de páginas visíveis (máx 7 botões)
        self.paginas = _calcular_paginas_visiveis(self.pagina_atual, self.total_paginas)


def _calcular_paginas_visiveis(pagina_atual: int, total_paginas: int, max_botoes: int = 7) -> list:
    """
    Calcula quais números de página exibir na barra de navegação.

    Retorna lista com números de página e None para reticências (...).
    Exemplo: [1, None, 4, 5, 6, None, 10]
    """
    if total_paginas <= max_botoes:
        return list(range(1, total_paginas + 1))

    paginas = []
    metade = max_botoes // 2

    # Sempre mostrar primeira e última página
    inicio = max(2, pagina_atual - metade)
    fim = min(total_paginas - 1, pagina_atual + metade)

    # Ajustar janela se estiver perto das bordas
    if pagina_atual - metade <= 1:
        fim = max_botoes - 2
    if pagina_atual + metade >= total_paginas:
        inicio = total_paginas - max_botoes + 3

    paginas.append(1)
    if inicio > 2:
        paginas.append(None)  # Reticências
    for p in range(inicio, fim + 1):
        paginas.append(p)
    if fim < total_paginas - 1:
        paginas.append(None)  # Reticências
    paginas.append(total_paginas)

    return paginas


def paginar(lista: list, pagina: int = 1, por_pagina: int = ITENS_POR_PAGINA_PADRAO) -> Paginacao:
    """
    Pagina uma lista em memória.

    Args:
        lista: Lista completa de itens
        pagina: Número da página desejada (1-based)
        por_pagina: Quantidade de itens por página

    Returns:
        Objeto Paginacao com items da página e metadados

    Exemplo:
        todos = repo.obter_todos()
        paginacao = paginar(todos, pagina=2, por_pagina=10)
        # paginacao.items -> itens 11-20
        # paginacao.total -> len(todos)
    """
    if por_pagina <= 0:
        por_pagina = ITENS_POR_PAGINA_PADRAO

    total = len(lista)
    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)

    # Garantir página válida
    pagina = max(1, min(pagina, total_paginas))

    inicio = (pagina - 1) * por_pagina
    fim = inicio + por_pagina
    items = lista[inicio:fim]

    return Paginacao(
        items=items,
        total=total,
        pagina_atual=pagina,
        por_pagina=por_pagina,
    )


def obter_paginado(
    sql_count: str,
    sql_dados: str,
    params: tuple,
    pagina: int,
    por_pagina: int,
    row_converter: Optional[Callable] = None,
) -> Paginacao:
    """
    Executa query paginada diretamente no banco de dados usando LIMIT/OFFSET.

    Esta abordagem é mais eficiente que paginar() para grandes volumes de dados,
    pois só busca os itens da página atual do banco.

    Args:
        sql_count: Query SQL para contar total (deve retornar coluna 'total')
        sql_dados: Query SQL para dados SEM LIMIT/OFFSET (será adicionado automaticamente)
        params: Parâmetros para ambas as queries (mesmos parâmetros)
        pagina: Número da página (1-based)
        por_pagina: Quantidade de itens por página
        row_converter: Função opcional para converter sqlite3.Row em objeto

    Returns:
        Objeto Paginacao com items e metadados

    Exemplo:
        paginacao = obter_paginado(
            sql_count="SELECT COUNT(*) as total FROM produto WHERE ativo = ?",
            sql_dados="SELECT * FROM produto WHERE ativo = ? ORDER BY nome",
            params=(1,),
            pagina=1,
            por_pagina=10,
            row_converter=_row_to_produto,
        )
    """
    if por_pagina <= 0:
        por_pagina = ITENS_POR_PAGINA_PADRAO

    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()

            # Contar total
            cursor.execute(sql_count, params)
            row_count = cursor.fetchone()
            total = row_count["total"] if row_count else 0

            # Calcular total de páginas e garantir página válida
            total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
            pagina = max(1, min(pagina, total_paginas))

            # Buscar dados da página
            offset = (pagina - 1) * por_pagina
            sql_paginado = f"{sql_dados} LIMIT ? OFFSET ?"
            cursor.execute(sql_paginado, (*params, por_pagina, offset))
            rows = cursor.fetchall()

            # Converter rows se necessário
            if row_converter:
                items = [row_converter(row) for row in rows]
            else:
                items = [dict(row) for row in rows]

            return Paginacao(
                items=items,
                total=total,
                pagina_atual=pagina,
                por_pagina=por_pagina,
            )

    except Exception as e:
        logger.error(f"Erro ao paginar query: {e}", exc_info=True)
        return Paginacao(items=[], total=0, pagina_atual=1, por_pagina=por_pagina)


def obter_pagina_request(pagina_param: Any, por_pagina: int = ITENS_POR_PAGINA_PADRAO) -> tuple[int, int]:
    """
    Extrai e valida os parâmetros de paginação de uma requisição HTTP.

    Args:
        pagina_param: Valor do parâmetro 'pagina' da query string
        por_pagina: Itens por página (padrão: ITENS_POR_PAGINA_PADRAO)

    Returns:
        Tupla (pagina, por_pagina) com valores válidos

    Exemplo no route:
        @router.get("/lista")
        async def listar(request: Request, pagina: int = 1):
            pagina, por_pagina = obter_pagina_request(pagina)
            paginacao = paginar(repo.obter_todos(), pagina, por_pagina)
    """
    try:
        pagina = int(pagina_param)
        pagina = max(1, pagina)
    except (ValueError, TypeError):
        pagina = 1

    return pagina, max(1, por_pagina)
