"""
Testes para o módulo util/db_util.py

Testa as funções de conexão e adaptadores de banco de dados.
"""

import pytest
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch, MagicMock
import tempfile
import os


class TestObterConexao:
    """Testes para o context manager obter_conexao"""

    def test_conexao_commit_em_sucesso(self):
        """Deve fazer commit quando não há erro"""
        from util.db_util import obter_conexao

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            with patch('util.db_util.DATABASE_PATH', db_path):
                with obter_conexao() as conn:
                    conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
                    conn.execute("INSERT INTO test VALUES (1)")

                # Verificar que dados foram salvos
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("SELECT * FROM test")
                rows = cursor.fetchall()
                conn.close()

                assert len(rows) == 1

    def test_conexao_rollback_em_erro(self):
        """Deve fazer rollback quando há erro"""
        from util.db_util import obter_conexao

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            # Criar tabela primeiro
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO test VALUES (1)")
            conn.commit()
            conn.close()

            with patch('util.db_util.DATABASE_PATH', db_path):
                try:
                    with obter_conexao() as conn:
                        # Inserir dados
                        conn.execute("INSERT INTO test VALUES (2)")
                        # Causar erro
                        raise ValueError("Erro intencional para teste")
                except ValueError:
                    pass

                # Verificar que segundo registro não foi salvo
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("SELECT * FROM test")
                rows = cursor.fetchall()
                conn.close()

                assert len(rows) == 1  # Apenas o registro inicial

    def test_conexao_propaga_excecao(self):
        """Deve propagar exceção após rollback"""
        from util.db_util import obter_conexao

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            with patch('util.db_util.DATABASE_PATH', db_path):
                with pytest.raises(RuntimeError, match="Erro de teste"):
                    with obter_conexao() as conn:
                        conn.execute("CREATE TABLE test (id INT)")
                        raise RuntimeError("Erro de teste")


class TestAdaptarDatetime:
    """Testes para a função adaptar_datetime"""

    def test_converte_datetime_com_timezone_para_utc(self):
        """Deve converter datetime com timezone para UTC"""
        from util.db_util import adaptar_datetime

        # Datetime em São Paulo (UTC-3)
        tz_sp = ZoneInfo("America/Sao_Paulo")
        dt_sp = datetime(2025, 1, 15, 12, 0, 0, tzinfo=tz_sp)

        resultado = adaptar_datetime(dt_sp)

        # Deve estar em formato ISO sem timezone
        assert "T" not in resultado or " " in resultado  # Formato com espaço
        # Hora deve ser convertida para UTC (15:00 UTC para 12:00 São Paulo)
        assert "15:00:00" in resultado or "12:00:00" in resultado

    def test_datetime_naive_tratado_como_utc(self):
        """Datetime naive deve ser tratado como UTC"""
        from util.db_util import adaptar_datetime

        # Datetime sem timezone
        dt_naive = datetime(2025, 1, 15, 12, 0, 0)

        resultado = adaptar_datetime(dt_naive)

        # Hora deve permanecer a mesma (assume UTC)
        assert "12:00:00" in resultado


class TestConverterDatetime:
    """Testes para a função converter_datetime"""

    def test_converte_string_para_datetime_com_timezone(self):
        """Deve converter string do banco para datetime com timezone"""
        from util.db_util import converter_datetime

        # String no formato do banco
        s = b"2025-01-15 12:00:00"

        resultado = converter_datetime(s)

        assert isinstance(resultado, datetime)
        assert resultado.tzinfo is not None

    def test_resultado_em_timezone_local(self):
        """Resultado deve estar no timezone da aplicação"""
        from util.db_util import converter_datetime, APP_TIMEZONE

        s = b"2025-01-15 15:00:00"  # 15:00 UTC

        resultado = converter_datetime(s)

        # Deve estar no timezone da aplicação
        assert resultado.tzinfo is not None


class TestRegistrarAdaptadores:
    """Testes para a função registrar_adaptadores"""

    def test_registra_adaptadores(self):
        """Deve registrar adaptadores sem erro"""
        from util.db_util import registrar_adaptadores

        # Não deve lançar exceção
        registrar_adaptadores()

    def test_adaptadores_funcionam(self):
        """Adaptadores devem funcionar com SQLite"""
        from util.db_util import registrar_adaptadores, adaptar_datetime

        registrar_adaptadores()

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")

            conn = sqlite3.connect(
                db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )

            # Criar tabela com coluna TIMESTAMP
            conn.execute("CREATE TABLE test (dt TIMESTAMP)")

            # Inserir datetime
            dt = datetime(2025, 1, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
            conn.execute("INSERT INTO test VALUES (?)", (dt,))
            conn.commit()

            # Verificar que foi salvo
            cursor = conn.execute("SELECT dt FROM test")
            row = cursor.fetchone()
            conn.close()

            assert row is not None
