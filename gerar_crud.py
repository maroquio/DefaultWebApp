#!/usr/bin/env python3
"""
Gerador de CRUD para DefaultWebApp.

Gera automaticamente todos os arquivos necessários para um novo CRUD,
seguindo exatamente os padrões do boilerplate.

Uso:
    python gerar_crud.py

    # Ou com argumentos diretos:
    python gerar_crud.py --entidade produto --campos "nome:str,preco:float,descricao:str,ativo:bool"

Arquivos gerados:
    model/{entidade}_model.py
    sql/{entidade}_sql.py
    repo/{entidade}_repo.py
    dtos/{entidade}_dto.py
    routes/{entidade}_routes.py
    templates/{entidade}/listar.html
    templates/{entidade}/cadastrar.html
    templates/{entidade}/alterar.html

Após geração, você ainda precisa:
    1. Importar o repo e adicionar à lista TABELAS em main.py
    2. Importar e adicionar o router à lista ROUTERS em main.py
    3. Customizar a lógica de negócio nos arquivos gerados (marcado com TODO)
"""

import sys
import re
import argparse
from pathlib import Path

# ─── Cores ────────────────────────────────────────────────────────────────────

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def cor(texto, codigo=""):
    if sys.stdout.isatty() and codigo:
        return f"{codigo}{texto}{RESET}"
    return texto


def ok(texto):
    print(cor(f"  ✓ {texto}", GREEN))


def aviso(texto):
    print(cor(f"  ⚠ {texto}", YELLOW))


def erro_fatal(texto):
    print(cor(f"  ✗ {texto}", RED))
    sys.exit(1)


def perguntar(prompt, padrao=""):
    sufixo = f" [{padrao}]" if padrao else ""
    try:
        resposta = input(cor(f"  → {prompt}{sufixo}: ", CYAN)).strip()
        return resposta if resposta else padrao
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)


# ─── Tipos Python → SQL ───────────────────────────────────────────────────────

TIPOS_SQL = {
    "str": "TEXT",
    "int": "INTEGER",
    "float": "REAL",
    "bool": "INTEGER",  # SQLite não tem BOOLEAN nativo
    "date": "DATE",
    "datetime": "TIMESTAMP",
    "Decimal": "REAL",
}

TIPOS_DTO = {
    "str": "str",
    "int": "int",
    "float": "float",
    "bool": "bool",
    "date": "date",
    "datetime": "datetime",
    "Decimal": "Decimal",
}

VALIDATORS_MAP = {
    "str": "validar_string_obrigatoria()",
    "int": "validar_inteiro_positivo()",
    "float": "validar_decimal_positivo()",
}

FORM_FIELD_TYPES = {
    "str": "text",
    "int": "text",
    "float": "text",
    "bool": "checkbox",
    "date": "date",
    "datetime": "text",
    "Decimal": "text",
}


# ─── Funções auxiliares ───────────────────────────────────────────────────────

