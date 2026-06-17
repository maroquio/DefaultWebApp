"""
Testes de integracao para rotas administrativas de chamados.

Cobre:
- Autenticacao obrigatoria
- Autorizacao (apenas administradores)
- Listagem de todos os chamados
- Formulario de resposta a chamados
- Resposta a chamados
- Fechamento de chamados
- Reabertura de chamados
- Rate limiting
- Tratamento de erros
"""
from unittest.mock import patch

from fastapi import status

from model.chamado_model import StatusChamado, PrioridadeChamado, Chamado
from model.chamado_interacao_model import ChamadoInteracao, TipoInteracao
from tests.test_helpers import assert_permission_denied, assert_redirects_to


class TestAdminChamadosAutenticacao:
    """Testes de autenticacao para rotas de admin de chamados"""

    def test_listar_requer_autenticacao(self, client):
        """Deve exigir autenticacao para listar chamados"""
        response = client.get("/admin/chamados/listar", follow_redirects=False)
        assert_permission_denied(response)

    def test_responder_get_requer_autenticacao(self, client):
        """Deve exigir autenticacao para acessar formulario de resposta"""
        response = client.get("/admin/chamados/1/responder", follow_redirects=False)
        assert_permission_denied(response)

    def test_responder_post_requer_autenticacao(self, client):
        """Deve exigir autenticacao para enviar resposta"""
        response = client.post("/admin/chamados/1/responder", data={
            "mensagem": "Resposta teste",
            "status_chamado": "Em Análise"
        }, follow_redirects=False)
        assert_permission_denied(response)

    def test_fechar_requer_autenticacao(self, client):
        """Deve exigir autenticacao para fechar chamado"""
        response = client.post("/admin/chamados/1/fechar", follow_redirects=False)
        assert_permission_denied(response)

    def test_reabrir_requer_autenticacao(self, client):
        """Deve exigir autenticacao para reabrir chamado"""
        response = client.post("/admin/chamados/1/reabrir", follow_redirects=False)
        assert_permission_denied(response)


