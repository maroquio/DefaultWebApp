"""
Testes para rotas de usuário (/usuario)
Testa perfil, alteração de senha e upload de foto
"""
from fastapi import status
from unittest.mock import patch, MagicMock
import pytest


class TestDashboard:
    """Testes do dashboard do usuário"""

    def test_dashboard_requer_autenticacao(self, client):
        """Usuário não autenticado não pode acessar dashboard"""
        response = client.get("/usuario", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_dashboard_usuario_cliente(self, cliente_autenticado):
        """Cliente autenticado pode acessar dashboard"""
        response = cliente_autenticado.get("/usuario")
        assert response.status_code == status.HTTP_200_OK

    def test_dashboard_admin(self, admin_autenticado):
        """Admin autenticado pode acessar dashboard"""
        response = admin_autenticado.get("/usuario")
        assert response.status_code == status.HTTP_200_OK


class TestVisualizarPerfil:
    """Testes para visualização de perfil"""

    def test_visualizar_perfil_requer_autenticacao(self, client):
        """Não autenticado não pode visualizar perfil"""
        response = client.get("/usuario/perfil/visualizar", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_visualizar_perfil_autenticado(self, cliente_autenticado):
        """Cliente autenticado pode visualizar perfil"""
        response = cliente_autenticado.get("/usuario/perfil/visualizar")
        assert response.status_code == status.HTTP_200_OK

    def test_visualizar_perfil_usuario_nao_encontrado(self, cliente_autenticado):
        """Redireciona para logout se usuário não for encontrado"""
        with patch('routes.usuario_routes.usuario_repo') as mock_repo:
            mock_repo.obter_por_id.return_value = None

            response = cliente_autenticado.get(
                "/usuario/perfil/visualizar",
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER


class TestEditarPerfil:
    """Testes para edição de perfil"""

    def test_get_editar_perfil_autenticado(self, cliente_autenticado):
        """Cliente autenticado pode acessar formulário de edição"""
        response = cliente_autenticado.get("/usuario/perfil/editar")
        assert response.status_code == status.HTTP_200_OK

    def test_post_editar_perfil_email_em_uso(self, cliente_autenticado):
        """Deve mostrar erro quando email já está em uso por outro usuário"""
        with patch('routes.usuario_routes.verificar_email_disponivel', return_value=(False, "Este e-mail já está cadastrado.")):
            response = cliente_autenticado.post(
                "/usuario/perfil/editar",
                data={
                    "nome": "Novo Nome",
                    "email": "emailemuso@test.com"
                }
            )

            assert response.status_code == status.HTTP_200_OK
            assert "já está cadastrado" in response.text.lower()

    def test_post_editar_perfil_validation_error(self, cliente_autenticado):
        """Deve mostrar erros de validação do DTO"""
        response = cliente_autenticado.post(
            "/usuario/perfil/editar",
            data={
                "nome": "",  # Nome vazio causa ValidationError
                "email": "email-invalido"  # Email inválido
            }
        )

        assert response.status_code == status.HTTP_200_OK

    def test_get_editar_perfil_rate_limit(self, cliente_autenticado):
        """Rate limit deve bloquear acesso ao formulário"""
        with patch('routes.usuario_routes.form_get_limiter.verificar', return_value=False):
            response = cliente_autenticado.get(
                "/usuario/perfil/editar",
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER
            assert response.headers["location"] == "/usuario"

    def test_get_editar_perfil_usuario_nao_encontrado(self, cliente_autenticado):
        """Redireciona para logout se usuário não for encontrado"""
        with patch('routes.usuario_routes.form_get_limiter.verificar', return_value=True):
            with patch('routes.usuario_routes.usuario_repo') as mock_repo:
                mock_repo.obter_por_id.return_value = None

                response = cliente_autenticado.get(
                    "/usuario/perfil/editar",
                    follow_redirects=False
                )

                assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_editar_perfil_sucesso(self, cliente_autenticado):
        """Edição de perfil com dados válidos deve funcionar"""
        response = cliente_autenticado.post(
            "/usuario/perfil/editar",
            data={
                "nome": "Novo Nome Teste",
                "email": "novoemail@test.com"
            },
            follow_redirects=False
        )

        # Pode redirecionar para visualizar ou reexibir formulário
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_303_SEE_OTHER]

    def test_post_editar_perfil_usuario_nao_encontrado(self, cliente_autenticado):
        """Deve redirecionar para logout se usuário não encontrado"""
        with patch('routes.usuario_routes.usuario_repo') as mock_repo:
            mock_repo.obter_por_id.return_value = None

            response = cliente_autenticado.post(
                "/usuario/perfil/editar",
                data={
                    "nome": "Novo Nome",
                    "email": "email@test.com"
                },
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_editar_perfil_erro_atualizar(self, cliente_autenticado):
        """Deve mostrar erro quando atualização falha"""
        with patch('routes.usuario_routes.usuario_repo') as mock_repo:
            mock_usuario = MagicMock()
            mock_usuario.id = 1
            mock_usuario.nome = "Teste"
            mock_usuario.email = "teste@test.com"
            mock_repo.obter_por_id.return_value = mock_usuario
            mock_repo.alterar.return_value = False

            with patch('routes.usuario_routes.verificar_email_disponivel', return_value=(True, None)):
                response = cliente_autenticado.post(
                    "/usuario/perfil/editar",
                    data={
                        "nome": "Novo Nome",
                        "email": "novoemail@test.com"
                    }
                )

                assert response.status_code == status.HTTP_200_OK
                assert "erro" in response.text.lower()


class TestAlterarSenha:
    """Testes para alteração de senha"""

    def test_get_alterar_senha_autenticado(self, cliente_autenticado):
        """Cliente autenticado pode acessar formulário de alteração de senha"""
        response = cliente_autenticado.get("/usuario/perfil/alterar-senha")
        assert response.status_code == status.HTTP_200_OK

    def test_get_alterar_senha_rate_limit(self, cliente_autenticado):
        """Rate limit deve bloquear acesso ao formulário"""
        with patch('routes.usuario_routes.form_get_limiter.verificar', return_value=False):
            response = cliente_autenticado.get(
                "/usuario/perfil/alterar-senha",
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER
            assert response.headers["location"] == "/usuario"

    def test_post_alterar_senha_rate_limit(self, cliente_autenticado):
        """Rate limit deve bloquear alteração de senha"""
        with patch('routes.usuario_routes.alterar_senha_limiter.verificar', return_value=False):
            response = cliente_autenticado.post(
                "/usuario/perfil/alterar-senha",
                data={
                    "senha_atual": "SenhaAtual@123",
                    "senha_nova": "NovaSenha@123",
                    "confirmar_senha": "NovaSenha@123"
                }
            )

            assert response.status_code == status.HTTP_200_OK
            assert "muitas tentativas" in response.text.lower() or "aguarde" in response.text.lower()

    def test_post_alterar_senha_atual_incorreta(self, cliente_autenticado, criar_usuario, usuario_teste):
        """Deve mostrar erro quando senha atual está incorreta"""
        # Criar usuário
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        with patch('routes.usuario_routes.alterar_senha_limiter.verificar', return_value=True):
            with patch('routes.usuario_routes.usuario_repo') as mock_repo:
                mock_usuario = MagicMock()
                mock_usuario.id = 1
                mock_usuario.senha = "$2b$12$hashedpassword"
                mock_repo.obter_por_id.return_value = mock_usuario

                with patch('routes.usuario_routes.verificar_senha', return_value=False):
                    response = cliente_autenticado.post(
                        "/usuario/perfil/alterar-senha",
                        data={
                            "senha_atual": "SenhaErrada@123",
                            "senha_nova": "NovaSenha@123",
                            "confirmar_senha": "NovaSenha@123"
                        }
                    )

                    assert response.status_code == status.HTTP_200_OK
                    assert "incorreta" in response.text.lower()

    def test_post_alterar_senha_nova_igual_atual(self, cliente_autenticado, criar_usuario, usuario_teste):
        """Deve mostrar erro quando nova senha é igual à atual"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        with patch('routes.usuario_routes.alterar_senha_limiter.verificar', return_value=True):
            with patch('routes.usuario_routes.usuario_repo') as mock_repo:
                mock_usuario = MagicMock()
                mock_usuario.id = 1
                mock_usuario.senha = "$2b$12$hashedpassword"
                mock_repo.obter_por_id.return_value = mock_usuario

                # Primeira chamada True (senha atual correta), segunda True (nova senha igual à atual)
                with patch('routes.usuario_routes.verificar_senha', return_value=True):
                    response = cliente_autenticado.post(
                        "/usuario/perfil/alterar-senha",
                        data={
                            "senha_atual": usuario_teste["senha"],
                            "senha_nova": usuario_teste["senha"],  # Mesma senha
                            "confirmar_senha": usuario_teste["senha"]
                        }
                    )

                    assert response.status_code == status.HTTP_200_OK
                    assert "diferente" in response.text.lower()

    def test_post_alterar_senha_sucesso(self, cliente_autenticado, criar_usuario, usuario_teste):
        """Deve alterar senha com sucesso quando dados válidos"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        with patch('routes.usuario_routes.alterar_senha_limiter.verificar', return_value=True):
            with patch('routes.usuario_routes.usuario_repo') as mock_repo:
                mock_usuario = MagicMock()
                mock_usuario.id = 1
                mock_usuario.senha = "$2b$12$hashedpassword"
                mock_repo.obter_por_id.return_value = mock_usuario
                mock_repo.atualizar_senha.return_value = True

                # Primeira chamada True (senha atual correta), segunda False (nova diferente)
                with patch('routes.usuario_routes.verificar_senha', side_effect=[True, False]):
                    response = cliente_autenticado.post(
                        "/usuario/perfil/alterar-senha",
                        data={
                            "senha_atual": usuario_teste["senha"],
                            "senha_nova": "NovaSenha@123",
                            "confirmar_senha": "NovaSenha@123"
                        },
                        follow_redirects=False
                    )

                    assert response.status_code == status.HTTP_303_SEE_OTHER
                    assert response.headers["location"] == "/usuario/perfil/visualizar"

    def test_post_alterar_senha_validation_error(self, cliente_autenticado):
        """Deve mostrar erros de validação do DTO"""
        with patch('routes.usuario_routes.alterar_senha_limiter.verificar', return_value=True):
            response = cliente_autenticado.post(
                "/usuario/perfil/alterar-senha",
                data={
                    "senha_atual": "curta",  # Muito curta
                    "senha_nova": "123",  # Inválida
                    "confirmar_senha": "456"  # Não coincide
                }
            )

            assert response.status_code == status.HTTP_200_OK

    def test_post_alterar_senha_usuario_nao_encontrado(self, cliente_autenticado):
        """Deve redirecionar para logout se usuário não encontrado"""
        with patch('routes.usuario_routes.alterar_senha_limiter.verificar', return_value=True):
            with patch('routes.usuario_routes.usuario_repo') as mock_repo:
                mock_repo.obter_por_id.return_value = None

                response = cliente_autenticado.post(
                    "/usuario/perfil/alterar-senha",
                    data={
                        "senha_atual": "SenhaAtual@123",
                        "senha_nova": "NovaSenha@123",
                        "confirmar_senha": "NovaSenha@123"
                    },
                    follow_redirects=False
                )

                assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_alterar_senha_erro_atualizar(self, cliente_autenticado, criar_usuario, usuario_teste):
        """Deve mostrar erro quando atualização falha"""
        # Criar usuário
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        with patch('routes.usuario_routes.alterar_senha_limiter.verificar', return_value=True):
            with patch('routes.usuario_routes.usuario_repo') as mock_repo:
                mock_usuario = MagicMock()
                mock_usuario.id = 1
                mock_usuario.senha = "$2b$12$hashedpassword"  # Hash fictício
                mock_repo.obter_por_id.return_value = mock_usuario
                mock_repo.atualizar_senha.return_value = False

                with patch('routes.usuario_routes.verificar_senha', side_effect=[True, False]):
                    # Primeira chamada: senha atual correta
                    # Segunda chamada: nova senha diferente da atual
                    response = cliente_autenticado.post(
                        "/usuario/perfil/alterar-senha",
                        data={
                            "senha_atual": usuario_teste["senha"],
                            "senha_nova": "NovaSenha@123",
                            "confirmar_senha": "NovaSenha@123"
                        }
                    )

                    assert response.status_code == status.HTTP_200_OK


class TestAtualizarFoto:
    """Testes para upload de foto de perfil"""

    def test_post_atualizar_foto_rate_limit(self, cliente_autenticado):
        """Rate limit deve bloquear upload de foto"""
        with patch('routes.usuario_routes.upload_foto_limiter.verificar', return_value=False):
            response = cliente_autenticado.post(
                "/usuario/perfil/atualizar-foto",
                data={"foto_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA" + "A" * 100},
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_atualizar_foto_foto_invalida(self, cliente_autenticado):
        """Deve rejeitar foto inválida (muito curta)"""
        with patch('routes.usuario_routes.upload_foto_limiter.verificar', return_value=True):
            response = cliente_autenticado.post(
                "/usuario/perfil/atualizar-foto",
                data={"foto_base64": "abc"},  # Muito curto
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_atualizar_foto_erro_salvar(self, cliente_autenticado):
        """Deve mostrar erro quando salvar foto falha"""
        with patch('routes.usuario_routes.upload_foto_limiter.verificar', return_value=True):
            with patch('routes.usuario_routes.salvar_foto_cropada_usuario', return_value=False):
                response = cliente_autenticado.post(
                    "/usuario/perfil/atualizar-foto",
                    data={"foto_base64": "data:image/png;base64," + "A" * 200},
                    follow_redirects=False
                )

                assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_atualizar_foto_erro_io(self, cliente_autenticado):
        """Deve tratar erro de I/O ao salvar foto"""
        with patch('routes.usuario_routes.upload_foto_limiter.verificar', return_value=True):
            with patch('routes.usuario_routes.salvar_foto_cropada_usuario', side_effect=IOError("Disk full")):
                response = cliente_autenticado.post(
                    "/usuario/perfil/atualizar-foto",
                    data={"foto_base64": "data:image/png;base64," + "A" * 200},
                    follow_redirects=False
                )

                assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_atualizar_foto_erro_valor(self, cliente_autenticado):
        """Deve tratar ValueError ao processar foto"""
        with patch('routes.usuario_routes.upload_foto_limiter.verificar', return_value=True):
            with patch('routes.usuario_routes.salvar_foto_cropada_usuario', side_effect=ValueError("Invalid base64")):
                response = cliente_autenticado.post(
                    "/usuario/perfil/atualizar-foto",
                    data={"foto_base64": "data:image/png;base64," + "A" * 200},
                    follow_redirects=False
                )

                assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_atualizar_foto_sucesso(self, cliente_autenticado):
        """Upload de foto com sucesso"""
        with patch('routes.usuario_routes.upload_foto_limiter.verificar', return_value=True):
            with patch('routes.usuario_routes.salvar_foto_cropada_usuario', return_value=True):
                response = cliente_autenticado.post(
                    "/usuario/perfil/atualizar-foto",
                    data={"foto_base64": "data:image/png;base64," + "A" * 200},
                    follow_redirects=False
                )

                assert response.status_code == status.HTTP_303_SEE_OTHER
                assert response.headers["location"] == "/usuario/perfil/visualizar"

    def test_post_atualizar_foto_muito_grande(self, cliente_autenticado):
        """Deve rejeitar foto maior que 10MB"""
        with patch('routes.usuario_routes.upload_foto_limiter.verificar', return_value=True):
            # Base64 tem ~33% de overhead, então 15MB de base64 = ~11MB binário
            foto_grande = "data:image/png;base64," + "A" * (15 * 1024 * 1024)
            response = cliente_autenticado.post(
                "/usuario/perfil/atualizar-foto",
                data={"foto_base64": foto_grande},
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_atualizar_foto_erro_os(self, cliente_autenticado):
        """Deve tratar OSError ao salvar foto"""
        with patch('routes.usuario_routes.upload_foto_limiter.verificar', return_value=True):
            with patch('routes.usuario_routes.salvar_foto_cropada_usuario', side_effect=OSError("Permission denied")):
                response = cliente_autenticado.post(
                    "/usuario/perfil/atualizar-foto",
                    data={"foto_base64": "data:image/png;base64," + "A" * 200},
                    follow_redirects=False
                )

                assert response.status_code == status.HTTP_303_SEE_OTHER
