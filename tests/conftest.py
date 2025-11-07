"""
Configurações e fixtures para testes pytest.

Fornece fixtures reutilizáveis e helpers para testes da aplicação.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status
import os
import tempfile
from pathlib import Path
from typing import Optional
from util.perfis import Perfil

# Configurar banco de dados de teste ANTES de importar a aplicação
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Configura banco de dados de teste em memória para toda a sessão"""
    # Criar arquivo temporário para o banco de testes
    test_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
    test_db_path = test_db.name
    test_db.close()

    # Configurar variável de ambiente para usar DB de teste
    os.environ['DATABASE_PATH'] = test_db_path

    # Desabilitar envio de e-mails durante testes
    os.environ['RESEND_API_KEY'] = ''

    # Configurar nível de log para testes
    os.environ['LOG_LEVEL'] = 'ERROR'

    yield test_db_path

    # Limpar: remover arquivo de banco após todos os testes
    try:
        os.unlink(test_db_path)
    except:
        pass


@pytest.fixture(scope="function", autouse=True)
def limpar_rate_limiter():
    """Limpa o rate limiter antes de cada teste para evitar bloqueios"""
    # Importar após configuração do banco de dados
    from routes.auth_routes import login_limiter, cadastro_limiter, esqueci_senha_limiter
    from routes.admin_usuarios_routes import admin_usuarios_limiter
    from routes.admin_backups_routes import admin_backups_limiter, backup_download_limiter
    from routes.admin_configuracoes_routes import admin_config_limiter
    from routes.chamados_routes import chamado_criar_limiter, chamado_responder_limiter
    from routes.admin_chamados_routes import admin_chamado_responder_limiter
    from routes.usuario_routes import upload_foto_limiter, alterar_senha_limiter, form_get_limiter
    from routes.chat_routes import chat_mensagem_limiter, chat_sala_limiter, busca_usuarios_limiter, chat_listagem_limiter
    from routes.public_routes import public_limiter
    from routes.examples_routes import examples_limiter

    # Lista de todos os limiters
    limiters = [
        login_limiter,
        cadastro_limiter,
        esqueci_senha_limiter,
        admin_usuarios_limiter,
        admin_backups_limiter,
        backup_download_limiter,
        admin_config_limiter,
        chamado_criar_limiter,
        chamado_responder_limiter,
        admin_chamado_responder_limiter,
        upload_foto_limiter,
        alterar_senha_limiter,
        form_get_limiter,
        chat_mensagem_limiter,
        chat_sala_limiter,
        busca_usuarios_limiter,
        chat_listagem_limiter,
        public_limiter,
        examples_limiter,
    ]

    # Limpar antes do teste
    for limiter in limiters:
        limiter.limpar()

    yield

    # Limpar depois do teste também
    for limiter in limiters:
        limiter.limpar()


@pytest.fixture(scope="function", autouse=True)
def limpar_banco_dados():
    """Limpa todas as tabelas do banco antes de cada teste para evitar interferência"""
    # Importar após configuração do banco de dados
    from util.db_util import get_connection

    def _limpar_tabelas():
        """Limpa tabelas se elas existirem e reseta autoincrement"""
        with get_connection() as conn:
            cursor = conn.cursor()
            # Verificar se tabelas existem antes de limpar
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('chamado', 'chamado_interacao', 'usuario', 'configuracao')"
            )
            tabelas_existentes = [row[0] for row in cursor.fetchall()]

            # Limpar apenas tabelas que existem (respeitando foreign keys)
            # Limpar chamado_interacao antes de chamado (devido à FK)
            if 'chamado_interacao' in tabelas_existentes:
                cursor.execute("DELETE FROM chamado_interacao")
            if 'chamado' in tabelas_existentes:
                cursor.execute("DELETE FROM chamado")
            if 'usuario' in tabelas_existentes:
                cursor.execute("DELETE FROM usuario")
            if 'configuracao' in tabelas_existentes:
                cursor.execute("DELETE FROM configuracao")

            # Resetar autoincrement (limpar sqlite_sequence se existir)
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'"
            )
            if cursor.fetchone():
                cursor.execute("DELETE FROM sqlite_sequence")

            conn.commit()

    # Limpar antes do teste
    _limpar_tabelas()

    yield

    # Limpar depois do teste também
    _limpar_tabelas()


