"""Schemas de resposta do módulo de usuários."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from model.usuario_model import Usuario
from util.foto_util import obter_caminho_foto_usuario


class UsuarioResponse(BaseModel):
    """Representação pública de um usuário (sem dados sensíveis)."""

    id: int
    nome: str
    email: str
    perfil: str
    foto_url: str = Field(..., description="URL relativa da foto de perfil")
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None

    @classmethod
    def de_usuario(cls, usuario: Usuario) -> "UsuarioResponse":
        """Constrói o response a partir da entidade de domínio."""
        return cls(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            perfil=usuario.perfil,
            foto_url=obter_caminho_foto_usuario(usuario.id),
            data_cadastro=usuario.data_cadastro,
            data_atualizacao=usuario.data_atualizacao,
        )


class DashboardResponse(BaseModel):
    """Contadores exibidos no painel inicial do usuário."""

    chamados_pendentes: Optional[int] = Field(
        default=None, description="Total de chamados pendentes (visão admin)"
    )
    chamados_abertos: Optional[int] = Field(
        default=None, description="Chamados em aberto do próprio usuário"
    )
