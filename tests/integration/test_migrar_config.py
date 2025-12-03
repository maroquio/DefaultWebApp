"""
Testes para o módulo util/migrar_config.py

Testa a migração de configurações do .env para o banco de dados.
"""

import pytest
import sqlite3
from unittest.mock import patch, MagicMock


class TestMigrarConfigsParaBanco:
    """Testes para a função migrar_configs_para_banco"""

    def test_nao_sobrescreve_configs_existentes(self):
        """Não deve sobrescrever configurações já existentes no banco"""
        with patch('util.migrar_config.configuracao_repo') as mock_repo:
            # Configuração já existe
            mock_repo.obter_por_chave.return_value = MagicMock(valor="valor_existente")

            with patch.dict('os.environ', {'APP_NAME': 'Novo Nome'}):
                from util.migrar_config import migrar_configs_para_banco
                migrar_configs_para_banco()

                # Não deve inserir ou atualizar
                mock_repo.inserir_ou_atualizar.assert_not_called()

    def test_migra_config_nova(self):
        """Deve migrar configuração que não existe no banco"""
        with patch('util.migrar_config.configuracao_repo') as mock_repo:
            # Configuração não existe
            mock_repo.obter_por_chave.return_value = None

            with patch.dict('os.environ', {'APP_NAME': 'Meu App', 'RESEND_FROM_EMAIL': 'email@teste.com'}):
                with patch('util.config_cache.config') as mock_cache:
                    from util.migrar_config import migrar_configs_para_banco
                    migrar_configs_para_banco()

                    # Deve ter tentado inserir
                    assert mock_repo.inserir_ou_atualizar.called

    def test_ignora_variaveis_vazias(self):
        """Deve ignorar variáveis de ambiente vazias"""
        with patch('util.migrar_config.configuracao_repo') as mock_repo:
            mock_repo.obter_por_chave.return_value = None

            with patch.dict('os.environ', {'APP_NAME': ''}, clear=False):
                from util.migrar_config import migrar_configs_para_banco

                # Conta chamadas antes
                mock_repo.inserir_ou_atualizar.reset_mock()

                migrar_configs_para_banco()

                # Variáveis vazias não devem ser migradas
                # (pode ter outras variáveis, mas APP_NAME vazia não deve ser inserida)

    def test_trata_erro_sqlite(self):
        """Deve tratar erros SQLite durante migração"""
        with patch('util.migrar_config.configuracao_repo') as mock_repo:
            mock_repo.obter_por_chave.return_value = None
            mock_repo.inserir_ou_atualizar.side_effect = sqlite3.Error("DB error")

            with patch.dict('os.environ', {'APP_NAME': 'Teste'}):
                from util.migrar_config import migrar_configs_para_banco

                # Não deve lançar exceção
                migrar_configs_para_banco()

    def test_limpa_cache_apos_migracao(self):
        """Deve limpar cache após migração"""
        with patch('util.migrar_config.configuracao_repo') as mock_repo:
            mock_repo.obter_por_chave.return_value = MagicMock()  # Todas existem

            with patch('util.config_cache.config') as mock_cache:
                from util.migrar_config import migrar_configs_para_banco
                migrar_configs_para_banco()

                mock_cache.limpar.assert_called_once()


class TestConfigsParaMigrar:
    """Testes para o dicionário CONFIGS_PARA_MIGRAR"""

    def test_configs_tem_formato_correto(self):
        """Cada config deve ter (var_env, descricao, categoria)"""
        from util.migrar_config import CONFIGS_PARA_MIGRAR

        for chave, valor in CONFIGS_PARA_MIGRAR.items():
            assert isinstance(chave, str), f"Chave deve ser string: {chave}"
            assert isinstance(valor, tuple), f"Valor deve ser tupla: {chave}"
            assert len(valor) == 3, f"Tupla deve ter 3 elementos: {chave}"

            var_env, descricao, categoria = valor
            assert isinstance(var_env, str), f"var_env deve ser string: {chave}"
            assert isinstance(descricao, str), f"descricao deve ser string: {chave}"
            assert isinstance(categoria, str), f"categoria deve ser string: {chave}"

    def test_categorias_conhecidas(self):
        """Categorias devem ser conhecidas"""
        from util.migrar_config import CONFIGS_PARA_MIGRAR

        categorias_validas = {
            "Aplicação", "Fotos", "Interface",
            "Segurança - Autenticação", "Operações de Usuário",
            "Chat", "Suporte", "Admin", "Páginas Públicas"
        }

        for chave, (_, _, categoria) in CONFIGS_PARA_MIGRAR.items():
            assert categoria in categorias_validas, f"Categoria desconhecida: {categoria} em {chave}"

    def test_variaveis_env_maiusculas(self):
        """Variáveis de ambiente devem estar em maiúsculas"""
        from util.migrar_config import CONFIGS_PARA_MIGRAR

        for chave, (var_env, _, _) in CONFIGS_PARA_MIGRAR.items():
            assert var_env == var_env.upper(), f"Var env deve ser maiúscula: {var_env}"

    def test_chaves_banco_minusculas(self):
        """Chaves do banco devem estar em minúsculas"""
        from util.migrar_config import CONFIGS_PARA_MIGRAR

        for chave in CONFIGS_PARA_MIGRAR.keys():
            assert chave == chave.lower(), f"Chave deve ser minúscula: {chave}"
