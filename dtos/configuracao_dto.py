import re

from pydantic import BaseModel, Field, field_validator
from typing import Optional

from dtos.validators import (
    validar_email_opcional,
    validar_rate_limit,
    validar_inteiro_range,
)

# =============================================================================
# Constantes de Validação
# =============================================================================

# Limites de foto de perfil (em pixels)
FOTO_PERFIL_MIN_PIXELS = 64
FOTO_PERFIL_MAX_PIXELS = 2048

# Limites de upload de foto (em bytes)
FOTO_UPLOAD_MIN_BYTES = 102400      # 100KB
FOTO_UPLOAD_MAX_BYTES = 52428800    # 50MB

# Limites de rate limiting
RATE_LIMIT_MAX_TENTATIVAS = 1000
RATE_LIMIT_MAX_MINUTOS = 1440       # 24 horas

# Limites de toast delay (em milissegundos)
TOAST_DELAY_MIN_MS = 1000           # 1 segundo
TOAST_DELAY_MAX_MS = 30000          # 30 segundos

# Limite de caracteres para strings
MAX_CARACTERES_NOME = 200


class ConfiguracaoBaseDTO(BaseModel):
    """DTO base para configurações"""

    chave: str = Field(..., description="Chave única da configuração em snake_case")
    valor: str = Field(..., description="Valor da configuração")
    descricao: Optional[str] = Field(
        default="", description="Descrição opcional da configuração"
    )


class ConfiguracaoAplicacaoDTO(BaseModel):
    """DTO para configurações de aplicação (nome, email, etc)"""

    app_name: Optional[str] = Field(
        default=None, description="Nome da aplicação exibido na interface"
    )
    resend_from_email: Optional[str] = Field(
        default=None, description="Email remetente para envio de notificações"
    )
    resend_from_name: Optional[str] = Field(
        default=None, description="Nome exibido como remetente dos emails"
    )

    _validar_email = field_validator("resend_from_email")(validar_email_opcional())


class ConfiguracaoFotosDTO(BaseModel):
    """DTO para configurações de fotos"""

    foto_perfil_tamanho_max: Optional[int] = Field(
        default=None, description="Tamanho máximo da foto de perfil em pixels (64-2048)"
    )
    foto_max_upload_bytes: Optional[int] = Field(
        default=None,
        description="Tamanho máximo de upload de foto em bytes (100KB-50MB)",
    )

    @field_validator("foto_perfil_tamanho_max")
    @classmethod
    def validar_tamanho_foto(cls, v):
        if v is not None:
            if v < FOTO_PERFIL_MIN_PIXELS:
                raise ValueError(f"Tamanho mínimo é {FOTO_PERFIL_MIN_PIXELS} pixels")
            if v > FOTO_PERFIL_MAX_PIXELS:
                raise ValueError(f"Tamanho máximo é {FOTO_PERFIL_MAX_PIXELS} pixels")
            if v % 2 != 0:
                raise ValueError("Tamanho deve ser número par de pixels")
        return v

    _validar_upload = field_validator("foto_max_upload_bytes")(
        validar_inteiro_range(FOTO_UPLOAD_MIN_BYTES, FOTO_UPLOAD_MAX_BYTES, "Tamanho de upload")
    )


# Validadores reutilizáveis para rate limiting
_validar_tentativas_generico, _validar_minutos_generico = validar_rate_limit(
    1, RATE_LIMIT_MAX_TENTATIVAS, 1, RATE_LIMIT_MAX_MINUTOS
)
_validar_tentativas_login, _validar_minutos_login = validar_rate_limit(3, 20, 1, 60, " de login")
_validar_tentativas_cadastro, _validar_minutos_cadastro = validar_rate_limit(1, 10, 5, 120, " de cadastro")
_validar_tentativas_senha, _validar_minutos_senha = validar_rate_limit(1, 10, 1, 60, " de senha")