@pytest.fixture(scope="function")
def client():
    """
    Cliente de teste FastAPI com sessão limpa para cada teste
    Importa app DEPOIS de configurar o banco de dados
    """
    # Importar aqui para garantir que as configurações de teste sejam aplicadas
    from main import app

    # Criar cliente de teste
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def usuario_teste():
    """Dados de um usuário de teste padrão"""
    return {
        "nome": "Usuario Teste",
        "email": "teste@example.com",
        "senha": "Senha@123",
        "perfil": Perfil.CLIENTE.value  # Usa Enum Perfil
    }


@pytest.fixture
def admin_teste():
    """Dados de um admin de teste"""
    return {
        "nome": "Admin Teste",
        "email": "admin@example.com",
        "senha": "Admin@123",
        "perfil": Perfil.ADMIN.value  # Usa Enum Perfil
    }


@pytest.fixture
def criar_usuario(client):
    """
    Fixture que retorna uma função para criar usuários
    Útil para criar múltiplos usuários em um teste
    """
    def _criar_usuario(nome: str, email: str, senha: str, perfil: str = Perfil.CLIENTE.value):
        """Cadastra um usuário via endpoint de cadastro"""
        response = client.post("/cadastrar", data={
            "perfil": perfil,
            "nome": nome,
            "email": email,
            "senha": senha,
            "confirmar_senha": senha
        }, follow_redirects=False)
        return response

    return _criar_usuario


@pytest.fixture
def fazer_login(client):
    """
    Fixture que retorna uma função para fazer login
    Retorna o cliente já autenticado
    """
    def _fazer_login(email: str, senha: str):
        """Faz login e retorna o cliente autenticado"""
        response = client.post("/login", data={
            "email": email,
            "senha": senha
        }, follow_redirects=False)
        return response

    return _fazer_login


@pytest.fixture
def cliente_autenticado(client, criar_usuario, fazer_login, usuario_teste):
    """
    Fixture que retorna um cliente já autenticado
    Cria um usuário e faz login automaticamente
    """
    # Criar usuário
    criar_usuario(
        usuario_teste["nome"],
        usuario_teste["email"],
        usuario_teste["senha"]
    )

    # Fazer login
    fazer_login(usuario_teste["email"], usuario_teste["senha"])

    # Retornar cliente autenticado
    return client


@pytest.fixture
def admin_autenticado(client, criar_usuario, fazer_login, admin_teste):
    """
    Fixture que retorna um cliente autenticado como admin
    """
    # Importar para manipular diretamente o banco
    from repo import usuario_repo
    from model.usuario_model import Usuario
    from util.security import criar_hash_senha

    # Criar admin diretamente no banco (pular validações de cadastro público)
    admin = Usuario(
        id=0,
        nome=admin_teste["nome"],
        email=admin_teste["email"],
        senha=criar_hash_senha(admin_teste["senha"]),
        perfil=Perfil.ADMIN.value  # Usa Enum Perfil
    )
    usuario_repo.inserir(admin)

    # Fazer login
    fazer_login(admin_teste["email"], admin_teste["senha"])

    # Retornar cliente autenticado
    return client


@pytest.fixture
def vendedor_teste():
    """Dados de um vendedor de teste"""
    return {
        "nome": "Vendedor Teste",
        "email": "vendedor@example.com",
        "senha": "Vendedor@123",
        "perfil": Perfil.VENDEDOR.value
    }


@pytest.fixture
def vendedor_autenticado(client, criar_usuario, fazer_login, vendedor_teste):
    """
    Fixture que retorna um cliente autenticado como vendedor
    """
    # Importar para manipular diretamente o banco
    from repo import usuario_repo
    from model.usuario_model import Usuario
    from util.security import criar_hash_senha

    # Criar vendedor diretamente no banco
    vendedor = Usuario(
        id=0,
        nome=vendedor_teste["nome"],
        email=vendedor_teste["email"],
        senha=criar_hash_senha(vendedor_teste["senha"]),
        perfil=Perfil.VENDEDOR.value
    )
    usuario_repo.inserir(vendedor)

    # Fazer login
    fazer_login(vendedor_teste["email"], vendedor_teste["senha"])

    # Retornar cliente autenticado
    return client


