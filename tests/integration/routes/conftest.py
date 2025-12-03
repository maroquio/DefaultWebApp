"""
Configuracoes especificas para testes de rotas.

Fornece fixtures reutilizaveis para testes de integracao de rotas.
A criacao de tabelas e feita pela fixture criar_tabelas_integracao
no conftest.py do nivel de integracao.
"""
import pytest

from model.chamado_model import Chamado, StatusChamado, PrioridadeChamado
from model.chamado_interacao_model import ChamadoInteracao, TipoInteracao
from repo import chamado_repo, chamado_interacao_repo, usuario_repo


@pytest.fixture(scope="function")
def criar_chamado_admin(admin_autenticado, admin_teste):
    """
    Cria um chamado de teste para cenarios de admin.

    Cria um usuario cliente e um chamado associado a ele,
    para que o admin possa responder/fechar/reabrir.

    Returns:
        int: ID do chamado criado
    """
    from model.usuario_model import Usuario
    from util.security import criar_hash_senha
    from util.perfis import Perfil

    # Criar um usuario cliente para associar ao chamado
    cliente = Usuario(
        id=0,
        nome="Cliente Chamado Teste",
        email="cliente_chamado@example.com",
        senha=criar_hash_senha("Senha@123"),
        perfil=Perfil.CLIENTE.value
    )
    cliente_id = usuario_repo.inserir(cliente)

    # Criar chamado associado ao cliente
    chamado = Chamado(
        id=0,
        titulo="Chamado de Teste Admin",
        status=StatusChamado.ABERTO,
        prioridade=PrioridadeChamado.MEDIA,
        usuario_id=cliente_id
    )
    chamado_id = chamado_repo.inserir(chamado)

    # Criar interacao inicial (abertura do chamado)
    interacao = ChamadoInteracao(
        id=0,
        chamado_id=chamado_id,
        usuario_id=cliente_id,
        mensagem="Descricao do problema inicial para teste",
        tipo=TipoInteracao.ABERTURA,
        data_interacao=None,
        status_resultante=StatusChamado.ABERTO.value
    )
    chamado_interacao_repo.inserir(interacao)

    return chamado_id
