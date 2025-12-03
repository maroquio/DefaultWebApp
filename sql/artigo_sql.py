# Queries SQL para operações com artigos

# Cria a tabela artigo se ela não existir
CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS artigo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT UNIQUE NOT NULL,
        resumo TEXT,
        conteudo TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Rascunho',
        usuario_id INTEGER NOT NULL,
        categoria_id INTEGER NOT NULL,
        qtde_visualizacoes INTEGER NOT NULL DEFAULT 0,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_atualizacao TIMESTAMP,
        data_publicacao TIMESTAMP,
        data_pausa TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuario(id),
        FOREIGN KEY (categoria_id) REFERENCES categoria(id)
    )
"""

# Insere um novo artigo
INSERIR = """
    INSERT INTO artigo (titulo, resumo, conteudo, status, usuario_id, categoria_id)
    VALUES (?, ?, ?, ?, ?, ?)
"""

# Atualiza um artigo existente
ALTERAR = """
    UPDATE artigo
    SET titulo=?, resumo=?, conteudo=?, status=?, categoria_id=?, data_atualizacao=CURRENT_TIMESTAMP
    WHERE id=?
"""

# Atualiza status do artigo
ALTERAR_STATUS = """
    UPDATE artigo
    SET status=?, data_atualizacao=CURRENT_TIMESTAMP,
        data_publicacao = CASE WHEN ? = 'Publicado' THEN CURRENT_TIMESTAMP ELSE data_publicacao END,
        data_pausa = CASE WHEN ? = 'Pausado' THEN CURRENT_TIMESTAMP ELSE data_pausa END
    WHERE id=?
"""

# Exclui um artigo
EXCLUIR = """
    DELETE FROM artigo WHERE id=?
"""

# Busca todos os artigos ordenados por data de cadastro (mais recentes primeiro)
OBTER_TODOS = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    ORDER BY a.data_cadastro DESC
"""

# Busca artigos por usuário (autor)
OBTER_POR_USUARIO = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    WHERE a.usuario_id = ?
    ORDER BY a.data_cadastro DESC
"""

# Busca artigos publicados (para exibição pública)
OBTER_PUBLICADOS = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    WHERE a.status = 'Publicado'
    ORDER BY a.data_publicacao DESC
"""

# Busca os últimos N artigos publicados
OBTER_ULTIMOS_PUBLICADOS = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    WHERE a.status = 'Publicado'
    ORDER BY a.data_publicacao DESC
    LIMIT ?
"""

# Busca um artigo por ID
OBTER_POR_ID = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    WHERE a.id = ?
"""

# Busca artigos por título (busca parcial)
BUSCAR_POR_TITULO = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    WHERE a.status = 'Publicado' AND a.titulo LIKE ?
    ORDER BY a.data_publicacao DESC
"""

# Busca artigos por categoria
OBTER_POR_CATEGORIA = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    WHERE a.status = 'Publicado' AND a.categoria_id = ?
    ORDER BY a.data_publicacao DESC
"""

# Incrementa visualizações
INCREMENTAR_VISUALIZACOES = """
    UPDATE artigo SET qtde_visualizacoes = qtde_visualizacoes + 1 WHERE id = ?
"""

# Conta quantidade de artigos
OBTER_QUANTIDADE = """
    SELECT COUNT(*) as quantidade FROM artigo
"""

# Conta quantidade de artigos publicados
OBTER_QUANTIDADE_PUBLICADOS = """
    SELECT COUNT(*) as quantidade FROM artigo WHERE status = 'Publicado'
"""

# Verifica se título já existe
VERIFICAR_TITULO_EXISTE = """
    SELECT id FROM artigo WHERE titulo = ? AND id != ?
"""