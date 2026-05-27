CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS carga (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    perfil TEXT NOT NULL
)
"""

INSERIR = """
INSERT INTO carga (nome, email, senha, perfil)
VALUES (?, ?, ?, ?)
"""

ALTERAR = """
UPDATE carga
SET nome = ?, email = ?, perfil = ?
WHERE id = ?
"""
OBTER_TODOS = "SELECT id, nome, email, senha, perfil FROM carga ORDER BY nome"

EXCLUIR = "DELETE FROM carga WHERE id = ?"

OBTER_POR_ID = "SELECT id, nome, email, senha, perfil FROM carga WHERE id = ?"

OBTER_QUANTIDADE = "SELECT COUNT(*) as quantidade FROM carga"
