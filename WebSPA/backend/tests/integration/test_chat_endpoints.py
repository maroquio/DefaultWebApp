"""
Testes de endpoint do módulo de chat (routes/chat_routes.py, prefixo /api/chat).

Cobre caminhos felizes e tristes de:
    GET  /api/chat/stream                     (SSE — text/event-stream)
    POST /api/chat/salas
    GET  /api/chat/conversas
    GET  /api/chat/mensagens/{sala_id}
    POST /api/chat/mensagens
    POST /api/chat/mensagens/lidas/{sala_id}
    GET  /api/chat/mensagens/nao-lidas/total
    GET  /api/chat/usuarios/buscar
    GET  /api/chat/health

Contrato (ver CLAUDE.md):
    - Sucesso: recurso puro com status correto (200/201) ou MensagemResponse.
    - Erro: {detail, type, errors} via util/exception_handlers.py.
    - Mutações exigem header X-CSRF-Token (senão 403, type="forbidden").
    - Sessão por cookie; @requer_autenticacao() → 401 sem sessão.

⚠️ SSE: GET /api/chat/stream é StreamingResponse e PENDURA o TestClient se o
corpo for lido. Os testes do caminho feliz usam `with client.stream(...)`,
verificam apenas status + content-type e fecham IMEDIATAMENTE sem iterar o
corpo. O caminho triste (401 sem sessão) é seguro com get() comum porque o
gate de auth dispara ANTES de qualquer streaming.
"""
import pytest
from fastapi import status

from util.perfis import Perfil


pytestmark = [pytest.mark.integration]


def _csrf(client):
    """Obtém um token CSRF válido para a sessão do cliente."""
    return client.get("/api/csrf-token").json()["token"]


# =============================================================================
# Isolamento de tabelas de chat (NÃO limpas pelo conftest)
# =============================================================================

@pytest.fixture(autouse=True)
def _limpar_tabelas_chat():  # pyright: ignore
    """Limpa as três tabelas de chat antes e depois de cada teste.

    Ordem respeitando FK: mensagem → participante → sala.
    """
    from util.db_util import obter_conexao

    def _limpa():
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name IN ('chat_mensagem', 'chat_participante', 'chat_sala')"
            )
            existentes = {row[0] for row in cursor.fetchall()}
            if "chat_mensagem" in existentes:
                cursor.execute("DELETE FROM chat_mensagem")
            if "chat_participante" in existentes:
                cursor.execute("DELETE FROM chat_participante")
            if "chat_sala" in existentes:
                cursor.execute("DELETE FROM chat_sala")
            conn.commit()

    _limpa()
    yield
    _limpa()


# =============================================================================
# Helpers de setup
# =============================================================================

def _meu_id(client):
    """Retorna o id do usuário logado via GET /api/me."""
    return client.get("/api/me").json()["id"]


