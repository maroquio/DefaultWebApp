"""
Utilitário para geração e aplicação de CSS de posicionamento de notificações toast.

A configuração de posição é persistida diretamente no arquivo CSS estático,
garantindo que o browser carregue a posição correta sem flash de reposicionamento.
"""
from pathlib import Path
from util.logger_config import logger


CUSTOM_CSS_PATH = Path(__file__).parent.parent / "static" / "css" / "custom.css"

MARKER_START = "/* === TOAST-CONFIG:START === */"
MARKER_END = "/* === TOAST-CONFIG:END === */"

POSICOES_VALIDAS = {
    "superior_direito",
    "superior_esquerdo",
    "inferior_direito",
    "inferior_esquerdo",
}


def gerar_css_toast(posicao: str, margem_vertical: int, margem_horizontal: int) -> str:
    """
    Gera o bloco CSS de posicionamento do toast container.

    Args:
        posicao: Posição da tela (ex: 'inferior_direito')
        margem_vertical: Distância em pixels da borda superior ou inferior
        margem_horizontal: Distância em pixels da borda direita ou esquerda

    Returns:
        String com o bloco CSS entre os marcadores
    """
    if posicao not in POSICOES_VALIDAS:
        posicao = "inferior_direito"

    eh_inferior = posicao.startswith("inferior")
    eh_direito = posicao.endswith("direito")

    vert_prop = "bottom" if eh_inferior else "top"
    vert_oposto = "top" if eh_inferior else "bottom"
    horiz_prop = "right" if eh_direito else "left"
    horiz_oposto = "left" if eh_direito else "right"

    return (
        f"{MARKER_START}\n"
        f"#toast-container {{\n"
        f"    {vert_prop}: {margem_vertical}px;\n"
        f"    {vert_oposto}: auto;\n"
        f"    {horiz_prop}: {margem_horizontal}px;\n"
        f"    {horiz_oposto}: auto;\n"
        f"}}\n"
        f"{MARKER_END}"
    )


def aplicar_css_toast() -> bool:
    """
    Lê as configurações do banco e atualiza a seção de posicionamento
    de toast no custom.css.

    A seção é delimitada por MARKER_START e MARKER_END. Se os marcadores
    não existirem, o bloco é adicionado ao final do arquivo.

    Returns:
        True se atualizado com sucesso, False em caso de erro.
    """
    from util.config_cache import config as cfg

    posicao = cfg.obter("toast_posicao", "inferior_direito")
    margem_v = cfg.obter_int("toast_margem_vertical", 20)
    margem_h = cfg.obter_int("toast_margem_horizontal", 20)

    novo_bloco = gerar_css_toast(posicao, margem_v, margem_h)

    try:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")

        if MARKER_START in css and MARKER_END in css:
            inicio = css.index(MARKER_START)
            fim = css.index(MARKER_END) + len(MARKER_END)
            css = css[:inicio] + novo_bloco + css[fim:]
        else:
            css = css.rstrip() + "\n\n" + novo_bloco + "\n"

        CUSTOM_CSS_PATH.write_text(css, encoding="utf-8")
        logger.info(
            f"CSS de toast atualizado: posicao={posicao}, "
            f"margem_v={margem_v}px, margem_h={margem_h}px"
        )
        return True

    except OSError as e:
        logger.error(f"Erro ao atualizar CSS de toast em '{CUSTOM_CSS_PATH}': {e}")
        return False
