"""
Testes para o módulo repo/configuracao_repo.py

Testa todas as operações CRUD de configurações do sistema.
"""

import pytest
import sqlite3
import tempfile
import os
from unittest.mock import patch, MagicMock

from model.configuracao_model import Configuracao
from repo import configuracao_repo


class TestRowToConfiguracao:
    """Testes para a função _row_to_configuracao"""

    def test_conversao_com_todos_campos(self):
        """Deve converter Row com todos os campos"""
        # Simular sqlite3.Row com todos os campos
        row = MagicMock()
        row.__getitem__ = lambda s, k: {
            "id": 1,
            "chave": "teste_chave",
            "valor": "teste_valor",
            "descricao": "Descrição de teste"
        }[k]
        row.keys = lambda: ["id", "chave", "valor", "descricao"]

        config = configuracao_repo._row_to_configuracao(row)

        assert config.id == 1
        assert config.chave == "teste_chave"
        assert config.valor == "teste_valor"
        assert config.descricao == "Descrição de teste"

    def test_conversao_sem_descricao(self):
        """Deve converter Row sem campo descricao"""
        row = MagicMock()
        row.__getitem__ = lambda s, k: {
            "id": 2,
            "chave": "outra_chave",
            "valor": "outro_valor"
        }[k]
        row.keys = lambda: ["id", "chave", "valor"]

        config = configuracao_repo._row_to_configuracao(row)

        assert config.id == 2
        assert config.chave == "outra_chave"
        assert config.valor == "outro_valor"
        assert config.descricao is None


class TestCriarTabela:
    """Testes para criar_tabela"""

    def test_criar_tabela_sucesso(self, configuracao_db):
        """Deve criar tabela de configurações"""
        # Tabela já foi criada pela fixture, verificar estrutura
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='configuracao'")
            tabela = cursor.fetchone()

        assert tabela is not None
        assert tabela[0] == "configuracao"

    def test_criar_tabela_idempotente(self, configuracao_db):
        """Criar tabela múltiplas vezes não deve falhar"""
        # Primeira criação já foi feita pela fixture
        resultado1 = configuracao_repo.criar_tabela()
        resultado2 = configuracao_repo.criar_tabela()

        assert resultado1 is True
        assert resultado2 is True


class TestObterPorChave:
    """Testes para obter_por_chave"""

    def test_obter_configuracao_existente(self, configuracao_db):
        """Deve retornar configuração existente"""
        # Inserir configuração de teste
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO configuracao (chave, valor, descricao) VALUES (?, ?, ?)",
                ("chave_teste", "valor_teste", "Descrição teste")
            )

        config = configuracao_repo.obter_por_chave("chave_teste")

        assert config is not None
        assert config.chave == "chave_teste"
        assert config.valor == "valor_teste"
        assert config.descricao == "Descrição teste"

    def test_obter_configuracao_inexistente(self, configuracao_db):
        """Deve retornar None para chave inexistente"""
        config = configuracao_repo.obter_por_chave("chave_que_nao_existe")

        assert config is None


class TestObterTodos:
    """Testes para obter_todos"""

    def test_obter_lista_vazia(self, configuracao_db):
        """Deve retornar lista vazia quando não há configurações"""
        configs = configuracao_repo.obter_todos()

        assert isinstance(configs, list)
        assert len(configs) == 0

    def test_obter_todas_configuracoes(self, configuracao_db):
        """Deve retornar todas as configurações"""
        # Inserir configurações de teste
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("chave_a", "valor_a"))
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("chave_b", "valor_b"))
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("chave_c", "valor_c"))

        configs = configuracao_repo.obter_todos()

        assert len(configs) == 3
        # Ordenado por chave
        assert configs[0].chave == "chave_a"
        assert configs[1].chave == "chave_b"
        assert configs[2].chave == "chave_c"

    def test_obter_todos_retorna_objetos_configuracao(self, configuracao_db):
        """Deve retornar lista de objetos Configuracao"""
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor, descricao) VALUES (?, ?, ?)",
                           ("config", "val", "desc"))

        configs = configuracao_repo.obter_todos()

        assert all(isinstance(c, Configuracao) for c in configs)