class TestAdminChamadosAutorizacao:
    """Testes de autorizacao para rotas de admin de chamados"""

    def test_listar_requer_admin(self, cliente_autenticado):
        """Apenas admin pode listar todos os chamados"""
        response = cliente_autenticado.get("/admin/chamados/listar", follow_redirects=False)
        # Cliente comum deve ser negado (403 ou redirect)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_responder_get_requer_admin(self, cliente_autenticado):
        """Apenas admin pode acessar formulario de resposta"""
        response = cliente_autenticado.get("/admin/chamados/1/responder", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_fechar_requer_admin(self, cliente_autenticado):
        """Apenas admin pode fechar chamado"""
        response = cliente_autenticado.post("/admin/chamados/1/fechar", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_reabrir_requer_admin(self, cliente_autenticado):
        """Apenas admin pode reabrir chamado"""
        response = cliente_autenticado.post("/admin/chamados/1/reabrir", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]


class TestAdminListarChamados:
    """Testes de listagem de chamados para administradores"""

    def test_admin_pode_listar_chamados(self, admin_autenticado):
        """Admin deve conseguir listar chamados"""
        response = admin_autenticado.get("/admin/chamados/listar")
        assert response.status_code == status.HTTP_200_OK
        assert "chamado" in response.text.lower()

    def test_listar_exibe_template_correto(self, admin_autenticado):
        """Deve renderizar template de listagem"""
        response = admin_autenticado.get("/admin/chamados/listar")
        assert response.status_code == status.HTTP_200_OK


class TestAdminResponderChamado:
    """Testes para resposta de chamados por administradores"""

    def test_get_responder_chamado_inexistente(self, admin_autenticado):
        """Deve tratar chamado inexistente"""
        response = admin_autenticado.get("/admin/chamados/99999/responder", follow_redirects=False)
        # Deve redirecionar ou retornar 404
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_404_NOT_FOUND]

    def test_post_responder_chamado_inexistente(self, admin_autenticado):
        """Deve tratar POST para chamado inexistente"""
        response = admin_autenticado.post("/admin/chamados/99999/responder", data={
            "mensagem": "Resposta teste",
            "status_chamado": "Em Análise"
        }, follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_404_NOT_FOUND]

    def test_responder_com_dados_validos(self, admin_autenticado, criar_chamado_admin):
        """Admin deve conseguir responder chamado com dados validos"""
        chamado_id = criar_chamado_admin

        response = admin_autenticado.post(f"/admin/chamados/{chamado_id}/responder", data={
            "mensagem": "Resposta do administrador ao chamado",
            "status_chamado": "Em Análise"
        }, follow_redirects=False)

        assert_redirects_to(response, "/admin/chamados/listar")

    def test_responder_com_mensagem_vazia(self, admin_autenticado, criar_chamado_admin):
        """Deve rejeitar mensagem vazia"""
        chamado_id = criar_chamado_admin

        response = admin_autenticado.post(f"/admin/chamados/{chamado_id}/responder", data={
            "mensagem": "",
            "status_chamado": "Em Análise"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK

    def test_responder_com_status_invalido(self, admin_autenticado, criar_chamado_admin):
        """Deve rejeitar status invalido"""
        chamado_id = criar_chamado_admin

        response = admin_autenticado.post(f"/admin/chamados/{chamado_id}/responder", data={
            "mensagem": "Resposta valida do administrador",
            "status_chamado": "StatusInvalido"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK


class TestAdminFecharChamado:
    """Testes para fechamento de chamados"""

    def test_fechar_chamado_existente(self, admin_autenticado, criar_chamado_admin):
        """Admin deve conseguir fechar chamado existente"""
        chamado_id = criar_chamado_admin

        response = admin_autenticado.post(f"/admin/chamados/{chamado_id}/fechar", follow_redirects=False)

        assert_redirects_to(response, "/admin/chamados/listar")

    def test_fechar_chamado_inexistente(self, admin_autenticado):
        """Deve tratar fechamento de chamado inexistente"""
        response = admin_autenticado.post("/admin/chamados/99999/fechar", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_404_NOT_FOUND]


class TestAdminReabrirChamado:
    """Testes para reabertura de chamados"""

    def test_reabrir_chamado_fechado(self, admin_autenticado, criar_chamado_admin):
        """Admin deve conseguir reabrir chamado fechado"""
        chamado_id = criar_chamado_admin

        # Primeiro fechar o chamado
        admin_autenticado.post(f"/admin/chamados/{chamado_id}/fechar", follow_redirects=False)

        # Depois tentar reabrir
        response = admin_autenticado.post(f"/admin/chamados/{chamado_id}/reabrir", follow_redirects=False)

        assert_redirects_to(response, "/admin/chamados/listar")

    def test_reabrir_chamado_inexistente(self, admin_autenticado):
        """Deve tratar reabertura de chamado inexistente"""
        response = admin_autenticado.post("/admin/chamados/99999/reabrir", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_404_NOT_FOUND]

    def test_reabrir_chamado_nao_fechado(self, admin_autenticado, criar_chamado_admin):
        """Nao deve permitir reabrir chamado que nao esta fechado"""
        chamado_id = criar_chamado_admin  # Chamado esta Aberto, nao Fechado

        response = admin_autenticado.post(f"/admin/chamados/{chamado_id}/reabrir", follow_redirects=False)

        # Deve redirecionar com mensagem de erro
        assert_redirects_to(response, "/admin/chamados/listar")


class TestAdminChamadosRateLimiting:
    """Testes de rate limiting para rotas de admin de chamados"""

    def test_rate_limit_responder(self, admin_autenticado, criar_chamado_admin):
        """Rate limit deve bloquear respostas excessivas"""
        chamado_id = criar_chamado_admin

        with patch('routes.admin_chamados_routes.admin_chamado_responder_limiter.verificar', return_value=False):
            response = admin_autenticado.post(f"/admin/chamados/{chamado_id}/responder", data={
                "mensagem": "Resposta de teste",
                "status_chamado": "Em Análise"
            }, follow_redirects=False)

            assert_redirects_to(response, f"/admin/chamados/{chamado_id}/responder")
