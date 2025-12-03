from typing import Optional
from model.artigo_model import Artigo
from sql.artigo_sql import *
from util.db_util import obter_conexao


def _row_to_artigo(row) -> Artigo:
    """
    Converte uma linha do banco de dados em objeto Artigo.
    """
    return Artigo(
        id=row["id"],
        titulo=row["titulo"],
        resumo=row["resumo"] if "resumo" in row.keys() else None,
        conteudo=row["conteudo"],
        status=row["status"],
        usuario_id=row["usuario_id"],
        categoria_id=row["categoria_id"],
        qtde_visualizacoes=row["qtde_visualizacoes"] if "qtde_visualizacoes" in row.keys() else 0,
        data_cadastro=row["data_cadastro"] if "data_cadastro" in row.keys() else None,
        data_atualizacao=row["data_atualizacao"] if "data_atualizacao" in row.keys() else None,
        data_publicacao=row["data_publicacao"] if "data_publicacao" in row.keys() else None,
        data_pausa=row["data_pausa"] if "data_pausa" in row.keys() else None,
        usuario_nome=row["usuario_nome"] if "usuario_nome" in row.keys() else None,
        usuario_email=row["usuario_email"] if "usuario_email" in row.keys() else None,
        categoria_nome=row["categoria_nome"] if "categoria_nome" in row.keys() else None,
    )


def criar_tabela() -> bool:
    """Cria a tabela de artigos se não existir."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(CRIAR_TABELA)
            return True
    except Exception as e:
        print(f"Erro ao criar tabela artigo: {e}")
        return False


def inserir(artigo: Artigo) -> Optional[int]:
    """Insere um novo artigo e retorna o ID gerado."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERIR, (
                artigo.titulo,
                artigo.resumo,
                artigo.conteudo,
                artigo.status,
                artigo.usuario_id,
                artigo.categoria_id
            ))
            return cursor.lastrowid
    except Exception as e:
        print(f"Erro ao inserir artigo: {e}")
        return None


def alterar(artigo: Artigo) -> bool:
    """Atualiza um artigo existente."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(ALTERAR, (
                artigo.titulo,
                artigo.resumo,
                artigo.conteudo,
                artigo.status,
                artigo.categoria_id,
                artigo.id
            ))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao alterar artigo: {e}")
        return False


def alterar_status(id: int, status: str) -> bool:
    """Atualiza apenas o status de um artigo."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(ALTERAR_STATUS, (status, status, status, id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao alterar status do artigo: {e}")
        return False


def excluir(id: int) -> bool:
    """Exclui um artigo pelo ID."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(EXCLUIR, (id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao excluir artigo: {e}")
        return False


def obter_por_id(id: int) -> Optional[Artigo]:
    """Busca um artigo pelo ID."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_ID, (id,))
            row = cursor.fetchone()
            if row:
                return _row_to_artigo(row)
            return None
    except Exception as e:
        print(f"Erro ao obter artigo por ID: {e}")
        return None


def obter_todos() -> list[Artigo]:
    """Retorna todos os artigos."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_TODOS)
            rows = cursor.fetchall()
            return [_row_to_artigo(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter todos os artigos: {e}")
        return []


def obter_por_usuario(usuario_id: int) -> list[Artigo]:
    """Retorna todos os artigos de um usuário específico."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_USUARIO, (usuario_id,))
            rows = cursor.fetchall()
            return [_row_to_artigo(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter artigos por usuário: {e}")
        return []


def obter_publicados() -> list[Artigo]:
    """Retorna todos os artigos publicados."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_PUBLICADOS)
            rows = cursor.fetchall()
            return [_row_to_artigo(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter artigos publicados: {e}")
        return []


def obter_ultimos_publicados(limite: int = 6) -> list[Artigo]:
    """Retorna os últimos N artigos publicados."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_ULTIMOS_PUBLICADOS, (limite,))
            rows = cursor.fetchall()
            return [_row_to_artigo(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter últimos artigos publicados: {e}")
        return []


def buscar_por_titulo(termo: str) -> list[Artigo]:
    """Busca artigos publicados pelo título."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(BUSCAR_POR_TITULO, (f"%{termo}%",))
            rows = cursor.fetchall()
            return [_row_to_artigo(row) for row in rows]
    except Exception as e:
        print(f"Erro ao buscar artigos por título: {e}")
        return []


def obter_por_categoria(categoria_id: int) -> list[Artigo]:
    """Retorna artigos publicados de uma categoria específica."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_CATEGORIA, (categoria_id,))
            rows = cursor.fetchall()
            return [_row_to_artigo(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter artigos por categoria: {e}")
        return []


def incrementar_visualizacoes(id: int) -> bool:
    """Incrementa o contador de visualizações de um artigo."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(INCREMENTAR_VISUALIZACOES, (id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao incrementar visualizações: {e}")
        return False


def obter_quantidade() -> int:
    """Retorna a quantidade total de artigos."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_QUANTIDADE)
            row = cursor.fetchone()
            return row["quantidade"] if row else 0
    except Exception as e:
        print(f"Erro ao obter quantidade de artigos: {e}")
        return 0


def obter_quantidade_publicados() -> int:
    """Retorna a quantidade de artigos publicados."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_QUANTIDADE_PUBLICADOS)
            row = cursor.fetchone()
            return row["quantidade"] if row else 0
    except Exception as e:
        print(f"Erro ao obter quantidade de artigos publicados: {e}")
        return 0


def titulo_existe(titulo: str, excluir_id: int = 0) -> bool:
    """Verifica se um título já existe (excluindo um ID específico)."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(VERIFICAR_TITULO_EXISTE, (titulo, excluir_id))
            row = cursor.fetchone()
            return row is not None
    except Exception as e:
        print(f"Erro ao verificar título: {e}")
        return False