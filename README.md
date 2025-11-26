# DefaultWebApp - Boilerplate FastAPI Completo

> Boilerplate profissional e educacional para desenvolvimento rápido de aplicações web modernas em Python, com componentes reutilizáveis, validação robusta e exemplos práticos. Agora com deploy via Jenkinsfile!

## 🎯 Visão Geral

**DefaultWebApp** é um template completo de aplicação web que elimina a necessidade de "começar do zero". Ele fornece toda a estrutura base e componentes reutilizáveis para você focar no que realmente importa: **desenvolver as funcionalidades específicas do seu projeto**.

### Por que usar este boilerplate?

✅ **Sistema de autenticação completo** - Login, cadastro, perfis de usuário, recuperação de senha

✅ **Componentes UI reutilizáveis** - Modais, formulários, galerias, tabelas responsivas

✅ **Validação robusta** - 15+ validadores prontos (CPF, CNPJ, email, telefone, etc.)

✅ **Tratamento de erros centralizado** - Sistema inteligente que elimina ~70% do código repetitivo

✅ **Máscaras de input** - CPF, CNPJ, telefone, valores monetários, datas, placas de veículo

✅ **Sistema de fotos** - Upload, crop, redimensionamento automático

✅ **28+ temas prontos** - Bootswatch themes para customização instantânea

✅ **Páginas de exemplo** - 9 exemplos completos de layouts e funcionalidades

✅ **Padrão CRUD** - Template documentado para criar novas entidades rapidamente

✅ **Logger profissional** - Sistema de logs com rotação automática

✅ **Email integrado** - Envio de emails transacionais (Resend.com)

✅ **Flash messages e toasts** - Feedback visual automático para o usuário

✅ **Testes configurados** - Estrutura completa de testes com pytest

✅ **Seed data** - Sistema de dados iniciais em JSON

✅ **Segurança** - Rate limiting, security headers, hash de senhas, proteção SQL injection

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/maroquio/DefaultWebApp
   cd DefaultWebApp
   ```

2. **Crie um ambiente virtual**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   # Copie o arquivo de exemplo
   cp .env.example .env

   # Edite o arquivo .env com suas configurações
   # Pelo menos altere o SECRET_KEY para produção
   ```

5. **Execute a aplicação**
   ```bash
   python main.py
   ```

6. **Acesse no navegador**
   ```
   http://localhost:8400
   ```

7. **Explore os exemplos**
   ```
   http://localhost:8400/exemplos
   ```

## 👥 Usuários Padrão

O sistema vem com usuários pré-cadastrados para facilitar os testes:

| Perfil | E-mail | Senha | Descrição |
|--------|--------|-------|-----------|
| **Admininistrador** | administrador@email.com | 1234aA@# | Acesso administrativo completo |
| **Cliente** | cliente@email.com | 1234aA@# | Usuário com perfil Cliente |
| **Vendedor** | vendedor@email.com | 1234aA@# | Usuário com perfil Vendedor |

> ⚠️ **Importante**: Altere essas senhas em ambiente de produção!

## 📚 O Que Este Boilerplate Oferece

### 🔐 Sistema de Autenticação Completo

- **Login/Logout** com sessões seguras
- **Cadastro de usuários** com validação de senha forte
- **Recuperação de senha** por email
- **Perfis de usuário** (Admin, Cliente, Vendedor - extensível)
- **Proteção de rotas** por perfil com decorator `@requer_autenticacao()`
- **Gerenciamento de usuários** (CRUD completo para admins)

### 🎨 Componentes UI Reutilizáveis

#### Templates Components (use `{% include %}`)

**Modal de Confirmação** (`components/modal_confirmacao.html`)
```javascript
abrirModalConfirmacao({
    url: '/rota/excluir/1',
    mensagem: 'Tem certeza?',
    detalhes: '<div>Detalhes aqui</div>'
});
```

**Modal de Crop de Imagem** (`components/modal_corte_imagem.html`)
- Integrado com Cropper.js
- Upload via drag & drop
- Redimensionamento automático

**Galeria de Fotos** (`components/galeria_fotos.html`)
```jinja
{% from 'components/galeria_fotos.html' import galeria_fotos %}
{{ galeria_fotos(images, gallery_id='gallery1') }}
```

