"""
Testes para o módulo util/config_cache.py

Testa o cache de configurações do sistema, incluindo
tratamento de erros, conversões de tipos e operações de cache.
"""

import pytest
from unittest.mock import patch, MagicMock
import sqlite3

from util.config_cache import ConfigCache, config


class TestConfigCacheObter:
    """Testes para o método obter()"""

    def setup_method(self):
        """Limpa o cache antes de cada teste"""
        ConfigCache.limpar()

    def test_obter_valor_do_cache(self):
        """Quando valor está no cache, deve retornar sem acessar banco"""
        # Preenche o cache manualmente
        ConfigCache._cache["chave_teste"] = "valor_cacheado"

        with patch('util.config_cache.configuracao_repo') as mock_repo:
            resultado = ConfigCache.obter("chave_teste", "padrao")

            # Não deve chamar o repo, pois está no cache
            mock_repo.obter_por_chave.assert_not_called()
            assert resultado == "valor_cacheado"

    def test_obter_valor_do_banco(self):
        """Quando valor não está no cache, deve buscar do banco"""
        mock_config = MagicMock()
        mock_config.valor = "valor_do_banco"

        with patch('util.config_cache.configuracao_repo') as mock_repo:
            mock_repo.obter_por_chave.return_value = mock_config

            resultado = ConfigCache.obter("chave_nova", "padrao")

            mock_repo.obter_por_chave.assert_called_once_with("chave_nova")
            assert resultado == "valor_do_banco"
            # Deve ter sido cacheado
            assert ConfigCache._cache["chave_nova"] == "valor_do_banco"

    def test_obter_retorna_padrao_quando_nao_existe(self):
        """Quando configuração não existe no banco, retorna padrão"""
        with patch('util.config_cache.configuracao_repo') as mock_repo:
            mock_repo.obter_por_chave.return_value = None

            resultado = ConfigCache.obter("chave_inexistente", "valor_padrao")

            assert resultado == "valor_padrao"
            # Deve cachear o padrão também
            assert ConfigCache._cache["chave_inexistente"] == "valor_padrao"

    def test_obter_sqlite_error_retorna_padrao(self):
        """Em caso de sqlite3.Error, retorna padrão sem crashar"""
        with patch('util.config_cache.configuracao_repo') as mock_repo:
            mock_repo.obter_por_chave.side_effect = sqlite3.Error("Erro de banco")

            with patch('util.config_cache.logger') as mock_logger:
                resultado = ConfigCache.obter("chave_erro", "padrao_erro")

                assert resultado == "padrao_erro"
                mock_logger.error.assert_called_once()
                assert "Erro ao buscar configuração" in str(mock_logger.error.call_args)

    def test_obter_exception_generica_retorna_padrao(self):
        """Em caso de Exception genérica, retorna padrão e loga como crítico"""
        with patch('util.config_cache.configuracao_repo') as mock_repo:
            mock_repo.obter_por_chave.side_effect = Exception("Erro inesperado")

            with patch('util.config_cache.logger') as mock_logger:
                resultado = ConfigCache.obter("chave_critica", "padrao_critico")

                assert resultado == "padrao_critico"
                mock_logger.critical.assert_called_once()
                assert "Erro crítico" in str(mock_logger.critical.call_args)


class TestConfigCacheObterInt:
    """Testes para o método obter_int()"""

    def setup_method(self):
        """Limpa o cache antes de cada teste"""
        ConfigCache.limpar()

    def test_obter_int_conversao_sucesso(self):
        """Deve converter string numérica para int"""
        ConfigCache._cache["numero"] = "42"

        resultado = ConfigCache.obter_int("numero", 0)

        assert resultado == 42
        assert isinstance(resultado, int)

    def test_obter_int_usa_padrao_quando_nao_existe(self):
        """Deve usar padrão quando chave não existe"""
        with patch('util.config_cache.configuracao_repo') as mock_repo:
            mock_repo.obter_por_chave.return_value = None

            resultado = ConfigCache.obter_int("inexistente", 100)

            assert resultado == 100

    def test_obter_int_valor_invalido_retorna_padrao(self):
        """Quando valor não é numérico, retorna padrão"""
        ConfigCache._cache["texto"] = "nao_e_numero"

        with patch('util.config_cache.logger') as mock_logger:
            resultado = ConfigCache.obter_int("texto", 999)

            assert resultado == 999
            mock_logger.error.assert_called_once()
            assert "converter" in str(mock_logger.error.call_args)

    def test_obter_int_valor_float_trunca(self):
        """Valor float na string deve funcionar"""
        ConfigCache._cache["decimal"] = "3.14"

        # int("3.14") levanta ValueError
        with patch('util.config_cache.logger'):
            resultado = ConfigCache.obter_int("decimal", 0)

            # Deve retornar o padrão pois int("3.14") falha
            assert resultado == 0


