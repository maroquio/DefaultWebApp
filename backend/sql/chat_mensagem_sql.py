"""
SQL statements para a tabela chat_mensagem.
Gerencia as mensagens trocadas nas salas de chat.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS chat_mensagem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id TEXT NOT NULL,
    usuario_id INTEGER NOT NULL,
    mensagem TEXT NOT NULL,
    data_envio TIMESTAMP NOT NULL,
    lida_em TIMESTAMP,
    FOREIGN KEY (sala_id) REFERENCES chat_sala(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

INSERIR = """
INSERT INTO chat_mensagem (sala_id, usuario_id, mensagem, data_envio, lida_em)
VALUES (?, ?, ?, ?, ?)
"""

OBTER_POR_ID = """
SELECT id, sala_id, usuario_id, mensagem, data_envio[timestamp], lida_em[timestamp]
FROM chat_mensagem
WHERE id = ?
"""

LISTAR_POR_SALA = """
SELECT id, sala_id, usuario_id, mensagem, data_envio[timestamp], lida_em[timestamp]
FROM chat_mensagem
WHERE sala_id = ?
ORDER BY id ASC
LIMIT ? OFFSET ?
"""

CONTAR_POR_SALA = """
SELECT COUNT(*) as total
FROM chat_mensagem
WHERE sala_id = ?
"""

MARCAR_COMO_LIDAS = """
UPDATE chat_mensagem
SET lida_em = ?
WHERE sala_id = ?
  AND usuario_id != ?
  AND lida_em IS NULL
"""

OBTER_ULTIMA_MENSAGEM_SALA = """
SELECT id, sala_id, usuario_id, mensagem, data_envio[timestamp], lida_em[timestamp]
FROM chat_mensagem
WHERE sala_id = ?
ORDER BY id DESC
LIMIT 1
"""

EXCLUIR = """
DELETE FROM chat_mensagem
WHERE id = ?
"""
