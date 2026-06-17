"""
Utilitário de CSS de Personalização de Tema.

Gera CSS inline para sobrescrever variáveis Bootstrap com as cores
e fontes configuradas pelo administrador via painel.

Segue o mesmo padrão do toast_css_util: callable chamado a cada render
de template para sempre refletir o config_cache atual sem cache de arquivo.

Uso no template (via global injetado em criar_templates):
    {% set css_tema = tema_css_inline() %}
    {% if css_tema %}
    <style>{{ css_tema }}</style>
    {% endif %}
"""

from util.config_cache import config
from util.logger_config import logger


# Chaves de config para cores do tema
_CHAVES_COR = [
    "tema_cor_primary",
    "tema_cor_secondary",
    "tema_cor_success",
    "tema_cor_danger",
    "tema_cor_warning",
    "tema_cor_info",
    "tema_cor_light",
    "tema_cor_dark",
    "tema_cor_custom",
]

# Mapeamento chave_config → nome da variável CSS Bootstrap
_MAPA_VAR_CSS = {
    "tema_cor_primary":   "primary",
    "tema_cor_secondary": "secondary",
    "tema_cor_success":   "success",
    "tema_cor_danger":    "danger",
    "tema_cor_warning":   "warning",
    "tema_cor_info":      "info",
    "tema_cor_light":     "light",
    "tema_cor_dark":      "dark",
    "tema_cor_custom":    "custom",
}


def hex_para_rgb(hex_str: str) -> tuple[int, int, int]:
    """
    Converte cor hexadecimal para tupla RGB.

    Args:
        hex_str: Cor no formato '#rrggbb' (com ou sem #)

    Returns:
        Tupla (r, g, b) com valores 0–255

    Raises:
        ValueError: Se o formato for inválido
    """
    hex_str = hex_str.lstrip("#")
    if len(hex_str) != 6:
        raise ValueError(f"Cor hex inválida: #{hex_str}")
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return (r, g, b)


def _validar_hex(valor: str) -> bool:
    """Verifica se o valor é um hex color válido (#rrggbb)."""
    import re
    return bool(re.match(r'^#[0-9a-fA-F]{6}$', valor))


def gerar_css_tema_inline() -> str:
    """
    Gera bloco CSS com variáveis de personalização do tema.

    Callable (chamado a cada render de template) para refletir o valor
    atual do config_cache sem depender de cache de arquivo CSS estático.

    Returns:
        String CSS pronta para injetar em <style>...</style>, ou string
        vazia se nenhuma personalização estiver configurada.
    """
    linhas_root: list[str] = []
    linhas_extra: list[str] = []

    for chave, nome_bs in _MAPA_VAR_CSS.items():
        valor = config.obter(chave, "").strip()
        if not valor or not _validar_hex(valor):
            continue

        try:
            r, g, b = hex_para_rgb(valor)
        except ValueError as e:
            logger.warning(f"Cor inválida em '{chave}': {e}")
            continue

        # Variável de cor e sua versão RGB (usada por utilitários Bootstrap)
        linhas_root.append(f"  --bs-{nome_bs}: {valor};")
        linhas_root.append(f"  --bs-{nome_bs}-rgb: {r},{g},{b};")

        # Classes utilitárias para cor custom (Bootstrap não gera automaticamente)
        if nome_bs == "custom":
            linhas_extra.extend([
                ".text-custom { color: var(--bs-custom) !important; }",
                ".bg-custom { background-color: var(--bs-custom) !important; }",
                ".border-custom { border-color: var(--bs-custom) !important; }",
                ".btn-custom {",
                "  --bs-btn-color: #fff;",
                "  --bs-btn-bg: var(--bs-custom);",
                "  --bs-btn-border-color: var(--bs-custom);",
                "  color: var(--bs-btn-color);",
                "  background-color: var(--bs-btn-bg);",
                "  border-color: var(--bs-btn-border-color);",
                "}",
                ".btn-custom:hover { filter: brightness(0.85); }",
            ])

    # Fontes Google
    fonte_titulos = config.obter("tema_fonte_titulos", "").strip()
    fonte_corpo = config.obter("tema_fonte_corpo", "").strip()

    if fonte_titulos:
        linhas_extra.append(
            f"h1,h2,h3,h4,h5,h6 {{ font-family: '{fonte_titulos}', sans-serif; }}"
        )

    if fonte_corpo:
        linhas_extra.append(
            f"body {{ font-family: '{fonte_corpo}', sans-serif; }}"
        )

    if not linhas_root and not linhas_extra:
        return ""

    partes = []
    if linhas_root:
        partes.append(":root {\n" + "\n".join(linhas_root) + "\n}")
    if linhas_extra:
        partes.append("\n".join(linhas_extra))

    return "\n".join(partes)


def _obter_config_tema() -> dict:
    """
    Retorna dicionário com configurações de identidade visual do tema.

    Callable injetado no Jinja2 como global 'tema_config'.
    Chamado a cada render para refletir o estado atual do cache.

    Returns:
        Dict com:
          - logo_url: URL do logo personalizado ou '/static/img/logo.svg'
          - favicon_url: URL do favicon personalizado ou ''
          - fonte_titulos: Nome da fonte para títulos ou ''
          - fonte_corpo: Nome da fonte para corpo ou ''
    """
    logo = config.obter("tema_logo", "").strip()
    favicon = config.obter("tema_favicon", "").strip()
    fonte_titulos = config.obter("tema_fonte_titulos", "").strip()
    fonte_corpo = config.obter("tema_fonte_corpo", "").strip()

    # Logo: se não configurado, usa o padrão do sistema
    if logo:
        logo_url = f"/static/{logo}" if not logo.startswith("/") else logo
    else:
        logo_url = "/static/img/logo.svg"

    # Favicon: se não configurado, retorna vazio (browser usa padrão)
    if favicon:
        favicon_url = f"/static/{favicon}" if not favicon.startswith("/") else favicon
    else:
        favicon_url = ""

    tema_atual = config.obter("theme", "original").strip()

    return {
        "logo_url": logo_url,
        "favicon_url": favicon_url,
        "fonte_titulos": fonte_titulos,
        "fonte_corpo": fonte_corpo,
        "tema_atual": tema_atual,
    }
