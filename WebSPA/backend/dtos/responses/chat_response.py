"""Schemas de resposta do módulo de chat (mensageria 1-a-1 via SSE)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from model.chat_mensagem_model import ChatMensagem
from model.chat_sala_model import ChatSala
from model.usuario_model import Usuario
from util.foto_util import obter_caminho_foto_usuario


class ChatSalaResponse(BaseModel):
    """Identificação de uma sala de chat criada ou recuperada."""

    sala_id: str = Field(..., description="Identificador único da sala (formato menor_id_maior_id)")

    @classmethod
    def de_sala(cls, sala: ChatSala) -> "ChatSalaResponse":
        """Constrói o response a partir da entidade de domínio."""
        return cls(sala_id=sala.id)


class UsuarioBuscaResponse(BaseModel):
    """Representação enxuta de usuário para busca/autocomplete e cabeçalho de conversa."""

    id: int = Field(..., description="ID único do usuário")
    nome: str = Field(..., description="Nome completo do usuário")
    email: str = Field(..., description="E-mail do usuário")
    foto_url: str = Field(..., description="URL relativa da foto de perfil")

    @classmethod
    def de_usuario(cls, usuario: Usuario) -> "UsuarioBuscaResponse":
        """Constrói o response a partir da entidade de domínio."""
        return cls(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            foto_url=obter_caminho_foto_usuario(usuario.id),
        )


class ChatMensagemResponse(BaseModel):
    """Representação de uma mensagem trocada em uma sala."""

    id: int = Field(..., description="ID único da mensagem")
    sala_id: str = Field(..., description="Identificador da sala")
    usuario_id: int = Field(..., description="ID do autor da mensagem")
    mensagem: str = Field(..., description="Conteúdo da mensagem")
    data_envio: Optional[datetime] = Field(default=None, description="Data/hora de envio")
    lida_em: Optional[datetime] = Field(default=None, description="Data/hora de leitura (None se não lida)")

    @classmethod
    def de_mensagem(cls, mensagem: ChatMensagem) -> "ChatMensagemResponse":
        """Constrói o response a partir da entidade de domínio."""
        return cls(
            id=mensagem.id,
            sala_id=mensagem.sala_id,
            usuario_id=mensagem.usuario_id,
            mensagem=mensagem.mensagem,
            data_envio=mensagem.data_envio,
            lida_em=mensagem.lida_em,
        )


class UltimaMensagemResponse(BaseModel):
    """Resumo da última mensagem exibido na lista de conversas."""

    mensagem: str = Field(..., description="Conteúdo da última mensagem")
    data_envio: Optional[datetime] = Field(default=None, description="Data/hora de envio")
    usuario_id: int = Field(..., description="ID do autor da última mensagem")

    @classmethod
    def de_mensagem(cls, mensagem: ChatMensagem) -> "UltimaMensagemResponse":
        """Constrói o response a partir da entidade de domínio."""
        return cls(
            mensagem=mensagem.mensagem,
            data_envio=mensagem.data_envio,
            usuario_id=mensagem.usuario_id,
        )


class ConversaResponse(BaseModel):
    """Resumo de uma conversa (sala) com o outro participante e indicadores."""

    sala_id: str = Field(..., description="Identificador da sala")
    outro_usuario: UsuarioBuscaResponse = Field(..., description="Dados do outro participante da conversa")
    ultima_mensagem: Optional[UltimaMensagemResponse] = Field(
        default=None, description="Última mensagem da conversa (None se vazia)"
    )
    nao_lidas: int = Field(default=0, description="Quantidade de mensagens não lidas pelo usuário logado")
    ultima_atividade: Optional[datetime] = Field(
        default=None, description="Data/hora da última atividade na conversa"
    )

    @classmethod
    def de_dados(
        cls,
        sala: ChatSala,
        outro_usuario: Usuario,
        ultima_mensagem: Optional[ChatMensagem],
        nao_lidas: int,
    ) -> "ConversaResponse":
        """Constrói o response agregando sala, outro usuário e indicadores."""
        return cls(
            sala_id=sala.id,
            outro_usuario=UsuarioBuscaResponse.de_usuario(outro_usuario),
            ultima_mensagem=(
                UltimaMensagemResponse.de_mensagem(ultima_mensagem)
                if ultima_mensagem
                else None
            ),
            nao_lidas=nao_lidas,
            ultima_atividade=sala.ultima_atividade,
        )


class TotalNaoLidasResponse(BaseModel):
    """Total de mensagens não lidas em todas as salas do usuário."""

    total: int = Field(..., description="Total de mensagens não lidas")


class ChatHealthResponse(BaseModel):
    """Status do subsistema de chat (conexões SSE ativas)."""

    status: str = Field(..., description="Estado do serviço de chat")
    conexoes_ativas: int = Field(..., description="Quantidade de conexões SSE ativas")
    timestamp: datetime = Field(..., description="Momento da verificação")
