"""
Testes de integracao das rotas administrativas de chamados (API JSON).

Contrato (SPA, tudo sob /api):
- Acesso restrito a administradores; nao-admin recebe 403.
- Mutacoes exigem header X-CSRF-Token (obtido em /api/csrf-token).
- Sucesso retorna JSON puro: GET 200, POST 201, PATCH 200.
- Erros seguem {detail, type, errors}: 401/403/404/409/422.
- Sem redirect, flash ou HTML.

Endpoints cobertos (routes/admin_chamados_routes.py, prefixo /api/admin/chamados):
- GET   /api/admin/chamados                 -> PaginaResponse[ChamadoResponse]
- GET   /api/admin/chamados/{id}            -> ChamadoResponse com interacoes
- POST  /api/admin/chamados/{id}/interacoes -> 201 (body ANINHADO:
        {"dto_mensagem": {...}, "dto_status": {...}})
- PATCH /api/admin/chamados/{id}/status     -> 200 ChamadoResponse

Usa a fixture criar_chamado_admin para obter um chamado pre-existente.
"""
from fastapi import status


# =============================================================================
# Helpers
# =============================================================================

def _csrf(client):
    """Obtem um token CSRF valido para a sessao atual."""
    return client.get("/api/csrf-token").json()["token"]


# =============================================================================
# Autorizacao
# =============================================================================

