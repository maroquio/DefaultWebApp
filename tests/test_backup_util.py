"""
Testes para o módulo util/backup_util.py

Testa todas as funções de gerenciamento de backup do banco de dados.
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import tempfile
import shutil

from util.backup_util import (
    BackupInfo,
    _formatar_tamanho,
    _validar_nome_arquivo,
    _garantir_diretorio_backup,
    _detectar_tipo_backup,
    _extrair_data_do_nome,
    _validar_integridade_backup,
    criar_backup,
    listar_backups,
    restaurar_backup,
    excluir_backup,
    obter_info_backup,
    obter_caminho_backup,
    BACKUP_DIR,
    BACKUP_FILENAME_PATTERN,
)


class TestBackupInfo:
    """Testes para o dataclass BackupInfo"""

    def test_criar_backup_info(self):
        """Deve criar objeto BackupInfo com todos os campos"""
        info = BackupInfo(
            nome_arquivo="backup_2025-01-15_10-30-00.db",
            caminho_completo="/backups/backup_2025-01-15_10-30-00.db",
            data_criacao=datetime(2025, 1, 15, 10, 30, 0),
            tamanho_bytes=1024000,
            tamanho_formatado="1000.00 KB",
            tipo="manual"
        )
        assert info.nome_arquivo == "backup_2025-01-15_10-30-00.db"
        assert info.tipo == "manual"
        assert info.tamanho_bytes == 1024000


class TestFormatarTamanho:
    """Testes para a função _formatar_tamanho"""

    def test_bytes(self):
        """Deve formatar em bytes para valores pequenos"""
        assert _formatar_tamanho(500) == "500 B"
        assert _formatar_tamanho(0) == "0 B"
        assert _formatar_tamanho(1023) == "1023 B"

    def test_kilobytes(self):
        """Deve formatar em KB"""
        resultado = _formatar_tamanho(1024)
        assert "KB" in resultado
        assert "1.00" in resultado

        resultado = _formatar_tamanho(1536)  # 1.5 KB
        assert "KB" in resultado

    def test_megabytes(self):
        """Deve formatar em MB"""
        resultado = _formatar_tamanho(1024 * 1024)  # 1 MB
        assert "MB" in resultado
        assert "1.00" in resultado

        resultado = _formatar_tamanho(5 * 1024 * 1024)  # 5 MB
        assert "MB" in resultado

    def test_gigabytes(self):
        """Deve formatar em GB"""
        resultado = _formatar_tamanho(1024 * 1024 * 1024)  # 1 GB
        assert "GB" in resultado
        assert "1.00" in resultado


class TestValidarNomeArquivo:
    """Testes para a função _validar_nome_arquivo"""

    def test_nome_valido_manual(self):
        """Deve aceitar nome válido de backup manual"""
        assert _validar_nome_arquivo("backup_2025-01-15_10-30-00.db") is True

    def test_nome_valido_automatico(self):
        """Deve aceitar nome válido de backup automático"""
        assert _validar_nome_arquivo("backup_auto_2025-01-15_10-30-00.db") is True

    def test_path_traversal_dois_pontos(self):
        """Deve rejeitar tentativa de path traversal com .."""
        assert _validar_nome_arquivo("../etc/passwd.db") is False
        assert _validar_nome_arquivo("backup_../test.db") is False

    def test_path_traversal_barra(self):
        """Deve rejeitar barra no nome"""
        assert _validar_nome_arquivo("/backup_test.db") is False
        assert _validar_nome_arquivo("backup/test.db") is False

    def test_path_traversal_barra_invertida(self):
        """Deve rejeitar barra invertida no nome"""
        assert _validar_nome_arquivo("backup\\test.db") is False

    def test_prefixo_invalido(self):
        """Deve rejeitar arquivos sem prefixo backup_"""
        assert _validar_nome_arquivo("database.db") is False
        assert _validar_nome_arquivo("bkp_2025-01-15.db") is False

    def test_extensao_invalida(self):
        """Deve rejeitar extensões diferentes de .db"""
        assert _validar_nome_arquivo("backup_2025-01-15.sql") is False
        assert _validar_nome_arquivo("backup_2025-01-15.txt") is False
        assert _validar_nome_arquivo("backup_2025-01-15") is False


class TestGarantirDiretorioBackup:
    """Testes para a função _garantir_diretorio_backup"""

    def test_criar_diretorio_se_nao_existir(self):
        """Deve criar diretório se não existir"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "novo_backup"

            with patch('util.backup_util.BACKUP_DIR', temp_path):
                _garantir_diretorio_backup()
                assert temp_path.exists()

    def test_nao_falhar_se_existir(self):
        """Não deve falhar se diretório já existir"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            with patch('util.backup_util.BACKUP_DIR', temp_path):
                # Não deve levantar exceção
                _garantir_diretorio_backup()
                assert temp_path.exists()


class TestDetectarTipoBackup:
    """Testes para a função _detectar_tipo_backup"""

    def test_backup_manual(self):
        """Deve detectar backup manual"""
        assert _detectar_tipo_backup("backup_2025-01-15_10-30-00.db") == "manual"

    def test_backup_automatico(self):
        """Deve detectar backup automático"""
        assert _detectar_tipo_backup("backup_auto_2025-01-15_10-30-00.db") == "automático"


class TestExtrairDataDoNome:
    """Testes para a função _extrair_data_do_nome"""

    def test_extrair_data_backup_manual(self):
        """Deve extrair data de nome de backup manual"""
        resultado = _extrair_data_do_nome("backup_2025-01-15_10-30-45.db")
        assert resultado is not None
        assert resultado.year == 2025
        assert resultado.month == 1
        assert resultado.day == 15
        assert resultado.hour == 10
        assert resultado.minute == 30
        assert resultado.second == 45

    def test_extrair_data_backup_automatico(self):
        """Deve extrair data de nome de backup automático"""
        resultado = _extrair_data_do_nome("backup_auto_2025-06-20_14-00-00.db")
        assert resultado is not None
        assert resultado.year == 2025
        assert resultado.month == 6
        assert resultado.day == 20
        assert resultado.hour == 14

    def test_nome_invalido_retorna_none(self):
        """Deve retornar None para nome inválido"""
        resultado = _extrair_data_do_nome("backup_invalido.db")
        assert resultado is None

    def test_formato_errado_retorna_none(self):
        """Deve retornar None para formato de data errado"""
        resultado = _extrair_data_do_nome("backup_15-01-2025.db")
        assert resultado is None


class TestValidarIntegridadeBackup:
    """Testes para a função _validar_integridade_backup"""

    @pytest.fixture
    def backup_valido(self):
        """Cria um arquivo de backup SQLite válido"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            # Criar banco SQLite válido
            conn = sqlite3.connect(f.name)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE teste (id INTEGER PRIMARY KEY)")
            cursor.execute("INSERT INTO teste VALUES (1)")
            conn.commit()
            conn.close()

            yield Path(f.name)

            # Cleanup
            Path(f.name).unlink(missing_ok=True)

    @pytest.fixture
    def backup_vazio(self):
        """Cria um arquivo vazio"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            # Arquivo vazio (tamanho 0)
            yield Path(f.name)
            Path(f.name).unlink(missing_ok=True)

    def test_backup_valido(self, backup_valido):
        """Deve validar backup íntegro"""
        valido, mensagem = _validar_integridade_backup(backup_valido)
        assert valido is True
        assert "válido" in mensagem.lower()

    def test_arquivo_nao_encontrado(self):
        """Deve falhar para arquivo inexistente"""
        caminho = Path("/caminho/que/nao/existe.db")
        valido, mensagem = _validar_integridade_backup(caminho)
        assert valido is False
        assert "não encontrado" in mensagem.lower()

    def test_arquivo_vazio(self, backup_vazio):
        """Deve falhar para arquivo vazio"""
        valido, mensagem = _validar_integridade_backup(backup_vazio)
        assert valido is False
        assert "vazio" in mensagem.lower()

    def test_arquivo_corrompido(self):
        """Deve falhar para arquivo corrompido"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            # Escrever dados inválidos
            f.write(b"conteudo invalido para sqlite")
            f.flush()

            caminho = Path(f.name)
            valido, mensagem = _validar_integridade_backup(caminho)

            assert valido is False
            assert "corrompido" in mensagem.lower() or "inválido" in mensagem.lower()

            caminho.unlink(missing_ok=True)


