"""
Enum centralizado para perfis de usuário.

Este módulo define o Enum Perfil que é a FONTE ÚNICA DA VERDADE
para perfis de usuário no sistema.

Gerado por configurar_projeto.py. Edite conforme necessário.
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
        - ERRADO: perfil = "admin"
    """

    # PERFIS DO SEU SISTEMA #####################################
    ADMIN = "Administrador"
    CLIENTE = "Cliente"
    VENDEDOR = "Vendedor"
    # FIM DOS PERFIS ############################################

    @classmethod
    def perfis_autocadastro(cls) -> list["Perfil"]:
        """
        Perfis que um anônimo PODE escolher no auto-cadastro público.

        NUNCA inclui ADMIN: aceitar o perfil enviado pelo cliente sem filtrar
        permite escalada de privilégio (um anônimo se registraria como
        Administrador). O auto-cadastro (auth_routes.post_cadastrar) valida o
        perfil recebido contra esta lista; a escolha de perfil administrativo
        fica restrita às rotas de admin.

        Fork: ajuste a regra ao seu domínio. Se o signup público tiver um único
        perfil, retorne só esse (ex.: `return [cls.CLIENTE]`). Se exigir
        aprovação manual, combine com um StatusConta inicial "Pendente".
        """
        return [perfil for perfil in cls if perfil != cls.ADMIN]
