import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv


load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', 'dados.db')
TIMEZONE = os.getenv('TIMEZONE', 'America/Sao_Paulo')
APP_TIMEZONE = ZoneInfo(TIMEZONE)


@contextmanager
def obter_conexao():
    """Context manager para conexão com banco de dados"""
    registrar_adaptadores()
    conn = sqlite3.connect(
        DATABASE_PATH,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def adaptar_datetime(dt: datetime) -> str:
    """
    Adaptador para converter datetime para string, armazenando em UTC naive.

    Estratégia:
    1. Se datetime tem timezone, converte para UTC
    2. Remove timezone info (armazena como "naive")
    3. Formato armazenado: YYYY-MM-DD HH:MM:SS.mmmmmm (sem offset)

    Args:
        dt: datetime object (com ou sem timezone)

    Returns:
        String no formato ISO sem timezone (UTC naive)
    """
    # Se já tem timezone, converte para UTC
    if dt.tzinfo is not None:
        dt_utc = dt.astimezone(ZoneInfo("UTC"))
    else:
        # Se é naive, assume que já está em UTC
        dt_utc = dt

    # Remove timezone info e formata
    dt_naive = dt_utc.replace(tzinfo=None)
    return dt_naive.isoformat(' ')


def converter_datetime(s: bytes) -> datetime:
    """
    Conversor para converter string do banco em datetime com timezone.

    Estratégia:
    1. Lê string do banco (assume que está em UTC naive)
    2. Adiciona timezone UTC
    3. Converte para timezone da aplicação

    Args:
        s: Bytes da string armazenada no banco

    Returns:
        datetime object com timezone da aplicação
    """
    # Parse string como naive (sem timezone)
    dt_str = s.decode().replace(' ', 'T')  # Normaliza formato
    dt_naive = datetime.fromisoformat(dt_str)

    # Adiciona UTC timezone
    dt_utc = dt_naive.replace(tzinfo=ZoneInfo("UTC"))

    # Converte para timezone da aplicação
    dt_local = dt_utc.astimezone(APP_TIMEZONE)

    return dt_local


def registrar_adaptadores() -> None:
    """Registra os adaptadores customizados para datetime no sqlite3"""
    sqlite3.register_adapter(datetime, adaptar_datetime)
    sqlite3.register_converter("TIMESTAMP", converter_datetime)
