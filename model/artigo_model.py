from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class StatusArtigo(Enum):
    RASCUNHO = "Rascunho"
    FINALIZADO = "Finalizado"
    PUBLICADO = "Publicado"
    PAUSADO = "Pausado"


@dataclass
class Artigo:
    # Campos obrigatórios (com defaults para permitir criação)
    titulo: str = ""
    conteudo: str = ""
    status: str = "Rascunho"
    usuario_id: int = 0
    categoria_id: int = 0
    # Campos opcionais
    id: Optional[int] = None
    resumo: Optional[str] = None
    qtde_visualizacoes: int = 0
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    data_publicacao: Optional[datetime] = None
    data_pausa: Optional[datetime] = None
    # Campos do JOIN (para exibição)
    usuario_nome: Optional[str] = None
    usuario_email: Optional[str] = None
    categoria_nome: Optional[str] = None