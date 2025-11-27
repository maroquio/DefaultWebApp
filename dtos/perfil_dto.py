from pydantic import BaseModel, Field, field_validator, model_validator
from dtos.validators import (
    validar_email,
    validar_senha_forte,
    validar_nome_pessoa,
    validar_string_obrigatoria,
    validar_senhas_coincidem,
)


class EditarPerfilDTO(BaseModel):
    nome: str = Field(..., description="Nome completo do usuário")
    email: str = Field(..., description="E-mail do usuário")

    _validar_nome = field_validator("nome")(validar_nome_pessoa(min_palavras=2))
    _validar_email = field_validator("email")(validar_email())


class AlterarSenhaDTO(BaseModel):
    senha_atual: str = Field(..., description="Senha atual do usuário")
    senha_nova: str = Field(..., description="Nova senha desejada")
    confirmar_senha: str = Field(..., description="Confirmação da nova senha")

    _validar_senha_atual = field_validator("senha_atual")(
        validar_string_obrigatoria("Senha atual")
    )
    _validar_senha_nova = field_validator("senha_nova")(validar_senha_forte())
    _validar_confirmar = field_validator("confirmar_senha")(
        validar_string_obrigatoria(
            "Confirmação de senha", tamanho_minimo=8, tamanho_maximo=128
        )
    )

    _validar_senhas_match = model_validator(mode="after")(
        validar_senhas_coincidem("senha_nova", "confirmar_senha")
    )
