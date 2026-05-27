"""
Função para redefinir a senha do usuário, apenas para fins de teste.

Uso: python reset_senha.py <email> <nova_senha>

Exemplos:
    python reset_senha.py admin@email.com "1234aA@!"
    python reset_senha.py usuario@sistema.com "NovaSenha@123"
"""

import sys
from repo.usuario_repo import obter_por_email, atualizar_senha
from util.security import criar_hash_senha


def redefinir_senha_por_email(email: str, nova_senha: str) -> bool:
    """
    Redefine a senha de um usuário baseado no email.
    
    Args:
        email (str): Email do usuário cuja senha será redefinida
        nova_senha (str): Nova senha
    
    Returns:
        bool: True se a senha foi redefinida com sucesso, False caso contrário
    
    Exemplo:
        >>> redefinir_senha_por_email("usuario@email.com", "NovaSenha@123")
        True
    """
    # Busca o usuário pelo email
    usuario = obter_por_email(email)
    
    if not usuario:
        print(f"❌ Usuário com email '{email}' não encontrado.")
        return False
    
    # Cria hash da nova senha
    senha_hash = criar_hash_senha(nova_senha)
    
    # Atualiza a senha no banco de dados
    sucesso = atualizar_senha(usuario.id, senha_hash)
    
    if sucesso:
        print(f"✓ Senha redefinida com sucesso!")
        print(f"  Email: {email}")
        print(f"  Nova senha: {nova_senha}")
        return True
    else:
        print(f"❌ Erro ao redefinir a senha para {email}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("❌ Uso incorreto!")
        print("\nUso: python reset_senha.py <email> <nova_senha>")
        print("\nExemplos:")
        print('  python reset_senha.py admin@email.com "1234aA@!"')
        print('  python reset_senha.py usuario@sistema.com "NovaSenha@123"')
        sys.exit(1)
    
    email = sys.argv[1]
    nova_senha = sys.argv[2]
    
    sucesso = redefinir_senha_por_email(email, nova_senha)
    sys.exit(0 if sucesso else 1)
