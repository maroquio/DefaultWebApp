---
name: crud-generator
description: |
  Gera um CRUD administrativo completo e funcional de ponta a ponta no DefaultWebApp,
  seguindo todos os padrões arquiteturais do projeto (Model, SQL, Repository, DTO, Índices,
  Routes, Templates, registro em main.py e navbar). Suporta entidades simples E entidades
  com relacionamentos (chave estrangeira para usuário ou para outras entidades, seleção via
  dropdown, e relações mestre-detalhe 1:N).
  Use esta skill sempre que o usuário quiser criar um novo CRUD, scaffold, formulário de
  cadastro/edição/exclusão, gerenciar entidades, adicionar uma nova feature com CRUD admin,
  ou quando menções a entidades como "produtos", "categorias", "pedidos", "serviços",
  "clientes", "fornecedores" sugerirem a necessidade de uma área administrativa de gerenciamento.
  Também deve ser usada quando o usuário disser "gerar CRUD", "criar CRUD", "scaffold",
  "criar entidade", "adicionar módulo", "nova tela de cadastro", ou descrever uma entidade
  que se relaciona com outra ("um produto tem uma categoria", "um pedido pertence a um cliente").
---

# Gerador de CRUD Administrativo

Gera **todas** as camadas de um CRUD administrativo completo e funcional no DefaultWebApp,
seguindo fielmente os padrões existentes — incluindo entidades que se **relacionam** com outras.

**Princípio central:** não invente padrões. A aplicação inteira segue convenções rígidas.
Toda decisão deve espelhar o que já existe em `usuario_repo`, `chamado_repo`,
`admin_usuarios_routes.py` e nos templates de `admin/usuarios/`. Quando em dúvida sobre um
padrão real, **leia o arquivo correspondente do projeto** antes de gerar — não confie só na memória.

## Visão Geral do Fluxo

```
1. Coletar a especificação completa (campos + relacionamentos)  ← NÃO PULE
2. Classificar cada campo (escalar / enum / FK-propriedade / FK-referência / decimal / computado)
3. Gerar arquivos na ordem obrigatória (dependências entre camadas)
4. Registrar em main.py (TABELAS na ordem de dependência de FK + ROUTERS)
5. Adicionar índices das FKs
6. Adicionar link na navbar
7. Verificar (import + criação de tabela + smoke test)
```

---

## Fase 1 — Coletar a Especificação Completa

Antes de gerar **qualquer** arquivo, confirme a especificação. Se o usuário já forneceu tudo,
apenas reafirme o entendimento em 2-3 linhas e prossiga. Se faltar informação, pergunte.

Colete:

1. **Nome da entidade** (singular, em português): ex: `produto`, `categoria`, `pedido`.
   Derive o **plural** para URLs/navbar (ex: `produtos`, `categorias`, `pedidos`).
2. **Campos escalares com tipos**: formato `nome:tipo` — tipos: `str`, `int`, `float`, `Decimal`, `bool`, `date`, `datetime`.
3. **Enums de domínio**: status/tipos/categorias internas e seus valores (ex: `StatusPedido = Pendente, Pago, Enviado`).
4. **Relacionamentos** (CRÍTICO — veja "Cookbook de Relacionamentos"):
   - **Pertence a um usuário?** (FK de propriedade `usuario_id`, vindo da sessão)
   - **Pertence a outra entidade?** (FK de referência, ex: `produto` → `categoria`; escolhida num dropdown).
     Para cada uma, pergunte: nome da entidade relacionada, e qual campo dela exibir (ex: `nome`).
   - **Possui muitos filhos?** (relação 1:N mestre-detalhe, estilo `chamado` → `chamado_interacao`).
5. **Apenas admin?** (padrão sim, prefixo `/admin/`) ou também rotas de usuário comum.
6. **Ícone Bootstrap** para navbar/títulos (ex: `bi-box`, `bi-tag`, `bi-cart`).

**Padrões sensatos quando não especificado:**
- CRUD apenas admin (prefixo `/admin/{plural}`).
- Sem `usuario_id` a menos que mencionado.
- Sem enum de status a menos que mencionado (CRUD pode ser totalmente sem enum).
- Ícone padrão: `bi-database`.

---

## Conceito-Chave: Classifique Cada Campo

Cada campo da entidade cai em **uma** destas categorias. A categoria determina como ele aparece
em cada camada. **Faça essa classificação mentalmente antes de gerar.**

| Categoria | Exemplo | Model | SQL | DTO | Form |
|-----------|---------|-------|-----|-----|------|
| **Escalar** | `nome:str`, `estoque:int` | tipo nativo | TEXT/INTEGER/REAL | `Field(...)` + validator | input text/number |
| **Decimal/moeda** | `preco:float`, `valor:Decimal` | `float`/`Decimal` | REAL | `Field(..., gt=0)` | `type='decimal'` (ver §Decimais) |
| **Booleano** | `ativo:bool` | `bool = False` | INTEGER DEFAULT 0 | `bool` (opcional) | `type='checkbox'` |
| **Enum** | `status:StatusX` | tipo Enum (`EnumEntidade`) | TEXT DEFAULT | `str` + `validar_tipo` | `type='select'` (dict) |
| **FK de propriedade** | `usuario_id` (da sessão) | `usuario_id:int` + `usuario_nome:Optional[str]` | FK + JOIN | **NÃO incluir** (vem da sessão) | — (oculto/automático) |
| **FK de referência** | `categoria_id` (escolhida) | `categoria_id:int` + `categoria_nome:Optional[str]` | FK + JOIN | `Field(..., gt=0)` | `type='select'` (dict de entidades) |
| **Data/hora** | `data_criacao:datetime` | `Optional[datetime]=None` | TIMESTAMP | normalmente **não** no DTO | `type='date'` ou automático |
| **Computado/JOIN** | `total_itens:int` | campo com default | (vem de subquery/agregação) | não | exibição apenas |

