"""Schemas de resposta do módulo de backups do banco de dados."""
from datetime import datetime

from pydantic import BaseModel, Field

from util.backup_util import BackupInfo


class BackupInfoResponse(BaseModel):
    """Representação pública de um arquivo de backup."""

    nome_arquivo: str = Field(..., description="Nome do arquivo de backup")
    caminho_completo: str = Field(..., description="Caminho completo no servidor")
    data_criacao: datetime = Field(..., description="Data/hora de criação do backup")
    tamanho_bytes: int = Field(..., description="Tamanho do arquivo em bytes")
    tamanho_formatado: str = Field(
        ..., description="Tamanho formatado para exibição (ex: '2.5 MB')"
    )
    tipo: str = Field(..., description="Tipo do backup: 'manual' ou 'automático'")

    @classmethod
    def de_backup_info(cls, info: BackupInfo) -> "BackupInfoResponse":
        """Constrói o response a partir do objeto BackupInfo do util."""
        return cls(
            nome_arquivo=info.nome_arquivo,
            caminho_completo=info.caminho_completo,
            data_criacao=info.data_criacao,
            tamanho_bytes=info.tamanho_bytes,
            tamanho_formatado=info.tamanho_formatado,
            tipo=info.tipo,
        )
