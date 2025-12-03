"""
Configuracao especifica para testes de repositorios.

Cria as tabelas necessarias antes dos testes de repo.
"""
import pytest


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
