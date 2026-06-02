# Exemplo Completo: CRUD com Relacionamento (Produto → Categoria + Usuário)

Gabarito de um CRUD **inteiro** gerado de ponta a ponta. Entidade `Produto`:
- campos escalares: `nome` (str), `descricao` (str), `preco` (float), `estoque` (int), `ativo` (bool)
- enum: `StatusProduto` = Ativo, Inativo, Esgotado
- **FK de referência**: `categoria_id` (escolhida num dropdown) → entidade `Categoria`
- **FK de propriedade**: `usuario_id` (dono, da sessão)

> Pressuposto: já existe um CRUD de `Categoria` (entidade simples: `id`, `nome`, `descricao`).
> Se não existir, gere-o primeiro (é um CRUD sem relacionamentos) e só então o de `Produto`.

---

## 1. `model/produto_model.py`

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from util.enum_base import EnumEntidade


class StatusProduto(EnumEntidade):
    """Status do produto."""
    ATIVO = "Ativo"
    INATIVO = "Inativo"
    ESGOTADO = "Esgotado"


@dataclass
class Produto:
    """Produto do catálogo, pertencente a uma categoria e a um usuário."""
    id: int
    nome: str
    descricao: str
    preco: float = 0.0
    estoque: int = 0
    ativo: bool = False
    status: StatusProduto = StatusProduto.ATIVO
    categoria_id: int = 0          # FK de referência
    usuario_id: int = 0            # FK de propriedade
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    # Campos de JOIN (apenas exibição)
    categoria_nome: Optional[str] = None
    usuario_nome: Optional[str] = None