#### Macros de Formulário (use `{% from ... import ... %}`)

Biblioteca completa em `macros/form_fields.html`:

```jinja
{% from 'macros/form_fields.html' import input_text, input_email, input_password,
   input_date, input_decimal, textarea, select, checkbox, radio %}

{# Campos de texto com validação #}
{{ input_text('nome', 'Nome Completo', value=nome, required=True, error=erros.get('nome')) }}

{# Email com validação #}
{{ input_email('email', 'E-mail', value=email, required=True) }}

{# Senha com toggle de visibilidade #}
{{ input_password('senha', 'Senha', required=True) }}

{# Data com calendário #}
{{ input_date('data_nascimento', 'Data de Nascimento', value=data) }}

{# Valores monetários/decimais #}
{{ input_decimal('preco', 'Preço', prefix='R$ ', decimal_places=2) }}

{# Select dropdown #}
{{ select('categoria', 'Categoria', options=categorias, value=categoria_atual) }}

{# Checkbox e radio buttons #}
{{ checkbox('aceito_termos', 'Aceito os termos de uso', checked=True) }}
{{ radio('tipo', 'Tipo', options=tipos, value=tipo_selecionado) }}
```

### 🎭 Máscaras de Input Automáticas

Sistema completo de máscaras em `static/js/input-mask.js`:

```html
<!-- CPF com máscara automática -->
<input data-mask="CPF" name="cpf" data-unmask="true">

<!-- CNPJ -->
<input data-mask="CNPJ" name="cnpj">

<!-- Telefone com 9 dígitos -->
<input data-mask="TELEFONE" name="telefone">

<!-- CEP -->
<input data-mask="CEP" name="cep">

<!-- Data -->
<input data-mask="DATA" name="data">

<!-- Placa de veículo Mercosul -->
<input data-mask="PLACA_MERCOSUL" name="placa">

<!-- Cartão de crédito -->
<input data-mask="CARTAO" name="cartao">

<!-- Valores monetários (formato brasileiro) -->
<input data-decimal
       data-decimal-places="2"
       data-decimal-prefix="R$ "
       data-show-thousands="true"
       name="preco">
```

**Máscaras pré-definidas disponíveis:**
- CPF: `000.000.000-00`
- CNPJ: `00.000.000/0000-00`
- TELEFONE: `(00) 00000-0000`
- TELEFONE_FIXO: `(00) 0000-0000`
- CEP: `00000-000`
- DATA: `00/00/0000`
- HORA: `00:00`
- DATA_HORA: `00/00/0000 00:00`
- PLACA_ANTIGA: `AAA-0000`
- PLACA_MERCOSUL: `AAA-0A00`
- CARTAO: `0000 0000 0000 0000`
- CVV: `000`
- VALIDADE_CARTAO: `00/00`

### 🛡️ Tratamento de Erros Centralizado

Sistema de tratamento de erros de validação que garante consistência em toda aplicação:

```python
from util.exceptions import FormValidationError
from pydantic import ValidationError

@router.post("/cadastrar")
async def post_cadastrar(request: Request, email: str = Form(), senha: str = Form()):
    # Armazena dados do formulário para reexibição em caso de erro
    dados_formulario = {"email": email}

    try:
        dto = CadastroDTO(email=email, senha=senha)
        # lógica de negócio...

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="auth/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="senha"
        )
```

**O handler global automaticamente:**
- ✅ Processa os erros de validação
- ✅ Exibe mensagem flash ao usuário
- ✅ Renderiza o template com dados e erros
- ✅ Registra o erro nos logs

### ✅ Validadores Reutilizáveis

15+ validadores prontos em `dtos/validators.py`:

```python
from dtos.validators import (
    validar_email,
    validar_senha_forte,
    validar_cpf,
    validar_cnpj,
    validar_telefone_br,
    validar_cep,
    validar_data,
    validar_inteiro_positivo,
    validar_decimal_positivo
)

class ProdutoDTO(BaseModel):
    nome: str
    email: str
    cpf: str
    preco: float
    estoque: int

    _validar_email = field_validator('email')(validar_email())
    _validar_cpf = field_validator('cpf')(validar_cpf())
    _validar_preco = field_validator('preco')(validar_decimal_positivo())
    _validar_estoque = field_validator('estoque')(validar_inteiro_positivo())
```

