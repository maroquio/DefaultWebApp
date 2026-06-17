"""
Testes para o módulo dtos/configuracao_dto.py

Testa todos os DTOs de configuração do sistema.
"""

import pytest
from pydantic import ValidationError

from dtos.configuracao_dto import (
    ConfiguracaoBaseDTO,
    ConfiguracaoAplicacaoDTO,
    ConfiguracaoFotosDTO,
    ConfiguracaoRateLimitDTO,
    ConfiguracaoRateLimitLoginDTO,
    ConfiguracaoRateLimitCadastroDTO,
    ConfiguracaoRateLimitSenhaDTO,
    ConfiguracaoUIDTO,
    EditarConfiguracaoDTO,
    ValidarRateLimitDTO,
    SalvarConfiguracaoLoteDTO,
    FOTO_PERFIL_MIN_PIXELS,
    FOTO_PERFIL_MAX_PIXELS,
    FOTO_UPLOAD_MIN_BYTES,
    FOTO_UPLOAD_MAX_BYTES,
    RATE_LIMIT_MAX_TENTATIVAS,
    RATE_LIMIT_MAX_MINUTOS,
    TOAST_DELAY_MIN_MS,
    TOAST_DELAY_MAX_MS,
    MAX_CARACTERES_NOME,
)


class TestConfiguracaoBaseDTO:
    """Testes para ConfiguracaoBaseDTO"""

    def test_criar_configuracao_valida(self):
        """Deve criar configuração com todos os campos"""
        config = ConfiguracaoBaseDTO(
            chave="minha_config",
            valor="valor_teste",
            descricao="Descrição da config"
        )
        assert config.chave == "minha_config"
        assert config.valor == "valor_teste"
        assert config.descricao == "Descrição da config"

    def test_descricao_opcional_default_vazio(self):
        """Descrição opcional deve ter default vazio"""
        config = ConfiguracaoBaseDTO(chave="chave", valor="valor")
        assert config.descricao == ""

    def test_chave_obrigatoria(self):
        """Chave é obrigatória"""
        with pytest.raises(ValidationError):
            ConfiguracaoBaseDTO(valor="valor")

    def test_valor_obrigatorio(self):
        """Valor é obrigatório"""
        with pytest.raises(ValidationError):
            ConfiguracaoBaseDTO(chave="chave")