def snake_case(nome):
    """Converte para snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", nome)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def pascal_case(nome):
    """Converte para PascalCase."""
    return "".join(w.capitalize() for w in re.split(r"[_\s\-]+", nome))


def plural(nome):
    """Heurística simples para plural em português."""
    if nome.endswith("ao"):
        return nome[:-2] + "oes"
    if nome.endswith("al"):
        return nome[:-2] + "ais"
    if nome.endswith("em"):
        return nome[:-2] + "ens"
    if nome.endswith("r") or nome.endswith("z") or nome.endswith("s"):
        return nome + "es"
    return nome + "s"


def parsear_campos(campos_str):
    """
    Converte "nome:str,preco:float,ativo:bool" em lista de (nome, tipo).
    """
    campos = []
    for item in campos_str.split(","):
        item = item.strip()
        if not item:
            continue
        partes = item.split(":")
        nome_campo = partes[0].strip()
        tipo_campo = partes[1].strip() if len(partes) > 1 else "str"
        if tipo_campo not in TIPOS_SQL:
            aviso(f"Tipo '{tipo_campo}' não reconhecido para campo '{nome_campo}'. Usando 'str'.")
            tipo_campo = "str"
        campos.append((nome_campo, tipo_campo))
    return campos


# ─── Templates de código ──────────────────────────────────────────────────────

def _campo_tipo_hint(nome, tipo):
    """Retorna declaração de campo para dataclass."""
    if tipo in ("date", "datetime"):
        return f"{nome}: Optional[{tipo}] = None"
    if tipo == "bool":
        return f"{nome}: bool = False"
    if tipo in ("int", "float"):
        return f"{nome}: {tipo} = 0"
    return f'{nome}: {tipo} = ""'


def gerar_model(entidade, campos):
    entidade_pascal = pascal_case(entidade)

    campos_dataclass = "\n    ".join(
        _campo_tipo_hint(nome, tipo)
        for nome, tipo in campos
    )

    imports_extra = ""
    if any(t == "date" for _, t in campos):
        imports_extra += "from datetime import date\n"
    if any(t == "datetime" for _, t in campos):
        imports_extra += "from datetime import datetime\n"
    if any(t == "Decimal" for _, t in campos):
        imports_extra += "from decimal import Decimal\n"

    return f'''\
from dataclasses import dataclass
from typing import Optional
{imports_extra}

@dataclass
class {entidade_pascal}:
    """
    Model para {entidade_pascal}.

    Representa uma entidade do domínio da aplicação.
    Campos obrigatórios: id (gerado automaticamente pelo banco).

    TODO: Adicione os campos específicos do seu domínio.
    """

    id: int
    {campos_dataclass}
'''


def gerar_sql(entidade, campos):
    entidade_upper = entidade.upper()
    entidade_pascal = pascal_case(entidade)

    colunas_sql = "\n    ".join(
        f"{nome} {TIPOS_SQL.get(tipo, 'TEXT')} NOT NULL{' DEFAULT 0' if tipo == 'bool' else ''},"
        for nome, tipo in campos
    )

    campos_insert = ", ".join(nome for nome, _ in campos)
    placeholders = ", ".join("?" for _ in campos)
    campos_update = ",\n    ".join(f"{nome} = ?" for nome, _ in campos)

    return f'''\
"""
Queries SQL para {entidade_pascal}.

TODO: Adicione índices para campos frequentemente pesquisados.
      Exemplo: CREATE INDEX IF NOT EXISTS idx_{entidade}_{campos[0][0] if campos else "id"} ON {entidade}({campos[0][0] if campos else "id"});
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS {entidade} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {colunas_sql}
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

INSERIR = """
INSERT INTO {entidade} ({campos_insert})
VALUES ({placeholders})
"""

OBTER_TODOS = """
SELECT * FROM {entidade}
ORDER BY id DESC
"""

OBTER_POR_ID = """
SELECT * FROM {entidade}
WHERE id = ?
"""

ATUALIZAR = """
UPDATE {entidade}
SET {campos_update},
    data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

EXCLUIR = """
DELETE FROM {entidade}
WHERE id = ?
"""

CONTAR = """
SELECT COUNT(*) as total FROM {entidade}
"""
'''


def _campo_row(nome, tipo):
    """Retorna linha de conversão de row para dataclass."""
    if tipo == "bool":
        return f'{nome}=bool(row["{nome}"]),'
    return f'{nome}=row["{nome}"],'


def _param_entidade(nome, tipo):
    """Retorna expressão para parâmetro de SQL."""
    if tipo == "bool":
        return f"1 if entidade.{nome} else 0"
    return f"entidade.{nome}"


def gerar_repo(entidade, campos):
    entidade_pascal = pascal_case(entidade)
    entidade_plural = plural(entidade)

    campos_row = "\n        ".join(
        _campo_row(nome, tipo)
        for nome, tipo in campos
    )

    params_insert = ",\n            ".join(
        _param_entidade(nome, tipo)
        for nome, tipo in campos
    )

    params_update = ",\n            ".join(
        _param_entidade(nome, tipo)
        for nome, tipo in campos
    ) + ",\n            entidade.id"

    return f'''\
"""
Repositório de {entidade_pascal}.

Responsável por todas as operações de banco de dados relacionadas a {entidade_pascal}.

Uso:
    from repo import {entidade}_repo
    {entidade_plural} = {entidade}_repo.obter_todos()
    {entidade} = {entidade}_repo.obter_por_id(1)
