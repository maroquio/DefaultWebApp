"""
Testes para as rotas de chat (routes/chat_routes.py).

Testa todos os endpoints de chat incluindo criação de salas,
envio de mensagens, listagem e busca de usuários.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestChatRoutes:
    """Testes para rotas de chat"""

    @pytest.fixture
    def usuarios_chat(self, client, fazer_login, criar_usuario_direto):
        """Fixture que cria dois usuários e loga o primeiro"""
        # Criar usuário 1 e logar
        usuario1_id = criar_usuario_direto(
            nome="Usuario Chat 1",
            email="chat1@teste.com",
            senha="Teste@123",
            perfil="Cliente"
        )
        fazer_login("chat1@teste.com", "Teste@123")

        # Criar usuário 2 (destino)
        usuario2_id = criar_usuario_direto(
            nome="Usuario Chat 2",
            email="chat2@teste.com",
            senha="Teste@123",
            perfil="Cliente"
        )

        return {
            "client": client,
            "usuario1_id": usuario1_id,
            "outro_usuario_id": usuario2_id
        }

    # =========================================================================
    # Testes de Health Check
    # =========================================================================

    def test_health_check(self, client):
        """Health check do chat deve retornar status healthy"""
        response = client.get("/chat/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "conexoes_ativas" in data
        assert "timestamp" in data

    # =========================================================================
    # Testes de Criação de Sala
    # =========================================================================

    def test_criar_sala_requer_autenticacao(self, client):
        """Criar sala deve requerer autenticação"""
        response = client.post("/chat/salas", data={"outro_usuario_id": 1}, follow_redirects=False)

        # Sem autenticação, deve redirecionar para login
        assert response.status_code == 303

    def test_criar_sala_sucesso(self, usuarios_chat):
        """Deve criar sala entre dois usuários"""
        client = usuarios_chat["client"]
        outro_id = usuarios_chat["outro_usuario_id"]

        response = client.post("/chat/salas", data={"outro_usuario_id": outro_id})

        assert response.status_code == 200
        data = response.json()
        assert "sala_id" in data

    def test_criar_sala_consigo_mesmo_falha(self, client, fazer_login, criar_usuario_direto):
        """Não pode criar sala consigo mesmo"""
        usuario_id = criar_usuario_direto(
            nome="Solo User",
            email="solo@teste.com",
            senha="Teste@123"
        )
        fazer_login("solo@teste.com", "Teste@123")

        response = client.post("/chat/salas", data={"outro_usuario_id": usuario_id}, follow_redirects=False)

        # Deve retornar erro 400 ou redirecionar (303)
        assert response.status_code in [303, 400]

    def test_criar_sala_usuario_inexistente(self, client, fazer_login, criar_usuario_direto):
        """Não pode criar sala com usuário inexistente"""
        criar_usuario_direto(
            nome="User Criar",
            email="criar@teste.com",
            senha="Teste@123"
        )
        fazer_login("criar@teste.com", "Teste@123")

        response = client.post("/chat/salas", data={"outro_usuario_id": 99999}, follow_redirects=False)

        # Deve retornar 404 ou redirecionar (303)
        assert response.status_code in [303, 404]

    # =========================================================================
    # Testes de Listagem de Conversas
    # =========================================================================

    def test_listar_conversas_requer_autenticacao(self, client):
        """Listar conversas deve requerer autenticação"""
        response = client.get("/chat/conversas", follow_redirects=False)

        assert response.status_code == 303

    def test_listar_conversas_retorna_lista(self, usuarios_chat):
        """Deve retornar lista de conversas"""
        client = usuarios_chat["client"]
        outro_id = usuarios_chat["outro_usuario_id"]

        # Criar sala primeiro
        client.post("/chat/salas", data={"outro_usuario_id": outro_id})

        response = client.get("/chat/conversas")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_listar_conversas_com_paginacao(self, usuarios_chat):
        """Deve respeitar parâmetros de paginação"""
        client = usuarios_chat["client"]

        response = client.get("/chat/conversas?limit=5&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    # =========================================================================
    # Testes de Listagem de Mensagens
    # =========================================================================

    def test_listar_mensagens_requer_autenticacao(self, client):
        """Listar mensagens deve requerer autenticação"""
        response = client.get("/chat/mensagens/1_2", follow_redirects=False)

        assert response.status_code == 303

    def test_listar_mensagens_sala_nao_participante(self, client, fazer_login, criar_usuario_direto):
        """Não pode listar mensagens de sala que não participa"""
        criar_usuario_direto(
            nome="Intruso",
            email="intruso@teste.com",
            senha="Teste@123"
        )
        fazer_login("intruso@teste.com", "Teste@123")

        response = client.get("/chat/mensagens/outra_sala", follow_redirects=False)

        # Deve retornar 403 ou redirecionar (303)
        assert response.status_code in [303, 403]

    def test_listar_mensagens_sala_participante(self, usuarios_chat):
        """Deve listar mensagens de sala que participa"""
        client = usuarios_chat["client"]
        outro_id = usuarios_chat["outro_usuario_id"]

        # Criar sala
        resp = client.post("/chat/salas", data={"outro_usuario_id": outro_id})
        sala_id = resp.json()["sala_id"]

        # Listar mensagens
        response = client.get(f"/chat/mensagens/{sala_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    # =========================================================================
    # Testes de Envio de Mensagem
    # =========================================================================

    def test_enviar_mensagem_requer_autenticacao(self, client):
        """Enviar mensagem deve requerer autenticação"""
        response = client.post(
            "/chat/mensagens",
            data={"sala_id": "1_2", "mensagem": "teste"},
            follow_redirects=False
        )

        assert response.status_code == 303

    def test_enviar_mensagem_sala_nao_participante(self, client, fazer_login, criar_usuario_direto):
        """Não pode enviar mensagem em sala que não participa"""
        criar_usuario_direto(
            nome="Sender Intruso",
            email="sender_intruso@teste.com",
            senha="Teste@123"
        )
        fazer_login("sender_intruso@teste.com", "Teste@123")

        response = client.post(
            "/chat/mensagens",
            data={"sala_id": "outra_sala", "mensagem": "teste"},
            follow_redirects=False
        )

        # Deve retornar 403 ou redirecionar (303)
        assert response.status_code in [303, 403]

    def test_enviar_mensagem_sucesso(self, usuarios_chat):
        """Deve enviar mensagem com sucesso"""
        client = usuarios_chat["client"]
        outro_id = usuarios_chat["outro_usuario_id"]

        # Criar sala
        resp = client.post("/chat/salas", data={"outro_usuario_id": outro_id})
        sala_id = resp.json()["sala_id"]

        # Enviar mensagem
        response = client.post(
            "/chat/mensagens",
            data={"sala_id": sala_id, "mensagem": "Olá, tudo bem?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mensagem"] == "Olá, tudo bem?"
        assert data["sala_id"] == sala_id

    def test_enviar_mensagem_sala_inexistente(self, client, fazer_login, criar_usuario_direto):
        """Não pode enviar mensagem em sala inexistente"""
        criar_usuario_direto(
            nome="Sender Sem Sala",
            email="sender_sem_sala@teste.com",
            senha="Teste@123"
        )
        fazer_login("sender_sem_sala@teste.com", "Teste@123")

        response = client.post(
            "/chat/mensagens",
            data={"sala_id": "sala_que_nao_existe", "mensagem": "teste"},
            follow_redirects=False
        )

        # Deve retornar 403/404 ou redirecionar (303)
        assert response.status_code in [303, 403, 404]

    # =========================================================================
    # Testes de Marcar como Lidas
    # =========================================================================

    def test_marcar_lidas_requer_autenticacao(self, client):
        """Marcar como lidas deve requerer autenticação"""
        response = client.post("/chat/mensagens/lidas/1_2", follow_redirects=False)

        assert response.status_code == 303

    def test_marcar_lidas_sala_nao_participante(self, client, fazer_login, criar_usuario_direto):
        """Não pode marcar como lidas em sala que não participa"""
        criar_usuario_direto(
            nome="Reader Intruso",
            email="reader_intruso@teste.com",
            senha="Teste@123"
        )
        fazer_login("reader_intruso@teste.com", "Teste@123")

        response = client.post("/chat/mensagens/lidas/outra_sala", follow_redirects=False)

        # Deve retornar 403 ou redirecionar (303)
        assert response.status_code in [303, 403]

    def test_marcar_lidas_sucesso(self, usuarios_chat):
        """Deve marcar mensagens como lidas"""
        client = usuarios_chat["client"]
        outro_id = usuarios_chat["outro_usuario_id"]

        # Criar sala
        resp = client.post("/chat/salas", data={"outro_usuario_id": outro_id})
        sala_id = resp.json()["sala_id"]

        # Marcar como lidas
        response = client.post(f"/chat/mensagens/lidas/{sala_id}")

        assert response.status_code == 200
        assert response.json()["sucesso"] is True

    # =========================================================================
    # Testes de Busca de Usuários
    # =========================================================================

    def test_buscar_usuarios_requer_autenticacao(self, client):
        """Buscar usuários deve requerer autenticação"""
        response = client.get("/chat/usuarios/buscar?q=teste", follow_redirects=False)

        assert response.status_code == 303

    def test_buscar_usuarios_termo_curto(self, client, fazer_login, criar_usuario_direto):
        """Termo muito curto deve retornar lista vazia"""
        criar_usuario_direto(
            nome="Buscador",
            email="buscador@teste.com",
            senha="Teste@123"
        )
        fazer_login("buscador@teste.com", "Teste@123")

        response = client.get("/chat/usuarios/buscar?q=a")

        assert response.status_code == 200
        assert response.json() == []

    def test_buscar_usuarios_retorna_lista(self, client, fazer_login, criar_usuario_direto):
        """Deve retornar lista de usuários encontrados"""
        # Criar vários usuários
        criar_usuario_direto(
            nome="Pessoa Busca 1",
            email="pessoa1@teste.com",
            senha="Teste@123"
        )
        criar_usuario_direto(
            nome="Pessoa Busca 2",
            email="pessoa2@teste.com",
            senha="Teste@123"
        )

        # Criar e logar buscador
        criar_usuario_direto(
            nome="Buscador Teste",
            email="buscador_t@teste.com",
            senha="Teste@123"
        )
        fazer_login("buscador_t@teste.com", "Teste@123")

        response = client.get("/chat/usuarios/buscar?q=pessoa")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_buscar_usuarios_exclui_admin(self, client, admin_autenticado):
        """Busca deve excluir administradores"""
        response = admin_autenticado.get("/chat/usuarios/buscar?q=admin")

        assert response.status_code == 200
        data = response.json()
        # Admins não devem aparecer nos resultados
        for usuario in data:
            assert usuario.get("perfil") != "Administrador"

    # =========================================================================
    # Testes de Contagem de Não Lidas
    # =========================================================================

    def test_contar_nao_lidas_requer_autenticacao(self, client):
        """Contar não lidas deve requerer autenticação"""
        response = client.get("/chat/mensagens/nao-lidas/total", follow_redirects=False)

        assert response.status_code == 303

    def test_contar_nao_lidas_retorna_total(self, usuarios_chat):
        """Deve retornar total de não lidas"""
        client = usuarios_chat["client"]

        response = client.get("/chat/mensagens/nao-lidas/total")

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert isinstance(data["total"], int)
        assert data["total"] >= 0


class TestChatRateLimiting:
    """Testes de rate limiting para rotas de chat"""

    def test_rate_limit_busca_usuarios(self, client, fazer_login, criar_usuario_direto):
        """Rate limit deve bloquear após muitas buscas"""
        criar_usuario_direto(
            nome="Buscador Rate",
            email="buscador_rate@teste.com",
            senha="Teste@123"
        )
        fazer_login("buscador_rate@teste.com", "Teste@123")

        # Fazer muitas requisições
        with patch('routes.chat_routes.busca_usuarios_limiter') as mock_limiter:
            mock_limiter.verificar.return_value = False

            response = client.get("/chat/usuarios/buscar?q=teste", follow_redirects=False)

            # Deve retornar 429 ou redirecionar (303)
            assert response.status_code in [303, 429]

    def test_rate_limit_criar_sala(self, client, fazer_login, criar_usuario_direto):
        """Rate limit deve bloquear criação excessiva de salas"""
        criar_usuario_direto(
            nome="Criador Rate",
            email="criador_rate@teste.com",
            senha="Teste@123"
        )
        fazer_login("criador_rate@teste.com", "Teste@123")

        with patch('routes.chat_routes.chat_sala_limiter') as mock_limiter:
            mock_limiter.verificar.return_value = False

            response = client.post("/chat/salas", data={"outro_usuario_id": 999})

            assert response.status_code == 429

    def test_rate_limit_enviar_mensagem(self, client, fazer_login, criar_usuario_direto):
        """Rate limit deve bloquear envio excessivo de mensagens"""
        criar_usuario_direto(
            nome="Sender Rate",
            email="sender_rate@teste.com",
            senha="Teste@123"
        )
        fazer_login("sender_rate@teste.com", "Teste@123")

        with patch('routes.chat_routes.chat_mensagem_limiter') as mock_limiter:
            mock_limiter.verificar.return_value = False

            response = client.post(
                "/chat/mensagens",
                data={"sala_id": "1_2", "mensagem": "teste"}
            )

            assert response.status_code == 429

    def test_rate_limit_listar_conversas(self, client, fazer_login, criar_usuario_direto):
        """Rate limit deve bloquear listagem excessiva"""
        criar_usuario_direto(
            nome="Listador Rate",
            email="listador_rate@teste.com",
            senha="Teste@123"
        )
        fazer_login("listador_rate@teste.com", "Teste@123")

        with patch('routes.chat_routes.chat_listagem_limiter') as mock_limiter:
            mock_limiter.verificar.return_value = False

            response = client.get("/chat/conversas")

            assert response.status_code == 429

    def test_rate_limit_listar_mensagens(self, client, fazer_login, criar_usuario_direto):
        """Rate limit deve bloquear listagem excessiva de mensagens"""
        criar_usuario_direto(
            nome="Leitor Rate",
            email="leitor_rate@teste.com",
            senha="Teste@123"
        )
        fazer_login("leitor_rate@teste.com", "Teste@123")

        with patch('routes.chat_routes.chat_listagem_limiter') as mock_limiter:
            mock_limiter.verificar.return_value = False

            response = client.get("/chat/mensagens/1_2")

            assert response.status_code == 429


class TestChatValidationErrors:
    """Testes de erros de validação nas rotas de chat"""

    def test_criar_sala_validation_error(self, client, fazer_login, criar_usuario_direto):
        """Deve retornar erro quando validação do DTO falha"""
        criar_usuario_direto(
            nome="User Validation",
            email="validation@teste.com",
            senha="Teste@123"
        )
        fazer_login("validation@teste.com", "Teste@123")

        # Enviar dado inválido - FastAPI valida como 422
        response = client.post("/chat/salas", data={"outro_usuario_id": "invalid"})

        # Deve retornar 422 Unprocessable Entity (validação do FastAPI)
        assert response.status_code == 422

    def test_enviar_mensagem_vazia_validation_error(self, client, fazer_login, criar_usuario_direto):
        """Deve retornar erro quando mensagem está vazia"""
        criar_usuario_direto(
            nome="User Msg Validation",
            email="msg_validation@teste.com",
            senha="Teste@123"
        )
        fazer_login("msg_validation@teste.com", "Teste@123")

        # Enviar mensagem vazia - deve falhar validação
        response = client.post(
            "/chat/mensagens",
            data={"sala_id": "1_2", "mensagem": ""}
        )

        # Deve retornar erro de validação (400, 422 ou 429 se rate limit)
        assert response.status_code in [400, 422, 429]

    def test_enviar_mensagem_sala_nao_existe_apos_verificacao(self, client, fazer_login, criar_usuario_direto):
        """Deve retornar 404 quando sala não existe após verificação de participante"""
        usuario_id = criar_usuario_direto(
            nome="User Sala Fantasma",
            email="sala_fantasma@teste.com",
            senha="Teste@123"
        )
        fazer_login("sala_fantasma@teste.com", "Teste@123")

        # Mock: participante existe mas sala não
        with patch('routes.chat_routes.chat_participante_repo.obter_por_sala_e_usuario') as mock_part:
            mock_part.return_value = MagicMock(usuario_id=usuario_id, sala_id="sala_fantasma")

            with patch('routes.chat_routes.chat_sala_repo.obter_por_id', return_value=None):
                response = client.post(
                    "/chat/mensagens",
                    data={"sala_id": "sala_fantasma", "mensagem": "teste"}
                )

                # Deve retornar 404
                assert response.status_code == 404


class TestChatTotalNaoLidas:
    """Testes para endpoint de total de mensagens não lidas"""

    def test_total_nao_lidas_com_participacoes(self, client, fazer_login, criar_usuario_direto):
        """Deve contar total de não lidas incluindo loop de participações"""
        usuario_id = criar_usuario_direto(
            nome="User Nao Lidas",
            email="nao_lidas@teste.com",
            senha="Teste@123"
        )
        fazer_login("nao_lidas@teste.com", "Teste@123")

        # Criar outro usuário para chat
        outro_id = criar_usuario_direto(
            nome="Outro Nao Lidas",
            email="outro_nao_lidas@teste.com",
            senha="Teste@123"
        )

        # Criar sala e enviar mensagem
        resp = client.post("/chat/salas", data={"outro_usuario_id": outro_id})

        if resp.status_code == 200:
            # Verificar total de não lidas (deve passar pelo loop de participações)
            response = client.get("/chat/mensagens/nao-lidas/total")

            assert response.status_code == 200
            data = response.json()
            assert "total" in data
            assert isinstance(data["total"], int)


class TestChatListarConversasEdgeCases:
    """Testes de casos de borda para listagem de conversas"""

    def test_listar_conversas_sala_inexistente(self, client, fazer_login, criar_usuario_direto):
        """Deve tratar quando sala não existe mais (continue no loop)"""
        usuario_id = criar_usuario_direto(
            nome="User Sala Inexistente",
            email="sala_inexistente@teste.com",
            senha="Teste@123"
        )
        fazer_login("sala_inexistente@teste.com", "Teste@123")

        # Mock para simular participação em sala que não existe
        with patch('routes.chat_routes.chat_participante_repo.listar_por_usuario') as mock_part:
            mock_participacao = MagicMock()
            mock_participacao.sala_id = "sala_que_nao_existe"
            mock_part.return_value = [mock_participacao]

            with patch('routes.chat_routes.chat_sala_repo.obter_por_id', return_value=None):
                response = client.get("/chat/conversas")

                assert response.status_code == 200
                # Lista deve estar vazia (sala inexistente é ignorada)
                assert response.json() == []

    def test_listar_conversas_outro_participante_inexistente(self, client, fazer_login, criar_usuario_direto):
        """Deve tratar quando não encontra outro participante na sala"""
        usuario_id = criar_usuario_direto(
            nome="User Sem Outro",
            email="sem_outro@teste.com",
            senha="Teste@123"
        )
        fazer_login("sem_outro@teste.com", "Teste@123")

        # Mock para simular sala sem outro participante
        with patch('routes.chat_routes.chat_participante_repo.listar_por_usuario') as mock_list_user:
            mock_participacao = MagicMock()
            mock_participacao.sala_id = "sala_teste"
            mock_list_user.return_value = [mock_participacao]

            with patch('routes.chat_routes.chat_sala_repo.obter_por_id') as mock_sala:
                mock_sala_obj = MagicMock()
                mock_sala_obj.id = "sala_teste"
                mock_sala.return_value = mock_sala_obj

                # Simular lista de participantes com apenas o próprio usuário
                with patch('routes.chat_routes.chat_participante_repo.listar_por_sala') as mock_list_sala:
                    mock_part_proprio = MagicMock()
                    mock_part_proprio.usuario_id = usuario_id
                    mock_list_sala.return_value = [mock_part_proprio]

                    response = client.get("/chat/conversas")

                    assert response.status_code == 200
                    # Lista deve estar vazia (sem outro participante)
                    assert response.json() == []

    def test_listar_conversas_outro_usuario_excluido(self, client, fazer_login, criar_usuario_direto):
        """Deve tratar quando outro usuário foi excluído do sistema"""
        usuario_id = criar_usuario_direto(
            nome="User Outro Excluido",
            email="outro_excluido@teste.com",
            senha="Teste@123"
        )
        fazer_login("outro_excluido@teste.com", "Teste@123")

        # Mock para simular sala com participante cujo usuário foi excluído
        with patch('routes.chat_routes.chat_participante_repo.listar_por_usuario') as mock_list_user:
            mock_participacao = MagicMock()
            mock_participacao.sala_id = "sala_teste"
            mock_list_user.return_value = [mock_participacao]

            with patch('routes.chat_routes.chat_sala_repo.obter_por_id') as mock_sala:
                mock_sala_obj = MagicMock()
                mock_sala_obj.id = "sala_teste"
                mock_sala.return_value = mock_sala_obj

                with patch('routes.chat_routes.chat_participante_repo.listar_por_sala') as mock_list_sala:
                    mock_part_proprio = MagicMock()
                    mock_part_proprio.usuario_id = usuario_id
                    mock_part_outro = MagicMock()
                    mock_part_outro.usuario_id = 99999  # Usuário que foi excluído
                    mock_list_sala.return_value = [mock_part_proprio, mock_part_outro]

                    # Usuário excluído - retorna None
                    with patch('routes.chat_routes.usuario_repo.obter_por_id', return_value=None):
                        response = client.get("/chat/conversas")

                        assert response.status_code == 200
                        # Lista deve estar vazia (outro usuário foi excluído)
                        assert response.json() == []


class TestChatEnviarMensagemEdgeCases:
    """Testes de casos de borda para envio de mensagem"""

    def test_enviar_mensagem_dto_validation_error(self, client, fazer_login, criar_usuario_direto):
        """Deve tratar ValidationError do DTO corretamente"""
        criar_usuario_direto(
            nome="User Msg DTO",
            email="msg_dto@teste.com",
            senha="Teste@123"
        )
        fazer_login("msg_dto@teste.com", "Teste@123")

        # Tentar enviar mensagem com dados que falham validação do DTO
        with patch('routes.chat_routes.EnviarMensagemDTO') as mock_dto:
            from pydantic import ValidationError as PydanticValidationError
            from pydantic import BaseModel, field_validator

            class TestModel(BaseModel):
                campo: str

                @field_validator('campo')
                @classmethod
                def validar(cls, v):
                    raise ValueError("Valor inválido")

            try:
                TestModel(campo="abc")
            except PydanticValidationError as e:
                mock_dto.side_effect = e

            response = client.post(
                "/chat/mensagens",
                data={"sala_id": "sala_teste", "mensagem": "teste"}
            )

            # Deve retornar 400 Bad Request
            assert response.status_code == 400

    def test_criar_sala_dto_validation_error(self, client, fazer_login, criar_usuario_direto):
        """Deve tratar ValidationError do CriarSalaDTO corretamente"""
        criar_usuario_direto(
            nome="User Sala DTO",
            email="sala_dto@teste.com",
            senha="Teste@123"
        )
        fazer_login("sala_dto@teste.com", "Teste@123")

        # Tentar criar sala com dados que falham validação do DTO
        with patch('routes.chat_routes.CriarSalaDTO') as mock_dto:
            from pydantic import ValidationError as PydanticValidationError
            from pydantic import BaseModel, field_validator

            class TestModel(BaseModel):
                campo: int

                @field_validator('campo')
                @classmethod
                def validar(cls, v):
                    raise ValueError("Valor inválido")

            try:
                TestModel(campo=1)
            except PydanticValidationError as e:
                mock_dto.side_effect = e

            response = client.post("/chat/salas", data={"outro_usuario_id": 1})

            # Deve retornar 400 Bad Request
            assert response.status_code == 400
