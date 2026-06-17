"""
Testes para o repositório de índices (repo/indices_repo.py)

Testa a criação de índices do banco de dados incluindo
tratamento de erros quando índices já existem.
"""

import pytest
from unittest.mock import patch, MagicMock
import sqlite3

from repo import indices_repo


class TestCriarIndices:
    """Testes para a função criar_indices()"""

    def test_cria_indices_com_sucesso(self):
        """Deve criar índices sem erro"""
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('repo.indices_repo.obter_conexao', return_value=mock_conn):
            with patch('repo.indices_repo.indices_sql') as mock_sql:
                mock_sql.TODOS_INDICES = ["CREATE INDEX idx1 ON t(c)", "CREATE INDEX idx2 ON t2(c2)"]

                with patch('repo.indices_repo.logger') as mock_logger:
                    indices_repo.criar_indices()

                    # Deve executar cada índice
                    assert mock_cursor.execute.call_count == 2
                    # Deve logar sucesso
                    mock_logger.info.assert_called_once()

    def test_indice_ja_existe_loga_warning(self):
        """Quando índice já existe, deve logar warning e continuar"""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = sqlite3.OperationalError("index already exists")
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('repo.indices_repo.obter_conexao', return_value=mock_conn):
            with patch('repo.indices_repo.indices_sql') as mock_sql:
                mock_sql.TODOS_INDICES = ["CREATE INDEX idx1 ON t(c)"]

                with patch('repo.indices_repo.logger') as mock_logger:
                    # Não deve levantar exceção
                    indices_repo.criar_indices()

                    # Deve logar warning
                    mock_logger.warning.assert_called_once()
                    assert "pode já existir" in str(mock_logger.warning.call_args)

    def test_erro_sqlite_loga_erro(self):
        """Erro de SQLite deve logar erro e não crashar"""
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(side_effect=sqlite3.Error("Database locked"))
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('repo.indices_repo.obter_conexao', return_value=mock_conn):
            with patch('repo.indices_repo.logger') as mock_logger:
                # Não deve levantar exceção
                indices_repo.criar_indices()

                # Deve logar erro
                mock_logger.error.assert_called_once()
                assert "Erro ao criar índices" in str(mock_logger.error.call_args)

    def test_lista_indices_vazia(self):
        """Deve funcionar com lista de índices vazia"""
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('repo.indices_repo.obter_conexao', return_value=mock_conn):
            with patch('repo.indices_repo.indices_sql') as mock_sql:
                mock_sql.TODOS_INDICES = []

                with patch('repo.indices_repo.logger') as mock_logger:
                    indices_repo.criar_indices()

                    # Não deve executar nenhum SQL
                    mock_cursor.execute.assert_not_called()
                    # Deve logar sucesso mesmo assim
                    mock_logger.info.assert_called_once()
