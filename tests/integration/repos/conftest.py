"""
Configuracao especifica para testes de repositorios.

Fornece fixtures reutilizaveis para testes de repos.
A criacao de tabelas e feita pela fixture criar_tabelas_integracao
no conftest.py do nivel de integracao.
"""
import pytest

from repo import usuario_repo, chamado_repo, chamado_interacao_repo
from model.usuario_model import Usuario
from model.chamado_model import Chamado, StatusChamado, PrioridadeChamado
from model.chamado_interacao_model import ChamadoInteracao, TipoInteracao
from util.security import criar_hash_senha
from util.perfis import Perfil


# ============================================================================
# FIXTURES REUTILIZAVEIS PARA TESTES DE REPOS
# ============================================================================


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
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
