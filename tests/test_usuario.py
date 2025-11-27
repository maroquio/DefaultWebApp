"""
Testes de rotas do usuário
Testa acesso ao dashboard do usuário autenticado
"""
from fastapi import status


class TestDashboard:
    """Testes do dashboard do usuário"""

    def test_dashboard_requer_autenticacao(self, client):
        """Deve exigir autenticação para acessar dashboard"""
        response = client.get("/usuario", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_dashboard_usuario_autenticado(self, cliente_autenticado, usuario_teste):
        """Usuário autenticado deve acessar dashboard"""
        response = cliente_autenticado.get("/usuario")
        assert response.status_code == status.HTTP_200_OK
        # Deve exibir dados do usuário
        assert usuario_teste["nome"] in response.text

    def test_dashboard_exibe_dados_usuario(self, cliente_autenticado, usuario_teste):
        """Dashboard deve exibir informações do usuário logado"""
        response = cliente_autenticado.get("/usuario")
        assert response.status_code == status.HTTP_200_OK
        # Verificar que informações do usuário estão presentes
        assert usuario_teste["nome"] in response.text
        # Email pode ou não ser exibido dependendo do design da página

    def test_dashboard_admin_acessa(self, admin_autenticado, admin_teste):
        """Admin também deve poder acessar seu dashboard"""
        response = admin_autenticado.get("/usuario")
        assert response.status_code == status.HTTP_200_OK
        assert admin_teste["nome"] in response.text

    def test_dashboard_vendedor_acessa(self, vendedor_autenticado, vendedor_teste):
        """Vendedor também deve poder acessar seu dashboard"""
        response = vendedor_autenticado.get("/usuario")
        assert response.status_code == status.HTTP_200_OK
        assert vendedor_teste["nome"] in response.text