A diferença mais importante: **FK de propriedade** (`usuario_id`) vem da sessão e **nunca** vai
ao formulário nem ao DTO; **FK de referência** (`categoria_id`) vem de um `<select>` e **vai** ao
DTO e ao formulário.

---

## Ordem de Geração (obrigatória)

Camadas posteriores dependem das anteriores. Siga EXATAMENTE:

1. **Model** → `model/{entidade}_model.py`
2. **SQL** → `sql/{entidade}_sql.py`
3. **Repository** → `repo/{entidade}_repo.py`
4. **DTO** → `dtos/{entidade}_dto.py`
5. **Índices** → editar `sql/indices_sql.py` (adicionar índices das FKs)
6. **Routes** → `routes/admin_{entidade}_routes.py`
7. **Templates** → `templates/admin/{entidade}/{listar,cadastrar,editar}.html`
8. **Registro em main.py** → TABELAS (ordem de FK!) e ROUTERS
9. **Navbar** → `templates/base_privada.html`
10. **Verificação** → import + smoke test

---

## Padrões por Camada

Leia atentamente. Cada camada segue EXATAMENTE estes padrões.

### 1. Model (`model/{entidade}_model.py`)

```python
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from util.enum_base import EnumEntidade


class Status{Entidade}(EnumEntidade):
    """Enum de status — herda de EnumEntidade para ganhar métodos úteis."""
    ATIVO = "Ativo"
    INATIVO = "Inativo"


@dataclass
class {Entidade}:
    """Entidade {Entidade}."""
    id: int
    nome: str
    valor: float = 0.0
    ativo: bool = False
    status: Status{Entidade} = Status{Entidade}.ATIVO
    # FK de referência (entidade escolhida no form)
    categoria_id: int = 0
    # FK de propriedade (usuário dono, vindo da sessão)
    usuario_id: int = 0
    # Datas — sempre Optional
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    # Campos de JOIN (apenas exibição) — sempre Optional[str] = None
    categoria_nome: Optional[str] = None
    usuario_nome: Optional[str] = None
```

**Regras:**
- Primeiro campo SEMPRE `id: int`.
- Enums de domínio SEMPRE herdam de `EnumEntidade` (de `util/enum_base.py`).
- `datetime`/`date` → `Optional[...] = None`. `bool` → `= False`.
- **Para cada FK** `{rel}_id: int` adicione um campo de exibição `{rel}_nome: Optional[str] = None`
  (preenchido via JOIN, usado só em listagens/detalhes).
- Campos com default vêm depois dos sem default (regra de dataclass).

### 2. SQL (`sql/{entidade}_sql.py`)

```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS {entidade} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    valor REAL NOT NULL DEFAULT 0,
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
INSERT INTO {entidade} (nome, valor, ativo, status, categoria_id, usuario_id)
VALUES (?, ?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT e.*, c.nome as categoria_nome, u.nome as usuario_nome
FROM {entidade} e
INNER JOIN categoria c ON e.categoria_id = c.id
INNER JOIN usuario u ON e.usuario_id = u.id
ORDER BY e.data_criacao DESC
"""

OBTER_POR_ID = """
SELECT e.*, c.nome as categoria_nome, u.nome as usuario_nome
FROM {entidade} e
INNER JOIN categoria c ON e.categoria_id = c.id
INNER JOIN usuario u ON e.usuario_id = u.id
WHERE e.id = ?
"""

# Query auxiliar para filtrar por uma FK (gere quando houver relacionamento relevante)
OBTER_POR_CATEGORIA = """
SELECT e.*, c.nome as categoria_nome, u.nome as usuario_nome
FROM {entidade} e
INNER JOIN categoria c ON e.categoria_id = c.id
INNER JOIN usuario u ON e.usuario_id = u.id
WHERE e.categoria_id = ?
ORDER BY e.data_criacao DESC
"""

ATUALIZAR = """
UPDATE {entidade}
SET nome = ?, valor = ?, ativo = ?, status = ?, categoria_id = ?,
    data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

EXCLUIR = "DELETE FROM {entidade} WHERE id = ?"
```

**Regras:**
- Constantes UPPERCASE. SEMPRE `?` placeholders — NUNCA concatenação.
- Tipos: `str`→TEXT, `int`→INTEGER, `float`/`Decimal`→REAL, `bool`→INTEGER, `date`→DATE, `datetime`→TIMESTAMP.
- `ATUALIZAR` SEMPRE inclui `data_atualizacao = CURRENT_TIMESTAMP` e `WHERE id = ?` por último.
  `ATUALIZAR` NÃO altera `usuario_id` (dono não muda) nem `data_criacao`.
- **Para cada FK**: declare `FOREIGN KEY (...) REFERENCES tabela(id) ON DELETE ...` e faça
  `INNER JOIN` em `OBTER_TODOS`/`OBTER_POR_ID` selecionando `{rel}.{campo} as {rel}_nome`.
  - `ON DELETE CASCADE` para FK de propriedade (`usuario_id`): apagar usuário apaga seus registros.
  - `ON DELETE RESTRICT` para FK de referência (`categoria_id`): impede apagar categoria em uso.
  - Use `LEFT JOIN` se a FK for **opcional** (nullable); `INNER JOIN` se obrigatória.
