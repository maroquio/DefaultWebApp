"""
Módulo de utilidades para templates Jinja2.

Fornece filtros customizados, funções globais e configuração
do ambiente Jinja2 para a aplicação FastAPI.
"""

from typing import Union, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from fastapi.templating import Jinja2Templates
from fastapi import Request

from util.flash_messages import obter_mensagens
from util.config import APP_NAME, VERSION, TOAST_AUTO_HIDE_DELAY_MS
from util.csrf_protection import obter_token_csrf, CSRF_FORM_FIELD
from util.config_cache import config


def formatar_data_br(
    data_str: Union[str, datetime, None],
    com_hora: bool = False
) -> str:
    """
    Converte data ISO para formato brasileiro.

    Função consolidada que formata datas com ou sem hora.

    Args:
        data_str: String com data no formato ISO (YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS)
                  ou objeto datetime
        com_hora: Se True, inclui hora no formato (DD/MM/YYYY HH:MM:SS)
                  Se False, retorna apenas data (DD/MM/YYYY)

    Returns:
        String formatada no padrão brasileiro ou string vazia se inválido
    """
    if not data_str:
        return ""

    try:
        # Se já for um objeto datetime
        if isinstance(data_str, datetime):
            formato = "%d/%m/%Y %H:%M:%S" if com_hora else "%d/%m/%Y"
            return data_str.strftime(formato)

        # Se for string, tentar parsear
        data_str = str(data_str).strip()

        # Tentar formato completo com hora (YYYY-MM-DD HH:MM:SS)
        if len(data_str) > 10:
            data = datetime.strptime(data_str[:19], "%Y-%m-%d %H:%M:%S")
        else:
            # Formato apenas data (YYYY-MM-DD)
            data = datetime.strptime(data_str[:10], "%Y-%m-%d")

        # Formatar de acordo com o parâmetro com_hora
        formato = "%d/%m/%Y %H:%M:%S" if com_hora else "%d/%m/%Y"
        return data.strftime(formato)

    except (ValueError, AttributeError):
        return str(data_str) if data_str else ""  # Retorna string vazia se falhar


def formatar_data(data: Union[datetime, None]) -> str:
    """
    Formata datetime para DD/MM/YYYY (sem hora).

    Args:
        data: Objeto datetime ou None

    Returns:
        String formatada (DD/MM/YYYY) ou vazia se None
    """
    if not data:
        return ""
    if isinstance(data, datetime):
        return data.strftime("%d/%m/%Y")
    return ""


def formatar_data_hora(data: Union[datetime, None]) -> str:
    """
    Formata datetime para DD/MM/YYYY HH:MM (sem segundos).

    Args:
        data: Objeto datetime ou None

    Returns:
        String formatada (DD/MM/YYYY HH:MM) ou vazia se None
    """
    if not data:
        return ""
    if isinstance(data, datetime):
        return data.strftime("%d/%m/%Y %H:%M")
    return ""


def formatar_data_as_hora(data: Union[datetime, None]) -> str:
    """
    Formata datetime para DD/MM/YYYY às HH:MM.

    Args:
        data: Objeto datetime ou None

    Returns:
        String formatada (DD/MM/YYYY às HH:MM) ou vazia se None
    """
    if not data:
        return ""
    if isinstance(data, datetime):
        return data.strftime("%d/%m/%Y às %H:%M")
    return ""


def formatar_hora(data: Union[datetime, None]) -> str:
    """
    Formata datetime para HH:MM (apenas hora).

    Args:
        data: Objeto datetime ou None

    Returns:
        String formatada (HH:MM) ou vazia se None
    """
    if not data:
        return ""
    if isinstance(data, datetime):
        return data.strftime("%H:%M")
    return ""


def foto_usuario(id: int) -> str:
    """
    Retorna o caminho da foto do usuário para uso em templates.

    Args:
        id: ID do usuário

    Returns:
        String com caminho da foto (ex: /static/img/usuarios/000001.jpg)
    """
    return f"/static/img/usuarios/{id:06d}.jpg"


def csrf_input(request: Optional[Request] = None) -> str:
    """
    Gera input HTML hidden com token CSRF.

    Args:
        request: Request object (obtido do contexto do template)

    Returns:
        String HTML com input hidden contendo token CSRF
    """
    if not request:
        # Fallback se request não estiver disponível
        return f'<input type="hidden" name="{CSRF_FORM_FIELD}" value="">'

    token = obter_token_csrf(request)
    return f'<input type="hidden" name="{CSRF_FORM_FIELD}" value="{token}">'


def criar_templates() -> Jinja2Templates:
    """
    Cria instância de Jinja2Templates com configurações customizadas.

    Configura o ambiente Jinja2 com:
    - Funções globais (obter_mensagens, csrf_input)
    - Variáveis globais (APP_NAME, VERSION)
    - Filtros customizados (data_br, data_hora_br, foto_usuario)

    Returns:
        Instância configurada de Jinja2Templates

    Note:
        Sempre usa o diretório raiz 'templates' para permitir
        acesso a templates base e componentes compartilhados.
    """
    # Usar o diretório raiz 'templates' para permitir acesso a base.html e subpastas
    env = Environment(loader=FileSystemLoader("templates"))

    # Adicionar função global para obter mensagens
    env.globals['obter_mensagens'] = obter_mensagens

    # Adicionar variáveis globais de configuração
    env.globals['APP_NAME'] = APP_NAME
    env.globals['VERSION'] = VERSION

    # Adicionar configuração dinâmica de toast delay (lê do banco → .env)
    env.globals['TOAST_AUTO_HIDE_DELAY_MS'] = config.obter_int(
        'toast_auto_hide_delay_ms',
        TOAST_AUTO_HIDE_DELAY_MS
    )

    # CSRF Protection: Adicionar função global para gerar input CSRF
    # IMPORTANTE: Esta função precisa receber 'request' do contexto
    # Uso no template: {{ csrf_input(request) }}
    env.globals['csrf_input'] = csrf_input

    # Adicionar filtros customizados
    env.filters['data_br'] = formatar_data_br
    env.filters['foto_usuario'] = foto_usuario

    # Filtros de formatação de data/hora (em português)
    env.filters['formatar_data'] = formatar_data
    env.filters['formatar_data_hora'] = formatar_data_hora
    env.filters['formatar_data_as_hora'] = formatar_data_as_hora
    env.filters['formatar_hora'] = formatar_hora

    templates = Jinja2Templates(env=env)
    return templates