@pytest.fixture
def foto_teste_base64():
    """
    Retorna uma imagem 1x1 pixel PNG válida em base64
    Útil para testes de upload de foto
    """
    # PNG 1x1 pixel transparente em base64
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


@pytest.fixture
def criar_backup():
    """
    Fixture que retorna uma função para criar backup de teste
    """
    def _criar_backup():
        """Cria um backup via util/backup_util"""
        from util import backup_util
        sucesso, mensagem = backup_util.criar_backup()
        return sucesso, mensagem

    return _criar_backup


# ===== TEST HELPERS - Funções auxiliares para assertions =====

def assert_permission_denied(response, expected_redirect: str = "/login"):
    """
    Helper para verificar se permissão foi negada.

    Verifica se resposta é 303 e redireciona para login ou página esperada.

    Args:
        response: Response object do TestClient
        expected_redirect: URL esperada de redirecionamento (padrão: /login)

    Example:
        >>> response = client.get("/admin/usuarios")
        >>> assert_permission_denied(response)
    """
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == expected_redirect


def assert_redirects_to(response, expected_url: str, expected_status: int = status.HTTP_303_SEE_OTHER):
    """
    Helper para verificar redirecionamento.

    Args:
        response: Response object do TestClient
        expected_url: URL esperada de redirecionamento
        expected_status: Status code esperado (padrão: 303)

    Example:
        >>> response = client.post("/login", data={...})
        >>> assert_redirects_to(response, "/usuario")
    """
    assert response.status_code == expected_status
    assert response.headers.get("location") == expected_url


def assert_contains_text(response, text: str, case_sensitive: bool = False):
    """
    Helper para verificar se response contém texto.

    Args:
        response: Response object do TestClient
        text: Texto esperado no conteúdo
        case_sensitive: Se deve ser case-sensitive (padrão: False)

    Example:
        >>> response = client.get("/")
        >>> assert_contains_text(response, "bem-vindo")
    """
    content = response.text
    if not case_sensitive:
        assert text.lower() in content.lower()
    else:
        assert text in content


# ===== FIXTURES AVANÇADAS =====

@pytest.fixture
def dois_usuarios(client, criar_usuario):
    """
    Fixture que cria dois usuários de teste.

    Útil para testes que verificam isolamento de dados entre usuários.

    Returns:
        Tuple com dados dos dois usuários (dict, dict)
    """
    usuario1 = {
        "nome": "Usuario Um",
        "email": "usuario1@example.com",
        "senha": "Senha@123",
        "perfil": Perfil.CLIENTE.value
    }
    usuario2 = {
        "nome": "Usuario Dois",
        "email": "usuario2@example.com",
        "senha": "Senha@456",
        "perfil": Perfil.CLIENTE.value
    }

    # Criar ambos usuários
    criar_usuario(usuario1["nome"], usuario1["email"], usuario1["senha"])
    criar_usuario(usuario2["nome"], usuario2["email"], usuario2["senha"])

    return usuario1, usuario2


@pytest.fixture
def usuario_com_foto(cliente_autenticado, foto_teste_base64):
    """
    Fixture que retorna um cliente autenticado com foto de perfil.

    Returns:
        TestClient autenticado com foto já salva
    """
    # Atualizar foto do perfil
    response = cliente_autenticado.post(
        "/perfil/foto/atualizar",
        json={"imagem": foto_teste_base64},
        follow_redirects=False
    )

    # Verificar se foto foi salva com sucesso
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_303_SEE_OTHER]

    return cliente_autenticado


@pytest.fixture
def obter_ultimo_backup():
    """
    Fixture que retorna função para obter último backup criado.

    Returns:
        Função que retorna dict com dados do último backup ou None
    """
    def _obter_ultimo_backup() -> Optional[dict]:
        """Obtém informações do último backup na pasta backups/"""
        from util import backup_util

        backups = backup_util.listar_backups()
        if not backups:
            return None

        # Retornar o mais recente (primeiro da lista)
        return backups[0]

    return _obter_ultimo_backup