- Alias de tabela: `e` para a entidade; iniciais distintas para as relacionadas (`c`, `u`).
- SEMPRE inclua: `CRIAR_TABELA`, `INSERIR`, `OBTER_TODOS`, `OBTER_POR_ID`, `ATUALIZAR`, `EXCLUIR`.

### 3. Repository (`repo/{entidade}_repo.py`)

```python
"""Repositório de {Entidade}."""

import sqlite3
from typing import Optional, Type, TypeVar

from model.{entidade}_model import {Entidade}, Status{Entidade}
from sql.{entidade}_sql import (
    CRIAR_TABELA, INSERIR, OBTER_TODOS, OBTER_POR_ID,
    OBTER_POR_CATEGORIA, ATUALIZAR, EXCLUIR,
)
from util.db_util import obter_conexao
from util.logger_config import logger

T = TypeVar("T")


def _converter_enum_seguro(valor: str, tipo_enum: Type[T], padrao: T) -> T:
    """Converte string para Enum de forma segura, com fallback logado."""
    try:
        return tipo_enum(valor)
    except ValueError:
        logger.error(f"Valor inválido para {tipo_enum.__name__}: '{valor}'. Usando padrão.")
        return padrao


def _row_to_{entidade}(row: sqlite3.Row) -> {Entidade}:
    """Converte sqlite3.Row em dataclass {Entidade}."""
    # Campos de JOIN — checar existência (podem não vir em todas as queries)
    categoria_nome = row["categoria_nome"] if "categoria_nome" in row.keys() else None
    usuario_nome = row["usuario_nome"] if "usuario_nome" in row.keys() else None

    return {Entidade}(
        id=row["id"],
        nome=row["nome"],
        valor=row["valor"],                              # REAL → float direto
        ativo=bool(row["ativo"]),                        # INTEGER → bool
        status=_converter_enum_seguro(row["status"], Status{Entidade}, Status{Entidade}.ATIVO),
        categoria_id=row["categoria_id"],
        usuario_id=row["usuario_id"],
        data_criacao=row["data_criacao"],               # TIMESTAMP convertido pelo db_util
        data_atualizacao=row["data_atualizacao"],
        categoria_nome=categoria_nome,
        usuario_nome=usuario_nome,
    )


def criar_tabela() -> bool:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(entidade: {Entidade}) -> Optional[int]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            entidade.nome,
            entidade.valor,
            1 if entidade.ativo else 0,        # bool → INTEGER
            entidade.status.value,             # Enum → .value
            entidade.categoria_id,
            entidade.usuario_id,
        ))
        return cursor.lastrowid


def obter_todos() -> list[{Entidade}]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_{entidade}(row) for row in cursor.fetchall()]


def obter_por_id(id: int) -> Optional[{Entidade}]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        return _row_to_{entidade}(row) if row else None


def obter_por_categoria(categoria_id: int) -> list[{Entidade}]:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_CATEGORIA, (categoria_id,))
        return [_row_to_{entidade}(row) for row in cursor.fetchall()]


def atualizar(entidade: {Entidade}) -> bool:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            entidade.nome,
            entidade.valor,
            1 if entidade.ativo else 0,
            entidade.status.value,
            entidade.categoria_id,
            entidade.id,                       # WHERE id = ? — SEMPRE por último
        ))
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0
```

**Regras:**
- SEMPRE `with obter_conexao() as conn:` (commit/rollback/close automáticos).
- `_row_to_{entidade}` SEMPRE existe; lê campos de JOIN defensivamente com `if "x" in row.keys()`.
- Enum: `_converter_enum_seguro(...)` ao ler, `.value` ao gravar. bool: `bool(row[...])` ao ler, `1 if x else 0` ao gravar.
- `criar_tabela()→bool`, `inserir()→lastrowid`, `atualizar()/excluir()→rowcount>0`, `obter_todos()→list`, `obter_por_id()→Optional`.
- **Imports circulares (mestre-detalhe):** se este repo precisar chamar um repo que também o importa
  (ex: `chamado_repo` ↔ `chamado_interacao_repo`), use **lazy import dentro da função**:
  `def obter_todos(): from repo import outro_repo; ...`. Documente com comentário no topo do arquivo.

### 4. DTO (`dtos/{entidade}_dto.py`)

```python
from pydantic import BaseModel, Field, field_validator
from dtos.validators import validar_string_obrigatoria, validar_tipo, validar_id_positivo
from model.{entidade}_model import Status{Entidade}


class Criar{Entidade}DTO(BaseModel):
    """DTO para criação de {Entidade}."""
    nome: str = Field(..., description="Nome")
    valor: float = Field(..., gt=0, description="Valor")
    status: str = Field(default="Ativo", description="Status")
    categoria_id: int = Field(..., gt=0, description="Categoria selecionada")
    ativo: bool = Field(default=False, description="Ativo")

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria(nome_campo="Nome", tamanho_minimo=3, tamanho_maximo=200)
    )
    _validar_status = field_validator("status")(validar_tipo("Status", Status{Entidade}))
    _validar_categoria = field_validator("categoria_id")(validar_id_positivo(nome_campo="Categoria"))


class Alterar{Entidade}DTO(Criar{Entidade}DTO):
    """DTO para alteração — mesmos campos da criação (status obrigatório)."""
    status: str = Field(..., description="Status")
```

**Regras:**
- SEMPRE dois DTOs: `Criar{Entidade}DTO` e `Alterar{Entidade}DTO` (pode herdar de Criar).
- SEMPRE use validators de `dtos/validators.py` — NUNCA reescreva validação. Principais:
  - Texto: `validar_string_obrigatoria(nome_campo=..., tamanho_minimo=..., tamanho_maximo=...)`
  - Enum: `validar_tipo("Campo", TipoEnum)`
  - Email: `validar_email()`; CPF/CNPJ: `validar_cpf()`/`validar_cnpj()`; data: `validar_data()`
  - FK / id: `validar_id_positivo(nome_campo="Categoria")`
  - Números: prefira restrições do Pydantic: `Field(..., gt=0)` (>0), `Field(..., ge=0)` (≥0).
