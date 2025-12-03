"""
Testes para os repositórios de chat.

Testa os módulos:
- repo/chat_sala_repo.py
- repo/chat_mensagem_repo.py
- repo/chat_participante_repo.py

Esses testes focam em testes unitários e funções auxiliares,
evitando testes de integração que dependem de foreign keys complexas.
"""

import pytest
from unittest.mock import MagicMock, patch
import sqlite3

from repo import chat_sala_repo
from repo import chat_mensagem_repo
from repo import chat_participante_repo
from model.chat_sala_model import ChatSala
from model.chat_mensagem_model import ChatMensagem
from model.chat_participante_model import ChatParticipante


class TestChatSalaRepo:
    """Testes para o repositório de salas de chat"""

    def test_gerar_sala_id_ordem_crescente(self):
        """Deve gerar ID com IDs em ordem crescente"""
        sala_id = chat_sala_repo.gerar_sala_id(3, 7)
        assert sala_id == "3_7"

    def test_gerar_sala_id_ordem_decrescente(self):
        """Deve gerar mesmo ID independente da ordem"""
        sala_id = chat_sala_repo.gerar_sala_id(7, 3)
        assert sala_id == "3_7"

    def test_gerar_sala_id_mesmo_resultado(self):
        """Deve gerar mesmo ID para mesmos usuários"""
        id1 = chat_sala_repo.gerar_sala_id(10, 20)
        id2 = chat_sala_repo.gerar_sala_id(20, 10)
        assert id1 == id2 == "10_20"

    def test_gerar_sala_id_usuarios_diferentes(self):
        """Deve gerar IDs diferentes para usuários diferentes"""
        id1 = chat_sala_repo.gerar_sala_id(1, 2)
        id2 = chat_sala_repo.gerar_sala_id(1, 3)
        assert id1 != id2

    def test_gerar_sala_id_iguais_zero(self):
        """Deve funcionar com ID zero"""
        sala_id = chat_sala_repo.gerar_sala_id(0, 5)
        assert sala_id == "0_5"

    def test_gerar_sala_id_numeros_grandes(self):
        """Deve funcionar com números grandes"""
        sala_id = chat_sala_repo.gerar_sala_id(999999, 888888)
        assert sala_id == "888888_999999"

    @patch.object(chat_sala_repo, 'obter_conexao')
    def test_obter_por_id_existente(self, mock_conexao):
        """Deve retornar sala existente por ID"""
        mock_cursor = MagicMock()
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda s, k: {
            "id": "1_2",
            "criada_em": "2025-01-15",
            "ultima_atividade": "2025-01-15"
        }[k]
        mock_row.keys = lambda: ["id", "criada_em", "ultima_atividade"]
        mock_cursor.fetchone.return_value = mock_row
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        sala = chat_sala_repo.obter_por_id("1_2")

        assert sala is not None
        assert sala.id == "1_2"

    @patch.object(chat_sala_repo, 'obter_conexao')
    def test_obter_por_id_inexistente(self, mock_conexao):
        """Deve retornar None para sala inexistente"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        sala = chat_sala_repo.obter_por_id("999_998")
        assert sala is None

    @patch.object(chat_sala_repo, 'obter_conexao')
    def test_criar_tabela(self, mock_conexao):
        """Deve criar tabela de salas"""
        mock_cursor = MagicMock()
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        # criar_tabela não retorna nada
        chat_sala_repo.criar_tabela()

        mock_cursor.execute.assert_called_once()

    @patch.object(chat_sala_repo, 'obter_conexao')
    def test_excluir_sala_existente(self, mock_conexao):
        """Deve excluir sala existente"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        resultado = chat_sala_repo.excluir("1_2")

        assert resultado is True

    @patch.object(chat_sala_repo, 'obter_conexao')
    def test_excluir_sala_inexistente(self, mock_conexao):
        """Deve retornar False para sala inexistente"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        resultado = chat_sala_repo.excluir("999_998")

        assert resultado is False

    @patch.object(chat_sala_repo, 'obter_conexao')
    def test_atualizar_ultima_atividade_sucesso(self, mock_conexao):
        """Deve atualizar última atividade"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        resultado = chat_sala_repo.atualizar_ultima_atividade("1_2")

        assert resultado is True

    @patch.object(chat_sala_repo, 'obter_conexao')
    def test_atualizar_ultima_atividade_sala_inexistente(self, mock_conexao):
        """Deve retornar False para sala inexistente"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        resultado = chat_sala_repo.atualizar_ultima_atividade("inexistente")

        assert resultado is False


class TestChatMensagemRepo:
    """Testes para o repositório de mensagens de chat"""

    def test_row_to_mensagem(self):
        """Deve converter Row para ChatMensagem"""
        row = MagicMock()
        row.__getitem__ = lambda s, k: {
            "id": 1,
            "sala_id": "1_2",
            "usuario_id": 1,
            "mensagem": "Olá",
            "data_envio": "2025-01-15 10:00:00",
            "lida_em": None
        }[k]
        row.keys = lambda: ["id", "sala_id", "usuario_id", "mensagem", "data_envio", "lida_em"]

        mensagem = chat_mensagem_repo._row_to_mensagem(row)

        assert mensagem.id == 1
        assert mensagem.sala_id == "1_2"
        assert mensagem.usuario_id == 1
        assert mensagem.mensagem == "Olá"

    @patch.object(chat_mensagem_repo, 'obter_conexao')
    def test_obter_por_id_existente(self, mock_conexao):
        """Deve retornar mensagem existente"""
        mock_cursor = MagicMock()
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda s, k: {
            "id": 1,
            "sala_id": "1_2",
            "usuario_id": 1,
            "mensagem": "Teste",
            "data_envio": "2025-01-15",
            "lida_em": None
        }[k]
        mock_row.keys = lambda: ["id", "sala_id", "usuario_id", "mensagem", "data_envio", "lida_em"]
        mock_cursor.fetchone.return_value = mock_row
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        mensagem = chat_mensagem_repo.obter_por_id(1)

        assert mensagem is not None
        assert mensagem.id == 1

    @patch.object(chat_mensagem_repo, 'obter_conexao')
    def test_obter_por_id_inexistente(self, mock_conexao):
        """Deve retornar None para mensagem inexistente"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        mensagem = chat_mensagem_repo.obter_por_id(99999)
        assert mensagem is None

    @patch.object(chat_mensagem_repo, 'obter_conexao')
    def test_criar_tabela(self, mock_conexao):
        """Deve criar tabela de mensagens"""
        mock_cursor = MagicMock()
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        # criar_tabela não retorna nada
        chat_mensagem_repo.criar_tabela()

        mock_cursor.execute.assert_called_once()

    @patch.object(chat_mensagem_repo, 'obter_conexao')
    def test_listar_por_sala_vazia(self, mock_conexao):
        """Deve retornar lista vazia para sala sem mensagens"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        mensagens = chat_mensagem_repo.listar_por_sala("1_2")

        assert mensagens == []

    @patch.object(chat_mensagem_repo, 'obter_conexao')
    def test_listar_por_sala_com_mensagens(self, mock_conexao):
        """Deve retornar lista de mensagens"""
        mock_cursor = MagicMock()
        mock_row1 = MagicMock()
        mock_row1.__getitem__ = lambda s, k: {
            "id": 1, "sala_id": "1_2", "usuario_id": 1,
            "mensagem": "Msg 1", "data_envio": "2025-01-15", "lida_em": None
        }[k]
        mock_row1.keys = lambda: ["id", "sala_id", "usuario_id", "mensagem", "data_envio", "lida_em"]

        mock_row2 = MagicMock()
        mock_row2.__getitem__ = lambda s, k: {
            "id": 2, "sala_id": "1_2", "usuario_id": 2,
            "mensagem": "Msg 2", "data_envio": "2025-01-15", "lida_em": None
        }[k]
        mock_row2.keys = lambda: ["id", "sala_id", "usuario_id", "mensagem", "data_envio", "lida_em"]

        mock_cursor.fetchall.return_value = [mock_row1, mock_row2]
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        mensagens = chat_mensagem_repo.listar_por_sala("1_2")

        assert len(mensagens) == 2
        assert all(m.sala_id == "1_2" for m in mensagens)

    @patch.object(chat_mensagem_repo, 'obter_conexao')
    def test_contar_por_sala(self, mock_conexao):
        """Deve contar mensagens da sala"""
        mock_cursor = MagicMock()
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda s, k: {"total": 5}[k]
        mock_cursor.fetchone.return_value = mock_row
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        total = chat_mensagem_repo.contar_por_sala("1_2")

        assert total == 5

    @patch.object(chat_mensagem_repo, 'obter_conexao')
    def test_excluir_mensagem_existente(self, mock_conexao):
        """Deve excluir mensagem existente"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        resultado = chat_mensagem_repo.excluir(1)

        assert resultado is True

    @patch.object(chat_mensagem_repo, 'obter_conexao')
    def test_excluir_mensagem_inexistente(self, mock_conexao):
        """Deve retornar False para mensagem inexistente"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        resultado = chat_mensagem_repo.excluir(99999)

        assert resultado is False

    @patch.object(chat_mensagem_repo, 'obter_conexao')
    def test_marcar_como_lidas(self, mock_conexao):
        """Deve marcar mensagens como lidas"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 2
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        resultado = chat_mensagem_repo.marcar_como_lidas("1_2", 1)

        assert resultado is True

    @patch.object(chat_mensagem_repo, 'obter_conexao')
    def test_obter_ultima_mensagem_sala(self, mock_conexao):
        """Deve retornar última mensagem"""
        mock_cursor = MagicMock()
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda s, k: {
            "id": 10, "sala_id": "1_2", "usuario_id": 1,
            "mensagem": "Última", "data_envio": "2025-01-15", "lida_em": None
        }[k]
        mock_row.keys = lambda: ["id", "sala_id", "usuario_id", "mensagem", "data_envio", "lida_em"]
        mock_cursor.fetchone.return_value = mock_row
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        ultima = chat_mensagem_repo.obter_ultima_mensagem_sala("1_2")

        assert ultima is not None
        assert ultima.mensagem == "Última"

    @patch.object(chat_mensagem_repo, 'obter_conexao')
    def test_obter_ultima_mensagem_sala_vazia(self, mock_conexao):
        """Deve retornar None para sala sem mensagens"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        ultima = chat_mensagem_repo.obter_ultima_mensagem_sala("1_2")

        assert ultima is None


class TestChatParticipanteRepo:
    """Testes para o repositório de participantes de chat"""

    def test_row_to_participante(self):
        """Deve converter Row para ChatParticipante"""
        row = MagicMock()
        row.__getitem__ = lambda s, k: {
            "sala_id": "1_2",
            "usuario_id": 1,
            "ultima_leitura": "2025-01-15 10:00:00"
        }[k]
        row.keys = lambda: ["sala_id", "usuario_id", "ultima_leitura"]

        participante = chat_participante_repo._row_to_participante(row)

        assert participante.sala_id == "1_2"
        assert participante.usuario_id == 1

    @patch.object(chat_participante_repo, 'obter_conexao')
    def test_obter_por_sala_e_usuario_existente(self, mock_conexao):
        """Deve retornar participante existente"""
        mock_cursor = MagicMock()
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda s, k: {
            "id": 1, "sala_id": "1_2", "usuario_id": 1, "ultima_leitura": None
        }[k]
        mock_row.keys = lambda: ["id", "sala_id", "usuario_id", "ultima_leitura"]
        mock_cursor.fetchone.return_value = mock_row
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        participante = chat_participante_repo.obter_por_sala_e_usuario("1_2", 1)

        assert participante is not None
        assert participante.usuario_id == 1

    @patch.object(chat_participante_repo, 'obter_conexao')
    def test_obter_por_sala_e_usuario_inexistente(self, mock_conexao):
        """Deve retornar None para participante inexistente"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        participante = chat_participante_repo.obter_por_sala_e_usuario("1_2", 99999)
        assert participante is None

    @patch.object(chat_participante_repo, 'obter_conexao')
    def test_criar_tabela(self, mock_conexao):
        """Deve criar tabela de participantes"""
        mock_cursor = MagicMock()
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        # criar_tabela não retorna nada
        chat_participante_repo.criar_tabela()

        mock_cursor.execute.assert_called_once()

    @patch.object(chat_participante_repo, 'obter_conexao')
    def test_listar_por_sala_vazia(self, mock_conexao):
        """Deve retornar lista vazia para sala sem participantes"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        participantes = chat_participante_repo.listar_por_sala("1_2")

        assert participantes == []

    @patch.object(chat_participante_repo, 'obter_conexao')
    def test_listar_por_sala_com_participantes(self, mock_conexao):
        """Deve retornar lista de participantes"""
        mock_cursor = MagicMock()
        mock_row1 = MagicMock()
        mock_row1.__getitem__ = lambda s, k: {
            "id": 1, "sala_id": "1_2", "usuario_id": 1, "ultima_leitura": None
        }[k]
        mock_row1.keys = lambda: ["id", "sala_id", "usuario_id", "ultima_leitura"]

        mock_row2 = MagicMock()
        mock_row2.__getitem__ = lambda s, k: {
            "id": 2, "sala_id": "1_2", "usuario_id": 2, "ultima_leitura": None
        }[k]
        mock_row2.keys = lambda: ["id", "sala_id", "usuario_id", "ultima_leitura"]

        mock_cursor.fetchall.return_value = [mock_row1, mock_row2]
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        participantes = chat_participante_repo.listar_por_sala("1_2")

        assert len(participantes) == 2

    @patch.object(chat_participante_repo, 'obter_conexao')
    def test_listar_por_usuario(self, mock_conexao):
        """Deve listar participações de um usuário"""
        mock_cursor = MagicMock()
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda s, k: {
            "id": 1, "sala_id": "1_2", "usuario_id": 1, "ultima_leitura": None
        }[k]
        mock_row.keys = lambda: ["id", "sala_id", "usuario_id", "ultima_leitura"]
        mock_cursor.fetchall.return_value = [mock_row]
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        participacoes = chat_participante_repo.listar_por_usuario(1)

        assert len(participacoes) == 1

    @patch.object(chat_participante_repo, 'obter_conexao')
    def test_atualizar_ultima_leitura_sucesso(self, mock_conexao):
        """Deve atualizar última leitura"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        resultado = chat_participante_repo.atualizar_ultima_leitura("1_2", 1)

        assert resultado is True

    @patch.object(chat_participante_repo, 'obter_conexao')
    def test_atualizar_ultima_leitura_inexistente(self, mock_conexao):
        """Deve retornar False para participante inexistente"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        resultado = chat_participante_repo.atualizar_ultima_leitura("1_2", 99999)

        assert resultado is False

    @patch.object(chat_participante_repo, 'obter_conexao')
    def test_contar_mensagens_nao_lidas(self, mock_conexao):
        """Deve contar mensagens não lidas"""
        mock_cursor = MagicMock()
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda s, k: {"total": 3}[k]
        mock_cursor.fetchone.return_value = mock_row
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        total = chat_participante_repo.contar_mensagens_nao_lidas("1_2", 1)

        assert total == 3

    @patch.object(chat_participante_repo, 'obter_conexao')
    def test_excluir_participante_existente(self, mock_conexao):
        """Deve excluir participante"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        resultado = chat_participante_repo.excluir("1_2", 1)

        assert resultado is True

    @patch.object(chat_participante_repo, 'obter_conexao')
    def test_excluir_participante_inexistente(self, mock_conexao):
        """Deve retornar False para participante inexistente"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_conexao.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        resultado = chat_participante_repo.excluir("1_2", 99999)

        assert resultado is False