class ConfiguracaoRateLimitDTO(BaseModel):
    """DTO genérico para configurações de rate limiting"""

    max_tentativas: int = Field(..., description="Máximo de tentativas permitidas")
    minutos: int = Field(..., description="Período em minutos (máx 24h)")

    _validar_max = field_validator("max_tentativas")(_validar_tentativas_generico)
    _validar_min = field_validator("minutos")(_validar_minutos_generico)


class ConfiguracaoRateLimitLoginDTO(ConfiguracaoRateLimitDTO):
    """DTO específico para rate limit de login (validações mais restritas)"""

    max_tentativas: int = Field(..., description="Tentativas de login (3-20)")
    minutos: int = Field(..., description="Período em minutos (1-60)")

    _validar_max = field_validator("max_tentativas")(_validar_tentativas_login)
    _validar_min = field_validator("minutos")(_validar_minutos_login)


class ConfiguracaoRateLimitCadastroDTO(ConfiguracaoRateLimitDTO):
    """DTO específico para rate limit de cadastro"""

    max_tentativas: int = Field(..., description="Tentativas de cadastro (1-10)")
    minutos: int = Field(..., description="Período em minutos (5-120)")

    _validar_max = field_validator("max_tentativas")(_validar_tentativas_cadastro)
    _validar_min = field_validator("minutos")(_validar_minutos_cadastro)


class ConfiguracaoRateLimitSenhaDTO(ConfiguracaoRateLimitDTO):
    """DTO específico para rate limit de recuperação/alteração de senha"""

    max_tentativas: int = Field(..., description="Tentativas (1-10)")
    minutos: int = Field(..., description="Período em minutos (1-60)")

    _validar_max = field_validator("max_tentativas")(_validar_tentativas_senha)
    _validar_min = field_validator("minutos")(_validar_minutos_senha)


class ConfiguracaoUIDTO(BaseModel):
    """DTO para configurações de interface"""

    toast_auto_hide_delay_ms: Optional[int] = Field(
        default=None,
        description="Tempo de exibição das notificações toast em milissegundos (1000-30000)",
    )

    @field_validator("toast_auto_hide_delay_ms")
    @classmethod
    def validar_delay(cls, v):
        if v is not None:
            if v < TOAST_DELAY_MIN_MS:
                raise ValueError(f"Delay mínimo é {TOAST_DELAY_MIN_MS}ms (1 segundo)")
            if v > TOAST_DELAY_MAX_MS:
                raise ValueError(f"Delay máximo é {TOAST_DELAY_MAX_MS}ms (30 segundos)")
        return v


class EditarConfiguracaoDTO(BaseModel):
    """DTO para edição de uma configuração individual"""

    chave: str = Field(..., description="Chave única da configuração em snake_case")
    valor: str = Field(..., description="Novo valor da configuração")

    @field_validator("valor")
    @classmethod
    def validar_valor_nao_vazio(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Valor não pode ser vazio")
        return v.strip()

    @field_validator("chave")
    @classmethod
    def validar_chave_formato(cls, v):
        """Valida que a chave segue o padrão snake_case"""
        if not re.match(r"^[a-z][a-z0-9_]*$", v):
            raise ValueError(
                "Chave deve estar em snake_case (apenas letras minúsculas, números e underscore)"
            )
        return v


class ValidarRateLimitDTO(BaseModel):
    """DTO para validação de qualquer par max/minutos de rate limit"""

    max_tentativas: str = Field(..., description="Máximo de tentativas")
    minutos: str = Field(..., description="Período em minutos")

    @field_validator("max_tentativas", "minutos")
    @classmethod
    def validar_numerico(cls, v, info):
        """Valida que os valores são números inteiros positivos"""
        try:
            num = int(v)
            if num < 1:
                raise ValueError(f"{info.field_name} deve ser pelo menos 1")
            if info.field_name == "max_tentativas" and num > RATE_LIMIT_MAX_TENTATIVAS:
                raise ValueError(f"Máximo de tentativas não pode exceder {RATE_LIMIT_MAX_TENTATIVAS}")
            if info.field_name == "minutos" and num > RATE_LIMIT_MAX_MINUTOS:
                raise ValueError(f"Período não pode exceder {RATE_LIMIT_MAX_MINUTOS} minutos (24 horas)")
            return v
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"{info.field_name} deve ser um número inteiro")
            raise


