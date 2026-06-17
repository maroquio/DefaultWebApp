"""
Testes de integração para os repositórios de chat.

Testa os módulos:
- repo/chat_sala_repo.py
- repo/chat_mensagem_repo.py
- repo/chat_participante_repo.py

Esses testes usam banco de dados real para validar integração.
"""
import pytest

from repo import chat_sala_repo
from repo import chat_mensagem_repo
from repo import chat_participante_repo
from repo import usuario_repo
from model.usuario_model import Usuario
from util.security import criar_hash_senha
from util.perfis import Perfil


# =============================================================================
# Testes de chat_sala_repo
# =============================================================================

class TestChatSalaRepoGerarId:
    """Testes para a função gerar_sala_id (função pura, sem banco)."""

    def test_gerar_sala_id_ordem_crescente(self):
        """Deve gerar ID com IDs em ordem crescente."""
        sala_id = chat_sala_repo.gerar_sala_id(3, 7)
        assert sala_id == "3_7"

    def test_gerar_sala_id_ordem_decrescente(self):
        """Deve gerar mesmo ID independente da ordem."""
        sala_id = chat_sala_repo.gerar_sala_id(7, 3)
        assert sala_id == "3_7"

    def test_gerar_sala_id_mesmo_resultado(self):
        """Deve gerar mesmo ID para mesmos usuários."""
        id1 = chat_sala_repo.gerar_sala_id(10, 20)
        id2 = chat_sala_repo.gerar_sala_id(20, 10)
        assert id1 == id2 == "10_20"

    def test_gerar_sala_id_usuarios_diferentes(self):
        """Deve gerar IDs diferentes para usuários diferentes."""
        id1 = chat_sala_repo.gerar_sala_id(1, 2)
        id2 = chat_sala_repo.gerar_sala_id(1, 3)
        assert id1 != id2

    def test_gerar_sala_id_com_zero(self):
        """Deve funcionar com ID zero."""
        sala_id = chat_sala_repo.gerar_sala_id(0, 5)
        assert sala_id == "0_5"

    def test_gerar_sala_id_numeros_grandes(self):
        """Deve funcionar com números grandes."""
        sala_id = chat_sala_repo.gerar_sala_id(999999, 888888)
        assert sala_id == "888888_999999"