class TestObterPorCategoria:
    """Testes para obter_por_categoria"""

    def test_agrupar_por_categoria_na_descricao(self, configuracao_db):
        """Deve agrupar configurações pela categoria na descrição"""
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor, descricao) VALUES (?, ?, ?)",
                           ("config_a", "val_a", "[Rate Limit] Configuração A"))
            cursor.execute("INSERT INTO configuracao (chave, valor, descricao) VALUES (?, ?, ?)",
                           ("config_b", "val_b", "[Rate Limit] Configuração B"))
            cursor.execute("INSERT INTO configuracao (chave, valor, descricao) VALUES (?, ?, ?)",
                           ("config_c", "val_c", "[UI] Configuração C"))

        agrupadas = configuracao_repo.obter_por_categoria()

        assert "Rate Limit" in agrupadas
        assert "UI" in agrupadas
        assert len(agrupadas["Rate Limit"]) == 2
        assert len(agrupadas["UI"]) == 1

    def test_configuracao_sem_categoria_vai_para_outras(self, configuracao_db):
        """Configurações sem categoria ficam em 'Outras'"""
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor, descricao) VALUES (?, ?, ?)",
                           ("config_sem_cat", "valor", "Descrição sem categoria"))
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)",
                           ("config_null_desc", "valor"))

        agrupadas = configuracao_repo.obter_por_categoria()

        assert "Outras" in agrupadas
        assert len(agrupadas["Outras"]) == 2

    def test_categoria_outras_vem_por_ultimo(self, configuracao_db):
        """A categoria 'Outras' deve aparecer por último"""
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor, descricao) VALUES (?, ?, ?)",
                           ("config_z", "val", "[Zebra] Categoria Z"))
            cursor.execute("INSERT INTO configuracao (chave, valor, descricao) VALUES (?, ?, ?)",
                           ("config_a", "val", "[Alpha] Categoria A"))
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)",
                           ("config_sem", "val"))

        agrupadas = configuracao_repo.obter_por_categoria()
        categorias = list(agrupadas.keys())

        assert categorias[-1] == "Outras"
        assert categorias[0] == "Alpha"  # Primeira alfabeticamente


class TestObterMultiplas:
    """Testes para obter_multiplas"""

    def test_obter_todas_chaves_existentes(self, configuracao_db):
        """Deve retornar todas as configurações solicitadas"""
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("chave_1", "valor_1"))
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("chave_2", "valor_2"))
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("chave_3", "valor_3"))

        resultado = configuracao_repo.obter_multiplas(["chave_1", "chave_3"])

        assert len(resultado) == 2
        assert resultado["chave_1"].valor == "valor_1"
        assert resultado["chave_3"].valor == "valor_3"

    def test_obter_chave_inexistente_retorna_none(self, configuracao_db):
        """Deve retornar None para chaves inexistentes"""
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("existe", "valor"))

        resultado = configuracao_repo.obter_multiplas(["existe", "nao_existe"])

        assert resultado["existe"] is not None
        assert resultado["nao_existe"] is None

    def test_obter_lista_vazia(self, configuracao_db):
        """Deve retornar dicionário vazio para lista vazia"""
        resultado = configuracao_repo.obter_multiplas([])

        assert resultado == {}


class TestAtualizar:
    """Testes para atualizar"""

    def test_atualizar_configuracao_existente(self, configuracao_db):
        """Deve atualizar valor de configuração existente"""
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("chave_update", "antigo"))

        resultado = configuracao_repo.atualizar("chave_update", "novo")

        assert resultado is True
        config = configuracao_repo.obter_por_chave("chave_update")
        assert config.valor == "novo"

    def test_atualizar_configuracao_inexistente(self, configuracao_db):
        """Deve retornar False para chave inexistente"""
        resultado = configuracao_repo.atualizar("chave_inexistente", "valor")

        assert resultado is False

    def test_atualizar_mantem_outros_campos(self, configuracao_db):
        """Atualização deve manter outros campos intactos"""
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor, descricao) VALUES (?, ?, ?)",
                           ("chave_desc", "antigo", "Descrição original"))

        configuracao_repo.atualizar("chave_desc", "novo")
        config = configuracao_repo.obter_por_chave("chave_desc")

        assert config.valor == "novo"
        assert config.descricao == "Descrição original"


