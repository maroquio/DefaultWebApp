CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    perfil TEXT NOT NULL,
    token_redefinicao TEXT,
    data_token TIMESTAMP,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP
)
"""

INSERIR = """
INSERT INTO usuario (nome, email, senha, perfil)
VALUES (?, ?, ?, ?)
"""

ALTERAR = """
UPDATE usuario
SET nome = ?, email = ?, perfil = ?, data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

ALTERAR_SENHA = """
UPDATE usuario
SET senha = ?, data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

EXCLUIR = "DELETE FROM usuario WHERE id = ?"

OBTER_POR_ID = "SELECT * FROM usuario WHERE id = ?"

OBTER_TODOS = "SELECT * FROM usuario ORDER BY nome"

OBTER_QUANTIDADE = "SELECT COUNT(*) as quantidade FROM usuario"

OBTER_POR_EMAIL = "SELECT * FROM usuario WHERE email = ?"

ATUALIZAR_TOKEN = """
UPDATE usuario
SET token_redefinicao = ?, data_token = ?
WHERE email = ?
"""

OBTER_POR_TOKEN = """
SELECT * FROM usuario
WHERE token_redefinicao = ?
"""

LIMPAR_TOKEN = """
UPDATE usuario
SET token_redefinicao = NULL, data_token = NULL
WHERE id = ?
"""

OBTER_TODOS_POR_PERFIL = """
SELECT * FROM usuario
WHERE perfil = ?
ORDER BY nome
"""

BUSCAR_POR_TERMO = """
SELECT id, nome, email, senha, perfil,
       token_redefinicao, data_token,
       data_cadastro[timestamp], data_atualizacao[timestamp]
FROM usuario
WHERE (LOWER(nome) LIKE LOWER(?) OR LOWER(email) LIKE LOWER(?))
LIMIT ?
"""