"""

import sqlite3
from typing import Optional

from model.{entidade}_model import {entidade_pascal}
from sql.{entidade}_sql import CRIAR_TABELA, INSERIR, OBTER_TODOS, OBTER_POR_ID, ATUALIZAR, EXCLUIR, CONTAR
from util.db_util import obter_conexao
from util.logger_config import logger


def _row_to_{entidade}(row: sqlite3.Row) -> {entidade_pascal}:
    """Converte sqlite3.Row em dataclass {entidade_pascal}."""
    return {entidade_pascal}(
        id=row["id"],
        {campos_row}
    )


def criar_tabela() -> bool:
    """Cria a tabela {entidade} se não existir."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(entidade: {entidade_pascal}) -> Optional[int]:
    """
    Insere um novo {entidade_pascal} no banco.

    Returns:
        ID do registro inserido ou None em caso de erro
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            {params_insert}
        ))
        return cursor.lastrowid


def obter_todos() -> list[{entidade_pascal}]:
    """Retorna todos os registros de {entidade_pascal}."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_{entidade}(row) for row in cursor.fetchall()]


def obter_por_id(id: int) -> Optional[{entidade_pascal}]:
    """Retorna um {entidade_pascal} pelo ID ou None se não encontrado."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        return _row_to_{entidade}(row) if row else None


def atualizar(entidade: {entidade_pascal}) -> bool:
    """
    Atualiza os dados de um {entidade_pascal}.

    Returns:
        True se atualizou com sucesso, False se não encontrou
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            {params_update}
        ))
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    """
    Exclui um {entidade_pascal} pelo ID.

    Returns:
        True se excluiu com sucesso, False se não encontrou
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0


def contar() -> int:
    """Retorna o total de {entidade_pascal} cadastrados."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        row = cursor.fetchone()
        return row["total"] if row else 0
'''


def gerar_dto(entidade, campos):
    entidade_pascal = pascal_case(entidade)

    campos_dto = "\n    ".join(
        f"{nome}: {TIPOS_DTO.get(tipo, 'str')}"
        for nome, tipo in campos
        if tipo != "bool"
    )

    campos_dto_bool = "\n    ".join(
        f"{nome}: bool = False"
        for nome, tipo in campos
        if tipo == "bool"
    )

    validators = "\n\n    ".join(
        f"_validar_{nome} = field_validator('{nome}')({VALIDATORS_MAP[tipo]})"
        for nome, tipo in campos
        if tipo in VALIDATORS_MAP
    )

    return f'''\
"""
DTOs de validação para {entidade_pascal}.

Usa validators reutilizáveis de dtos/validators.py.

TODO: Adicione validações específicas do seu domínio.
      Consulte docs/CRIAR_CRUD.md para exemplos de validação.
"""

from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria, validar_inteiro_positivo, validar_decimal_positivo


class Criar{entidade_pascal}DTO(BaseModel):
    """DTO para criação de {entidade_pascal}. Valida dados do formulário de cadastro."""

    {campos_dto}
    {campos_dto_bool}

    # TODO: Adicione validators específicos abaixo
    # Exemplos de validators disponíveis em dtos/validators.py:
    {validators if validators else "# _validar_nome = field_validator('nome')(validar_string_obrigatoria())"}


class Alterar{entidade_pascal}DTO(BaseModel):
    """DTO para atualização de {entidade_pascal}. Valida dados do formulário de edição."""

    {campos_dto}
    {campos_dto_bool}

    # TODO: Adicione validators específicos abaixo
    {validators if validators else "# _validar_nome = field_validator('nome')(validar_string_obrigatoria())"}
'''


def gerar_routes(entidade, campos):
    entidade_pascal = pascal_case(entidade)
    entidade_plural = plural(entidade)

    def _form_param(nome, tipo):
        if tipo == "bool":
            return f"{nome}: bool = Form(False)"
        return f'{nome}: str = Form("")'

    # Parâmetros Form para POST cadastrar
    form_params = ",\n    ".join(
        _form_param(nome, tipo)
        for nome, tipo in campos
    )

    # dados_formulario dict
    dados_form = "\n            ".join(
        f'"{nome}": {nome},'
        for nome, _ in campos
    )

    # Criação do DTO
    dto_params = "\n            ".join(
        f"{nome}={nome},"
        for nome, _ in campos
    )

    # Construção do model
    model_params = "\n            ".join(
        f"{nome}=dto.{nome},"
        for nome, _ in campos
    )

    return f'''\