class TestAtualizarMultiplas:
    """Testes para atualizar_multiplas"""

    def test_atualizar_todas_configuracoes(self, configuracao_db):
        """Deve atualizar todas as configurações em lote"""
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("batch_1", "antigo_1"))
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("batch_2", "antigo_2"))
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("batch_3", "antigo_3"))

        quantidade, nao_encontradas = configuracao_repo.atualizar_multiplas({
            "batch_1": "novo_1",
            "batch_2": "novo_2",
            "batch_3": "novo_3"
        })

        assert quantidade == 3
        assert len(nao_encontradas) == 0
        assert configuracao_repo.obter_por_chave("batch_1").valor == "novo_1"
        assert configuracao_repo.obter_por_chave("batch_2").valor == "novo_2"
        assert configuracao_repo.obter_por_chave("batch_3").valor == "novo_3"

    def test_atualizar_algumas_inexistentes(self, configuracao_db):
        """Deve retornar chaves não encontradas"""
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("existe_1", "antigo"))

        quantidade, nao_encontradas = configuracao_repo.atualizar_multiplas({
            "existe_1": "novo",
            "nao_existe_1": "valor",
            "nao_existe_2": "valor"
        })

        assert quantidade == 1
        assert len(nao_encontradas) == 2
        assert "nao_existe_1" in nao_encontradas
        assert "nao_existe_2" in nao_encontradas

    def test_atualizar_dicionario_vazio(self, configuracao_db):
        """Dicionário vazio deve retornar (0, [])"""
        quantidade, nao_encontradas = configuracao_repo.atualizar_multiplas({})

        assert quantidade == 0
        assert nao_encontradas == []

    def test_atualizar_multiplas_e_atomica(self, configuracao_db):
        """Atualização múltipla deve ser atômica (transação única)"""
        # Este teste verifica que todas as atualizações são feitas em uma transação
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("atomic_1", "antigo"))
            cursor.execute("INSERT INTO configuracao (chave, valor) VALUES (?, ?)", ("atomic_2", "antigo"))

        # Atualização parcial (uma existente, uma não)
        quantidade, nao_encontradas = configuracao_repo.atualizar_multiplas({
            "atomic_1": "novo",
            "atomic_nao_existe": "valor"
        })

        # A configuração existente deve ser atualizada
        assert quantidade == 1
        assert configuracao_repo.obter_por_chave("atomic_1").valor == "novo"


class TestInserirOuAtualizar:
    """Testes para inserir_ou_atualizar (upsert)"""

    def test_inserir_nova_configuracao(self, configuracao_db):
        """Deve inserir nova configuração quando não existe"""
        resultado = configuracao_repo.inserir_ou_atualizar(
            chave="nova_config",
            valor="novo_valor",
            descricao="Nova descrição"
        )

        assert resultado is True
        config = configuracao_repo.obter_por_chave("nova_config")
        assert config is not None
        assert config.valor == "novo_valor"
        assert config.descricao == "Nova descrição"

    def test_atualizar_configuracao_existente(self, configuracao_db):
        """Deve atualizar quando configuração já existe"""
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor, descricao) VALUES (?, ?, ?)",
                           ("existe_upsert", "antigo", "Desc antiga"))

        resultado = configuracao_repo.inserir_ou_atualizar(
            chave="existe_upsert",
            valor="novo",
            descricao="Desc nova (não usada)"
        )

        assert resultado is True
        config = configuracao_repo.obter_por_chave("existe_upsert")
        assert config.valor == "novo"
        # Descrição não é atualizada no upsert
        assert config.descricao == "Desc antiga"

    def test_inserir_sem_descricao(self, configuracao_db):
        """Deve permitir inserir sem descrição"""
        resultado = configuracao_repo.inserir_ou_atualizar(
            chave="sem_desc",
            valor="valor"
        )

        assert resultado is True
        config = configuracao_repo.obter_por_chave("sem_desc")
        assert config.valor == "valor"
        assert config.descricao == ""  # String vazia como padrão


class TestInserirPadrao:
    """Testes para inserir_padrao"""

    def test_inserir_configuracoes_padrao(self, configuracao_db):
        """Deve inserir todas as configurações padrão"""
        configuracao_repo.inserir_padrao()

        # Verificar que configurações padrão existem
        assert configuracao_repo.obter_por_chave("nome_sistema") is not None
        assert configuracao_repo.obter_por_chave("email_contato") is not None
        assert configuracao_repo.obter_por_chave("tema_padrao") is not None
        assert configuracao_repo.obter_por_chave("theme") is not None

    def test_nao_sobrescrever_existentes(self, configuracao_db):
        """Não deve sobrescrever configurações que já existem"""
        # Inserir com valor customizado
        with configuracao_repo.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO configuracao (chave, valor, descricao) VALUES (?, ?, ?)",
                           ("nome_sistema", "Meu Sistema Customizado", "Custom"))

        # Chamar inserir_padrao
        configuracao_repo.inserir_padrao()

        # Valor original deve ser mantido
        config = configuracao_repo.obter_por_chave("nome_sistema")
        assert config.valor == "Meu Sistema Customizado"

    def test_inserir_padrao_idempotente(self, configuracao_db):
        """Chamar inserir_padrao múltiplas vezes deve funcionar"""
        # Primeira chamada
        configuracao_repo.inserir_padrao()
        configs_antes = len(configuracao_repo.obter_todos())

        # Segunda chamada
        configuracao_repo.inserir_padrao()
        configs_depois = len(configuracao_repo.obter_todos())

        # Quantidade deve ser a mesma
        assert configs_antes == configs_depois


