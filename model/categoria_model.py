from dataclasses import dataclass
from typing import Optional


@dataclass
class Categoria:
    """Entidade Categoria."""
    id: int
    nome: str
    data_criacao: Optional[str] = None
    data_atualizacao: Optional[str] = None
