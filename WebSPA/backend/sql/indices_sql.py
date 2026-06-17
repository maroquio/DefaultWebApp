# Índices da tabela usuario
CRIAR_INDICE_USUARIO_PERFIL = """
CREATE INDEX IF NOT EXISTS idx_usuario_perfil
ON usuario(perfil)
"""

CRIAR_INDICE_USUARIO_TOKEN = """
CREATE INDEX IF NOT EXISTS idx_usuario_token
ON usuario(token_redefinicao)
WHERE token_redefinicao IS NOT NULL
"""

# Índices da tabela chamado
CRIAR_INDICE_CHAMADO_USUARIO = """
CREATE INDEX IF NOT EXISTS idx_chamado_usuario_id
ON chamado(usuario_id)
"""

CRIAR_INDICE_CHAMADO_STATUS = """
CREATE INDEX IF NOT EXISTS idx_chamado_status
ON chamado(status)
"""

# Índices da tabela chamado_interacao
CRIAR_INDICE_INTERACAO_CHAMADO = """
CREATE INDEX IF NOT EXISTS idx_chamado_interacao_chamado_id
ON chamado_interacao(chamado_id)
"""

# Índices da tabela chat_mensagem
CRIAR_INDICE_CHAT_MENSAGEM_SALA = """
CREATE INDEX IF NOT EXISTS idx_chat_mensagem_sala_id
ON chat_mensagem(sala_id)
"""

# Índices da tabela chat_participante
# Nota: PRIMARY KEY (sala_id, usuario_id) já cria índice composto
# Mas precisamos de índice em usuario_id para LISTAR_POR_USUARIO
CRIAR_INDICE_CHAT_PARTICIPANTE_USUARIO = """
CREATE INDEX IF NOT EXISTS idx_chat_participante_usuario_id
ON chat_participante(usuario_id)
"""

# Lista de todos os índices para criação
TODOS_INDICES = [
    # Usuario
    CRIAR_INDICE_USUARIO_PERFIL,
    CRIAR_INDICE_USUARIO_TOKEN,
    # Chamado
    CRIAR_INDICE_CHAMADO_USUARIO,
    CRIAR_INDICE_CHAMADO_STATUS,
    # Chamado Interação
    CRIAR_INDICE_INTERACAO_CHAMADO,
    # Chat
    CRIAR_INDICE_CHAT_MENSAGEM_SALA,
    CRIAR_INDICE_CHAT_PARTICIPANTE_USUARIO,
]
