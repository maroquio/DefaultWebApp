"""
Configuracao de testes de integracao.

Testes de integracao testam multiplos componentes juntos,
incluindo banco de dados, requisicoes HTTP via TestClient,
e interacao entre camadas da aplicacao.

As fixtures do conftest.py principal sao herdadas automaticamente.
"""
import pytest


# Marca todos os testes nesta pasta como de integracao
def pytest_collection_modifyitems(items):
    """Adiciona marca 'integration' a todos os testes nesta pasta."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="function", autouse=True)
def criar_tabelas_integracao():
    """
    Cria todas as tabelas necessarias para testes de integracao.

    Esta fixture e herdada por todos os testes em repos/ e routes/,
    garantindo que as tabelas existam no banco de dados de teste.
    Substitui as fixtures duplicadas criar_tabelas_repos e criar_tabelas_rotas.
    """
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
