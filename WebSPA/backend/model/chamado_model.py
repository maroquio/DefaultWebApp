from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from util.enum_base import EnumEntidade


class StatusChamado(EnumEntidade):
    """
    Enum para status de chamados.

    Herda de EnumEntidade que fornece métodos úteis:
        - valores(): Lista todos os valores
        - existe(valor): Verifica se valor existe
        - from_valor(valor): Converte string para enum
        - validar(valor): Valida e retorna ou levanta ValueError
    """

    ABERTO = "Aberto"
    EM_ANALISE = "Em Análise"
    RESOLVIDO = "Resolvido"
    FECHADO = "Fechado"


class PrioridadeChamado(EnumEntidade):
    """
    Enum para prioridade de chamados.

    Herda de EnumEntidade que fornece métodos úteis:
        - valores(): Lista todos os valores
        - existe(valor): Verifica se valor existe
        - from_valor(valor): Converte string para enum
        - validar(valor): Valida e retorna ou levanta ValueError
    """

    BAIXA = "Baixa"
    MEDIA = "Média"
    ALTA = "Alta"
    URGENTE = "Urgente"


@dataclass
class Chamado:
    id: int
    titulo: str
    status: StatusChamado
    prioridade: PrioridadeChamado
    usuario_id: int
    data_abertura: Optional[datetime] = None
    data_fechamento: Optional[datetime] = None
    # Campos do JOIN (para exibição)
    usuario_nome: Optional[str] = None
    usuario_email: Optional[str] = None
    mensagens_nao_lidas: int = 0
    tem_resposta_admin: bool = False
