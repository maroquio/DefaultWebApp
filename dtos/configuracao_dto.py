"""
DTOs para validação de configurações do sistema.

Cada categoria de configuração tem validações específicas para prevenir
valores perigosos ou inválidos.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ConfiguracaoBaseDTO(BaseModel):
    """DTO base para configurações"""
    chave: str = Field(..., description="Chave única da configuração em snake_case")
    valor: str = Field(..., description="Valor da configuração")
    descricao: Optional[str] = Field(default="", description="Descrição opcional da configuração")


class ConfiguracaoAplicacaoDTO(BaseModel):
    """DTO para configurações de aplicação (nome, email, etc)"""
    app_name: Optional[str] = Field(default=None, description="Nome da aplicação exibido na interface")
    resend_from_email: Optional[str] = Field(default=None, description="Email remetente para envio de notificações")
    resend_from_name: Optional[str] = Field(default=None, description="Nome exibido como remetente dos emails")

    @field_validator('resend_from_email')
    @classmethod
    def validar_email(cls, v):
        if v is None:
            return v
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Email inválido')
        return v


class ConfiguracaoFotosDTO(BaseModel):
    """DTO para configurações de fotos"""
    foto_perfil_tamanho_max: Optional[int] = Field(default=None, description="Tamanho máximo da foto de perfil em pixels (64-2048)")
    foto_max_upload_bytes: Optional[int] = Field(default=None, description="Tamanho máximo de upload de foto em bytes (100KB-50MB)")

    @field_validator('foto_perfil_tamanho_max')
    @classmethod
    def validar_tamanho_foto(cls, v):
        if v is not None:
            if v < 64:
                raise ValueError('Tamanho mínimo é 64 pixels')
            if v > 2048:
                raise ValueError('Tamanho máximo é 2048 pixels')
            if v % 2 != 0:
                raise ValueError('Tamanho deve ser número par de pixels')
        return v

    @field_validator('foto_max_upload_bytes')
    @classmethod
    def validar_max_upload(cls, v):
        if v is not None:
            if v < 102400:
                raise ValueError('Tamanho mínimo de upload é 100KB (102400 bytes)')
            if v > 52428800:
                raise ValueError('Tamanho máximo de upload é 50MB (52428800 bytes)')
        return v


class ConfiguracaoRateLimitDTO(BaseModel):
    """DTO genérico para configurações de rate limiting"""
    max_tentativas: int = Field(..., description="Máximo de tentativas permitidas")
    minutos: int = Field(..., description="Período em minutos (máx 24h)")

    @field_validator('max_tentativas')
    @classmethod
    def validar_max_tentativas(cls, v):
        if v < 1:
            raise ValueError('Deve permitir pelo menos 1 tentativa')
        if v > 1000:
            raise ValueError('Limite muito alto (máximo 1000)')
        return v

    @field_validator('minutos')
    @classmethod
    def validar_minutos(cls, v):
        if v < 1:
            raise ValueError('Período deve ser pelo menos 1 minuto')
        if v > 1440:  # 24 horas
            raise ValueError('Período máximo é 24 horas (1440 minutos)')
        return v


class ConfiguracaoRateLimitLoginDTO(ConfiguracaoRateLimitDTO):
    """DTO específico para rate limit de login (validações mais restritas)"""
    max_tentativas: int = Field(..., description="Tentativas de login (3-20)")
    minutos: int = Field(..., description="Período em minutos (1-60)")

    @field_validator('max_tentativas')
    @classmethod
    def validar_max_tentativas_login(cls, v):
        if v < 3:
            raise ValueError('Login deve permitir pelo menos 3 tentativas')
        if v > 20:
            raise ValueError('Login não deve permitir mais que 20 tentativas')
        return v

    @field_validator('minutos')
    @classmethod
    def validar_minutos_login(cls, v):
        if v < 1:
            raise ValueError('Período deve ser pelo menos 1 minuto')
        if v > 60:
            raise ValueError('Período de login não deve exceder 60 minutos')
        return v


class ConfiguracaoRateLimitCadastroDTO(ConfiguracaoRateLimitDTO):
    """DTO específico para rate limit de cadastro"""
    max_tentativas: int = Field(..., description="Tentativas de cadastro (1-10)")
    minutos: int = Field(..., description="Período em minutos (5-120)")

    @field_validator('max_tentativas')
    @classmethod
    def validar_max_tentativas_cadastro(cls, v):
        if v < 1:
            raise ValueError('Cadastro deve permitir pelo menos 1 tentativa')
        if v > 10:
            raise ValueError('Cadastro não deve permitir mais que 10 tentativas')
        return v

    @field_validator('minutos')
    @classmethod
    def validar_minutos_cadastro(cls, v):
        if v < 5:
            raise ValueError('Período de cadastro deve ser pelo menos 5 minutos')
        if v > 120:
            raise ValueError('Período de cadastro não deve exceder 120 minutos')
        return v


class ConfiguracaoRateLimitSenhaDTO(ConfiguracaoRateLimitDTO):
    """DTO específico para rate limit de recuperação/alteração de senha"""
    max_tentativas: int = Field(..., description="Tentativas (1-10)")
    minutos: int = Field(..., description="Período em minutos (1-60)")

    @field_validator('max_tentativas')
    @classmethod
    def validar_max_tentativas_senha(cls, v):
        if v < 1:
            raise ValueError('Deve permitir pelo menos 1 tentativa')
        if v > 10:
            raise ValueError('Senha não deve permitir mais que 10 tentativas')
        return v

    @field_validator('minutos')
    @classmethod
    def validar_minutos_senha(cls, v):
        if v < 1:
            raise ValueError('Período deve ser pelo menos 1 minuto')
        if v > 60:
            raise ValueError('Período de senha não deve exceder 60 minutos')
        return v


class ConfiguracaoUIDTO(BaseModel):
    """DTO para configurações de interface"""
    toast_auto_hide_delay_ms: Optional[int] = Field(default=None, description="Tempo de exibição das notificações toast em milissegundos (1000-30000)")

    @field_validator('toast_auto_hide_delay_ms')
    @classmethod
    def validar_delay(cls, v):
        if v is not None:
            if v < 1000:
                raise ValueError('Delay mínimo é 1000ms (1 segundo)')
            if v > 30000:
                raise ValueError('Delay máximo é 30000ms (30 segundos)')
        return v


class EditarConfiguracaoDTO(BaseModel):
    """DTO para edição de uma configuração individual"""
    chave: str = Field(..., description="Chave única da configuração em snake_case")
    valor: str = Field(..., description="Novo valor da configuração")

    @field_validator('valor')
    @classmethod
    def validar_valor_nao_vazio(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Valor não pode ser vazio')
        return v.strip()

    @field_validator('chave')
    @classmethod
    def validar_chave_formato(cls, v):
        """Valida que a chave segue o padrão snake_case"""
        import re
        if not re.match(r'^[a-z][a-z0-9_]*$', v):
            raise ValueError('Chave deve estar em snake_case (apenas letras minúsculas, números e underscore)')
        return v


class ValidarRateLimitDTO(BaseModel):
    """DTO para validação de qualquer par max/minutos de rate limit"""
    max_tentativas: str = Field(..., description="Máximo de tentativas")
    minutos: str = Field(..., description="Período em minutos")

    @field_validator('max_tentativas', 'minutos')
    @classmethod
    def validar_numerico(cls, v, info):
        """Valida que os valores são números inteiros positivos"""
        try:
            num = int(v)
            if num < 1:
                raise ValueError(f'{info.field_name} deve ser pelo menos 1')
            if info.field_name == 'max_tentativas' and num > 1000:
                raise ValueError('Máximo de tentativas não pode exceder 1000')
            if info.field_name == 'minutos' and num > 1440:
                raise ValueError('Período não pode exceder 1440 minutos (24 horas)')
            return v
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f'{info.field_name} deve ser um número inteiro')
            raise


class SalvarConfiguracaoLoteDTO(BaseModel):
    """
    DTO para salvamento em lote de configurações.

    Recebe um dicionário de {chave: valor} e valida cada par
    de acordo com regras específicas baseadas na chave.

    Example:
        {
            "rate_limit_login_max": "5",
            "rate_limit_login_minutos": "5",
            "app_name": "Meu Sistema",
            "toast_auto_hide_delay_ms": "5000"
        }
    """
    configs: dict[str, str] = Field(..., description="Dicionário de configurações")

    @field_validator('configs')
    @classmethod
    def validar_configs(cls, v):
        """Valida cada configuração individualmente"""
        if not v:
            raise ValueError('Deve fornecer pelo menos uma configuração')

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
                if chave.endswith('_max'):
                    num = int(valor)
                    if num < 1:
                        erros[chave] = "Deve ser pelo menos 1"
                    elif num > 1000:
                        erros[chave] = "Máximo permitido é 1000"

                elif chave.endswith('_minutos'):
                    num = int(valor)
                    if num < 1:
                        erros[chave] = "Deve ser pelo menos 1 minuto"
                    elif num > 1440:
                        erros[chave] = "Máximo permitido é 1440 minutos (24 horas)"

                # Toast delay
                elif chave == 'toast_auto_hide_delay_ms':
                    num = int(valor)
                    if num < 1000:
                        erros[chave] = "Mínimo é 1000ms (1 segundo)"
                    elif num > 30000:
                        erros[chave] = "Máximo é 30000ms (30 segundos)"

                # Foto perfil tamanho
                elif chave == 'foto_perfil_tamanho_max':
                    num = int(valor)
                    if num < 64:
                        erros[chave] = "Mínimo é 64 pixels"
                    elif num > 2048:
                        erros[chave] = "Máximo é 2048 pixels"

                # Foto upload bytes
                elif chave == 'foto_max_upload_bytes':
                    num = int(valor)
                    if num < 102400:  # 100KB
                        erros[chave] = "Mínimo é 100KB (102400 bytes)"
                    elif num > 52428800:  # 50MB
                        erros[chave] = "Máximo é 50MB (52428800 bytes)"

                # Email
                elif chave == 'resend_from_email':
                    import re
                    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(pattern, valor):
                        erros[chave] = "Email inválido"

                # Strings gerais (app_name, resend_from_name, etc)
                elif chave in ['app_name', 'resend_from_name']:
                    if len(valor) > 200:
                        erros[chave] = "Máximo de 200 caracteres"

            except ValueError:
                erros[chave] = "Valor deve ser um número válido"

        # Se houver erros, levantar exceção com detalhes
        if erros:
            erro_msg = "; ".join([f"{k}: {v}" for k, v in erros.items()])
            raise ValueError(f"Erros de validação encontrados: {erro_msg}")

        return v
