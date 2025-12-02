CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS chamado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Aberto',
    prioridade TEXT NOT NULL DEFAULT 'Média',
    usuario_id INTEGER NOT NULL,
    data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fechamento TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

INSERIR = """
INSERT INTO chamado (titulo, prioridade, status, usuario_id)
VALUES (?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT c.*,
       u.nome as usuario_nome,
       u.email as usuario_email
FROM chamado c
INNER JOIN usuario u ON c.usuario_id = u.id
ORDER BY
    CASE c.prioridade
        WHEN 'Urgente' THEN 1
        WHEN 'Alta' THEN 2
        WHEN 'Média' THEN 3
        WHEN 'Baixa' THEN 4
    END,
    c.data_abertura DESC
"""

OBTER_POR_USUARIO = """
SELECT c.*,
       u.nome as usuario_nome,
       u.email as usuario_email
FROM chamado c
INNER JOIN usuario u ON c.usuario_id = u.id
WHERE c.usuario_id = ?
ORDER BY
    CASE c.status
        WHEN 'Aberto' THEN 1
        WHEN 'Em Análise' THEN 2
        WHEN 'Resolvido' THEN 3
        WHEN 'Fechado' THEN 4
    END,
    c.data_abertura DESC
"""

OBTER_POR_ID = """
SELECT c.*,
       u.nome as usuario_nome,
       u.email as usuario_email
FROM chamado c
INNER JOIN usuario u ON c.usuario_id = u.id
WHERE c.id = ?
"""

ATUALIZAR_STATUS = """
UPDATE chamado
SET status = ?, data_fechamento = ?
WHERE id = ?
"""

EXCLUIR = "DELETE FROM chamado WHERE id = ?"

CONTAR_ABERTOS_POR_USUARIO = """
SELECT COUNT(*) as total
FROM chamado
WHERE usuario_id = ? AND status IN ('Aberto', 'Em Análise')
"""

CONTAR_PENDENTES = """
SELECT COUNT(*) as total
FROM chamado
WHERE status IN ('Aberto', 'Em Análise')
"""
