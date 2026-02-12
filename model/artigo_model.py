from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from util.enum_base import EnumEntidade


class StatusArtigo(EnumEntidade):
    """
    Enum para status de artigos.

    Herda de EnumEntidade que fornece métodos úteis:
        - valores(): Lista todos os valores
        - existe(valor): Verifica se valor existe
        - from_valor(valor): Converte string para enum
        - validar(valor): Valida e retorna ou levanta ValueError
    """

    RASCUNHO = "Rascunho"
    FINALIZADO = "Finalizado"
    PUBLICADO = "Publicado"
    PAUSADO = "Pausado"


@dataclass
class Artigo:
    # Campos obrigatórios (com defaults para permitir criação)
    titulo: str = ""
    conteudo: str = ""
    status: StatusArtigo = StatusArtigo.RASCUNHO
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