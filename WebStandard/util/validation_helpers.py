"""
Helpers de validação reutilizáveis

Funções auxiliares para validações comuns em formulários e DTOs,
centralizando lógica que seria duplicada em múltiplos lugares.

Autor: DefaultWebApp
Versão: 1.0.0
"""
import sqlite3
from typing import Optional
from repo import usuario_repo
from util.logger_config import logger


def verificar_email_disponivel(
    email: str,
    usuario_id_atual: Optional[int] = None
) -> tuple[bool, Optional[str]]:
    """
    Verifica se um e-mail está disponível para uso

    Args:
        email: E-mail a ser verificado
        usuario_id_atual: ID do usuário atual (para permitir manter próprio email)
                         Se None, qualquer email existente é considerado indisponível

    Returns:
        Tupla (disponivel: bool, mensagem_erro: Optional[str])
        - (True, None): Email está disponível
        - (False, "mensagem"): Email não disponível com mensagem de erro

    Examples:
        >>> # Verificar em cadastro (sem usuário atual)
        >>> disponivel, msg = verificar_email_disponivel("novo@email.com")
        >>> if not disponivel:
        ...     print(msg)  # "Este e-mail já está cadastrado"

        >>> # Verificar em edição (com usuário atual)
        >>> disponivel, msg = verificar_email_disponivel("usuario@email.com", usuario_id=5)
        >>> # Retorna True se email pertence ao usuário 5 ou não existe
    """
    try:
        # Buscar usuário com esse email
        usuario_existente = usuario_repo.obter_por_email(email)

        # Se não existe, email está disponível
        if not usuario_existente:
            return True, None

        # Se existe e temos um usuario_id_atual
        if usuario_id_atual is not None:
            # Verifica se o email pertence ao próprio usuário
            if usuario_existente.id == usuario_id_atual:
                # Email do próprio usuário - pode manter
                return True, None
            else:
                # Email de outro usuário
                logger.warning(
                    f"Tentativa de usar email já cadastrado: {email} "
                    f"(Pertence ao usuário ID {usuario_existente.id}, "
                    f"tentativa do usuário ID {usuario_id_atual})"
                )
                return False, "Este e-mail já está sendo usado em outra conta de usuário."

        # Existe e não temos usuario_id_atual (cadastro novo)
        logger.warning(f"Tentativa de cadastro com email já existente: {email}")
        return False, "Este e-mail já está cadastrado no sistema."

    except sqlite3.Error as e:
        # Em caso de erro de banco, logar e retornar como indisponível por segurança
        logger.error(f"Erro ao verificar disponibilidade de email '{email}': {e}")
        return False, "Erro ao verificar e-mail. Tente novamente."


def email_existe(email: str) -> bool:
    """
    Verifica simplesmente se um e-mail existe no sistema

    Args:
        email: E-mail a ser verificado

    Returns:
        True se e-mail existe, False caso contrário

    Examples:
        >>> if email_existe("admin@sistema.com"):
        ...     print("Email já cadastrado")
    """
    try:
        usuario = usuario_repo.obter_por_email(email)
        return usuario is not None
    except sqlite3.Error as e:
        logger.error(f"Erro ao verificar existência de email '{email}': {e}")
        # Em caso de erro, retornar True por segurança (assume que existe)
        return True
