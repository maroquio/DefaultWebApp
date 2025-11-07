# Índices da tabela usuario
CRIAR_INDICE_USUARIO_PERFIL = """
CREATE INDEX IF NOT EXISTS idx_usuario_perfil
ON usuario(perfil)
"""

CRIAR_INDICE_USUARIO_TOKEN = """
CREATE INDEX IF NOT EXISTS idx_usuario_token
ON usuario(token_redefinicao)
WHERE token_redefinicao IS NOT NULL
"""

# Lista de todos os índices para criação
TODOS_INDICES = [
    CRIAR_INDICE_USUARIO_PERFIL,
    CRIAR_INDICE_USUARIO_TOKEN,
]
