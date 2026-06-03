CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

INSERIR = """
INSERT INTO categoria (nome)
VALUES (?)
"""

OBTER_TODOS = """
SELECT * FROM categoria
ORDER BY nome ASC
"""

OBTER_POR_ID = """
SELECT * FROM categoria
WHERE id = ?
"""

ATUALIZAR = """
UPDATE categoria
SET nome = ?,
    data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

EXCLUIR = "DELETE FROM categoria WHERE id = ?"
