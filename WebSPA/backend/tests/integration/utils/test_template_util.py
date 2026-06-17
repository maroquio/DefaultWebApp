"""
Testes para o módulo util/template_util.py

Testa filtros de formatação de data e funções de template.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from util.template_util import (
    formatar_data_br,
    formatar_data,
    formatar_data_hora,
    formatar_data_as_hora,
    formatar_hora,
    foto_usuario,
    csrf_input,
    criar_templates
)


class TestFormatarDataBr:
    """Testes para a função formatar_data_br()"""

    def test_data_none_retorna_vazio(self):
        """Data None deve retornar string vazia"""
        resultado = formatar_data_br(None)
        assert resultado == ""

    def test_data_string_vazia_retorna_vazio(self):
        """String vazia deve retornar string vazia"""
        resultado = formatar_data_br("")
        assert resultado == ""

    def test_datetime_sem_hora(self):
        """Datetime deve formatar para DD/MM/YYYY"""
        data = datetime(2025, 1, 15, 10, 30, 45)
        resultado = formatar_data_br(data, com_hora=False)
        assert resultado == "15/01/2025"

    def test_datetime_com_hora(self):
        """Datetime com hora deve formatar para DD/MM/YYYY HH:MM:SS"""
        data = datetime(2025, 1, 15, 10, 30, 45)
        resultado = formatar_data_br(data, com_hora=True)
        assert resultado == "15/01/2025 10:30:45"

    def test_string_iso_sem_hora(self):
        """String ISO deve formatar para DD/MM/YYYY"""
        resultado = formatar_data_br("2025-01-15", com_hora=False)
        assert resultado == "15/01/2025"

    def test_string_iso_completa(self):
        """String ISO completa deve formatar com hora"""
        resultado = formatar_data_br("2025-01-15 10:30:45", com_hora=True)
        assert resultado == "15/01/2025 10:30:45"

    def test_string_iso_completa_sem_hora(self):
        """String ISO completa sem hora deve formatar apenas data"""
        resultado = formatar_data_br("2025-01-15 10:30:45", com_hora=False)
        assert resultado == "15/01/2025"

    def test_string_invalida_retorna_string_original(self):
        """String inválida deve retornar a string original"""
        resultado = formatar_data_br("data invalida")
        assert resultado == "data invalida"

    def test_string_vazia_com_espacos(self):
        """String só com espaços deve retornar string vazia"""
        resultado = formatar_data_br("   ")
        # Vai tentar parsear e falhar, retornando a string original
        assert resultado == ""


class TestFormatarData:
    """Testes para a função formatar_data()"""

    def test_data_none_retorna_vazio(self):
        """Data None deve retornar string vazia"""
        resultado = formatar_data(None)
        assert resultado == ""

    def test_datetime_formata_corretamente(self):
        """Datetime deve formatar para DD/MM/YYYY"""
        data = datetime(2025, 3, 20)
        resultado = formatar_data(data)
        assert resultado == "20/03/2025"

    def test_nao_datetime_retorna_vazio(self):
        """Tipo não datetime deve retornar string vazia"""
        resultado = formatar_data("2025-01-01")  # type: ignore
        assert resultado == ""


class TestFormatarDataHora:
    """Testes para a função formatar_data_hora()"""

    def test_data_none_retorna_vazio(self):
        """Data None deve retornar string vazia"""
        resultado = formatar_data_hora(None)
        assert resultado == ""

    def test_datetime_formata_corretamente(self):
        """Datetime deve formatar para DD/MM/YYYY HH:MM"""
        data = datetime(2025, 3, 20, 14, 30, 45)
        resultado = formatar_data_hora(data)
        assert resultado == "20/03/2025 14:30"

    def test_nao_datetime_retorna_vazio(self):
        """Tipo não datetime deve retornar string vazia"""
        resultado = formatar_data_hora("2025-01-01")  # type: ignore
        assert resultado == ""


class TestFormatarDataAsHora:
    """Testes para a função formatar_data_as_hora()"""

    def test_data_none_retorna_vazio(self):
        """Data None deve retornar string vazia"""
        resultado = formatar_data_as_hora(None)
        assert resultado == ""

    def test_datetime_formata_corretamente(self):
        """Datetime deve formatar para DD/MM/YYYY às HH:MM"""
        data = datetime(2025, 3, 20, 14, 30)
        resultado = formatar_data_as_hora(data)
        assert resultado == "20/03/2025 às 14:30"

    def test_nao_datetime_retorna_vazio(self):
        """Tipo não datetime deve retornar string vazia"""
        resultado = formatar_data_as_hora("2025-01-01")  # type: ignore
        assert resultado == ""


class TestFormatarHora:
    """Testes para a função formatar_hora()"""

    def test_data_none_retorna_vazio(self):
        """Data None deve retornar string vazia"""
        resultado = formatar_hora(None)
        assert resultado == ""

    def test_datetime_formata_corretamente(self):
        """Datetime deve formatar para HH:MM"""
        data = datetime(2025, 3, 20, 14, 30, 45)
        resultado = formatar_hora(data)
        assert resultado == "14:30"

    def test_nao_datetime_retorna_vazio(self):
        """Tipo não datetime deve retornar string vazia"""
        resultado = formatar_hora("14:30")  # type: ignore
        assert resultado == ""


class TestFotoUsuario:
    """Testes para a função foto_usuario()"""

    def test_id_1_formata_corretamente(self):
        """ID 1 deve formatar para 000001.jpg"""
        resultado = foto_usuario(1)
        assert resultado == "/static/img/usuarios/000001.jpg"

    def test_id_grande_formata_corretamente(self):
        """ID grande deve formatar com zeros à esquerda"""
        resultado = foto_usuario(12345)
        assert resultado == "/static/img/usuarios/012345.jpg"

    def test_id_com_6_digitos(self):
        """ID com 6 dígitos deve formatar sem zeros extras"""
        resultado = foto_usuario(999999)
        assert resultado == "/static/img/usuarios/999999.jpg"


class TestCsrfInput:
    """Testes para a função csrf_input()"""

    def test_sem_request_retorna_input_vazio(self):
        """Sem request deve retornar input com value vazio"""
        resultado = csrf_input(None)
        assert 'type="hidden"' in resultado
        assert 'value=""' in resultado

    def test_com_request_retorna_token(self):
        """Com request deve retornar input com token"""
        mock_request = MagicMock()
        mock_request.session = {"csrf_token": "token123"}

        with patch('util.template_util.obter_token_csrf', return_value="token123"):
            resultado = csrf_input(mock_request)

            assert 'type="hidden"' in resultado
            assert 'value="token123"' in resultado


class TestCriarTemplates:
    """Testes para a função criar_templates()"""

    def test_templates_retorna_jinja2templates(self):
        """Deve retornar instância de Jinja2Templates"""
        from fastapi.templating import Jinja2Templates

        templates = criar_templates()

        assert isinstance(templates, Jinja2Templates)

    def test_templates_tem_filtros_customizados(self):
        """Templates deve ter filtros customizados registrados"""
        templates = criar_templates()

        assert 'data_br' in templates.env.filters
        assert 'foto_usuario' in templates.env.filters
        assert 'formatar_data' in templates.env.filters
        assert 'formatar_data_hora' in templates.env.filters
        assert 'formatar_data_as_hora' in templates.env.filters
        assert 'formatar_hora' in templates.env.filters

    def test_templates_tem_globals(self):
        """Templates deve ter variáveis globais registradas"""
        templates = criar_templates()

        assert 'obter_mensagens' in templates.env.globals
        assert 'APP_NAME' in templates.env.globals
        assert 'VERSION' in templates.env.globals
        assert 'csrf_input' in templates.env.globals
        assert 'TOAST_AUTO_HIDE_DELAY_MS' in templates.env.globals
