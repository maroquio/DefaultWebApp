"""
Testes para o módulo util/seed_data.py

Testa a carga de dados seed para o sistema.
"""

import json
import pytest
import sqlite3
from unittest.mock import patch, MagicMock


class TestCarregarUsuariosSeed:
    """Testes para a função carregar_usuarios_seed"""

    def test_nao_executa_se_usuarios_existem(self):
        """Não deve criar usuários se já existem no banco"""
        with patch('util.seed_data.usuario_repo') as mock_repo:
            mock_repo.obter_quantidade.return_value = 5

            from util.seed_data import carregar_usuarios_seed
            carregar_usuarios_seed()

            # Não deve chamar inserir
            mock_repo.inserir.assert_not_called()

    def test_cria_usuarios_quando_banco_vazio(self):
        """Deve criar usuários quando banco está vazio"""
        with patch('util.seed_data.usuario_repo') as mock_repo:
            mock_repo.obter_quantidade.return_value = 0
            mock_repo.inserir.return_value = 1  # ID do usuário criado

            from util.seed_data import carregar_usuarios_seed
            carregar_usuarios_seed()

            # Deve chamar inserir pelo menos uma vez (para cada perfil)
            assert mock_repo.inserir.called

    def test_trata_erro_insercao(self):
        """Deve tratar erro na inserção de usuário"""
        with patch('util.seed_data.usuario_repo') as mock_repo:
            mock_repo.obter_quantidade.return_value = 0
            mock_repo.inserir.return_value = None  # Falha na inserção

            from util.seed_data import carregar_usuarios_seed

            # Não deve lançar exceção
            carregar_usuarios_seed()

    def test_trata_erro_sqlite(self):
        """Deve tratar erros SQLite durante criação"""
        with patch('util.seed_data.usuario_repo') as mock_repo:
            mock_repo.obter_quantidade.return_value = 0
            mock_repo.inserir.side_effect = sqlite3.Error("Database error")

            from util.seed_data import carregar_usuarios_seed

            # Não deve lançar exceção
            carregar_usuarios_seed()

    def test_cria_admin_definido_no_json(self, tmp_path):
        """Deve criar o usuário configurado em data/admin_seed.json"""
        seed_file = tmp_path / "admin_seed.json"
        seed_file.write_text(
            json.dumps({"usuarios": [
                {"nome": "Chefe", "email": "chefe@empresa.com",
                 "senha": "Senha@123", "perfil": "Administrador"}
            ]}),
            encoding="utf-8",
        )

        with patch('util.seed_data.usuario_repo') as mock_repo, \
             patch('util.seed_data.CAMINHO_SEED_USUARIOS', seed_file):
            mock_repo.obter_quantidade.return_value = 0
            mock_repo.inserir.return_value = 1

            from util.seed_data import carregar_usuarios_seed
            carregar_usuarios_seed()

            # Deve criar exatamente o usuário do JSON (não os perfis do enum)
            assert mock_repo.inserir.call_count == 1
            usuario = mock_repo.inserir.call_args[0][0]
            assert usuario.email == "chefe@empresa.com"
            assert usuario.nome == "Chefe"
            assert usuario.perfil == "Administrador"
            # Senha deve ser armazenada com hash, nunca em texto puro
            assert usuario.senha != "Senha@123"

    def test_fallback_para_perfis_sem_json(self, tmp_path):
        """Sem arquivo de seed, deve gerar um usuário por perfil do enum"""
        seed_file = tmp_path / "inexistente.json"

        with patch('util.seed_data.usuario_repo') as mock_repo, \
             patch('util.seed_data.CAMINHO_SEED_USUARIOS', seed_file):
            mock_repo.obter_quantidade.return_value = 0
            mock_repo.inserir.return_value = 1

            from util.seed_data import carregar_usuarios_seed, Perfil
            carregar_usuarios_seed()

            assert mock_repo.inserir.call_count == len(list(Perfil))


class TestInicializarDados:
    """Testes para a função inicializar_dados"""

    def test_inicializar_chama_carregar_usuarios(self):
        """Deve chamar carregar_usuarios_seed"""
        with patch('util.seed_data.carregar_usuarios_seed') as mock_carregar:
            from util.seed_data import inicializar_dados
            inicializar_dados()

            mock_carregar.assert_called_once()

    def test_inicializar_trata_erro_sqlite(self):
        """Deve tratar erro SQLite na inicialização"""
        with patch('util.seed_data.carregar_usuarios_seed') as mock_carregar:
            mock_carregar.side_effect = sqlite3.Error("Critical error")

            from util.seed_data import inicializar_dados

            # Não deve lançar exceção
            inicializar_dados()

    def test_loga_inicio_e_fim(self):
        """Deve logar início e fim da inicialização"""
        with patch('util.seed_data.carregar_usuarios_seed'):
            with patch('util.seed_data.logger') as mock_logger:
                from util.seed_data import inicializar_dados
                inicializar_dados()

                # Deve ter chamado logger.info várias vezes
                assert mock_logger.info.call_count >= 2
