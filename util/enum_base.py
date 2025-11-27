"""
Classe base para Enums de entidades do sistema.

Fornece métodos utilitários comuns para todos os Enums que representam
tipos, status, categorias e outras constantes de domínio.
"""

from enum import Enum
from typing import Optional, List


class EnumEntidade(str, Enum):
    """
    Classe base para Enums de entidades do sistema.

    Herda de str para permitir comparação direta com strings.
    Fornece métodos utilitários para validação, listagem e conversão.
    """

    def __str__(self) -> str:
        """Retorna o valor do enum como string."""
        return self.value

    @classmethod
    def valores(cls) -> List[str]:
        """
        Retorna lista de todos os valores do enum.

        Returns:
            Lista com os valores de cada membro do enum
        """
        return [item.value for item in cls]

    @classmethod
    def nomes(cls) -> List[str]:
        """
        Retorna lista de todos os nomes (keys) do enum.

        Returns:
            Lista com os nomes de cada membro (ex: ['ADMIN', 'CLIENTE'])
        """
        return [item.name for item in cls]

    @classmethod
    def existe(cls, valor: str) -> bool:
        """
        Verifica se um valor existe no enum.

        Args:
            valor: String do valor a verificar

        Returns:
            True se o valor existe, False caso contrário
        """
        return valor in cls.valores()

    @classmethod
    def from_valor(cls, valor: str) -> Optional['EnumEntidade']:
        """
        Converte uma string para o Enum correspondente.

        Args:
            valor: String do valor

        Returns:
            Enum correspondente ou None se inválido
        """
        try:
            return cls(valor)
        except ValueError:
            return None

    @classmethod
    def validar(cls, valor: str) -> str:
        """
        Valida e retorna o valor, levantando exceção se inválido.

        Args:
            valor: String do valor a validar

        Returns:
            O valor validado

        Raises:
            ValueError: Se o valor não for válido
        """
        if not cls.existe(valor):
            raise ValueError(
                f'Valor inválido para {cls.__name__}: "{valor}". '
                f'Valores aceitos: {", ".join(cls.valores())}'
            )
        return valor

    @classmethod
    def obter_por_nome(cls, nome: str) -> Optional['EnumEntidade']:
        """
        Obtém o enum pelo nome (key) ao invés do valor.

        Args:
            nome: Nome do membro (ex: 'ADMIN', 'PENDENTE')

        Returns:
            Enum correspondente ou None se inválido
        """
        try:
            return cls[nome]
        except KeyError:
            return None

    @classmethod
    def para_opcoes_select(cls) -> List[tuple]:
        """
        Retorna lista de tuplas (valor, label) para uso em selects HTML.

        Returns:
            Lista de tuplas [(valor, label), ...]
        """
        return [(item.value, item.value) for item in cls]
