from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from dtos.validators import validar_string_obrigatoria, validar_id_positivo


class CriarSalaDTO(BaseModel):
    """DTO para criar ou obter uma sala de chat."""
    outro_usuario_id: int = Field(..., description="ID do outro usuário participante da conversa")

    _validar_outro_usuario_id = field_validator('outro_usuario_id')(
        validar_id_positivo("ID do usuário")
    )


class EnviarMensagemDTO(BaseModel):
    """DTO para enviar uma mensagem em uma sala."""
    sala_id: str = Field(..., description="Identificador único da sala de chat")
    mensagem: str = Field(..., description="Conteúdo da mensagem a ser enviada")

    _validar_sala_id = field_validator('sala_id')(validar_string_obrigatoria("ID da sala"))
    _validar_mensagem = field_validator('mensagem')(
        validar_string_obrigatoria("Mensagem", tamanho_minimo=1, tamanho_maximo=5000)
    )


class ConversaResumoDTO(BaseModel):
    """DTO para resumo de uma conversa na lista."""
    sala_id: str = Field(..., description="Identificador único da sala de chat")
    outro_usuario: dict = Field(..., description="Dados do outro participante {id, nome, email, foto_url}")
    ultima_mensagem: Optional[dict] = Field(
        default=None, description="Última mensagem da conversa {mensagem, data_envio, usuario_id}"
    )
    nao_lidas: int = Field(default=0, description="Quantidade de mensagens não lidas")
    ultima_atividade: datetime = Field(..., description="Data/hora da última atividade na conversa")


class UsuarioBuscaDTO(BaseModel):
    """DTO para resultado de busca de usuários."""
    id: int = Field(..., description="ID único do usuário")
    nome: str = Field(..., description="Nome completo do usuário")
    email: str = Field(..., description="Email do usuário")
    foto_url: str = Field(..., description="URL da foto de perfil do usuário")
