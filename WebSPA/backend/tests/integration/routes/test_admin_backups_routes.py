"""
Testes de integração das rotas administrativas de backups (contrato JSON / SPA).

Endpoints sob ``/api/admin/backups`` (admin-only):
- ``GET    /api/admin/backups``                      -> 200, lista de BackupInfoResponse
- ``POST   /api/admin/backups``                      -> 201, BackupInfoResponse
- ``GET    /api/admin/backups/{nome}/download``      -> 200, FileResponse binário
- ``POST   /api/admin/backups/{nome}/restaurar``     -> 200, MensagemResponse
- ``DELETE /api/admin/backups/{nome}``               -> 204, sem corpo

Acesso restrito a ``Perfil.ADMIN``: não-admin recebe 403, sem sessão 401.
Mutações exigem ``X-CSRF-Token`` (de ``GET /api/csrf-token``).
"""
import pytest
from fastapi import status


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _csrf(client):
    """Obtém um token CSRF válido para a sessão atual."""
    return client.get("/api/csrf-token").json()["token"]


def _criar_backup_via_api(client):
    """Cria um backup pela API (admin autenticado) e retorna o nome do arquivo."""
    token = _csrf(client)
    resp = client.post("/api/admin/backups", headers={"X-CSRF-Token": token})
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    return resp.json()["nome_arquivo"]


@pytest.fixture(autouse=True)
def _limpar_backups():
    """
    Garante diretório de backups limpo antes/depois de cada teste, para
    isolar os cenários (criação/listagem/exclusão contam arquivos).
    """
    from util import backup_util

    def _limpar():
        for b in backup_util.listar_backups():
            backup_util.excluir_backup(b.nome_arquivo)
        # Remover também backups automáticos de segurança (pré-restauração)
        for arquivo in backup_util.BACKUP_DIR.glob("backup_auto_*.db"):
            try:
                arquivo.unlink()
            except OSError:
                pass

    _limpar()
    yield
    _limpar()


# ---------------------------------------------------------------------------
# Controle de acesso
# ---------------------------------------------------------------------------

class TestAcessoBackups:
    """Apenas administradores acessam o módulo de backups."""

    def test_listar_sem_auth_401(self, client):
        resp = client.get("/api/admin/backups")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_listar_nao_admin_403(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/admin/backups")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_criar_nao_admin_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/admin/backups", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_excluir_nao_admin_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.delete(
            "/api/admin/backups/backup_qualquer.db",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_download_nao_admin_403(self, cliente_autenticado):
        resp = cliente_autenticado.get(
            "/api/admin/backups/backup_qualquer.db/download"
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_restaurar_nao_admin_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/admin/backups/backup_qualquer.db/restaurar",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Criação
# ---------------------------------------------------------------------------

class TestCriarBackup:
    """POST /api/admin/backups — cria backup manual."""

    def test_criar_backup_201(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            "/api/admin/backups", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_201_CREATED
        body = resp.json()
        assert body["nome_arquivo"].startswith("backup_")
        assert body["nome_arquivo"].endswith(".db")
        assert body["tipo"] == "manual"
        assert body["tamanho_bytes"] >= 0
        assert "tamanho_formatado" in body
        assert "data_criacao" in body


# ---------------------------------------------------------------------------
# Listagem
# ---------------------------------------------------------------------------

class TestListarBackups:
    """GET /api/admin/backups — lista backups disponíveis."""

    def test_listar_vazio_200(self, admin_autenticado):
        resp = admin_autenticado.get("/api/admin/backups")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_listar_apos_criar(self, admin_autenticado):
        nome = _criar_backup_via_api(admin_autenticado)
        resp = admin_autenticado.get("/api/admin/backups")
        assert resp.status_code == status.HTTP_200_OK
        backups = resp.json()
        assert isinstance(backups, list)
        assert any(b["nome_arquivo"] == nome for b in backups)


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

class TestDownloadBackup:
    """GET /api/admin/backups/{nome}/download — download binário."""

    def test_download_200_binario(self, admin_autenticado):
        nome = _criar_backup_via_api(admin_autenticado)
        resp = admin_autenticado.get(f"/api/admin/backups/{nome}/download")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.headers["content-type"] == "application/octet-stream"
        # Conteúdo binário deve estar presente
        assert isinstance(resp.content, bytes)
        assert len(resp.content) > 0
        # SQLite files começam com a assinatura "SQLite format 3\x00"
        assert resp.content[:16] == b"SQLite format 3\x00"

    def test_download_inexistente_404(self, admin_autenticado):
        resp = admin_autenticado.get(
            "/api/admin/backups/backup_2099-01-01_00-00-00.db/download"
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Restauração
# ---------------------------------------------------------------------------

class TestRestaurarBackup:
    """POST /api/admin/backups/{nome}/restaurar — restaura o banco."""

    def test_restaurar_200(self, admin_autenticado):
        nome = _criar_backup_via_api(admin_autenticado)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            f"/api/admin/backups/{nome}/restaurar",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert "message" in resp.json()

    def test_restaurar_inexistente_404(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            "/api/admin/backups/backup_2099-01-01_00-00-00.db/restaurar",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Exclusão
# ---------------------------------------------------------------------------

class TestExcluirBackup:
    """DELETE /api/admin/backups/{nome} — exclui um backup."""

    def test_excluir_204(self, admin_autenticado):
        nome = _criar_backup_via_api(admin_autenticado)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.delete(
            f"/api/admin/backups/{nome}", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert resp.content == b""

        # Backup não deve mais aparecer na listagem
        lista = admin_autenticado.get("/api/admin/backups").json()
        assert all(b["nome_arquivo"] != nome for b in lista)

    def test_excluir_inexistente_404(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.delete(
            "/api/admin/backups/backup_2099-01-01_00-00-00.db",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
