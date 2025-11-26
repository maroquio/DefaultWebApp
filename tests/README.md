# Guia de Testes - DefaultWebApp

Este documento define as convenções, padrões e melhores práticas para escrever testes neste projeto.

## 📋 Índice

- [Estrutura de Testes](#estrutura-de-testes)
- [Fixtures Disponíveis](#fixtures-disponíveis)
- [Test Helpers](#test-helpers)
- [Padrões de Assertion](#padrões-de-assertion)
- [Convenções de Nomenclatura](#convenções-de-nomenclatura)
- [Exemplos Práticos](#exemplos-práticos)

---

## 🏗️ Estrutura de Testes

### Organização de Arquivos

```
tests/
├── conftest.py              # Fixtures compartilhadas
├── test_helpers.py          # Funções helper para assertions
├── test_auth.py             # Testes de autenticação
├── test_perfil.py           # Testes de perfil do usuário
├── test_usuario.py          # Testes de dashboard do usuário
├── test_tarefas.py          # Testes CRUD de tarefas
├── test_admin_usuarios.py   # Testes de administração de usuários
├── test_admin_backups.py    # Testes de backups
├── test_admin_configuracoes.py  # Testes de configurações
├── test_public.py           # Testes de rotas públicas
└── README.md                # Este arquivo
```

### Organização de Classes

Cada arquivo de teste deve organizar testes em classes temáticas:

```python
class TestListarTarefas:
    """Testes de listagem de tarefas"""

class TestCriarTarefa:
    """Testes de criação de tarefa"""

class TestExcluirTarefa:
    """Testes de exclusão de tarefa"""
```

**Convenção**: Use o prefixo `Test` nas classes e agrupe testes relacionados.

---

## 🔧 Fixtures Disponíveis

Todas as fixtures estão definidas em `conftest.py` e disponíveis automaticamente para todos os testes.

### Fixtures Básicas

#### `client` - TestClient FastAPI
Cliente de teste com sessão limpa para cada teste.

```python
def test_acessar_home(client):
    response = client.get("/")
    assert response.status_code == 200
```

#### `usuario_teste` - Dados de usuário padrão
Dicionário com dados de um usuário de teste (Cliente).

```python
def test_com_dados_usuario(usuario_teste):
    assert usuario_teste["email"] == "teste@example.com"
    assert usuario_teste["perfil"] == Perfil.CLIENTE.value
```

#### `admin_teste` - Dados de admin
Dicionário com dados de um administrador de teste.

```python
def test_com_dados_admin(admin_teste):
    assert admin_teste["perfil"] == Perfil.ADMIN.value
```

#### `vendedor_teste` - Dados de vendedor
Dicionário com dados de um vendedor de teste.

```python
def test_com_dados_vendedor(vendedor_teste):
    assert vendedor_teste["perfil"] == Perfil.VENDEDOR.value
```

### Fixtures de Ação

#### `criar_usuario` - Função para criar usuários
Retorna uma função que cadastra usuários via endpoint.

```python
def test_criar_usuario(criar_usuario):
    response = criar_usuario("João Silva", "joao@example.com", "Senha@123")
    assert response.status_code == 303
```

#### `fazer_login` - Função para fazer login
Retorna uma função que faz login via endpoint.

```python
def test_fazer_login(client, criar_usuario, usuario_teste, fazer_login):
    criar_usuario(usuario_teste["nome"], usuario_teste["email"], usuario_teste["senha"])
    response = fazer_login(usuario_teste["email"], usuario_teste["senha"])
    assert response.status_code == 303
```

### Fixtures de Cliente Autenticado

#### `cliente_autenticado` - Cliente logado como usuário
Cliente TestClient já autenticado como usuário padrão (Cliente).

```python
def test_acessar_dashboard(cliente_autenticado):
    response = cliente_autenticado.get("/usuario")
    assert response.status_code == 200
```

#### `admin_autenticado` - Cliente logado como admin
Cliente TestClient já autenticado como administrador.

```python
def test_listar_usuarios(admin_autenticado):
    response = admin_autenticado.get("/admin/usuarios/listar")
    assert response.status_code == 200
```

#### `vendedor_autenticado` - Cliente logado como vendedor
Cliente TestClient já autenticado como vendedor.

```python
def test_acessar_vendas(vendedor_autenticado):
    response = vendedor_autenticado.get("/vendas")
    assert response.status_code == 200
```

### Fixtures Avançadas

#### `dois_usuarios` - Dois usuários para testes de isolamento
Cria dois usuários e retorna tupla com seus dados.

```python
def test_isolamento_dados(client, dois_usuarios, fazer_login):
    usuario1, usuario2 = dois_usuarios

    # Login como usuário 1
    fazer_login(usuario1["email"], usuario1["senha"])
    # ... verificar que só vê seus dados
```

#### `usuario_com_foto` - Cliente com foto de perfil
Cliente autenticado que já tem foto de perfil salva.

```python
def test_visualizar_foto(usuario_com_foto):
    response = usuario_com_foto.get("/perfil/visualizar")
    assert response.status_code == 200
    # Foto já existe
```

#### `foto_teste_base64` - Imagem válida em base64
Retorna uma imagem PNG 1x1 pixel em formato base64 para testes de upload.

```python
def test_upload_foto(cliente_autenticado, foto_teste_base64):
    response = cliente_autenticado.post("/perfil/atualizar-foto", json={
        "imagem": foto_teste_base64
    })
    assert response.status_code == 303
```

#### `criar_backup` - Função para criar backup
Retorna função que cria backup para testes.

```python
def test_listar_backups(admin_autenticado, criar_backup):
    sucesso, mensagem = criar_backup()
    assert sucesso is True
```

#### `obter_ultimo_backup` - Função para obter último backup
Retorna função que obtém informações do backup mais recente.

```python
def test_restaurar_backup(admin_autenticado, criar_backup, obter_ultimo_backup):
    criar_backup()
    backup = obter_ultimo_backup()
    assert backup is not None
    assert "nome_arquivo" in backup
```

---

## 🛠️ Test Helpers

Funções helper definidas em `test_helpers.py` para padronizar assertions comuns.

### `assert_permission_denied(response, expected_redirect="/login")`

Verifica que permissão foi negada (status 303 e redirect para login).

**Uso:**
```python
from tests.test_helpers import assert_permission_denied

def test_area_protegida_sem_login(client):
    response = client.get("/admin/usuarios", follow_redirects=False)
    assert_permission_denied(response)
```

**Quando usar:**
- Testar acesso a rotas protegidas sem autenticação
- Testar acesso a rotas admin sem perfil adequado
- Verificar redirecionamento para login

**Características:**
- Aceita query strings no redirect (ex: `/login?redirect=/page`)
- Permite customizar URL de redirect esperada

### `assert_redirects_to(response, expected_url, expected_status=303)`

Verifica redirecionamento para URL específica.

**Uso:**
```python
from tests.test_helpers import assert_redirects_to

def test_login_redireciona_para_dashboard(client, criar_usuario, usuario_teste):
    criar_usuario(usuario_teste["nome"], usuario_teste["email"], usuario_teste["senha"])
    response = client.post("/login", data={
        "email": usuario_teste["email"],
        "senha": usuario_teste["senha"]
    }, follow_redirects=False)

    assert_redirects_to(response, "/usuario")
```

**Quando usar:**
- Verificar redirecionamentos após POST (PRG pattern)
- Testar fluxos de navegação
- Validar redirecionamentos após login/logout

**Características:**
- Verifica status code (padrão: 303)
- Verifica URL exata no header `location`

### `assert_contains_text(response, text, case_sensitive=False)`

Verifica que resposta contém texto específico.

**Uso:**
```python
from tests.test_helpers import assert_contains_text

def test_dashboard_exibe_nome(cliente_autenticado, usuario_teste):
    response = cliente_autenticado.get("/usuario")
    assert_contains_text(response, usuario_teste["nome"])
```

**Quando usar:**
- Verificar conteúdo de páginas HTML
- Validar mensagens de erro/sucesso
- Testar se dados aparecem na listagem

**Características:**
- Case-insensitive por padrão
- Pode ativar case-sensitive com parâmetro

---

## ✅ Padrões de Assertion

### 1. Status Code

**SEMPRE verifique o status code**, mesmo com `follow_redirects=True`:

```python
# ✅ CORRETO
response = client.get("/pagina", follow_redirects=True)
assert response.status_code == 200

# ❌ ERRADO - não verifica status
response = client.get("/pagina", follow_redirects=True)
assert "conteudo" in response.text
```

**Convenções:**
- Use `==` para status único esperado
- Use `in [...]` APENAS quando múltiplos status são válidos

```python
# ✅ CORRETO - status único
assert response.status_code == status.HTTP_200_OK

# ✅ CORRETO - múltiplos válidos (admin pode retornar 303 ou 403)
assert response.status_code in [
    status.HTTP_303_SEE_OTHER,
    status.HTTP_403_FORBIDDEN
]

# ❌ EVITE - use helper em vez disso
assert response.status_code == 303
assert response.headers["location"] == "/login"

# ✅ MELHOR - use helper
assert_permission_denied(response)
```

### 2. Redirects

**SEMPRE use `follow_redirects=False`** quando testar redirecionamentos:

```python
# ✅ CORRETO
response = client.post("/login", data={...}, follow_redirects=False)
assert_redirects_to(response, "/usuario")

# ❌ ERRADO - follow_redirects=True esconde o redirect
response = client.post("/login", data={...}, follow_redirects=True)
assert response.status_code == 200  # Já seguiu o redirect!
```

**Quando seguir redirects:**
- Quando você quer testar o conteúdo final
- Quando o redirect não é o foco do teste

```python
# ✅ CORRETO - testa conteúdo após redirect
response = client.post("/cadastrar", data={...}, follow_redirects=True)
assert response.status_code == 200
assert_contains_text(response, "Login")
```

### 3. Conteúdo de Resposta

**SEMPRE use case-insensitive** para verificações de texto (a menos que case importe):

```python
# ✅ CORRETO - use helper
assert_contains_text(response, "bem-vindo")

# ✅ CORRETO - manual case-insensitive
assert "erro" in response.text.lower()

# ❌ EVITE - case-sensitive pode falhar desnecessariamente
assert "Bem-vindo" in response.text
```

### 4. Validação de Dados

**SEMPRE verifique dados no banco após operações de escrita:**

```python
# ✅ CORRETO
response = client.post("/cadastrar", data={...})
assert_redirects_to(response, "/login")

# Verificar no banco
from repo import usuario_repo
usuario = usuario_repo.obter_por_email("teste@example.com")
assert usuario is not None
assert usuario.nome == "Usuario Teste"

# ❌ INCOMPLETO - só verifica redirect, não o dado
response = client.post("/cadastrar", data={...})
assert_redirects_to(response, "/login")
```

### 5. Autorização e Isolamento

**SEMPRE teste isolamento de dados entre usuários:**

```python
# ✅ CORRETO - verifica isolamento
def test_usuario_nao_ve_tarefas_de_outros(client, dois_usuarios, fazer_login):
    usuario1, usuario2 = dois_usuarios

    # Usuario 1 cria tarefa
    fazer_login(usuario1["email"], usuario1["senha"])
    client.post("/tarefas/cadastrar", data={"titulo": "Tarefa do Usuario 1"})
    client.get("/logout")

    # Usuario 2 não deve ver
    fazer_login(usuario2["email"], usuario2["senha"])
    response = client.get("/tarefas/listar")
    assert "Tarefa do Usuario 1" not in response.text
```

---

## 📛 Convenções de Nomenclatura

### Nomes de Testes

Padrão: `test_<acao>_<condicao>_<resultado_esperado>`

**Exemplos:**

```python
# ✅ BOM - claro e descritivo
def test_login_com_credenciais_validas_redireciona_para_dashboard():
    pass

def test_usuario_nao_autenticado_nao_acessa_dashboard():
    pass

# ❌ RUIM - vago
def test_login():
    pass

def test_tarefa():
    pass

def test_erro():
    pass
```

### Nomes de Classes

Padrão: `Test<Entidade><Acao>`

**Exemplos:**

```python
# ✅ BOM
class TestListarUsuarios:
    """Testes de listagem de usuários"""

class TestCriarTarefa:
    """Testes de criação de tarefa"""

class TestAutorizacao:
    """Testes de autorização e controle de acesso"""

# ❌ RUIM
class Tests:
    pass

class UsuarioTests:
    pass
```

### Docstrings

**SEMPRE adicione docstrings** em testes não-triviais:

```python
def test_admin_nao_pode_excluir_a_si_mesmo(admin_autenticado, admin_teste):
    """Admin não deve poder excluir sua própria conta.

    Isso previne que o último admin seja removido do sistema,
    deixando a aplicação sem administradores.
    """
    from repo import usuario_repo
    admin = usuario_repo.obter_por_email(admin_teste["email"])

    response = admin_autenticado.post(f"/admin/usuarios/excluir/{admin.id}")
    assert_redirects_to(response, "/admin/usuarios/listar")

    # Verificar que admin ainda existe
    admin_ainda_existe = usuario_repo.obter_por_id(admin.id)
    assert admin_ainda_existe is not None
```

---

## 💡 Exemplos Práticos

### Exemplo 1: Teste de Autenticação Completo

```python
def test_fluxo_completo_cadastro_e_login(client):
    """Testa fluxo completo de cadastro e login de usuário."""

    # 1. Cadastrar novo usuário
    response_cadastro = client.post("/cadastrar", data={
        "perfil": Perfil.CLIENTE.value,
        "nome": "João da Silva",
        "email": "joao@example.com",
        "senha": "Senha@123",
        "confirmar_senha": "Senha@123"
    }, follow_redirects=False)

    # Deve redirecionar para login
    assert_redirects_to(response_cadastro, "/login")

    # 2. Verificar que usuário foi criado no banco
    from repo import usuario_repo
    usuario = usuario_repo.obter_por_email("joao@example.com")
    assert usuario is not None
    assert usuario.nome == "João da Silva"
    assert usuario.perfil == Perfil.CLIENTE.value

    # 3. Fazer login
    response_login = client.post("/login", data={
        "email": "joao@example.com",
        "senha": "Senha@123"
    }, follow_redirects=False)

    # Deve redirecionar para dashboard
    assert_redirects_to(response_login, "/usuario")

    # 4. Verificar acesso ao dashboard
    response_dashboard = client.get("/usuario")
    assert response_dashboard.status_code == 200
    assert_contains_text(response_dashboard, "João da Silva")
```

### Exemplo 2: Teste de Autorização

```python
def test_cliente_nao_acessa_area_admin(cliente_autenticado):
    """Cliente não deve ter acesso a áreas administrativas."""

    # Tentar acessar listagem de usuários (admin only)
    response = cliente_autenticado.get("/admin/usuarios/listar", follow_redirects=False)

    # Deve negar acesso (redirect ou 403)
    assert response.status_code in [
        status.HTTP_303_SEE_OTHER,
        status.HTTP_403_FORBIDDEN
    ]

    # Se redirect, deve ser para página adequada
    if response.status_code == status.HTTP_303_SEE_OTHER:
        location = response.headers.get("location")
        assert location in ["/login", "/usuario", "/"]
```

### Exemplo 4: Teste com Fixtures Avançadas

```python
def test_restaurar_backup_cria_backup_automatico(
    admin_autenticado,
    criar_backup,
    obter_ultimo_backup
):
    """Restaurar backup deve criar backup automático antes."""

    # Criar backup inicial
    sucesso, mensagem = criar_backup()
    assert sucesso is True

    backup_original = obter_ultimo_backup()
    assert backup_original is not None
    nome_backup = backup_original["nome_arquivo"]

    # Fazer algumas alterações no banco (criar usuário, por exemplo)
    from repo import usuario_repo
    from model.usuario_model import Usuario
    from util.security import criar_hash_senha

    novo_usuario = Usuario(
        id=0,
        nome="Usuario Teste",
        email="teste_restauracao@example.com",
        senha=criar_hash_senha("Senha@123"),
        perfil=Perfil.CLIENTE.value
    )
    usuario_id = usuario_repo.inserir(novo_usuario)
    assert usuario_id is not None

    # Restaurar backup (deve criar backup automático antes)
    response = admin_autenticado.post(
        f"/admin/backups/restaurar/{nome_backup}",
        follow_redirects=False
    )
    assert_redirects_to(response, "/admin/backups/listar")

    # Verificar que usuário criado não existe mais (foi restaurado estado anterior)
    usuario = usuario_repo.obter_por_email("teste_restauracao@example.com")
    assert usuario is None
```

---

## 🚀 Executando Testes

### Comandos Básicos

```bash
# Rodar todos os testes
pytest

# Rodar com verbose
pytest -v

# Rodar arquivo específico
pytest tests/test_auth.py

# Rodar teste específico
pytest tests/test_auth.py::TestLogin::test_login_com_credenciais_validas

# Rodar testes que contém palavra-chave
pytest -k "login"

# Rodar com coverage
pytest --cov

# Rodar com coverage e relatório HTML
pytest --cov --cov-report=html
```

### Markers Úteis

```python
@pytest.mark.auth
def test_login():
    pass

@pytest.mark.crud
def test_criar_tarefa():
    pass

@pytest.mark.integration
def test_fluxo_completo():
    pass
```

Executar por marker:
```bash
pytest -m auth        # Apenas testes de autenticação
pytest -m crud        # Apenas testes de CRUD
pytest -m integration # Apenas testes de integração
```

---

## 📚 Referências

- **Pytest Documentation**: https://docs.pytest.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **TestClient**: https://www.starlette.io/testclient/

---

**Última atualização**: 2025-10-22
**Versão**: 1.0