- **FK de propriedade (`usuario_id`): NÃO incluir no DTO** — vem de `usuario_logado.id`.
- **FK de referência (`categoria_id`): INCLUIR** como `int = Field(..., gt=0)` — vem do `<select>`.

### 5. Índices (`sql/indices_sql.py`)

Para **toda FK**, adicione um índice (acelera JOINs e filtros). Edite `sql/indices_sql.py`:

```python
# Índices da tabela {entidade}
CRIAR_INDICE_{ENTIDADE}_CATEGORIA = """
CREATE INDEX IF NOT EXISTS idx_{entidade}_categoria_id
ON {entidade}(categoria_id)
"""

CRIAR_INDICE_{ENTIDADE}_USUARIO = """
CREATE INDEX IF NOT EXISTS idx_{entidade}_usuario_id
ON {entidade}(usuario_id)
"""
```

E adicione-os à lista `TODOS_INDICES`:

```python
TODOS_INDICES = [
    # ...existentes...
    CRIAR_INDICE_{ENTIDADE}_CATEGORIA,
    CRIAR_INDICE_{ENTIDADE}_USUARIO,
]
```

Crie também índice para campos muito filtrados (ex: `status`). Os índices são criados no startup
por `indices_repo.criar_indices()` (já chamado em `main.py`). Falha de índice não é crítica.

### 6. Routes (`routes/admin_{entidade}_routes.py`)

> Este template mostra o caso **completo** (com FK de referência `categoria_id`, FK de propriedade
> `usuario_id`, enum `status` e campo decimal `valor`). **Adapte por classificação de campos:**
> - Sem FK de referência → remova `from repo import categoria_repo`, `categorias` de `_opcoes_formulario()` e o parâmetro/uso de `categoria_id`.
> - Sem `usuario_id` → remova a linha `usuario_id=...` na criação e `usuario_id=item.usuario_id` no update.
> - Sem enum → remova `status` e `status_valores` (e o `import Status{Entidade}`).
> - Sem campo float/Decimal → remova `_normalizar_decimal` e use o tipo direto no `Form()`.
> - Se sobrar nada em `_opcoes_formulario()` (sem FK de referência e sem enum), remova a função e os `**_opcoes_formulario()`.

