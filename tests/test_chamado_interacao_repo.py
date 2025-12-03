"""
Testes para o repositório de interações de chamados (repo/chamado_interacao_repo.py)

Testa as funções de CRUD para interações de chamados.
"""

import pytest
from unittest.mock import patch, MagicMock

from repo import chamado_interacao_repo


class TestObterPorId:
    """Testes para a função obter_por_id()"""

    def test_obter_por_id_existente(self):
        """Deve retornar interação quando existe"""
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda self, key: {
            "id": 1,
            "chamado_id": 10,
            "usuario_id": 5,
            "mensagem": "Mensagem de teste",
            "tipo": "Abertura",
            "data_interacao": "2025-01-01 10:00:00",
            "status_resultante": None,
            "data_leitura": None,
            "usuario_nome": "Teste",
            "usuario_email": "teste@email.com"
        }.get(key)
        mock_row.keys.return_value = [
            "id", "chamado_id", "usuario_id", "mensagem", "tipo",
            "data_interacao", "status_resultante", "data_leitura",
            "usuario_nome", "usuario_email"
        ]
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_row
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('repo.chamado_interacao_repo.obter_conexao', return_value=mock_conn):
            resultado = chamado_interacao_repo.obter_por_id(1)

            mock_cursor.execute.assert_called_once()
            assert resultado is not None
            assert resultado.id == 1
            assert resultado.mensagem == "Mensagem de teste"

    def test_obter_por_id_nao_existente(self):
        """Deve retornar None quando não existe"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('repo.chamado_interacao_repo.obter_conexao', return_value=mock_conn):
            resultado = chamado_interacao_repo.obter_por_id(999)

            assert resultado is None


class TestContarPorChamado:
    """Testes para a função contar_por_chamado()"""

    def test_contar_com_interacoes(self):
        """Deve retornar número correto de interações"""
        mock_row = {"total": 5}
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_row
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('repo.chamado_interacao_repo.obter_conexao', return_value=mock_conn):
            resultado = chamado_interacao_repo.contar_por_chamado(10)

            assert resultado == 5

    def test_contar_sem_interacoes(self):
        """Deve retornar 0 quando não há interações"""
        mock_row = {"total": 0}
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_row
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('repo.chamado_interacao_repo.obter_conexao', return_value=mock_conn):
            resultado = chamado_interacao_repo.contar_por_chamado(999)

            assert resultado == 0

    def test_contar_sem_resultado(self):
        """Deve retornar 0 quando fetchone retorna None"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('repo.chamado_interacao_repo.obter_conexao', return_value=mock_conn):
            resultado = chamado_interacao_repo.contar_por_chamado(999)

            assert resultado == 0


class TestExcluirPorChamado:
    """Testes para a função excluir_por_chamado()"""

    def test_excluir_com_interacoes(self):
        """Deve retornar True ao excluir interações"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 3
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('repo.chamado_interacao_repo.obter_conexao', return_value=mock_conn):
            resultado = chamado_interacao_repo.excluir_por_chamado(10)

            mock_cursor.execute.assert_called_once()
            assert resultado is True

    def test_excluir_sem_interacoes(self):
        """Deve retornar True mesmo sem interações para excluir"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('repo.chamado_interacao_repo.obter_conexao', return_value=mock_conn):
            resultado = chamado_interacao_repo.excluir_por_chamado(999)

            # Deve retornar True (rowcount >= 0)
            assert resultado is True