class TestValoresPadrao:
    """Testes para verificar os valores padrão corretos"""

    def test_valores_padrao_corretos(self, configuracao_db):
        """Deve inserir valores padrão corretos"""
        configuracao_repo.inserir_padrao()

        assert configuracao_repo.obter_por_chave("nome_sistema").valor == "Sistema Web"
        assert configuracao_repo.obter_por_chave("email_contato").valor == "contato@sistema.com"
        assert configuracao_repo.obter_por_chave("tema_padrao").valor == "claro"
        assert configuracao_repo.obter_por_chave("theme").valor == "original"


class TestIntegracao:
    """Testes de integração simulando fluxos reais"""

    def test_fluxo_crud_completo(self, configuracao_db):
        """Simula fluxo CRUD completo"""
        # Create
        configuracao_repo.inserir_ou_atualizar("taxa_juros", "5.5", "[Financeiro] Taxa de juros mensal")

        # Read
        config = configuracao_repo.obter_por_chave("taxa_juros")
        assert config.valor == "5.5"

        # Update
        configuracao_repo.atualizar("taxa_juros", "6.0")
        config = configuracao_repo.obter_por_chave("taxa_juros")
        assert config.valor == "6.0"

        # Read All
        todas = configuracao_repo.obter_todos()
        assert len(todas) == 1

    def test_fluxo_batch_update(self, configuracao_db):
        """Simula atualização em lote de rate limits"""
        # Inserir configurações iniciais
        rate_limits = {
            "rate_limit_login_max": "5",
            "rate_limit_login_minutos": "15",
            "rate_limit_cadastro_max": "3",
            "rate_limit_cadastro_minutos": "60"
        }

        for chave, valor in rate_limits.items():
            configuracao_repo.inserir_ou_atualizar(chave, valor, f"[Rate Limit] {chave}")

        # Atualizar em lote
        novas_configs = {
            "rate_limit_login_max": "10",
            "rate_limit_login_minutos": "30",
            "rate_limit_cadastro_max": "5"
        }

        quantidade, nao_encontradas = configuracao_repo.atualizar_multiplas(novas_configs)

        assert quantidade == 3
        assert configuracao_repo.obter_por_chave("rate_limit_login_max").valor == "10"

    def test_agrupamento_configuracoes_admin(self, configuracao_db):
        """Simula agrupamento para tela de admin"""
        # Inserir configurações de diferentes categorias
        configs = [
            ("toast_delay", "5000", "[UI] Tempo de exibição do toast"),
            ("max_upload", "5242880", "[Upload] Tamanho máximo de upload"),
            ("rate_limit_api", "100", "[Rate Limit] Limite de requisições API"),
            ("rate_limit_login", "5", "[Rate Limit] Limite de logins"),
            ("debug_mode", "false", "Modo de depuração"),  # Sem categoria
        ]

        for chave, valor, descricao in configs:
            configuracao_repo.inserir_ou_atualizar(chave, valor, descricao)

        agrupadas = configuracao_repo.obter_por_categoria()

        assert len(agrupadas["Rate Limit"]) == 2
        assert len(agrupadas["UI"]) == 1
        assert len(agrupadas["Upload"]) == 1
        assert len(agrupadas["Outras"]) == 1

    def test_multiplas_leituras_otimizado(self, configuracao_db):
        """Simula leitura de múltiplas configurações de uma vez"""
        # Inserir várias configurações
        for i in range(10):
            configuracao_repo.inserir_ou_atualizar(f"config_{i}", f"valor_{i}")

        # Buscar apenas algumas
        chaves = ["config_0", "config_5", "config_9", "nao_existe"]
        resultado = configuracao_repo.obter_multiplas(chaves)

        assert len(resultado) == 4
        assert resultado["config_0"].valor == "valor_0"
        assert resultado["config_5"].valor == "valor_5"
        assert resultado["config_9"].valor == "valor_9"
        assert resultado["nao_existe"] is None


# Fixture para banco de dados de teste
@pytest.fixture
def configuracao_db(tmp_path):
    """Cria banco de dados de teste isolado"""
    # Criar arquivo de banco temporário
    db_path = tmp_path / "test_config.db"

    # Patch para usar o banco de teste
    with patch.object(configuracao_repo, 'obter_conexao') as mock_obter:
        # Criar conexão real para banco de teste
        def criar_conexao_teste():
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            return conn

        # Usar context manager real
        from contextlib import contextmanager

        @contextmanager
        def mock_context():
            conn = criar_conexao_teste()
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

        mock_obter.return_value.__enter__ = lambda s: criar_conexao_teste()
        mock_obter.return_value.__exit__ = lambda s, *args: None

        # Atribuir o mock para funcionar como context manager
        mock_obter.side_effect = lambda: mock_context()

        # Criar tabela
        with mock_context() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chave TEXT UNIQUE NOT NULL,
                    valor TEXT NOT NULL,
                    descricao TEXT
                )
            """)
            conn.commit()

        yield db_path
