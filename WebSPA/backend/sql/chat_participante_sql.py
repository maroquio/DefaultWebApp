"""
SQL statements para a tabela chat_participante.
Gerencia os participantes de cada sala de chat.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS chat_participante (
    sala_id TEXT NOT NULL,
    usuario_id INTEGER NOT NULL,
    ultima_leitura TIMESTAMP,
    PRIMARY KEY (sala_id, usuario_id),
    FOREIGN KEY (sala_id) REFERENCES chat_sala(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

INSERIR = """
INSERT INTO chat_participante (sala_id, usuario_id, ultima_leitura)
VALUES (?, ?, ?)
"""

OBTER_POR_SALA_E_USUARIO = """
SELECT sala_id, usuario_id, ultima_leitura[timestamp]
FROM chat_participante
WHERE sala_id = ? AND usuario_id = ?
"""

LISTAR_POR_SALA = """
SELECT sala_id, usuario_id, ultima_leitura[timestamp]
FROM chat_participante
WHERE sala_id = ?
"""

LISTAR_POR_USUARIO = """
SELECT sala_id, usuario_id, ultima_leitura[timestamp]
FROM chat_participante
WHERE usuario_id = ?
"""

ATUALIZAR_ULTIMA_LEITURA = """
UPDATE chat_participante
SET ultima_leitura = ?
WHERE sala_id = ? AND usuario_id = ?
"""

CONTAR_MENSAGENS_NAO_LIDAS = """
SELECT COUNT(*) as total
FROM chat_mensagem m
WHERE m.sala_id = ?
  AND m.usuario_id != ?
  AND (
    (SELECT cp.ultima_leitura
     FROM chat_participante cp
     WHERE cp.sala_id = m.sala_id AND cp.usuario_id = ?) IS NULL
    OR
    (SELECT cp.ultima_leitura
     FROM chat_participante cp
     WHERE cp.sala_id = m.sala_id AND cp.usuario_id = ?) < m.data_envio
  )
"""

EXCLUIR = """
DELETE FROM chat_participante
WHERE sala_id = ? AND usuario_id = ?
"""
