"""
Módulo de configurações centralizadas da aplicação.

Carrega e disponibiliza todas as variáveis de ambiente e configurações
do sistema em um único local, facilitando a manutenção e evitando duplicação.
"""
import os
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# === Configurações da Aplicação ===
APP_NAME = os.getenv("APP_NAME", "Sistema Web")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-super-segura-mude-isso-em-producao")

# === Validação de Segurança ===
# Verifica se SECRET_KEY padrão está sendo usada em produção
RUNNING_MODE_CHECK = os.getenv("RUNNING_MODE", "Production")
if RUNNING_MODE_CHECK.lower() != "development":
    # Validação 1: Não pode usar a chave padrão
    if SECRET_KEY == "sua-chave-secreta-super-segura-mude-isso-em-producao":
        raise ValueError(
            "SEGURANÇA CRÍTICA: SECRET_KEY padrão não pode ser usada em produção!\n"
            "Configure uma chave secreta forte no arquivo .env:\n"
            "SECRET_KEY=sua-chave-aleatoria-gerada-aqui\n"
            "Você pode gerar uma com: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )

    # Validação 2: Tamanho mínimo de 32 caracteres para segurança adequada
    # (32 chars = 256 bits de entropia, recomendado para HMAC/sessões)
    MIN_SECRET_KEY_LENGTH = 32
    if len(SECRET_KEY) < MIN_SECRET_KEY_LENGTH:
        raise ValueError(
            f"SEGURANÇA CRÍTICA: SECRET_KEY muito curta ({len(SECRET_KEY)} caracteres)!\n"
            f"Em produção, SECRET_KEY deve ter no mínimo {MIN_SECRET_KEY_LENGTH} caracteres.\n"
            "Você pode gerar uma chave segura com:\n"
            "  python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )

# === Configurações do Banco de Dados ===
DATABASE_PATH = os.getenv("DATABASE_PATH", "database.db")

# === Configurações de Logging ===
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))

# === Configurações de Email (Resend.com) ===
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "noreply@seudominio.com")
RESEND_FROM_NAME = os.getenv("RESEND_FROM_NAME", APP_NAME)

# === Configurações do Servidor ===
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "True").lower() == "true"

# === Modo de Execução ===
RUNNING_MODE = os.getenv("RUNNING_MODE", "Production")
IS_DEVELOPMENT = RUNNING_MODE.lower() == "development"

