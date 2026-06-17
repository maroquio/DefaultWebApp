"""
SQL statements para a tabela chat_sala.
Gerencia as salas de chat entre dois usuários.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS chat_sala (
    id TEXT PRIMARY KEY,
    criada_em TIMESTAMP NOT NULL,
    ultima_atividade TIMESTAMP NOT NULL
)
"""

INSERIR = """
INSERT INTO chat_sala (id, criada_em, ultima_atividade)
VALUES (?, ?, ?)
"""

OBTER_POR_ID = """
SELECT id, criada_em[timestamp], ultima_atividade[timestamp]
FROM chat_sala
WHERE id = ?
"""

ATUALIZAR_ULTIMA_ATIVIDADE = """
UPDATE chat_sala
SET ultima_atividade = ?
WHERE id = ?
"""

EXCLUIR = """
DELETE FROM chat_sala
WHERE id = ?
"""
