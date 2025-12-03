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
