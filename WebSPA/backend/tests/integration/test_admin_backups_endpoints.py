"""
Testes de endpoint das rotas administrativas de backups
(routes/admin_backups_routes.py — prefixo /api/admin/backups, exigem ADMIN).

Cobre caminhos felizes e tristes de:
    GET    /api/admin/backups               (listar)
    POST   /api/admin/backups               (criar)
    GET    /api/admin/backups/{nome}/download
    POST   /api/admin/backups/{nome}/restaurar
    DELETE /api/admin/backups/{nome}        (excluir)

⚠️ FILESYSTEM: todas as funções de util/backup_util que tocam o disco real
(listar_backups, criar_backup, restaurar_backup, excluir_backup,
obter_caminho_backup) são MOCKADAS no ponto de uso (routes.admin_backups_routes).
Nenhum arquivo real é criado/restaurado/excluído em backups/ e dados.db nunca é
tocado. O único arquivo real escrito é um tempfile próprio do teste de download
(removido ao final do teste).

Contrato (ver CLAUDE.md):
    - @requer_autenticacao([ADMIN]) → 401 sem sessão; 403 perfil não-admin.
    - Mutações (POST/DELETE) exigem header X-CSRF-Token → 403 sem ele.
    - Erro: {detail, type, errors} via util/exception_handlers.py.

Descobertas sobre o contrato real (ver retorno do agente):
    - Path traversal / nome inválido NÃO retorna 400. O util valida o nome:
      * download  → obter_caminho_backup() devolve None → 404 "Backup não encontrado."
      * restaurar → restaurar_backup() devolve msg com "inválido" → 404
      * excluir   → excluir_backup() devolve msg com "inválido" → 404
"""
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import status

from util.backup_util import BackupInfo


pytestmark = [pytest.mark.integration]


def _csrf(client):
    """Obtém um token CSRF válido para a sessão do cliente."""
    return client.get("/api/csrf-token").json()["token"]


def _fake_backup(nome="backup_2026-06-18_10-00-00.db", tipo="manual", tamanho=2048):
    """Constrói um BackupInfo fake (sem tocar no disco)."""
    return BackupInfo(
        nome_arquivo=nome,
        caminho_completo=f"backups/{nome}",
        data_criacao=datetime(2026, 6, 18, 10, 0, 0),
        tamanho_bytes=tamanho,
        tamanho_formatado="2.00 KB",
        tipo=tipo,
    )


# Caminho base para o patch das funções no ponto de uso (módulo da rota).
_MOD = "routes.admin_backups_routes.backup_util"


# =============================================================================
# GET /api/admin/backups  (listar)
# =============================================================================

class TestListarBackups:
    def test_listar_sucesso_retorna_lista(self, admin_autenticado):
        fakes = [
            _fake_backup("backup_2026-06-18_10-00-00.db", "manual"),
            _fake_backup("backup_auto_2026-06-17_09-00-00.db", "automático", 1024),
        ]
        with patch(f"{_MOD}.listar_backups", return_value=fakes):
            resp = admin_autenticado.get("/api/admin/backups")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert isinstance(corpo, list)
        assert len(corpo) == 2
        primeiro = corpo[0]
        assert primeiro["nome_arquivo"] == "backup_2026-06-18_10-00-00.db"
        assert primeiro["tipo"] == "manual"
        assert primeiro["tamanho_bytes"] == 2048
        assert "data_criacao" in primeiro
        assert primeiro["tamanho_formatado"] == "2.00 KB"

    def test_listar_vazio_retorna_lista_vazia(self, admin_autenticado):
        with patch(f"{_MOD}.listar_backups", return_value=[]):
            resp = admin_autenticado.get("/api/admin/backups")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_listar_sem_sessao_401(self, client):
        # Mesmo mockado, a autenticação deve barrar antes.
        with patch(f"{_MOD}.listar_backups", return_value=[]):
            resp = client.get("/api/admin/backups")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_listar_perfil_nao_admin_403(self, cliente_autenticado):
        with patch(f"{_MOD}.listar_backups", return_value=[]):
            resp = cliente_autenticado.get("/api/admin/backups")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"


# =============================================================================
# POST /api/admin/backups  (criar)
# =============================================================================

