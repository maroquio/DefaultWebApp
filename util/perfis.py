"""
Enum centralizado para perfis de usuário.

Este módulo define o Enum Perfil que é a FONTE ÚNICA DA VERDADE
para perfis de usuário no sistema.
"""

from util.enum_base import EnumEntidade


class Perfil(EnumEntidade):
    """
    Enum centralizado para perfis de usuário.

    Este é a FONTE ÚNICA DA VERDADE para perfis no sistema.
    SEMPRE use este Enum ao referenciar perfis, NUNCA strings literais.

    Herda de EnumEntidade que fornece métodos úteis:
        - valores(): Lista todos os valores
        - existe(valor): Verifica se valor existe
        - from_valor(valor): Converte string para enum
        - validar(valor): Valida e retorna ou levanta ValueError

    Exemplos:
        - Correto: perfil = Perfil.ADMIN.value
        - Correto: perfil = Perfil.CLIENTE.value
        - Correto: perfil = Perfil.VENDEDOR.value
        - ERRADO: perfil = "admin"
        - ERRADO: perfil = "cliente"
        - ERRADO: perfil = "vendedor"
    """

    # PERFIS DO SEU SISTEMA #####################################
    ADMIN = "Administrador"
    CLIENTE = "Cliente"
    VENDEDOR = "Vendedor"
    # FIM DOS PERFIS ############################################
