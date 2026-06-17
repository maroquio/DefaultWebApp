"""
Configuracao de testes unitarios.

Testes unitarios testam funcoes e classes isoladamente,
usando mocks quando necessario. Nao dependem de banco de dados
ou requisicoes HTTP reais.

As fixtures do conftest.py principal sao herdadas automaticamente.
"""
import pytest


# Marca todos os testes nesta pasta como unitarios
def pytest_collection_modifyitems(items):
    """Adiciona marca 'unit' a todos os testes nesta pasta."""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