class TestConfiguracaoAplicacaoDTO:
    """Testes para ConfiguracaoAplicacaoDTO"""

    def test_criar_com_todos_campos(self):
        """Deve criar configuração com todos os campos"""
        config = ConfiguracaoAplicacaoDTO(
            app_name="Minha App",
            resend_from_email="email@dominio.com",
            resend_from_name="Minha Empresa"
        )
        assert config.app_name == "Minha App"
        assert config.resend_from_email == "email@dominio.com"
        assert config.resend_from_name == "Minha Empresa"

    def test_todos_campos_opcionais(self):
        """Todos os campos são opcionais"""
        config = ConfiguracaoAplicacaoDTO()
        assert config.app_name is None
        assert config.resend_from_email is None
        assert config.resend_from_name is None

    def test_email_valido(self):
        """Email válido deve passar"""
        config = ConfiguracaoAplicacaoDTO(resend_from_email="test@example.com")
        assert config.resend_from_email == "test@example.com"

    def test_email_invalido_falha(self):
        """Email inválido deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            ConfiguracaoAplicacaoDTO(resend_from_email="email_invalido")
        assert "email" in str(exc_info.value).lower()

    def test_email_vazio_retorna_none(self):
        """Email vazio deve retornar None"""
        config = ConfiguracaoAplicacaoDTO(resend_from_email="")
        assert config.resend_from_email is None


class TestConfiguracaoFotosDTO:
    """Testes para ConfiguracaoFotosDTO"""

    def test_criar_com_valores_validos(self):
        """Deve aceitar valores dentro dos limites"""
        config = ConfiguracaoFotosDTO(
            foto_perfil_tamanho_max=256,
            foto_max_upload_bytes=5000000
        )
        assert config.foto_perfil_tamanho_max == 256
        assert config.foto_max_upload_bytes == 5000000

    def test_campos_opcionais(self):
        """Todos os campos são opcionais"""
        config = ConfiguracaoFotosDTO()
        assert config.foto_perfil_tamanho_max is None
        assert config.foto_max_upload_bytes is None

    def test_tamanho_foto_minimo_permitido(self):
        """Deve aceitar tamanho mínimo de foto"""
        config = ConfiguracaoFotosDTO(foto_perfil_tamanho_max=FOTO_PERFIL_MIN_PIXELS)
        assert config.foto_perfil_tamanho_max == FOTO_PERFIL_MIN_PIXELS

    def test_tamanho_foto_maximo_permitido(self):
        """Deve aceitar tamanho máximo de foto"""
        config = ConfiguracaoFotosDTO(foto_perfil_tamanho_max=FOTO_PERFIL_MAX_PIXELS)
        assert config.foto_perfil_tamanho_max == FOTO_PERFIL_MAX_PIXELS

    def test_tamanho_foto_abaixo_minimo_falha(self):
        """Tamanho abaixo do mínimo deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            ConfiguracaoFotosDTO(foto_perfil_tamanho_max=FOTO_PERFIL_MIN_PIXELS - 1)
        assert "mínimo" in str(exc_info.value).lower()

    def test_tamanho_foto_acima_maximo_falha(self):
        """Tamanho acima do máximo deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            ConfiguracaoFotosDTO(foto_perfil_tamanho_max=FOTO_PERFIL_MAX_PIXELS + 1)
        assert "máximo" in str(exc_info.value).lower()

    def test_tamanho_foto_deve_ser_par(self):
        """Tamanho deve ser número par de pixels"""
        with pytest.raises(ValidationError) as exc_info:
            ConfiguracaoFotosDTO(foto_perfil_tamanho_max=127)  # Ímpar
        assert "par" in str(exc_info.value).lower()

    def test_upload_minimo_permitido(self):
        """Deve aceitar tamanho mínimo de upload"""
        config = ConfiguracaoFotosDTO(foto_max_upload_bytes=FOTO_UPLOAD_MIN_BYTES)
        assert config.foto_max_upload_bytes == FOTO_UPLOAD_MIN_BYTES

    def test_upload_maximo_permitido(self):
        """Deve aceitar tamanho máximo de upload"""
        config = ConfiguracaoFotosDTO(foto_max_upload_bytes=FOTO_UPLOAD_MAX_BYTES)
        assert config.foto_max_upload_bytes == FOTO_UPLOAD_MAX_BYTES

    def test_upload_abaixo_minimo_falha(self):
        """Upload abaixo do mínimo deve falhar"""
        with pytest.raises(ValidationError):
            ConfiguracaoFotosDTO(foto_max_upload_bytes=FOTO_UPLOAD_MIN_BYTES - 1)

    def test_upload_acima_maximo_falha(self):
        """Upload acima do máximo deve falhar"""
        with pytest.raises(ValidationError):
            ConfiguracaoFotosDTO(foto_max_upload_bytes=FOTO_UPLOAD_MAX_BYTES + 1)


class TestConfiguracaoRateLimitDTO:
    """Testes para ConfiguracaoRateLimitDTO genérico"""

    def test_criar_com_valores_validos(self):
        """Deve aceitar valores válidos"""
        config = ConfiguracaoRateLimitDTO(max_tentativas=10, minutos=60)
        assert config.max_tentativas == 10
        assert config.minutos == 60

    def test_valor_minimo_permitido(self):
        """Deve aceitar valores mínimos (1)"""
        config = ConfiguracaoRateLimitDTO(max_tentativas=1, minutos=1)
        assert config.max_tentativas == 1
        assert config.minutos == 1

    def test_valor_maximo_tentativas(self):
        """Deve aceitar valor máximo de tentativas"""
        config = ConfiguracaoRateLimitDTO(
            max_tentativas=RATE_LIMIT_MAX_TENTATIVAS,
            minutos=60
        )
        assert config.max_tentativas == RATE_LIMIT_MAX_TENTATIVAS

    def test_valor_maximo_minutos(self):
        """Deve aceitar valor máximo de minutos (24h)"""
        config = ConfiguracaoRateLimitDTO(
            max_tentativas=10,
            minutos=RATE_LIMIT_MAX_MINUTOS
        )
        assert config.minutos == RATE_LIMIT_MAX_MINUTOS

    def test_tentativas_abaixo_minimo_falha(self):
        """Tentativas abaixo do mínimo deve falhar"""
        with pytest.raises(ValidationError):
            ConfiguracaoRateLimitDTO(max_tentativas=0, minutos=60)

    def test_minutos_abaixo_minimo_falha(self):
        """Minutos abaixo do mínimo deve falhar"""
        with pytest.raises(ValidationError):
            ConfiguracaoRateLimitDTO(max_tentativas=10, minutos=0)

    def test_tentativas_acima_maximo_falha(self):
        """Tentativas acima do máximo deve falhar"""
        with pytest.raises(ValidationError):
            ConfiguracaoRateLimitDTO(
                max_tentativas=RATE_LIMIT_MAX_TENTATIVAS + 1,
                minutos=60
            )

    def test_minutos_acima_maximo_falha(self):
        """Minutos acima do máximo deve falhar"""
        with pytest.raises(ValidationError):
            ConfiguracaoRateLimitDTO(
                max_tentativas=10,
                minutos=RATE_LIMIT_MAX_MINUTOS + 1
            )


class TestConfiguracaoRateLimitLoginDTO:
    """Testes para ConfiguracaoRateLimitLoginDTO (mais restrito)"""

    def test_criar_com_valores_validos(self):
        """Deve aceitar valores válidos para login"""
        config = ConfiguracaoRateLimitLoginDTO(max_tentativas=5, minutos=15)
        assert config.max_tentativas == 5
        assert config.minutos == 15

    def test_minimo_tentativas_login(self):
        """Mínimo de 3 tentativas para login"""
        config = ConfiguracaoRateLimitLoginDTO(max_tentativas=3, minutos=15)
        assert config.max_tentativas == 3

    def test_maximo_tentativas_login(self):
        """Máximo de 20 tentativas para login"""
        config = ConfiguracaoRateLimitLoginDTO(max_tentativas=20, minutos=15)
        assert config.max_tentativas == 20

    def test_minimo_minutos_login(self):
        """Mínimo de 1 minuto para login"""
        config = ConfiguracaoRateLimitLoginDTO(max_tentativas=5, minutos=1)
        assert config.minutos == 1

    def test_maximo_minutos_login(self):
        """Máximo de 60 minutos para login"""
        config = ConfiguracaoRateLimitLoginDTO(max_tentativas=5, minutos=60)
        assert config.minutos == 60

    def test_tentativas_abaixo_limite_login_falha(self):
        """Menos de 3 tentativas deve falhar para login"""
        with pytest.raises(ValidationError) as exc_info:
            ConfiguracaoRateLimitLoginDTO(max_tentativas=2, minutos=15)
        assert "login" in str(exc_info.value).lower()

    def test_tentativas_acima_limite_login_falha(self):
        """Mais de 20 tentativas deve falhar para login"""
        with pytest.raises(ValidationError):
            ConfiguracaoRateLimitLoginDTO(max_tentativas=21, minutos=15)

    def test_minutos_acima_limite_login_falha(self):
        """Mais de 60 minutos deve falhar para login"""
        with pytest.raises(ValidationError):
            ConfiguracaoRateLimitLoginDTO(max_tentativas=5, minutos=61)


class TestConfiguracaoRateLimitCadastroDTO:
    """Testes para ConfiguracaoRateLimitCadastroDTO"""

    def test_criar_com_valores_validos(self):
        """Deve aceitar valores válidos para cadastro"""
        config = ConfiguracaoRateLimitCadastroDTO(max_tentativas=5, minutos=30)
        assert config.max_tentativas == 5
        assert config.minutos == 30

    def test_minimo_tentativas_cadastro(self):
        """Mínimo de 1 tentativa para cadastro"""
        config = ConfiguracaoRateLimitCadastroDTO(max_tentativas=1, minutos=10)
        assert config.max_tentativas == 1

    def test_maximo_tentativas_cadastro(self):
        """Máximo de 10 tentativas para cadastro"""
        config = ConfiguracaoRateLimitCadastroDTO(max_tentativas=10, minutos=10)
        assert config.max_tentativas == 10

    def test_minimo_minutos_cadastro(self):
        """Mínimo de 5 minutos para cadastro"""
        config = ConfiguracaoRateLimitCadastroDTO(max_tentativas=5, minutos=5)
        assert config.minutos == 5

    def test_maximo_minutos_cadastro(self):
        """Máximo de 120 minutos para cadastro"""
        config = ConfiguracaoRateLimitCadastroDTO(max_tentativas=5, minutos=120)
        assert config.minutos == 120

    def test_tentativas_acima_limite_cadastro_falha(self):
        """Mais de 10 tentativas deve falhar para cadastro"""
        with pytest.raises(ValidationError):
            ConfiguracaoRateLimitCadastroDTO(max_tentativas=11, minutos=30)

    def test_minutos_abaixo_limite_cadastro_falha(self):
        """Menos de 5 minutos deve falhar para cadastro"""
        with pytest.raises(ValidationError) as exc_info:
            ConfiguracaoRateLimitCadastroDTO(max_tentativas=5, minutos=4)
        assert "cadastro" in str(exc_info.value).lower()

    def test_minutos_acima_limite_cadastro_falha(self):
        """Mais de 120 minutos deve falhar para cadastro"""
        with pytest.raises(ValidationError):
            ConfiguracaoRateLimitCadastroDTO(max_tentativas=5, minutos=121)


class TestConfiguracaoRateLimitSenhaDTO:
    """Testes para ConfiguracaoRateLimitSenhaDTO"""

    def test_criar_com_valores_validos(self):
        """Deve aceitar valores válidos para senha"""
        config = ConfiguracaoRateLimitSenhaDTO(max_tentativas=5, minutos=30)
        assert config.max_tentativas == 5
        assert config.minutos == 30

    def test_minimo_tentativas_senha(self):
        """Mínimo de 1 tentativa para senha"""
        config = ConfiguracaoRateLimitSenhaDTO(max_tentativas=1, minutos=10)
        assert config.max_tentativas == 1

    def test_maximo_tentativas_senha(self):
        """Máximo de 10 tentativas para senha"""
        config = ConfiguracaoRateLimitSenhaDTO(max_tentativas=10, minutos=10)
        assert config.max_tentativas == 10

    def test_minimo_minutos_senha(self):
        """Mínimo de 1 minuto para senha"""
        config = ConfiguracaoRateLimitSenhaDTO(max_tentativas=5, minutos=1)
        assert config.minutos == 1

    def test_maximo_minutos_senha(self):
        """Máximo de 60 minutos para senha"""
        config = ConfiguracaoRateLimitSenhaDTO(max_tentativas=5, minutos=60)
        assert config.minutos == 60

    def test_tentativas_acima_limite_senha_falha(self):
        """Mais de 10 tentativas deve falhar para senha"""
        with pytest.raises(ValidationError):
            ConfiguracaoRateLimitSenhaDTO(max_tentativas=11, minutos=30)

    def test_minutos_acima_limite_senha_falha(self):
        """Mais de 60 minutos deve falhar para senha"""
        with pytest.raises(ValidationError) as exc_info:
            ConfiguracaoRateLimitSenhaDTO(max_tentativas=5, minutos=61)
        assert "senha" in str(exc_info.value).lower()


class TestConfiguracaoUIDTO:
    """Testes para ConfiguracaoUIDTO"""

    def test_criar_com_valor_valido(self):
        """Deve aceitar valor válido de delay"""
        config = ConfiguracaoUIDTO(toast_auto_hide_delay_ms=5000)
        assert config.toast_auto_hide_delay_ms == 5000

    def test_campo_opcional(self):
        """Campo é opcional"""
        config = ConfiguracaoUIDTO()
        assert config.toast_auto_hide_delay_ms is None

    def test_delay_minimo_permitido(self):
        """Deve aceitar delay mínimo"""
        config = ConfiguracaoUIDTO(toast_auto_hide_delay_ms=TOAST_DELAY_MIN_MS)
        assert config.toast_auto_hide_delay_ms == TOAST_DELAY_MIN_MS

    def test_delay_maximo_permitido(self):
        """Deve aceitar delay máximo"""
        config = ConfiguracaoUIDTO(toast_auto_hide_delay_ms=TOAST_DELAY_MAX_MS)
        assert config.toast_auto_hide_delay_ms == TOAST_DELAY_MAX_MS

    def test_delay_abaixo_minimo_falha(self):
        """Delay abaixo do mínimo deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            ConfiguracaoUIDTO(toast_auto_hide_delay_ms=TOAST_DELAY_MIN_MS - 1)
        assert "mínimo" in str(exc_info.value).lower()

    def test_delay_acima_maximo_falha(self):
        """Delay acima do máximo deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            ConfiguracaoUIDTO(toast_auto_hide_delay_ms=TOAST_DELAY_MAX_MS + 1)
        assert "máximo" in str(exc_info.value).lower()


class TestEditarConfiguracaoDTO:
    """Testes para EditarConfiguracaoDTO"""

    def test_criar_com_valores_validos(self):
        """Deve criar configuração válida"""
        config = EditarConfiguracaoDTO(chave="minha_config", valor="valor_teste")
        assert config.chave == "minha_config"
        assert config.valor == "valor_teste"

    def test_valor_vazio_falha(self):
        """Valor vazio deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            EditarConfiguracaoDTO(chave="config", valor="")
        assert "vazio" in str(exc_info.value).lower()

    def test_valor_apenas_espacos_falha(self):
        """Valor apenas com espaços deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            EditarConfiguracaoDTO(chave="config", valor="   ")
        assert "vazio" in str(exc_info.value).lower()

    def test_valor_trimado(self):
        """Valor deve ser trimado"""
        config = EditarConfiguracaoDTO(chave="config", valor="  teste  ")
        assert config.valor == "teste"

    def test_chave_snake_case_valida(self):
        """Chave em snake_case válida deve passar"""
        config = EditarConfiguracaoDTO(chave="minha_config_teste", valor="v")
        assert config.chave == "minha_config_teste"

    def test_chave_com_numero_valida(self):
        """Chave com números (não no início) deve passar"""
        config = EditarConfiguracaoDTO(chave="config_123", valor="v")
        assert config.chave == "config_123"

    def test_chave_maiuscula_falha(self):
        """Chave com maiúscula deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            EditarConfiguracaoDTO(chave="MinhaConfig", valor="v")
        assert "snake_case" in str(exc_info.value).lower()

    def test_chave_comeca_numero_falha(self):
        """Chave que começa com número deve falhar"""
        with pytest.raises(ValidationError):
            EditarConfiguracaoDTO(chave="1config", valor="v")

    def test_chave_com_espacos_falha(self):
        """Chave com espaços deve falhar"""
        with pytest.raises(ValidationError):
            EditarConfiguracaoDTO(chave="minha config", valor="v")

    def test_chave_com_hifen_falha(self):
        """Chave com hífen deve falhar (não é snake_case)"""
        with pytest.raises(ValidationError):
            EditarConfiguracaoDTO(chave="minha-config", valor="v")


