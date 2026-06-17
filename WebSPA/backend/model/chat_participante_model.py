from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatParticipante:
    """
    Representa a participação de um usuário em uma sala de chat.

    Attributes:
        sala_id: ID da sala de chat
        usuario_id: ID do usuário participante
        ultima_leitura: Timestamp da última vez que o usuário leu mensagens
    """
    sala_id: str
    usuario_id: int
    ultima_leitura: Optional[datetime] = None