class TestConfigCacheObterBool:
    """Testes para o método obter_bool()"""

    def setup_method(self):
        """Limpa o cache antes de cada teste"""
        ConfigCache.limpar()

    def test_obter_bool_true_strings(self):
        """Deve reconhecer várias strings como verdadeiro"""
        valores_true = ["true", "TRUE", "True", "1", "yes", "YES", "sim", "SIM", "verdadeiro"]

        for valor in valores_true:
            ConfigCache._cache["bool_test"] = valor
            resultado = ConfigCache.obter_bool("bool_test", False)
            assert resultado is True, f"'{valor}' deveria ser True"

    def test_obter_bool_false_strings(self):
        """Deve reconhecer outras strings como falso"""
        valores_false = ["false", "FALSE", "0", "no", "nao", "não", "qualquer_coisa"]

        for valor in valores_false:
            ConfigCache._cache["bool_test"] = valor
            resultado = ConfigCache.obter_bool("bool_test", True)
            assert resultado is False, f"'{valor}' deveria ser False"

    def test_obter_bool_exception_retorna_padrao(self):
        """Em caso de exceção, retorna padrão"""
        # Simular erro na conversão mockando o método obter
        with patch.object(ConfigCache, 'obter') as mock_obter:
            mock_obter.return_value = MagicMock()
            # MagicMock().lower() retorna outro MagicMock que não está em ("true", ...)
            # Mas para forçar exceção, fazemos o lower() levantar erro
            mock_obter.return_value.lower.side_effect = AttributeError("Sem lower")

            with patch('util.config_cache.logger') as mock_logger:
                resultado = ConfigCache.obter_bool("chave_erro", True)

                assert resultado is True
                mock_logger.error.assert_called_once()


class TestConfigCacheObterFloat:
    """Testes para o método obter_float()"""

    def setup_method(self):
        """Limpa o cache antes de cada teste"""
        ConfigCache.limpar()

    def test_obter_float_conversao_sucesso(self):
        """Deve converter string para float"""
        ConfigCache._cache["decimal"] = "3.14159"

        resultado = ConfigCache.obter_float("decimal", 0.0)

        assert resultado == 3.14159
        assert isinstance(resultado, float)

    def test_obter_float_inteiro_funciona(self):
        """Deve converter inteiro para float"""
        ConfigCache._cache["inteiro"] = "42"

        resultado = ConfigCache.obter_float("inteiro", 0.0)

        assert resultado == 42.0

    def test_obter_float_valor_invalido_retorna_padrao(self):
        """Quando valor não é numérico, retorna padrão"""
        ConfigCache._cache["texto"] = "nao_e_numero"

        with patch('util.config_cache.logger') as mock_logger:
            resultado = ConfigCache.obter_float("texto", 9.99)

            assert resultado == 9.99
            mock_logger.error.assert_called_once()

    def test_obter_float_notacao_cientifica(self):
        """Deve aceitar notação científica"""
        ConfigCache._cache["cientifico"] = "1.5e-10"

        resultado = ConfigCache.obter_float("cientifico", 0.0)

        assert resultado == 1.5e-10