class TestAdminChamadosAutorizacao:
    """Apenas administradores acessam as rotas de admin."""

    def test_listar_sem_auth_401(self, client):
        response = client.get("/api/admin/chamados")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_listar_nao_admin_403(self, cliente_autenticado):
        response = cliente_autenticado.get("/api/admin/chamados")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_obter_nao_admin_403(self, cliente_autenticado):
        response = cliente_autenticado.get("/api/admin/chamados/1")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_responder_nao_admin_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.post(
            "/api/admin/chamados/1/interacoes",
            json={
                "dto_mensagem": {"mensagem": "Resposta de teste do admin."},
                "dto_status": {"status": "Em Análise"},
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_alterar_status_nao_admin_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.patch(
            "/api/admin/chamados/1/status",
            json={"status": "Resolvido"},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# Listagem
# =============================================================================

class TestAdminListarChamados:
    """GET /api/admin/chamados (todos os chamados do sistema)."""

    def test_listar_vazio(self, admin_autenticado):
        response = admin_autenticado.get("/api/admin/chamados")
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["items"] == []
        assert corpo["total"] == 0

    def test_listar_com_chamado(self, admin_autenticado, criar_chamado_admin):
        response = admin_autenticado.get("/api/admin/chamados")
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["total"] == 1
        assert corpo["items"][0]["id"] == criar_chamado_admin
        # Listagem nao carrega o historico de interacoes
        assert corpo["items"][0]["interacoes"] is None

    def test_listar_filtro_status(self, admin_autenticado, criar_chamado_admin):
        response = admin_autenticado.get(
            "/api/admin/chamados", params={"status_filtro": "Aberto"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 1

        vazio = admin_autenticado.get(
            "/api/admin/chamados", params={"status_filtro": "Resolvido"}
        )
        assert vazio.json()["total"] == 0


# =============================================================================
# Detalhe
# =============================================================================

class TestAdminObterChamado:
    """GET /api/admin/chamados/{id}."""

    def test_obter_detalhe(self, admin_autenticado, criar_chamado_admin):
        response = admin_autenticado.get(f"/api/admin/chamados/{criar_chamado_admin}")
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["id"] == criar_chamado_admin
        assert corpo["interacoes"] is not None
        assert len(corpo["interacoes"]) >= 1

    def test_obter_inexistente_404(self, admin_autenticado):
        response = admin_autenticado.get("/api/admin/chamados/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# Resposta do admin (interacao + alteracao de status; body aninhado)
# =============================================================================

class TestAdminResponder:
    """POST /api/admin/chamados/{id}/interacoes (body aninhado)."""

    def test_responder_com_mudanca_status(self, admin_autenticado, criar_chamado_admin):
        token = _csrf(admin_autenticado)
        response = admin_autenticado.post(
            f"/api/admin/chamados/{criar_chamado_admin}/interacoes",
            json={
                "dto_mensagem": {"mensagem": "Estamos analisando a sua solicitacao."},
                "dto_status": {"status": "Em Análise"},
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_201_CREATED

        corpo = response.json()
        assert corpo["status"] == "Em Análise"
        tipos = [i["tipo"] for i in corpo["interacoes"]]
        assert "Resposta do Administrador" in tipos

    def test_responder_e_fechar(self, admin_autenticado, criar_chamado_admin):
        token = _csrf(admin_autenticado)
        response = admin_autenticado.post(
            f"/api/admin/chamados/{criar_chamado_admin}/interacoes",
            json={
                "dto_mensagem": {"mensagem": "Problema resolvido, encerrando o chamado."},
                "dto_status": {"status": "Fechado"},
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_201_CREATED

        corpo = response.json()
        assert corpo["status"] == "Fechado"
        assert corpo["data_fechamento"] is not None

    def test_responder_mensagem_curta_422(self, admin_autenticado, criar_chamado_admin):
        token = _csrf(admin_autenticado)
        response = admin_autenticado.post(
            f"/api/admin/chamados/{criar_chamado_admin}/interacoes",
            json={
                "dto_mensagem": {"mensagem": "curta"},
                "dto_status": {"status": "Em Análise"},
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_responder_status_invalido_422(self, admin_autenticado, criar_chamado_admin):
        token = _csrf(admin_autenticado)
        response = admin_autenticado.post(
            f"/api/admin/chamados/{criar_chamado_admin}/interacoes",
            json={
                "dto_mensagem": {"mensagem": "Mensagem valida para o teste."},
                "dto_status": {"status": "Inexistente"},
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_responder_inexistente_404(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        response = admin_autenticado.post(
            "/api/admin/chamados/999999/interacoes",
            json={
                "dto_mensagem": {"mensagem": "Mensagem valida para o teste."},
                "dto_status": {"status": "Em Análise"},
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# Alteracao de status (PATCH)
# =============================================================================

class TestAdminAlterarStatus:
    """PATCH /api/admin/chamados/{id}/status."""

    def test_alterar_status(self, admin_autenticado, criar_chamado_admin):
        token = _csrf(admin_autenticado)
        response = admin_autenticado.patch(
            f"/api/admin/chamados/{criar_chamado_admin}/status",
            json={"status": "Resolvido"},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "Resolvido"

    def test_fechar_grava_data_fechamento(self, admin_autenticado, criar_chamado_admin):
        token = _csrf(admin_autenticado)
        response = admin_autenticado.patch(
            f"/api/admin/chamados/{criar_chamado_admin}/status",
            json={"status": "Fechado"},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["status"] == "Fechado"
        assert corpo["data_fechamento"] is not None

    def test_reabertura_invalida_409(self, admin_autenticado, criar_chamado_admin):
        """Chamado fechado so pode ser reaberto como 'Em Análise'."""
        token = _csrf(admin_autenticado)
        # Primeiro fecha
        fechar = admin_autenticado.patch(
            f"/api/admin/chamados/{criar_chamado_admin}/status",
            json={"status": "Fechado"},
            headers={"X-CSRF-Token": token},
        )
        assert fechar.status_code == status.HTTP_200_OK

        # Tenta reabrir como 'Resolvido' (proibido) -> 409
        token = _csrf(admin_autenticado)
        response = admin_autenticado.patch(
            f"/api/admin/chamados/{criar_chamado_admin}/status",
            json={"status": "Resolvido"},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_reabertura_valida_em_analise(self, admin_autenticado, criar_chamado_admin):
        """De 'Fechado' para 'Em Análise' e permitido."""
        token = _csrf(admin_autenticado)
        admin_autenticado.patch(
            f"/api/admin/chamados/{criar_chamado_admin}/status",
            json={"status": "Fechado"},
            headers={"X-CSRF-Token": token},
        )

        token = _csrf(admin_autenticado)
        response = admin_autenticado.patch(
            f"/api/admin/chamados/{criar_chamado_admin}/status",
            json={"status": "Em Análise"},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "Em Análise"

    def test_alterar_status_invalido_422(self, admin_autenticado, criar_chamado_admin):
        token = _csrf(admin_autenticado)
        response = admin_autenticado.patch(
            f"/api/admin/chamados/{criar_chamado_admin}/status",
            json={"status": "Inexistente"},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_alterar_status_inexistente_404(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        response = admin_autenticado.patch(
            "/api/admin/chamados/999999/status",
            json={"status": "Resolvido"},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