```python
"""Rotas administrativas para gerenciamento de {Entidade}."""

# =============================================================================
# Imports
# =============================================================================

from typing import Optional

from fastapi import APIRouter, Form, Request
from fastapi import status as http_status   # alias: evita colisão com o campo Form `status`
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.{entidade}_dto import Criar{Entidade}DTO, Alterar{Entidade}DTO
from model.{entidade}_model import {Entidade}, Status{Entidade}
from model.usuario_logado_model import UsuarioLogado
from repo import {entidade}_repo
from repo import categoria_repo          # repo da entidade relacionada (para o dropdown)

from util.auth_decorator import requer_autenticacao
from util.exceptions import ErroValidacaoFormulario
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.repository_helpers import obter_ou_404
from util.template_util import criar_templates

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/admin/{entidade_plural}")
templates = criar_templates()

# =============================================================================
# Rate Limiter
# =============================================================================

{entidade}_limiter = DynamicRateLimiter(
    chave_max="rate_limit_admin_{entidade}_max",
    chave_minutos="rate_limit_admin_{entidade}_minutos",
    padrao_max=30,
    padrao_minutos=1,
    nome="admin_{entidade}",
)


# Inclua este helper SOMENTE se a entidade tiver campo float/Decimal (ver §Decimais).
def _normalizar_decimal(valor: str) -> str:
    """Converte '1.234,56' ou 'R$ 1.234,56' ou '1234.56' em '1234.56'."""
    valor = (valor or "").strip().replace("R$", "").replace(" ", "")
    if "," in valor:                       # formato pt-BR: ponto=milhar, vírgula=decimal
        valor = valor.replace(".", "").replace(",", ".")
    return valor or "0"


def _opcoes_formulario() -> dict:
    """Dados auxiliares (relacionamentos + enums) para popular selects do formulário."""
    return {
        "categorias": categoria_repo.obter_todos(),
        "status_valores": Status{Entidade}.valores(),
    }


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Lista todos os {entidade_plural}."""
    assert usuario_logado is not None
    itens = {entidade}_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/{entidade}/listar.html",
        {"request": request, "{entidade_plural}": itens, "usuario_logado": usuario_logado},
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe formulário de cadastro."""
    assert usuario_logado is not None
    return templates.TemplateResponse(
        "admin/{entidade}/cadastrar.html",
        {"request": request, "usuario_logado": usuario_logado, **_opcoes_formulario()},
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    valor: str = Form(...),                 # decimal chega como string — normalizar (ver §Decimais)
    status: str = Form("Ativo"),
    categoria_id: int = Form(...),
    ativo: bool = Form(False),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Cadastra um novo {entidade}."""
    assert usuario_logado is not None

    ip = obter_identificador_cliente(request)
    if not {entidade}_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento.")
        return RedirectResponse("/admin/{entidade_plural}/listar", status_code=http_status.HTTP_303_SEE_OTHER)

    valor_norm = _normalizar_decimal(valor)
    dados_formulario: dict = {
        "nome": nome, "valor": valor, "status": status,
        "categoria_id": categoria_id, "ativo": ativo,
    }

    try:
        dto = Criar{Entidade}DTO(
            nome=nome, valor=float(valor_norm), status=status,
            categoria_id=categoria_id, ativo=ativo,
        )
        novo = {Entidade}(
            id=0, nome=dto.nome, valor=dto.valor, ativo=dto.ativo,
            status=Status{Entidade}(dto.status), categoria_id=dto.categoria_id,
            usuario_id=usuario_logado.id,        # FK de propriedade — da sessão
        )
        id_criado = {entidade}_repo.inserir(novo)
        if id_criado:
            informar_sucesso(request, "{Entidade} cadastrado com sucesso!")
            logger.info(f"{Entidade} #{id_criado} criado por admin {usuario_logado.id}")
        else:
            informar_erro(request, "Erro ao cadastrar {entidade}.")
    except ValidationError as e:
        dados_formulario.update(_opcoes_formulario())   # reinjeta selects
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/{entidade}/cadastrar.html",
            dados_formulario=dados_formulario,
        )

    return RedirectResponse("/admin/{entidade_plural}/listar", status_code=http_status.HTTP_303_SEE_OTHER)


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe formulário de edição."""
    assert usuario_logado is not None
    item = obter_ou_404(
        {entidade}_repo.obter_por_id(id), request,
        "{Entidade} não encontrado", "/admin/{entidade_plural}/listar",
    )
    if isinstance(item, RedirectResponse):
        return item

    dados = item.__dict__.copy()             # <- repopula o form (value=dados.campo)
    return templates.TemplateResponse(
        "admin/{entidade}/editar.html",
        {
            "request": request,
            "{entidade}": item,
            "dados": dados,
            "usuario_logado": usuario_logado,
            **_opcoes_formulario(),
        },
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    valor: str = Form(...),
    status: str = Form(...),
    categoria_id: int = Form(...),
    ativo: bool = Form(False),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Altera um {entidade}."""
    assert usuario_logado is not None

    ip = obter_identificador_cliente(request)
    if not {entidade}_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento.")
        return RedirectResponse("/admin/{entidade_plural}/listar", status_code=http_status.HTTP_303_SEE_OTHER)

    item = obter_ou_404(
        {entidade}_repo.obter_por_id(id), request,
        "{Entidade} não encontrado", "/admin/{entidade_plural}/listar",
    )
    if isinstance(item, RedirectResponse):
        return item

    valor_norm = _normalizar_decimal(valor)
    dados_formulario: dict = {
        "id": id, "nome": nome, "valor": valor, "status": status,
        "categoria_id": categoria_id, "ativo": ativo,
    }

    try:
        dto = Alterar{Entidade}DTO(
            nome=nome, valor=float(valor_norm), status=status,
            categoria_id=categoria_id, ativo=ativo,
        )
        atualizado = {Entidade}(
            id=id, nome=dto.nome, valor=dto.valor, ativo=dto.ativo,
            status=Status{Entidade}(dto.status), categoria_id=dto.categoria_id,
            usuario_id=item.usuario_id,          # dono não muda
        )
        if {entidade}_repo.atualizar(atualizado):
            informar_sucesso(request, "{Entidade} atualizado com sucesso!")
            logger.info(f"{Entidade} #{id} alterado por admin {usuario_logado.id}")
        else:
            informar_erro(request, "Erro ao atualizar {entidade}.")
    except ValidationError as e:
        dados_formulario["{entidade}"] = item
        dados_formulario.update(_opcoes_formulario())
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/{entidade}/editar.html",
            dados_formulario=dados_formulario,
        )

    return RedirectResponse("/admin/{entidade_plural}/listar", status_code=http_status.HTTP_303_SEE_OTHER)


@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: Optional[UsuarioLogado] = None):
    """Exclui um {entidade}."""
    assert usuario_logado is not None
    if {entidade}_repo.excluir(id):
        informar_sucesso(request, "{Entidade} excluído com sucesso!")
        logger.info(f"{Entidade} #{id} excluído por admin {usuario_logado.id}")
    else:
        informar_erro(request, "Erro ao excluir {entidade}.")
    return RedirectResponse("/admin/{entidade_plural}/listar", status_code=http_status.HTTP_303_SEE_OTHER)
```

> **Colisão `status`:** o template acima já importa `from fastapi import status as http_status`
> e usa `http_status.HTTP_303_SEE_OTHER` em todos os redirects. Isso é **obrigatório** sempre que a
> entidade tiver um campo/parâmetro `status: str = Form(...)`, pois o parâmetro `status` sombrearia
> o módulo `fastapi.status` dentro da função (causando `AttributeError`). Se a entidade NÃO tiver
> campo `status`, você pode importar `status` direto e usar `status.HTTP_303_SEE_OTHER` — mas usar
> o alias `http_status` sempre é seguro e é o padrão recomendado.

**Regras:**
- Arquivo `routes/admin_{entidade}_routes.py`, prefixo do router `/admin/{entidade_plural}`.
- TODAS as rotas: `@requer_autenticacao([Perfil.ADMIN.value])` e `assert usuario_logado is not None`.
- TODAS as POST: rate limiter + PRG (`RedirectResponse(..., status_code=HTTP_303_SEE_OTHER)`).
- Validação SEMPRE via `ErroValidacaoFormulario` (nunca TemplateResponse manual no `except`).
- `obter_ou_404()` antes de editar/excluir; cheque `isinstance(item, RedirectResponse)`.
- **GET editar passa `dados = item.__dict__.copy()`** (essencial p/ repopular o form).
- **Dropdowns de relacionamento/enum:** GET cadastrar/editar passam `**_opcoes_formulario()`;
  no `except ValidationError`, faça `dados_formulario.update(_opcoes_formulario())` (o handler
  faz merge de `dados_formulario` no contexto top-level, então `categorias`/`status_valores`
  ficam acessíveis no template).
