"""Schemas de resposta do módulo de configurações do sistema."""
from typing import Optional

from pydantic import BaseModel, Field

from model.configuracao_model import Configuracao


class ConfigItemResponse(BaseModel):
    """Representação de uma configuração individual do sistema."""

    chave: str = Field(..., description="Chave única da configuração")
    valor: str = Field(..., description="Valor atual da configuração")
    descricao: Optional[str] = Field(
        default=None, description="Descrição da configuração (pode incluir [Categoria])"
    )
    categoria: str = Field(..., description="Categoria extraída da descrição")

    @staticmethod
    def _extrair_categoria(descricao: Optional[str]) -> str:
        """Extrai a categoria do formato '[Categoria] Descrição' da descrição."""
        import re

        if descricao:
            match = re.match(r"^\[([^\]]+)\]", descricao)
            if match:
                return match.group(1)
        return "Outras"

    @classmethod
    def de_configuracao(cls, config: Configuracao) -> "ConfigItemResponse":
        """Constrói o response a partir da entidade de domínio."""
        return cls(
            chave=config.chave,
            valor=config.valor,
            descricao=config.descricao,
            categoria=cls._extrair_categoria(config.descricao),
        )


class ConfigCategoriaResponse(BaseModel):
    """Grupo de configurações pertencentes a uma mesma categoria."""

    categoria: str = Field(..., description="Nome da categoria")
    itens: list[ConfigItemResponse] = Field(
        ..., description="Configurações desta categoria"
    )


class ConfigListaResponse(BaseModel):
    """Listagem completa de configurações agrupadas por categoria."""

    total: int = Field(..., description="Total de configurações")
    categorias: list[ConfigCategoriaResponse] = Field(
        ..., description="Configurações agrupadas por categoria"
    )

    @classmethod
    def de_agrupado(
        cls, agrupado: dict[str, list[Configuracao]]
    ) -> "ConfigListaResponse":
        """
        Constrói o response a partir do dicionário {categoria: [Configuracao]}
        retornado por ``configuracao_repo.obter_por_categoria()``.
        """
        categorias = [
            ConfigCategoriaResponse(
                categoria=categoria,
                itens=[ConfigItemResponse.de_configuracao(c) for c in configs],
            )
            for categoria, configs in agrupado.items()
        ]
        total = sum(len(c.itens) for c in categorias)
        return cls(total=total, categorias=categorias)


class SalvarConfigResultadoResponse(BaseModel):
    """Resultado de uma atualização em lote de configurações."""

    atualizadas: int = Field(..., description="Quantidade de configurações atualizadas")
    chaves_nao_encontradas: list[str] = Field(
        default_factory=list,
        description="Chaves enviadas que não existem no banco (ignoradas)",
    )
    message: str = Field(..., description="Mensagem legível do resultado")
