"""
Testes de rotas públicas
Testa páginas acessíveis sem autenticação (landing page, sobre, etc.)
"""
from fastapi import status
from unittest.mock import patch
import pytest


class TestRotasPublicas:
    """Testes de rotas públicas"""

    def test_home_acessivel_sem_autenticacao(self, client):
        """Landing page deve ser acessível sem autenticação"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK

    def test_index_acessivel_sem_autenticacao(self, client):
        """Página index deve ser acessível sem autenticação"""
        response = client.get("/index")
        assert response.status_code == status.HTTP_200_OK

    def test_sobre_acessivel_sem_autenticacao(self, client):
        """Página sobre deve ser acessível sem autenticação"""
        response = client.get("/sobre")
        assert response.status_code == status.HTTP_200_OK

    def test_home_contem_conteudo(self, client):
        """Landing page deve conter conteúdo relevante"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        # Deve ter algum conteúdo HTML
        assert len(response.text) > 100

    def test_sobre_contem_informacoes(self, client):
        """Página sobre deve conter informações do projeto"""
        response = client.get("/sobre")
        assert response.status_code == status.HTTP_200_OK
        # Deve ter conteúdo relevante
        assert "sobre" in response.text.lower() or "projeto" in response.text.lower()


class TestRotasPublicasComUsuarioLogado:
    """Testes de rotas públicas acessadas por usuário logado"""

    def test_home_acessivel_usuario_logado(self, cliente_autenticado):
        """Usuário logado também pode acessar landing page"""
        response = cliente_autenticado.get("/")
        assert response.status_code == status.HTTP_200_OK

    def test_sobre_acessivel_usuario_logado(self, cliente_autenticado):
        """Usuário logado pode acessar página sobre"""
        response = cliente_autenticado.get("/sobre")
        assert response.status_code == status.HTTP_200_OK

    def test_home_acessivel_admin_logado(self, admin_autenticado):
        """Admin logado pode acessar landing page"""
        response = admin_autenticado.get("/")
        assert response.status_code == status.HTTP_200_OK

    def test_sobre_acessivel_admin_logado(self, admin_autenticado):
        """Admin logado pode acessar página sobre"""
        response = admin_autenticado.get("/sobre")
        assert response.status_code == status.HTTP_200_OK


class TestExemplos:
    """Testes de rotas de exemplos"""

    def test_exemplos_index_acessivel(self, client):
        """Página de exemplos deve ser acessível"""
        response = client.get("/exemplos")
        assert response.status_code == status.HTTP_200_OK

    def test_exemplo_campos_formulario(self, client):
        """Exemplo de campos de formulário deve ser acessível"""
        response = client.get("/exemplos/campos-formulario")
        assert response.status_code == status.HTTP_200_OK

    def test_exemplo_grade_cartoes(self, client):
        """Exemplo de grade de cartões deve ser acessível"""
        response = client.get("/exemplos/grade-cartoes")
        assert response.status_code == status.HTTP_200_OK

    def test_exemplo_bootswatch(self, client):
        """Exemplo de temas Bootswatch deve ser acessível"""
        response = client.get("/exemplos/bootswatch")
        assert response.status_code == status.HTTP_200_OK

    def test_exemplo_detalhes_produto(self, client):
        """Exemplo de detalhes de produto deve ser acessível"""
        response = client.get("/exemplos/detalhes-produto")
        assert response.status_code == status.HTTP_200_OK

    def test_exemplo_detalhes_servico(self, client):
        """Exemplo de detalhes de serviço deve ser acessível"""
        response = client.get("/exemplos/detalhes-servico")
        assert response.status_code == status.HTTP_200_OK

    def test_exemplo_detalhes_perfil(self, client):
        """Exemplo de detalhes de perfil deve ser acessível"""
        response = client.get("/exemplos/detalhes-perfil")
        assert response.status_code == status.HTTP_200_OK

    def test_exemplo_detalhes_imovel(self, client):
        """Exemplo de detalhes de imóvel deve ser acessível"""
        response = client.get("/exemplos/detalhes-imovel")
        assert response.status_code == status.HTTP_200_OK

    def test_exemplo_lista_tabela(self, client):
        """Exemplo de lista em tabela deve ser acessível"""
        response = client.get("/exemplos/lista-tabela")
        assert response.status_code == status.HTTP_200_OK

    def test_exemplo_lista_tabela_tem_dados(self, client):
        """Exemplo de lista em tabela deve conter dados mockados"""
        response = client.get("/exemplos/lista-tabela")
        assert response.status_code == status.HTTP_200_OK
        # Deve ter conteúdo de exemplo
        assert len(response.text) > 500


class TestHealthCheck:
    """Testes de health check"""

    def test_health_check_endpoint(self, client):
        """Endpoint /health deve retornar status"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        # Deve retornar JSON com status
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_check_sem_autenticacao(self, client):
        """Health check deve ser acessível sem autenticação"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK


class TestErros:
    """Testes de páginas de erro"""

    def test_pagina_404_em_rota_inexistente(self, client):
        """Rota inexistente deve retornar 404"""
        response = client.get("/rota-que-nao-existe-xyz123")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_pagina_404_contem_mensagem(self, client):
        """Página 404 deve conter mensagem amigável"""
        response = client.get("/rota-inexistente")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # Deve ter alguma mensagem sobre não encontrado
        assert "404" in response.text or "não encontrad" in response.text.lower()


class TestPublicRateLimiting:
    """Testes de rate limiting para páginas públicas"""

    @pytest.fixture
    def mock_rate_limit_block(self):
        """Fixture para mockar rate limiter que bloqueia"""
        with patch('routes.public_routes.public_limiter') as mock_limiter:
            mock_limiter.verificar.return_value = False
            yield mock_limiter

    def test_rate_limit_home(self, client, mock_rate_limit_block):
        """Rate limit na página home"""
        response = client.get("/")

        assert response.status_code == 429

    def test_rate_limit_index(self, client, mock_rate_limit_block):
        """Rate limit na página index"""
        response = client.get("/index")

        assert response.status_code == 429

    def test_rate_limit_sobre(self, client, mock_rate_limit_block):
        """Rate limit na página sobre"""
        response = client.get("/sobre")

        assert response.status_code == 429
