"""
Testes de integração das rotas de chat (contrato JSON puro / SPA).

Todos os endpoints vivem sob ``/api/chat``. As mutações exigem o header
``X-CSRF-Token`` obtido em ``GET /api/csrf-token``. Respostas seguem o
contrato JSON: GET 200, POST 201, ações 200; erros como
``{detail, type, errors}`` com 401/403/404/422.

O endpoint SSE ``GET /api/chat/stream`` NÃO é exercido com o ``TestClient``:
o ``StreamingResponse`` mantém um gerador infinito (loop ``while True`` sobre
uma fila assíncrona) e consumir o corpo trava o cliente de teste. Cobrimos
apenas o caso sem autenticação, garantindo o 401 SEM tocar no corpo da
resposta (a autenticação é checada antes de o gerador começar a emitir).
"""
from fastapi import status


# ---------------------------------------------------------------------------
# Helpers locais
# ---------------------------------------------------------------------------

def _csrf(client):
    """Obtém um token CSRF válido para a sessão atual."""
    return client.get("/api/csrf-token").json()["token"]


def _registrar(client, nome, email, senha="Senha@123"):
    """Cadastra um usuário via API e retorna o ID criado."""
    # O validador de nome exige no mínimo 2 palavras; garante sobrenome.
    if len(nome.split()) < 2:
        nome = f"{nome} Teste"
    token = _csrf(client)
    resp = client.post(
        "/api/cadastrar",
        json={
            "perfil": "Cliente",
            "nome": nome,
            "email": email,
            "senha": senha,
            "confirmar_senha": senha,
        },
        headers={"X-CSRF-Token": token},
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    return resp.json()["id"]


def _login(client, email, senha="Senha@123"):
    """Faz login (troca a identidade da sessão no client compartilhado)."""
    token = _csrf(client)
    resp = client.post(
        "/api/login",
        json={"email": email, "senha": senha},
        headers={"X-CSRF-Token": token},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    return resp


def _criar_sala(client, outro_usuario_id):
    """Cria/obtém uma sala com outro usuário; retorna o sala_id."""
    token = _csrf(client)
    resp = client.post(
        "/api/chat/salas",
        json={"outro_usuario_id": outro_usuario_id},
        headers={"X-CSRF-Token": token},
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    return resp.json()["sala_id"]


def _enviar(client, sala_id, mensagem):
    """Envia uma mensagem para a sala; retorna a resposta."""
    token = _csrf(client)
    return client.post(
        "/api/chat/mensagens",
        json={"sala_id": sala_id, "mensagem": mensagem},
        headers={"X-CSRF-Token": token},
    )


# ---------------------------------------------------------------------------
# Autenticação obrigatória
# ---------------------------------------------------------------------------

class TestChatRequerAutenticacao:
    """Endpoints protegidos devem retornar 401 sem sessão."""

    def test_criar_sala_sem_auth(self, client):
        token = _csrf(client)
        resp = client.post(
            "/api/chat/salas",
            json={"outro_usuario_id": 1},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_listar_conversas_sem_auth(self, client):
        resp = client.get("/api/chat/conversas")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_listar_mensagens_sem_auth(self, client):
        resp = client.get("/api/chat/mensagens/1_2")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_enviar_mensagem_sem_auth(self, client):
        token = _csrf(client)
        resp = client.post(
            "/api/chat/mensagens",
            json={"sala_id": "1_2", "mensagem": "oi"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_marcar_lidas_sem_auth(self, client):
        token = _csrf(client)
        resp = client.post(
            "/api/chat/mensagens/lidas/1_2",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_total_nao_lidas_sem_auth(self, client):
        resp = client.get("/api/chat/mensagens/nao-lidas/total")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_buscar_usuarios_sem_auth(self, client):
        resp = client.get("/api/chat/usuarios/buscar", params={"q": "us"})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_stream_sem_auth(self, client):
        """
        SSE: sem autenticação deve dar 401. A checagem de auth ocorre ANTES
        de o gerador começar a emitir, então a resposta nunca vira um stream
        contínuo. Não consumimos um corpo de stream (em caso de erro não há).
        """
        resp = client.get("/api/chat/stream")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Health (público)
# ---------------------------------------------------------------------------

class TestChatHealth:
    """O health check do chat é público e retorna JSON estruturado."""

    def test_health_200(self, client):
        resp = client.get("/api/chat/health")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["status"] == "healthy"
        assert body["conexoes_ativas"] == 0
        assert "timestamp" in body


# ---------------------------------------------------------------------------
# Criação de sala
# ---------------------------------------------------------------------------

class TestCriarSala:
    """POST /api/chat/salas — cria ou obtém a sala entre dois usuários."""

    def test_criar_sala_entre_dois_usuarios(self, client):
        _registrar(client, "Alice", "alice@example.com")
        bob_id = _registrar(client, "Bob", "bob@example.com")

        _login(client, "alice@example.com")
        token = _csrf(client)
        resp = client.post(
            "/api/chat/salas",
            json={"outro_usuario_id": bob_id},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        body = resp.json()
        assert "sala_id" in body
        assert body["sala_id"]

    def test_criar_sala_idempotente(self, client):
        """Criar a mesma sala duas vezes retorna o mesmo sala_id."""
        _registrar(client, "Alice", "alice@example.com")
        bob_id = _registrar(client, "Bob", "bob@example.com")

        _login(client, "alice@example.com")
        primeiro = _criar_sala(client, bob_id)
        segundo = _criar_sala(client, bob_id)
        assert primeiro == segundo

    def test_criar_sala_consigo_mesmo_400(self, client):
        alice_id = _registrar(client, "Alice", "alice@example.com")
        _login(client, "alice@example.com")
        token = _csrf(client)
        resp = client.post(
            "/api/chat/salas",
            json={"outro_usuario_id": alice_id},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_criar_sala_usuario_inexistente_404(self, client):
        _registrar(client, "Alice", "alice@example.com")
        _login(client, "alice@example.com")
        token = _csrf(client)
        resp = client.post(
            "/api/chat/salas",
            json={"outro_usuario_id": 999999},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_criar_sala_dto_invalido_422(self, client):
        """ID não positivo viola o DTO -> 422."""
        _registrar(client, "Alice", "alice@example.com")
        _login(client, "alice@example.com")
        token = _csrf(client)
        resp = client.post(
            "/api/chat/salas",
            json={"outro_usuario_id": 0},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# Envio e listagem de mensagens
# ---------------------------------------------------------------------------

class TestMensagens:
    """Fluxo de envio/listagem de mensagens entre dois usuários."""

    def test_enviar_e_listar_mensagens(self, client):
        _registrar(client, "Alice", "alice@example.com")
        bob_id = _registrar(client, "Bob", "bob@example.com")

        _login(client, "alice@example.com")
        sala_id = _criar_sala(client, bob_id)

        resp = _enviar(client, sala_id, "Olá Bob!")
        assert resp.status_code == status.HTTP_201_CREATED
        msg = resp.json()
        assert msg["mensagem"] == "Olá Bob!"
        assert msg["sala_id"] == sala_id
        assert msg["lida_em"] is None
        assert "id" in msg

        # Alice lista as mensagens da sala
        lista = client.get(f"/api/chat/mensagens/{sala_id}")
        assert lista.status_code == status.HTTP_200_OK
        corpo = lista.json()
        assert isinstance(corpo, list)
        assert any(m["mensagem"] == "Olá Bob!" for m in corpo)

    def test_listar_mensagens_paginacao(self, client):
        _registrar(client, "Alice", "alice@example.com")
        bob_id = _registrar(client, "Bob", "bob@example.com")

        _login(client, "alice@example.com")
        sala_id = _criar_sala(client, bob_id)
        for i in range(3):
            assert _enviar(client, sala_id, f"msg {i}").status_code == 201

        resp = client.get(
            f"/api/chat/mensagens/{sala_id}", params={"limit": 2, "offset": 0}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.json()) <= 2

    def test_enviar_mensagem_sala_sem_acesso_403(self, client):
        """Usuário que não participa da sala não pode enviar mensagem."""
        _registrar(client, "Alice", "alice@example.com")
        bob_id = _registrar(client, "Bob", "bob@example.com")
        _registrar(client, "Carol", "carol@example.com")

        _login(client, "alice@example.com")
        sala_id = _criar_sala(client, bob_id)

        # Carol tenta enviar na sala de Alice e Bob
        _login(client, "carol@example.com")
        resp = _enviar(client, sala_id, "intruso")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_listar_mensagens_sala_sem_acesso_403(self, client):
        _registrar(client, "Alice", "alice@example.com")
        bob_id = _registrar(client, "Bob", "bob@example.com")
        _registrar(client, "Carol", "carol@example.com")

        _login(client, "alice@example.com")
        sala_id = _criar_sala(client, bob_id)

        _login(client, "carol@example.com")
        resp = client.get(f"/api/chat/mensagens/{sala_id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_enviar_mensagem_vazia_422(self, client):
        _registrar(client, "Alice", "alice@example.com")
        bob_id = _registrar(client, "Bob", "bob@example.com")
        _login(client, "alice@example.com")
        sala_id = _criar_sala(client, bob_id)
        resp = _enviar(client, sala_id, "")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# Marcar como lidas e contagem de não lidas
# ---------------------------------------------------------------------------

class TestNaoLidas:
    """Contagem de não lidas e marcação de mensagens como lidas."""

    def test_total_nao_lidas_apos_recebimento(self, client):
        _registrar(client, "Alice", "alice@example.com")
        bob_id = _registrar(client, "Bob", "bob@example.com")

        _login(client, "alice@example.com")
        sala_id = _criar_sala(client, bob_id)

        # Bob envia para Alice
        _login(client, "bob@example.com")
        assert _enviar(client, sala_id, "Oi Alice").status_code == 201

        # Alice agora tem ao menos 1 não lida
        _login(client, "alice@example.com")
        resp = client.get("/api/chat/mensagens/nao-lidas/total")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["total"] >= 1

    def test_marcar_como_lidas_zera_contador(self, client):
        _registrar(client, "Alice", "alice@example.com")
        bob_id = _registrar(client, "Bob", "bob@example.com")

        _login(client, "alice@example.com")
        sala_id = _criar_sala(client, bob_id)

        _login(client, "bob@example.com")
        assert _enviar(client, sala_id, "Mensagem para Alice").status_code == 201

        _login(client, "alice@example.com")
        # Marca como lidas
        token = _csrf(client)
        marcar = client.post(
            f"/api/chat/mensagens/lidas/{sala_id}",
            headers={"X-CSRF-Token": token},
        )
        assert marcar.status_code == status.HTTP_200_OK
        assert "message" in marcar.json()

        total = client.get("/api/chat/mensagens/nao-lidas/total")
        assert total.status_code == status.HTTP_200_OK
        assert total.json()["total"] == 0

    def test_marcar_lidas_sala_sem_acesso_403(self, client):
        _registrar(client, "Alice", "alice@example.com")
        bob_id = _registrar(client, "Bob", "bob@example.com")
        _registrar(client, "Carol", "carol@example.com")

        _login(client, "alice@example.com")
        sala_id = _criar_sala(client, bob_id)

        _login(client, "carol@example.com")
        token = _csrf(client)
        resp = client.post(
            f"/api/chat/mensagens/lidas/{sala_id}",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Listagem de conversas
# ---------------------------------------------------------------------------

class TestConversas:
    """GET /api/chat/conversas — lista as conversas do usuário logado."""

    def test_conversas_vazia(self, client):
        _registrar(client, "Alice", "alice@example.com")
        _login(client, "alice@example.com")
        resp = client.get("/api/chat/conversas")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_conversas_apos_mensagem(self, client):
        _registrar(client, "Alice", "alice@example.com")
        bob_id = _registrar(client, "Bob", "bob@example.com")

        _login(client, "alice@example.com")
        sala_id = _criar_sala(client, bob_id)
        assert _enviar(client, sala_id, "Olá!").status_code == 201

        resp = client.get("/api/chat/conversas")
        assert resp.status_code == status.HTTP_200_OK
        conversas = resp.json()
        assert len(conversas) == 1
        conversa = conversas[0]
        assert conversa["sala_id"] == sala_id
        assert conversa["outro_usuario"]["nome"] == "Bob Teste"
        assert conversa["ultima_mensagem"]["mensagem"] == "Olá!"


# ---------------------------------------------------------------------------
# Busca de usuários
# ---------------------------------------------------------------------------

class TestBuscarUsuarios:
    """GET /api/chat/usuarios/buscar — autocomplete de usuários."""

    def test_buscar_usuarios_encontra(self, client):
        _registrar(client, "Alice", "alice@example.com")
        _registrar(client, "Bob Marley", "bob@example.com")

        _login(client, "alice@example.com")
        resp = client.get("/api/chat/usuarios/buscar", params={"q": "Bob"})
        assert resp.status_code == status.HTTP_200_OK
        resultados = resp.json()
        assert isinstance(resultados, list)
        assert any(u["nome"] == "Bob Marley" for u in resultados)
        # Não retorna o próprio usuário logado
        assert all(u["email"] != "alice@example.com" for u in resultados)

    def test_buscar_usuarios_termo_curto_vazio(self, client):
        """Termo com menos de 2 caracteres retorna lista vazia."""
        _registrar(client, "Alice", "alice@example.com")
        _login(client, "alice@example.com")
        resp = client.get("/api/chat/usuarios/buscar", params={"q": "a"})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_buscar_usuarios_exclui_admin(self, client):
        """Administradores não aparecem nos resultados da busca."""
        from repo import usuario_repo
        from model.usuario_model import Usuario
        from util.security import criar_hash_senha
        from util.perfis import Perfil

        usuario_repo.inserir(
            Usuario(
                id=0,
                nome="Admin Buscavel",
                email="adminbusca@example.com",
                senha=criar_hash_senha("Admin@123"),
                perfil=Perfil.ADMIN.value,
            )
        )
        _registrar(client, "Alice", "alice@example.com")
        _login(client, "alice@example.com")

        resp = client.get("/api/chat/usuarios/buscar", params={"q": "Admin"})
        assert resp.status_code == status.HTTP_200_OK
        assert all(u["nome"] != "Admin Buscavel" for u in resp.json())
