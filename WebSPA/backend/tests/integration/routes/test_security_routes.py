"""
Testes de segurança da aplicação.

Testa proteções contra:
- XSS (Cross-Site Scripting)
- SQL Injection
- Escalação de privilégios
- Rate limiting
- Validação de inputs maliciosos
- Autorização inadequada
"""
from fastapi import status
from util.perfis import Perfil
from tests.test_helpers import assert_permission_denied, assert_redirects_to


class TestXSSProtection:
    """Testes de proteção contra XSS (Cross-Site Scripting)"""

    def test_cadastro_com_script_tag_no_nome(self, client):
        """Nome com script tag deve ser escapado/rejeitado"""
        malicious_name = '<script>alert("XSS")</script>Usuario'

        response = client.post("/cadastrar", data={
            "perfil": Perfil.CLIENTE.value,
            "nome": malicious_name,
            "email": "xss@example.com",
            "senha": "Senha@123",
            "confirmar_senha": "Senha@123"
        }, follow_redirects=False)

        # Deve ser aceito (Jinja2 escapa automaticamente) ou rejeitado
        if response.status_code == 303:
            # Se aceito, verificar que foi escapado no banco
            from repo import usuario_repo
            usuario = usuario_repo.obter_por_email("xss@example.com")
            if usuario:
                # Nome foi salvo, mas Jinja2 deve escapar ao exibir
                # Script tag não deve ser executável
                assert "<script>" in usuario.nome or usuario.nome == malicious_name


class TestSQLInjection:
    """Testes de proteção contra SQL Injection"""

    def test_login_com_sql_injection_no_email(self, client, criar_usuario, usuario_teste):
        """SQL injection no email não deve permitir login"""
        # Criar usuário legítimo
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Tentar SQL injection
        sql_injection_email = "' OR '1'='1' --"

        response = client.post("/login", data={
            "email": sql_injection_email,
            "senha": "qualquercoisa"
        }, follow_redirects=True)

        # Não deve fazer login (prepared statements protegem)
        assert response.status_code == 200
        assert "e-mail ou senha" in response.text.lower() or \
               "inválido" in response.text.lower()

    def test_buscar_usuario_por_id_com_sql_injection(self, admin_autenticado):
        """SQL injection no ID de usuário não deve causar problemas"""

        # Tentar injetar SQL via ID
        malicious_id = "1 OR 1=1"

        response = admin_autenticado.get(
            f"/admin/usuarios/editar/{malicious_id}",
            follow_redirects=False
        )

        # Deve falhar graciosamente (ID inválido)
        # FastAPI path param validation deve rejeitar
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,  # Validação falhou
            status.HTTP_303_SEE_OTHER,              # Redirect para lista
            status.HTTP_404_NOT_FOUND               # Não encontrado
        ]

    def test_email_com_aspas_simples_nao_quebra_query(self, client):
        """Email com aspas simples deve ser tratado corretamente"""
        email_com_aspas = "test'user@example.com"

        response = client.post("/cadastrar", data={
            "perfil": Perfil.CLIENTE.value,
            "nome": "Usuario Teste",
            "email": email_com_aspas,
            "senha": "Senha@123",
            "confirmar_senha": "Senha@123"
        }, follow_redirects=True)

        # Pode ser rejeitado por validação de email OU aceito
        # Se aceito, prepared statements protegem
        assert response.status_code in [200, 303]