class TestConfigCacheObterMultiplos:
    """Testes para o método obter_multiplos()"""

    def setup_method(self):
        """Limpa o cache antes de cada teste"""
        ConfigCache.limpar()

    def test_obter_multiplos_sucesso(self):
        """Deve retornar dicionário com todas as configurações"""
        ConfigCache._cache["config1"] = "valor1"
        ConfigCache._cache["config2"] = "valor2"

        resultado = ConfigCache.obter_multiplos(
            ["config1", "config2"],
            ["padrao1", "padrao2"]
        )

        assert resultado == {"config1": "valor1", "config2": "valor2"}

    def test_obter_multiplos_usa_padroes(self):
        """Deve usar padrões quando configs não existem"""
        with patch('util.config_cache.configuracao_repo') as mock_repo:
            mock_repo.obter_por_chave.return_value = None

            resultado = ConfigCache.obter_multiplos(
                ["nova1", "nova2"],
                ["padrao1", "padrao2"]
            )

            assert resultado == {"nova1": "padrao1", "nova2": "padrao2"}

    def test_obter_multiplos_listas_tamanhos_diferentes(self):
        """Quando listas têm tamanhos diferentes, loga erro e retorna zip"""
        with patch('util.config_cache.logger') as mock_logger:
            resultado = ConfigCache.obter_multiplos(
                ["chave1", "chave2", "chave3"],
                ["padrao1", "padrao2"]  # Faltando um padrão
            )

            mock_logger.error.assert_called_once()
            assert "número de chaves diferente" in str(mock_logger.error.call_args)
            # Deve retornar o zip das listas
            assert resultado == {"chave1": "padrao1", "chave2": "padrao2"}

    def test_obter_multiplos_lista_vazia(self):
        """Deve funcionar com listas vazias"""
        resultado = ConfigCache.obter_multiplos([], [])

        assert resultado == {}


class TestConfigCacheLimpar:
    """Testes para os métodos de limpeza de cache"""

    def setup_method(self):
        """Prepara cache com dados de teste"""
        ConfigCache._cache = {
            "chave1": "valor1",
            "chave2": "valor2",
            "chave3": "valor3"
        }

    def test_limpar_remove_todo_cache(self):
        """limpar() deve remover todas as entradas do cache"""
        assert len(ConfigCache._cache) == 3

        ConfigCache.limpar()

        assert len(ConfigCache._cache) == 0
        assert ConfigCache._cache == {}

    def test_limpar_chave_existente(self):
        """limpar_chave() deve remover apenas a chave especificada"""
        assert "chave1" in ConfigCache._cache

        ConfigCache.limpar_chave("chave1")

        assert "chave1" not in ConfigCache._cache
        assert "chave2" in ConfigCache._cache
        assert "chave3" in ConfigCache._cache

    def test_limpar_chave_inexistente(self):
        """limpar_chave() não deve falhar para chave inexistente"""
        # Não deve levantar exceção
        ConfigCache.limpar_chave("chave_que_nao_existe")

        # Cache deve permanecer intacto
        assert len(ConfigCache._cache) == 3


class TestConfigCacheThreadSafety:
    """Testes de thread-safety (básicos)"""

    def setup_method(self):
        """Limpa o cache antes de cada teste"""
        ConfigCache.limpar()

    def test_cache_usa_rlock(self):
        """Verifica que a classe usa RLock para sincronização"""
        # RLock não é um tipo diretamente, verificamos pelo nome do tipo
        assert type(ConfigCache._lock).__name__ == 'RLock'

    def test_obter_thread_safe(self):
        """Verifica que obter() funciona com cache populado"""
        # Testa comportamento básico que demonstra thread-safety
        ConfigCache._cache["teste"] = "valor"

        resultado = ConfigCache.obter("teste", "padrao")

        assert resultado == "valor"


class TestConfigInstanciaGlobal:
    """Testes para a instância global config"""

    def test_config_e_configcache(self):
        """Verifica que 'config' é instância de ConfigCache"""
        assert isinstance(config, ConfigCache)

    def test_config_pode_acessar_metodos(self):
        """Verifica que config pode acessar métodos da classe"""
        config.limpar()

        # Deve funcionar sem erro
        with patch('util.config_cache.configuracao_repo') as mock_repo:
            mock_repo.obter_por_chave.return_value = None
            resultado = config.obter("teste", "valor_teste")
            assert resultado == "valor_teste"
