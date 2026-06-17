from passlib.context import CryptContext
import secrets
from datetime import datetime, timedelta
from util.datetime_util import agora

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def criar_hash_senha(senha: str) -> str:
    """Cria hash da senha"""
    return pwd_context.hash(senha)


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Verifica se senha corresponde ao hash"""
    return pwd_context.verify(senha_plana, senha_hash)


def gerar_token_redefinicao() -> str:
    """Gera token seguro para redefinição de senha"""
    return secrets.token_urlsafe(32)


def obter_data_expiracao_token(horas: int = 1) -> datetime:
    """
    Retorna data de expiração do token com timezone configurado.

    Args:
        horas: Número de horas até a expiração (padrão: 1)

    Returns:
        datetime: Data/hora de expiração no timezone da aplicação
    """
    expiracao = agora() + timedelta(hours=horas)
    return expiracao