**Validadores disponíveis:**
- **Texto**: `validar_string_obrigatoria()`, `validar_comprimento()`
- **Email**: `validar_email()`
- **Senha**: `validar_senha_forte()`, `validar_senhas_coincidem()`
- **Brasileiro**: `validar_cpf()`, `validar_cnpj()`, `validar_telefone_br()`, `validar_cep()`
- **Datas**: `validar_data()`, `validar_data_futura()`, `validar_data_passada()`
- **Números**: `validar_inteiro_positivo()`, `validar_decimal_positivo()`
- **Arquivos**: `validar_extensao_arquivo()`, `validar_tamanho_arquivo()`

### 📸 Sistema de Fotos de Perfil

Sistema completo de upload e crop de fotos em `util/foto_util.py`:

```python
from util.foto_util import (
    obter_caminho_foto_usuario,
    criar_foto_padrao_usuario,
    salvar_foto_cropada_usuario
)

# No template
<img src="{{ obter_caminho_foto_usuario(usuario.id) }}" alt="Foto">

# Criar foto padrão para novo usuário
criar_foto_padrao_usuario(usuario_id)

# Salvar foto cropada (recebida do frontend)
salvar_foto_cropada_usuario(usuario_id, base64_data)
```

**Funcionalidades:**
- Upload com drag & drop
- Crop interativo (Cropper.js)
- Redimensionamento automático (256px por padrão)
- Formato padronizado: `static/img/usuarios/{id:06d}.jpg`

### 🎨 28+ Temas Bootswatch Prontos

Acesse `/exemplos/bootswatch` para visualizar e escolher entre 28+ temas:

**Temas Claros**: Cerulean, Cosmo, Flatly, Journal, Litera, Lumen, Minty, Pulse, Sandstone, Simplex, Sketchy, United, Yeti, Zephyr, Brite, Morph, Quartz, Spacelab

**Temas Escuros**: Cyborg, Darkly, Slate, Solar, Superhero, Vapor

**Temas Únicos**: Lux, Materia, Original

Para trocar o tema, edite a linha do CSS no `base_publica.html` ou `base_privada.html`:
```html
<link rel="stylesheet" href="/static/css/bootswatch/flatly.bootstrap.min.css">
```

### 📋 Páginas de Exemplo (`/exemplos`)

9 exemplos completos e funcionais para você usar como referência:

1. **Form Fields Demo** - Todos os macros de formulário
2. **Cards Grid** - Grid responsivo com cards
3. **Table List** - Tabela de dados com ações e badges
4. **Product Detail** - Página de produto e-commerce
5. **Service Detail** - Página de serviço profissional
6. **Profile Detail** - Perfil de pessoa/profissional
7. **Property Detail** - Página de imóvel
8. **Bootswatch Themes** - Seletor interativo de temas
9. **Examples Index** - Galeria de todos os exemplos

Cada exemplo inclui:
- Código HTML completo
- Uso de componentes reutilizáveis
- Layout responsivo
- Boas práticas de UI/UX

### 🔔 Sistema de Notificações

**Flash Messages** (backend → frontend):
```python
from util.flash_messages import informar_sucesso, informar_erro, informar_aviso, informar_info

# Em qualquer rota
informar_sucesso(request, "Produto cadastrado com sucesso!")
informar_erro(request, "Erro ao processar pagamento.")
informar_aviso(request, "Seu plano expira em 3 dias.")
informar_info(request, "Nova atualização disponível.")
```

**Toast Programático** (JavaScript):
```javascript
// Exibir toast via JavaScript
window.exibirToast('Operação realizada!', 'success');
window.exibirToast('Atenção!', 'warning');
window.exibirToast('Erro ao salvar.', 'danger');
window.exibirToast('Informação importante.', 'info');
```

### 📝 Logger Profissional

Sistema de logs com rotação automática:

