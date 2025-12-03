"""
Configuracao especifica para testes de repositorios.

Cria as tabelas necessarias antes dos testes de repo.
Fornece fixtures reutilizaveis para testes de repos.
"""
import pytest

from repo import usuario_repo, chamado_repo, chamado_interacao_repo
from model.usuario_model import Usuario
from model.chamado_model import Chamado, StatusChamado, PrioridadeChamado
from model.chamado_interacao_model import ChamadoInteracao, TipoInteracao
from util.security import criar_hash_senha
from util.perfis import Perfil


@pytest.fixture(scope="function", autouse=True)
def criar_tabelas_repos():
    """
    Cria as tabelas necessarias para os testes de repositorio.

    Esta fixture roda antes de cada teste para garantir que
    as tabelas existam no banco de dados de teste.
    """
    # Importar repos apos configuracao do banco (feita no conftest.py principal)
    from repo import (
        usuario_repo,
        chamado_repo,
        chamado_interacao_repo,
        configuracao_repo,
        indices_repo,
        chat_sala_repo,
        chat_participante_repo,
        chat_mensagem_repo,
    )

    # Criar tabelas na ordem correta (respeitando dependencias)
    usuario_repo.criar_tabela()
    configuracao_repo.criar_tabela()
    chamado_repo.criar_tabela()
    chamado_interacao_repo.criar_tabela()
    indices_repo.criar_indices()
    chat_sala_repo.criar_tabela()
    chat_participante_repo.criar_tabela()
    chat_mensagem_repo.criar_tabela()

    yield

    # Nao precisa limpar - o conftest.py principal ja faz isso


# ============================================================================
# FIXTURES REUTILIZAVEIS PARA TESTES DE REPOS
# ============================================================================


@pytest.fixture
def usuario_repo_teste():
    """
    Cria um usuario para associar a entidades que requerem FK de usuario.

    Returns:
        int: ID do usuario criado
    """
    usuario = Usuario(
        id=0,
        nome="Usuario Repo Teste",
        email="usuario_repo@example.com",
        senha=criar_hash_senha("Senha@123"),
        perfil=Perfil.CLIENTE.value
    )
    usuario_id = usuario_repo.inserir(usuario)
    return usuario_id


@pytest.fixture
def admin_repo_teste():
    """
    Cria um usuario admin para testes que requerem perfil administrativo.

    Returns:
        int: ID do admin criado
    """
    usuario = Usuario(
        id=0,
        nome="Admin Repo Teste",
        email="admin_repo@example.com",
        senha=criar_hash_senha("Senha@123"),
        perfil=Perfil.ADMIN.value
    )
    usuario_id = usuario_repo.inserir(usuario)
    return usuario_id


@pytest.fixture
def chamado_repo_teste(usuario_repo_teste):
    """
    Cria um chamado de teste associado a um usuario.

    Args:
        usuario_repo_teste: Fixture que fornece ID do usuario

    Returns:
        int: ID do chamado criado
    """
    chamado = Chamado(
        id=0,
        titulo="Chamado Repo Teste",
        status=StatusChamado.ABERTO,
        prioridade=PrioridadeChamado.MEDIA,
        usuario_id=usuario_repo_teste
    )
    chamado_id = chamado_repo.inserir(chamado)
    return chamado_id


@pytest.fixture
def interacao_repo_teste(chamado_repo_teste, usuario_repo_teste):
    """
    Cria uma interacao de teste para um chamado.

    Args:
        chamado_repo_teste: Fixture que fornece ID do chamado
        usuario_repo_teste: Fixture que fornece ID do usuario

    Returns:
        int: ID da interacao criada
    """
    interacao = ChamadoInteracao(
        id=0,
        chamado_id=chamado_repo_teste,
        usuario_id=usuario_repo_teste,
        mensagem="Mensagem de teste",
        tipo=TipoInteracao.ABERTURA,
        data_interacao=None,
        status_resultante=StatusChamado.ABERTO.value
    )
    interacao_id = chamado_interacao_repo.inserir(interacao)
    return interacao_id