- **FK de propriedade:** `usuario_id=usuario_logado.id` na criação; **não** alterada no update.
- **Campo `status` colidindo com `fastapi.status`:** o template já usa `from fastapi import status as http_status` + `http_status.HTTP_303_SEE_OTHER` em todos os redirects (obrigatório quando há campo `status`).

### 7. Templates

#### 7a. `templates/admin/{entidade}/listar.html`

```html
{% extends "base_privada.html" %}
{% from 'macros/action_buttons.html' import btn_group_crud %}
{% from 'macros/empty_states.html' import empty_state %}

{% block titulo %}Gerenciar {Entidade}s{% endblock %}

{% block content %}
<div class="row"><div class="col-12">
  <div class="d-flex justify-content-between align-items-center mb-4">
    <h2><i class="bi bi-{icone}"></i> Gerenciar {Entidade}s</h2>
    <a href="/admin/{entidade_plural}/cadastrar" class="btn btn-primary">
      <i class="bi bi-plus-circle"></i> Novo {Entidade}
    </a>
  </div>

  <div class="card shadow-sm"><div class="card-body p-0">
    {% if {entidade_plural} %}
    <div class="table-responsive">
      <table class="table table-hover align-middle mb-0">
        <thead class="table-light">
          <tr>
            <th>#</th>
            <th>Nome</th>
            <th>Categoria</th>          {# coluna do relacionamento #}
            <th>Status</th>
            <th class="text-center">Ações</th>
          </tr>
        </thead>
        <tbody>
          {% for item in {entidade_plural} %}
          <tr>
            <td>{{ item.id }}</td>
            <td>{{ item.nome }}</td>
            <td>{{ item.categoria_nome }}</td>   {# campo de JOIN #}
            <td><span class="badge bg-secondary">{{ item.status }}</span></td>
            <td class="text-center">
              {{ btn_group_crud(
                item.id, item.nome, '/admin/{entidade_plural}',
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
      {{ empty_state(
        'Nenhum {entidade} cadastrado',
        'Comece cadastrando o primeiro {entidade}.',
        action_url='/admin/{entidade_plural}/cadastrar',
        action_text='Cadastrar Primeiro {Entidade}',
        icon='{icone}', variant='info'
      ) }}
    </div>
    {% endif %}
  </div></div>
</div></div>

{% include 'components/modal_confirmacao.html' %}
{% endblock %}

{% block scripts %}
<script>
function confirmarExclusao(id, nome) {
  abrirModalConfirmacao({
    url: `/admin/{entidade_plural}/excluir/${id}`,
    mensagem: `Tem certeza que deseja excluir "${nome}"?`,
  });
}
</script>
{% endblock %}
```

#### 7b. `templates/admin/{entidade}/cadastrar.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Cadastrar {Entidade}{% endblock %}

