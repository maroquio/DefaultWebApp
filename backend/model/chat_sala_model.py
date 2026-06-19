from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatSala:
    """
    Representa uma sala de chat privada entre dois usuários.

    O ID da sala segue o padrão: "menor_id_maior_id"
    """
    id: str
    criada_em: datetime
    ultima_atividade: datetime
