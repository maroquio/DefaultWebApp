from dataclasses import dataclass
from typing import Optional


@dataclass
class Configuracao:
    id: int
    chave: str
    valor: str
    descricao: Optional[str] = None