{% block content %}
<div class="row justify-content-center"><div class="col-lg-8">
  <div class="d-flex align-items-center mb-4">
    <h2 class="mb-0"><i class="bi bi-plus-circle"></i> Cadastrar {Entidade}</h2>
  </div>

  <div class="card shadow-sm">
    <form method="POST" action="/admin/{entidade_plural}/cadastrar">
      {{ csrf_input(request) }}
      <div class="card-body p-4"><div class="row">
        <div class="col-12">{% include "components/alerta_erro.html" %}</div>

        <div class="col-12 mb-3">
          {{ field(name='nome', label='Nome', type='text', required=true) }}
        </div>

        {# Decimal/moeda — usa máscara; o submit envia valor parseável #}
        <div class="col-md-6 mb-3">
          {{ field(name='valor', label='Valor', type='decimal', required=true, decimal_prefix='R$ ') }}
        </div>

        {# Enum -> select. O macro field exige options como DICT {valor: label}. #}
        <div class="col-md-6 mb-3">
          {% set status_opcoes = {} %}
          {% for s in status_valores %}{% set _ = status_opcoes.update({s: s}) %}{% endfor %}
          {{ field(name='status', label='Status', type='select', required=true, options=status_opcoes) }}
        </div>

        {# FK de referência -> select populado com a lista de entidades relacionadas. #}
        <div class="col-md-6 mb-3">
          {% set categoria_opcoes = {} %}
          {% for c in categorias %}{% set _ = categoria_opcoes.update({c.id: c.nome}) %}{% endfor %}
          {{ field(name='categoria_id', label='Categoria', type='select', required=true, options=categoria_opcoes) }}
        </div>

        <div class="col-12 mb-3">
          {{ field(name='ativo', label='Ativo', type='checkbox') }}
        </div>
      </div></div>
      <div class="card-footer p-4"><div class="d-flex gap-3">
        <button type="submit" class="btn btn-primary"><i class="bi bi-check-circle"></i> Cadastrar</button>
        <a href="/admin/{entidade_plural}/listar" class="btn btn-secondary"><i class="bi bi-x-circle"></i> Cancelar</a>
      </div></div>
    </form>
  </div>
</div></div>
{% endblock %}
```

#### 7c. `templates/admin/{entidade}/editar.html`

Idêntico ao cadastrar, com três diferenças: título "Alterar", `action` com o id, e `value=dados.campo`
em cada campo (inclusive nos selects).

```html
<form method="POST" action="/admin/{entidade_plural}/editar/{{ dados.id if dados.id is defined else {entidade}.id }}">
  {{ csrf_input(request) }}
  ...
  {{ field(name='nome', label='Nome', type='text', required=true, value=dados.nome) }}
  {{ field(name='valor', label='Valor', type='decimal', required=true, decimal_prefix='R$ ', value=dados.valor) }}
  {{ field(name='status', label='Status', type='select', required=true, options=status_opcoes, value=dados.status) }}
  {{ field(name='categoria_id', label='Categoria', type='select', required=true, options=categoria_opcoes, value=dados.categoria_id) }}
  {{ field(name='ativo', label='Ativo', type='checkbox', value=dados.ativo) }}
```

**Regras de Template:**
- SEMPRE herdam de `base_privada.html`; blocos disponíveis: `titulo`, `head`, `content`, `scripts`.
- SEMPRE `{% from "macros/form_fields.html" import field with context %}` e use `field()` para TODOS
  os campos (nunca HTML de input manual).
- **SEMPRE `{{ csrf_input(request) }}`** — passe `request` (é o uso documentado em `template_util.py`;
  `csrf_input()` sem argumento gera token vazio).
- SEMPRE `{% include "components/alerta_erro.html" %}` no form e `{% include 'components/modal_confirmacao.html' %}` na listagem.
- **`field` exige `options` como DICT `{valor: label}`** (ele itera `options.items()`).
  `Enum.para_opcoes_select()` retorna lista de tuplas e NÃO serve direto — construa o dict no template
  (padrão `{% set d = {} %}{% for ... %}{% set _ = d.update({k: v}) %}{% endfor %}`) ou passe um dict pronto da rota.
- Para FK: o dict é `{entidade.id: entidade.campo_exibicao}`; o `value=dados.{fk}_id` pré-seleciona.
- Edição: `value=dados.campo` em todo campo (repopulação após erro de validação e na carga inicial).
- Tipos do `field`: `text`, `email`, `password`, `number`, `date`, `decimal`, `checkbox`, `textarea`,
  `select`, `radio`. Para máscaras (CPF/CNPJ/telefone/CEP) use `mask='CPF'` (e `unmask=true` p/ enviar sem máscara).

### 8. Registro em `main.py`

**a) TABELAS — RESPEITE A ORDEM DE DEPENDÊNCIA DE FK.** A tabela referenciada deve ser criada
ANTES da que a referencia (a entidade relacionada precisa existir antes). Ex.: `categoria` antes de `produto`.

```python
from repo import {entidade}_repo
# ...
TABELAS = [
    (usuario_repo, "usuario"),
    # ... entidades de referência (ex: categoria_repo) ANTES ...
    ({entidade}_repo, "{entidade}"),   # depois das tabelas que ele referencia
]
```

**b) ROUTERS:**

```python
from routes.admin_{entidade}_routes import router as admin_{entidade}_router
# ...
ROUTERS = [
    # ...outros routers admin...
    (admin_{entidade}_router, ["Admin - {Entidade}"], "admin de {entidade}"),
    # ...
    (public_router, ["Público"], "público"),     # penúltimo
    (examples_router, ["Exemplos"], "exemplos"),  # último
]
```

- TABELAS = tuplas `(repo, "nome_tabela")`. ROUTERS = tuplas `(router, [tags], "descrição")`.
- `public_router` e `examples_router` SEMPRE por último. Routers admin no meio.

### 9. Navbar (`templates/base_privada.html`)

Adicione um `<li>` dentro do bloco `{% if usuario_logado and usuario_logado.perfil == 'Administrador' %}`,
APÓS os links admin existentes e ANTES do `{% else %}`. Use `request.path` (não `request.url.path`):

```html
<li class="nav-item">
  <a class="nav-link {{ 'active' if '/admin/{entidade_plural}/' in request.path else '' }}"
     href="/admin/{entidade_plural}/listar"
     {{ 'aria-current=page' if '/admin/{entidade_plural}/' in request.path else '' }}>{Entidade}s</a>
</li>
```

### 10. Verificação (não pule)

Após gerar tudo, **verifique** antes de declarar concluído:

1. **Import/sintaxe:** `python -c "import main"` — deve importar sem erro (pega erros de sintaxe,
   imports faltando, colisão `status`).
2. **Criação de tabela e índices:** rode o app uma vez (`python main.py` e encerre) ou um script que
   chame `{entidade}_repo.criar_tabela()` — confirme que a tabela foi criada
   (`sqlite3 dados.db ".tables"`).
3. **Smoke test manual sugerido ao usuário:** subir o app, logar como admin
   (`admin@sistema.com` / `Admin@123`), acessar `/admin/{entidade_plural}/listar`, criar, editar e excluir um registro.
4. Se houver testes, rode `pytest` nos arquivos relevantes.

Relate o que foi verificado e o que ficou pendente. Nunca afirme "funciona" sem ter rodado ao menos o passo 1.

---

## Decimais e Moeda (round-trip)

O `field(type='decimal')` aplica máscara brasileira (`R$ 1.234,56`). No envio, o campo visível
manda o texto formatado. **Não confie em `float(valor)` direto** (quebra com separador de milhar).
Na rota, receba como `str` e normalize:

```python
def _normalizar_decimal(valor: str) -> str:
    """Converte '1.234,56' ou 'R$ 1.234,56' ou '1234.56' em '1234.56'."""
    valor = (valor or "").strip().replace("R$", "").replace(" ", "")
    if "," in valor:                       # formato pt-BR: ponto=milhar, vírgula=decimal
        valor = valor.replace(".", "").replace(",", ".")
    return valor or "0"
```

Depois: `dto = ...DTO(valor=float(_normalizar_decimal(valor)))`. No DTO use `valor: float = Field(..., gt=0)`.
(Alternativa do projeto: a máscara também injeta um campo oculto `valor_unmasked` já numérico;
você pode lê-lo via `Form()`, mas a normalização acima é mais robusta e independe de JS.)

---

## Cookbook de Relacionamentos

### A) Pertence-a usuário (FK de propriedade) — `usuario_id`
- Model: `usuario_id: int` + `usuario_nome: Optional[str] = None`.
- SQL: `FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE` + JOIN `u.nome as usuario_nome`.
- DTO: **não** inclui `usuario_id`.
- Rota: `usuario_id=usuario_logado.id` ao criar; **não** alterar no update.
- Template: exibe `item.usuario_nome` na listagem; sem campo de input.

### B) Pertence-a outra entidade (FK de referência) — `categoria_id`
- Model: `categoria_id: int` + `categoria_nome: Optional[str] = None`.
- SQL: `FOREIGN KEY (categoria_id) REFERENCES categoria(id) ON DELETE RESTRICT` + JOIN `c.nome as categoria_nome`.
- DTO: inclui `categoria_id: int = Field(..., gt=0)` + `validar_id_positivo`.
- Rota: GET cadastrar/editar carregam `categoria_repo.obter_todos()`; reinjetam em erro.
- Template: `<select>` populado com `{c.id: c.nome}`.
- main.py: `categoria` criada ANTES; índice `idx_{entidade}_categoria_id`.
- **FK opcional (nullable):** `categoria_id INTEGER` (sem NOT NULL), `LEFT JOIN`, DTO `Optional[int]`,
  e no select adicione opção vazia (o `field` já adiciona "Selecione..." quando `required=false`).

### C) Possui-muitos (mestre-detalhe 1:N) — estilo `chamado` → `chamado_interacao`
Padrão avançado: a entidade filha tem `{pai}_id` FK ao pai. Veja
**`references/master-detail.md`** para o passo a passo completo (repo filho com `obter_por_{pai}`,
view de detalhe renderizando filhos, formulário de adicionar filho, e lazy imports para evitar
import circular quando os repos se referenciam).

### Exemplo completo de ponta a ponta
Para um exemplo **inteiro** gerado (entidade `Produto` com FK `categoria_id` + `usuario_id`,
todos os 8 arquivos escritos por completo + registros), veja
**`references/exemplo-relacionamento.md`**. Use-o como gabarito ao gerar.

---

## Mapeamento de Tipos (todas as camadas)

| Tipo Python | SQL | DTO | `field` type | Observação |
|------------|-----|-----|--------------|-----------|
| `str` | TEXT | `Field(...)` + `validar_string_obrigatoria` | `text`/`textarea` | — |
| `str` email | TEXT | `validar_email()` | `email` | — |
| `str` CPF/CNPJ/tel/CEP | TEXT | `validar_cpf()`/… | `text` | `mask='CPF'` etc. |
| `int` | INTEGER | `Field(..., ge=0)` | `number` | — |
| `float`/`Decimal` | REAL | `Field(..., gt=0)` | `decimal` | normalizar (§Decimais) |
| `bool` | INTEGER DEFAULT 0 | `Field(default=False)` | `checkbox` | `1/0` no repo |
| `date` | DATE | `validar_data()` | `date` | — |
| `datetime` | TIMESTAMP | (não no DTO) | (automático) | `CURRENT_TIMESTAMP` |
| `Enum` (`EnumEntidade`) | TEXT | `str` + `validar_tipo` | `select`/`radio` | options = dict |
| FK propriedade `usuario_id` | INTEGER + FK | (não no DTO) | — | da sessão |
| FK referência `{rel}_id` | INTEGER + FK | `Field(..., gt=0)` + `validar_id_positivo` | `select` | options = `{id: nome}` |

---

## Checklist Final

- [ ] **Spec coletada** (campos classificados, relacionamentos identificados, plural definido)
- [ ] **Model**: `@dataclass`, `id:int` primeiro, enums `EnumEntidade`, FK `{rel}_id` + `{rel}_nome:Optional[str]`
- [ ] **SQL**: `?` placeholders, `CURRENT_TIMESTAMP`, FKs com `ON DELETE` correto, JOINs p/ `{rel}_nome`
- [ ] **Repo**: `_row_to_*` (JOIN defensivo), enum seguro, bool `1/0`, lazy import se circular
- [ ] **DTO**: `Criar*`/`Alterar*`, validators de `dtos/validators.py`, FK-referência incluída, FK-propriedade NÃO
- [ ] **Índices**: índice para cada FK adicionado a `sql/indices_sql.py` + `TODOS_INDICES`
- [ ] **Routes**: `@requer_autenticacao([Perfil.ADMIN.value])`, rate limiter, PRG, `ErroValidacaoFormulario`
- [ ] **Routes**: GET editar passa `dados=item.__dict__.copy()`; selects via `_opcoes_formulario()` (e reinjeção no erro)
- [ ] **Routes**: colisão do parâmetro `status` com `fastapi.status` resolvida (`import status as http_status`)
- [ ] **Templates**: `base_privada.html`, `field()` p/ tudo, `{{ csrf_input(request) }}`, `alerta_erro`, `modal_confirmacao`
- [ ] **Templates**: selects com `options` DICT; FK exibida na listagem (`{rel}_nome`); `value=dados.*` na edição
- [ ] **main.py**: TABELAS na ORDEM de FK (referenciada antes), ROUTERS antes de public/examples
- [ ] **Navbar**: `<li>` no bloco admin, `request.path` para `active`
- [ ] **Decimais** normalizados na rota (`_normalizar_decimal`)
- [ ] **Verificação**: `python -c "import main"` OK; tabela criada; smoke test relatado
