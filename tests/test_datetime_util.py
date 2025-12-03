"""
Testes para o módulo util/datetime_util.py

Testa funções de manipulação de datetime com timezone.
"""

import pytest
from datetime import datetime, date
from zoneinfo import ZoneInfo

from util.datetime_util import (
    agora,
    hoje,
    converter_para_timezone,
    datetime_para_string_iso,
    string_iso_para_datetime
)
from util.config import APP_TIMEZONE


class TestAgora:
    """Testes para a função agora()"""

    def test_retorna_datetime(self):
        """Deve retornar objeto datetime"""
        resultado = agora()
        assert isinstance(resultado, datetime)

    def test_datetime_com_timezone(self):
        """Datetime deve ter timezone configurado"""
        resultado = agora()
        assert resultado.tzinfo is not None
        assert resultado.tzinfo == APP_TIMEZONE

    def test_datetime_proximo_ao_atual(self):
        """Datetime deve ser próximo ao momento atual"""
        antes = datetime.now(APP_TIMEZONE)
        resultado = agora()
        depois = datetime.now(APP_TIMEZONE)

        assert antes <= resultado <= depois


class TestHoje:
    """Testes para a função hoje()"""

    def test_retorna_date(self):
        """Deve retornar objeto date"""
        resultado = hoje()
        assert isinstance(resultado, date)

    def test_date_igual_a_hoje(self):
        """Date deve ser igual à data atual no timezone configurado"""
        resultado = hoje()
        esperado = datetime.now(APP_TIMEZONE).date()

        assert resultado == esperado


class TestConverterParaTimezone:
    """Testes para a função converter_para_timezone()"""

    def test_conversao_de_utc_para_app_timezone(self):
        """Deve converter de UTC para timezone da aplicação"""
        dt_utc = datetime(2024, 1, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        resultado = converter_para_timezone(dt_utc)

        assert resultado.tzinfo == APP_TIMEZONE
        # America/Sao_Paulo é UTC-3
        assert resultado.hour == 9  # 12 - 3 = 9

    def test_conversao_com_timezone_customizado(self):
        """Deve converter para timezone customizado"""
        dt_utc = datetime(2024, 1, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        tz_tokyo = ZoneInfo("Asia/Tokyo")

        resultado = converter_para_timezone(dt_utc, tz_tokyo)

        assert resultado.tzinfo == tz_tokyo
        # Tokyo é UTC+9
        assert resultado.hour == 21  # 12 + 9 = 21

    def test_datetime_naive_assume_utc(self):
        """Datetime naive (sem timezone) deve assumir UTC"""
        dt_naive = datetime(2024, 1, 15, 12, 0, 0)  # Sem timezone

        resultado = converter_para_timezone(dt_naive)

        # Deve ter sido interpretado como UTC e convertido para APP_TIMEZONE
        assert resultado.tzinfo == APP_TIMEZONE

    def test_conversao_entre_timezones(self):
        """Deve converter corretamente entre timezones diferentes"""
        tz_ny = ZoneInfo("America/New_York")
        dt_ny = datetime(2024, 6, 15, 12, 0, 0, tzinfo=tz_ny)  # Meio-dia em NY

        tz_la = ZoneInfo("America/Los_Angeles")
        resultado = converter_para_timezone(dt_ny, tz_la)

        # NY é 3 horas à frente de LA no horário de verão
        assert resultado.hour == 9  # 12 - 3 = 9

    def test_preserva_microseconds(self):
        """Deve preservar microsegundos na conversão"""
        dt_utc = datetime(2024, 1, 15, 12, 30, 45, 123456, tzinfo=ZoneInfo("UTC"))

        resultado = converter_para_timezone(dt_utc)

        assert resultado.microsecond == 123456


class TestDatetimeParaStringIso:
    """Testes para a função datetime_para_string_iso()"""

    def test_formato_iso_com_timezone(self):
        """Deve retornar string no formato ISO 8601 com timezone"""
        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=ZoneInfo("America/Sao_Paulo"))

        resultado = datetime_para_string_iso(dt)

        assert "2024-01-15" in resultado
        assert "10:30:45" in resultado
        assert "-03:00" in resultado  # Offset de São Paulo

    def test_formato_iso_utc(self):
        """Deve funcionar com timezone UTC"""
        dt = datetime(2024, 6, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))

        resultado = datetime_para_string_iso(dt)

        assert "2024-06-15" in resultado
        assert "12:00:00" in resultado
        assert "+00:00" in resultado

    def test_formato_iso_com_microseconds(self):
        """Deve incluir microsegundos se presentes"""
        dt = datetime(2024, 1, 15, 10, 30, 45, 123456, tzinfo=ZoneInfo("UTC"))

        resultado = datetime_para_string_iso(dt)

        assert ".123456" in resultado