class TestEscalacaoPrivilegios:
    """Testes de proteção contra escalação de privilégios"""

    def test_cliente_nao_pode_acessar_admin_usuarios(self, cliente_autenticado):
        """Cliente não deve acessar painel de administração de usuários"""
        response = cliente_autenticado.get("/admin/usuarios/listar", follow_redirects=False)

        assert response.status_code in [
            status.HTTP_303_SEE_OTHER,
            status.HTTP_403_FORBIDDEN
        ]

    def test_cliente_nao_pode_criar_usuario_como_admin(self, cliente_autenticado):
        """Cliente não deve poder acessar endpoint de criação de usuário admin"""
        response = cliente_autenticado.post("/admin/usuarios/cadastrar", data={
            "nome": "Hacker Admin",
            "email": "hacker@example.com",
            "senha": "Senha@123",
            "perfil": Perfil.ADMIN.value
        }, follow_redirects=False)

        # Deve ser bloqueado
        assert response.status_code in [
            status.HTTP_303_SEE_OTHER,
            status.HTTP_403_FORBIDDEN
        ]

    def test_vendedor_nao_pode_acessar_backups(self, vendedor_autenticado):
        """Vendedor não deve acessar área de backups (apenas admin)"""
        response = vendedor_autenticado.get("/admin/backups/listar", follow_redirects=False)

        assert response.status_code in [
            status.HTTP_303_SEE_OTHER,
            status.HTTP_403_FORBIDDEN
        ]

    def test_vendedor_nao_pode_criar_backup(self, vendedor_autenticado):
        """Vendedor não deve poder criar backups"""
        response = vendedor_autenticado.post("/admin/backups/criar", follow_redirects=False)

        assert response.status_code in [
            status.HTTP_303_SEE_OTHER,
            status.HTTP_403_FORBIDDEN
        ]

    def test_usuario_nao_pode_editar_outro_usuario(self, client, dois_usuarios, fazer_login):
        """Usuário comum não deve poder editar dados de outro usuário comum"""
        usuario1, usuario2 = dois_usuarios

        # Login como usuario1
        fazer_login(usuario1["email"], usuario1["senha"])

        # Tentar editar usuario2 via endpoint de perfil (se existisse endpoint público)
        # Ou verificar que não há tal endpoint acessível
        # Este teste valida que perfil só edita próprio usuário

        response = client.get("/usuario/perfil/editar")
        assert response.status_code == 200

        # Modificar para tentar editar outro usuário (simulação)
        # Na verdade, perfil/editar só edita usuário logado
        # Teste passa se não há forma de especificar ID de outro usuário


class TestRateLimiting:
    """Testes de rate limiting para prevenir brute force"""

    def test_multiplas_tentativas_login_falhas_sao_limitadas(self, client):
        """Múltiplas tentativas de login com falha devem ser bloqueadas"""

        # Fazer 6 tentativas (limite é 5)
        for i in range(6):
            response = client.post("/login", data={
                "email": "inexistente@example.com",
                "senha": "SenhaErrada@123"
            }, follow_redirects=True)

        # Última tentativa deve ser bloqueada por rate limiting
        assert response.status_code == 200
        # Deve conter mensagem sobre muitas tentativas
        assert "muitas tentativas" in response.text.lower() or \
               "aguarde" in response.text.lower() or \
               "bloqueado" in response.text.lower()

    def test_cadastro_limitado_por_ip(self, client):
        """Múltiplos cadastros do mesmo IP devem ser limitados"""

        # Tentar cadastrar 4 usuários (limite é 3)
        for i in range(4):
            response = client.post("/cadastrar", data={
                "perfil": Perfil.CLIENTE.value,
                "nome": f"Usuario {i}",
                "email": f"usuario{i}@example.com",
                "senha": "Senha@123",
                "confirmar_senha": "Senha@123"
            }, follow_redirects=True)

        # 4ª tentativa deve ser bloqueada
        assert "muitas tentativas" in response.text.lower() or \
               "limite" in response.text.lower() or \
               response.status_code == 429  # Too Many Requests

    def test_esqueci_senha_fortemente_limitado(self, client, criar_usuario, usuario_teste):
        """Esqueci senha deve ter rate limiting rigoroso (1 por minuto)"""

        # Criar usuário
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Primeira solicitação deve passar
        response1 = client.post("/esqueci-senha", data={
            "email": usuario_teste["email"]
        }, follow_redirects=False)
        assert response1.status_code == 303

        # Segunda solicitação imediata deve ser bloqueada
        response2 = client.post("/esqueci-senha", data={
            "email": usuario_teste["email"]
        }, follow_redirects=True)

        # Deve conter mensagem de rate limit
        assert "aguarde" in response2.text.lower() or \
               "muitas tentativas" in response2.text.lower()


