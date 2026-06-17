from pydantic import BaseModel, Field, field_validator, model_validator
from dtos.validators import (
    validar_email,
    validar_tipo,
    validar_senha_forte,
    validar_nome_pessoa,
    validar_string_obrigatoria,
    validar_senhas_coincidem,
)
from util.perfis import Perfil


class LoginDTO(BaseModel):
    email: str = Field(..., description="E-mail do usuário")
    senha: str = Field(..., description="Senha do usuário")

    _validar_email = field_validator("email")(validar_email())
    _validar_senha = field_validator("senha")(validar_senha_forte())


class CadastroDTO(BaseModel):
    perfil: str = Field(..., description="Perfil/Role do usuário")
    nome: str = Field(..., description="Nome completo do usuário")
    email: str = Field(..., description="E-mail do usuário")
    senha: str = Field(..., description="Senha do usuário")
    confirmar_senha: str = Field(..., description="Confirmação da senha")

    _validar_perfil = field_validator("perfil")(validar_tipo("Perfil", Perfil))
    _validar_nome = field_validator("nome")(validar_nome_pessoa())
    _validar_email = field_validator("email")(validar_email())
    _validar_senha = field_validator("senha")(validar_senha_forte())
    _validar_confirmar = field_validator("confirmar_senha")(validar_senha_forte())

    _validar_senhas_match = model_validator(mode="after")(validar_senhas_coincidem())


class EsqueciSenhaDTO(BaseModel):
    email: str = Field(..., description="E-mail cadastrado do usuário")

    _validar_email = field_validator("email")(validar_email())


class RedefinirSenhaDTO(BaseModel):
    token: str = Field(..., description="Token de redefinição recebido por e-mail")
    senha: str = Field(..., description="Nova senha do usuário")
    confirmar_senha: str = Field(..., description="Confirmação da nova senha")

    _validar_token = field_validator("token")(
        validar_string_obrigatoria("Token", tamanho_minimo=1)
    )
    _validar_senha = field_validator("senha")(validar_senha_forte())
    _validar_confirmar = field_validator("confirmar_senha")(validar_senha_forte())

    _validar_senhas_match = model_validator(mode="after")(validar_senhas_coincidem())
