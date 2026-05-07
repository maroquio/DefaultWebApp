from pydantic import BaseModel, Field, field_validator
from dtos.validators import (
    validar_email,
    validar_senha_forte,
    validar_nome_pessoa,
    validar_id_positivo,
    validar_tipo,
)


class CriarCargaDTO(BaseModel):
    """DTO para criação de Cagas pelo administrador."""

    # nome: str = Field(..., description="Nome completo do usuário")
    # email: str = Field(..., description="E-mail do usuário")
    # senha: str = Field(..., description="Senha do usuário")
    # perfil: str = Field(..., description="Perfil/Role do usuário")

    # _validar_nome = field_validator("nome")(())
    # _validar_email = field_validator("email")(())
    # _validar_senha = field_validator("senha")(())
    # _validar_perfil = field_validator("perfil")(())