```python
from util.logger_config import logger

logger.info("Usuário realizou login")
logger.warning("Tentativa de acesso não autorizado")
logger.error("Falha ao conectar com API externa")
logger.debug("Variável X = 123")
```

**Características:**
- Logs diários: `logs/app.2025.10.20.log`
- Rotação automática à meia-noite
- Retenção configurável (padrão: 30 dias)
- Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Logs coloridos no console (desenvolvimento)

### 📧 Sistema de E-mail

Integrado com Resend.com para envio transacional:

```python
from util.email_service import enviar_email

# Email de boas-vindas
enviar_email_boas_vindas(usuario.email, usuario.nome)

# Email de recuperação de senha
enviar_email_recuperacao_senha(email, token)

# Email customizado
enviar_email(
    destinatario="user@example.com",
    assunto="Assunto do Email",
    corpo_html="<h1>Olá!</h1><p>Mensagem aqui</p>"
)
```

## 🛠️ Como Implementar Novas Funcionalidades

### Criando um Novo CRUD (Passo a Passo)

Exemplo: vamos criar um CRUD de **Produtos**

#### 1. Criar o Model (`model/produto_model.py`)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Produto:
    id: Optional[int]
    nome: str
    descricao: str
    preco: float
    estoque: int
    ativo: bool
    data_cadastro: Optional[datetime]
```

#### 2. Criar os SQLs (`sql/produto_sql.py`)

```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS produto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco REAL NOT NULL,
    estoque INTEGER NOT NULL DEFAULT 0,
    ativo INTEGER NOT NULL DEFAULT 1,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

INSERIR = """
INSERT INTO produto (nome, descricao, preco, estoque, ativo)
VALUES (?, ?, ?, ?, ?)
"""

OBTER_TODOS = "SELECT * FROM produto ORDER BY nome"

OBTER_POR_ID = "SELECT * FROM produto WHERE id = ?"

ATUALIZAR = """
UPDATE produto
SET nome = ?, descricao = ?, preco = ?, estoque = ?, ativo = ?
WHERE id = ?
"""

EXCLUIR = "DELETE FROM produto WHERE id = ?"
```

#### 3. Criar o Repository (`repo/produto_repo.py`)

```python
from typing import List, Optional
from model.produto_model import Produto
from sql.produto_sql import *
from util.db_util import get_connection

def _row_to_produto(row) -> Produto:
    """Converte linha do banco em objeto Produto"""
    return Produto(
        id=row["id"],
        nome=row["nome"],
        descricao=row["descricao"],
        preco=row["preco"],
        estoque=row["estoque"],
        ativo=bool(row["ativo"]),
        data_cadastro=row["data_cadastro"]
    )

def criar_tabela():
    """Cria a tabela de produtos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)

def inserir(produto: Produto) -> int:
    """Insere um novo produto e retorna o ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            produto.nome,
            produto.descricao,
            produto.preco,
            produto.estoque,
            1 if produto.ativo else 0
        ))
        return cursor.lastrowid

def obter_todos() -> List[Produto]:
    """Retorna todos os produtos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_produto(row) for row in cursor.fetchall()]

def obter_por_id(produto_id: int) -> Optional[Produto]:
    """Retorna um produto pelo ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (produto_id,))
        row = cursor.fetchone()
        return _row_to_produto(row) if row else None

def atualizar(produto: Produto):
    """Atualiza um produto"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            produto.nome,
            produto.descricao,
            produto.preco,
            produto.estoque,
            1 if produto.ativo else 0,
            produto.id
        ))

def excluir(produto_id: int):
    """Exclui um produto"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (produto_id,))
```

#### 4. Criar os DTOs (`dtos/produto_dto.py`)

```python
from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria, validar_decimal_positivo, validar_inteiro_positivo

class ProdutoCriarDTO(BaseModel):
    nome: str
    descricao: str
    preco: float
    estoque: int

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=3, tamanho_maximo=100)
    )
    _validar_preco = field_validator('preco')(validar_decimal_positivo())
    _validar_estoque = field_validator('estoque')(validar_inteiro_positivo())

class ProdutoAlterarDTO(BaseModel):
    nome: str
    descricao: str
    preco: float
    estoque: int
    ativo: bool

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=3, tamanho_maximo=100)
    )
    _validar_preco = field_validator('preco')(validar_decimal_positivo())
    _validar_estoque = field_validator('estoque')(validar_inteiro_positivo())
