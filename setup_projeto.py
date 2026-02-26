#!/usr/bin/env python3
"""
Script de Configuração Inicial do DefaultWebApp.

Execute este script ao clonar o projeto para configurar
o ambiente rapidamente sem editar arquivos manualmente.

Uso:
    python setup_projeto.py

O script irá:
1. Criar o arquivo .env com configurações personalizadas
2. Atualizar util/perfis.py com os perfis do seu projeto
3. Atualizar data/usuarios_seed.json com o administrador configurado
4. Exibir os próximos passos

SEGURANÇA: Este script nunca sobrescreve arquivos existentes sem confirmação.
"""

import json
import os
import re
import secrets
import string
import sys
from pathlib import Path

# ─── Cores para terminal ─────────────────────────────────────────────────────

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
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


def secao(texto: str) -> None:
    print()
    print(cor(f"── {texto}", CYAN))


def ok(texto: str) -> None:
    print(cor(f"  ✓ {texto}", GREEN))


def aviso(texto: str) -> None:
    print(cor(f"  ⚠ {texto}", YELLOW))


def erro(texto: str) -> None:
    print(cor(f"  ✗ {texto}", RED))


def perguntar(prompt: str, padrao: str = "") -> str:
    """Exibe prompt e retorna entrada do usuário (ou padrão)."""
    sufixo = f" [{padrao}]" if padrao else ""
    try:
        resposta = input(cor(f"  → {prompt}{sufixo}: ", CYAN)).strip()
        return resposta if resposta else padrao
    except (KeyboardInterrupt, EOFError):
        print()
        print(cor("\nSetup cancelado.", YELLOW))
        sys.exit(0)


def confirmar(prompt: str, padrao: bool = True) -> bool:
    """Pergunta sim/não, retorna bool."""
    opcoes = "[S/n]" if padrao else "[s/N]"
    try:
        resposta = input(cor(f"  → {prompt} {opcoes}: ", CYAN)).strip().lower()
        if not resposta:
            return padrao
        return resposta in ("s", "sim", "y", "yes")
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)


def gerar_secret_key(tamanho: int = 64) -> str:
    """Gera uma chave secreta aleatória segura."""
    alfabeto = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alfabeto) for _ in range(tamanho))


