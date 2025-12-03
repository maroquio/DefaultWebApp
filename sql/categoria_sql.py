# Queries SQL para operações com categorias

# Cria a tabela categoria se ela não existir
CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS categoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        descricao TEXT,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_atualizacao TIMESTAMP
    )
"""

# Insere uma nova categoria
INSERIR = """
    INSERT INTO categoria (nome, descricao)
    VALUES (?, ?)
"""

# Atualiza uma categoria existente
ALTERAR = """
    UPDATE categoria
    SET nome=?, descricao=?, data_atualizacao=CURRENT_TIMESTAMP
    WHERE id=?
"""

# Exclui uma categoria
EXCLUIR = """
    DELETE FROM categoria WHERE id=?
"""

# Busca todas as categorias ordenadas por nome
OBTER_TODOS = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    ORDER BY nome
"""

# Busca uma categoria por ID
OBTER_POR_ID = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    WHERE id=?
"""

# Busca uma categoria por nome
OBTER_POR_NOME = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    WHERE nome=?
"""