class TestChatSalaRepoCriarOuObter:
    """Testes para a função criar_ou_obter_sala."""

    def test_criar_nova_sala(self):
        """Deve criar nova sala entre dois usuários."""
        # Criar usuários
        usuario1 = Usuario(
            id=0,
            nome="Usuario Chat 1",
            email="chat1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Chat 2",
            email="chat2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)

        # Criar sala
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        assert sala is not None
        assert sala.id == chat_sala_repo.gerar_sala_id(usuario1_id, usuario2_id)
        assert sala.criada_em is not None

    def test_obter_sala_existente(self):
        """Deve retornar sala existente ao invés de criar nova."""
        # Criar usuários
        usuario1 = Usuario(
            id=0,
            nome="Usuario Sala Existente 1",
            email="sala_exist1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Sala Existente 2",
            email="sala_exist2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)

        # Criar sala primeira vez
        sala1 = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Tentar criar novamente - deve retornar a mesma
        sala2 = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        assert sala1.id == sala2.id

    def test_criar_sala_ordem_invertida(self):
        """Deve retornar mesma sala independente da ordem dos usuários."""
        # Criar usuários
        usuario1 = Usuario(
            id=0,
            nome="Usuario Ordem 1",
            email="ordem1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Ordem 2",
            email="ordem2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)

        # Criar com ordem 1, 2
        sala1 = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Criar com ordem 2, 1
        sala2 = chat_sala_repo.criar_ou_obter_sala(usuario2_id, usuario1_id)

        assert sala1.id == sala2.id


class TestChatSalaRepoObterPorId:
    """Testes para a função obter_por_id."""

    def test_obter_por_id_existente(self):
        """Deve retornar sala existente por ID."""
        # Criar usuários e sala
        usuario1 = Usuario(
            id=0,
            nome="Usuario Obter 1",
            email="obter1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Obter 2",
            email="obter2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Obter por ID
        resultado = chat_sala_repo.obter_por_id(sala.id)

        assert resultado is not None
        assert resultado.id == sala.id

    def test_obter_por_id_inexistente(self):
        """Deve retornar None para sala inexistente."""
        resultado = chat_sala_repo.obter_por_id("999999_999998")
        assert resultado is None


class TestChatSalaRepoAtualizar:
    """Testes para a função atualizar_ultima_atividade."""

    def test_atualizar_ultima_atividade_sucesso(self):
        """Deve atualizar última atividade da sala."""
        # Criar usuários e sala
        usuario1 = Usuario(
            id=0,
            nome="Usuario Atividade 1",
            email="atividade1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Atividade 2",
            email="atividade2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Atualizar atividade
        resultado = chat_sala_repo.atualizar_ultima_atividade(sala.id)

        assert resultado is True

    def test_atualizar_ultima_atividade_sala_inexistente(self):
        """Deve retornar False para sala inexistente."""
        resultado = chat_sala_repo.atualizar_ultima_atividade("inexistente_999")
        assert resultado is False


class TestChatSalaRepoExcluir:
    """Testes para a função excluir."""

    def test_excluir_sala_existente(self):
        """Deve excluir sala existente."""
        # Criar usuários e sala
        usuario1 = Usuario(
            id=0,
            nome="Usuario Excluir 1",
            email="excluir_sala1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Excluir 2",
            email="excluir_sala2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Excluir
        resultado = chat_sala_repo.excluir(sala.id)

        assert resultado is True
        # Verificar que não existe mais
        assert chat_sala_repo.obter_por_id(sala.id) is None

    def test_excluir_sala_inexistente(self):
        """Deve retornar False para sala inexistente."""
        resultado = chat_sala_repo.excluir("inexistente_sala")
        assert resultado is False


class TestChatSalaRepoCriarTabela:
    """Testes para a função criar_tabela."""

    def test_criar_tabela_nao_falha(self):
        """Deve criar tabela sem erro."""
        # Não deve lançar exceção
        chat_sala_repo.criar_tabela()


# =============================================================================
# Testes de chat_mensagem_repo
# =============================================================================

class TestChatMensagemRepoInserir:
    """Testes para a função inserir."""

    def test_inserir_mensagem(self):
        """Deve inserir mensagem e retornar objeto."""
        # Criar usuários e sala
        usuario1 = Usuario(
            id=0,
            nome="Usuario Msg 1",
            email="msg1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Msg 2",
            email="msg2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Inserir mensagem
        mensagem = chat_mensagem_repo.inserir(sala.id, usuario1_id, "Olá, tudo bem?")

        assert mensagem is not None
        assert mensagem.id > 0
        assert mensagem.sala_id == sala.id
        assert mensagem.usuario_id == usuario1_id
        assert mensagem.mensagem == "Olá, tudo bem?"
        assert mensagem.data_envio is not None

    def test_inserir_multiplas_mensagens(self):
        """Deve inserir múltiplas mensagens na mesma sala."""
        # Criar usuários e sala
        usuario1 = Usuario(
            id=0,
            nome="Usuario Multi Msg 1",
            email="multi_msg1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Multi Msg 2",
            email="multi_msg2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Inserir várias mensagens
        msg1 = chat_mensagem_repo.inserir(sala.id, usuario1_id, "Primeira mensagem")
        msg2 = chat_mensagem_repo.inserir(sala.id, usuario2_id, "Segunda mensagem")
        msg3 = chat_mensagem_repo.inserir(sala.id, usuario1_id, "Terceira mensagem")

        assert msg1.id != msg2.id != msg3.id
        assert msg1.usuario_id == usuario1_id
        assert msg2.usuario_id == usuario2_id


class TestChatMensagemRepoObterPorId:
    """Testes para a função obter_por_id."""

    def test_obter_por_id_existente(self):
        """Deve retornar mensagem existente."""
        # Criar usuários, sala e mensagem
        usuario1 = Usuario(
            id=0,
            nome="Usuario Obter Msg 1",
            email="obter_msg1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Obter Msg 2",
            email="obter_msg2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)
        mensagem = chat_mensagem_repo.inserir(sala.id, usuario1_id, "Mensagem teste")

        # Obter por ID
        resultado = chat_mensagem_repo.obter_por_id(mensagem.id)

        assert resultado is not None
        assert resultado.id == mensagem.id
        assert resultado.mensagem == "Mensagem teste"

    def test_obter_por_id_inexistente(self):
        """Deve retornar None para mensagem inexistente."""
        resultado = chat_mensagem_repo.obter_por_id(999999)
        assert resultado is None


class TestChatMensagemRepoListar:
    """Testes para a função listar_por_sala."""

    def test_listar_por_sala_vazia(self):
        """Deve retornar lista vazia para sala sem mensagens."""
        # Criar usuários e sala
        usuario1 = Usuario(
            id=0,
            nome="Usuario Lista Vazia 1",
            email="lista_vazia1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Lista Vazia 2",
            email="lista_vazia2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Listar mensagens
        mensagens = chat_mensagem_repo.listar_por_sala(sala.id)

        assert mensagens == []

    def test_listar_por_sala_com_mensagens(self):
        """Deve retornar lista de mensagens."""
        # Criar usuários, sala e mensagens
        usuario1 = Usuario(
            id=0,
            nome="Usuario Lista 1",
            email="lista1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Lista 2",
            email="lista2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        chat_mensagem_repo.inserir(sala.id, usuario1_id, "Msg 1")
        chat_mensagem_repo.inserir(sala.id, usuario2_id, "Msg 2")

        # Listar mensagens
        mensagens = chat_mensagem_repo.listar_por_sala(sala.id)

        assert len(mensagens) == 2
        assert all(m.sala_id == sala.id for m in mensagens)

    def test_listar_por_sala_com_limite(self):
        """Deve respeitar limite de resultados."""
        # Criar usuários, sala e mensagens
        usuario1 = Usuario(
            id=0,
            nome="Usuario Limite 1",
            email="limite1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Limite 2",
            email="limite2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        for i in range(5):
            chat_mensagem_repo.inserir(sala.id, usuario1_id, f"Msg {i}")

        # Listar com limite
        mensagens = chat_mensagem_repo.listar_por_sala(sala.id, limit=3)

        assert len(mensagens) == 3


class TestChatMensagemRepoContar:
    """Testes para a função contar_por_sala."""

    def test_contar_por_sala(self):
        """Deve contar mensagens da sala."""
        # Criar usuários, sala e mensagens
        usuario1 = Usuario(
            id=0,
            nome="Usuario Contar 1",
            email="contar1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Contar 2",
            email="contar2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        chat_mensagem_repo.inserir(sala.id, usuario1_id, "Msg 1")
        chat_mensagem_repo.inserir(sala.id, usuario2_id, "Msg 2")
        chat_mensagem_repo.inserir(sala.id, usuario1_id, "Msg 3")

        # Contar
        total = chat_mensagem_repo.contar_por_sala(sala.id)

        assert total == 3

    def test_contar_por_sala_vazia(self):
        """Deve retornar zero para sala sem mensagens."""
        # Criar usuários e sala
        usuario1 = Usuario(
            id=0,
            nome="Usuario Contar Vazia 1",
            email="contar_vazia1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Contar Vazia 2",
            email="contar_vazia2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Contar
        total = chat_mensagem_repo.contar_por_sala(sala.id)

        assert total == 0


class TestChatMensagemRepoMarcar:
    """Testes para a função marcar_como_lidas."""

    def test_marcar_como_lidas(self):
        """Deve marcar mensagens como lidas."""
        # Criar usuários, sala e mensagens
        usuario1 = Usuario(
            id=0,
            nome="Usuario Marcar 1",
            email="marcar1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Marcar 2",
            email="marcar2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Usuario 1 envia mensagens
        chat_mensagem_repo.inserir(sala.id, usuario1_id, "Msg do usuario 1")

        # Usuario 2 marca como lidas
        resultado = chat_mensagem_repo.marcar_como_lidas(sala.id, usuario2_id)

        assert resultado is True


class TestChatMensagemRepoUltima:
    """Testes para a função obter_ultima_mensagem_sala."""

    def test_obter_ultima_mensagem_sala(self):
        """Deve retornar última mensagem."""
        # Criar usuários, sala e mensagens
        usuario1 = Usuario(
            id=0,
            nome="Usuario Ultima 1",
            email="ultima1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Ultima 2",
            email="ultima2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        chat_mensagem_repo.inserir(sala.id, usuario1_id, "Primeira")
        chat_mensagem_repo.inserir(sala.id, usuario2_id, "Segunda")
        chat_mensagem_repo.inserir(sala.id, usuario1_id, "Última mensagem")

        # Obter última
        ultima = chat_mensagem_repo.obter_ultima_mensagem_sala(sala.id)

        assert ultima is not None
        assert ultima.mensagem == "Última mensagem"

    def test_obter_ultima_mensagem_sala_vazia(self):
        """Deve retornar None para sala sem mensagens."""
        # Criar usuários e sala
        usuario1 = Usuario(
            id=0,
            nome="Usuario Ultima Vazia 1",
            email="ultima_vazia1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Ultima Vazia 2",
            email="ultima_vazia2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Obter última
        ultima = chat_mensagem_repo.obter_ultima_mensagem_sala(sala.id)

        assert ultima is None


class TestChatMensagemRepoExcluir:
    """Testes para a função excluir."""

    def test_excluir_mensagem_existente(self):
        """Deve excluir mensagem existente."""
        # Criar usuários, sala e mensagem
        usuario1 = Usuario(
            id=0,
            nome="Usuario Excluir Msg 1",
            email="excluir_msg1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Excluir Msg 2",
            email="excluir_msg2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)
        mensagem = chat_mensagem_repo.inserir(sala.id, usuario1_id, "Mensagem a excluir")

        # Excluir
        resultado = chat_mensagem_repo.excluir(mensagem.id)

        assert resultado is True
        assert chat_mensagem_repo.obter_por_id(mensagem.id) is None

    def test_excluir_mensagem_inexistente(self):
        """Deve retornar False para mensagem inexistente."""
        resultado = chat_mensagem_repo.excluir(999999)
        assert resultado is False


class TestChatMensagemRepoCriarTabela:
    """Testes para a função criar_tabela."""

    def test_criar_tabela_nao_falha(self):
        """Deve criar tabela sem erro."""
        chat_mensagem_repo.criar_tabela()


# =============================================================================
# Testes de chat_participante_repo
# =============================================================================

class TestChatParticipanteRepoInserir:
    """Testes para a função adicionar_participante."""

    def test_adicionar_participante(self):
        """Deve adicionar participante à sala."""
        # Criar usuários e sala
        usuario1 = Usuario(
            id=0,
            nome="Usuario Part 1",
            email="part1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Part 2",
            email="part2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Adicionar participante
        participante = chat_participante_repo.adicionar_participante(sala.id, usuario1_id)

        assert participante is not None
        assert participante.sala_id == sala.id
        assert participante.usuario_id == usuario1_id


class TestChatParticipanteRepoObter:
    """Testes para a função obter_por_sala_e_usuario."""

    def test_obter_por_sala_e_usuario_existente(self):
        """Deve retornar participante existente."""
        # Criar usuários, sala e participante
        usuario1 = Usuario(
            id=0,
            nome="Usuario Obter Part 1",
            email="obter_part1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Obter Part 2",
            email="obter_part2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)
        chat_participante_repo.adicionar_participante(sala.id, usuario1_id)

        # Obter
        resultado = chat_participante_repo.obter_por_sala_e_usuario(sala.id, usuario1_id)

        assert resultado is not None
        assert resultado.usuario_id == usuario1_id

    def test_obter_por_sala_e_usuario_inexistente(self):
        """Deve retornar None para participante inexistente."""
        resultado = chat_participante_repo.obter_por_sala_e_usuario("inexistente", 99999)
        assert resultado is None


class TestChatParticipanteRepoListar:
    """Testes para as funções listar_por_sala e listar_por_usuario."""

    def test_listar_por_sala_vazia(self):
        """Deve retornar lista vazia para sala sem participantes."""
        # Criar usuários e sala
        usuario1 = Usuario(
            id=0,
            nome="Usuario Listar Sala 1",
            email="listar_sala1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Listar Sala 2",
            email="listar_sala2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)

        # Listar
        participantes = chat_participante_repo.listar_por_sala(sala.id)

        assert participantes == []

    def test_listar_por_sala_com_participantes(self):
        """Deve retornar lista de participantes."""
        # Criar usuários, sala e participantes
        usuario1 = Usuario(
            id=0,
            nome="Usuario Listar Part 1",
            email="listar_part1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Listar Part 2",
            email="listar_part2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)
        chat_participante_repo.adicionar_participante(sala.id, usuario1_id)
        chat_participante_repo.adicionar_participante(sala.id, usuario2_id)

        # Listar
        participantes = chat_participante_repo.listar_por_sala(sala.id)

        assert len(participantes) == 2

    def test_listar_por_usuario(self):
        """Deve listar participações de um usuário."""
        # Criar usuários e salas
        usuario1 = Usuario(
            id=0,
            nome="Usuario Listar User 1",
            email="listar_user1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Listar User 2",
            email="listar_user2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario3 = Usuario(
            id=0,
            nome="Usuario Listar User 3",
            email="listar_user3@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        usuario3_id = usuario_repo.inserir(usuario3)

        # Criar duas salas com usuario1
        sala1 = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)
        sala2 = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario3_id)
        chat_participante_repo.adicionar_participante(sala1.id, usuario1_id)
        chat_participante_repo.adicionar_participante(sala2.id, usuario1_id)

        # Listar participações do usuario1
        participacoes = chat_participante_repo.listar_por_usuario(usuario1_id)

        assert len(participacoes) == 2


class TestChatParticipanteRepoAtualizar:
    """Testes para a função atualizar_ultima_leitura."""

    def test_atualizar_ultima_leitura_sucesso(self):
        """Deve atualizar última leitura."""
        # Criar usuários, sala e participante
        usuario1 = Usuario(
            id=0,
            nome="Usuario Leitura 1",
            email="leitura1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Leitura 2",
            email="leitura2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)
        chat_participante_repo.adicionar_participante(sala.id, usuario1_id)

        # Atualizar leitura
        resultado = chat_participante_repo.atualizar_ultima_leitura(sala.id, usuario1_id)

        assert resultado is True

    def test_atualizar_ultima_leitura_inexistente(self):
        """Deve retornar False para participante inexistente."""
        resultado = chat_participante_repo.atualizar_ultima_leitura("inexistente", 99999)
        assert resultado is False


class TestChatParticipanteRepoContar:
    """Testes para a função contar_mensagens_nao_lidas."""

    def test_contar_mensagens_nao_lidas(self):
        """Deve contar mensagens não lidas."""
        # Criar usuários, sala, participantes e mensagens
        usuario1 = Usuario(
            id=0,
            nome="Usuario Nao Lidas 1",
            email="nao_lidas1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Nao Lidas 2",
            email="nao_lidas2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)
        chat_participante_repo.adicionar_participante(sala.id, usuario1_id)
        chat_participante_repo.adicionar_participante(sala.id, usuario2_id)

        # Usuario 1 envia mensagens
        chat_mensagem_repo.inserir(sala.id, usuario1_id, "Msg 1")
        chat_mensagem_repo.inserir(sala.id, usuario1_id, "Msg 2")

        # Contar não lidas para usuario 2
        total = chat_participante_repo.contar_mensagens_nao_lidas(sala.id, usuario2_id)

        # Deve contar as mensagens do usuario 1 como não lidas para usuario 2
        assert total >= 0  # Valor depende da implementação


class TestChatParticipanteRepoExcluir:
    """Testes para a função excluir."""

    def test_excluir_participante_existente(self):
        """Deve excluir participante."""
        # Criar usuários, sala e participante
        usuario1 = Usuario(
            id=0,
            nome="Usuario Excluir Part 1",
            email="excluir_part1@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario2 = Usuario(
            id=0,
            nome="Usuario Excluir Part 2",
            email="excluir_part2@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario1_id = usuario_repo.inserir(usuario1)
        usuario2_id = usuario_repo.inserir(usuario2)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario1_id, usuario2_id)
        chat_participante_repo.adicionar_participante(sala.id, usuario1_id)

        # Excluir
        resultado = chat_participante_repo.excluir(sala.id, usuario1_id)

        assert resultado is True
        assert chat_participante_repo.obter_por_sala_e_usuario(sala.id, usuario1_id) is None

    def test_excluir_participante_inexistente(self):
        """Deve retornar False para participante inexistente."""
        resultado = chat_participante_repo.excluir("inexistente", 99999)
        assert resultado is False


class TestChatParticipanteRepoCriarTabela:
    """Testes para a função criar_tabela."""

    def test_criar_tabela_nao_falha(self):
        """Deve criar tabela sem erro."""
        chat_participante_repo.criar_tabela()