```

#### 5. Criar as Rotas (`routes/produto_routes.py`)

```python
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.exceptions import FormValidationError
from util.perfis import Perfil

import repo.produto_repo as produto_repo
from dtos.produto_dto import ProdutoCriarDTO, ProdutoAlterarDTO
from model.produto_model import Produto

router = APIRouter(prefix="/produtos")
templates = criar_templates("templates")

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: dict):
    produtos = produto_repo.obter_todos()
    return templates.TemplateResponse(
        "produtos/listar.html",
        {"request": request, "produtos": produtos}
    )

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def cadastrar_get(request: Request, usuario_logado: dict):
    return templates.TemplateResponse(
        "produtos/cadastrar.html",
        {"request": request}
    )

@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def cadastrar_post(
    request: Request,
    usuario_logado: dict,
    nome: str = Form(...),
    descricao: str = Form(...),
    preco: float = Form(...),
    estoque: int = Form(...)
):
    # Armazena dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque
    }

    try:
        # Validar com DTO
        dto = ProdutoCriarDTO(
            nome=nome,
            descricao=descricao,
            preco=preco,
            estoque=estoque
        )

        # Criar produto
        produto = Produto(
            id=None,
            nome=dto.nome,
            descricao=dto.descricao,
            preco=dto.preco,
            estoque=dto.estoque,
            ativo=True,
            data_cadastro=None
        )

        produto_repo.inserir(produto)
        informar_sucesso(request, "Produto cadastrado com sucesso!")
        return RedirectResponse("/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="produtos/cadastrar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
        )