```

## 2. `sql/produto_sql.py`

```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS produto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    preco REAL NOT NULL DEFAULT 0,
    estoque INTEGER NOT NULL DEFAULT 0,
    ativo INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'Ativo',
    categoria_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categoria(id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

INSERIR = """
INSERT INTO produto (nome, descricao, preco, estoque, ativo, status, categoria_id, usuario_id)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT p.*, c.nome as categoria_nome, u.nome as usuario_nome
FROM produto p
INNER JOIN categoria c ON p.categoria_id = c.id
INNER JOIN usuario u ON p.usuario_id = u.id
ORDER BY p.data_criacao DESC
"""

OBTER_POR_ID = """
SELECT p.*, c.nome as categoria_nome, u.nome as usuario_nome
FROM produto p
INNER JOIN categoria c ON p.categoria_id = c.id
INNER JOIN usuario u ON p.usuario_id = u.id
WHERE p.id = ?
"""

OBTER_POR_CATEGORIA = """
SELECT p.*, c.nome as categoria_nome, u.nome as usuario_nome
FROM produto p
INNER JOIN categoria c ON p.categoria_id = c.id
INNER JOIN usuario u ON p.usuario_id = u.id
WHERE p.categoria_id = ?
ORDER BY p.data_criacao DESC
"""

ATUALIZAR = """
UPDATE produto
SET nome = ?, descricao = ?, preco = ?, estoque = ?, ativo = ?, status = ?, categoria_id = ?,
    data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

EXCLUIR = "DELETE FROM produto WHERE id = ?"
```

## 3. `repo/produto_repo.py`

```python
"""Repositório de Produto."""

import sqlite3
from typing import Optional, Type, TypeVar

from model.produto_model import Produto, StatusProduto
from sql.produto_sql import (
    CRIAR_TABELA, INSERIR, OBTER_TODOS, OBTER_POR_ID,
    OBTER_POR_CATEGORIA, ATUALIZAR, EXCLUIR,
)
from util.db_util import obter_conexao
from util.logger_config import logger

T = TypeVar("T")


def _converter_enum_seguro(valor: str, tipo_enum: Type[T], padrao: T) -> T:
    try:
        return tipo_enum(valor)
    except ValueError:
        logger.error(f"Valor inválido para {tipo_enum.__name__}: '{valor}'. Usando padrão.")
        return padrao


def _row_to_produto(row: sqlite3.Row) -> Produto:
    categoria_nome = row["categoria_nome"] if "categoria_nome" in row.keys() else None
    usuario_nome = row["usuario_nome"] if "usuario_nome" in row.keys() else None
    return Produto(
        id=row["id"],
        nome=row["nome"],
        descricao=row["descricao"],
        preco=row["preco"],
        estoque=row["estoque"],
        ativo=bool(row["ativo"]),
        status=_converter_enum_seguro(row["status"], StatusProduto, StatusProduto.ATIVO),
        categoria_id=row["categoria_id"],
        usuario_id=row["usuario_id"],
        data_criacao=row["data_criacao"],
        data_atualizacao=row["data_atualizacao"],
        categoria_nome=categoria_nome,
        usuario_nome=usuario_nome,
    )


def criar_tabela() -> bool:
    with obter_conexao() as conn:
        conn.cursor().execute(CRIAR_TABELA)
        return True


def inserir(produto: Produto) -> Optional[int]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            produto.nome, produto.descricao, produto.preco, produto.estoque,
            1 if produto.ativo else 0, produto.status.value,
            produto.categoria_id, produto.usuario_id,
        ))
        return cursor.lastrowid


def obter_todos() -> list[Produto]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_produto(r) for r in cursor.fetchall()]


def obter_por_id(id: int) -> Optional[Produto]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        return _row_to_produto(row) if row else None


def obter_por_categoria(categoria_id: int) -> list[Produto]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_CATEGORIA, (categoria_id,))
        return [_row_to_produto(r) for r in cursor.fetchall()]


def atualizar(produto: Produto) -> bool:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            produto.nome, produto.descricao, produto.preco, produto.estoque,
            1 if produto.ativo else 0, produto.status.value, produto.categoria_id,
            produto.id,
        ))
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0
```

## 4. `dtos/produto_dto.py`

```python
from pydantic import BaseModel, Field, field_validator
from dtos.validators import validar_string_obrigatoria, validar_tipo, validar_id_positivo
from model.produto_model import StatusProduto


class CriarProdutoDTO(BaseModel):
    nome: str = Field(..., description="Nome do produto")
    descricao: str = Field(..., description="Descrição")
    preco: float = Field(..., gt=0, description="Preço")
    estoque: int = Field(..., ge=0, description="Estoque")
    ativo: bool = Field(default=False, description="Ativo")
    status: str = Field(default="Ativo", description="Status")
    categoria_id: int = Field(..., gt=0, description="Categoria")

    _v_nome = field_validator("nome")(
        validar_string_obrigatoria(nome_campo="Nome", tamanho_minimo=3, tamanho_maximo=200))
    _v_descricao = field_validator("descricao")(
        validar_string_obrigatoria(nome_campo="Descrição", tamanho_minimo=10, tamanho_maximo=2000))
    _v_status = field_validator("status")(validar_tipo("Status", StatusProduto))
    _v_categoria = field_validator("categoria_id")(validar_id_positivo(nome_campo="Categoria"))


class AlterarProdutoDTO(CriarProdutoDTO):
    status: str = Field(..., description="Status")   # obrigatório na alteração
```

## 5. Índices — adicionar em `sql/indices_sql.py`

```python
# Índices da tabela produto
CRIAR_INDICE_PRODUTO_CATEGORIA = """
CREATE INDEX IF NOT EXISTS idx_produto_categoria_id ON produto(categoria_id)
"""
CRIAR_INDICE_PRODUTO_USUARIO = """
CREATE INDEX IF NOT EXISTS idx_produto_usuario_id ON produto(usuario_id)
"""
CRIAR_INDICE_PRODUTO_STATUS = """
CREATE INDEX IF NOT EXISTS idx_produto_status ON produto(status)
"""

TODOS_INDICES = [
    # ...existentes...
    CRIAR_INDICE_PRODUTO_CATEGORIA,
    CRIAR_INDICE_PRODUTO_USUARIO,
    CRIAR_INDICE_PRODUTO_STATUS,
]
```

## 6. `routes/admin_produto_routes.py`

Note o `import status as http_status` por causa do campo `status` do produto.

```python
"""Rotas administrativas para gerenciamento de Produto."""

from typing import Optional

from fastapi import APIRouter, Form, Request
from fastapi import status as http_status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.produto_dto import CriarProdutoDTO, AlterarProdutoDTO
from model.produto_model import Produto, StatusProduto
from model.usuario_logado_model import UsuarioLogado
from repo import produto_repo, categoria_repo

from util.auth_decorator import requer_autenticacao
from util.exceptions import ErroValidacaoFormulario
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.repository_helpers import obter_ou_404
from util.template_util import criar_templates

router = APIRouter(prefix="/admin/produtos")
templates = criar_templates()

produto_limiter = DynamicRateLimiter(
    chave_max="rate_limit_admin_produto_max",
    chave_minutos="rate_limit_admin_produto_minutos",
    padrao_max=30, padrao_minutos=1, nome="admin_produto",
)

REDIR_LISTAR = "/admin/produtos/listar"


def _normalizar_decimal(valor: str) -> str:
    valor = (valor or "").strip().replace("R$", "").replace(" ", "")
    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")
    return valor or "0"


def _opcoes_formulario() -> dict:
    return {
        "categorias": categoria_repo.obter_todos(),
        "status_valores": StatusProduto.valores(),
    }


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    assert usuario_logado is not None
    produtos = produto_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/produto/listar.html",
        {"request": request, "produtos": produtos, "usuario_logado": usuario_logado},
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    assert usuario_logado is not None
    return templates.TemplateResponse(
        "admin/produto/cadastrar.html",
        {"request": request, "usuario_logado": usuario_logado, **_opcoes_formulario()},
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(...),
    preco: str = Form(...),
    estoque: int = Form(0),
    ativo: bool = Form(False),
    status: str = Form("Ativo"),
    categoria_id: int = Form(...),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    assert usuario_logado is not None

    ip = obter_identificador_cliente(request)
    if not produto_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento.")
        return RedirectResponse(REDIR_LISTAR, status_code=http_status.HTTP_303_SEE_OTHER)

    dados_formulario: dict = {
        "nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque,
        "ativo": ativo, "status": status, "categoria_id": categoria_id,
    }
    try:
        dto = CriarProdutoDTO(
            nome=nome, descricao=descricao, preco=float(_normalizar_decimal(preco)),
            estoque=estoque, ativo=ativo, status=status, categoria_id=categoria_id,
        )
        novo = Produto(
            id=0, nome=dto.nome, descricao=dto.descricao, preco=dto.preco, estoque=dto.estoque,
            ativo=dto.ativo, status=StatusProduto(dto.status), categoria_id=dto.categoria_id,
            usuario_id=usuario_logado.id,
        )
        id_criado = produto_repo.inserir(novo)
        if id_criado:
            informar_sucesso(request, "Produto cadastrado com sucesso!")
            logger.info(f"Produto #{id_criado} criado por admin {usuario_logado.id}")
        else:
            informar_erro(request, "Erro ao cadastrar produto.")
    except ValidationError as e:
        dados_formulario.update(_opcoes_formulario())
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/produto/cadastrar.html",
            dados_formulario=dados_formulario,
        )
    return RedirectResponse(REDIR_LISTAR, status_code=http_status.HTTP_303_SEE_OTHER)


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    assert usuario_logado is not None
    item = obter_ou_404(produto_repo.obter_por_id(id), request, "Produto não encontrado", REDIR_LISTAR)
    if isinstance(item, RedirectResponse):
        return item
    dados = item.__dict__.copy()
    return templates.TemplateResponse(
        "admin/produto/editar.html",
        {"request": request, "produto": item, "dados": dados,
         "usuario_logado": usuario_logado, **_opcoes_formulario()},
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    descricao: str = Form(...),
    preco: str = Form(...),
    estoque: int = Form(0),
    ativo: bool = Form(False),
    status: str = Form(...),
    categoria_id: int = Form(...),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    assert usuario_logado is not None

    ip = obter_identificador_cliente(request)
    if not produto_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento.")
        return RedirectResponse(REDIR_LISTAR, status_code=http_status.HTTP_303_SEE_OTHER)

    item = obter_ou_404(produto_repo.obter_por_id(id), request, "Produto não encontrado", REDIR_LISTAR)
    if isinstance(item, RedirectResponse):
        return item

    dados_formulario: dict = {
        "id": id, "nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque,
        "ativo": ativo, "status": status, "categoria_id": categoria_id,
    }
    try:
        dto = AlterarProdutoDTO(
            nome=nome, descricao=descricao, preco=float(_normalizar_decimal(preco)),
            estoque=estoque, ativo=ativo, status=status, categoria_id=categoria_id,
        )
        atualizado = Produto(
            id=id, nome=dto.nome, descricao=dto.descricao, preco=dto.preco, estoque=dto.estoque,
            ativo=dto.ativo, status=StatusProduto(dto.status), categoria_id=dto.categoria_id,
            usuario_id=item.usuario_id,
        )
        if produto_repo.atualizar(atualizado):
            informar_sucesso(request, "Produto atualizado com sucesso!")
            logger.info(f"Produto #{id} alterado por admin {usuario_logado.id}")
        else:
            informar_erro(request, "Erro ao atualizar produto.")
    except ValidationError as e:
        dados_formulario["produto"] = item
        dados_formulario.update(_opcoes_formulario())
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/produto/editar.html",
            dados_formulario=dados_formulario,
        )
    return RedirectResponse(REDIR_LISTAR, status_code=http_status.HTTP_303_SEE_OTHER)


@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    assert usuario_logado is not None
    if produto_repo.excluir(id):
        informar_sucesso(request, "Produto excluído com sucesso!")
        logger.info(f"Produto #{id} excluído por admin {usuario_logado.id}")
    else:
        informar_erro(request, "Erro ao excluir produto.")
    return RedirectResponse(REDIR_LISTAR, status_code=http_status.HTTP_303_SEE_OTHER)
```

## 7. Templates

### `templates/admin/produto/listar.html`

```html
{% extends "base_privada.html" %}
{% from 'macros/action_buttons.html' import btn_group_crud %}
{% from 'macros/empty_states.html' import empty_state %}

{% block titulo %}Gerenciar Produtos{% endblock %}

{% block content %}
<div class="row"><div class="col-12">
  <div class="d-flex justify-content-between align-items-center mb-4">
    <h2><i class="bi bi-box"></i> Gerenciar Produtos</h2>
    <a href="/admin/produtos/cadastrar" class="btn btn-primary"><i class="bi bi-plus-circle"></i> Novo Produto</a>
  </div>
  <div class="card shadow-sm"><div class="card-body p-0">
    {% if produtos %}
    <div class="table-responsive">
      <table class="table table-hover align-middle mb-0">
        <thead class="table-light"><tr>
          <th>#</th><th>Nome</th><th>Categoria</th><th>Preço</th><th>Estoque</th><th>Status</th>
          <th class="text-center">Ações</th>
        </tr></thead>
        <tbody>
          {% for item in produtos %}
          <tr>
            <td>{{ item.id }}</td>
            <td>{{ item.nome }}</td>
            <td>{{ item.categoria_nome }}</td>
            <td>R$ {{ "%.2f"|format(item.preco) }}</td>
            <td>{{ item.estoque }}</td>
            <td><span class="badge bg-secondary">{{ item.status }}</span></td>
            <td class="text-center">
              {{ btn_group_crud(
                item.id, item.nome, '/admin/produtos',
                "confirmarExclusao(" ~ item.id ~ ", '" ~ item.nome|replace("'", "\\'") ~ "')"
              ) }}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
    <div class="p-4">
      {{ empty_state('Nenhum produto cadastrado', 'Comece cadastrando o primeiro produto.',
        action_url='/admin/produtos/cadastrar', action_text='Cadastrar Primeiro Produto',
        icon='box', variant='info') }}
    </div>
    {% endif %}
  </div></div>
</div></div>
{% include 'components/modal_confirmacao.html' %}
{% endblock %}

{% block scripts %}
<script>
function confirmarExclusao(id, nome) {
  abrirModalConfirmacao({ url: `/admin/produtos/excluir/${id}`, mensagem: `Tem certeza que deseja excluir "${nome}"?` });
}
</script>
{% endblock %}
```

### `templates/admin/produto/cadastrar.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Cadastrar Produto{% endblock %}

{% block content %}
<div class="row justify-content-center"><div class="col-lg-8">
  <div class="d-flex align-items-center mb-4">
    <h2 class="mb-0"><i class="bi bi-plus-circle"></i> Cadastrar Produto</h2>
  </div>
  <div class="card shadow-sm">
    <form method="POST" action="/admin/produtos/cadastrar">
      {{ csrf_input(request) }}
      <div class="card-body p-4"><div class="row">
        <div class="col-12">{% include "components/alerta_erro.html" %}</div>

        <div class="col-12 mb-3">{{ field(name='nome', label='Nome', type='text', required=true) }}</div>
        <div class="col-12 mb-3">{{ field(name='descricao', label='Descrição', type='textarea', required=true) }}</div>
        <div class="col-md-6 mb-3">{{ field(name='preco', label='Preço', type='decimal', required=true, decimal_prefix='R$ ') }}</div>
        <div class="col-md-6 mb-3">{{ field(name='estoque', label='Estoque', type='number', required=true) }}</div>

        <div class="col-md-6 mb-3">
          {% set status_opcoes = {} %}
          {% for s in status_valores %}{% set _ = status_opcoes.update({s: s}) %}{% endfor %}
          {{ field(name='status', label='Status', type='select', required=true, options=status_opcoes) }}
        </div>

        <div class="col-md-6 mb-3">
          {% set categoria_opcoes = {} %}
          {% for c in categorias %}{% set _ = categoria_opcoes.update({c.id: c.nome}) %}{% endfor %}
          {{ field(name='categoria_id', label='Categoria', type='select', required=true, options=categoria_opcoes) }}
        </div>

        <div class="col-12 mb-3">{{ field(name='ativo', label='Produto ativo', type='checkbox') }}</div>
      </div></div>
      <div class="card-footer p-4"><div class="d-flex gap-3">
        <button type="submit" class="btn btn-primary"><i class="bi bi-check-circle"></i> Cadastrar</button>
        <a href="/admin/produtos/listar" class="btn btn-secondary"><i class="bi bi-x-circle"></i> Cancelar</a>
      </div></div>
    </form>
  </div>
</div></div>
{% endblock %}
```

### `templates/admin/produto/editar.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Alterar Produto{% endblock %}

{% block content %}
<div class="row justify-content-center"><div class="col-lg-8">
  <div class="d-flex align-items-center mb-4">
    <h2 class="mb-0"><i class="bi bi-pencil"></i> Alterar Produto</h2>
  </div>
  <div class="card shadow-sm">
    <form method="POST" action="/admin/produtos/editar/{{ dados.id if dados.id is defined else produto.id }}">
      {{ csrf_input(request) }}
      <div class="card-body p-4"><div class="row">
        <div class="col-12">{% include "components/alerta_erro.html" %}</div>

        <div class="col-12 mb-3">{{ field(name='nome', label='Nome', type='text', required=true, value=dados.nome) }}</div>
        <div class="col-12 mb-3">{{ field(name='descricao', label='Descrição', type='textarea', required=true, value=dados.descricao) }}</div>
        <div class="col-md-6 mb-3">{{ field(name='preco', label='Preço', type='decimal', required=true, decimal_prefix='R$ ', value=dados.preco) }}</div>
        <div class="col-md-6 mb-3">{{ field(name='estoque', label='Estoque', type='number', required=true, value=dados.estoque) }}</div>

        <div class="col-md-6 mb-3">
          {% set status_opcoes = {} %}
          {% for s in status_valores %}{% set _ = status_opcoes.update({s: s}) %}{% endfor %}
          {{ field(name='status', label='Status', type='select', required=true, options=status_opcoes, value=dados.status) }}
        </div>

        <div class="col-md-6 mb-3">
          {% set categoria_opcoes = {} %}
          {% for c in categorias %}{% set _ = categoria_opcoes.update({c.id: c.nome}) %}{% endfor %}
          {{ field(name='categoria_id', label='Categoria', type='select', required=true, options=categoria_opcoes, value=dados.categoria_id) }}
        </div>

        <div class="col-12 mb-3">{{ field(name='ativo', label='Produto ativo', type='checkbox', value=dados.ativo) }}</div>
      </div></div>
      <div class="card-footer p-4"><div class="d-flex gap-3">
        <button type="submit" class="btn btn-primary"><i class="bi bi-check-circle"></i> Salvar Alterações</button>
        <a href="/admin/produtos/listar" class="btn btn-secondary"><i class="bi bi-x-circle"></i> Cancelar</a>
      </div></div>
    </form>
  </div>
</div></div>
{% endblock %}
```

## 8. `main.py` — registros

```python
# imports
from repo import produto_repo            # (categoria_repo já importado)
from routes.admin_produto_routes import router as admin_produto_router

# TABELAS — categoria ANTES de produto (FK)
TABELAS = [
    (usuario_repo, "usuario"),
    (categoria_repo, "categoria"),       # referenciada primeiro
    # ...
    (produto_repo, "produto"),           # referencia categoria e usuario
]

# ROUTERS — admin no meio, public/examples por último
ROUTERS = [
    # ...
    (admin_produto_router, ["Admin - Produtos"], "admin de produtos"),
    # ...
    (public_router, ["Público"], "público"),
    (examples_router, ["Exemplos"], "exemplos"),
]
```

## 9. Navbar — `templates/base_privada.html`

```html
<li class="nav-item">
  <a class="nav-link {{ 'active' if '/admin/produtos/' in request.path else '' }}"
     href="/admin/produtos/listar"
     {{ 'aria-current=page' if '/admin/produtos/' in request.path else '' }}>Produtos</a>
</li>
```
