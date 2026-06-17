"""
Módulo de utilitários para manipulação de datetime com timezone.

Centraliza toda criação de datetime no sistema para garantir
consistência de timezone em toda a aplicação.
"""
from datetime import datetime, date
from zoneinfo import ZoneInfo
from typing import Optional
from util.config import APP_TIMEZONE


def agora() -> datetime:
    """
    Retorna datetime atual no timezone configurado da aplicação.

    Esta função deve ser usada em vez de datetime.now() para garantir
    que todos os timestamps sejam criados com o timezone correto.

    Returns:
        datetime: Datetime atual com timezone configurado (America/Sao_Paulo)
    """
    return datetime.now(APP_TIMEZONE)


def hoje() -> date:
    """
    Retorna date de hoje no timezone configurado da aplicação.

    Returns:
        date: Data atual no timezone configurado
    """
    return agora().date()


def converter_para_timezone(dt: datetime, tz: Optional[ZoneInfo] = None) -> datetime:
    """
    Converte um datetime para o timezone especificado.

    Se o datetime fornecido for naive (sem timezone), assume UTC.
    Se o timezone de destino não for especificado, usa APP_TIMEZONE.

    Args:
        dt: Datetime a ser convertido
        tz: Timezone de destino (opcional, padrão: APP_TIMEZONE)

    Returns:
        datetime: Datetime convertido para o timezone especificado
    """
    if tz is None:
        tz = APP_TIMEZONE

    # Se datetime é naive (sem timezone), assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    # Converte para o timezone de destino
    return dt.astimezone(tz)


def datetime_para_string_iso(dt: datetime) -> str:
    """
    Converte datetime para string ISO 8601 com timezone.

    Args:
        dt: Datetime a ser convertido

    Returns:
        str: String no formato ISO 8601 (YYYY-MM-DDTHH:MM:SS+HH:MM)
    """
    return dt.isoformat()


def string_iso_para_datetime(iso_string: str) -> datetime:
    """
    Converte string ISO 8601 para datetime com timezone.

    Args:
        iso_string: String no formato ISO 8601

    Returns:
        datetime: Datetime parseado com timezone
    """
    return datetime.fromisoformat(iso_string)