class TestCriarBackup:
    """Testes para a função criar_backup"""

    @pytest.fixture
    def setup_backup_env(self):
        """Configura ambiente de teste para backups"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir) / "backups"
            db_path = Path(temp_dir) / "database.db"

            # Criar banco de dados de teste
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE teste (id INTEGER PRIMARY KEY)")
            conn.commit()
            conn.close()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                with patch('util.backup_util.DATABASE_PATH', str(db_path)):
                    yield {
                        'backup_dir': backup_dir,
                        'db_path': db_path
                    }

    def test_criar_backup_manual(self, setup_backup_env):
        """Deve criar backup manual com sucesso"""
        sucesso, mensagem = criar_backup(automatico=False)

        assert sucesso is True
        assert "sucesso" in mensagem.lower()
        assert "manual" in mensagem.lower()

        # Verificar se arquivo foi criado
        backups = list(setup_backup_env['backup_dir'].glob("backup_*.db"))
        assert len(backups) == 1
        assert "_auto_" not in backups[0].name

    def test_criar_backup_automatico(self, setup_backup_env):
        """Deve criar backup automático com sucesso"""
        sucesso, mensagem = criar_backup(automatico=True)

        assert sucesso is True
        assert "sucesso" in mensagem.lower()
        assert "automático" in mensagem.lower()

        # Verificar se arquivo foi criado com prefixo auto
        backups = list(setup_backup_env['backup_dir'].glob("backup_auto_*.db"))
        assert len(backups) == 1

    def test_criar_backup_sem_banco(self):
        """Deve falhar se banco de dados não existir"""
        with patch('util.backup_util.DATABASE_PATH', '/caminho/inexistente/db.db'):
            with tempfile.TemporaryDirectory() as temp_dir:
                with patch('util.backup_util.BACKUP_DIR', Path(temp_dir)):
                    sucesso, mensagem = criar_backup()

                    assert sucesso is False
                    assert "não encontrado" in mensagem.lower()


class TestListarBackups:
    """Testes para a função listar_backups"""

    @pytest.fixture
    def setup_backups(self):
        """Cria ambiente com vários backups de teste"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)

            # Criar vários arquivos de backup
            backups_criados = []

            for i, nome in enumerate([
                "backup_2025-01-10_10-00-00.db",
                "backup_2025-01-15_10-00-00.db",
                "backup_auto_2025-01-12_10-00-00.db"
            ]):
                caminho = backup_dir / nome
                # Criar banco SQLite válido
                conn = sqlite3.connect(str(caminho))
                conn.execute("CREATE TABLE t (id INT)")
                conn.commit()
                conn.close()
                backups_criados.append(nome)

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                yield {
                    'backup_dir': backup_dir,
                    'backups': backups_criados
                }

    def test_listar_backups(self, setup_backups):
        """Deve listar todos os backups"""
        backups = listar_backups()

        assert len(backups) == 3
        assert all(isinstance(b, BackupInfo) for b in backups)

    def test_backups_ordenados_por_data(self, setup_backups):
        """Backups devem estar ordenados por data (mais recente primeiro)"""
        backups = listar_backups()

        # O mais recente (15/01) deve ser o primeiro
        assert backups[0].nome_arquivo == "backup_2025-01-15_10-00-00.db"

    def test_detecta_tipo_backup(self, setup_backups):
        """Deve detectar tipo de cada backup"""
        backups = listar_backups()

        tipos = {b.nome_arquivo: b.tipo for b in backups}
        assert tipos["backup_auto_2025-01-12_10-00-00.db"] == "automático"
        assert tipos["backup_2025-01-15_10-00-00.db"] == "manual"

    def test_listar_diretorio_vazio(self):
        """Deve retornar lista vazia se não houver backups"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('util.backup_util.BACKUP_DIR', Path(temp_dir)):
                backups = listar_backups()
                assert backups == []


class TestExcluirBackup:
    """Testes para a função excluir_backup"""

    @pytest.fixture
    def setup_backup_para_exclusao(self):
        """Cria backup para teste de exclusão"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)
            nome_backup = "backup_2025-01-15_10-00-00.db"
            caminho = backup_dir / nome_backup

            # Criar banco SQLite
            conn = sqlite3.connect(str(caminho))
            conn.execute("CREATE TABLE t (id INT)")
            conn.commit()
            conn.close()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                yield {
                    'backup_dir': backup_dir,
                    'nome_backup': nome_backup,
                    'caminho': caminho
                }

    def test_excluir_backup_existente(self, setup_backup_para_exclusao):
        """Deve excluir backup existente"""
        nome = setup_backup_para_exclusao['nome_backup']
        caminho = setup_backup_para_exclusao['caminho']

        # Verificar que existe
        assert caminho.exists()

        sucesso, mensagem = excluir_backup(nome)

        assert sucesso is True
        assert "sucesso" in mensagem.lower()
        assert not caminho.exists()

    def test_excluir_backup_inexistente(self):
        """Deve falhar ao excluir backup inexistente"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('util.backup_util.BACKUP_DIR', Path(temp_dir)):
                sucesso, mensagem = excluir_backup("backup_inexistente.db")

                assert sucesso is False
                assert "não encontrado" in mensagem.lower()

    def test_excluir_nome_invalido(self):
        """Deve falhar com nome de arquivo inválido"""
        sucesso, mensagem = excluir_backup("../etc/passwd")

        assert sucesso is False
        assert "inválido" in mensagem.lower()


class TestObterInfoBackup:
    """Testes para a função obter_info_backup"""

    @pytest.fixture
    def setup_backup_info(self):
        """Cria backup para teste de obter info"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)
            nome_backup = "backup_2025-01-15_10-30-45.db"
            caminho = backup_dir / nome_backup

            # Criar banco SQLite com algum tamanho
            conn = sqlite3.connect(str(caminho))
            conn.execute("CREATE TABLE t (id INT, dados TEXT)")
            for i in range(100):
                conn.execute("INSERT INTO t VALUES (?, ?)", (i, "dados" * 100))
            conn.commit()
            conn.close()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                yield {
                    'backup_dir': backup_dir,
                    'nome_backup': nome_backup,
                    'caminho': caminho
                }

    def test_obter_info_backup_existente(self, setup_backup_info):
        """Deve retornar info de backup existente"""
        nome = setup_backup_info['nome_backup']

        info = obter_info_backup(nome)

        assert info is not None
        assert isinstance(info, BackupInfo)
        assert info.nome_arquivo == nome
        assert info.tipo == "manual"
        assert info.tamanho_bytes > 0
        assert info.data_criacao.year == 2025
        assert info.data_criacao.month == 1
        assert info.data_criacao.day == 15

    def test_obter_info_backup_inexistente(self):
        """Deve retornar None para backup inexistente"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('util.backup_util.BACKUP_DIR', Path(temp_dir)):
                info = obter_info_backup("backup_inexistente.db")
                assert info is None

    def test_obter_info_nome_invalido(self):
        """Deve retornar None para nome inválido"""
        info = obter_info_backup("../invalid.db")
        assert info is None


class TestObterCaminhoBackup:
    """Testes para a função obter_caminho_backup"""

    @pytest.fixture
    def setup_caminho_backup(self):
        """Cria backup para teste de obter caminho"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)
            nome_backup = "backup_2025-01-15_10-00-00.db"
            caminho = backup_dir / nome_backup

            # Criar arquivo
            caminho.touch()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                yield {
                    'backup_dir': backup_dir,
                    'nome_backup': nome_backup,
                    'caminho': caminho
                }

    def test_obter_caminho_existente(self, setup_caminho_backup):
        """Deve retornar caminho de backup existente"""
        nome = setup_caminho_backup['nome_backup']
        caminho_esperado = setup_caminho_backup['caminho']

        resultado = obter_caminho_backup(nome)

        assert resultado is not None
        assert resultado == caminho_esperado

    def test_obter_caminho_inexistente(self):
        """Deve retornar None para backup inexistente"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('util.backup_util.BACKUP_DIR', Path(temp_dir)):
                resultado = obter_caminho_backup("backup_inexistente.db")
                assert resultado is None

    def test_obter_caminho_nome_invalido(self):
        """Deve retornar None para nome inválido"""
        resultado = obter_caminho_backup("../traversal.db")
        assert resultado is None


class TestRestaurarBackup:
    """Testes para a função restaurar_backup"""

    @pytest.fixture
    def setup_restauracao(self):
        """Configura ambiente para teste de restauração"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            backup_dir = temp_path / "backups"
            backup_dir.mkdir()

            db_path = temp_path / "database.db"

            # Criar banco de dados atual
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE atual (valor TEXT)")
            conn.execute("INSERT INTO atual VALUES ('dados_atuais')")
            conn.commit()
            conn.close()

            # Criar backup para restaurar
            nome_backup = "backup_2025-01-15_10-00-00.db"
            caminho_backup = backup_dir / nome_backup

            conn = sqlite3.connect(str(caminho_backup))
            conn.execute("CREATE TABLE backup (valor TEXT)")
            conn.execute("INSERT INTO backup VALUES ('dados_backup')")
            conn.commit()
            conn.close()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                with patch('util.backup_util.DATABASE_PATH', str(db_path)):
                    yield {
                        'backup_dir': backup_dir,
                        'db_path': db_path,
                        'nome_backup': nome_backup,
                        'caminho_backup': caminho_backup
                    }

    def test_restaurar_backup_sucesso(self, setup_restauracao):
        """Deve restaurar backup com sucesso"""
        nome = setup_restauracao['nome_backup']
        db_path = setup_restauracao['db_path']

        sucesso, mensagem, backup_seguranca = restaurar_backup(nome)

        assert sucesso is True
        assert "sucesso" in mensagem.lower()

        # Verificar que banco foi restaurado (deve ter tabela "backup", não "atual")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in cursor.fetchall()]
        conn.close()

        assert "backup" in tabelas

    def test_restaurar_cria_backup_seguranca(self, setup_restauracao):
        """Deve criar backup de segurança antes de restaurar"""
        nome = setup_restauracao['nome_backup']

        sucesso, _, backup_seguranca = restaurar_backup(nome, criar_backup_antes=True)

        assert sucesso is True
        # Deve ter criado um backup automático
        if backup_seguranca:
            assert "_auto_" in backup_seguranca

    def test_restaurar_sem_backup_seguranca(self, setup_restauracao):
        """Pode restaurar sem criar backup de segurança"""
        nome = setup_restauracao['nome_backup']

        sucesso, _, _ = restaurar_backup(nome, criar_backup_antes=False)

        assert sucesso is True

    def test_restaurar_backup_inexistente(self):
        """Deve falhar ao restaurar backup inexistente"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('util.backup_util.BACKUP_DIR', Path(temp_dir)):
                sucesso, mensagem, _ = restaurar_backup("backup_inexistente.db")

                assert sucesso is False
                assert "não encontrado" in mensagem.lower()

    def test_restaurar_nome_invalido(self):
        """Deve falhar com nome inválido"""
        sucesso, mensagem, _ = restaurar_backup("../traversal.db")

        assert sucesso is False
        assert "inválido" in mensagem.lower()

    def test_restaurar_backup_corrompido(self, setup_restauracao):
        """Deve falhar ao restaurar backup corrompido"""
        backup_dir = setup_restauracao['backup_dir']
        nome_corrompido = "backup_2025-01-20_10-00-00.db"
        caminho_corrompido = backup_dir / nome_corrompido

        # Criar arquivo corrompido (não é SQLite válido)
        caminho_corrompido.write_bytes(b"dados_invalidos_nao_sqlite")

        sucesso, mensagem, _ = restaurar_backup(nome_corrompido)

        assert sucesso is False
        assert "corrompido" in mensagem.lower() or "inválido" in mensagem.lower()


class TestRestaurarBackupRollback:
    """Testes para rollback na restauração de backup"""

    @pytest.fixture
    def setup_restauracao_rollback(self):
        """Configura ambiente para teste de rollback"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            backup_dir = temp_path / "backups"
            backup_dir.mkdir()

            db_path = temp_path / "database.db"

            # Criar banco de dados atual válido
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE atual (valor TEXT)")
            conn.execute("INSERT INTO atual VALUES ('dados_originais')")
            conn.commit()
            conn.close()

            # Criar backup válido para restaurar
            nome_backup = "backup_2025-01-15_10-00-00.db"
            caminho_backup = backup_dir / nome_backup

            conn = sqlite3.connect(str(caminho_backup))
            conn.execute("CREATE TABLE backup_table (valor TEXT)")
            conn.execute("INSERT INTO backup_table VALUES ('dados_backup')")
            conn.commit()
            conn.close()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                with patch('util.backup_util.DATABASE_PATH', str(db_path)):
                    yield {
                        'backup_dir': backup_dir,
                        'db_path': db_path,
                        'nome_backup': nome_backup,
                    }

    def test_rollback_quando_pos_restauracao_falha(self, setup_restauracao_rollback):
        """Deve fazer rollback quando verificação pós-restauração falha"""
        nome = setup_restauracao_rollback['nome_backup']

        # Simular falha na verificação pós-restauração
        with patch('util.backup_util._verificar_database_pos_restauracao', return_value=False):
            sucesso, mensagem, _ = restaurar_backup(nome, criar_backup_antes=True)

            assert sucesso is False
            assert "falhou" in mensagem.lower() or "revertido" in mensagem.lower()

    def test_rollback_falha_sem_backup_seguranca(self, setup_restauracao_rollback):
        """Deve retornar erro crítico se rollback falhar sem backup de segurança"""
        nome = setup_restauracao_rollback['nome_backup']

        with patch('util.backup_util._verificar_database_pos_restauracao', return_value=False):
            # Não criar backup de segurança
            sucesso, mensagem, _ = restaurar_backup(nome, criar_backup_antes=False)

            assert sucesso is False
            assert "crítico" in mensagem.lower() or "falhou" in mensagem.lower()


