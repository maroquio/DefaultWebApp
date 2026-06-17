from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatMensagem:
    """
    Representa uma mensagem trocada em uma sala de chat.

    Attributes:
        id: ID único da mensagem
        sala_id: ID da sala de chat
        usuario_id: ID do usuário que enviou a mensagem
        mensagem: Conteúdo da mensagem (suporta markdown lite)
        data_envio: Timestamp de quando a mensagem foi enviada
        lida_em: Timestamp de quando a mensagem foi lida (None se não lida)
    """
    id: int
    sala_id: str
    usuario_id: int
    mensagem: str
    data_envio: datetime
    lida_em: Optional[datetime] = None
