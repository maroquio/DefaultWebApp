from pydantic import BaseModel, Field, field_validator
from dtos.validators import validar_string_obrigatoria


class CriarInteracaoDTO(BaseModel):
    """DTO para criação de interação/resposta em chamado."""

    mensagem: str = Field(..., description="Texto da mensagem/resposta")

    _validar_mensagem = field_validator("mensagem")(
        validar_string_obrigatoria(
            nome_campo="Mensagem", tamanho_minimo=10, tamanho_maximo=2000
        )
    )
