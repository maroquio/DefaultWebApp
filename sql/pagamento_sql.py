CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS pagamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    descricao TEXT NOT NULL,
    valor REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pendente',
    preference_id TEXT,
    payment_id TEXT,
    external_reference TEXT,
    url_checkout TEXT,
    data_criacao TIMESTAMP,
    data_atualizacao TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

INSERIR = """
INSERT INTO pagamento (
    usuario_id, descricao, valor, status,
    preference_id, payment_id, external_reference, url_checkout,
    data_criacao, data_atualizacao
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT p.*, u.nome as usuario_nome
FROM pagamento p
INNER JOIN usuario u ON p.usuario_id = u.id
ORDER BY p.data_criacao DESC
"""

OBTER_POR_USUARIO = """
SELECT p.*, u.nome as usuario_nome
FROM pagamento p
INNER JOIN usuario u ON p.usuario_id = u.id
WHERE p.usuario_id = ?
ORDER BY p.data_criacao DESC
"""

OBTER_POR_ID = """
SELECT p.*, u.nome as usuario_nome
FROM pagamento p
INNER JOIN usuario u ON p.usuario_id = u.id
WHERE p.id = ?
"""

OBTER_POR_PREFERENCE_ID = """
SELECT p.*, u.nome as usuario_nome
FROM pagamento p
INNER JOIN usuario u ON p.usuario_id = u.id
WHERE p.preference_id = ?
"""

OBTER_POR_EXTERNAL_REFERENCE = """
SELECT p.*, u.nome as usuario_nome
FROM pagamento p
INNER JOIN usuario u ON p.usuario_id = u.id
WHERE p.external_reference = ?
"""

ATUALIZAR_STATUS = """
UPDATE pagamento
SET status = ?, payment_id = ?, data_atualizacao = ?
WHERE id = ?
"""

ATUALIZAR_PREFERENCE = """
UPDATE pagamento
SET preference_id = ?, url_checkout = ?, data_atualizacao = ?
WHERE id = ?
"""

EXCLUIR = "DELETE FROM pagamento WHERE id = ?"

CONTAR_POR_STATUS = """
SELECT status, COUNT(*) as total
FROM pagamento
GROUP BY status
"""
