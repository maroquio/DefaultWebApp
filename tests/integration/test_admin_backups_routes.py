"""
Testes de gerenciamento de backups
Testa criação, listagem, restauração, exclusão e download de backups
"""
from fastapi import status


class TestListarBackups:
    """Testes de listagem de backups"""

    def test_listar_backups_requer_admin(self, cliente_autenticado):
        """Cliente não deve acessar listagem de backups"""
        response = cliente_autenticado.get("/admin/backups/listar", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_listar_backups_admin_acessa(self, admin_autenticado):
        """Admin deve acessar listagem de backups"""
        response = admin_autenticado.get("/admin/backups/listar")
        assert response.status_code == status.HTTP_200_OK

    def test_listar_backups_exibe_lista(self, admin_autenticado):
        """Deve exibir lista de backups (mesmo que vazia)"""
        response = admin_autenticado.get("/admin/backups/listar")
        assert response.status_code == status.HTTP_200_OK
        assert "backup" in response.text.lower()

    def test_listar_backups_sem_autenticacao(self, client):
        """Não autenticado deve ser redirecionado"""
        response = client.get("/admin/backups/listar", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_vendedor_nao_acessa_listagem(self, vendedor_autenticado):
        """Vendedor não deve acessar listagem de backups"""
        response = vendedor_autenticado.get("/admin/backups/listar", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]


class TestCriarBackup:
    """Testes de criação de backup"""

    def test_criar_backup_por_admin(self, admin_autenticado):
        """Admin deve poder criar backup"""
        response = admin_autenticado.post("/admin/backups/criar", follow_redirects=False)

        # Deve redirecionar para listagem
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/admin/backups/listar"

    def test_criar_backup_cria_arquivo(self, admin_autenticado):
        """Criar backup deve gerar arquivo em backups/"""
        from util import backup_util

        # Criar backup
        admin_autenticado.post("/admin/backups/criar")

        # Verificar que existe pelo menos um backup
        backups = backup_util.listar_backups()
        assert len(backups) > 0

    def test_criar_backup_nome_com_timestamp(self, admin_autenticado):
        """Backup deve ter nome com timestamp"""
        from util import backup_util

        # Criar backup
        admin_autenticado.post("/admin/backups/criar")

        # Verificar formato do nome
        backups = backup_util.listar_backups()
        assert len(backups) > 0
        # Nome deve conter data/hora: backup_YYYYMMDD_HHMMSS.db
        assert "backup_" in backups[0].nome_arquivo
        assert ".db" in backups[0].nome_arquivo

    def test_cliente_nao_pode_criar_backup(self, cliente_autenticado):
        """Cliente não deve poder criar backup"""
        response = cliente_autenticado.post("/admin/backups/criar", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_vendedor_nao_pode_criar_backup(self, vendedor_autenticado):
        """Vendedor não deve poder criar backup"""
        response = vendedor_autenticado.post("/admin/backups/criar", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]


class TestRestaurarBackup:
    """Testes de restauração de backup"""

    def test_restaurar_backup_valido(self, admin_autenticado, criar_backup):
        """Admin deve poder restaurar backup válido"""
        # Criar backup primeiro
        sucesso, mensagem = criar_backup()
        assert sucesso

        # Obter nome do backup criado
        from util import backup_util
        backups = backup_util.listar_backups()
        assert len(backups) > 0
        nome_backup = backups[0].nome_arquivo

        # Restaurar backup
        response = admin_autenticado.post(
            f"/admin/backups/restaurar/{nome_backup}",
            follow_redirects=False
        )

        # Deve redirecionar
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_restaurar_backup_cria_backup_automatico(self, admin_autenticado, criar_backup):
        """Restaurar deve criar backup automático antes"""
        from util import backup_util

        # Criar backup para restaurar
        criar_backup()
        backups_antes = backup_util.listar_backups()
        nome_backup = backups_antes[0].nome_arquivo

        # Restaurar
        admin_autenticado.post(f"/admin/backups/restaurar/{nome_backup}")

        # Deve ter criado um backup adicional (backup de segurança)
        backups_depois = backup_util.listar_backups()
        assert len(backups_depois) >= len(backups_antes)

    def test_restaurar_backup_inexistente(self, admin_autenticado):
        """Deve tratar restauração de backup inexistente"""
        response = admin_autenticado.post(
            "/admin/backups/restaurar/backup_inexistente.db",
            follow_redirects=False
        )

        # Deve redirecionar (com mensagem de erro)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_cliente_nao_pode_restaurar_backup(self, cliente_autenticado, criar_backup):
        """Cliente não deve poder restaurar backup"""
        criar_backup()
        from util import backup_util
        backups = backup_util.listar_backups()

        if len(backups) > 0:
            response = cliente_autenticado.post(
                f"/admin/backups/restaurar/{backups[0].nome_arquivo}",
                follow_redirects=False
            )
            assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]


class TestExcluirBackup:
    """Testes de exclusão de backup"""

    def test_excluir_backup_existente(self, admin_autenticado, criar_backup):
        """Admin deve poder excluir backup"""
        # Criar backup
        criar_backup()

        from util import backup_util
        backups_antes = backup_util.listar_backups()
        assert len(backups_antes) > 0
        nome_backup = backups_antes[0].nome_arquivo

        # Excluir
        response = admin_autenticado.post(
            f"/admin/backups/excluir/{nome_backup}",
            follow_redirects=False
        )

        # Deve redirecionar
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Verificar que foi excluído
        backups_depois = backup_util.listar_backups()
        nomes_depois = [b.nome_arquivo for b in backups_depois]
        assert nome_backup not in nomes_depois

    def test_excluir_backup_inexistente(self, admin_autenticado):
        """Deve tratar exclusão de backup inexistente"""
        response = admin_autenticado.post(
            "/admin/backups/excluir/backup_inexistente.db",
            follow_redirects=False
        )

        # Deve redirecionar (com mensagem de erro)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_cliente_nao_pode_excluir_backup(self, cliente_autenticado, criar_backup):
        """Cliente não deve poder excluir backup"""
        criar_backup()
        from util import backup_util
        backups = backup_util.listar_backups()

        if len(backups) > 0:
            response = cliente_autenticado.post(
                f"/admin/backups/excluir/{backups[0].nome_arquivo}",
                follow_redirects=False
            )
            assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]


class TestDownloadBackup:
    """Testes de download de backup"""

    def test_download_backup_existente(self, admin_autenticado, criar_backup):
        """Admin deve poder fazer download de backup"""
        # Criar backup
        criar_backup()

        from util import backup_util
        backups = backup_util.listar_backups()
        assert len(backups) > 0
        nome_backup = backups[0].nome_arquivo

        # Download
        response = admin_autenticado.get(f"/admin/backups/download/{nome_backup}")

        # Deve retornar arquivo
        assert response.status_code == status.HTTP_200_OK
        assert "application/octet-stream" in response.headers.get("content-type", "")

    def test_download_backup_inexistente(self, admin_autenticado):
        """Deve tratar download de backup inexistente"""
        response = admin_autenticado.get(
            "/admin/backups/download/backup_inexistente.db",
            follow_redirects=False
        )

        # Deve redirecionar ou retornar 404
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_404_NOT_FOUND]

    def test_cliente_nao_pode_baixar_backup(self, cliente_autenticado, criar_backup):
        """Cliente não deve poder baixar backup"""
        criar_backup()
        from util import backup_util
        backups = backup_util.listar_backups()

        if len(backups) > 0:
            response = cliente_autenticado.get(
                f"/admin/backups/download/{backups[0].nome_arquivo}",
                follow_redirects=False
            )
            assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_vendedor_nao_pode_baixar_backup(self, vendedor_autenticado, criar_backup):
        """Vendedor não deve poder baixar backup"""
        criar_backup()
        from util import backup_util
        backups = backup_util.listar_backups()

        if len(backups) > 0:
            response = vendedor_autenticado.get(
                f"/admin/backups/download/{backups[0].nome_arquivo}",
                follow_redirects=False
            )
            assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]


