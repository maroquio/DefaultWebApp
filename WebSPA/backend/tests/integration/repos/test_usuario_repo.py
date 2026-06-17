"""
Testes de integração para o repositório de usuários.

Testa as operações CRUD e funções auxiliares do usuario_repo.
"""
import pytest
from datetime import timedelta

from repo import usuario_repo
from model.usuario_model import Usuario
from util.security import criar_hash_senha
from util.datetime_util import agora
from util.perfis import Perfil


class TestUsuarioRepoInserir:
    """Testes para a função inserir."""

    def test_inserir_usuario_retorna_id(self):
        """Deve inserir usuário e retornar ID."""
        usuario = Usuario(
            id=0,
            nome="Teste Inserir",
            email="inserir@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )

        usuario_id = usuario_repo.inserir(usuario)

        assert usuario_id is not None
        assert usuario_id > 0

    def test_inserir_usuario_com_perfil_vendedor(self):
        """Deve inserir usuário vendedor corretamente."""
        usuario = Usuario(
            id=0,
            nome="Vendedor Teste",
            email="vendedor@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.VENDEDOR.value
        )

        usuario_id = usuario_repo.inserir(usuario)

        assert usuario_id is not None
        usuario_salvo = usuario_repo.obter_por_id(usuario_id)
        assert usuario_salvo.perfil == Perfil.VENDEDOR.value

    def test_inserir_usuario_com_perfil_admin(self):
        """Deve inserir usuário admin corretamente."""
        usuario = Usuario(
            id=0,
            nome="Admin Teste",
            email="admin_repo@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.ADMIN.value
        )

        usuario_id = usuario_repo.inserir(usuario)

        assert usuario_id is not None
        usuario_salvo = usuario_repo.obter_por_id(usuario_id)
        assert usuario_salvo.perfil == Perfil.ADMIN.value


class TestUsuarioRepoObterPorId:
    """Testes para a função obter_por_id."""

    def test_obter_por_id_existente(self):
        """Deve retornar usuário quando ID existe."""
        usuario = Usuario(
            id=0,
            nome="Teste Obter",
            email="obter@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_id = usuario_repo.inserir(usuario)

        resultado = usuario_repo.obter_por_id(usuario_id)

        assert resultado is not None
        assert resultado.id == usuario_id
        assert resultado.nome == "Teste Obter"
        assert resultado.email == "obter@example.com"

    def test_obter_por_id_inexistente(self):
        """Deve retornar None quando ID não existe."""
        resultado = usuario_repo.obter_por_id(99999)

        assert resultado is None


class TestUsuarioRepoObterPorEmail:
    """Testes para a função obter_por_email."""

    def test_obter_por_email_existente(self):
        """Deve retornar usuário quando email existe."""
        usuario = Usuario(
            id=0,
            nome="Teste Email",
            email="email_teste@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_repo.inserir(usuario)

        resultado = usuario_repo.obter_por_email("email_teste@example.com")

        assert resultado is not None
        assert resultado.email == "email_teste@example.com"
        assert resultado.nome == "Teste Email"

    def test_obter_por_email_inexistente(self):
        """Deve retornar None quando email não existe."""
        resultado = usuario_repo.obter_por_email("naoexiste@example.com")

        assert resultado is None


class TestUsuarioRepoAlterar:
    """Testes para a função alterar."""

    def test_alterar_usuario_existente(self):
        """Deve alterar dados do usuário existente."""
        usuario = Usuario(
            id=0,
            nome="Nome Original",
            email="alterar@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_id = usuario_repo.inserir(usuario)

        usuario.id = usuario_id
        usuario.nome = "Nome Alterado"
        usuario.email = "alterado@example.com"
        resultado = usuario_repo.alterar(usuario)

        assert resultado is True
        usuario_alterado = usuario_repo.obter_por_id(usuario_id)
        assert usuario_alterado.nome == "Nome Alterado"
        assert usuario_alterado.email == "alterado@example.com"

    def test_alterar_perfil_usuario(self):
        """Deve alterar perfil do usuário."""
        usuario = Usuario(
            id=0,
            nome="Teste Perfil",
            email="perfil@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_id = usuario_repo.inserir(usuario)

        usuario.id = usuario_id
        usuario.perfil = Perfil.VENDEDOR.value
        resultado = usuario_repo.alterar(usuario)

        assert resultado is True
        usuario_alterado = usuario_repo.obter_por_id(usuario_id)
        assert usuario_alterado.perfil == Perfil.VENDEDOR.value

    def test_alterar_usuario_inexistente(self):
        """Deve retornar False quando usuário não existe."""
        usuario = Usuario(
            id=99999,
            nome="Inexistente",
            email="inexistente@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )

        resultado = usuario_repo.alterar(usuario)

        assert resultado is False


class TestUsuarioRepoAtualizarSenha:
    """Testes para a função atualizar_senha."""

    def test_atualizar_senha_usuario_existente(self):
        """Deve atualizar senha do usuário existente."""
        usuario = Usuario(
            id=0,
            nome="Teste Senha",
            email="senha@example.com",
            senha=criar_hash_senha("SenhaAntiga@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_id = usuario_repo.inserir(usuario)

        nova_senha = criar_hash_senha("SenhaNova@456")
        resultado = usuario_repo.atualizar_senha(usuario_id, nova_senha)

        assert resultado is True
        usuario_atualizado = usuario_repo.obter_por_id(usuario_id)
        assert usuario_atualizado.senha == nova_senha

    def test_atualizar_senha_usuario_inexistente(self):
        """Deve retornar False quando usuário não existe."""
        resultado = usuario_repo.atualizar_senha(99999, "nova_senha_hash")

        assert resultado is False


class TestUsuarioRepoExcluir:
    """Testes para a função excluir."""

    def test_excluir_usuario_existente(self):
        """Deve excluir usuário existente."""
        usuario = Usuario(
            id=0,
            nome="Teste Excluir",
            email="excluir@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_id = usuario_repo.inserir(usuario)

        resultado = usuario_repo.excluir(usuario_id)

        assert resultado is True
        usuario_excluido = usuario_repo.obter_por_id(usuario_id)
        assert usuario_excluido is None

    def test_excluir_usuario_inexistente(self):
        """Deve retornar False quando usuário não existe."""
        resultado = usuario_repo.excluir(99999)

        assert resultado is False


class TestUsuarioRepoObterTodos:
    """Testes para a função obter_todos."""

    def test_obter_todos_com_usuarios(self):
        """Deve retornar lista de todos os usuários."""
        # Inserir alguns usuários
        for i in range(3):
            usuario = Usuario(
                id=0,
                nome=f"Usuario {i}",
                email=f"todos{i}@example.com",
                senha=criar_hash_senha("Senha@123"),
                perfil=Perfil.CLIENTE.value
            )
            usuario_repo.inserir(usuario)

        resultado = usuario_repo.obter_todos()

        assert isinstance(resultado, list)
        assert len(resultado) >= 3


class TestUsuarioRepoObterQuantidade:
    """Testes para a função obter_quantidade."""

    def test_obter_quantidade_com_usuarios(self):
        """Deve retornar quantidade correta de usuários."""
        # Inserir usuário
        usuario = Usuario(
            id=0,
            nome="Teste Quantidade",
            email="quantidade@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_repo.inserir(usuario)

        quantidade = usuario_repo.obter_quantidade()

        assert isinstance(quantidade, int)
        assert quantidade >= 1


class TestUsuarioRepoObterTodosPorPerfil:
    """Testes para a função obter_todos_por_perfil."""

    def test_obter_todos_por_perfil_cliente(self):
        """Deve retornar apenas usuários com perfil Cliente."""
        # Inserir usuários de diferentes perfis
        cliente = Usuario(
            id=0,
            nome="Cliente Perfil",
            email="cliente_perfil@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        vendedor = Usuario(
            id=0,
            nome="Vendedor Perfil",
            email="vendedor_perfil@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.VENDEDOR.value
        )
        usuario_repo.inserir(cliente)
        usuario_repo.inserir(vendedor)

        resultado = usuario_repo.obter_todos_por_perfil(Perfil.CLIENTE.value)

        assert isinstance(resultado, list)
        for usuario in resultado:
            assert usuario.perfil == Perfil.CLIENTE.value

    def test_obter_todos_por_perfil_vendedor(self):
        """Deve retornar apenas usuários com perfil Vendedor."""
        vendedor = Usuario(
            id=0,
            nome="Vendedor Filtro",
            email="vendedor_filtro@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.VENDEDOR.value
        )
        usuario_repo.inserir(vendedor)

        resultado = usuario_repo.obter_todos_por_perfil(Perfil.VENDEDOR.value)

        assert isinstance(resultado, list)
        for usuario in resultado:
            assert usuario.perfil == Perfil.VENDEDOR.value


class TestUsuarioRepoBuscarPorTermo:
    """Testes para a função buscar_por_termo."""

    def test_buscar_por_termo_nome(self):
        """Deve encontrar usuário por parte do nome."""
        usuario = Usuario(
            id=0,
            nome="Fulano Buscavel",
            email="fulano_busca@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_repo.inserir(usuario)

        resultado = usuario_repo.buscar_por_termo("Buscavel")

        assert len(resultado) >= 1
        assert any(u.nome == "Fulano Buscavel" for u in resultado)

    def test_buscar_por_termo_email(self):
        """Deve encontrar usuário por parte do email."""
        usuario = Usuario(
            id=0,
            nome="Usuario Email",
            email="busca_email_teste@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_repo.inserir(usuario)

        resultado = usuario_repo.buscar_por_termo("busca_email_teste")

        assert len(resultado) >= 1
        assert any(u.email == "busca_email_teste@example.com" for u in resultado)

    def test_buscar_por_termo_inexistente(self):
        """Deve retornar lista vazia quando termo não encontra nada."""
        resultado = usuario_repo.buscar_por_termo("xyztermoqueNaoExiste123")

        assert isinstance(resultado, list)
        assert len(resultado) == 0

    def test_buscar_por_termo_com_limite(self):
        """Deve respeitar limite de resultados."""
        # Inserir vários usuários com termo comum
        for i in range(5):
            usuario = Usuario(
                id=0,
                nome=f"Limite Teste {i}",
                email=f"limite{i}@example.com",
                senha=criar_hash_senha("Senha@123"),
                perfil=Perfil.CLIENTE.value
            )
            usuario_repo.inserir(usuario)

        resultado = usuario_repo.buscar_por_termo("Limite Teste", limit=3)

        assert len(resultado) <= 3


class TestUsuarioRepoToken:
    """Testes para funções de token de redefinição de senha."""

    def test_atualizar_token(self):
        """Deve atualizar token de redefinição."""
        usuario = Usuario(
            id=0,
            nome="Teste Token",
            email="token@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_repo.inserir(usuario)

        token = "abc123token"
        data_expiracao = agora() + timedelta(hours=1)
        resultado = usuario_repo.atualizar_token("token@example.com", token, data_expiracao)

        assert resultado is True

    def test_obter_por_token_existente(self):
        """Deve retornar usuário pelo token."""
        usuario = Usuario(
            id=0,
            nome="Teste Obter Token",
            email="obter_token@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_repo.inserir(usuario)

        token = "token_obtencao_123"
        data_expiracao = agora() + timedelta(hours=1)
        usuario_repo.atualizar_token("obter_token@example.com", token, data_expiracao)

        resultado = usuario_repo.obter_por_token(token)

        assert resultado is not None
        assert resultado.email == "obter_token@example.com"

    def test_obter_por_token_inexistente(self):
        """Deve retornar None quando token não existe."""
        resultado = usuario_repo.obter_por_token("token_que_nao_existe")

        assert resultado is None

    def test_limpar_token(self):
        """Deve limpar token do usuário."""
        usuario = Usuario(
            id=0,
            nome="Teste Limpar Token",
            email="limpar_token@example.com",
            senha=criar_hash_senha("Senha@123"),
            perfil=Perfil.CLIENTE.value
        )
        usuario_id = usuario_repo.inserir(usuario)

        # Definir token
        token = "token_para_limpar"
        data_expiracao = agora() + timedelta(hours=1)
        usuario_repo.atualizar_token("limpar_token@example.com", token, data_expiracao)

        # Limpar token
        resultado = usuario_repo.limpar_token(usuario_id)

        assert resultado is True
        usuario_atualizado = usuario_repo.obter_por_token(token)
        assert usuario_atualizado is None

    def test_limpar_token_usuario_inexistente(self):
        """Deve retornar False quando usuário não existe."""
        resultado = usuario_repo.limpar_token(99999)

        assert resultado is False


class TestUsuarioRepoCriarTabela:
    """Testes para a função criar_tabela."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar/verificar tabela."""
        resultado = usuario_repo.criar_tabela()

        assert resultado is True