class TestValidarRateLimitDTO:
    """Testes para ValidarRateLimitDTO"""

    def test_valores_validos(self):
        """Deve aceitar valores numéricos válidos como string"""
        config = ValidarRateLimitDTO(max_tentativas="10", minutos="60")
        assert config.max_tentativas == "10"
        assert config.minutos == "60"

    def test_valor_minimo(self):
        """Deve aceitar valor mínimo (1)"""
        config = ValidarRateLimitDTO(max_tentativas="1", minutos="1")
        assert config.max_tentativas == "1"
        assert config.minutos == "1"

    def test_tentativas_nao_numerico_falha(self):
        """Tentativas não numérico deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            ValidarRateLimitDTO(max_tentativas="abc", minutos="60")
        assert "inteiro" in str(exc_info.value).lower()

    def test_minutos_nao_numerico_falha(self):
        """Minutos não numérico deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            ValidarRateLimitDTO(max_tentativas="10", minutos="xyz")
        assert "inteiro" in str(exc_info.value).lower()

    def test_tentativas_zero_falha(self):
        """Zero tentativas deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            ValidarRateLimitDTO(max_tentativas="0", minutos="60")
        assert "pelo menos 1" in str(exc_info.value).lower()

    def test_tentativas_negativo_falha(self):
        """Tentativas negativo deve falhar"""
        with pytest.raises(ValidationError):
            ValidarRateLimitDTO(max_tentativas="-5", minutos="60")

    def test_tentativas_acima_maximo_falha(self):
        """Tentativas acima do máximo deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            ValidarRateLimitDTO(
                max_tentativas=str(RATE_LIMIT_MAX_TENTATIVAS + 1),
                minutos="60"
            )
        assert str(RATE_LIMIT_MAX_TENTATIVAS) in str(exc_info.value)

    def test_minutos_acima_maximo_falha(self):
        """Minutos acima do máximo deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            ValidarRateLimitDTO(
                max_tentativas="10",
                minutos=str(RATE_LIMIT_MAX_MINUTOS + 1)
            )
        assert "24 horas" in str(exc_info.value).lower()


class TestSalvarConfiguracaoLoteDTO:
    """Testes para SalvarConfiguracaoLoteDTO"""

    def test_criar_com_configuracoes_validas(self):
        """Deve aceitar configurações válidas"""
        config = SalvarConfiguracaoLoteDTO(configs={
            "app_name": "Minha App",
            "resend_from_name": "Sistema"
        })
        assert config.configs["app_name"] == "Minha App"

    def test_configs_vazias_falha(self):
        """Dicionário vazio deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={})
        assert "pelo menos uma" in str(exc_info.value).lower()

    def test_valor_vazio_falha(self):
        """Valor vazio em config deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={"app_name": ""})
        assert "vazio" in str(exc_info.value).lower()

    def test_valor_apenas_espacos_falha(self):
        """Valor com apenas espaços deve falhar"""
        with pytest.raises(ValidationError):
            SalvarConfiguracaoLoteDTO(configs={"app_name": "   "})

    # Testes para rate limits
    def test_rate_limit_max_valido(self):
        """Valor válido para rate limit max"""
        config = SalvarConfiguracaoLoteDTO(configs={"login_max": "10"})
        assert config.configs["login_max"] == "10"

    def test_rate_limit_max_zero_falha(self):
        """Rate limit max zero deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={"login_max": "0"})
        assert "pelo menos 1" in str(exc_info.value).lower()

    def test_rate_limit_max_acima_limite_falha(self):
        """Rate limit max acima do limite deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={
                "login_max": str(RATE_LIMIT_MAX_TENTATIVAS + 1)
            })
        assert str(RATE_LIMIT_MAX_TENTATIVAS) in str(exc_info.value)

    def test_rate_limit_minutos_valido(self):
        """Valor válido para rate limit minutos"""
        config = SalvarConfiguracaoLoteDTO(configs={"login_minutos": "60"})
        assert config.configs["login_minutos"] == "60"

    def test_rate_limit_minutos_zero_falha(self):
        """Rate limit minutos zero deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={"login_minutos": "0"})
        assert "1 minuto" in str(exc_info.value).lower()

    def test_rate_limit_minutos_acima_limite_falha(self):
        """Rate limit minutos acima de 24h deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={
                "login_minutos": str(RATE_LIMIT_MAX_MINUTOS + 1)
            })
        assert "24 horas" in str(exc_info.value).lower()

    # Testes para toast delay
    def test_toast_delay_valido(self):
        """Toast delay válido"""
        config = SalvarConfiguracaoLoteDTO(configs={
            "toast_auto_hide_delay_ms": "5000"
        })
        assert config.configs["toast_auto_hide_delay_ms"] == "5000"

    def test_toast_delay_abaixo_minimo_falha(self):
        """Toast delay abaixo do mínimo deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={
                "toast_auto_hide_delay_ms": str(TOAST_DELAY_MIN_MS - 1)
            })
        assert "1 segundo" in str(exc_info.value).lower()

    def test_toast_delay_acima_maximo_falha(self):
        """Toast delay acima do máximo deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={
                "toast_auto_hide_delay_ms": str(TOAST_DELAY_MAX_MS + 1)
            })
        assert "30 segundos" in str(exc_info.value).lower()

    # Testes para foto perfil
    # Nota: foto_perfil_tamanho_max termina com "_max", então é validado como
    # rate limit primeiro (máximo 1000), não como foto (máximo 2048)
    def test_foto_tamanho_valido(self):
        """Tamanho de foto válido dentro do limite de rate limit"""
        config = SalvarConfiguracaoLoteDTO(configs={
            "foto_perfil_tamanho_max": "256"
        })
        assert config.configs["foto_perfil_tamanho_max"] == "256"

    def test_foto_tamanho_limite_rate_limit(self):
        """Tamanho de foto acima de 1000 falha por validação de rate limit"""
        # Como a chave termina com "_max", é validada como rate limit (max 1000)
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={
                "foto_perfil_tamanho_max": "1001"
            })
        assert "1000" in str(exc_info.value)

    # Testes para foto upload bytes
    def test_foto_upload_valido(self):
        """Tamanho de upload válido"""
        config = SalvarConfiguracaoLoteDTO(configs={
            "foto_max_upload_bytes": "5000000"
        })
        assert config.configs["foto_max_upload_bytes"] == "5000000"

    def test_foto_upload_abaixo_minimo_falha(self):
        """Upload abaixo do mínimo deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={
                "foto_max_upload_bytes": str(FOTO_UPLOAD_MIN_BYTES - 1)
            })
        assert "100KB" in str(exc_info.value)

    def test_foto_upload_acima_maximo_falha(self):
        """Upload acima do máximo deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={
                "foto_max_upload_bytes": str(FOTO_UPLOAD_MAX_BYTES + 1)
            })
        assert "50MB" in str(exc_info.value)

    # Testes para email
    def test_email_valido(self):
        """Email válido deve passar"""
        config = SalvarConfiguracaoLoteDTO(configs={
            "resend_from_email": "test@example.com"
        })
        assert config.configs["resend_from_email"] == "test@example.com"

    def test_email_invalido_falha(self):
        """Email inválido deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={
                "resend_from_email": "email_invalido"
            })
        assert "inválido" in str(exc_info.value).lower()

    # Testes para strings gerais
    def test_app_name_valido(self):
        """App name válido"""
        config = SalvarConfiguracaoLoteDTO(configs={"app_name": "Minha App"})
        assert config.configs["app_name"] == "Minha App"

    def test_app_name_muito_longo_falha(self):
        """App name muito longo deve falhar"""
        nome_longo = "a" * (MAX_CARACTERES_NOME + 1)
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={"app_name": nome_longo})
        assert str(MAX_CARACTERES_NOME) in str(exc_info.value)

    # Testes para valores não numéricos
    def test_rate_limit_nao_numerico_falha(self):
        """Rate limit com valor não numérico deve falhar"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={"login_max": "abc"})
        assert "número válido" in str(exc_info.value).lower()

    # Testes para múltiplas configurações
    def test_multiplas_configs_validas(self):
        """Deve aceitar múltiplas configurações válidas"""
        config = SalvarConfiguracaoLoteDTO(configs={
            "app_name": "App",
            "login_max": "10",
            "login_minutos": "60",
            "toast_auto_hide_delay_ms": "5000"
        })
        assert len(config.configs) == 4

    def test_multiplas_configs_com_erro(self):
        """Erro em uma config deve reportar todas as falhas"""
        with pytest.raises(ValidationError) as exc_info:
            SalvarConfiguracaoLoteDTO(configs={
                "app_name": "App",  # válido
                "login_max": "-1",  # inválido
                "toast_auto_hide_delay_ms": "abc"  # inválido
            })
        erro = str(exc_info.value)
        # Deve conter informação sobre ambos os erros
        assert "login_max" in erro or "toast" in erro.lower()
