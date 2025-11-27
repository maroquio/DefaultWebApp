from pydantic import BaseModel, Field, field_validator
from util.perfis import Perfil
from dtos.validators import (
    validar_email,
    validar_senha_forte,
    validar_nome_pessoa,
    validar_id_positivo,
    validar_tipo,
)


class CriarUsuarioDTO(BaseModel):
    """DTO para criação de usuário pelo administrador."""

    nome: str = Field(..., description="Nome completo do usuário")
    email: str = Field(..., description="E-mail do usuário")
    senha: str = Field(..., description="Senha do usuário")
    perfil: str = Field(..., description="Perfil/Role do usuário")

    _validar_nome = field_validator("nome")(validar_nome_pessoa())
    _validar_email = field_validator("email")(validar_email())
    _validar_senha = field_validator("senha")(validar_senha_forte())
    _validar_perfil = field_validator("perfil")(validar_tipo("Perfil", Perfil))


class AlterarUsuarioDTO(BaseModel):
    """DTO para alteração de usuário pelo administrador."""

    id: int = Field(..., description="ID do usuário a ser alterado")
    nome: str = Field(..., description="Nome completo do usuário")
    email: str = Field(..., description="E-mail do usuário")
    perfil: str = Field(..., description="Perfil/Role do usuário")

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_nome = field_validator("nome")(validar_nome_pessoa())
    _validar_email = field_validator("email")(validar_email())
    _validar_perfil = field_validator("perfil")(validar_tipo("Perfil", Perfil))
