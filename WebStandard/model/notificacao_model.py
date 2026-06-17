from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from util.enum_base import EnumEntidade


class TipoNotificacao(EnumEntidade):
    """
    Tipos de notificação disponíveis.

    Herda de EnumEntidade que fornece métodos úteis:
        - valores(): Lista todos os valores
        - existe(valor): Verifica se valor existe
        - from_valor(valor): Converte string para enum

    Para adicionar novos tipos: adicione apenas nesta classe.
    """

    INFO = "info"
    SUCESSO = "sucesso"
    AVISO = "aviso"
    ERRO = "erro"


@dataclass
class Notificacao:
    """
    Notificação persistente para um usuário.

    Campos:
        id: ID da notificação
        usuario_id: ID do usuário destinatário
        titulo: Título curto da notificação
        mensagem: Corpo da mensagem
        tipo: Tipo visual (info, sucesso, aviso, erro)
        lida: Se o usuário já visualizou
        url_acao: URL opcional para redirecionar ao clicar
        data_criacao: Quando foi criada

    Exemplo de criação via utilitário:
        from util.notificacao_util import criar_notificacao
        criar_notificacao(
            usuario_id=usuario_logado.id,
            titulo="Pedido aprovado",
            mensagem="Seu pedido #123 foi aprovado com sucesso.",
            url_acao="/pedidos/123",
            tipo=TipoNotificacao.SUCESSO,
        )
    """

    id: int
    usuario_id: int
    titulo: str
    mensagem: str
    tipo: TipoNotificacao = TipoNotificacao.INFO
    lida: bool = False
    url_acao: Optional[str] = None
    data_criacao: Optional[datetime] = None