def _criar_sala(client, outro_usuario_id):
    """Cria/obtém uma sala entre o usuário logado e outro; retorna sala_id."""
    token = _csrf(client)
    resp = client.post(
        "/api/chat/salas",
        json={"outro_usuario_id": outro_usuario_id},
        headers={"X-CSRF-Token": token},
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    return resp.json()["sala_id"]


# =============================================================================
# GET /api/chat/stream  (SSE)
# =============================================================================

class TestStream:
    def test_sem_sessao_401(self, client):
        """Caminho triste seguro: o gate de auth dispara antes de qualquer
        streaming, então get() comum NÃO pendura."""
        resp = client.get("/api/chat/stream")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    async def test_autenticado_recebe_evento_sse(self):
        """Happy-path real do SSE, dirigindo a app ASGI diretamente.

        O ``TestClient`` síncrono pendura no stream (o gerador bloqueia em
        ``queue.get()`` sem produtor concorrente) e ``httpx.ASGITransport`` não
        faz streaming incremental — coleta a resposta inteira e travaria no
        gerador infinito. Então acionamos ``app(scope, receive, send)`` na mão:
        injetamos o cookie de sessão (obtido por um login real), rodamos a app
        como task, empurramos um evento para a fila do usuário conectado e
        confirmamos que ele sai formatado como ``data: ...``. Cancelamos a task
        após o primeiro chunk (o ``finally`` do gerador desconecta o usuário).
        """
        import asyncio

        from fastapi.testclient import TestClient

        from main import app
        from model.usuario_model import Usuario
        from repo import usuario_repo
        from util.chat_manager import gerenciador_chat
        from util.security import criar_hash_senha

        # Usuário próprio (autouse já limpou a tabela usuario antes do teste)
        uid = usuario_repo.inserir(
            Usuario(
                id=0,
                nome="Usuario SSE",
                email="sse@example.com",
                senha=criar_hash_senha("Senha@123"),
                perfil=Perfil.CLIENTE.value,
            )
        )

        # Cookie de sessão assinado, via login real num TestClient síncrono.
        with TestClient(app) as c:
            tok = c.get("/api/csrf-token").json()["token"]
            login = c.post(
                "/api/login",
                json={"email": "sse@example.com", "senha": "Senha@123"},
                headers={"X-CSRF-Token": tok},
            )
            assert login.status_code == status.HTTP_200_OK
            session_cookie = c.cookies.get("session")
        assert session_cookie, "cookie de sessão não emitido no login"

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/api/chat/stream",
            "raw_path": b"/api/chat/stream",
            "query_string": b"",
            "root_path": "",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
            "headers": [
                (b"host", b"testserver"),
                (b"cookie", b"session=" + session_cookie.encode()),
            ],
        }

        inicio: dict = {}
        body_chunks: list[bytes] = []
        primeiro_chunk = asyncio.Event()

        async def receive():
            # Mantém a "conexão" aberta; só liberamos via cancel da task.
            await asyncio.sleep(3600)
            return {"type": "http.disconnect"}

        async def send(message):
            if message["type"] == "http.response.start":
                inicio["status"] = message["status"]
                inicio["headers"] = dict(message.get("headers", []))
            elif message["type"] == "http.response.body":
                corpo = message.get("body") or b""
                if corpo:
                    body_chunks.append(corpo)
                    primeiro_chunk.set()

        app_task = asyncio.create_task(app(scope, receive, send))

        # Espera a conexão ser registrada e injeta um evento na fila do usuário.
        fila = None
        for _ in range(500):
            fila = gerenciador_chat._connections.get(uid)
            if fila is not None:
                fila.put_nowait({"tipo": "teste_sse", "conteudo": "ola"})
                break
            await asyncio.sleep(0.01)
        assert fila is not None, "usuário não foi registrado no GerenciadorChat"

        try:
            await asyncio.wait_for(primeiro_chunk.wait(), timeout=5)
        finally:
            app_task.cancel()
            try:
                await app_task
            except (asyncio.CancelledError, Exception):
                pass
            await gerenciador_chat.desconectar(uid)

        assert inicio.get("status") == status.HTTP_200_OK
        assert b"text/event-stream" in inicio["headers"].get(b"content-type", b"")
        corpo = b"".join(body_chunks).decode()
        assert "teste_sse" in corpo
        assert "ola" in corpo

    def test_stream_registrado_como_sse(self):
        """Verifica, sem abrir conexão viva, que a rota /api/chat/stream existe
        e está montada como GET sob /api/chat (inspeção da app, não request).

        Isto cobre o 'wiring' do caminho feliz com segurança: confirma que
        existe exatamente uma rota com esse path e que o método GET está
        presente — sem acoplar a nomes internos de função e sem disparar o
        gerador infinito que pendura o TestClient."""
        from main import app

        rotas_stream = [
            r for r in app.routes
            if getattr(r, "path", None) == "/api/chat/stream"
        ]
        assert len(rotas_stream) == 1
        rota = rotas_stream[0]
        assert "GET" in (getattr(rota, "methods", None) or set())


# =============================================================================
# POST /api/chat/salas
# =============================================================================