class TestRateLimitBackups:
    """Testes de rate limiting para operações de backup"""

    def test_rate_limit_criar_backup(self, admin_autenticado):
        """Deve bloquear quando rate limit de criar backup é excedido"""
        from unittest.mock import patch

        with patch('routes.admin_backups_routes.admin_backups_limiter.verificar', return_value=False):
            response = admin_autenticado.post("/admin/backups/criar", follow_redirects=True)

            assert response.status_code == status.HTTP_200_OK
            assert "muitas" in response.text.lower() or "aguarde" in response.text.lower()

    def test_rate_limit_restaurar_backup(self, admin_autenticado, criar_backup):
        """Deve bloquear quando rate limit de restaurar backup é excedido"""
        from unittest.mock import patch
        from util import backup_util

        # Criar backup para restaurar
        criar_backup()
        backups = backup_util.listar_backups()
        nome_backup = backups[0].nome_arquivo if backups else "test.db"

        with patch('routes.admin_backups_routes.admin_backups_limiter.verificar', return_value=False):
            response = admin_autenticado.post(
                f"/admin/backups/restaurar/{nome_backup}",
                follow_redirects=True
            )

            assert response.status_code == status.HTTP_200_OK
            assert "muitas" in response.text.lower() or "aguarde" in response.text.lower()

    def test_rate_limit_excluir_backup(self, admin_autenticado, criar_backup):
        """Deve bloquear quando rate limit de excluir backup é excedido"""
        from unittest.mock import patch
        from util import backup_util

        # Criar backup para excluir
        criar_backup()
        backups = backup_util.listar_backups()
        nome_backup = backups[0].nome_arquivo if backups else "test.db"

        with patch('routes.admin_backups_routes.admin_backups_limiter.verificar', return_value=False):
            response = admin_autenticado.post(
                f"/admin/backups/excluir/{nome_backup}",
                follow_redirects=True
            )

            assert response.status_code == status.HTTP_200_OK
            assert "muitas" in response.text.lower() or "aguarde" in response.text.lower()

    def test_rate_limit_download_backup(self, admin_autenticado, criar_backup):
        """Deve bloquear quando rate limit de download é excedido"""
        from unittest.mock import patch
        from util import backup_util

        # Criar backup para download
        criar_backup()
        backups = backup_util.listar_backups()
        nome_backup = backups[0].nome_arquivo if backups else "test.db"

        with patch('routes.admin_backups_routes.backup_download_limiter.verificar', return_value=False):
            response = admin_autenticado.get(
                f"/admin/backups/download/{nome_backup}",
                follow_redirects=True
            )

            assert response.status_code == status.HTTP_200_OK
            assert "muitas" in response.text.lower() or "aguarde" in response.text.lower()


