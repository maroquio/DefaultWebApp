from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from util.enum_base import EnumEntidade


class StatusPagamento(EnumEntidade):
    """
    Enum para status de pagamentos.

    Herda de EnumEntidade que fornece métodos úteis:
        - valores(): Lista todos os valores
        - existe(valor): Verifica se valor existe
        - from_valor(valor): Converte string para enum
        - validar(valor): Valida e retorna ou levanta ValueError
    """

    PENDENTE = "Pendente"
    EM_PROCESSAMENTO = "Em Processamento"
    APROVADO = "Aprovado"
    RECUSADO = "Recusado"
    CANCELADO = "Cancelado"
    REEMBOLSADO = "Reembolsado"


@dataclass
class Pagamento:
    id: int
    usuario_id: int
    descricao: str
    valor: float
    status: StatusPagamento
    preference_id: Optional[str] = None       # ID da preferência no Mercado Pago
    payment_id: Optional[str] = None          # ID do pagamento confirmado no MP
    external_reference: Optional[str] = None  # Referência externa gerada pela app
    url_checkout: Optional[str] = None        # URL init_point para redirecionamento
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    # Campo via JOIN para exibição
    usuario_nome: Optional[str] = None