class TestCriarSala:
    def test_cria_sala_sucesso_201(self, cliente_autenticado, criar_usuario_direto):
        outro = criar_usuario_direto("Outro Um", "outro1@example.com", "Senha@123")
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chat/salas",
            json={"outro_usuario_id": outro},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        corpo = resp.json()
        assert "sala_id" in corpo
        # Determinístico: menor_id_maior_id
        meu = _meu_id(cliente_autenticado)
        esperado = f"{min(meu, outro)}_{max(meu, outro)}"
        assert corpo["sala_id"] == esperado

    def test_idempotente_mesma_sala(self, cliente_autenticado, criar_usuario_direto):
        outro = criar_usuario_direto("Outro Idem", "outroidem@example.com", "Senha@123")
        primeira = _criar_sala(cliente_autenticado, outro)
        segunda = _criar_sala(cliente_autenticado, outro)
        assert primeira == segunda

    def test_sem_sessao_401(self, client, criar_usuario_direto):
        outro = criar_usuario_direto("Outro 401", "outro401@example.com", "Senha@123")
        token = _csrf(client)
        resp = client.post(
            "/api/chat/salas",
            json={"outro_usuario_id": outro},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_sem_csrf_403(self, cliente_autenticado, criar_usuario_direto):
        outro = criar_usuario_direto("Outro Csrf", "outrocsrf@example.com", "Senha@123")
        resp = cliente_autenticado.post(
            "/api/chat/salas",
            json={"outro_usuario_id": outro},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_consigo_mesmo_400(self, cliente_autenticado):
        meu = _meu_id(cliente_autenticado)
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chat/salas",
            json={"outro_usuario_id": meu},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json()["type"] == "bad_request"

    def test_usuario_inexistente_404(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chat/salas",
            json={"outro_usuario_id": 999999},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_id_invalido_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chat/salas",
            json={"outro_usuario_id": -5},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_payload_faltando_campo_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chat/salas",
            json={},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_rate_limit_429(self, cliente_autenticado, criar_usuario_direto, bloquear_rate_limiter):
        outro = criar_usuario_direto("Outro RL", "outrorl@example.com", "Senha@123")
        token = _csrf(cliente_autenticado)
        with bloquear_rate_limiter("routes.chat_routes.chat_sala_limiter"):
            resp = cliente_autenticado.post(
                "/api/chat/salas",
                json={"outro_usuario_id": outro},
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert resp.json()["type"] == "rate_limited"
        assert "Retry-After" in resp.headers


# =============================================================================
# GET /api/chat/conversas
# =============================================================================

class TestListarConversas:
    def test_lista_vazia_200(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/chat/conversas")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_lista_com_conversa_200(self, cliente_autenticado, criar_usuario_direto):
        outro = criar_usuario_direto("Conversa A", "conva@example.com", "Senha@123")
        sala_id = _criar_sala(cliente_autenticado, outro)
        resp = cliente_autenticado.get("/api/chat/conversas")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert len(corpo) == 1
        conversa = corpo[0]
        assert conversa["sala_id"] == sala_id
        assert conversa["outro_usuario"]["id"] == outro
        assert conversa["outro_usuario"]["nome"] == "Conversa A"
        assert conversa["nao_lidas"] == 0
        assert conversa["ultima_mensagem"] is None

    def test_conversa_reflete_mensagem_nao_lida(
        self, cliente_autenticado, criar_usuario_direto
    ):
        """Mensagem enviada pelo OUTRO usuário aparece como não lida."""
        from repo import chat_mensagem_repo
        outro = criar_usuario_direto("Conversa NL", "convnl@example.com", "Senha@123")
        sala_id = _criar_sala(cliente_autenticado, outro)
        chat_mensagem_repo.inserir(sala_id, outro, "Olá!")
        resp = cliente_autenticado.get("/api/chat/conversas")
        conversa = resp.json()[0]
        assert conversa["nao_lidas"] == 1
        assert conversa["ultima_mensagem"]["mensagem"] == "Olá!"
        assert conversa["ultima_mensagem"]["usuario_id"] == outro

    def test_sem_sessao_401(self, client):
        resp = client.get("/api/chat/conversas")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_rate_limit_429(self, cliente_autenticado, bloquear_rate_limiter):
        with bloquear_rate_limiter("routes.chat_routes.chat_listagem_limiter"):
            resp = cliente_autenticado.get("/api/chat/conversas")
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert resp.json()["type"] == "rate_limited"


# =============================================================================
# GET /api/chat/mensagens/{sala_id}
# =============================================================================

class TestListarMensagens:
    def test_lista_mensagens_200(self, cliente_autenticado, criar_usuario_direto):
        from repo import chat_mensagem_repo
        outro = criar_usuario_direto("Msg Lista", "msglista@example.com", "Senha@123")
        sala_id = _criar_sala(cliente_autenticado, outro)
        chat_mensagem_repo.inserir(sala_id, outro, "Primeira")
        chat_mensagem_repo.inserir(sala_id, _meu_id(cliente_autenticado), "Segunda")
        resp = cliente_autenticado.get(f"/api/chat/mensagens/{sala_id}")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert len(corpo) == 2
        textos = {m["mensagem"] for m in corpo}
        assert textos == {"Primeira", "Segunda"}
        for m in corpo:
            assert m["sala_id"] == sala_id
            assert "id" in m and "usuario_id" in m

    def test_sala_sem_mensagens_lista_vazia_200(self, cliente_autenticado, criar_usuario_direto):
        outro = criar_usuario_direto("Msg Vazia", "msgvazia@example.com", "Senha@123")
        sala_id = _criar_sala(cliente_autenticado, outro)
        resp = cliente_autenticado.get(f"/api/chat/mensagens/{sala_id}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_sem_sessao_401(self, client):
        resp = client.get("/api/chat/mensagens/1_2")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_sala_que_nao_participa_403(self, cliente_autenticado, criar_usuario_direto):
        """Sala existe entre OUTROS dois usuários; o logado não participa → 403."""
        from repo import chat_sala_repo, chat_participante_repo
        a = criar_usuario_direto("Alheio A", "alheioa@example.com", "Senha@123")
        b = criar_usuario_direto("Alheio B", "alheiob@example.com", "Senha@123")
        sala = chat_sala_repo.criar_ou_obter_sala(a, b)
        chat_participante_repo.adicionar_participante(sala.id, a)
        chat_participante_repo.adicionar_participante(sala.id, b)
        resp = cliente_autenticado.get(f"/api/chat/mensagens/{sala.id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_sala_inexistente_403(self, cliente_autenticado):
        """Sala que não existe: rota checa participação primeiro → 403 (não 404)."""
        resp = cliente_autenticado.get("/api/chat/mensagens/9991_9992")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_rate_limit_429(self, cliente_autenticado, criar_usuario_direto, bloquear_rate_limiter):
        outro = criar_usuario_direto("Msg RL", "msgrl@example.com", "Senha@123")
        sala_id = _criar_sala(cliente_autenticado, outro)
        with bloquear_rate_limiter("routes.chat_routes.chat_listagem_limiter"):
            resp = cliente_autenticado.get(f"/api/chat/mensagens/{sala_id}")
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert resp.json()["type"] == "rate_limited"


# =============================================================================
# POST /api/chat/mensagens
# =============================================================================

class TestEnviarMensagem:
    def test_envia_sucesso_201(self, cliente_autenticado, criar_usuario_direto):
        outro = criar_usuario_direto("Env A", "enva@example.com", "Senha@123")
        sala_id = _criar_sala(cliente_autenticado, outro)
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chat/mensagens",
            json={"sala_id": sala_id, "mensagem": "Oi tudo bem?"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        corpo = resp.json()
        assert corpo["sala_id"] == sala_id
        assert corpo["mensagem"] == "Oi tudo bem?"
        assert corpo["usuario_id"] == _meu_id(cliente_autenticado)
        assert corpo["lida_em"] is None
        assert "id" in corpo

    def test_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.post(
            "/api/chat/mensagens",
            json={"sala_id": "1_2", "mensagem": "Oi"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_sem_csrf_403(self, cliente_autenticado, criar_usuario_direto):
        outro = criar_usuario_direto("Env Csrf", "envcsrf@example.com", "Senha@123")
        sala_id = _criar_sala(cliente_autenticado, outro)
        resp = cliente_autenticado.post(
            "/api/chat/mensagens",
            json={"sala_id": sala_id, "mensagem": "Oi"},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_sala_que_nao_participa_403(self, cliente_autenticado, criar_usuario_direto):
        from repo import chat_sala_repo, chat_participante_repo
        a = criar_usuario_direto("EnvAlheio A", "envalheioa@example.com", "Senha@123")
        b = criar_usuario_direto("EnvAlheio B", "envalheiob@example.com", "Senha@123")
        sala = chat_sala_repo.criar_ou_obter_sala(a, b)
        chat_participante_repo.adicionar_participante(sala.id, a)
        chat_participante_repo.adicionar_participante(sala.id, b)
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chat/mensagens",
            json={"sala_id": sala.id, "mensagem": "Intruso"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_mensagem_vazia_422(self, cliente_autenticado, criar_usuario_direto):
        outro = criar_usuario_direto("Env Vazia", "envvazia@example.com", "Senha@123")
        sala_id = _criar_sala(cliente_autenticado, outro)
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chat/mensagens",
            json={"sala_id": sala_id, "mensagem": "   "},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_sala_id_vazio_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chat/mensagens",
            json={"sala_id": "", "mensagem": "Oi"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_rate_limit_429(self, cliente_autenticado, criar_usuario_direto, bloquear_rate_limiter):
        outro = criar_usuario_direto("Env RL", "envrl@example.com", "Senha@123")
        sala_id = _criar_sala(cliente_autenticado, outro)
        token = _csrf(cliente_autenticado)
        with bloquear_rate_limiter("routes.chat_routes.chat_mensagem_limiter"):
            resp = cliente_autenticado.post(
                "/api/chat/mensagens",
                json={"sala_id": sala_id, "mensagem": "Oi"},
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert resp.json()["type"] == "rate_limited"
        assert "Retry-After" in resp.headers


# =============================================================================
# POST /api/chat/mensagens/lidas/{sala_id}
# =============================================================================

class TestMarcarComoLidas:
    def test_marca_lidas_sucesso_200(self, cliente_autenticado, criar_usuario_direto):
        from repo import chat_mensagem_repo
        outro = criar_usuario_direto("Lidas A", "lidasa@example.com", "Senha@123")
        sala_id = _criar_sala(cliente_autenticado, outro)
        chat_mensagem_repo.inserir(sala_id, outro, "Mensagem nao lida")
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            f"/api/chat/mensagens/lidas/{sala_id}",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert "message" in resp.json()
        # Após marcar, o total não lidas deve zerar
        total = cliente_autenticado.get("/api/chat/mensagens/nao-lidas/total").json()
        assert total["total"] == 0

    def test_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.post(
            "/api/chat/mensagens/lidas/1_2",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_sem_csrf_403(self, cliente_autenticado, criar_usuario_direto):
        outro = criar_usuario_direto("Lidas Csrf", "lidascsrf@example.com", "Senha@123")
        sala_id = _criar_sala(cliente_autenticado, outro)
        resp = cliente_autenticado.post(f"/api/chat/mensagens/lidas/{sala_id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_sala_que_nao_participa_403(self, cliente_autenticado, criar_usuario_direto):
        from repo import chat_sala_repo, chat_participante_repo
        a = criar_usuario_direto("LidasAlheio A", "lidasalheioa@example.com", "Senha@123")
        b = criar_usuario_direto("LidasAlheio B", "lidasalheiob@example.com", "Senha@123")
        sala = chat_sala_repo.criar_ou_obter_sala(a, b)
        chat_participante_repo.adicionar_participante(sala.id, a)
        chat_participante_repo.adicionar_participante(sala.id, b)
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            f"/api/chat/mensagens/lidas/{sala.id}",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"


# =============================================================================
# GET /api/chat/mensagens/nao-lidas/total
# =============================================================================

class TestTotalNaoLidas:
    def test_total_zero_200(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/chat/mensagens/nao-lidas/total")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["total"] == 0

    def test_total_soma_varias_salas(self, cliente_autenticado, criar_usuario_direto):
        from repo import chat_mensagem_repo
        a = criar_usuario_direto("Total A", "totala@example.com", "Senha@123")
        b = criar_usuario_direto("Total B", "totalb@example.com", "Senha@123")
        sala_a = _criar_sala(cliente_autenticado, a)
        sala_b = _criar_sala(cliente_autenticado, b)
        chat_mensagem_repo.inserir(sala_a, a, "msg1")
        chat_mensagem_repo.inserir(sala_a, a, "msg2")
        chat_mensagem_repo.inserir(sala_b, b, "msg3")
        resp = cliente_autenticado.get("/api/chat/mensagens/nao-lidas/total")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["total"] == 3

    def test_sem_sessao_401(self, client):
        resp = client.get("/api/chat/mensagens/nao-lidas/total")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# GET /api/chat/usuarios/buscar
# =============================================================================

class TestBuscarUsuarios:
    def test_busca_encontra_usuario_200(self, cliente_autenticado, criar_usuario_direto):
        criar_usuario_direto("Busca Alvo", "buscaalvo@example.com", "Senha@123")
        resp = cliente_autenticado.get("/api/chat/usuarios/buscar", params={"q": "Busca Alvo"})
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert any(u["nome"] == "Busca Alvo" for u in corpo)
        for u in corpo:
            assert "id" in u and "email" in u and "foto_url" in u

    def test_termo_curto_retorna_vazio(self, cliente_autenticado, criar_usuario_direto):
        criar_usuario_direto("Z", "zzz@example.com", "Senha@123")
        resp = cliente_autenticado.get("/api/chat/usuarios/buscar", params={"q": "a"})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_exclui_proprio_usuario(self, cliente_autenticado, usuario_teste):
        resp = cliente_autenticado.get(
            "/api/chat/usuarios/buscar", params={"q": usuario_teste["nome"]}
        )
        assert resp.status_code == status.HTTP_200_OK
        meu = _meu_id(cliente_autenticado)
        assert all(u["id"] != meu for u in resp.json())

    def test_exclui_admin(self, cliente_autenticado, criar_usuario_direto):
        criar_usuario_direto(
            "Admin Oculto", "adminoculto@example.com", "Admin@123", Perfil.ADMIN.value
        )
        resp = cliente_autenticado.get(
            "/api/chat/usuarios/buscar", params={"q": "Admin Oculto"}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert all(u["email"] != "adminoculto@example.com" for u in resp.json())

    def test_sem_sessao_401(self, client):
        resp = client.get("/api/chat/usuarios/buscar", params={"q": "qualquer"})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_sem_query_obrigatoria_422(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/chat/usuarios/buscar")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_rate_limit_429(self, cliente_autenticado, bloquear_rate_limiter):
        with bloquear_rate_limiter("routes.chat_routes.busca_usuarios_limiter"):
            resp = cliente_autenticado.get(
                "/api/chat/usuarios/buscar", params={"q": "teste"}
            )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert resp.json()["type"] == "rate_limited"
        assert "Retry-After" in resp.headers


# =============================================================================
# GET é isento de CSRF (o middleware só checa mutações)
# =============================================================================

class TestGetIsentoCsrf:
    def test_get_conversas_ignora_csrf_invalido_200(self, cliente_autenticado):
        """GET é isento de CSRF: um X-CSRF-Token inválido NÃO bloqueia o GET.

        Não usamos /stream aqui (StreamingResponse pendura o TestClient).
        """
        resp = cliente_autenticado.get(
            "/api/chat/conversas",
            headers={"X-CSRF-Token": "token-errado"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_get_total_nao_lidas_ignora_csrf_invalido_200(self, cliente_autenticado):
        """Reforço: outro GET com CSRF inválido ainda retorna 200."""
        resp = cliente_autenticado.get(
            "/api/chat/mensagens/nao-lidas/total",
            headers={"X-CSRF-Token": "token-errado"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["total"] == 0


# =============================================================================
# Vendedor autenticado consegue acessar o chat (@requer_autenticacao() sem lista)
# =============================================================================

class TestVendedorAcessaChat:
    def test_vendedor_lista_conversas_200(self, vendedor_autenticado):
        """@requer_autenticacao() sem lista de perfis permite QUALQUER usuário
        autenticado — inclusive VENDEDOR."""
        resp = vendedor_autenticado.get("/api/chat/conversas")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_vendedor_total_nao_lidas_200(self, vendedor_autenticado):
        resp = vendedor_autenticado.get("/api/chat/mensagens/nao-lidas/total")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["total"] == 0


# =============================================================================
# GET /api/chat/health
# =============================================================================

class TestChatHealth:
    def test_health_publico_200(self, client):
        """Health não exige autenticação."""
        resp = client.get("/api/chat/health")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["status"] == "healthy"
        assert "conexoes_ativas" in corpo
        assert "timestamp" in corpo