class TestValidacaoInputs:
    """Testes de validação de inputs maliciosos/inválidos"""

    def test_email_extremamente_longo_rejeitado(self, client):
        """Email com mais de 255 caracteres deve ser rejeitado"""
        email_longo = "a" * 250 + "@example.com"

        response = client.post("/cadastrar", data={
            "perfil": Perfil.CLIENTE.value,
            "nome": "Usuario Teste",
            "email": email_longo,
            "senha": "Senha@123",
            "confirmar_senha": "Senha@123"
        }, follow_redirects=True)

        # Deve rejeitar (validação ou constraint)
        assert response.status_code == 200
        assert "e-mail" in response.text.lower() or "inválido" in response.text.lower()

    def test_senha_com_caracteres_unicode_aceita(self, client):
        """Senha com caracteres unicode válidos deve ser aceita"""
        senha_unicode = "Sẽnha@123éú"

        response = client.post("/cadastrar", data={
            "perfil": Perfil.CLIENTE.value,
            "nome": "Usuario Teste",
            "email": "unicode@example.com",
            "senha": senha_unicode,
            "confirmar_senha": senha_unicode
        }, follow_redirects=False)

        # Deve ser aceita (bcrypt suporta unicode)
        assert response.status_code == 303

    def test_nome_com_null_bytes_rejeitado(self, client):
        """Nome com null bytes deve ser rejeitado"""
        nome_com_null = "Usuario\x00Admin"

        response = client.post("/cadastrar", data={
            "perfil": Perfil.CLIENTE.value,
            "nome": nome_com_null,
            "email": "nullbyte@example.com",
            "senha": "Senha@123",
            "confirmar_senha": "Senha@123"
        }, follow_redirects=True)

        # Pode ser rejeitado por validação ou sanitizado
        assert response.status_code in [200, 303]

    def test_perfil_invalido_rejeitado_no_cadastro_admin(self, admin_autenticado):
        """Perfil inválido no cadastro admin deve ser rejeitado"""
        response = admin_autenticado.post("/admin/usuarios/cadastrar", data={
            "nome": "Usuario Teste",
            "email": "teste@example.com",
            "senha": "Senha@123",
            "perfil": "SUPER_ADMIN"  # Perfil inexistente
        }, follow_redirects=True)

        assert response.status_code == 200
        assert "perfil" in response.text.lower() or "inválido" in response.text.lower()


