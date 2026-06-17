CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS notificacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    mensagem TEXT NOT NULL,
    tipo TEXT NOT NULL DEFAULT 'info',
    lida INTEGER NOT NULL DEFAULT 0,
    url_acao TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

INSERIR = """
INSERT INTO notificacao (usuario_id, titulo, mensagem, tipo, url_acao)
VALUES (?, ?, ?, ?, ?)
"""

OBTER_POR_USUARIO = """
SELECT * FROM notificacao
WHERE usuario_id = ?
ORDER BY data_criacao DESC
LIMIT ?
"""

OBTER_NAO_LIDAS_POR_USUARIO = """
SELECT * FROM notificacao
WHERE usuario_id = ? AND lida = 0
ORDER BY data_criacao DESC
LIMIT ?
"""

CONTAR_NAO_LIDAS = """
SELECT COUNT(*) as total FROM notificacao
WHERE usuario_id = ? AND lida = 0
"""

MARCAR_COMO_LIDA = """
UPDATE notificacao SET lida = 1
WHERE id = ? AND usuario_id = ?
"""

MARCAR_TODAS_COMO_LIDAS = """
UPDATE notificacao SET lida = 1
WHERE usuario_id = ?
"""

EXCLUIR = """
DELETE FROM notificacao
WHERE id = ? AND usuario_id = ?
"""

EXCLUIR_ANTIGAS = """
DELETE FROM notificacao
WHERE usuario_id = ? AND data_criacao < datetime('now', '-? days')
"""

EXCLUIR_LIDAS = """
DELETE FROM notificacao
WHERE usuario_id = ? AND lida = 1
"""