class SalvarConfiguracaoLoteDTO(BaseModel):
    """
    DTO para salvamento em lote de configurações.

    Recebe um dicionário de {chave: valor} e valida cada par
    de acordo com regras específicas baseadas na chave.
    """

    configs: dict[str, str] = Field(..., description="Dicionário de configurações")

    @field_validator("configs")
    @classmethod
    def validar_configs(cls, v):
        """Valida cada configuração individualmente"""
        if not v:
            raise ValueError("Deve fornecer pelo menos uma configuração")

        erros = {}

        for chave, valor in v.items():
            # Validar formato da chave
            if not chave or not isinstance(chave, str):
                erros[chave] = "Chave inválida"
                continue

            # Validar valor não vazio
            if not valor or not isinstance(valor, str) or valor.strip() == "":
                erros[chave] = "Valor não pode ser vazio"
                continue

            # Validações específicas por tipo de configuração
            try:
                # Rate limits (pares max/minutos)
                if chave.endswith("_max"):
                    num = int(valor)
                    if num < 1:
                        erros[chave] = "Deve ser pelo menos 1"
                    elif num > RATE_LIMIT_MAX_TENTATIVAS:
                        erros[chave] = f"Máximo permitido é {RATE_LIMIT_MAX_TENTATIVAS}"

                elif chave.endswith("_minutos"):
                    num = int(valor)
                    if num < 1:
                        erros[chave] = "Deve ser pelo menos 1 minuto"
                    elif num > RATE_LIMIT_MAX_MINUTOS:
                        erros[chave] = f"Máximo permitido é {RATE_LIMIT_MAX_MINUTOS} minutos (24 horas)"

                # Toast delay
                elif chave == "toast_auto_hide_delay_ms":
                    num = int(valor)
                    if num < TOAST_DELAY_MIN_MS:
                        erros[chave] = f"Mínimo é {TOAST_DELAY_MIN_MS}ms (1 segundo)"
                    elif num > TOAST_DELAY_MAX_MS:
                        erros[chave] = f"Máximo é {TOAST_DELAY_MAX_MS}ms (30 segundos)"

                # Foto perfil tamanho
                elif chave == "foto_perfil_tamanho_max":
                    num = int(valor)
                    if num < FOTO_PERFIL_MIN_PIXELS:
                        erros[chave] = f"Mínimo é {FOTO_PERFIL_MIN_PIXELS} pixels"
                    elif num > FOTO_PERFIL_MAX_PIXELS:
                        erros[chave] = f"Máximo é {FOTO_PERFIL_MAX_PIXELS} pixels"

                # Foto upload bytes
                elif chave == "foto_max_upload_bytes":
                    num = int(valor)
                    if num < FOTO_UPLOAD_MIN_BYTES:
                        erros[chave] = f"Mínimo é 100KB ({FOTO_UPLOAD_MIN_BYTES} bytes)"
                    elif num > FOTO_UPLOAD_MAX_BYTES:
                        erros[chave] = f"Máximo é 50MB ({FOTO_UPLOAD_MAX_BYTES} bytes)"

                # Email
                elif chave == "resend_from_email":
                    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                    if not re.match(pattern, valor):
                        erros[chave] = "Email inválido"

                # Strings gerais (app_name, resend_from_name, etc)
                elif chave in ["app_name", "resend_from_name"]:
                    if len(valor) > MAX_CARACTERES_NOME:
                        erros[chave] = f"Máximo de {MAX_CARACTERES_NOME} caracteres"

            except ValueError:
                erros[chave] = "Valor deve ser um número válido"

        # Se houver erros, levantar exceção com detalhes
        if erros:
            erro_msg = "; ".join([f"{k}: {v}" for k, v in erros.items()])
            raise ValueError(f"Erros de validação encontrados: {erro_msg}")

        return v