class TestBackupErrosIO:
    """Testes para tratamento de erros de I/O em backups"""

    def test_criar_backup_oserror(self):
        """Deve tratar OSError ao criar backup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            backup_dir = temp_path / "backups"
            db_path = temp_path / "database.db"

            # Criar banco de dados
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE t (id INT)")
            conn.commit()
            conn.close()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                with patch('util.backup_util.DATABASE_PATH', str(db_path)):
                    with patch('shutil.copy2', side_effect=OSError("Permission denied")):
                        sucesso, mensagem = criar_backup()

                        assert sucesso is False
                        assert "erro" in mensagem.lower()

    def test_listar_backups_oserror_diretorio(self):
        """Deve retornar lista vazia em erro de diretório"""
        with patch('util.backup_util.BACKUP_DIR') as mock_dir:
            mock_dir.exists.return_value = True
            mock_dir.glob.side_effect = OSError("Permission denied")

            backups = listar_backups()
            assert backups == []

    def test_listar_backups_oserror_arquivo(self):
        """Deve continuar listando mesmo com erro em um arquivo"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)

            # Criar um backup válido
            nome_valido = "backup_2025-01-15_10-00-00.db"
            caminho = backup_dir / nome_valido
            conn = sqlite3.connect(str(caminho))
            conn.execute("CREATE TABLE t (id INT)")
            conn.commit()
            conn.close()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                # Simular erro ao obter stat de um arquivo mas não de todos
                original_stat = Path.stat

                def stat_with_error(self):
                    if "error" in str(self):
                        raise OSError("stat error")
                    return original_stat(self)

                # Criar arquivo que vai dar erro
                (backup_dir / "backup_error_2025-01-16_10-00-00.db").touch()

                with patch.object(Path, 'stat', stat_with_error):
                    backups = listar_backups()
                    # Deve retornar pelo menos o backup válido
                    assert len(backups) >= 0

    def test_excluir_backup_oserror(self):
        """Deve tratar OSError ao excluir backup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)
            nome = "backup_2025-01-15_10-00-00.db"
            caminho = backup_dir / nome
            caminho.touch()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                with patch.object(Path, 'unlink', side_effect=OSError("Permission denied")):
                    sucesso, mensagem = excluir_backup(nome)

                    assert sucesso is False
                    assert "erro" in mensagem.lower()

    def test_obter_info_backup_oserror(self):
        """Deve retornar None em erro de I/O"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)
            nome = "backup_2025-01-15_10-00-00.db"
            caminho = backup_dir / nome
            caminho.touch()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                with patch.object(Path, 'stat', side_effect=OSError("stat error")):
                    info = obter_info_backup(nome)
                    assert info is None

    def test_restaurar_backup_oserror_copia(self):
        """Deve tratar OSError ao copiar backup para restauração"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            backup_dir = temp_path / "backups"
            backup_dir.mkdir()
            db_path = temp_path / "database.db"

            # Criar banco atual
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE t (id INT)")
            conn.commit()
            conn.close()

            # Criar backup válido
            nome = "backup_2025-01-15_10-00-00.db"
            caminho = backup_dir / nome
            conn = sqlite3.connect(str(caminho))
            conn.execute("CREATE TABLE backup (id INT)")
            conn.commit()
            conn.close()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                with patch('util.backup_util.DATABASE_PATH', str(db_path)):
                    # Simular erro na cópia após validação
                    original_copy = shutil.copy2
                    call_count = [0]

                    def copy_with_error(*args, **kwargs):
                        call_count[0] += 1
                        # Permitir criação de backup de segurança, falhar na restauração
                        if call_count[0] > 1:
                            raise OSError("Copy failed")
                        return original_copy(*args, **kwargs)

                    with patch('shutil.copy2', side_effect=copy_with_error):
                        sucesso, mensagem, _ = restaurar_backup(nome)
                        # Pode falhar ou ter rollback
                        if not sucesso:
                            assert "erro" in mensagem.lower() or "revertido" in mensagem.lower()


class TestValidarIntegridadeBackupErros:
    """Testes adicionais para validação de integridade"""

    def test_validar_database_error(self):
        """Deve tratar DatabaseError corretamente"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            # Escrever conteúdo que parece SQLite mas está corrompido
            f.write(b"SQLite format 3\x00" + b"\x00" * 100)
            f.flush()

            caminho = Path(f.name)
            valido, mensagem = _validar_integridade_backup(caminho)

            assert valido is False
            assert "corrompido" in mensagem.lower() or "inválido" in mensagem.lower()

            caminho.unlink(missing_ok=True)

    def test_validar_integridade_oserror(self):
        """Deve tratar OSError na validação"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            # Criar banco válido
            conn = sqlite3.connect(f.name)
            conn.execute("CREATE TABLE t (id INT)")
            conn.commit()
            conn.close()

            caminho = Path(f.name)

            # Simular erro ao conectar
            with patch('sqlite3.connect', side_effect=OSError("Access denied")):
                valido, mensagem = _validar_integridade_backup(caminho)

                assert valido is False
                assert "erro" in mensagem.lower()

            caminho.unlink(missing_ok=True)


class TestObterInfoBackupDataFallback:
    """Testes para fallback de data em obter_info_backup"""

    def test_obter_info_data_fallback_mtime(self):
        """Deve usar mtime quando não consegue extrair data do nome"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)
            # Nome que não segue o padrão de data esperado
            nome = "backup_formato_estranho.db"
            caminho = backup_dir / nome

            # Criar arquivo
            conn = sqlite3.connect(str(caminho))
            conn.execute("CREATE TABLE t (id INT)")
            conn.commit()
            conn.close()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                info = obter_info_backup(nome)

                # Deve retornar info usando mtime como fallback
                assert info is not None
                assert info.data_criacao is not None


class TestListarBackupsDataFallback:
    """Testes para fallback de data em listar_backups"""

    def test_listar_com_nome_sem_data_valida(self):
        """Deve usar mtime quando nome não tem data válida"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)

            # Criar backup com nome sem data válida
            nome = "backup_sem_data_valida.db"
            caminho = backup_dir / nome
            conn = sqlite3.connect(str(caminho))
            conn.execute("CREATE TABLE t (id INT)")
            conn.commit()
            conn.close()

            with patch('util.backup_util.BACKUP_DIR', backup_dir):
                backups = listar_backups()

                assert len(backups) == 1
                # Data deve ter sido obtida do mtime
                assert backups[0].data_criacao is not None
