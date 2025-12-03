"""
Testes para as funções híbridas de configuração em util/config.py

Testa obter_config_str, obter_config_int, obter_config_bool
"""

import pytest
from unittest.mock import patch, MagicMock


class TestObterConfigStr:
    """Testes para obter_config_str"""

    def test_retorna_valor_do_banco(self):
        """Deve retornar valor do banco quando existe"""
        from util.config import obter_config_str

        with patch('util.config_cache.config') as mock_config:
            mock_config.obter.return_value = "valor_banco"

            resultado = obter_config_str("chave", "padrao_env")

            assert resultado == "valor_banco"

    def test_retorna_padrao_env_quando_banco_vazio(self):
        """Deve retornar padrão do .env quando banco retorna vazio"""
        from util.config import obter_config_str

        with patch('util.config_cache.config') as mock_config:
            mock_config.obter.return_value = ""

            resultado = obter_config_str("chave", "padrao_env")

            assert resultado == "padrao_env"

    def test_retorna_padrao_env_quando_banco_none(self):
        """Deve retornar padrão do .env quando banco retorna None"""
        from util.config import obter_config_str

        with patch('util.config_cache.config') as mock_config:
            mock_config.obter.return_value = None

            resultado = obter_config_str("chave", "padrao_env")

            assert resultado == "padrao_env"


class TestObterConfigInt:
    """Testes para obter_config_int"""

    def test_retorna_valor_int_do_banco(self):
        """Deve retornar valor inteiro do banco quando existe"""
        from util.config import obter_config_int

        with patch('util.config_cache.config') as mock_config:
            mock_config.obter.return_value = "42"

            resultado = obter_config_int("chave", 10)

            assert resultado == 42

    def test_retorna_padrao_quando_banco_vazio(self):
        """Deve retornar padrão quando banco retorna vazio"""
        from util.config import obter_config_int

        with patch('util.config_cache.config') as mock_config:
            mock_config.obter.return_value = ""

            resultado = obter_config_int("chave", 99)

            assert resultado == 99

    def test_retorna_padrao_quando_valor_invalido(self):
        """Deve retornar padrão quando valor não é conversível para int"""
        from util.config import obter_config_int

        with patch('util.config_cache.config') as mock_config:
            mock_config.obter.return_value = "nao_e_numero"

            resultado = obter_config_int("chave", 50)

            assert resultado == 50

    def test_retorna_padrao_quando_banco_none(self):
        """Deve retornar padrão quando banco retorna None"""
        from util.config import obter_config_int

        with patch('util.config_cache.config') as mock_config:
            mock_config.obter.return_value = None

            resultado = obter_config_int("chave", 25)

            assert resultado == 25


class TestObterConfigBool:
    """Testes para obter_config_bool"""

    def test_retorna_true_para_valores_verdadeiros(self):
        """Deve retornar True para valores reconhecidos como verdadeiros"""
        from util.config import obter_config_bool

        valores_true = ["true", "True", "TRUE", "1", "yes", "Yes", "sim", "Sim", "verdadeiro"]

        for valor in valores_true:
            with patch('util.config_cache.config') as mock_config:
                mock_config.obter.return_value = valor

                resultado = obter_config_bool("chave", False)

                assert resultado is True, f"Falhou para valor: {valor}"

    def test_retorna_false_para_valores_falsos(self):
        """Deve retornar False para valores não reconhecidos como verdadeiros"""
        from util.config import obter_config_bool

        valores_false = ["false", "False", "0", "no", "nao", "qualquer_coisa"]

        for valor in valores_false:
            with patch('util.config_cache.config') as mock_config:
                mock_config.obter.return_value = valor

                resultado = obter_config_bool("chave", True)

                assert resultado is False, f"Falhou para valor: {valor}"

    def test_retorna_padrao_quando_banco_vazio(self):
        """Deve retornar padrão quando banco retorna vazio"""
        from util.config import obter_config_bool

        with patch('util.config_cache.config') as mock_config:
            mock_config.obter.return_value = ""

            resultado_true = obter_config_bool("chave", True)
            assert resultado_true is True

        with patch('util.config_cache.config') as mock_config:
            mock_config.obter.return_value = ""

            resultado_false = obter_config_bool("chave", False)
            assert resultado_false is False

    def test_retorna_padrao_quando_banco_none(self):
        """Deve retornar padrão quando banco retorna None"""
        from util.config import obter_config_bool

        with patch('util.config_cache.config') as mock_config:
            mock_config.obter.return_value = None

            resultado = obter_config_bool("chave", True)

            assert resultado is True


class TestConstantesConfig:
    """Testes para as constantes de configuração"""

    def test_constantes_existem(self):
        """Constantes de configuração devem existir"""
        from util import config

        assert hasattr(config, 'APP_NAME')
        assert hasattr(config, 'SECRET_KEY')
        assert hasattr(config, 'DATABASE_PATH')
        assert hasattr(config, 'HOST')
        assert hasattr(config, 'PORT')
        assert hasattr(config, 'IS_DEVELOPMENT')

    def test_port_e_inteiro(self):
        """PORT deve ser inteiro"""
        from util.config import PORT

        assert isinstance(PORT, int)

    def test_is_development_e_booleano(self):
        """IS_DEVELOPMENT deve ser booleano"""
        from util.config import IS_DEVELOPMENT

        assert isinstance(IS_DEVELOPMENT, bool)