class TestErroCriarBackup:
    """Testes de erro ao criar backup"""

    def test_erro_criar_backup(self, admin_autenticado):
        """Deve mostrar mensagem de erro quando criação falha"""
        from unittest.mock import patch

        with patch('routes.admin_backups_routes.backup_util.criar_backup', return_value=(False, "Erro ao criar backup")):
            response = admin_autenticado.post("/admin/backups/criar", follow_redirects=True)

            assert response.status_code == status.HTTP_200_OK


class TestFluxoCompletoBackup:
    """Testes de fluxo completo de backup"""

    def test_fluxo_criar_listar_restaurar_excluir(self, admin_autenticado):
        """Testar fluxo completo: criar -> listar -> restaurar -> excluir"""
        from util import backup_util

        # 1. Criar backup
        admin_autenticado.post("/admin/backups/criar")

        # 2. Listar e verificar
        backups = backup_util.listar_backups()
        assert len(backups) > 0
        nome_backup = backups[0].nome_arquivo

        # 3. Restaurar
        response_restaurar = admin_autenticado.post(
            f"/admin/backups/restaurar/{nome_backup}",
            follow_redirects=False
        )
        assert response_restaurar.status_code == status.HTTP_303_SEE_OTHER

        # 4. Listar novamente (deve ter backup adicional criado na restauração)
        backups_apos_restaurar = backup_util.listar_backups()
        assert len(backups_apos_restaurar) >= len(backups)

        # 5. Excluir um backup
        if len(backups_apos_restaurar) > 0:
            nome_para_excluir = backups_apos_restaurar[0].nome_arquivo
            response_excluir = admin_autenticado.post(
                f"/admin/backups/excluir/{nome_para_excluir}",
                follow_redirects=False
            )
            assert response_excluir.status_code == status.HTTP_303_SEE_OTHER

    def test_multiplos_backups(self, admin_autenticado):
        """Deve permitir criar múltiplos backups"""
        from util import backup_util
        import time

        # Criar primeiro backup
        admin_autenticado.post("/admin/backups/criar")
        backups_1 = backup_util.listar_backups()

        # Aguardar um pouco para garantir timestamp diferente
        time.sleep(1)

        # Criar segundo backup
        admin_autenticado.post("/admin/backups/criar")
        backups_2 = backup_util.listar_backups()

        # Deve ter mais backups
        assert len(backups_2) > len(backups_1)
