"""
Testes para o módulo util/validation_helpers.py

Testa os helpers de validação reutilizáveis.
"""

import pytest
from unittest.mock import patch, MagicMock
import sqlite3

from util.validation_helpers import (
    verificar_email_disponivel,
    email_existe
)


class TestVerificarEmailDisponivel:
    """Testes para a função verificar_email_disponivel()"""

    def test_email_novo_disponivel(self):
        """Email que não existe deve estar disponível"""
        with patch('util.validation_helpers.usuario_repo') as mock_repo:
            mock_repo.obter_por_email.return_value = None

            disponivel, msg = verificar_email_disponivel("novo@email.com")

            assert disponivel is True
            assert msg is None

    def test_email_existente_cadastro_novo(self):
        """Email existente em cadastro novo deve ser indisponível"""
        mock_usuario = MagicMock()
        mock_usuario.id = 10

        with patch('util.validation_helpers.usuario_repo') as mock_repo:
            mock_repo.obter_por_email.return_value = mock_usuario

            with patch('util.validation_helpers.logger'):
                disponivel, msg = verificar_email_disponivel("existente@email.com")

                assert disponivel is False
                assert "já está cadastrado" in msg

    def test_email_proprio_usuario_edicao(self):
        """Email do próprio usuário em edição deve estar disponível"""
        mock_usuario = MagicMock()
        mock_usuario.id = 5

        with patch('util.validation_helpers.usuario_repo') as mock_repo:
            mock_repo.obter_por_email.return_value = mock_usuario

            disponivel, msg = verificar_email_disponivel(
                "meu@email.com",
                usuario_id_atual=5
            )

            assert disponivel is True
            assert msg is None

    def test_email_outro_usuario_edicao(self):
        """Email de outro usuário em edição deve ser indisponível"""
        mock_usuario = MagicMock()
        mock_usuario.id = 10

        with patch('util.validation_helpers.usuario_repo') as mock_repo:
            mock_repo.obter_por_email.return_value = mock_usuario

            with patch('util.validation_helpers.logger'):
                disponivel, msg = verificar_email_disponivel(
                    "outro@email.com",
                    usuario_id_atual=5
                )

                assert disponivel is False
                assert "já está sendo usado" in msg

    def test_erro_sqlite_retorna_indisponivel(self):
        """Erro de SQLite deve retornar indisponível por segurança"""
        with patch('util.validation_helpers.usuario_repo') as mock_repo:
            mock_repo.obter_por_email.side_effect = sqlite3.Error("Database error")

            with patch('util.validation_helpers.logger') as mock_logger:
                disponivel, msg = verificar_email_disponivel("test@email.com")

                assert disponivel is False
                assert "Erro ao verificar" in msg
                mock_logger.error.assert_called_once()


class TestEmailExiste:
    """Testes para a função email_existe()"""

    def test_email_existe_true(self):
        """Deve retornar True quando email existe"""
        mock_usuario = MagicMock()

        with patch('util.validation_helpers.usuario_repo') as mock_repo:
            mock_repo.obter_por_email.return_value = mock_usuario

            resultado = email_existe("existe@email.com")

            assert resultado is True

    def test_email_existe_false(self):
        """Deve retornar False quando email não existe"""
        with patch('util.validation_helpers.usuario_repo') as mock_repo:
            mock_repo.obter_por_email.return_value = None

            resultado = email_existe("naoexiste@email.com")

            assert resultado is False

    def test_erro_sqlite_retorna_true(self):
        """Erro de SQLite deve retornar True por segurança"""
        with patch('util.validation_helpers.usuario_repo') as mock_repo:
            mock_repo.obter_por_email.side_effect = sqlite3.Error("DB error")

            with patch('util.validation_helpers.logger') as mock_logger:
                resultado = email_existe("test@email.com")

                # Retorna True por segurança em caso de erro
                assert resultado is True
                mock_logger.error.assert_called_once()