class TestStringIsoParaDatetime:
    """Testes para a função string_iso_para_datetime()"""

    def test_parse_string_iso_com_timezone(self):
        """Deve parsear string ISO com timezone"""
        iso_string = "2024-01-15T10:30:45-03:00"

        resultado = string_iso_para_datetime(iso_string)

        assert isinstance(resultado, datetime)
        assert resultado.year == 2024
        assert resultado.month == 1
        assert resultado.day == 15
        assert resultado.hour == 10
        assert resultado.minute == 30
        assert resultado.second == 45

    def test_parse_string_iso_utc(self):
        """Deve parsear string ISO em UTC"""
        iso_string = "2024-06-15T12:00:00+00:00"

        resultado = string_iso_para_datetime(iso_string)

        assert resultado.tzinfo is not None
        assert resultado.hour == 12

    def test_parse_string_iso_com_microseconds(self):
        """Deve parsear string ISO com microsegundos"""
        iso_string = "2024-01-15T10:30:45.123456+00:00"

        resultado = string_iso_para_datetime(iso_string)

        assert resultado.microsecond == 123456

    def test_parse_string_iso_formato_z(self):
        """Deve parsear string ISO com Z para UTC"""
        iso_string = "2024-01-15T10:30:45+00:00"

        resultado = string_iso_para_datetime(iso_string)

        assert resultado.tzinfo is not None

    def test_roundtrip_conversao(self):
        """Conversão para string e de volta deve preservar valores"""
        original = datetime(2024, 3, 15, 14, 30, 0, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))

        iso_string = datetime_para_string_iso(original)
        resultado = string_iso_para_datetime(iso_string)

        assert resultado.year == original.year
        assert resultado.month == original.month
        assert resultado.day == original.day
        assert resultado.hour == original.hour
        assert resultado.minute == original.minute
        assert resultado.second == original.second


class TestIntegracaoTimezone:
    """Testes de integração entre as funções de datetime"""

    def test_agora_para_iso_e_de_volta(self):
        """Fluxo completo: agora() -> ISO -> datetime"""
        momento = agora()
        iso_string = datetime_para_string_iso(momento)
        restaurado = string_iso_para_datetime(iso_string)

        assert restaurado.year == momento.year
        assert restaurado.month == momento.month
        assert restaurado.day == momento.day
        assert restaurado.hour == momento.hour
        assert restaurado.minute == momento.minute
        assert restaurado.second == momento.second

    def test_conversao_de_timezone_preserva_instante(self):
        """Conversão de timezone deve preservar o mesmo instante no tempo"""
        momento_sp = agora()
        momento_utc = converter_para_timezone(momento_sp, ZoneInfo("UTC"))

        # Converter de volta para SP
        momento_sp_novamente = converter_para_timezone(momento_utc, APP_TIMEZONE)

        # Devem representar o mesmo instante
        assert momento_sp.timestamp() == momento_utc.timestamp()
        assert momento_sp.timestamp() == momento_sp_novamente.timestamp()
