#!/usr/bin/env python3
"""
Script de Instalação do Navegador do Playwright (apenas Chromium).

O pacote Python `playwright` é instalado via requirements.txt, mas os binários
dos navegadores NÃO vêm pelo pip — precisam ser baixados à parte. Este script
baixa somente o Chromium, que é o navegador usado pelos testes e2e do projeto
(pytest-playwright usa Chromium por padrão).

Uso (de dentro do venv do projeto):
    python scripts/instalar_playwright.py
    python scripts/instalar_playwright.py --inseguro   # redes com interceptação TLS

O script irá:
1. Confirmar que o pacote `playwright` está instalado neste interpretador
2. Baixar o navegador Chromium (em ~/AppData/Local/ms-playwright no Windows)
3. Exibir como rodar os testes e2e

Redes com proxy/antivírus que interceptam TLS podem falhar o download com
"unable to verify the first certificate". Duas saídas:
- SEGURA: aponte NODE_EXTRA_CA_CERTS para o certificado raiz corporativo (.pem)
  antes de rodar o script.
- RÁPIDA: rode com --inseguro, que desativa a verificação TLS APENAS no
  subprocesso de download (não altera variáveis de ambiente do sistema).

Observação: usa sys.executable, então instala para o MESMO Python que executa
este script. Rode-o com o python do .venv para instalar no ambiente correto.
"""

import os
import subprocess
import sys

# ─── Cores para terminal ─────────────────────────────────────────────────────

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def cor(texto: str, codigo: str) -> str:
    """Aplica cor ao texto se o terminal suportar."""
    if sys.stdout.isatty():
        return f"{codigo}{texto}{RESET}"
    return texto


def titulo(texto: str) -> None:
    print()
    print(cor("=" * 60, BLUE))
    print(cor(f"  {texto}", BOLD))
    print(cor("=" * 60, BLUE))
    print()


def ok(texto: str) -> None:
    print(cor(f"  [OK] {texto}", GREEN))


def aviso(texto: str) -> None:
    print(cor(f"  [!] {texto}", YELLOW))


def erro(texto: str) -> None:
    print(cor(f"  [X] {texto}", RED))


def verificar_pacote_playwright() -> bool:
    """Confirma que o pacote `playwright` está instalado neste interpretador."""
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def main() -> int:
    titulo("DefaultWebApp — Instalação do Chromium (Playwright)")

    inseguro = "--inseguro" in sys.argv

    print(f"  Interpretador: {cor(sys.executable, CYAN)}")
    print()

    # 1. Verificar pacote
    if not verificar_pacote_playwright():
        erro("O pacote 'playwright' não está instalado neste interpretador.")
        print("      Instale as dependências primeiro:")
        print(cor("        pip install -r requirements.txt", CYAN))
        return 1

    ok("Pacote 'playwright' encontrado.")
    print()

    # Ambiente do subprocesso (cópia do atual, sem alterar o do sistema)
    env = os.environ.copy()
    if inseguro:
        # Desativa a verificação TLS apenas para este download (redes com
        # interceptação TLS por proxy/antivírus). NÃO recomendado fora disso.
        env["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"
        aviso("Modo --inseguro: verificação TLS desativada só para este download.")
    elif env.get("NODE_EXTRA_CA_CERTS"):
        ok(f"Usando NODE_EXTRA_CA_CERTS: {env['NODE_EXTRA_CA_CERTS']}")
    print()

    # 2. Baixar somente o Chromium
    print("  Baixando o navegador Chromium (pode levar alguns minutos)...")
    print()
    try:
        resultado = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=False,
            env=env,
        )
    except OSError as e:
        erro(f"Falha ao executar o instalador do Playwright: {e}")
        return 1

    print()
    if resultado.returncode != 0:
        erro(f"Instalação do Chromium falhou (código {resultado.returncode}).")
        if not inseguro:
            print("      Se o erro foi de certificado TLS "
                  "('unable to verify the first certificate'),")
            print("      sua rede provavelmente intercepta TLS. Tente:")
            print(cor("        python scripts/instalar_playwright.py --inseguro", CYAN))
            print("      ou aponte NODE_EXTRA_CA_CERTS para o certificado raiz corporativo.")
        return resultado.returncode

    ok("Chromium instalado com sucesso.")

    # 3. Próximos passos
    titulo("Pronto!")
    print(cor("Para rodar os testes e2e:", BOLD))
    print(cor("  pytest tests/e2e", CYAN))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