# === Configurações de Fotos de Perfil ===
FOTO_PERFIL_TAMANHO_MAX = int(os.getenv("FOTO_PERFIL_TAMANHO_MAX", "256"))
# Tamanho máximo em bytes (5MB)
FOTO_MAX_UPLOAD_BYTES = int(os.getenv("FOTO_MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))

# === Configurações de Senha ===
PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
PASSWORD_MAX_LENGTH = int(os.getenv("PASSWORD_MAX_LENGTH", "128"))

# === Configurações de UI (Frontend) ===
TOAST_AUTO_HIDE_DELAY_MS = int(os.getenv("TOAST_AUTO_HIDE_DELAY_MS", "5000"))

# === Configurações de Rate Limiting ===
# Autenticação
RATE_LIMIT_LOGIN_MAX = int(os.getenv("RATE_LIMIT_LOGIN_MAX", "5"))
RATE_LIMIT_LOGIN_MINUTOS = int(os.getenv("RATE_LIMIT_LOGIN_MINUTOS", "5"))
RATE_LIMIT_CADASTRO_MAX = int(os.getenv("RATE_LIMIT_CADASTRO_MAX", "3"))
RATE_LIMIT_CADASTRO_MINUTOS = int(os.getenv("RATE_LIMIT_CADASTRO_MINUTOS", "10"))
RATE_LIMIT_ESQUECI_SENHA_MAX = int(os.getenv("RATE_LIMIT_ESQUECI_SENHA_MAX", "1"))
RATE_LIMIT_ESQUECI_SENHA_MINUTOS = int(os.getenv("RATE_LIMIT_ESQUECI_SENHA_MINUTOS", "1"))

# Upload de Foto de Perfil
RATE_LIMIT_UPLOAD_FOTO_MAX = int(os.getenv("RATE_LIMIT_UPLOAD_FOTO_MAX", "5"))
RATE_LIMIT_UPLOAD_FOTO_MINUTOS = int(os.getenv("RATE_LIMIT_UPLOAD_FOTO_MINUTOS", "10"))

# Alteração de Senha
RATE_LIMIT_ALTERAR_SENHA_MAX = int(os.getenv("RATE_LIMIT_ALTERAR_SENHA_MAX", "5"))
RATE_LIMIT_ALTERAR_SENHA_MINUTOS = int(os.getenv("RATE_LIMIT_ALTERAR_SENHA_MINUTOS", "15"))

# Chat - Mensagens
RATE_LIMIT_CHAT_MESSAGE_MAX = int(os.getenv("RATE_LIMIT_CHAT_MESSAGE_MAX", "30"))
RATE_LIMIT_CHAT_MESSAGE_MINUTOS = int(os.getenv("RATE_LIMIT_CHAT_MESSAGE_MINUTOS", "1"))

# Chat - Salas
RATE_LIMIT_CHAT_SALA_MAX = int(os.getenv("RATE_LIMIT_CHAT_SALA_MAX", "10"))
RATE_LIMIT_CHAT_SALA_MINUTOS = int(os.getenv("RATE_LIMIT_CHAT_SALA_MINUTOS", "10"))

# Chat - Busca de Usuários
RATE_LIMIT_BUSCA_USUARIOS_MAX = int(os.getenv("RATE_LIMIT_BUSCA_USUARIOS_MAX", "30"))
RATE_LIMIT_BUSCA_USUARIOS_MINUTOS = int(os.getenv("RATE_LIMIT_BUSCA_USUARIOS_MINUTOS", "1"))

# Chamados - Criação
RATE_LIMIT_CHAMADO_CRIAR_MAX = int(os.getenv("RATE_LIMIT_CHAMADO_CRIAR_MAX", "5"))
RATE_LIMIT_CHAMADO_CRIAR_MINUTOS = int(os.getenv("RATE_LIMIT_CHAMADO_CRIAR_MINUTOS", "30"))

# Chamados - Respostas (Usuário)
RATE_LIMIT_CHAMADO_RESPONDER_MAX = int(os.getenv("RATE_LIMIT_CHAMADO_RESPONDER_MAX", "10"))
RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS = int(os.getenv("RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS", "10"))

# Chamados - Respostas (Admin)
RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MAX = int(os.getenv("RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MAX", "20"))
RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MINUTOS = int(os.getenv("RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MINUTOS", "5"))

# Chat - Listagens (Conversas e Mensagens)
RATE_LIMIT_CHAT_LISTAGEM_MAX = int(os.getenv("RATE_LIMIT_CHAT_LISTAGEM_MAX", "60"))
RATE_LIMIT_CHAT_LISTAGEM_MINUTOS = int(os.getenv("RATE_LIMIT_CHAT_LISTAGEM_MINUTOS", "1"))

# Admin - Download de Backups
RATE_LIMIT_BACKUP_DOWNLOAD_MAX = int(os.getenv("RATE_LIMIT_BACKUP_DOWNLOAD_MAX", "5"))
RATE_LIMIT_BACKUP_DOWNLOAD_MINUTOS = int(os.getenv("RATE_LIMIT_BACKUP_DOWNLOAD_MINUTOS", "10"))

# Formulários GET (Edição de Perfil)
RATE_LIMIT_FORM_GET_MAX = int(os.getenv("RATE_LIMIT_FORM_GET_MAX", "60"))
RATE_LIMIT_FORM_GET_MINUTOS = int(os.getenv("RATE_LIMIT_FORM_GET_MINUTOS", "1"))

# Páginas Públicas
RATE_LIMIT_PUBLIC_MAX = int(os.getenv("RATE_LIMIT_PUBLIC_MAX", "100"))
RATE_LIMIT_PUBLIC_MINUTOS = int(os.getenv("RATE_LIMIT_PUBLIC_MINUTOS", "1"))

# Páginas de Exemplos
RATE_LIMIT_EXAMPLES_MAX = int(os.getenv("RATE_LIMIT_EXAMPLES_MAX", "100"))
RATE_LIMIT_EXAMPLES_MINUTOS = int(os.getenv("RATE_LIMIT_EXAMPLES_MINUTOS", "1"))

# === Versão da Aplicação ===
VERSION = "1.0.0"

# === Configurações de Timezone ===
TIMEZONE = os.getenv("TIMEZONE", "America/Sao_Paulo")
APP_TIMEZONE = ZoneInfo(TIMEZONE)

# === Funções Helper para Leitura Híbrida (Database + .env) ===


def obter_config_str(chave: str, padrao_env: str) -> str:
    """
    Obtém configuração com leitura híbrida: database primeiro, .env como fallback

    Args:
        chave: Chave da configuração no banco (ex: "app_name")
        padrao_env: Valor do .env ou padrão hardcoded

    Returns:
        Valor do banco de dados ou do .env
    """
    from util.config_cache import config
    # Tenta buscar do banco primeiro, se não encontrar usa o valor do .env
    valor_db = config.obter(chave, "")
    return valor_db if valor_db else padrao_env


def obter_config_int(chave: str, padrao_env: int) -> int:
    """
    Obtém configuração inteira com leitura híbrida: database primeiro, .env como fallback

    Args:
        chave: Chave da configuração no banco (ex: "rate_limit_login_max")
        padrao_env: Valor do .env ou padrão hardcoded

    Returns:
        Valor do banco de dados ou do .env
    """
    from util.config_cache import config
    # obter_int já retorna o padrão se não encontrar ou der erro
    # Mas precisamos verificar se existe no banco antes
    valor_db_str = config.obter(chave, "")
    if valor_db_str:
        try:
            return int(valor_db_str)
        except ValueError:
            return padrao_env
    return padrao_env


def obter_config_bool(chave: str, padrao_env: bool) -> bool:
    """
    Obtém configuração booleana com leitura híbrida: database primeiro, .env como fallback

    Args:
        chave: Chave da configuração no banco
        padrao_env: Valor do .env ou padrão hardcoded

    Returns:
        Valor do banco de dados ou do .env
    """
    from util.config_cache import config
    valor_db_str = config.obter(chave, "")
    if valor_db_str:
        return valor_db_str.lower() in ("true", "1", "yes", "sim", "verdadeiro")
    return padrao_env
