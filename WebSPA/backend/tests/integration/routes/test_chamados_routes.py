"""
Testes de integracao das rotas de chamados do usuario (API JSON).

Contrato (SPA, tudo sob /api):
- Mutacoes exigem header X-CSRF-Token (obtido em /api/csrf-token).
- Sucesso retorna JSON puro: GET 200, POST 201, DELETE 204.
- Erros seguem {detail, type, errors}: 401/403/404/409/422.
- Sem redirect, flash ou HTML.

Endpoints cobertos (routes/chamados_routes.py, prefixo /api/chamados):
- GET    /api/chamados                 -> PaginaResponse[ChamadoResponse] (filtros)
- POST   /api/chamados                 -> 201 ChamadoResponse (CriarChamadoDTO)
- GET    /api/chamados/{id}            -> ChamadoResponse com interacoes
- POST   /api/chamados/{id}/interacoes -> 201 ChamadoResponse (CriarInteracaoDTO)
- DELETE /api/chamados/{id}            -> 204 (regras de exclusao)
"""
from fastapi import status


# =============================================================================
# Helpers
# =============================================================================

def _csrf(client):
    """Obtem um token CSRF valido para a sessao atual."""
    return client.get("/api/csrf-token").json()["token"]


def _criar_chamado(client, titulo="Problema no acesso ao sistema",
                   descricao="Descricao detalhada do problema encontrado hoje.",
                   prioridade="Alta"):
    """Cria um chamado e retorna a resposta HTTP."""
    token = _csrf(client)
    return client.post(
        "/api/chamados",
        json={"titulo": titulo, "descricao": descricao, "prioridade": prioridade},
        headers={"X-CSRF-Token": token},
    )


# =============================================================================
# Autenticacao
# =============================================================================

