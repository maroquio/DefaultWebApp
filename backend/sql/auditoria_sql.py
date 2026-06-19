CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    acao TEXT NOT NULL,
    entidade TEXT NOT NULL,
    entidade_id INTEGER,
    dados_antes TEXT,
    dados_depois TEXT,
    ip TEXT,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE SET NULL
)
"""

INSERIR = """
INSERT INTO auditoria (usuario_id, acao, entidade, entidade_id, dados_antes, dados_depois, ip)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT a.*, u.nome as usuario_nome
FROM auditoria a
LEFT JOIN usuario u ON a.usuario_id = u.id
ORDER BY a.data DESC
LIMIT ?
"""

OBTER_COM_FILTROS = """
SELECT a.*, u.nome as usuario_nome
FROM auditoria a
LEFT JOIN usuario u ON a.usuario_id = u.id
WHERE 1=1
{filtros}
ORDER BY a.data DESC
LIMIT ? OFFSET ?
"""

CONTAR_COM_FILTROS = """
SELECT COUNT(*) as total
FROM auditoria a
LEFT JOIN usuario u ON a.usuario_id = u.id
WHERE 1=1
{filtros}
"""

OBTER_POR_ID = """
SELECT a.*, u.nome as usuario_nome
FROM auditoria a
LEFT JOIN usuario u ON a.usuario_id = u.id
WHERE a.id = ?
"""

EXCLUIR_ANTIGOS = """
DELETE FROM auditoria
WHERE data < datetime('now', ? || ' days')
"""
