"""
Testes para as rotas de exemplos (routes/examples_routes.py)

Testa rate limiting e acesso às páginas de exemplos.
"""

import pytest
from unittest.mock import patch


class TestExamplesRateLimiting:
    """Testes de rate limiting para páginas de exemplos"""

    @pytest.fixture
    def mock_rate_limit_block(self):
        """Fixture para mockar rate limiter que bloqueia"""
        with patch('routes.examples_routes.examples_limiter') as mock_limiter:
            mock_limiter.verificar.return_value = False
            yield mock_limiter

    def test_rate_limit_index(self, client, mock_rate_limit_block):
        """Rate limit na página index de exemplos"""
        response = client.get("/exemplos/")

        assert response.status_code == 429

    def test_rate_limit_campos_formulario(self, client, mock_rate_limit_block):
        """Rate limit na página de campos de formulário"""
        response = client.get("/exemplos/campos-formulario")

        assert response.status_code == 429

    def test_rate_limit_grade_cartoes(self, client, mock_rate_limit_block):
        """Rate limit na página de grade de cartões"""
        response = client.get("/exemplos/grade-cartoes")

        assert response.status_code == 429

    def test_rate_limit_lista_tabela(self, client, mock_rate_limit_block):
        """Rate limit na página de lista tabela"""
        response = client.get("/exemplos/lista-tabela")

        assert response.status_code == 429

    def test_rate_limit_detalhes_produto(self, client, mock_rate_limit_block):
        """Rate limit na página de detalhes de produto"""
        response = client.get("/exemplos/detalhes-produto")

        assert response.status_code == 429

    def test_rate_limit_detalhes_servico(self, client, mock_rate_limit_block):
        """Rate limit na página de detalhes de serviço"""
        response = client.get("/exemplos/detalhes-servico")

        assert response.status_code == 429

    def test_rate_limit_detalhes_imovel(self, client, mock_rate_limit_block):
        """Rate limit na página de detalhes de imóvel"""
        response = client.get("/exemplos/detalhes-imovel")

        assert response.status_code == 429

    def test_rate_limit_detalhes_perfil(self, client, mock_rate_limit_block):
        """Rate limit na página de detalhes de perfil"""
        response = client.get("/exemplos/detalhes-perfil")

        assert response.status_code == 429

    def test_rate_limit_bootswatch(self, client, mock_rate_limit_block):
        """Rate limit na página de bootswatch"""
        response = client.get("/exemplos/bootswatch")

        assert response.status_code == 429


class TestExamplesAccess:
    """Testes de acesso normal às páginas de exemplos"""

    def test_acesso_index(self, client):
        """Deve acessar página index de exemplos"""
        response = client.get("/exemplos/")

        assert response.status_code == 200

    def test_acesso_campos_formulario(self, client):
        """Deve acessar página de campos de formulário"""
        response = client.get("/exemplos/campos-formulario")

        assert response.status_code == 200

    def test_acesso_grade_cartoes(self, client):
        """Deve acessar página de grade de cartões"""
        response = client.get("/exemplos/grade-cartoes")

        assert response.status_code == 200

    def test_acesso_lista_tabela(self, client):
        """Deve acessar página de lista tabela"""
        response = client.get("/exemplos/lista-tabela")

        assert response.status_code == 200

    def test_acesso_detalhes_produto(self, client):
        """Deve acessar página de detalhes de produto"""
        response = client.get("/exemplos/detalhes-produto")

        assert response.status_code == 200

    def test_acesso_detalhes_servico(self, client):
        """Deve acessar página de detalhes de serviço"""
        response = client.get("/exemplos/detalhes-servico")

        assert response.status_code == 200

    def test_acesso_detalhes_imovel(self, client):
        """Deve acessar página de detalhes de imóvel"""
        response = client.get("/exemplos/detalhes-imovel")

        assert response.status_code == 200

    def test_acesso_detalhes_perfil(self, client):
        """Deve acessar página de detalhes de perfil"""
        response = client.get("/exemplos/detalhes-perfil")

        assert response.status_code == 200

    def test_acesso_bootswatch(self, client):
        """Deve acessar página de bootswatch"""
        response = client.get("/exemplos/bootswatch")

        assert response.status_code == 200
