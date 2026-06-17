#!/usr/bin/env python3
"""
Script standalone para resetar senha de usuários.

Uso:
    python redefinir_senha.py admin@email.com 123456
    python redefinir_senha.py joao@email.com NovaS3nh@123

Validações:
    - Senha deve ter mínimo 8 e máximo 128 caracteres
    - Deve conter: maiúscula, minúscula, número e caractere especial
"""

import sys
import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo

# Carrega variáveis de ambiente
load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', 'dados.db')
TIMEZONE = os.getenv('TIMEZONE', 'America/Sao_Paulo')

# Importa funções de segurança (raiz do projeto = pasta pai de scripts/)
sys.path.insert(0, str(Path(__file__).parent.parent))
from util.security import criar_hash_senha
from util.senha_util import validar_forca_senha
from util.db_util import obter_conexao, adaptar_datetime


def validar_argumentos(args):
    """Valida argumentos de linha de comando"""
    if len(args) != 3:
        print("❌ Uso incorreto!")
        print("\nSintaxe:")
        print("  python redefinir_senha.py <email> <nova_senha>")
        print("\nExemplos:")
        print("  python redefinir_senha.py admin@email.com Senha@123")
        print("  python redefinir_senha.py joao@email.com NovaS3nh@456")
        print("\nRequisitos da senha:")
        print("  - Mínimo 8 caracteres")
        print("  - Máximo 128 caracteres")
        print("  - Pelo menos 1 letra maiúscula")
        print("  - Pelo menos 1 letra minúscula")
        print("  - Pelo menos 1 número")
        print("  - Pelo menos 1 caractere especial (!@#$%^&*...)")
        sys.exit(1)

    email, senha = args[1], args[2]
    return email, senha


def verificar_banco_existe():
    """Verifica se o banco de dados existe"""
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ Banco de dados não encontrado em: {DATABASE_PATH}")
        print("\nVerifique se a aplicação foi executada pelo menos uma vez.")
        sys.exit(1)


def buscar_usuario(email: str):
    """Busca usuário pelo email"""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, email, perfil FROM usuario WHERE email = ?", (email,))
            usuario = cursor.fetchone()
            return usuario
    except sqlite3.Error as e:
        print(f"❌ Erro ao acessar banco de dados: {e}")
        sys.exit(1)


def atualizar_senha(usuario_id: int, senha_hash: str):
    """Atualiza senha do usuário"""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE usuario SET senha = ?, data_atualizacao = ? WHERE id = ?",
                (senha_hash, datetime.now(ZoneInfo(TIMEZONE)), usuario_id)
            )
            if cursor.rowcount == 0:
                return False
            return True
    except sqlite3.Error as e:
        print(f"❌ Erro ao atualizar banco de dados: {e}")
        sys.exit(1)


def main():
    """Função principal"""
    # Valida argumentos
    email, senha = validar_argumentos(sys.argv)

    print("\n" + "="*60)
    print("🔑 REDEFINIR SENHA DE USUÁRIO")
    print("="*60)

    # Verifica se banco existe
    print(f"\n📂 Banco de dados: {DATABASE_PATH}")
    verificar_banco_existe()
    print("   ✅ Banco encontrado")

    # Busca usuário
    print(f"\n👤 Procurando usuário: {email}")
    usuario = buscar_usuario(email)

    if not usuario:
        print(f"   ❌ Usuário '{email}' não encontrado!")
        sys.exit(1)

    usuario_id, nome, _, perfil = usuario
    print(f"   ✅ Usuário encontrado: {nome} ({perfil})")

    # Valida força da senha
    print(f"\n🔐 Validando nova senha...")
    é_valida, mensagem = validar_forca_senha(senha)

    if not é_valida:
        print(f"   ❌ {mensagem}")
        sys.exit(1)

    print(f"   ✅ Senha válida")

    # Confirma operação
    print(f"\n⚠️  CONFIRMAÇÃO:")
    print(f"   Usuário: {nome} ({email})")
    print(f"   Ação: Redefinir senha")
    resposta = input("\n   Deseja continuar? (s/n): ").strip().lower()

    if resposta != 's':
        print("\n❌ Operação cancelada!")
        sys.exit(0)

    # Cria hash e atualiza
    print(f"\n🔄 Atualizando senha...")
    try:
        senha_hash = criar_hash_senha(senha)
        if atualizar_senha(usuario_id, senha_hash):
            print("   ✅ Senha atualizada com sucesso!")
            print("\n" + "="*60)
            print("✅ OPERAÇÃO CONCLUÍDA COM ÊXITO!")
            print("="*60 + "\n")
        else:
            print("   ❌ Falha ao atualizar senha")
            sys.exit(1)
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