class TestCriarBackup:
    def test_criar_sucesso_retorna_201(self, admin_autenticado):
        criado = _fake_backup("backup_2026-06-18_11-00-00.db", "manual")
        token = _csrf(admin_autenticado)
        with patch(f"{_MOD}.criar_backup", return_value=(True, "Backup manual criado")), \
             patch(f"{_MOD}.listar_backups", return_value=[criado]):
            resp = admin_autenticado.post(
                "/api/admin/backups", headers={"X-CSRF-Token": token}
            )
        assert resp.status_code == status.HTTP_201_CREATED
        corpo = resp.json()
        assert corpo["nome_arquivo"] == "backup_2026-06-18_11-00-00.db"
        assert corpo["tipo"] == "manual"

    def test_criar_falha_util_retorna_500(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        with patch(f"{_MOD}.criar_backup", return_value=(False, "Disco cheio")):
            resp = admin_autenticado.post(
                "/api/admin/backups", headers={"X-CSRF-Token": token}
            )
        assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert resp.json()["type"] == "internal_error"

    def test_criar_sem_recuperar_info_retorna_500(self, admin_autenticado):
        """criar_backup ok, mas listar_backups não retorna nenhum manual → 500."""
        token = _csrf(admin_autenticado)
        auto = _fake_backup("backup_auto_2026-06-18_11-00-00.db", "automático")
        with patch(f"{_MOD}.criar_backup", return_value=(True, "ok")), \
             patch(f"{_MOD}.listar_backups", return_value=[auto]):
            resp = admin_autenticado.post(
                "/api/admin/backups", headers={"X-CSRF-Token": token}
            )
        assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_criar_sem_csrf_403(self, admin_autenticado):
        # Não deve nem chegar ao util; ainda assim mockamos por segurança.
        with patch(f"{_MOD}.criar_backup", return_value=(True, "ok")), \
             patch(f"{_MOD}.listar_backups", return_value=[]):
            resp = admin_autenticado.post("/api/admin/backups")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_criar_sem_sessao_401(self, client):
        token = _csrf(client)
        with patch(f"{_MOD}.criar_backup", return_value=(True, "ok")), \
             patch(f"{_MOD}.listar_backups", return_value=[]):
            resp = client.post("/api/admin/backups", headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_criar_perfil_nao_admin_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        with patch(f"{_MOD}.criar_backup", return_value=(True, "ok")), \
             patch(f"{_MOD}.listar_backups", return_value=[]):
            resp = cliente_autenticado.post(
                "/api/admin/backups", headers={"X-CSRF-Token": token}
            )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_criar_excede_rate_limit_429(self, admin_autenticado, bloquear_rate_limiter):
        token = _csrf(admin_autenticado)
        with patch(f"{_MOD}.criar_backup", return_value=(True, "ok")), \
             patch(f"{_MOD}.listar_backups", return_value=[]), \
             bloquear_rate_limiter("routes.admin_backups_routes.admin_backups_limiter"):
            resp = admin_autenticado.post(
                "/api/admin/backups", headers={"X-CSRF-Token": token}
            )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in resp.headers


# =============================================================================
# GET /api/admin/backups/{nome}/download
# =============================================================================

class TestDownloadBackup:
    def test_download_sucesso_retorna_arquivo(self, admin_autenticado):
        nome = "backup_2026-06-18_10-00-00.db"
        fd, caminho = tempfile.mkstemp(suffix=".db")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(b"conteudo-fake-de-backup")
            with patch(f"{_MOD}.obter_caminho_backup", return_value=Path(caminho)):
                resp = admin_autenticado.get(f"/api/admin/backups/{nome}/download")
            assert resp.status_code == status.HTTP_200_OK
            assert resp.headers["content-type"] == "application/octet-stream"
            assert resp.content == b"conteudo-fake-de-backup"
        finally:
            os.unlink(caminho)

    def test_download_inexistente_404(self, admin_autenticado):
        """util devolve None para nome inexistente → 404."""
        nome = "backup_2099-01-01_00-00-00.db"
        with patch(f"{_MOD}.obter_caminho_backup", return_value=None):
            resp = admin_autenticado.get(f"/api/admin/backups/{nome}/download")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_download_caminho_nao_existe_no_disco_404(self, admin_autenticado):
        """obter_caminho_backup devolve Path que não existe → 404."""
        nome = "backup_2026-06-18_10-00-00.db"
        with patch(
            f"{_MOD}.obter_caminho_backup",
            return_value=Path("/tmp/inexistente_xyz_backup.db"),
        ):
            resp = admin_autenticado.get(f"/api/admin/backups/{nome}/download")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_download_path_traversal_404_sem_mock(self, admin_autenticado):
        """
        Nome malicioso com '..' — sem mock, o util real rejeita o nome
        (obter_caminho_backup → None) e a rota responde 404, sem tocar o disco.
        O '..' é codificado para não ser normalizado pelo cliente/roteador.
        """
        nome = "..%2F..%2Fetc%2Fpasswd"
        resp = admin_autenticado.get(f"/api/admin/backups/{nome}/download")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_download_sem_sessao_401(self, client):
        resp = client.get("/api/admin/backups/backup_x.db/download")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_download_perfil_nao_admin_403(self, cliente_autenticado):
        resp = cliente_autenticado.get(
            "/api/admin/backups/backup_x.db/download"
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_download_excede_rate_limit_429(self, admin_autenticado, bloquear_rate_limiter):
        nome = "backup_2026-06-18_10-00-00.db"
        with bloquear_rate_limiter(
            "routes.admin_backups_routes.backup_download_limiter"
        ):
            resp = admin_autenticado.get(f"/api/admin/backups/{nome}/download")
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in resp.headers


# =============================================================================
# POST /api/admin/backups/{nome}/restaurar
# =============================================================================

class TestRestaurarBackup:
    def test_restaurar_sucesso_retorna_mensagem(self, admin_autenticado):
        nome = "backup_2026-06-18_10-00-00.db"
        token = _csrf(admin_autenticado)
        with patch(
            f"{_MOD}.restaurar_backup",
            return_value=(True, "Backup restaurado com sucesso", "backup_auto_x.db"),
        ):
            resp = admin_autenticado.post(
                f"/api/admin/backups/{nome}/restaurar",
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert "message" in corpo
        assert "backup_auto_x.db" in corpo["message"]

    def test_restaurar_sucesso_sem_backup_seguranca(self, admin_autenticado):
        nome = "backup_2026-06-18_10-00-00.db"
        token = _csrf(admin_autenticado)
        with patch(
            f"{_MOD}.restaurar_backup",
            return_value=(True, "Backup restaurado com sucesso", None),
        ):
            resp = admin_autenticado.post(
                f"/api/admin/backups/{nome}/restaurar",
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_200_OK
        assert "Aviso" in resp.json()["message"]

    def test_restaurar_inexistente_404(self, admin_autenticado):
        """msg com 'não encontrado' → 404."""
        nome = "backup_2099-01-01_00-00-00.db"
        token = _csrf(admin_autenticado)
        with patch(
            f"{_MOD}.restaurar_backup",
            return_value=(False, "Arquivo de backup não encontrado", None),
        ):
            resp = admin_autenticado.post(
                f"/api/admin/backups/{nome}/restaurar",
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_restaurar_nome_invalido_404(self, admin_autenticado):
        """msg com 'inválido' → 404 (path traversal mapeado pelo util)."""
        nome = "qualquer_invalido.db"
        token = _csrf(admin_autenticado)
        with patch(
            f"{_MOD}.restaurar_backup",
            return_value=(False, "Nome de arquivo de backup inválido", None),
        ):
            resp = admin_autenticado.post(
                f"/api/admin/backups/{nome}/restaurar",
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_restaurar_falha_integridade_500(self, admin_autenticado):
        """msg sem 'não encontrado'/'inválido' → 500 (falha de integridade)."""
        nome = "backup_2026-06-18_10-00-00.db"
        token = _csrf(admin_autenticado)
        with patch(
            f"{_MOD}.restaurar_backup",
            return_value=(False, "Backup corrompido! Restauração abortada.", None),
        ):
            resp = admin_autenticado.post(
                f"/api/admin/backups/{nome}/restaurar",
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert resp.json()["type"] == "internal_error"

    def test_restaurar_path_traversal_404_sem_mock(self, admin_autenticado):
        """
        Sem mock: o util real valida o nome e devolve msg com 'inválido' → 404.
        Não toca dados.db (a validação acontece antes de qualquer cópia).
        """
        token = _csrf(admin_autenticado)
        nome = "..%2F..%2Fetc%2Fpasswd"
        resp = admin_autenticado.post(
            f"/api/admin/backups/{nome}/restaurar",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_restaurar_sem_csrf_403(self, admin_autenticado):
        nome = "backup_2026-06-18_10-00-00.db"
        with patch(
            f"{_MOD}.restaurar_backup",
            return_value=(True, "ok", None),
        ):
            resp = admin_autenticado.post(f"/api/admin/backups/{nome}/restaurar")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_restaurar_sem_sessao_401(self, client):
        token = _csrf(client)
        with patch(f"{_MOD}.restaurar_backup", return_value=(True, "ok", None)):
            resp = client.post(
                "/api/admin/backups/backup_x.db/restaurar",
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_restaurar_perfil_nao_admin_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        with patch(f"{_MOD}.restaurar_backup", return_value=(True, "ok", None)):
            resp = cliente_autenticado.post(
                "/api/admin/backups/backup_x.db/restaurar",
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_restaurar_excede_rate_limit_429(self, admin_autenticado, bloquear_rate_limiter):
        nome = "backup_2026-06-18_10-00-00.db"
        token = _csrf(admin_autenticado)
        with patch(f"{_MOD}.restaurar_backup", return_value=(True, "ok", None)), \
             bloquear_rate_limiter(
                 "routes.admin_backups_routes.admin_backups_limiter"
             ):
            resp = admin_autenticado.post(
                f"/api/admin/backups/{nome}/restaurar",
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in resp.headers


# =============================================================================
# DELETE /api/admin/backups/{nome}  (excluir)
# =============================================================================

class TestExcluirBackup:
    def test_excluir_sucesso_retorna_204(self, admin_autenticado):
        nome = "backup_2026-06-18_10-00-00.db"
        token = _csrf(admin_autenticado)
        with patch(
            f"{_MOD}.excluir_backup",
            return_value=(True, "Backup excluído com sucesso"),
        ):
            resp = admin_autenticado.delete(
                f"/api/admin/backups/{nome}", headers={"X-CSRF-Token": token}
            )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert resp.content == b""

    def test_excluir_inexistente_404(self, admin_autenticado):
        nome = "backup_2099-01-01_00-00-00.db"
        token = _csrf(admin_autenticado)
        with patch(
            f"{_MOD}.excluir_backup",
            return_value=(False, "Arquivo de backup não encontrado"),
        ):
            resp = admin_autenticado.delete(
                f"/api/admin/backups/{nome}", headers={"X-CSRF-Token": token}
            )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_excluir_nome_invalido_404(self, admin_autenticado):
        nome = "qualquer_invalido.db"
        token = _csrf(admin_autenticado)
        with patch(
            f"{_MOD}.excluir_backup",
            return_value=(False, "Nome de arquivo de backup inválido"),
        ):
            resp = admin_autenticado.delete(
                f"/api/admin/backups/{nome}", headers={"X-CSRF-Token": token}
            )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_excluir_falha_os_500(self, admin_autenticado):
        nome = "backup_2026-06-18_10-00-00.db"
        token = _csrf(admin_autenticado)
        with patch(
            f"{_MOD}.excluir_backup",
            return_value=(False, "Erro ao excluir backup: permissão negada"),
        ):
            resp = admin_autenticado.delete(
                f"/api/admin/backups/{nome}", headers={"X-CSRF-Token": token}
            )
        assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert resp.json()["type"] == "internal_error"

    def test_excluir_path_traversal_404_sem_mock(self, admin_autenticado):
        """Sem mock: util real rejeita '..' → msg 'inválido' → 404, sem tocar disco."""
        token = _csrf(admin_autenticado)
        nome = "..%2F..%2Fetc%2Fpasswd"
        resp = admin_autenticado.delete(
            f"/api/admin/backups/{nome}", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_excluir_sem_csrf_403(self, admin_autenticado):
        nome = "backup_2026-06-18_10-00-00.db"
        with patch(f"{_MOD}.excluir_backup", return_value=(True, "ok")):
            resp = admin_autenticado.delete(f"/api/admin/backups/{nome}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_excluir_sem_sessao_401(self, client):
        token = _csrf(client)
        with patch(f"{_MOD}.excluir_backup", return_value=(True, "ok")):
            resp = client.delete(
                "/api/admin/backups/backup_x.db", headers={"X-CSRF-Token": token}
            )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_excluir_perfil_nao_admin_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        with patch(f"{_MOD}.excluir_backup", return_value=(True, "ok")):
            resp = cliente_autenticado.delete(
                "/api/admin/backups/backup_x.db", headers={"X-CSRF-Token": token}
            )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_excluir_excede_rate_limit_429(self, admin_autenticado, bloquear_rate_limiter):
        nome = "backup_2026-06-18_10-00-00.db"
        token = _csrf(admin_autenticado)
        with patch(f"{_MOD}.excluir_backup", return_value=(True, "ok")), \
             bloquear_rate_limiter(
                 "routes.admin_backups_routes.admin_backups_limiter"
             ):
            resp = admin_autenticado.delete(
                f"/api/admin/backups/{nome}", headers={"X-CSRF-Token": token}
            )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in resp.headers
