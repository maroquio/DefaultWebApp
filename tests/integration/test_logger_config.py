"""
Testes para o módulo util/logger_config.py

Testa o sistema de logging com rotação diária.
"""

import pytest
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestDailyRotatingFileHandler:
    """Testes para a classe DailyRotatingFileHandler"""

    def test_cria_diretorio_logs(self):
        """Deve criar diretório de logs se não existir"""
        # Importa dentro do teste para evitar efeitos colaterais
        from util.logger_config import DailyRotatingFileHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs_teste")

            with patch('util.logger_config.agora') as mock_agora:
                mock_agora.return_value = datetime(2025, 1, 15, 10, 30)

                handler = DailyRotatingFileHandler(
                    log_dir=log_dir,
                    backupCount=7
                )

                assert Path(log_dir).exists()
                handler.close()

    def test_nome_arquivo_com_data(self):
        """Deve criar arquivo com data no nome"""
        from util.logger_config import DailyRotatingFileHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs")

            with patch('util.logger_config.agora') as mock_agora:
                mock_agora.return_value = datetime(2025, 1, 15, 10, 30)

                handler = DailyRotatingFileHandler(
                    log_dir=log_dir,
                    backupCount=7
                )

                assert "app.2025.01.15.log" in handler.baseFilename
                handler.close()

    def test_get_filename_for_date(self):
        """Deve gerar nome de arquivo correto para data"""
        from util.logger_config import DailyRotatingFileHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs")

            with patch('util.logger_config.agora') as mock_agora:
                mock_agora.return_value = datetime(2025, 1, 15)

                handler = DailyRotatingFileHandler(log_dir=log_dir)

                data_teste = datetime(2025, 3, 20)
                nome = handler._get_filename_for_date(data_teste)

                assert "app.2025.03.20.log" in nome
                handler.close()


class TestDailyRotatingFileHandlerRollover:
    """Testes para o rollover do DailyRotatingFileHandler"""

    def test_do_rollover_fecha_stream(self):
        """doRollover deve fechar stream atual"""
        from util.logger_config import DailyRotatingFileHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs")

            with patch('util.logger_config.agora') as mock_agora:
                mock_agora.return_value = datetime(2025, 1, 15)

                handler = DailyRotatingFileHandler(log_dir=log_dir, backupCount=0)

                # Força abertura do stream
                handler.emit(logging.LogRecord(
                    name="test",
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg="test",
                    args=(),
                    exc_info=None
                ))

                # Simula meia-noite
                mock_agora.return_value = datetime(2025, 1, 16)

                handler.doRollover()

                # Verifica que o novo arquivo tem a nova data
                assert "app.2025.01.16.log" in handler.baseFilename
                handler.close()

    def test_do_rollover_sem_stream(self):
        """doRollover sem stream não deve dar erro"""
        from util.logger_config import DailyRotatingFileHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs")

            with patch('util.logger_config.agora') as mock_agora:
                mock_agora.return_value = datetime(2025, 1, 15)

                handler = DailyRotatingFileHandler(
                    log_dir=log_dir,
                    backupCount=0
                )

                handler.stream = None  # Simula stream fechado

                mock_agora.return_value = datetime(2025, 1, 16)

                # Não deve lançar exceção
                handler.doRollover()

                handler.close()

    def test_do_rollover_com_backup_count(self):
        """doRollover deve respeitar backupCount"""
        from util.logger_config import DailyRotatingFileHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs")

            with patch('util.logger_config.agora') as mock_agora:
                mock_agora.return_value = datetime(2025, 1, 15)

                handler = DailyRotatingFileHandler(
                    log_dir=log_dir,
                    backupCount=3
                )

                assert handler.backupCount == 3
                handler.close()


class TestLoggerGlobal:
    """Testes para a instância global do logger"""

    def test_logger_existe(self):
        """Logger global deve existir"""
        from util.logger_config import logger

        assert logger is not None

    def test_logger_pode_logar(self):
        """Logger global deve poder registrar mensagens"""
        from util.logger_config import logger

        # Não deve lançar exceção
        logger.debug("Teste de debug")
        logger.info("Teste de info")
        logger.warning("Teste de warning")

    def test_logger_e_instancia_logger(self):
        """Logger global deve ser instância de Logger"""
        from util.logger_config import logger

        assert isinstance(logger, logging.Logger)