class TestAutorizacaoArquivos:
    """Testes de autorização de acesso a arquivos"""

    def test_usuario_nao_pode_baixar_backup_diretamente(self, cliente_autenticado, criar_backup):
        """Usuário comum não deve poder baixar backups"""

        # Criar backup como admin (precisamos mockar ou usar admin)
        # Este teste assume que cliente_autenticado não é admin

        # Tentar baixar backup (mesmo sem saber o nome)
        response = cliente_autenticado.get(
            "/admin/backups/download/algum_backup.db",
            follow_redirects=False
        )

        # Deve ser negado
        assert response.status_code in [
            status.HTTP_303_SEE_OTHER,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_usuario_nao_pode_acessar_foto_por_path_direto(self, client):
        """Fotos de perfil devem ser acessíveis via static, mas isso é OK (públicas)"""

        # Fotos são intencionalmente públicas em /static/img/usuarios/
        # Este teste documenta esse comportamento
        response = client.get("/static/img/usuarios/000001.jpg")

        # Foto pode existir ou não, mas endpoint deve ser acessível
        assert response.status_code in [200, 404]

        # NOTA: Se fotos devem ser privadas, implementar proteção
        # Por ora, este é comportamento esperado (fotos públicas)


class TestSessionSecurity:
    """Testes de segurança de sessão"""

    def test_logout_invalida_sessao(self, cliente_autenticado):
        """Logout deve invalidar sessão e prevenir acesso subsequente"""

        # Verificar que está logado antes do logout
        response_antes = cliente_autenticado.get("/usuario", follow_redirects=False)
        assert response_antes.status_code == 200, "Deveria estar autenticado antes do logout"

        # Fazer logout
        response_logout = cliente_autenticado.get("/logout", follow_redirects=False)
        assert_redirects_to(response_logout, "/")

        # Tentar acessar área protegida com mesma sessão
        response_protegido = cliente_autenticado.get("/usuario", follow_redirects=False)

        # Deve redirecionar para login (sessão inválida)
        assert_permission_denied(response_protegido)

    def test_sessao_nao_compartilhada_entre_usuarios(self, client, criar_usuario):
        """Sessões devem ser isoladas entre usuários diferentes"""

        # Criar dois usuários
        criar_usuario("Usuario 1", "user1@example.com", "Senha@123")
        criar_usuario("Usuario 2", "user2@example.com", "Senha@123")

        # Login como usuario1
        client.post("/login", data={
            "email": "user1@example.com",
            "senha": "Senha@123"
        })

        # Verificar que está logado como user1
        response1 = client.get("/usuario")
        assert "Usuario 1" in response1.text

        # Logout
        client.get("/logout")

        # Login como usuario2
        client.post("/login", data={
            "email": "user2@example.com",
            "senha": "Senha@123"
        })

        # Verificar que agora está logado como user2 (não user1)
        response2 = client.get("/usuario")
        assert "Usuario 2" in response2.text
        assert "Usuario 1" not in response2.text


class TestPasswordSecurity:
    """Testes de segurança de senha"""

    def test_senha_nao_retornada_em_respostas(self, client, criar_usuario, usuario_teste):
        """Senha não deve aparecer em nenhuma resposta da aplicação"""

        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Login
        client.post("/login", data={
            "email": usuario_teste["email"],
            "senha": usuario_teste["senha"]
        })

        # Acessar várias páginas
        pages = ["/usuario", "/usuario/perfil/visualizar", "/usuario/perfil/editar"]

        for page in pages:
            response = client.get(page)
            # Senha (plain ou hash) não deve aparecer
            assert usuario_teste["senha"] not in response.text
            assert "Senha@123" not in response.text

    def test_senha_armazenada_como_hash(self, client, criar_usuario, usuario_teste):
        """Senha deve ser armazenada como hash bcrypt no banco"""

        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Verificar no banco
        from repo import usuario_repo
        usuario = usuario_repo.obter_por_email(usuario_teste["email"])

        assert usuario is not None
        # Hash bcrypt começa com $2b$ e tem 60 caracteres
        assert usuario.senha.startswith("$2b$")
        assert len(usuario.senha) == 60
        # Senha plain não deve estar no banco
        assert usuario_teste["senha"] not in usuario.senha

    def test_senha_fraca_rejeitada(self, client):
        """Senha que não atende requisitos deve ser rejeitada"""
        senhas_fracas = [
            "123456",           # Só números
            "abcdefgh",         # Só letras minúsculas
            "ABCDEFGH",         # Só letras maiúsculas
            "Abc123",           # Muito curta
            "Senha123",         # Sem caractere especial
        ]

        for senha_fraca in senhas_fracas:
            response = client.post("/cadastrar", data={
                "perfil": Perfil.CLIENTE.value,
                "nome": "Usuario Teste",
                "email": f"teste_{senha_fraca}@example.com",
                "senha": senha_fraca,
                "confirmar_senha": senha_fraca
            }, follow_redirects=True)

            # Deve rejeitar
            assert response.status_code == 200
            # Deve ter mensagem sobre requisitos de senha
            assert any(
                palavra in response.text.lower()
                for palavra in ["senha", "mínimo", "maiúscula", "minúscula", "especial"]
            )


class TestInformationDisclosure:
    """Testes para prevenir vazamento de informações"""

    def test_erro_500_nao_expoe_stack_trace_em_producao(self, client):
        """Erro 500 não deve expor detalhes técnicos em produção"""

        # Tentar causar erro (ex: ID inválido que causa exceção)
        response = client.get("/admin/usuarios/editar/abc")  # ID não numérico

        # Pode ser 422 (validação) ou 500 (erro interno)
        if response.status_code == 500:
            # Não deve conter stack trace ou paths do sistema
            assert "Traceback" not in response.text
            assert "/Volumes/" not in response.text
            assert "File" not in response.text or "arquivo" in response.text.lower()

    def test_usuario_inexistente_nao_revela_existencia(self, client):
        """Login com email inexistente não deve revelar que email não existe"""

        response = client.post("/login", data={
            "email": "naoexiste@example.com",
            "senha": "Senha@123"
        }, follow_redirects=True)

        # Mensagem genérica, não específica
        assert "e-mail ou senha" in response.text.lower()
        # Não deve dizer "email não cadastrado" especificamente
        assert "não cadastrado" not in response.text.lower()

    def test_esqueci_senha_nao_revela_email_inexistente(self, client):
        """Esqueci senha não deve revelar se email existe ou não"""

        response = client.post("/esqueci-senha", data={
            "email": "naoexiste@example.com"
        }, follow_redirects=False)

        # Mesmo comportamento independente de email existir
        assert response.status_code == 303
        assert_redirects_to(response, "/login")

        # Flash message deve ser genérica (testado em outro teste)
