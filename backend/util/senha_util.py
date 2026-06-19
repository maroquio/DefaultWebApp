import re
from typing import Tuple
from util.config import PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH


def validar_forca_senha(senha: str) -> Tuple[bool, str]:
    """
    Valida força da senha
    Retorna: (é_válida, mensagem)
    """
    if len(senha) < PASSWORD_MIN_LENGTH:
        return False, f"Senha deve ter no mínimo {PASSWORD_MIN_LENGTH} caracteres"

    if len(senha) > PASSWORD_MAX_LENGTH:
        return False, f"Senha deve ter no máximo {PASSWORD_MAX_LENGTH} caracteres"

    if not re.search(r"[A-Z]", senha):
        return False, "Senha deve conter pelo menos uma letra maiúscula"

    if not re.search(r"[a-z]", senha):
        return False, "Senha deve conter pelo menos uma letra minúscula"

    if not re.search(r"\d", senha):
        return False, "Senha deve conter pelo menos um número"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        return False, "Senha deve conter pelo menos um caractere especial"

    return True, "Senha válida"


def calcular_nivel_senha(senha: str) -> str:
    """Retorna: fraca, média, forte"""
    pontos = 0

    if len(senha) >= PASSWORD_MIN_LENGTH:
        pontos += 1
    if len(senha) >= 12:
        pontos += 1
    if re.search(r"[A-Z]", senha):
        pontos += 1
    if re.search(r"[a-z]", senha):
        pontos += 1
    if re.search(r"\d", senha):
        pontos += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        pontos += 1

    if pontos <= 2:
        return "fraca"
    if pontos <= 4:
        return "média"
    return "forte"