def validar_email(email: str) -> bool:
    """Validação básica de email."""
    return bool(re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", email))


def normalizar_perfil(nome: str) -> tuple[str, str]:
    """
    Normaliza um nome de perfil para nome de constante e valor.

    Exemplo:
        "Professor" -> ("PROFESSOR", "Professor")
        "aluno" -> ("ALUNO", "Aluno")
    """
    valor = nome.strip().title()
    constante = re.sub(r"[^A-Z0-9]", "_", valor.upper())
    constante = re.sub(r"_+", "_", constante).strip("_")
    return constante, valor


# ─── Coletando informações ────────────────────────────────────────────────────

titulo("DefaultWebApp — Configuração Inicial do Projeto")

print("Este script configura o seu projeto em poucos minutos.")
print("Pressione ENTER para aceitar os valores padrão.")

# ── Nome do projeto ──────────────────────────────────────────────────────────
secao("1. Nome do Projeto")
nome_projeto = perguntar("Nome do projeto (ex: MeuSistema, ClinicaOnline)", "MeuProjeto")

# ── Perfis de usuário ────────────────────────────────────────────────────────
secao("2. Perfis de Usuário")
print("  O sistema já tem 'Administrador' como perfil obrigatório.")
print("  Defina os perfis adicionais do seu sistema (separados por vírgula).")
print("  Exemplos: Professor, Aluno | Médico, Paciente | Vendedor, Cliente")
perfis_input = perguntar("Perfis adicionais (além de Administrador)", "Cliente, Vendedor")

# Processar perfis
perfis_extras = [p.strip() for p in perfis_input.split(",") if p.strip()]
todos_perfis = [("ADMIN", "Administrador")] + [normalizar_perfil(p) for p in perfis_extras]

print()
print("  Perfis configurados:")
for constante, valor in todos_perfis:
    print(f"    • Perfil.{constante} = \"{valor}\"")

# ── Administrador inicial ────────────────────────────────────────────────────
secao("3. Usuário Administrador Inicial")
while True:
    admin_email = perguntar("E-mail do administrador", "admin@sistema.com")
    if validar_email(admin_email):
        break
    erro("E-mail inválido. Tente novamente.")

admin_nome = perguntar("Nome do administrador", "Administrador")
admin_senha = perguntar("Senha do administrador (mín. 8 chars, maiúscula, número, símbolo)", "Admin@123")

# ── Configurações do servidor ────────────────────────────────────────────────
secao("4. Servidor")
porta = perguntar("Porta do servidor", "8400")
try:
    int(porta)
except ValueError:
    aviso(f"Porta '{porta}' inválida. Usando 8400.")
    porta = "8400"

# ── Email (opcional) ─────────────────────────────────────────────────────────
secao("5. Serviço de Email (Resend.com) — opcional")
print("  Necessário apenas para recuperação de senha por e-mail.")
configurar_email = confirmar("Configurar e-mail agora?", padrao=False)
resend_key = ""
resend_from = ""
resend_from_name = nome_projeto
if configurar_email:
    resend_key = perguntar("RESEND_API_KEY (chave da API)")
    resend_from = perguntar("E-mail remetente (ex: noreply@seudominio.com)")

# ── Confirmar ────────────────────────────────────────────────────────────────
secao("Resumo da Configuração")
print(f"  Projeto:        {nome_projeto}")
print(f"  Perfis:         {', '.join(v for _, v in todos_perfis)}")
print(f"  Admin:          {admin_nome} ({admin_email})")
print(f"  Porta:          {porta}")
print(f"  E-mail:         {'Configurado' if resend_key else 'Não configurado'}")
print()

if not confirmar("Confirmar e aplicar configurações?"):
    print(cor("Setup cancelado.", YELLOW))
    sys.exit(0)

# ─── Aplicar configurações ────────────────────────────────────────────────────

secao("Aplicando configurações...")

# ── 1. Criar/atualizar .env ──────────────────────────────────────────────────
env_path = Path(".env")
env_example_path = Path(".env.example")

if env_path.exists():
    if not confirmar(f"Arquivo .env já existe. Sobrescrever?", padrao=False):
        aviso("Arquivo .env mantido sem alterações.")
    else:
        env_path.unlink()

if not env_path.exists():
    # Ler template
    if env_example_path.exists():
        conteudo_env = env_example_path.read_text(encoding="utf-8")
    else:
        conteudo_env = ""

    # Gerar chave secreta
    secret_key = gerar_secret_key()

    # Substituir valores
    substituicoes = {
        "APP_NAME=SeuProjeto": f"APP_NAME={nome_projeto}",
        "APP_NAME=MeuProjeto": f"APP_NAME={nome_projeto}",
        "SECRET_KEY=cole_a_chave_de_sessao_aqui # gere em https://generate-secret.now.sh/64": f"SECRET_KEY={secret_key}",
        "PORT=8400": f"PORT={porta}",
        "HOST=127.0.0.1": "HOST=127.0.0.1",
    }

    if resend_key:
        substituicoes["RESEND_API_KEY=cole_a_chave_de_api_do_resend_aqui # gere em https://resend.com/"] = f"RESEND_API_KEY={resend_key}"
    if resend_from:
        substituicoes["RESEND_FROM_EMAIL=noreply@seuprojeto.cachoeiro.es"] = f"RESEND_FROM_EMAIL={resend_from}"
        substituicoes['RESEND_FROM_NAME="Seu Projeto"'] = f'RESEND_FROM_NAME="{resend_from_name}"'

    if conteudo_env:
        for antigo, novo in substituicoes.items():
            conteudo_env = conteudo_env.replace(antigo, novo)
    else:
        # Criar .env do zero se não houver .env.example
        conteudo_env = f"""# Gerado por setup_projeto.py
APP_NAME={nome_projeto}
SECRET_KEY={secret_key}
DATABASE_PATH=dados.db
HOST=127.0.0.1
PORT={porta}
RELOAD=True
RUNNING_MODE=Development
TIMEZONE=America/Sao_Paulo
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30
RESEND_API_KEY={resend_key or 'cole_aqui'}
RESEND_FROM_EMAIL={resend_from or 'noreply@example.com'}
RESEND_FROM_NAME="{resend_from_name}"
FOTO_PERFIL_TAMANHO_MAX=256
FOTO_MAX_UPLOAD_BYTES=5242880
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_LENGTH=128
TOAST_AUTO_HIDE_DELAY_MS=5000
"""

    env_path.write_text(conteudo_env, encoding="utf-8")
    ok(f"Arquivo .env criado")

# ── 2. Atualizar util/perfis.py ──────────────────────────────────────────────
perfis_path = Path("util/perfis.py")
if perfis_path.exists():
    linhas_perfis = "\n".join(
        f'    {constante} = "{valor}"'
        for constante, valor in todos_perfis
    )

    novo_conteudo = f'''\
"""
Enum centralizado para perfis de usuário.

Este módulo define o Enum Perfil que é a FONTE ÚNICA DA VERDADE
para perfis de usuário no sistema.

Gerado por setup_projeto.py. Edite conforme necessário.
"""

from util.enum_base import EnumEntidade


class Perfil(EnumEntidade):
    """
    Enum centralizado para perfis de usuário.

    Este é a FONTE ÚNICA DA VERDADE para perfis no sistema.
    SEMPRE use este Enum ao referenciar perfis, NUNCA strings literais.

    Herda de EnumEntidade que fornece métodos úteis:
        - valores(): Lista todos os valores
        - existe(valor): Verifica se valor existe
        - from_valor(valor): Converte string para enum
        - validar(valor): Valida e retorna ou levanta ValueError

    Exemplos:
        - Correto: perfil = Perfil.ADMIN.value
        - Correto: perfil = Perfil.{todos_perfis[1][0] if len(todos_perfis) > 1 else "CLIENTE"}.value
        - ERRADO: perfil = "admin"
    """

    # PERFIS DO SEU SISTEMA #####################################
{linhas_perfis}
    # FIM DOS PERFIS ############################################
'''
    perfis_path.write_text(novo_conteudo, encoding="utf-8")
    ok(f"util/perfis.py atualizado com {len(todos_perfis)} perfil(s)")

# ── 3. Atualizar data/usuarios_seed.json ────────────────────────────────────
seed_path = Path("data/usuarios_seed.json")
if seed_path.exists():
    # Ler dados existentes
    try:
        dados_existentes = json.loads(seed_path.read_text(encoding="utf-8"))
        usuarios_existentes = dados_existentes.get("usuarios", [])

        # Verificar se admin já existe
        admin_ja_existe = any(
            u.get("email") == admin_email for u in usuarios_existentes
        )

        if admin_ja_existe:
            aviso(f"Usuário {admin_email} já existe no seed. Mantendo dados existentes.")
        else:
            # Criar novos dados de seed: só o admin configurado
            novo_seed = {
                "usuarios": [
                    {
                        "nome": admin_nome,
                        "email": admin_email,
                        "senha": admin_senha,
                        "perfil": "Administrador",
                    }
                ]
            }
            seed_path.write_text(
                json.dumps(novo_seed, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            ok(f"data/usuarios_seed.json atualizado com admin {admin_email}")
    except (json.JSONDecodeError, OSError) as e:
        erro(f"Erro ao processar seed: {e}")

# ─── Próximos passos ──────────────────────────────────────────────────────────

titulo("Configuração Concluída!")

print(cor("Próximos passos:", BOLD))
print()
print("  1. Instale as dependências:")
print(cor("     pip install -r requirements.txt", CYAN))
print()
print("  2. Inicie o servidor:")
print(cor("     python main.py", CYAN))
print()
print(f"  3. Acesse: {cor(f'http://localhost:{porta}', CYAN)}")
print()
print(f"  4. Login com: {cor(admin_email, CYAN)} / {cor(admin_senha, CYAN)}")
print()

if not resend_key:
    aviso("E-mail não configurado. Recuperação de senha por e-mail não funcionará.")
    print("     Configure RESEND_API_KEY no .env quando necessário.")
    print()

print(cor("  Dica:", YELLOW) + " Remova o módulo /exemplos quando iniciar o desenvolvimento real.")
print(cor("        Edite routes/examples_routes.py e desregistre em main.py.", ""))
print()