@router.get("/editar/{produto_id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def editar_get(request: Request, produto_id: int, usuario_logado: dict):
    produto = produto_repo.obter_por_id(produto_id)
    if not produto:
        informar_erro(request, "Produto não encontrado.")
        return RedirectResponse("/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "produtos/editar.html",
        {"request": request, "produto": produto}
    )

@router.post("/editar/{produto_id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def editar_post(
    request: Request,
    produto_id: int,
    usuario_logado: dict,
    nome: str = Form(...),
    descricao: str = Form(...),
    preco: float = Form(...),
    estoque: int = Form(...),
    ativo: bool = Form(False)
):
    # Armazena dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "ativo": ativo
    }

    try:
        # Validar com DTO
        dto = ProdutoAlterarDTO(
            nome=nome,
            descricao=descricao,
            preco=preco,
            estoque=estoque,
            ativo=ativo
        )

        # Atualizar produto
        produto = Produto(
            id=produto_id,
            nome=dto.nome,
            descricao=dto.descricao,
            preco=dto.preco,
            estoque=dto.estoque,
            ativo=dto.ativo,
            data_cadastro=None
        )

        produto_repo.atualizar(produto)
        informar_sucesso(request, "Produto atualizado com sucesso!")
        return RedirectResponse("/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Adicionar produto aos dados para renderizar o formulário
        dados_formulario["produto"] = produto_repo.obter_por_id(produto_id)
        raise FormValidationError(
            validation_error=e,
            template_path="produtos/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
        )

@router.post("/excluir/{produto_id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def excluir(request: Request, produto_id: int, usuario_logado: dict):
    produto_repo.excluir(produto_id)
    informar_sucesso(request, "Produto excluído com sucesso!")
    return RedirectResponse("/produtos/listar", status_code=status.HTTP_303_SEE_OTHER)
```

#### 6. Criar os Templates

**`templates/produtos/listar.html`**:
```html
{% extends "base_privada.html" %}

{% block titulo %}Produtos{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-box-seam"></i> Produtos</h2>
            <a href="/produtos/cadastrar" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> Novo Produto
            </a>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                {% if produtos %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th>ID</th>
                                <th>Nome</th>
                                <th>Preço</th>
                                <th>Estoque</th>
                                <th>Status</th>
                                <th class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for produto in produtos %}
                            <tr>
                                <td>{{ produto.id }}</td>
                                <td>{{ produto.nome }}</td>
                                <td>R$ {{ "%.2f"|format(produto.preco) }}</td>
                                <td>{{ produto.estoque }}</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if produto.ativo else 'secondary' }}">
                                        {{ 'Ativo' if produto.ativo else 'Inativo' }}
                                    </span>
                                </td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm">
                                        <a href="/produtos/editar/{{ produto.id }}"
                                           class="btn btn-outline-primary">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger"
                                                onclick="excluirProduto({{ produto.id }}, '{{ produto.nome|replace("'", "\\'") }}')">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="alert alert-info text-center mb-0">
                    <i class="bi bi-info-circle"></i> Nenhum produto cadastrado.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

{% include 'components/modal_confirmacao.html' %}
{% endblock %}

{% block scripts %}
<script>
function excluirProduto(id, nome) {
    abrirModalConfirmacao({
        url: `/produtos/excluir/${id}`,
        mensagem: 'Tem certeza que deseja excluir este produto?',
        detalhes: `<div class="alert alert-warning"><strong>${nome}</strong></div>`
    });
}
</script>
{% endblock %}
```

**`templates/produtos/cadastrar.html`**:
```html
{% extends "base_privada.html" %}
{% from 'macros/form_fields.html' import input_text, input_decimal, textarea %}

{% block titulo %}Cadastrar Produto{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12 col-lg-8 offset-lg-2">
        <h2 class="mb-4"><i class="bi bi-plus-circle"></i> Cadastrar Produto</h2>

        <div class="card shadow-sm">
            <div class="card-body">
                <form method="POST" action="/produtos/cadastrar">
                    {{ input_text('nome', 'Nome do Produto', required=True,
                                  error=erros.get('nome'), value=dados.get('nome', '')) }}

                    {{ textarea('descricao', 'Descrição', rows=4,
                               error=erros.get('descricao'), value=dados.get('descricao', '')) }}

                    {{ input_decimal('preco', 'Preço', prefix='R$ ', decimal_places=2,
                                    required=True, error=erros.get('preco')) }}

                    {{ input_text('estoque', 'Estoque', type='number', required=True,
                                 error=erros.get('estoque'), value=dados.get('estoque', '0')) }}

                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Cadastrar
                        </button>
                        <a href="/produtos/listar" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### 7. Registrar no `main.py`

```python
# Importar o repositório
import repo.produto_repo as produto_repo

# Importar as rotas
from routes import produto_routes

# Criar tabela na inicialização
@app.on_event("startup")
async def startup():
    # ... outras tabelas
    produto_repo.criar_tabela()
    logger.info("Tabela 'produto' criada/verificada")

# Incluir o router
app.include_router(produto_routes.router)
logger.info("Router de produtos incluído")
```

### ✅ Pronto! Seu CRUD está completo

Acesse: `http://localhost:8400/produtos/listar`

## 📖 Estrutura do Projeto

```
DefaultWebApp/
├── data/                    # Dados seed em JSON
│   └── usuarios_seed.json
│
├── docs/                    # Documentação
│   ├── CRIAR_CRUD.md       # Tutorial CRUD detalhado
│   ├── PERFIS.md           # Como adicionar perfis
│   └── QUICK_START.md      # Início rápido
│
├── dtos/                    # DTOs Pydantic para validação
│   ├── validators.py       # ⭐ 15+ validadores reutilizáveis
│   ├── usuario_dto.py
│   └── login_dto.py
│
├── model/                   # Modelos de entidades (dataclasses)
│   ├── usuario_model.py
│   └── configuracao_model.py
│
├── repo/                    # Repositórios de acesso a dados
│   ├── usuario_repo.py
│   └── configuracao_repo.py
│
├── routes/                  # Rotas organizadas por módulo
│   ├── auth_routes.py
│   ├── perfil_routes.py
│   ├── usuario_routes.py
│   ├── tarefas_routes.py
│   ├── admin_usuarios_routes.py
│   ├── admin_configuracoes_routes.py
│   ├── public_routes.py
│   └── examples_routes.py  # ⭐ 9 exemplos práticos
│
├── sql/                     # Comandos SQL
│   ├── usuario_sql.py
│   └── configuracao_sql.py
│
├── static/                  # Arquivos estáticos
│   ├── css/
│   │   ├── bootstrap.min.css
│   │   ├── bootswatch/     # ⭐ 28+ temas prontos
│   │   └── custom.css
│   ├── js/
│   │   ├── toasts.js       # ⭐ Sistema de notificações
│   │   ├── input-mask.js   # ⭐ Máscaras automáticas
│   │   ├── image-cropper.js
│   │   ├── password-validator.js
│   │   └── perfil-photo-handler.js
│   └── img/
│       └── usuarios/        # Fotos de perfil
│
├── templates/               # Templates Jinja2
│   ├── base_publica.html   # Base para páginas públicas
│   ├── base_privada.html   # Base para páginas autenticadas
│   ├── auth/               # Login, cadastro, recuperação
│   ├── perfil/             # Perfil do usuário
│   ├── tarefas/            # Exemplo CRUD
│   ├── admin/              # Área administrativa
│   │   ├── usuarios/
│   │   └── configuracoes/
│   ├── components/         # ⭐ Componentes reutilizáveis
│   │   ├── modal_confirmacao.html
│   │   ├── modal_corte_imagem.html
│   │   └── galeria_fotos.html
│   ├── macros/             # ⭐ Macros de formulário
│   │   └── form_fields.html
│   ├── exemplos/           # ⭐ 9 páginas de exemplo
│   │   ├── index.html
│   │   ├── demo_campos_formulario.html
│   │   ├── grade_cartoes.html
│   │   ├── lista_tabela.html
│   │   ├── bootswatch.html
│   │   ├── detalhes_produto.html
│   │   ├── detalhes_servico.html
│   │   ├── detalhes_perfil.html
│   │   └── detalhes_imovel.html
│   └── errors/             # Páginas de erro
│       ├── 404.html
│       └── 500.html
│
├── util/                    # Utilitários
│   ├── auth_decorator.py   # ⭐ Decorator de autenticação
│   ├── perfis.py           # ⭐ Enum de perfis
│   ├── db_util.py          # Gerenciamento de conexão
│   ├── security.py         # Hash de senhas
│   ├── senha_util.py       # Validação de senha forte
│   ├── email_service.py    # Envio de emails
│   ├── foto_util.py        # ⭐ Sistema de fotos
│   ├── exceptions.py       # ⭐ Exceções customizadas
│   ├── exception_handlers.py # ⭐ Handlers globais de exceções
│   ├── validation_util.py  # ⭐ Processamento de erros de validação
│   ├── flash_messages.py   # ⭐ Flash messages
│   ├── logger_config.py    # ⭐ Logger profissional
│   ├── template_util.py    # Helpers de templates
│   ├── config.py           # Configurações
│   ├── config_cache.py     # Cache de configurações
│   ├── seed_data.py        # Carregamento de seeds
│   └── security_headers.py
│
├── tests/                   # Testes automatizados
│   ├── conftest.py         # Fixtures do pytest
│   └── test_*.py
│
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore
├── CLAUDE.md                # ⭐ Documentação técnica completa
├── main.py                  # Arquivo principal
├── requirements.txt
└── README.md                # Este arquivo
```

## 🔧 Tecnologias Utilizadas

### Backend
- **FastAPI 0.115+** - Framework web moderno e rápido
- **Uvicorn** - Servidor ASGI de alta performance
- **Pydantic 2.0+** - Validação de dados com type hints
- **Passlib + Bcrypt** - Hash de senhas seguro

### Frontend
- **Jinja2** - Engine de templates
- **Bootstrap 5.3.8** - Framework CSS responsivo
- **Bootstrap Icons** - Biblioteca de ícones
- **Bootswatch** - 28+ temas prontos
- **JavaScript vanilla** - Sem dependências frontend pesadas
- **Cropper.js** - Crop de imagens

### Banco de Dados
- **SQLite3** - Banco de dados embutido
- **SQL Puro** - Sem ORM para máximo controle

### Comunicação
- **Resend** - Envio de e-mails transacionais
- **Requests** - Cliente HTTP

### Desenvolvimento
- **Python-dotenv** - Gerenciamento de variáveis de ambiente
- **Pytest** - Framework de testes
- **Logging** - Sistema de logs profissional

## ⚙️ Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```env
# Banco de Dados
DATABASE_PATH=database.db

# Aplicação
APP_NAME=DefaultWebApp
SECRET_KEY=sua_chave_secreta_super_segura_aqui
BASE_URL=http://localhost:8400

# Servidor
HOST=0.0.0.0
PORT=8400
RELOAD=True
RUNNING_MODE=Development

# Logging
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30

# E-mail (Resend.com)
RESEND_API_KEY=seu_api_key_aqui
RESEND_FROM_EMAIL=noreply@seudominio.com
RESEND_FROM_NAME=Sistema

# Fotos
FOTO_PERFIL_TAMANHO_MAX=256
```

## 🧪 Testes

Execute os testes com pytest:

```bash
# Todos os testes
pytest

# Com verbose
pytest -v

# Teste específico
pytest tests/test_auth.py

# Por marcador
pytest -m auth
pytest -m crud

# Com cobertura
pytest --cov=. --cov-report=html
```

## 📚 Documentação Adicional

- **[CLAUDE.md](CLAUDE.md)** - Documentação técnica completa para desenvolvedores
- **[docs/CRIAR_CRUD.md](docs/CRIAR_CRUD.md)** - Tutorial detalhado para criar CRUDs
- **[docs/PERFIS.md](docs/PERFIS.md)** - Como adicionar novos perfis de usuário
- **[docs/QUICK_START.md](docs/QUICK_START.md)** - Guia de início rápido
- **[/exemplos](http://localhost:8400/exemplos)** - 9 exemplos práticos funcionais

## 🔒 Segurança

### Implementações Atuais
✅ Senhas com hash bcrypt
✅ Sessões com chave secreta
✅ Rate limiting no login
✅ Validação de força de senha
✅ Security headers (X-Frame-Options, etc.)
✅ Proteção contra SQL injection (prepared statements)
✅ Validação de dados com Pydantic
✅ XSS protection via Jinja2 auto-escaping

### Checklist para Produção
- [ ] Alterar `SECRET_KEY` para valor único e seguro
- [ ] Alterar senhas padrão dos usuários
- [ ] Configurar HTTPS/SSL
- [ ] Configurar firewall
- [ ] Backup regular do banco de dados
- [ ] Monitoramento de logs
- [ ] Limitar tentativas de login por IP
- [ ] Configurar CSRF tokens
- [ ] Adicionar controle de acesso a fotos de perfil

## 🚀 Próximos Passos

Após instalar e explorar o projeto:

1. **Explore os exemplos**: Acesse `/exemplos` para ver todos os componentes em ação
2. **Leia o CLAUDE.md**: Documentação técnica completa do projeto
3. **Crie seu primeiro CRUD**: Siga o tutorial em `docs/CRIAR_CRUD.md`
4. **Customize o tema**: Escolha um tema em `/exemplos/bootswatch`
5. **Adicione suas funcionalidades**: Use os componentes reutilizáveis
6. **Configure o email**: Obtenha API key gratuita em [resend.com](https://resend.com)
7. **Execute os testes**: Garanta que tudo está funcionando

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é um boilerplate educacional livre para uso.

## 💬 Suporte

Para dúvidas e suporte:
- Consulte a documentação em `/docs` e `CLAUDE.md`
- Explore os exemplos em `/exemplos`
- Verifique os exemplos no código
- Abra uma issue no GitHub

## 🎯 Roadmap

### Em Desenvolvimento
- [ ] Docker e docker-compose
- [ ] CI/CD com GitHub Actions
- [ ] Paginação de listagens
- [ ] Filtros e busca avançada
- [ ] Exportação de dados (CSV, Excel)

### Futuras Melhorias
- [ ] API REST endpoints
- [ ] Documentação automática (Swagger/OpenAPI)
- [ ] Internacionalização (i18n)
- [ ] Theme switcher persistente
- [ ] WebSockets para notificações real-time
- [ ] Upload de múltiplos arquivos
- [ ] Dashboard com gráficos

---

**Desenvolvido com 💙 para acelerar o desenvolvimento de aplicações web com Python e FastAPI**

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**