class TestChamadosAutenticacao:
    """Acesso sem autenticacao deve retornar 401 (sem redirect)."""

    def test_listar_sem_auth(self, client):
        response = client.get("/api/chamados")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_criar_sem_auth(self, client):
        token = _csrf(client)
        response = client.post(
            "/api/chamados",
            json={
                "titulo": "Titulo qualquer aqui",
                "descricao": "Descricao detalhada o suficiente para passar.",
                "prioridade": "Média",
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_obter_sem_auth(self, client):
        response = client.get("/api/chamados/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_excluir_sem_auth(self, client):
        token = _csrf(client)
        response = client.delete(
            "/api/chamados/1", headers={"X-CSRF-Token": token}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Criacao
# =============================================================================

class TestCriarChamado:
    """POST /api/chamados."""

    def test_criar_com_dados_validos(self, cliente_autenticado):
        response = _criar_chamado(cliente_autenticado)
        assert response.status_code == status.HTTP_201_CREATED

        corpo = response.json()
        assert corpo["id"] > 0
        assert corpo["titulo"] == "Problema no acesso ao sistema"
        assert corpo["status"] == "Aberto"
        assert corpo["prioridade"] == "Alta"
        # Interacao inicial (abertura) deve estar presente no detalhe retornado
        assert corpo["interacoes"] is not None
        assert len(corpo["interacoes"]) == 1
        assert corpo["interacoes"][0]["tipo"] == "Abertura"
        assert (
            corpo["interacoes"][0]["mensagem"]
            == "Descricao detalhada do problema encontrado hoje."
        )

    def test_criar_prioridade_padrao(self, cliente_autenticado):
        """Sem prioridade explicita, usa o padrao 'Média'."""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.post(
            "/api/chamados",
            json={
                "titulo": "Titulo valido sem prioridade",
                "descricao": "Descricao detalhada o suficiente para passar.",
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["prioridade"] == "Média"

    def test_criar_titulo_curto(self, cliente_autenticado):
        """Titulo com menos de 10 caracteres deve falhar com 422."""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.post(
            "/api/chamados",
            json={
                "titulo": "Curto",
                "descricao": "Descricao detalhada o suficiente para passar.",
                "prioridade": "Média",
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()

    def test_criar_descricao_curta(self, cliente_autenticado):
        """Descricao com menos de 20 caracteres deve falhar com 422."""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.post(
            "/api/chamados",
            json={
                "titulo": "Titulo suficientemente longo",
                "descricao": "Curta",
                "prioridade": "Média",
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_criar_prioridade_invalida(self, cliente_autenticado):
        """Prioridade fora do enum deve falhar com 422."""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.post(
            "/api/chamados",
            json={
                "titulo": "Titulo suficientemente longo",
                "descricao": "Descricao detalhada o suficiente para passar.",
                "prioridade": "Inexistente",
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# =============================================================================
# Listagem
# =============================================================================

class TestListarChamados:
    """GET /api/chamados (paginado, com filtros)."""

    def test_listar_vazio(self, cliente_autenticado):
        response = cliente_autenticado.get("/api/chamados")
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["items"] == []
        assert corpo["total"] == 0
        assert corpo["pagina"] == 1

    def test_listar_apos_criar(self, cliente_autenticado):
        _criar_chamado(cliente_autenticado, titulo="Primeiro chamado de teste")
        _criar_chamado(cliente_autenticado, titulo="Segundo chamado de teste")

        response = cliente_autenticado.get("/api/chamados")
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["total"] == 2
        assert len(corpo["items"]) == 2
        # Listagem nao carrega o historico de interacoes
        assert corpo["items"][0]["interacoes"] is None

    def test_listar_paginacao(self, cliente_autenticado):
        for i in range(3):
            _criar_chamado(
                cliente_autenticado, titulo=f"Chamado numero {i} de teste"
            )

        response = cliente_autenticado.get(
            "/api/chamados", params={"pagina": 1, "por_pagina": 2}
        )
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["por_pagina"] == 2
        assert corpo["total"] == 3
        assert corpo["total_paginas"] == 2
        assert len(corpo["items"]) == 2

    def test_listar_filtro_q(self, cliente_autenticado):
        _criar_chamado(cliente_autenticado, titulo="Erro de login no portal")
        _criar_chamado(cliente_autenticado, titulo="Pagamento nao processado")

        response = cliente_autenticado.get("/api/chamados", params={"q": "login"})
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["total"] == 1
        assert "login" in corpo["items"][0]["titulo"].lower()

    def test_listar_filtro_prioridade(self, cliente_autenticado):
        _criar_chamado(cliente_autenticado, titulo="Chamado urgente um", prioridade="Urgente")
        _criar_chamado(cliente_autenticado, titulo="Chamado baixo dois", prioridade="Baixa")

        response = cliente_autenticado.get(
            "/api/chamados", params={"prioridade": "Urgente"}
        )
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["total"] == 1
        assert corpo["items"][0]["prioridade"] == "Urgente"

    def test_listar_filtro_status(self, cliente_autenticado):
        _criar_chamado(cliente_autenticado, titulo="Chamado aberto qualquer")

        response = cliente_autenticado.get(
            "/api/chamados", params={"status_filtro": "Aberto"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 1

        response_vazio = cliente_autenticado.get(
            "/api/chamados", params={"status_filtro": "Fechado"}
        )
        assert response_vazio.json()["total"] == 0


# =============================================================================
# Isolamento entre usuarios
# =============================================================================

class TestIsolamentoUsuarios:
    """Cada usuario so enxerga / acessa os proprios chamados."""

    def test_listagem_isolada(self, client, criar_usuario, fazer_login):
        # Usuario A cria um chamado
        criar_usuario("Usuario A", "usuario_a@example.com", "Senha@123")
        fazer_login("usuario_a@example.com", "Senha@123")
        resp_a = _criar_chamado(client, titulo="Chamado do usuario A")
        assert resp_a.status_code == status.HTTP_201_CREATED

        # Usuario B faz login (mesmo client) e nao deve ver o chamado de A
        criar_usuario("Usuario B", "usuario_b@example.com", "Senha@456")
        fazer_login("usuario_b@example.com", "Senha@456")

        response = client.get("/api/chamados")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 0

    def test_detalhe_de_outro_usuario_403(self, client, criar_usuario, fazer_login):
        # Usuario A cria um chamado
        criar_usuario("Usuario A", "usuario_a@example.com", "Senha@123")
        fazer_login("usuario_a@example.com", "Senha@123")
        chamado_id = _criar_chamado(client, titulo="Chamado privado do A").json()["id"]

        # Usuario B tenta acessar -> 403
        criar_usuario("Usuario B", "usuario_b@example.com", "Senha@456")
        fazer_login("usuario_b@example.com", "Senha@456")

        response = client.get(f"/api/chamados/{chamado_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_responder_chamado_de_outro_403(self, client, criar_usuario, fazer_login):
        criar_usuario("Usuario A", "usuario_a@example.com", "Senha@123")
        fazer_login("usuario_a@example.com", "Senha@123")
        chamado_id = _criar_chamado(client, titulo="Chamado privado do A").json()["id"]

        criar_usuario("Usuario B", "usuario_b@example.com", "Senha@456")
        fazer_login("usuario_b@example.com", "Senha@456")

        token = _csrf(client)
        response = client.post(
            f"/api/chamados/{chamado_id}/interacoes",
            json={"mensagem": "Tentando responder chamado alheio."},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# Detalhe
# =============================================================================

class TestObterChamado:
    """GET /api/chamados/{id}."""

    def test_obter_detalhe(self, cliente_autenticado):
        chamado_id = _criar_chamado(cliente_autenticado).json()["id"]

        response = cliente_autenticado.get(f"/api/chamados/{chamado_id}")
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["id"] == chamado_id
        assert corpo["interacoes"] is not None
        assert len(corpo["interacoes"]) >= 1

    def test_obter_inexistente_404(self, cliente_autenticado):
        response = cliente_autenticado.get("/api/chamados/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# Interacoes (respostas do usuario)
# =============================================================================

class TestResponderChamado:
    """POST /api/chamados/{id}/interacoes."""

    def test_responder_proprio_chamado(self, cliente_autenticado):
        chamado_id = _criar_chamado(cliente_autenticado).json()["id"]

        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.post(
            f"/api/chamados/{chamado_id}/interacoes",
            json={"mensagem": "Adicionando mais informacoes ao chamado."},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_201_CREATED

        corpo = response.json()
        # Abertura + a nova resposta
        assert len(corpo["interacoes"]) == 2
        tipos = [i["tipo"] for i in corpo["interacoes"]]
        assert "Resposta do Usuário" in tipos

    def test_responder_mensagem_curta_422(self, cliente_autenticado):
        chamado_id = _criar_chamado(cliente_autenticado).json()["id"]

        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.post(
            f"/api/chamados/{chamado_id}/interacoes",
            json={"mensagem": "curta"},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_responder_chamado_inexistente_404(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.post(
            "/api/chamados/999999/interacoes",
            json={"mensagem": "Mensagem valida para um chamado inexistente."},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# Exclusao
# =============================================================================

class TestExcluirChamado:
    """DELETE /api/chamados/{id}."""

    def test_excluir_chamado_aberto(self, cliente_autenticado):
        chamado_id = _criar_chamado(cliente_autenticado).json()["id"]

        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.delete(
            f"/api/chamados/{chamado_id}", headers={"X-CSRF-Token": token}
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Confirmar que sumiu da listagem
        listagem = cliente_autenticado.get("/api/chamados")
        assert listagem.json()["total"] == 0

    def test_excluir_inexistente_404(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.delete(
            "/api/chamados/999999", headers={"X-CSRF-Token": token}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_excluir_de_outro_usuario_403(self, client, criar_usuario, fazer_login):
        criar_usuario("Usuario A", "usuario_a@example.com", "Senha@123")
        fazer_login("usuario_a@example.com", "Senha@123")
        chamado_id = _criar_chamado(client, titulo="Chamado privado do A").json()["id"]

        criar_usuario("Usuario B", "usuario_b@example.com", "Senha@456")
        fazer_login("usuario_b@example.com", "Senha@456")

        token = _csrf(client)
        response = client.delete(
            f"/api/chamados/{chamado_id}", headers={"X-CSRF-Token": token}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_excluir_com_resposta_admin_409(
        self, client, criar_usuario, fazer_login, admin_teste
    ):
        """Chamado que ja recebeu resposta de admin nao pode ser excluido (409)."""
        from repo import usuario_repo
        from model.usuario_model import Usuario
        from util.security import criar_hash_senha
        from util.perfis import Perfil

        # Cliente cria o chamado
        criar_usuario("Dono Chamado", "dono@example.com", "Senha@123")
        fazer_login("dono@example.com", "Senha@123")
        chamado_id = _criar_chamado(client, titulo="Chamado que tera resposta").json()["id"]

        # Admin responde (gera resposta_admin) via rota administrativa
        admin = Usuario(
            id=0,
            nome=admin_teste["nome"],
            email=admin_teste["email"],
            senha=criar_hash_senha(admin_teste["senha"]),
            perfil=Perfil.ADMIN.value,
        )
        usuario_repo.inserir(admin)
        fazer_login(admin_teste["email"], admin_teste["senha"])

        token = _csrf(client)
        resp_admin = client.post(
            f"/api/admin/chamados/{chamado_id}/interacoes",
            json={
                "dto_mensagem": {"mensagem": "Estamos analisando o seu caso."},
                "dto_status": {"status": "Em Análise"},
            },
            headers={"X-CSRF-Token": token},
        )
        assert resp_admin.status_code == status.HTTP_201_CREATED

        # Dono volta e tenta excluir -> agora o status nao e mais Aberto (409)
        fazer_login("dono@example.com", "Senha@123")
        token = _csrf(client)
        response = client.delete(
            f"/api/chamados/{chamado_id}", headers={"X-CSRF-Token": token}
        )
        assert response.status_code == status.HTTP_409_CONFLICT