"""
Rotas para gerenciamento de {entidade_pascal}.

Padrão PRG (Post-Redirect-Get) aplicado em todos os POSTs.
Rate limiting e autenticação configurados.

TODO: Ajuste os perfis de acesso conforme necessário.
TODO: Adicione validações de negócio específicas.
"""

from typing import Optional

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.{entidade}_dto import Criar{entidade_pascal}DTO, Alterar{entidade_pascal}DTO
from model.{entidade}_model import {entidade_pascal}
from model.usuario_logado_model import UsuarioLogado
from repo import {entidade}_repo
from util.auth_decorator import requer_autenticacao
from util.exceptions import ErroValidacaoFormulario
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.paginacao_util import paginar
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.template_util import criar_templates

router = APIRouter(prefix="/{entidade_plural}")
templates = criar_templates()

# TODO: Configure os limites de rate limiting adequados para o seu caso
{entidade}_limiter = DynamicRateLimiter(
    chave_max="rate_limit_{entidade}_max",
    chave_minutos="rate_limit_{entidade}_minutos",
    padrao_max=30,
    padrao_minutos=1,
    nome="{entidade}_crud",
)


@router.get("/")
@requer_autenticacao()
async def listar(
    request: Request,
    pagina: int = 1,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Lista todos os {entidade_plural} com paginação."""
    assert usuario_logado is not None

    todos = {entidade}_repo.obter_todos()
    paginacao = paginar(todos, pagina=pagina, por_pagina=10)

    return templates.TemplateResponse(
        "{entidade}/listar.html",
        {{
            "request": request,
            "usuario_logado": usuario_logado,
            "paginacao": paginacao,
            "{entidade_plural}": paginacao.items,
        }},
    )


@router.get("/cadastrar")
@requer_autenticacao()
async def get_cadastrar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe formulário de cadastro."""
    assert usuario_logado is not None
    return templates.TemplateResponse(
        "{entidade}/cadastrar.html",
        {{"request": request, "usuario_logado": usuario_logado}},
    )


@router.post("/cadastrar")
@requer_autenticacao()
async def post_cadastrar(
    request: Request,
    {form_params},
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Processa o formulário de cadastro."""
    assert usuario_logado is not None

    dados_formulario = {{
        {dados_form}
    }}

    try:
        dto = Criar{entidade_pascal}DTO(
            {dto_params}
        )

        novo = {entidade_pascal}(
            id=0,
            {model_params}
        )
        id_criado = {entidade}_repo.inserir(novo)

        if id_criado:
            informar_sucesso(request, "{entidade_pascal} cadastrado com sucesso!")
        else:
            informar_erro(request, "Erro ao cadastrar {entidade_pascal}.")

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="{entidade}/cadastrar.html",
            dados_formulario=dados_formulario,
        )

    return RedirectResponse(url="/{entidade_plural}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/editar/{{id}}")
@requer_autenticacao()
async def get_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exibe formulário de edição."""
    assert usuario_logado is not None

    item = {entidade}_repo.obter_por_id(id)
    if not item:
        informar_erro(request, "{entidade_pascal} não encontrado.")
        return RedirectResponse(url="/{entidade_plural}", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "{entidade}/alterar.html",
        {{
            "request": request,
            "usuario_logado": usuario_logado,
            "{entidade}": item,
        }},
    )


@router.post("/editar/{{id}}")
@requer_autenticacao()
async def post_editar(
    request: Request,
    id: int,
    {form_params},
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Processa o formulário de edição."""
    assert usuario_logado is not None

    item = {entidade}_repo.obter_por_id(id)
    if not item:
        informar_erro(request, "{entidade_pascal} não encontrado.")
        return RedirectResponse(url="/{entidade_plural}", status_code=status.HTTP_303_SEE_OTHER)

    dados_formulario = {{
        {dados_form}
    }}

    try:
        dto = Alterar{entidade_pascal}DTO(
            {dto_params}
        )

        item_atualizado = {entidade_pascal}(
            id=id,
            {model_params}
        )
        sucesso = {entidade}_repo.atualizar(item_atualizado)

        if sucesso:
            informar_sucesso(request, "{entidade_pascal} atualizado com sucesso!")
        else:
            informar_erro(request, "Erro ao atualizar {entidade_pascal}.")

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="{entidade}/alterar.html",
            dados_formulario={{**dados_formulario, "{entidade}": item}},
        )

    return RedirectResponse(url="/{entidade_plural}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/excluir/{{id}}")
@requer_autenticacao()
async def excluir(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exclui um {entidade_pascal}."""
    assert usuario_logado is not None

    sucesso = {entidade}_repo.excluir(id)
    if sucesso:
        informar_sucesso(request, "{entidade_pascal} excluído com sucesso!")
    else:
        informar_erro(request, "Erro ao excluir {entidade_pascal}.")

    return RedirectResponse(url="/{entidade_plural}", status_code=status.HTTP_303_SEE_OTHER)
'''


def gerar_template_listar(entidade, campos):
    entidade_pascal = pascal_case(entidade)
    entidade_plural = plural(entidade)

    cabecalhos_th = "\n                                    ".join(
        f"<th>{nome.replace('_', ' ').title()}</th>"
        for nome, _ in campos[:4]  # Máx 4 colunas na listagem
    )

    colunas_td = "\n                                    ".join(
        f"<td>{{{{ item.{nome} }}}}</td>"
        for nome, _ in campos[:4]
    )

    return f'''\
{{% extends "base_privada.html" %}}
{{% from "macros/empty_states.html" import empty_state %}}
{{% from "macros/paginacao.html" import paginacao_completa %}}
{{% from "macros/action_buttons.html" import btn_group_crud %}}

{{% block titulo %}}{entidade_pascal}s{{% endblock %}}

{{% block content %}}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-list-ul"></i> {entidade_pascal}s</h2>
            <a href="/{entidade_plural}/cadastrar" class="btn btn-success">
                <i class="bi bi-plus-circle"></i> Novo {entidade_pascal}
            </a>
        </div>

        {{% if {entidade_plural} %}}
        <div class="card shadow-sm">
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>#</th>
                                {cabecalhos_th}
                                <th class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {{% for item in {entidade_plural} %}}
                            <tr>
                                <td>{{{{ item.id }}}}</td>
                                {colunas_td}
                                <td class="text-center">
                                    {{{{ btn_group_crud(
                                        entity_id=item.id,
                                        entity_name=item.{campos[0][0] if campos else 'id'},
                                        base_url="/{entidade_plural}",
                                        delete_function="confirmarExclusao(" ~ item.id ~ ", '" ~ item.{campos[0][0] if campos else 'id'} ~ "')"
                                    ) }}}}
                                </td>
                            </tr>
                            {{% endfor %}}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        {{{{ paginacao_completa(paginacao, "/{entidade_plural}") }}}}

        {{% else %}}
        {{{{ empty_state('inbox', 'Nenhum {entidade} cadastrado', 'Clique em "Novo {entidade_pascal}" para adicionar o primeiro.', '/{entidade_plural}/cadastrar', 'Novo {entidade_pascal}') }}}}
        {{% endif %}}
    </div>
</div>

{{% include "components/modal_confirmacao.html" %}}
{{% endblock %}}

{{% block scripts %}}
<script>
function confirmarExclusao(id, nome) {{
    abrirModalConfirmacao({{
        url: `/{entidade_plural}/excluir/${{id}}`,
        mensagem: `Tem certeza que deseja excluir "${{nome}}"?`,
    }});
}}
</script>
{{% endblock %}}
'''


def gerar_template_cadastrar(entidade, campos):
    entidade_pascal = pascal_case(entidade)
    entidade_plural = plural(entidade)

    campos_form = "\n\n            ".join(
        f"""{{% call field(name='{nome}', label='{nome.replace('_', ' ').title()}', type='{'checkbox' if tipo == 'bool' else FORM_FIELD_TYPES.get(tipo, 'text')}') %}}
            {{% endcall %}}"""
        if False else  # Usar field simples
        f"""{{{{ field(name='{nome}', label='{nome.replace('_', ' ').title()}', type='{'checkbox' if tipo == 'bool' else FORM_FIELD_TYPES.get(tipo, 'text')}', required={'true' if tipo != 'bool' else 'false'}) }}}}"""
        for nome, tipo in campos
    )

    return f'''\
{{% extends "base_privada.html" %}}
{{% from "macros/form_fields.html" import field with context %}}
{{% from "macros/action_buttons.html" import btn_voltar %}}

{{% block titulo %}}Novo {entidade_pascal}{{% endblock %}}

{{% block content %}}
<div class="row justify-content-center">
    <div class="col-md-8 col-lg-6">
        <div class="d-flex align-items-center gap-3 mb-4">
            {{{{ btn_voltar("/{entidade_plural}") }}}}
            <h2 class="mb-0"><i class="bi bi-plus-circle"></i> Novo {entidade_pascal}</h2>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                <form method="post" action="/{entidade_plural}/cadastrar">
                    {{{{ csrf_input(request) }}}}

                    {campos_form}

                    <div class="d-grid mt-4">
                        <button type="submit" class="btn btn-success btn-lg">
                            <i class="bi bi-check-circle"></i> Cadastrar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{{% endblock %}}
'''


def gerar_template_alterar(entidade, campos):
    entidade_pascal = pascal_case(entidade)
    entidade_plural = plural(entidade)

    campos_form = "\n\n            ".join(
        f"""{{{{ field(name='{nome}', label='{nome.replace('_', ' ').title()}', type='{'checkbox' if tipo == 'bool' else FORM_FIELD_TYPES.get(tipo, 'text')}', value={entidade}.{nome}, required={'true' if tipo != 'bool' else 'false'}) }}}}"""
        for nome, tipo in campos
    )

    return f'''\
{{% extends "base_privada.html" %}}
{{% from "macros/form_fields.html" import field with context %}}
{{% from "macros/action_buttons.html" import btn_voltar %}}

{{% block titulo %}}Editar {entidade_pascal}{{% endblock %}}

{{% block content %}}
<div class="row justify-content-center">
    <div class="col-md-8 col-lg-6">
        <div class="d-flex align-items-center gap-3 mb-4">
            {{{{ btn_voltar("/{entidade_plural}") }}}}
            <h2 class="mb-0"><i class="bi bi-pencil"></i> Editar {entidade_pascal}</h2>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                <form method="post" action="/{entidade_plural}/editar/{{{{{entidade}.id}}}}">
                    {{{{ csrf_input(request) }}}}

                    {campos_form}

                    <div class="d-grid mt-4">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="bi bi-check-circle"></i> Salvar Alterações
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{{% endblock %}}
'''


# ─── Função principal ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Gerador de CRUD para DefaultWebApp")
    parser.add_argument("--entidade", help="Nome da entidade em snake_case (ex: produto)")
    parser.add_argument("--campos", help="Campos em formato 'nome:tipo,nome:tipo' (ex: 'nome:str,preco:float')")
    args = parser.parse_args()

    print()
    print(cor("=" * 60, BLUE))
    print(cor("  DefaultWebApp — Gerador de CRUD", BOLD))
    print(cor("=" * 60, BLUE))
    print()

    # Coletar nome da entidade
    if args.entidade:
        entidade = snake_case(args.entidade)
    else:
        print("  Digite o nome da entidade em singular (ex: produto, pedido, servico):")
        entidade = snake_case(perguntar("Nome da entidade"))
        if not entidade:
            erro_fatal("Nome da entidade não pode ser vazio.")

    entidade_pascal = pascal_case(entidade)

    # Coletar campos
    if args.campos:
        campos_str = args.campos
    else:
        print()
        print("  Campos em formato: nome:tipo,nome:tipo")
        print("  Tipos disponíveis: str, int, float, bool, date, datetime")
        print("  Exemplo: nome:str,preco:float,descricao:str,ativo:bool")
        campos_str = perguntar("Campos", "nome:str,descricao:str")

    campos = parsear_campos(campos_str)
    if not campos:
        erro_fatal("Nenhum campo válido informado.")

    print()
    print(f"  Entidade: {cor(entidade_pascal, BOLD)}")
    print(f"  Campos:   {', '.join(f'{n}:{t}' for n, t in campos)}")
    print()

    # Verificar se arquivos já existem
    arquivos_a_criar = [
        (Path(f"model/{entidade}_model.py"), "Model"),
        (Path(f"sql/{entidade}_sql.py"), "SQL"),
        (Path(f"repo/{entidade}_repo.py"), "Repositório"),
        (Path(f"dtos/{entidade}_dto.py"), "DTO"),
        (Path(f"routes/{entidade}_routes.py"), "Routes"),
        (Path(f"templates/{entidade}/listar.html"), "Template Lista"),
        (Path(f"templates/{entidade}/cadastrar.html"), "Template Cadastrar"),
        (Path(f"templates/{entidade}/alterar.html"), "Template Alterar"),
    ]

    existentes = [(p, n) for p, n in arquivos_a_criar if p.exists()]
    if existentes:
        aviso(f"Os seguintes arquivos já existem:")
        for p, n in existentes:
            print(f"    {n}: {p}")
        try:
            resposta = input(cor("  → Sobrescrever todos? [s/N]: ", CYAN)).strip().lower()
            if resposta not in ("s", "sim", "y", "yes"):
                print(cor("  Geração cancelada.", YELLOW))
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

    # Gerar arquivos
    print()
    print(cor("  Gerando arquivos...", BOLD))

    # Model
    path = Path(f"model/{entidade}_model.py")
    path.write_text(gerar_model(entidade, campos), encoding="utf-8")
    ok(f"model/{entidade}_model.py")

    # SQL
    path = Path(f"sql/{entidade}_sql.py")
    path.write_text(gerar_sql(entidade, campos), encoding="utf-8")
    ok(f"sql/{entidade}_sql.py")

    # Repo
    path = Path(f"repo/{entidade}_repo.py")
    path.write_text(gerar_repo(entidade, campos), encoding="utf-8")
    ok(f"repo/{entidade}_repo.py")

    # DTO
    path = Path(f"dtos/{entidade}_dto.py")
    path.write_text(gerar_dto(entidade, campos), encoding="utf-8")
    ok(f"dtos/{entidade}_dto.py")

    # Routes
    path = Path(f"routes/{entidade}_routes.py")
    path.write_text(gerar_routes(entidade, campos), encoding="utf-8")
    ok(f"routes/{entidade}_routes.py")

    # Templates
    templates_dir = Path(f"templates/{entidade}")
    templates_dir.mkdir(parents=True, exist_ok=True)

    (templates_dir / "listar.html").write_text(gerar_template_listar(entidade, campos), encoding="utf-8")
    ok(f"templates/{entidade}/listar.html")

    (templates_dir / "cadastrar.html").write_text(gerar_template_cadastrar(entidade, campos), encoding="utf-8")
    ok(f"templates/{entidade}/cadastrar.html")

    (templates_dir / "alterar.html").write_text(gerar_template_alterar(entidade, campos), encoding="utf-8")
    ok(f"templates/{entidade}/alterar.html")

    # Próximos passos
    print()
    print(cor("=" * 60, GREEN))
    print(cor("  Geração concluída! Próximos passos:", BOLD))
    print(cor("=" * 60, GREEN))
    print()
    print("  1. Registre em main.py:")
    print(cor(f"     from repo import {entidade}_repo", CYAN))
    print(cor(f"     # Adicione à lista TABELAS:", CYAN))
    print(cor(f"     ({entidade}_repo, \"{entidade}\"),", CYAN))
    print()
    print(cor(f"     from routes.{entidade}_routes import router as {entidade}_router", CYAN))
    print(cor(f"     # Adicione à lista ROUTERS:", CYAN))
    print(cor(f"     ({entidade}_router, [\"{entidade_pascal}\"], \"{entidade}\"),", CYAN))
    print()
    print("  2. Procure por 'TODO' nos arquivos gerados para customizar a lógica")
    print()
    print(f"  3. Acesse: {cor(f'http://localhost:8400/{plural(entidade)}', CYAN)}")
    print()


if __name__ == "__main__":
    main()
