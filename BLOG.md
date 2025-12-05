# Tutorial: Criando um Blog Completo a partir do DefaultWebApp

Este tutorial guia você passo a passo na criação de um blog completo usando como base o repositório DefaultWebApp. Ao final, você terá um sistema de blog funcional com:

- **CRUD de Categorias** (Administrador)
- **CRUD de Artigos** (Autor)
- **Visualização de Artigos** (Leitor, Autor, Administrador)
- **Home Page com os últimos artigos**
- **Busca e filtros de artigos**
- **Editor Markdown integrado**

---

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Fork do Repositório](#2-fork-do-repositório)
3. [Clonando o Repositório](#3-clonando-o-repositório)
4. [Configurando o Ambiente](#4-configurando-o-ambiente)
5. [Configurando os Perfis de Usuário](#5-configurando-os-perfis-de-usuário)
6. [Criando o CRUD de Categorias](#6-criando-o-crud-de-categorias)
7. [Registrando o CRUD de Categorias](#7-registrando-o-crud-de-categorias)
8. [Adicionando Menu e Card de Categorias no Dashboard](#8-adicionando-menu-e-card-de-categorias-no-dashboard)
9. [Testando o CRUD de Categorias](#9-testando-o-crud-de-categorias)
10. [Criando o CRUD de Artigos](#10-criando-o-crud-de-artigos)
11. [Templates de Artigos](#11-templates-de-artigos)
12. [Registrando o CRUD de Artigos](#12-registrando-o-crud-de-artigos)
13. [Adicionando Menu e Card de Artigos no Dashboard](#13-adicionando-menu-e-card-de-artigos-no-dashboard)
14. [Testando o CRUD de Artigos](#14-testando-o-crud-de-artigos)
15. [Templates Base e Home Page](#15-templates-base-e-home-page)
16. [Rotas Públicas e Configuração do main.py](#16-rotas-públicas-e-configuração-do-mainpy)
17. [Testando a Aplicação Completa](#17-testando-a-aplicação-completa)
18. [Resumo dos Arquivos Criados](#18-resumo-dos-arquivos-criados)
19. [Conclusão](#19-conclusão)

---

## 1. Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.10+**
- **Git**
- **Conta no GitHub**
- **Editor de código** (VS Code recomendado)

---

## 2. Fork do Repositório

1. Acesse o repositório upstream: https://github.com/maroquio/DefaultWebApp
2. Clique no botão **Fork** no canto superior direito
3. Selecione sua conta como destino do fork
4. **Renomeie o repositório para "BlogSimples"** no campo "Repository name"
5. Clique em **Create fork**

---

## 3. Clonando o Repositório

Após criar o fork, você deve cloná-lo para sua máquina. Para isso, abra o VS Code em uma pasta vazia de sua preferência e abra o terminal integrado (Ctrl + `). Em seguida, execute os comandos abaixo:

```bash
# Substitua SEU_USUARIO pelo seu usuário do GitHub
git clone https://github.com/SEU_USUARIO/BlogSimples.git
cd BlogSimples
code .
```

Uma nova instância do VS Code será aberta na pasta do projeto clonado como raiz. Mantenha apenas esta instância aberta para evitar conflitos de ambiente, ou seja, feche outras janelas do VS Code que estejam abertas em outras pastas.

### 3.1. Configurando o Git

Em um terminal integrado do novo VS Code aberto na raiz do projeto, configure seu nome e e-mail para os commits:

```bash
# Configure seu nome (usado nos commits)
git config user.name "Seu Nome Completo"

# Configure seu e-mail (deve ser o mesmo do GitHub)
git config user.email "seu.email@exemplo.com"
```

### 3.2. Configurando o upstream

Para receber atualizações futuras do repositório original, execute o seguinte no terminal integrado:

```bash
git remote add upstream https://github.com/maroquio/DefaultWebApp.git
```

---

## 4. Configurando o Ambiente

### 4.1. Criando o ambiente virtual

```bash
# Criar o ambiente virtual
python -m venv .venv

# Ativar o ambiente (Linux/Mac)
source .venv/bin/activate

# Ativar o ambiente (Windows)
.venv\Scripts\activate
```

### 4.2. Instalando dependências

```bash
pip install -r requirements.txt
```

### 4.3. Extensões recomendadas do VS Code

Para uma melhor experiência de desenvolvimento, instale as seguintes extensões no VS Code:

| Extensão | Descrição |
|----------|-----------|
| **Python** | Suporte completo para Python (IntelliSense, debug, linting) |
| **Jinja** | Syntax highlighting para templates Jinja2 |
| **HTML CSS Support** | Autocomplete de classes CSS em arquivos HTML |
| **IntelliSense for CSS class names in HTML** | Autocomplete de classes CSS baseado nos arquivos do projeto |
| **SQLite3 Editor** | Visualizar e editar o banco de dados SQLite |
| **vscode-icons** | Ícones para diferentes tipos de arquivos |
| **Reload** | Botão para recarregar a janela do VS Code rapidamente |

> **Dica:** Para instalar uma extensão, pressione **Ctrl+Shift+X**, pesquise pelo nome e clique em **Install**.

### 4.4. Selecionando o interpretador Python

Após criar o ambiente virtual, é importante configurar o VS Code para usar o interpretador Python correto:

1. Pressione **Ctrl+Shift+P** para abrir a paleta de comandos
2. Digite **Python: Select Interpreter** e pressione Enter
3. Selecione o interpretador que está dentro da pasta `.venv`:
   - Windows: `.venv\Scripts\python.exe`
   - Linux/Mac: `.venv/bin/python`

> **Importante:** Sempre que abrir o projeto, verifique se o interpretador correto está selecionado. Você pode ver o interpretador atual na barra de status do VS Code (canto inferior esquerdo).

### 4.5. Configurando variáveis de ambiente

Copie o arquivo de exemplo e configure:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e atualize as seguintes variáveis:

1. **APP_NAME**: Altere para o nome do seu blog
   ```
   APP_NAME=Blog do João Silva
   ```
   > Substitua "João Silva" pelo seu nome completo.

2. **SECRET_KEY**: Gere uma chave secreta única para sua aplicação
   - Acesse: https://generate-secret.now.sh/64
   - Copie a chave gerada e cole no arquivo `.env`:
   ```
   SECRET_KEY=sua_chave_gerada_aqui
   ```
   > **Importante:** Nunca compartilhe ou versione sua SECRET_KEY.

### 4.6. Testando a instalação

Rode a aplicação com Ctrl + F5 e acesse Acesse http://localhost:8400 para verificar se está funcionando (porta padrão do projeto).

---

## 5. Configurando os Perfis de Usuário

O sistema de blog utiliza dois perfis de usuário diferentes dos existentes. O arquivo `util/perfis.py` do projeto original contém os perfis ADMIN, CLIENTE e VENDEDOR. **Você deve SUBSTITUIR os perfis CLIENTE e VENDEDOR por AUTOR e LEITOR**:

### Arquivo: `util/perfis.py`

Localize o enum `Perfil` e **substitua** os perfis `CLIENTE` e `VENDEDOR` por `AUTOR` e `LEITOR`. O arquivo deve ficar assim:

```python
"""
Enum centralizado para perfis de usuário.

Este módulo define o Enum Perfil que é a FONTE ÚNICA DA VERDADE
para perfis de usuário no sistema.
"""

from util.enum_base import EnumEntidade


class Perfil(EnumEntidade):
    """
    Enum centralizado para perfis de usuário.

    Este é a FONTE ÚNICA DA VERDADE para perfis no sistema.
    SEMPRE use este Enum ao referenciar perfis, NUNCA strings literais.

    Herda de EnumEntidade que fornece métodos úteis:
        - valores(): Lista todos os valores
        - existe(valor): Verifica se valor existe
        - from_valor(valor): Converte string para enum
        - validar(valor): Valida e retorna ou levanta ValueError

    Exemplos:
        - Correto: perfil = Perfil.ADMIN.value
        - Correto: perfil = Perfil.AUTOR.value
        - Correto: perfil = Perfil.LEITOR.value
        - ERRADO: perfil = "admin"
        - ERRADO: perfil = "autor"
        - ERRADO: perfil = "leitor"
    """

    # PERFIS DO SEU SISTEMA #####################################
    ADMIN = "Administrador"
    AUTOR = "Autor"
    LEITOR = "Leitor"
    # FIM DOS PERFIS ############################################

```

### Explicação dos Perfis:

- **Administrador**: Gerencia categorias e tem acesso administrativo completo
- **Autor**: Pode criar, editar e publicar artigos
- **Leitor**: Pode ler artigos publicados

### 5.1. Atualizando o UsuarioLogado

O arquivo `model/usuario_logado_model.py` contém o dataclass `UsuarioLogado` que representa o usuário autenticado. Como substituímos os perfis CLIENTE e VENDEDOR, você deve **substituir os métodos `is_cliente()` e `is_vendedor()` por `is_autor()` e `is_leitor()`**:

```python
    def is_autor(self) -> bool:
        """Verifica se o usuário é autor."""
        return self.perfil == Perfil.AUTOR.value

    def is_leitor(self) -> bool:
        """Verifica se o usuário é leitor."""
        return self.perfil == Perfil.LEITOR.value
```

> **Nota:** O método `is_admin()` deve ser mantido. Remova apenas `is_cliente()` e `is_vendedor()`.

### 5.3. Substituindo os Perfis Antigos Pelos Novos no Restante do Projeto

Clique na ferramenta de busca do VS Code (Ctrl + Shift + F), ative a sensibilidade a maiúsculas e minúsculas e faça as seguintes substituições globais no projeto:

| Buscar               | Substituir por      |
|----------------------|---------------------|
| `CLIENTE`            | `AUTOR`             |
| `VENDEDOR`           | `LEITOR`            |
| `Cliente`            | `Autor`             |
| `Vendedor`           | `Leitor`            |
| `cliente`            | `autor`             |
| `vendedor`           | `leitor`            |


### 5.4. Acertando Uma Substituição Incorreta

Antes da substituição anterior, havia uma função chamada `obter_identificador_cliente` que foi renomeada para `obter_identificador_autor`. Você deve renomeá-la de volta para `obter_identificador_cliente` para manter a consistência com o restante do projeto. 

Para fazer a correção, na ferramenta de busca do VS Code (Ctrl + Shift + F), ative a sensibilidade a maiúsculas e minúsculas e faça a seguinte substituição global no projeto (todas as ocorrências):

| Buscar                       | Substituir por                |
|------------------------------|-------------------------------|
| `obter_identificador_autor`  | `obter_identificador_cliente` |

Feito isso, o projeto estará pronto para que você possa seguir em frente com o restante desse tutorial.

### Salvando seu progresso

Após concluir as alterações desta seção, é importante salvar seu progresso no repositório:

1. Abra o painel **Source Control** do VS Code (Ctrl + Shift + G)
2. Revise as alterações realizadas
3. Digite a seguinte mensagem de commit:
   ```
   configuração dos perfis de usuário (Autor e Leitor)
   ```
4. Clique no botão **Commit** (ícone ✓) para confirmar as alterações
5. Clique no botão **Sync Changes** para sincronizar com o GitHub

> **Dica:** Manter commits frequentes facilita o acompanhamento do progresso e permite reverter alterações caso necessário.

---

## 6. Criando o CRUD de Categorias

### 6.1. Model de Categoria

Crie o arquivo `model/categoria_model.py`:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Categoria:
    """
    Representa uma categoria do blog.

    Atributos:
        id: Identificador único da categoria
        nome: Nome da categoria (ex: "Tecnologia")
        descricao: Descrição opcional da categoria
        data_cadastro: Data/hora de criação do registro
        data_atualizacao: Data/hora da última atualização
    """
    id: Optional[int] = None
    nome: str = ""
    descricao: str = ""
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
```

### 6.2. Queries SQL de Categoria

Crie o arquivo `sql/categoria_sql.py`:

```python
# Queries SQL para operações com categorias

# Cria a tabela categoria se ela não existir
CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS categoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        descricao TEXT,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_atualizacao TIMESTAMP
    )
"""

# Insere uma nova categoria
INSERIR = """
    INSERT INTO categoria (nome, descricao)
    VALUES (?, ?)
"""

# Atualiza uma categoria existente
ALTERAR = """
    UPDATE categoria
    SET nome=?, descricao=?, data_atualizacao=CURRENT_TIMESTAMP
    WHERE id=?
"""

# Exclui uma categoria
EXCLUIR = """
    DELETE FROM categoria WHERE id=?
"""

# Busca todas as categorias ordenadas por nome
OBTER_TODOS = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    ORDER BY nome
"""

# Busca uma categoria por ID
OBTER_POR_ID = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    WHERE id=?
"""

# Busca uma categoria por nome
OBTER_POR_NOME = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    WHERE nome=?
"""
```

### 6.3. Repositório de Categoria

Crie o arquivo `repo/categoria_repo.py`:

```python
from typing import Optional
from model.categoria_model import Categoria
from sql.categoria_sql import *
from util.db_util import obter_conexao


def _row_to_categoria(row) -> Categoria:
    """
    Converte uma linha do banco de dados em objeto Categoria.
    """
    return Categoria(
        id=row["id"],
        nome=row["nome"],
        descricao=row["descricao"],
        data_cadastro=row["data_cadastro"],
        data_atualizacao=row["data_atualizacao"]
    )


def criar_tabela():
    """
    Cria a tabela de categorias se ela não existir.
    Deve ser chamada na inicialização do sistema.
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(categoria: Categoria) -> Optional[Categoria]:
    """
    Insere uma nova categoria no banco de dados.

    Args:
        categoria: Objeto Categoria com nome e descrição

    Returns:
        Categoria com ID preenchido se sucesso, None se erro
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERIR, (categoria.nome, categoria.descricao))

            # Pega o ID gerado automaticamente
            if cursor.lastrowid:
                categoria.id = cursor.lastrowid
                return categoria
            return None
    except Exception as e:
        print(f"Erro ao inserir categoria: {e}")
        return None


def alterar(categoria: Categoria) -> bool:
    """
    Atualiza uma categoria existente.

    Args:
        categoria: Objeto Categoria com ID, nome e descrição

    Returns:
        True se atualizou, False se erro
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                ALTERAR,
                (categoria.nome, categoria.descricao, categoria.id)
            )
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao alterar categoria: {e}")
        return False


def excluir(id: int) -> bool:
    """
    Exclui uma categoria do banco de dados.

    Args:
        id: ID da categoria a ser excluída

    Returns:
        True se excluiu, False se erro ou não encontrou
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(EXCLUIR, (id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao excluir categoria: {e}")
        return False


def obter_por_id(id: int) -> Optional[Categoria]:
    """
    Busca uma categoria por ID.

    Args:
        id: ID da categoria

    Returns:
        Objeto Categoria se encontrou, None se não encontrou
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_ID, (id,))
            row = cursor.fetchone()

            if row:
                return _row_to_categoria(row)
            return None
    except Exception as e:
        print(f"Erro ao obter categoria por ID: {e}")
        return None


def obter_todos() -> list[Categoria]:
    """
    Retorna todas as categorias do banco de dados.

    Returns:
        Lista de objetos Categoria (pode ser vazia)
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_TODOS)
            rows = cursor.fetchall()

            return [_row_to_categoria(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter todas as categorias: {e}")
        return []


def obter_por_nome(nome: str) -> Optional[Categoria]:
    """
    Busca uma categoria pelo nome exato.
    Útil para verificar se já existe categoria com aquele nome.

    Args:
        nome: Nome da categoria (case-sensitive)

    Returns:
        Objeto Categoria se encontrou, None se não encontrou
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_NOME, (nome,))
            row = cursor.fetchone()

            if row:
                return _row_to_categoria(row)
            return None
    except Exception as e:
        print(f"Erro ao obter categoria por nome: {e}")
        return None
```

### 6.4. DTO de Categoria

Crie o arquivo `dtos/categoria_dto.py`:

```python
from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria, validar_comprimento

class CriarCategoriaDTO(BaseModel):
    """
    DTO para validar dados ao criar uma nova categoria.

    Regras:
    - nome: obrigatório, entre 3 e 50 caracteres
    - descricao: opcional, máximo 200 caracteres
    """
    nome: str
    descricao: str = ""

    # Validador do campo 'nome'
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria(
            nome_campo="Nome",
            tamanho_minimo=3,
            tamanho_maximo=50
        )
    )

    # Validador do campo 'descricao'
    _validar_descricao = field_validator("descricao")(
        validar_comprimento(tamanho_maximo=200)
    )


class AlterarCategoriaDTO(BaseModel):
    """
    DTO para validar dados ao editar uma categoria existente.

    Regras: mesmas do CriarCategoriaDTO
    """
    nome: str
    descricao: str = ""

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria(
            nome_campo="Nome",
            tamanho_minimo=3,
            tamanho_maximo=50
        )
    )

    _validar_descricao = field_validator("descricao")(
        validar_comprimento(tamanho_maximo=200)
    )
```

### 6.5. Rotas de Categoria

Crie o arquivo `routes/admin_categorias_routes.py`:

```python
from typing import Optional

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

# DTOs e modelo
from dtos.categoria_dto import CriarCategoriaDTO, AlterarCategoriaDTO
from model.categoria_model import Categoria
from model.usuario_logado_model import UsuarioLogado

# Repositório
from repo import categoria_repo

# Utilitários
from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.exceptions import ErroValidacaoFormulario
from util.perfis import Perfil
from util.template_util import criar_templates

# ----------------------------------------------------------------------
# Configurações do router e dos templates
# ----------------------------------------------------------------------
router = APIRouter(prefix="/admin/categorias")
templates = criar_templates()

# Rate limiter dinâmico: valores podem ser alterados via configuração
admin_categorias_limiter = DynamicRateLimiter(
    chave_max="rate_limit_admin_categorias_max",
    chave_minutos="rate_limit_admin_categorias_minutos",
    padrao_max=10,
    padrao_minutos=1,
    nome="admin_categorias"
)

# ----------------------------------------------------------------------
# Rotas
# ----------------------------------------------------------------------

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Redireciona a raiz para /listar
    """
    return RedirectResponse(
        url="/admin/categorias/listar",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Lista todas as categorias.
    Acessível em: GET /admin/categorias/listar
    """
    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "admin/categorias/listar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "categorias": categorias,
        },
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Exibe o formulário de cadastro.
    Acessível em: GET /admin/categorias/cadastrar
    """
    return templates.TemplateResponse(
        "admin/categorias/cadastrar.html",
        {"request": request, "usuario_logado": usuario_logado},
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
    nome: str = Form(""),
    descricao: str = Form(""),
):
    """
    Processa o cadastro de uma nova categoria.
    Acessível em: POST /admin/categorias/cadastrar
    """
    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente.",
        )
        return RedirectResponse(
            url="/admin/categorias/cadastrar",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Lógica de criação
    try:
        dto = CriarCategoriaDTO(nome=nome, descricao=descricao)

        # Verifica duplicidade
        categoria_existente = categoria_repo.obter_por_nome(dto.nome)
        if categoria_existente:
            informar_erro(request, "Já existe uma categoria com este nome.")
            return RedirectResponse(
                url="/admin/categorias/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        nova_categoria = Categoria(nome=dto.nome, descricao=dto.descricao)
        categoria_inserida = categoria_repo.inserir(nova_categoria)

        if categoria_inserida:
            informar_sucesso(request, "Categoria cadastrada com sucesso!")
            return RedirectResponse(
                url="/admin/categorias/listar",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            informar_erro(request, "Erro ao cadastrar categoria.")
            return RedirectResponse(
                url="/admin/categorias/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER,
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/categorias/cadastrar.html",
            dados_formulario={"nome": nome, "descricao": descricao},
            campo_padrao="nome",
        )


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Exibe o formulário de edição de uma categoria.
    Acessível em: GET /admin/categorias/editar/<id>
    """
    categoria = categoria_repo.obter_por_id(id)

    if not categoria:
        informar_erro(request, "Categoria não encontrada.")
        return RedirectResponse(
            url="/admin/categorias/listar",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return templates.TemplateResponse(
        "admin/categorias/editar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "categoria": categoria,
        },
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
    nome: str = Form(""),
    descricao: str = Form(""),
):
    """
    Processa a edição de uma categoria.
    Acessível em: POST /admin/categorias/editar/<id>
    """
    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente.",
        )
        return RedirectResponse(
            url=f"/admin/categorias/editar/{id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Busca a categoria
    categoria_atual = categoria_repo.obter_por_id(id)
    if not categoria_atual:
        informar_erro(request, "Categoria não encontrada.")
        return RedirectResponse(
            url="/admin/categorias/listar",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    try:
        dto = AlterarCategoriaDTO(nome=nome, descricao=descricao)

        # Se o nome mudou, verifica duplicidade
        if dto.nome != categoria_atual.nome:
            categoria_existente = categoria_repo.obter_por_nome(dto.nome)
            if categoria_existente:
                informar_erro(request, "Já existe uma categoria com este nome.")
                return RedirectResponse(
                    url=f"/admin/categorias/editar/{id}",
                    status_code=status.HTTP_303_SEE_OTHER,
                )

        # Atualiza os campos
        categoria_atual.nome = dto.nome
        categoria_atual.descricao = dto.descricao

        if categoria_repo.alterar(categoria_atual):
            informar_sucesso(request, "Categoria alterada com sucesso!")
            return RedirectResponse(
                url="/admin/categorias/listar",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            informar_erro(request, "Erro ao alterar categoria.")
            return RedirectResponse(
                url=f"/admin/categorias/editar/{id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="admin/categorias/editar.html",
            dados_formulario={
                "nome": nome,
                "descricao": descricao,
                "id": id,
            },
            campo_padrao="nome",
        )


# ----------------------------------------------------------------------
# Endpoint de Exclusão
# ----------------------------------------------------------------------
@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Exclui uma categoria.
    Acessível em: POST /admin/categorias/excluir/<id>
    """
    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            url="/admin/categorias/listar",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Busca a categoria
    categoria = categoria_repo.obter_por_id(id)
    if not categoria:
        informar_erro(request, "Categoria não encontrada.")
        return RedirectResponse(
            url="/admin/categorias/listar",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Exclui do banco
    if categoria_repo.excluir(id):
        informar_sucesso(request, f"Categoria '{categoria.nome}' excluída com sucesso!")
    else:
        informar_erro(request, "Erro ao excluir categoria.")

    return RedirectResponse(
        url="/admin/categorias/listar",
        status_code=status.HTTP_303_SEE_OTHER,
    )
```

### 6.6. Templates de Categoria

#### 6.6.1. Template de Listagem

Crie a pasta `templates/admin/categorias/` e dentro dela crie o arquivo `listar.html`:

```html
{% extends "base_privada.html" %}

{% block titulo %}Gerenciar Categorias{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-folder"></i> Gerenciar Categorias</h2>
            <a href="/admin/categorias/cadastrar" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> Nova Categoria
            </a>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                {% if categorias %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Nome</th>
                                <th scope="col">Descrição</th>
                                <th scope="col">Data Cadastro</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for categoria in categorias %}
                            <tr>
                                <td>{{ categoria.id }}</td>
                                <td><strong>{{ categoria.nome }}</strong></td>
                                <td>{{ categoria.descricao if categoria.descricao else '-' }}</td>
                                <td>{{ categoria.data_cadastro|data_br if categoria.data_cadastro else '-' }}</td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/admin/categorias/editar/{{ categoria.id }}"
                                            class="btn btn-outline-primary" title="Editar"
                                            aria-label="Editar categoria {{ categoria.nome }}">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger" title="Excluir"
                                            aria-label="Excluir categoria {{ categoria.nome }}"
                                            onclick="excluirCategoria({{ categoria.id }}, '{{ categoria.nome|replace("'", "\\'") }}', '{{ categoria.descricao|replace("'", "\\'") if categoria.descricao else "" }}')">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                <div class="mt-3">
                    <small class="text-muted">
                        Total: {{ categorias|length }} categoria(s)
                    </small>
                </div>
                {% else %}
                <div class="alert alert-info text-center mb-0">
                    <i class="bi bi-info-circle"></i> Nenhuma categoria cadastrada.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    /**
     * Função para excluir uma categoria
     */
    function excluirCategoria(categoriaId, categoriaNome, categoriaDescricao) {
        const detalhes = `
        <div class="card bg-light">
            <div class="card-body">
                <table class="table table-sm table-borderless mb-0">
                    <tr>
                        <th scope="row" width="30%">Nome:</th>
                        <td><strong>${categoriaNome}</strong></td>
                    </tr>
                    <tr>
                        <th scope="row">Descrição:</th>
                        <td>${categoriaDescricao || '-'}</td>
                    </tr>
                </table>
            </div>
        </div>
    `;

        abrirModalConfirmacao({
            url: `/admin/categorias/excluir/${categoriaId}`,
            mensagem: 'Tem certeza que deseja excluir esta categoria?',
            detalhes: detalhes
        });
    }
</script>
{% endblock %}
```

**ATENÇÃO:** Não se preocupe caso veja algum erro de checagem de código no VS Code relacionado ao template acima e aos demais que forem criados. Isso ocorre porque algumas variáveis são dinâmicas e só estarão disponíveis em tempo de execução. Desde que o template funcione corretamente ao rodar a aplicação, você pode ignorar esses avisos.

#### 6.6.2. Template de Cadastro

Crie o arquivo `templates/admin/categorias/cadastrar.html`:

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Cadastrar Categoria{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-folder-plus"></i> Cadastrar Nova Categoria</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/categorias/cadastrar">
                {{ csrf_input() }}
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(
                                name='nome',
                                label='Nome da Categoria',
                                type='text',
                                required=true,
                                placeholder='Ex: Tecnologia, Esportes, Política...',
                                help_text='Nome único para identificar a categoria (3-50 caracteres)'
                            ) }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(
                                name='descricao',
                                label='Descrição',
                                type='textarea',
                                required=false,
                                placeholder='Descrição opcional da categoria...',
                                help_text='Breve descrição sobre o que essa categoria abrange (máx 200 caracteres)',
                                rows=3
                            ) }}
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Cadastrar
                        </button>
                        <a href="/admin/categorias/listar" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

#### 6.6.3. Template de Edição

Crie o arquivo `templates/admin/categorias/editar.html`:

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Editar Categoria{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-folder-check"></i> Editar Categoria</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/categorias/editar/{{ dados.id if dados is defined and dados.id else categoria.id }}">
                {{ csrf_input() }}
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(
                                name='nome',
                                label='Nome da Categoria',
                                type='text',
                                required=true,
                                placeholder='Ex: Tecnologia, Esportes, Política...',
                                help_text='Nome único para identificar a categoria (3-50 caracteres)',
                                value=dados.nome if dados is defined and dados.nome else categoria.nome
                            ) }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(
                                name='descricao',
                                label='Descrição',
                                type='textarea',
                                required=false,
                                placeholder='Descrição opcional da categoria...',
                                help_text='Breve descrição sobre o que essa categoria abrange (máx 200 caracteres)',
                                rows=3,
                                value=dados.descricao if dados is defined and dados.descricao else categoria.descricao
                            ) }}
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Salvar Alterações
                        </button>
                        <a href="/admin/categorias/listar" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

### Salvando seu progresso

Após concluir as alterações desta seção, é importante salvar seu progresso no repositório:

1. Abra o painel **Source Control** do VS Code (Ctrl + Shift + G)
2. Revise as alterações realizadas
3. Digite a seguinte mensagem de commit:
   ```
   criação do CRUD de Categorias (model, sql, repo, dto, routes, templates)
   ```
4. Clique no botão **Commit** (ícone ✓) para confirmar as alterações
5. Clique no botão **Sync Changes** para sincronizar com o GitHub

> **Dica:** Manter commits frequentes facilita o acompanhamento do progresso e permite reverter alterações caso necessário.

---

## 7. Registrando o CRUD de Categorias

Antes de testar o CRUD de Categorias, precisamos registrá-lo no `main.py` para que a aplicação reconheça as novas rotas e crie a tabela no banco de dados.

### 7.1. Adicionar import do repositório

No início do arquivo `main.py`, no final da linha 26, adicione `categoria_repo`. A linha vai ficar assim:

```python
from repo import chat_sala_repo, chat_participante_repo, chat_mensagem_repo, categoria_repo
```

### 7.2. Adicionar import das rotas

Ainda no `main.py`, no final da seção de importação de rotas, aproximadamente depois da linha 38, adicione a linha a seguir:

```python
from routes.admin_categorias_routes import router as admin_categorias_router
```

### 7.3. Adicionar tabela na lista TABELAS

No arquivo `main.py`, localize a lista `TABELAS` e adicione a nova tabela `categoria` ao final da listagem:

```python
TABELAS = [
    (usuario_repo, "usuario"),
    (configuracao_repo, "configuracao"),
    (chamado_repo, "chamado"),
    (chamado_interacao_repo, "chamado_interacao"),
    (chat_sala_repo, "chat_sala"),
    (chat_participante_repo, "chat_participante"),
    (chat_mensagem_repo, "chat_mensagem"),
    (categoria_repo, "categoria"),  # NOVA TABELA
]
```

### 7.4. Adicionar router na lista ROUTERS

Localize a lista `ROUTERS` e adicione o novo router, logo depois da linha `(admin_chamados_router, ["Admin - Chamados"], "admin de chamados"),`, que provavelmente está na linha 118. A linha a ser adicionada é:

```python
    (admin_categorias_router, ["Admin - Categorias"], "admin de categorias"),  # NOVO ROUTER
```

O bloco `ROUTERS` ficará assim:

```python
ROUTERS = [
    (auth_router, ["Autenticação"], "autenticação"),
    (chamados_router, ["Chamados"], "chamados"),
    (admin_usuarios_router, ["Admin - Usuários"], "admin de usuários"),
    (admin_config_router, ["Admin - Configurações"], "admin de configurações"),
    (admin_backups_router, ["Admin - Backups"], "admin de backups"),
    (admin_chamados_router, ["Admin - Chamados"], "admin de chamados"),
    (admin_categorias_router, ["Admin - Categorias"], "admin de categorias"),  # NOVO ROUTER
    (usuario_router, ["Usuário"], "usuário"),
    (chat_router, ["Chat"], "chat"),
    (public_router, ["Público"], "público"),  # Deve ficar por último
    (examples_router, ["Exemplos"], "exemplos"),  # Deve ficar por último
]
```

> **IMPORTANTE**: Os routers `public_router` e `examples_router` devem ser incluídos **por último** para evitar conflitos de rotas com "/".

### Salvando seu progresso

Após concluir as alterações desta seção, é importante salvar seu progresso no repositório:

1. Abra o painel **Source Control** do VS Code (Ctrl + Shift + G)
2. Revise as alterações realizadas
3. Digite a seguinte mensagem de commit:
   ```
   registro do CRUD de Categorias no main.py
   ```
4. Clique no botão **Commit** (ícone ✓) para confirmar as alterações
5. Clique no botão **Sync Changes** para sincronizar com o GitHub

> **Dica:** Manter commits frequentes facilita o acompanhamento do progresso e permite reverter alterações caso necessário.

---

## 8. Adicionando Menu e Card de Categorias no Dashboard

Agora vamos adicionar o acesso ao CRUD de Categorias no painel do administrador.

### 8.1. Adicionando o link no menu de navegação

No arquivo `templates/base_privada.html`, localize a seção de navegação do administrador (dentro do bloco `{% if usuario_logado and usuario_logado.perfil == 'Administrador' %}` da linha 52).

Após o final do link de **Backup** na linha 82, de um ENTER e adicione o link para **Categorias**:

```html
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if '/admin/categorias/' in request.path else '' }}"
                            href="/admin/categorias/listar"
                            {{ 'aria-current=page' if '/admin/categorias/' in request.path else '' }}>Categorias</a>
                    </li>
```

### 8.2. Adicionando o card no dashboard do administrador

No arquivo `templates/dashboard.html`, localize a seção de cards do administrador (dentro do bloco `{% if usuario_logado and usuario_logado.perfil == 'Administrador' %}`).

Adicione um novo card para **Categorias** junto aos outros cards administrativos:

```html
                <!-- Card Categorias -->
                <div class="col">
                    <div class="card h-100 shadow-sm shadow-hover">
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <i class="bi bi-folder text-primary" style="font-size: 3rem;"></i>
                            </div>
                            <h5 class="card-title">Categorias</h5>
                            <p class="card-text text-muted">
                                Gerencie as categorias de artigos do blog
                            </p>
                            <a href="/admin/categorias/listar" class="btn btn-primary">
                                <i class="bi bi-folder"></i> Acessar
                            </a>
                        </div>
                    </div>
                </div>
```

> **Resultado esperado:** O administrador verá o link "Categorias" no menu superior e um card de acesso rápido na página inicial (dashboard).

### Salvando seu progresso

Após concluir as alterações desta seção, é importante salvar seu progresso no repositório:

1. Abra o painel **Source Control** do VS Code (Ctrl + Shift + G)
2. Revise as alterações realizadas
3. Digite a seguinte mensagem de commit:
   ```
   adição do menu e card de Categorias no dashboard
   ```
4. Clique no botão **Commit** (ícone ✓) para confirmar as alterações
5. Clique no botão **Sync Changes** para sincronizar com o GitHub

> **Dica:** Manter commits frequentes facilita o acompanhamento do progresso e permite reverter alterações caso necessário.

---

## 9. Testando o CRUD de Categorias

Agora vamos testar se o CRUD de Categorias está funcionando corretamente.

### 9.1. Iniciando a aplicação

No VS Code, pressione **Ctrl+F5** para executar a aplicação sem depuração (ou execute `python main.py` no terminal).

Você deverá ver algo como:

```
============================================================
                    BLOG DO FULANO
============================================================
Modo de execução: Development
============================================================

INFO:     Tabela 'categoria' verificada/criada com sucesso.
...
INFO:     Uvicorn running on http://0.0.0.0:8400 (Press CTRL+C to quit)
```

### 9.2. Acessando como Administrador

1. Acesse http://localhost:8400 no navegador
2. Clique em **Entrar** ou acesse http://localhost:8400/login
3. Faça login com as credenciais do administrador padrão:
   - **E-mail:** `padrao@administrador.com`
   - **Senha:** `1234aA@#`

### 9.3. Testando as funcionalidades

Após o login, teste as seguintes funcionalidades:

1. **Verificar o menu:** O link "Categorias" deve aparecer no menu superior
2. **Verificar o dashboard:** O card "Categorias" deve aparecer na página inicial
3. **Listar categorias:** Clique em "Categorias" - a lista deve estar vazia inicialmente
4. **Cadastrar categoria:** Clique em "Nova Categoria" e cadastre algumas categorias de teste:
   - Nome: "Tecnologia", Descrição: "Artigos sobre tecnologia e programação"
   - Nome: "Esportes", Descrição: "Notícias e artigos sobre esportes"
   - Nome: "Cultura", Descrição: "Arte, música, cinema e literatura"
5. **Editar categoria:** Altere o nome da categoria "Cultura" para "Cultura e Entretenimento", salve e depois altere novamente para "Cultura"
6. **Excluir categoria:** Crie uma categoria chamada "Teste Exclusão" e depois exclua essa categoria

> **Dica:** Se encontrar erros, verifique o terminal onde a aplicação está rodando para ver as mensagens de log.

---

## 10. Criando o CRUD de Artigos

### 10.1. Model de Artigo

Crie o arquivo `model/artigo_model.py`:

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class StatusArtigo(Enum):
    RASCUNHO = "Rascunho"
    FINALIZADO = "Finalizado"
    PUBLICADO = "Publicado"
    PAUSADO = "Pausado"


@dataclass
class Artigo:
    # Campos obrigatórios (com defaults para permitir criação)
    titulo: str = ""
    conteudo: str = ""
    status: str = "Rascunho"
    usuario_id: int = 0
    categoria_id: int = 0
    # Campos opcionais
    id: Optional[int] = None
    resumo: Optional[str] = None
    qtde_visualizacoes: int = 0
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    data_publicacao: Optional[datetime] = None
    data_pausa: Optional[datetime] = None
    # Campos do JOIN (para exibição)
    usuario_nome: Optional[str] = None
    usuario_email: Optional[str] = None
    categoria_nome: Optional[str] = None
```

### 10.2. Queries SQL de Artigo

Crie o arquivo `sql/artigo_sql.py`:

```python
# Queries SQL para operações com artigos

# Cria a tabela artigo se ela não existir
CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS artigo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT UNIQUE NOT NULL,
        resumo TEXT,
        conteudo TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Rascunho',
        usuario_id INTEGER NOT NULL,
        categoria_id INTEGER NOT NULL,
        qtde_visualizacoes INTEGER NOT NULL DEFAULT 0,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_atualizacao TIMESTAMP,
        data_publicacao TIMESTAMP,
        data_pausa TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuario(id),
        FOREIGN KEY (categoria_id) REFERENCES categoria(id)
    )
"""

# Insere um novo artigo
INSERIR = """
    INSERT INTO artigo (titulo, resumo, conteudo, status, usuario_id, categoria_id)
    VALUES (?, ?, ?, ?, ?, ?)
"""

# Atualiza um artigo existente
ALTERAR = """
    UPDATE artigo
    SET titulo=?, resumo=?, conteudo=?, status=?, categoria_id=?, data_atualizacao=CURRENT_TIMESTAMP
    WHERE id=?
"""

# Atualiza status do artigo
ALTERAR_STATUS = """
    UPDATE artigo
    SET status=?, data_atualizacao=CURRENT_TIMESTAMP,
        data_publicacao = CASE WHEN ? = 'Publicado' THEN CURRENT_TIMESTAMP ELSE data_publicacao END,
        data_pausa = CASE WHEN ? = 'Pausado' THEN CURRENT_TIMESTAMP ELSE data_pausa END
    WHERE id=?
"""

# Exclui um artigo
EXCLUIR = """
    DELETE FROM artigo WHERE id=?
"""

# Busca todos os artigos ordenados por data de cadastro (mais recentes primeiro)
OBTER_TODOS = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    ORDER BY a.data_cadastro DESC
"""

# Busca artigos por usuário (autor)
OBTER_POR_USUARIO = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    WHERE a.usuario_id = ?
    ORDER BY a.data_cadastro DESC
"""

# Busca artigos publicados (para exibição pública)
OBTER_PUBLICADOS = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    WHERE a.status = 'Publicado'
    ORDER BY a.data_publicacao DESC
"""

# Busca os últimos N artigos publicados
OBTER_ULTIMOS_PUBLICADOS = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    WHERE a.status = 'Publicado'
    ORDER BY a.data_publicacao DESC
    LIMIT ?
"""

# Busca um artigo por ID
OBTER_POR_ID = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    WHERE a.id = ?
"""

# Busca artigos por título (busca parcial)
BUSCAR_POR_TITULO = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    WHERE a.status = 'Publicado' AND a.titulo LIKE ?
    ORDER BY a.data_publicacao DESC
"""

# Busca artigos por categoria
OBTER_POR_CATEGORIA = """
    SELECT a.id, a.titulo, a.resumo, a.conteudo, a.status, a.usuario_id, a.categoria_id,
           a.qtde_visualizacoes, a.data_cadastro, a.data_atualizacao,
           a.data_publicacao, a.data_pausa,
           u.nome as usuario_nome, u.email as usuario_email,
           c.nome as categoria_nome
    FROM artigo a
    LEFT JOIN usuario u ON a.usuario_id = u.id
    LEFT JOIN categoria c ON a.categoria_id = c.id
    WHERE a.status = 'Publicado' AND a.categoria_id = ?
    ORDER BY a.data_publicacao DESC
"""

# Incrementa visualizações
INCREMENTAR_VISUALIZACOES = """
    UPDATE artigo SET qtde_visualizacoes = qtde_visualizacoes + 1 WHERE id = ?
"""

# Conta quantidade de artigos
OBTER_QUANTIDADE = """
    SELECT COUNT(*) as quantidade FROM artigo
"""

# Conta quantidade de artigos publicados
OBTER_QUANTIDADE_PUBLICADOS = """
    SELECT COUNT(*) as quantidade FROM artigo WHERE status = 'Publicado'
"""

# Verifica se título já existe
VERIFICAR_TITULO_EXISTE = """
    SELECT id FROM artigo WHERE titulo = ? AND id != ?
"""
```

### 10.3. Repositório de Artigo

Crie o arquivo `repo/artigo_repo.py`:

```python
from typing import Optional
from model.artigo_model import Artigo
from sql.artigo_sql import *
from util.db_util import obter_conexao


def _row_to_artigo(row) -> Artigo:
    """
    Converte uma linha do banco de dados em objeto Artigo.
    """
    return Artigo(
        id=row["id"],
        titulo=row["titulo"],
        resumo=row["resumo"] if "resumo" in row.keys() else None,
        conteudo=row["conteudo"],
        status=row["status"],
        usuario_id=row["usuario_id"],
        categoria_id=row["categoria_id"],
        qtde_visualizacoes=row["qtde_visualizacoes"] if "qtde_visualizacoes" in row.keys() else 0,
        data_cadastro=row["data_cadastro"] if "data_cadastro" in row.keys() else None,
        data_atualizacao=row["data_atualizacao"] if "data_atualizacao" in row.keys() else None,
        data_publicacao=row["data_publicacao"] if "data_publicacao" in row.keys() else None,
        data_pausa=row["data_pausa"] if "data_pausa" in row.keys() else None,
        usuario_nome=row["usuario_nome"] if "usuario_nome" in row.keys() else None,
        usuario_email=row["usuario_email"] if "usuario_email" in row.keys() else None,
        categoria_nome=row["categoria_nome"] if "categoria_nome" in row.keys() else None,
    )


def criar_tabela() -> bool:
    """Cria a tabela de artigos se não existir."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(CRIAR_TABELA)
            return True
    except Exception as e:
        print(f"Erro ao criar tabela artigo: {e}")
        return False


def inserir(artigo: Artigo) -> Optional[int]:
    """Insere um novo artigo e retorna o ID gerado."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERIR, (
                artigo.titulo,
                artigo.resumo,
                artigo.conteudo,
                artigo.status,
                artigo.usuario_id,
                artigo.categoria_id
            ))
            return cursor.lastrowid
    except Exception as e:
        print(f"Erro ao inserir artigo: {e}")
        return None


def alterar(artigo: Artigo) -> bool:
    """Atualiza um artigo existente."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(ALTERAR, (
                artigo.titulo,
                artigo.resumo,
                artigo.conteudo,
                artigo.status,
                artigo.categoria_id,
                artigo.id
            ))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao alterar artigo: {e}")
        return False


def alterar_status(id: int, status: str) -> bool:
    """Atualiza apenas o status de um artigo."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(ALTERAR_STATUS, (status, status, status, id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao alterar status do artigo: {e}")
        return False


def excluir(id: int) -> bool:
    """Exclui um artigo pelo ID."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(EXCLUIR, (id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao excluir artigo: {e}")
        return False


def obter_por_id(id: int) -> Optional[Artigo]:
    """Busca um artigo pelo ID."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_ID, (id,))
            row = cursor.fetchone()
            if row:
                return _row_to_artigo(row)
            return None
    except Exception as e:
        print(f"Erro ao obter artigo por ID: {e}")
        return None


def obter_todos() -> list[Artigo]:
    """Retorna todos os artigos."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_TODOS)
            rows = cursor.fetchall()
            return [_row_to_artigo(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter todos os artigos: {e}")
        return []


def obter_por_usuario(usuario_id: int) -> list[Artigo]:
    """Retorna todos os artigos de um usuário específico."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_USUARIO, (usuario_id,))
            rows = cursor.fetchall()
            return [_row_to_artigo(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter artigos por usuário: {e}")
        return []


def obter_publicados() -> list[Artigo]:
    """Retorna todos os artigos publicados."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_PUBLICADOS)
            rows = cursor.fetchall()
            return [_row_to_artigo(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter artigos publicados: {e}")
        return []


def obter_ultimos_publicados(limite: int = 6) -> list[Artigo]:
    """Retorna os últimos N artigos publicados."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_ULTIMOS_PUBLICADOS, (limite,))
            rows = cursor.fetchall()
            return [_row_to_artigo(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter últimos artigos publicados: {e}")
        return []


def buscar_por_titulo(termo: str) -> list[Artigo]:
    """Busca artigos publicados pelo título."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(BUSCAR_POR_TITULO, (f"%{termo}%",))
            rows = cursor.fetchall()
            return [_row_to_artigo(row) for row in rows]
    except Exception as e:
        print(f"Erro ao buscar artigos por título: {e}")
        return []


def obter_por_categoria(categoria_id: int) -> list[Artigo]:
    """Retorna artigos publicados de uma categoria específica."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_CATEGORIA, (categoria_id,))
            rows = cursor.fetchall()
            return [_row_to_artigo(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter artigos por categoria: {e}")
        return []


def incrementar_visualizacoes(id: int) -> bool:
    """Incrementa o contador de visualizações de um artigo."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(INCREMENTAR_VISUALIZACOES, (id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao incrementar visualizações: {e}")
        return False


def obter_quantidade() -> int:
    """Retorna a quantidade total de artigos."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_QUANTIDADE)
            row = cursor.fetchone()
            return row["quantidade"] if row else 0
    except Exception as e:
        print(f"Erro ao obter quantidade de artigos: {e}")
        return 0


def obter_quantidade_publicados() -> int:
    """Retorna a quantidade de artigos publicados."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_QUANTIDADE_PUBLICADOS)
            row = cursor.fetchone()
            return row["quantidade"] if row else 0
    except Exception as e:
        print(f"Erro ao obter quantidade de artigos publicados: {e}")
        return 0


def titulo_existe(titulo: str, excluir_id: int = 0) -> bool:
    """Verifica se um título já existe (excluindo um ID específico)."""
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(VERIFICAR_TITULO_EXISTE, (titulo, excluir_id))
            row = cursor.fetchone()
            return row is not None
    except Exception as e:
        print(f"Erro ao verificar título: {e}")
        return False
```

### 10.4. DTO de Artigo

Crie o arquivo `dtos/artigo_dto.py`:

```python
from pydantic import BaseModel, field_validator
from model.artigo_model import StatusArtigo
from dtos.validators import (
    validar_id_positivo,
    validar_string_obrigatoria,
    validar_comprimento,
    validar_tipo,
)


class CriarArtigoDTO(BaseModel):
    titulo: str
    resumo: str = ""
    conteudo: str
    status: str = "Rascunho"
    categoria_id: int

    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria(
            nome_campo="Título",
            tamanho_minimo=5,
            tamanho_maximo=200
        )
    )
    _validar_resumo = field_validator("resumo")(
        validar_comprimento(tamanho_maximo=500)
    )
    _validar_conteudo = field_validator("conteudo")(
        validar_string_obrigatoria(
            nome_campo="Conteúdo",
            tamanho_minimo=50,
            tamanho_maximo=50000
        )
    )
    _validar_status = field_validator("status")(validar_tipo("Status", StatusArtigo))
    _validar_id_categoria = field_validator("categoria_id")(validar_id_positivo("Categoria"))


class AlterarArtigoDTO(BaseModel):
    id: int
    titulo: str
    resumo: str = ""
    conteudo: str
    status: str
    categoria_id: int

    _validar_id = field_validator("id")(validar_id_positivo("ID"))
    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria(
            nome_campo="Título",
            tamanho_minimo=5,
            tamanho_maximo=200
        )
    )
    _validar_resumo = field_validator("resumo")(
        validar_comprimento(tamanho_maximo=500)
    )
    _validar_conteudo = field_validator("conteudo")(
        validar_string_obrigatoria(
            nome_campo="Conteúdo",
            tamanho_minimo=50,
            tamanho_maximo=50000
        )
    )
    _validar_status = field_validator("status")(validar_tipo("Status", StatusArtigo))
    _validar_id_categoria = field_validator("categoria_id")(validar_id_positivo("Categoria"))
```

### 10.5. Rotas de Artigos

Crie o arquivo `routes/artigos_routes.py`:

```python
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.artigo_dto import CriarArtigoDTO, AlterarArtigoDTO
from model.artigo_model import Artigo, StatusArtigo
from model.usuario_logado_model import UsuarioLogado
from repo import artigo_repo, categoria_repo
from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.exceptions import ErroValidacaoFormulario
from util.perfis import Perfil
from util.template_util import criar_templates
from util.logger_config import logger

router = APIRouter(prefix="/artigos")
templates = criar_templates()

# Rate limiter dinâmico: valores podem ser alterados via configuração
artigos_limiter = DynamicRateLimiter(
    chave_max="rate_limit_artigos_max",
    chave_minutos="rate_limit_artigos_minutos",
    padrao_max=20,
    padrao_minutos=1,
    nome="artigos"
)


@router.get("/meus")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def meus_artigos(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    """Lista os artigos do autor logado."""
    artigos = artigo_repo.obter_por_usuario(usuario_logado.id)

    return templates.TemplateResponse(
        "artigos/listar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "artigos": artigos,
            "status_artigo": StatusArtigo,
        },
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def get_cadastrar(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exibe o formulário de cadastro de artigo."""
    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "artigos/cadastrar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "categorias": categorias,
            "status_artigo": StatusArtigo,
        },
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
    titulo: str = Form(""),
    resumo: str = Form(""),
    conteudo: str = Form(""),
    acao: str = Form("rascunho"),
    categoria_id: int = Form(0),
):
    """Processa o cadastro de um novo artigo."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    ip = obter_identificador_cliente(request)
    if not artigos_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente.",
        )
        return RedirectResponse(
            url="/artigos/cadastrar",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    categorias = categoria_repo.obter_todos()

    # Determina status baseado na ação do botão clicado
    status_artigo = "Rascunho" if acao == "rascunho" else "Finalizado"

    try:
        dto = CriarArtigoDTO(
            titulo=titulo,
            resumo=resumo,
            conteudo=conteudo,
            status=status_artigo,
            categoria_id=categoria_id
        )

        # Verifica se título já existe
        if artigo_repo.titulo_existe(dto.titulo):
            informar_erro(request, "Já existe um artigo com este título.")
            return RedirectResponse(
                url="/artigos/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        novo_artigo = Artigo(
            id=0,
            titulo=dto.titulo,
            resumo=dto.resumo,
            conteudo=dto.conteudo,
            status=dto.status,
            usuario_id=usuario_logado.id,
            categoria_id=dto.categoria_id
        )

        artigo_id = artigo_repo.inserir(novo_artigo)

        if artigo_id:
            logger.info(f"Artigo '{dto.titulo}' criado por usuário {usuario_logado.id}")
            informar_sucesso(request, "Artigo cadastrado com sucesso!")
            return RedirectResponse(
                url="/artigos/meus",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            informar_erro(request, "Erro ao cadastrar artigo.")
            return RedirectResponse(
                url="/artigos/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER,
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="artigos/cadastrar.html",
            dados_formulario={
                "titulo": titulo,
                "resumo": resumo,
                "conteudo": conteudo,
                "categoria_id": categoria_id,
                "categorias": categorias,
            },
            campo_padrao="titulo",
        )


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def get_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exibe o formulário de edição de artigo."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    artigo = artigo_repo.obter_por_id(id)

    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica se o usuário é o autor do artigo ou admin
    if artigo.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
        informar_erro(request, "Você não tem permissão para editar este artigo.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "artigos/editar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "artigo": artigo,
            "categorias": categorias,
            "status_artigo": StatusArtigo,
        },
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
    titulo: str = Form(""),
    resumo: str = Form(""),
    conteudo: str = Form(""),
    acao: str = Form("rascunho"),
    categoria_id: int = Form(0),
):
    """Processa a edição de um artigo."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    ip = obter_identificador_cliente(request)
    if not artigos_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente.",
        )
        return RedirectResponse(
            url=f"/artigos/editar/{id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    artigo_atual = artigo_repo.obter_por_id(id)
    if not artigo_atual:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica permissão
    if artigo_atual.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
        informar_erro(request, "Você não tem permissão para editar este artigo.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    categorias = categoria_repo.obter_todos()

    # Determina status baseado na ação do botão clicado
    status_artigo = "Rascunho" if acao == "rascunho" else "Finalizado"

    try:
        dto = AlterarArtigoDTO(
            id=id,
            titulo=titulo,
            resumo=resumo,
            conteudo=conteudo,
            status=status_artigo,
            categoria_id=categoria_id
        )

        # Verifica duplicidade de título
        if dto.titulo != artigo_atual.titulo and artigo_repo.titulo_existe(dto.titulo, id):
            informar_erro(request, "Já existe um artigo com este título.")
            return RedirectResponse(
                url=f"/artigos/editar/{id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        artigo_atual.titulo = dto.titulo
        artigo_atual.resumo = dto.resumo
        artigo_atual.conteudo = dto.conteudo
        artigo_atual.status = dto.status
        artigo_atual.categoria_id = dto.categoria_id

        if artigo_repo.alterar(artigo_atual):
            logger.info(f"Artigo {id} alterado por usuário {usuario_logado.id}")
            informar_sucesso(request, "Artigo alterado com sucesso!")
            return RedirectResponse(
                url="/artigos/meus",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            informar_erro(request, "Erro ao alterar artigo.")
            return RedirectResponse(
                url=f"/artigos/editar/{id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

    except ValidationError as e:
        raise ErroValidacaoFormulario(
            validation_error=e,
            template_path="artigos/editar.html",
            dados_formulario={
                "titulo": titulo,
                "resumo": resumo,
                "conteudo": conteudo,
                "categoria_id": categoria_id,
                "id": id,
                "artigo": artigo_atual,
                "categorias": categorias,
            },
            campo_padrao="titulo",
        )


@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def post_excluir(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exclui um artigo."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    ip = obter_identificador_cliente(request)
    if not artigos_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    artigo = artigo_repo.obter_por_id(id)
    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica permissão
    if artigo.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
        informar_erro(request, "Você não tem permissão para excluir este artigo.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if artigo_repo.excluir(id):
        logger.info(f"Artigo {id} excluído por usuário {usuario_logado.id}")
        informar_sucesso(request, f"Artigo '{artigo.titulo}' excluído com sucesso!")
    else:
        informar_erro(request, "Erro ao excluir artigo.")

    return RedirectResponse(
        url="/artigos/meus",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/publicar/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def post_publicar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Publica um artigo."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    artigo = artigo_repo.obter_por_id(id)
    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica permissão
    if artigo.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
        informar_erro(request, "Você não tem permissão para publicar este artigo.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if artigo_repo.alterar_status(id, StatusArtigo.PUBLICADO.value):
        logger.info(f"Artigo {id} publicado por usuário {usuario_logado.id}")
        informar_sucesso(request, "Artigo publicado com sucesso!")
    else:
        informar_erro(request, "Erro ao publicar artigo.")

    return RedirectResponse(
        url="/artigos/meus",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/pausar/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def post_pausar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Pausa um artigo publicado."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    artigo = artigo_repo.obter_por_id(id)
    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica permissão
    if artigo.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
        informar_erro(request, "Você não tem permissão para pausar este artigo.")
        return RedirectResponse(
            url="/artigos/meus",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if artigo_repo.alterar_status(id, StatusArtigo.PAUSADO.value):
        logger.info(f"Artigo {id} pausado por usuário {usuario_logado.id}")
        informar_sucesso(request, "Artigo pausado com sucesso!")
    else:
        informar_erro(request, "Erro ao pausar artigo.")

    return RedirectResponse(
        url="/artigos/meus",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# =====================================================
# ROTAS PÚBLICAS (para leitores)
# =====================================================

@router.get("/")
async def listar_artigos(
    request: Request,
    q: str = "",
    categoria: int = 0,
    ordem: str = "recentes",
):
    """Lista artigos publicados com busca e filtros."""
    from util.auth_decorator import obter_usuario_logado
    usuario_logado = obter_usuario_logado(request)

    if q:
        artigos = artigo_repo.buscar_por_titulo(q)
    elif categoria > 0:
        artigos = artigo_repo.obter_por_categoria(categoria)
    else:
        artigos = artigo_repo.obter_publicados()

    # Ordenação
    if ordem == "antigos":
        artigos = sorted(artigos, key=lambda a: a.data_publicacao or a.data_cadastro or datetime.min)
    elif ordem == "visualizacoes":
        artigos = sorted(artigos, key=lambda a: a.qtde_visualizacoes or 0, reverse=True)
    # Default é "recentes" (já vem ordenado do banco)

    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "artigos/buscar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "artigos": artigos,
            "categorias": categorias,
            "termo_busca": q,
            "categoria_selecionada": categoria,
            "ordem_selecionada": ordem,
        },
    )


@router.get("/ler/{id}")
@requer_autenticacao()
async def ler_artigo(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exibe um artigo completo (somente para usuários autenticados)."""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    artigo = artigo_repo.obter_por_id(id)

    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(
            url="/artigos",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica se o artigo está publicado ou se o usuário é o autor/admin
    if artigo.status != StatusArtigo.PUBLICADO.value:
        if artigo.usuario_id != usuario_logado.id and not usuario_logado.is_admin():
            informar_erro(request, "Este artigo não está disponível.")
            return RedirectResponse(
                url="/artigos",
                status_code=status.HTTP_303_SEE_OTHER,
            )

    # Incrementa visualizações apenas para artigos publicados
    if artigo.status == StatusArtigo.PUBLICADO.value:
        artigo_repo.incrementar_visualizacoes(id)
        artigo.qtde_visualizacoes = (artigo.qtde_visualizacoes or 0) + 1

    return templates.TemplateResponse(
        "artigos/ler.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "artigo": artigo,
        },
    )
```

### Salvando seu progresso

Após concluir as alterações desta seção, é importante salvar seu progresso no repositório:

1. Abra o painel **Source Control** do VS Code (Ctrl + Shift + G)
2. Revise as alterações realizadas
3. Digite a seguinte mensagem de commit:
   ```
   criação do CRUD de Artigos (model, sql, repo, dto, routes)
   ```
4. Clique no botão **Commit** (ícone ✓) para confirmar as alterações
5. Clique no botão **Sync Changes** para sincronizar com o GitHub

> **Dica:** Manter commits frequentes facilita o acompanhamento do progresso e permite reverter alterações caso necessário.

---

## 11. Templates de Artigos

Agora vamos criar os templates HTML para o módulo de artigos. Os autores usarão esses templates para gerenciar seus artigos, enquanto os leitores usarão para navegar e ler o conteúdo.

### 11.1 Template de Listagem (Meus Artigos)

Crie o arquivo `templates/artigos/listar.html`:

```html
{% extends "base_privada.html" %}

{% block titulo %}Meus Artigos{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-file-earmark-text"></i> Meus Artigos</h2>
            <a href="/artigos/cadastrar" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> Novo Artigo
            </a>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                {% if artigos %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">Título</th>
                                <th scope="col">Categoria</th>
                                <th scope="col">Status</th>
                                <th scope="col">Visualizações</th>
                                <th scope="col">Data</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for artigo in artigos %}
                            <tr>
                                <td>
                                    <strong>{{ artigo.titulo }}</strong>
                                    {% if artigo.resumo %}
                                    <br><small class="text-muted">{{ artigo.resumo[:80] }}{% if artigo.resumo|length > 80 %}...{% endif %}</small>
                                    {% endif %}
                                </td>
                                <td>
                                    <span class="badge bg-secondary">{{ artigo.categoria_nome or 'Sem categoria' }}</span>
                                </td>
                                <td>
                                    {% if artigo.status == 'Publicado' %}
                                        <span class="badge bg-success">Publicado</span>
                                    {% elif artigo.status == 'Rascunho' %}
                                        <span class="badge bg-warning text-dark">Rascunho</span>
                                    {% elif artigo.status == 'Finalizado' %}
                                        <span class="badge bg-info">Finalizado</span>
                                    {% elif artigo.status == 'Pausado' %}
                                        <span class="badge bg-secondary">Pausado</span>
                                    {% else %}
                                        <span class="badge bg-light text-dark">{{ artigo.status }}</span>
                                    {% endif %}
                                </td>
                                <td>
                                    <i class="bi bi-eye"></i> {{ artigo.qtde_visualizacoes or 0 }}
                                </td>
                                <td>
                                    {{ artigo.data_cadastro|data_br if artigo.data_cadastro else '-' }}
                                </td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        {% if artigo.status == 'Publicado' %}
                                        <a href="/artigos/ler/{{ artigo.id }}"
                                            class="btn btn-outline-success" title="Visualizar">
                                            <i class="bi bi-eye"></i>
                                        </a>
                                        {% endif %}
                                        <a href="/artigos/editar/{{ artigo.id }}"
                                            class="btn btn-outline-primary" title="Editar">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        {% if artigo.status == 'Publicado' %}
                                        <button type="button" class="btn btn-outline-warning" title="Pausar"
                                            onclick="pausarArtigo({{ artigo.id }}, '{{ artigo.titulo|replace("'", "\\'") }}')">
                                            <i class="bi bi-pause-circle"></i>
                                        </button>
                                        {% elif artigo.status in ['Finalizado', 'Pausado'] %}
                                        <button type="button" class="btn btn-outline-success" title="Publicar"
                                            onclick="publicarArtigo({{ artigo.id }}, '{{ artigo.titulo|replace("'", "\\'") }}')">
                                            <i class="bi bi-send"></i>
                                        </button>
                                        {% endif %}
                                        <button type="button" class="btn btn-outline-danger" title="Excluir"
                                            onclick="excluirArtigo({{ artigo.id }}, '{{ artigo.titulo|replace("'", "\\'") }}')">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                <div class="mt-3">
                    <small class="text-muted">
                        Total: {{ artigos|length }} artigo(s)
                    </small>
                </div>
                {% else %}
                <div class="alert alert-info text-center mb-0">
                    <i class="bi bi-info-circle"></i> Você ainda não possui artigos.
                    <a href="/artigos/cadastrar">Crie seu primeiro artigo!</a>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function excluirArtigo(artigoId, artigoTitulo) {
        abrirModalConfirmacao({
            url: `/artigos/excluir/${artigoId}`,
            mensagem: `Tem certeza que deseja excluir o artigo "${artigoTitulo}"?`,
            detalhes: '<p class="text-danger"><i class="bi bi-exclamation-triangle"></i> Esta ação não pode ser desfeita.</p>'
        });
    }

    function publicarArtigo(artigoId, artigoTitulo) {
        abrirModalConfirmacao({
            url: `/artigos/publicar/${artigoId}`,
            mensagem: `Deseja publicar o artigo "${artigoTitulo}"?`,
            detalhes: '<p class="text-info"><i class="bi bi-info-circle"></i> O artigo ficará visível para todos os usuários autenticados.</p>',
            tipo: 'warning',
            titulo: 'Confirmar Publicação',
            icone: 'bi-send',
            btnTexto: 'Publicar',
            btnIcone: 'bi-send'
        });
    }

    function pausarArtigo(artigoId, artigoTitulo) {
        abrirModalConfirmacao({
            url: `/artigos/pausar/${artigoId}`,
            mensagem: `Deseja pausar o artigo "${artigoTitulo}"?`,
            detalhes: '<p class="text-warning"><i class="bi bi-info-circle"></i> O artigo ficará temporariamente indisponível para leitores.</p>',
            tipo: 'warning',
            titulo: 'Confirmar Pausa',
            icone: 'bi-pause-circle',
            btnTexto: 'Pausar',
            btnIcone: 'bi-pause-circle'
        });
    }
</script>
{% endblock %}
```

### 11.2 Template de Cadastro

Crie o arquivo `templates/artigos/cadastrar.html`:

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Novo Artigo{% endblock %}

{% block head %}
<!-- EasyMDE - Editor Markdown -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css">
<style>
    .EasyMDEContainer .CodeMirror {
        border-radius: 0 0 4px 4px;
    }
    .editor-toolbar {
        border-radius: 4px 4px 0 0;
    }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-10">
        <div class="d-flex align-items-center mb-4">
            <a href="/artigos/meus" class="btn btn-outline-secondary me-3">
                <i class="bi bi-arrow-left"></i>
            </a>
            <h2 class="mb-0"><i class="bi bi-file-earmark-plus"></i> Novo Artigo</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/artigos/cadastrar" id="formArtigo">
                {{ csrf_input() }}
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-md-8 mb-3">
                            {{ field(
                                name='titulo',
                                label='Título do Artigo',
                                type='text',
                                required=true,
                                placeholder='Digite um título atrativo para seu artigo...',
                                help_text='O título deve ter entre 5 e 200 caracteres'
                            ) }}
                        </div>

                        <div class="col-md-4">
                            {% set categorias_dict = {'': 'Selecione uma categoria...'} %}
                            {% for cat in categorias %}
                                {% set _ = categorias_dict.update({cat.id|string: cat.nome}) %}
                            {% endfor %}
                            {{ field(
                                name='categoria_id',
                                label='Categoria',
                                type='select',
                                required=true,
                                options=categorias_dict
                            ) }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(
                                name='resumo',
                                label='Resumo',
                                type='textarea',
                                required=false,
                                placeholder='Um breve resumo do artigo que será exibido na listagem...',
                                help_text='Opcional. Máximo de 500 caracteres.',
                                rows=2
                            ) }}
                        </div>

                        <div class="col-12 mb-3">
                            <label for="conteudo" class="form-label">Conteúdo <span class="text-danger">*</span></label>
                            <textarea name="conteudo" id="conteudo">{{ dados.conteudo if dados is defined and dados.conteudo else '' }}</textarea>
                            <small class="form-text text-muted">
                                Use Markdown para formatar seu texto. Mínimo de 50 caracteres.
                            </small>
                        </div>

                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <input type="hidden" name="acao" id="acao" value="rascunho">
                        <button type="submit" class="btn btn-secondary" onclick="document.getElementById('acao').value='rascunho'">
                            <i class="bi bi-file-earmark"></i> Salvar Rascunho
                        </button>
                        <button type="submit" class="btn btn-success" onclick="document.getElementById('acao').value='finalizar'">
                            <i class="bi bi-check-circle"></i> Concluir Artigo
                        </button>
                        <a href="/artigos/meus" class="btn btn-outline-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<!-- EasyMDE - Editor Markdown -->
<script src="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const easyMDE = new EasyMDE({
            element: document.getElementById('conteudo'),
            spellChecker: false,
            autosave: {
                enabled: true,
                uniqueId: 'artigo-novo',
                delay: 1000,
            },
            placeholder: 'Escreva seu artigo aqui usando Markdown...\n\n# Título\n\nParágrafo de texto...\n\n## Subtítulo\n\n- Item de lista\n- Outro item',
            toolbar: [
                'bold', 'italic', 'heading', '|',
                'quote', 'unordered-list', 'ordered-list', '|',
                'link', 'image', '|',
                'preview', 'side-by-side', 'fullscreen', '|',
                'guide'
            ],
            status: ['autosave', 'lines', 'words'],
            minHeight: '300px',
        });

        // Sincronizar valor do editor para o textarea antes do submit
        document.getElementById('formArtigo').addEventListener('submit', function(e) {
            // Sincroniza o valor do editor para o textarea
            const conteudo = easyMDE.value();
            document.getElementById('conteudo').value = conteudo;

            // Valida se o conteúdo não está vazio
            if (!conteudo || conteudo.trim().length < 50) {
                e.preventDefault();
                window.App.Modal.showWarning(
                    'O conteúdo do artigo deve ter pelo menos 50 caracteres.',
                    'Conteúdo obrigatório'
                );
                return false;
            }

            // Limpa o autosave do localStorage após validação bem-sucedida
            localStorage.removeItem('smde_artigo-novo');
        });
    });
</script>
{% endblock %}
```

### 11.3 Template de Edição

Crie o arquivo `templates/artigos/editar.html`:

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Editar Artigo{% endblock %}

{% block head %}
<!-- EasyMDE - Editor Markdown -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css">
<style>
    .EasyMDEContainer .CodeMirror {
        border-radius: 0 0 4px 4px;
    }
    .editor-toolbar {
        border-radius: 4px 4px 0 0;
    }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-10">
        <div class="d-flex align-items-center mb-4">
            <a href="/artigos/meus" class="btn btn-outline-secondary me-3">
                <i class="bi bi-arrow-left"></i>
            </a>
            <h2 class="mb-0"><i class="bi bi-pencil-square"></i> Editar Artigo</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/artigos/editar/{{ artigo.id }}" id="formArtigo">
                {{ csrf_input() }}
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-md-8">
                            {{ field(
                                name='titulo',
                                label='Título do Artigo',
                                type='text',
                                required=true,
                                value=dados.titulo if dados is defined and dados.titulo else artigo.titulo,
                                placeholder='Digite um título atrativo para seu artigo...',
                                help_text='O título deve ter entre 5 e 200 caracteres'
                            ) }}
                        </div>

                        <div class="col-md-4">
                            {% set categorias_dict = {'': 'Selecione uma categoria...'} %}
                            {% for cat in categorias %}
                                {% set _ = categorias_dict.update({cat.id|string: cat.nome}) %}
                            {% endfor %}
                            {% set categoria_valor = dados.categoria_id if dados is defined and dados.categoria_id else artigo.categoria_id %}
                            {{ field(
                                name='categoria_id',
                                label='Categoria',
                                type='select',
                                required=true,
                                value=categoria_valor,
                                options=categorias_dict
                            ) }}
                        </div>

                        <div class="col-12">
                            {{ field(
                                name='resumo',
                                label='Resumo',
                                type='textarea',
                                required=false,
                                value=dados.resumo if dados is defined and dados.resumo else artigo.resumo,
                                placeholder='Um breve resumo do artigo que será exibido na listagem...',
                                help_text='Opcional. Máximo de 500 caracteres.',
                                rows=2
                            ) }}
                        </div>

                        <div class="col-12 mb-3">
                            <label for="conteudo" class="form-label">Conteúdo <span class="text-danger">*</span></label>
                            <textarea name="conteudo" id="conteudo">{{ dados.conteudo if dados is defined and dados.conteudo else artigo.conteudo }}</textarea>
                            <small class="form-text text-muted">
                                Use Markdown para formatar seu texto. Mínimo de 50 caracteres.
                            </small>
                        </div>

                        <div class="col-md-6 mb-3">
                            <label class="form-label">Informações</label>
                            <div class="small text-muted">
                                <p class="mb-1"><i class="bi bi-eye"></i> Visualizações: {{ artigo.qtde_visualizacoes or 0 }}</p>
                                <p class="mb-1"><i class="bi bi-calendar"></i> Criado em: {{ artigo.data_cadastro|data_br if artigo.data_cadastro else '-' }}</p>
                                {% if artigo.data_publicacao %}
                                <p class="mb-0"><i class="bi bi-send"></i> Publicado em: {{ artigo.data_publicacao|data_br }}</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <input type="hidden" name="acao" id="acao" value="rascunho">
                        <button type="submit" class="btn btn-secondary" onclick="document.getElementById('acao').value='rascunho'">
                            <i class="bi bi-file-earmark"></i> Salvar Rascunho
                        </button>
                        <button type="submit" class="btn btn-success" onclick="document.getElementById('acao').value='finalizar'">
                            <i class="bi bi-check-circle"></i> Concluir Artigo
                        </button>
                        <a href="/artigos/meus" class="btn btn-outline-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<!-- EasyMDE - Editor Markdown -->
<script src="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const easyMDE = new EasyMDE({
            element: document.getElementById('conteudo'),
            spellChecker: false,
            autosave: {
                enabled: true,
                uniqueId: 'artigo-{{ artigo.id }}',
                delay: 1000,
            },
            toolbar: [
                'bold', 'italic', 'heading', '|',
                'quote', 'unordered-list', 'ordered-list', '|',
                'link', 'image', '|',
                'preview', 'side-by-side', 'fullscreen', '|',
                'guide'
            ],
            status: ['autosave', 'lines', 'words'],
            minHeight: '300px',
        });

        // Sincronizar valor do editor para o textarea antes do submit
        document.getElementById('formArtigo').addEventListener('submit', function(e) {
            // Sincroniza o valor do editor para o textarea
            const conteudo = easyMDE.value();
            document.getElementById('conteudo').value = conteudo;

            // Valida se o conteúdo não está vazio
            if (!conteudo || conteudo.trim().length < 50) {
                e.preventDefault();
                window.App.Modal.showWarning(
                    'O conteúdo do artigo deve ter pelo menos 50 caracteres.',
                    'Conteúdo obrigatório'
                );
                return false;
            }
        });
    });
</script>
{% endblock %}
```

### 11.4 Template de Busca (Listagem Pública)

Crie o arquivo `templates/artigos/buscar.html`:

```html
{% extends "base_publica.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Artigos{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-newspaper"></i> Artigos</h2>
        </div>

        <!-- Barra de Busca e Filtros -->
        <div class="card shadow-sm mb-4">
            <div class="card-body">
                <form method="GET" action="/artigos" class="row g-3 align-items-end">
                    <div class="col-md-5">
                        {{ field(
                            name='q',
                            label='Buscar',
                            type='search',
                            value=termo_busca,
                            placeholder='Buscar por título...',
                            append_icon='bi-search',
                            wrapper_class='mb-0'
                        ) }}
                    </div>
                    <div class="col-md-3">
                        {% set categorias_dict = {'0': 'Todas as categorias'} %}
                        {% for cat in categorias %}
                            {% set _ = categorias_dict.update({cat.id|string: cat.nome}) %}
                        {% endfor %}
                        {{ field(
                            name='categoria',
                            label='Categoria',
                            type='select',
                            value=categoria_selecionada,
                            options=categorias_dict,
                            wrapper_class='mb-0'
                        ) }}
                    </div>
                    <div class="col-md-2">
                        {{ field(
                            name='ordem',
                            label='Ordenar por',
                            type='select',
                            value=ordem_selecionada,
                            options={
                                'recentes': 'Mais recentes',
                                'antigos': 'Mais antigos',
                                'visualizacoes': 'Mais lidos'
                            },
                            wrapper_class='mb-0'
                        ) }}
                    </div>
                    <div class="col-md-2">
                        <button type="submit" class="btn btn-primary w-100" style="height: calc(3.5rem + 2px);">
                            <i class="bi bi-filter"></i> Filtrar
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Lista de Artigos -->
        {% if artigos %}
        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
            {% for artigo in artigos %}
            <div class="col">
                <div class="card h-100 shadow-sm shadow-hover">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge bg-secondary">{{ artigo.categoria_nome or 'Sem categoria' }}</span>
                            <small class="text-muted">
                                <i class="bi bi-eye"></i> {{ artigo.qtde_visualizacoes or 0 }}
                            </small>
                        </div>
                        <h5 class="card-title">{{ artigo.titulo }}</h5>
                        <p class="card-text text-muted">
                            {% if artigo.resumo %}
                                {{ artigo.resumo[:150] }}{% if artigo.resumo|length > 150 %}...{% endif %}
                            {% else %}
                                {{ artigo.conteudo[:150]|striptags }}{% if artigo.conteudo|length > 150 %}...{% endif %}
                            {% endif %}
                        </p>
                    </div>
                    <div class="card-footer bg-transparent">
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="bi bi-person"></i> {{ artigo.usuario_nome or 'Anônimo' }}
                                <br>
                                <i class="bi bi-calendar"></i> {{ artigo.data_publicacao|data_br if artigo.data_publicacao else artigo.data_cadastro|data_br }}
                            </small>
                            {% if usuario_logado %}
                            <a href="/artigos/ler/{{ artigo.id }}" class="btn btn-sm btn-outline-primary">
                                Ler mais <i class="bi bi-arrow-right"></i>
                            </a>
                            {% else %}
                            <a href="/login?next=/artigos/ler/{{ artigo.id }}" class="btn btn-sm btn-outline-secondary">
                                <i class="bi bi-lock"></i> Fazer login
                            </a>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="mt-4 text-center text-muted">
            <small>{{ artigos|length }} artigo(s) encontrado(s)</small>
        </div>
        {% else %}
        <div class="card shadow-sm">
            <div class="card-body text-center py-5">
                <i class="bi bi-search display-1 text-muted mb-3"></i>
                <h4 class="text-muted">Nenhum artigo encontrado</h4>
                {% if termo_busca or categoria_selecionada > 0 %}
                <p class="text-muted">Tente ajustar seus filtros de busca.</p>
                <a href="/artigos" class="btn btn-outline-primary">
                    <i class="bi bi-x-circle"></i> Limpar filtros
                </a>
                {% else %}
                <p class="text-muted">Ainda não há artigos publicados.</p>
                {% endif %}
            </div>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

### 11.5 Template de Leitura

Crie o arquivo `templates/artigos/ler.html`:

```html
{% extends "base_privada.html" %}

{% block titulo %}{{ artigo.titulo }}{% endblock %}

{% block head %}
<!-- Highlight.js para syntax highlighting em código -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github.min.css">
<style>
    .artigo-conteudo {
        line-height: 1.8;
        font-size: 1.1rem;
    }
    .artigo-conteudo h1, .artigo-conteudo h2, .artigo-conteudo h3 {
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .artigo-conteudo p {
        margin-bottom: 1rem;
    }
    .artigo-conteudo img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .artigo-conteudo pre {
        background-color: #f6f8fa;
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
    }
    .artigo-conteudo blockquote {
        border-left: 4px solid #0d6efd;
        padding-left: 1rem;
        margin: 1rem 0;
        color: #6c757d;
    }
    .artigo-conteudo code {
        background-color: #f6f8fa;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
    }
    .artigo-conteudo pre code {
        background-color: transparent;
        padding: 0;
    }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-10">
        <!-- Navegação -->
        <div class="mb-4">
            <a href="/artigos" class="btn btn-outline-secondary">
                <i class="bi bi-arrow-left"></i> Voltar para artigos
            </a>
        </div>

        <!-- Cabeçalho do Artigo -->
        <div class="card shadow-sm mb-4">
            <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <span class="badge bg-primary">{{ artigo.categoria_nome or 'Sem categoria' }}</span>
                    <div class="text-muted">
                        <span class="me-3"><i class="bi bi-eye"></i> {{ artigo.qtde_visualizacoes or 0 }} visualizações</span>
                    </div>
                </div>

                <h1 class="card-title mb-3">{{ artigo.titulo }}</h1>

                {% if artigo.resumo %}
                <p class="lead text-muted">{{ artigo.resumo }}</p>
                {% endif %}

                <hr>

                <div class="d-flex justify-content-between align-items-center text-muted">
                    <div>
                        <i class="bi bi-person-circle"></i>
                        <strong>{{ artigo.usuario_nome or 'Anônimo' }}</strong>
                    </div>
                    <div>
                        <i class="bi bi-calendar3"></i>
                        {% if artigo.data_publicacao %}
                            Publicado em {{ artigo.data_publicacao|data_br }}
                        {% else %}
                            Criado em {{ artigo.data_cadastro|data_br if artigo.data_cadastro else '-' }}
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <!-- Conteúdo do Artigo -->
        <div class="card shadow-sm">
            <div class="card-body p-4 p-md-5">
                <div class="artigo-conteudo" id="conteudo-artigo">
                    {{ artigo.conteudo }}
                </div>
            </div>
        </div>

        <!-- Rodapé do Artigo -->
        <div class="card shadow-sm mt-4">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <small class="text-muted">
                            {% if artigo.data_atualizacao %}
                            <i class="bi bi-clock-history"></i> Atualizado em {{ artigo.data_atualizacao|data_br }}
                            {% endif %}
                        </small>
                    </div>
                    <div>
                        <a href="/artigos" class="btn btn-outline-primary">
                            <i class="bi bi-newspaper"></i> Ver mais artigos
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<!-- Marked.js para renderização de Markdown -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<!-- Highlight.js para syntax highlighting -->
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/core.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/javascript.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/python.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/html.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/css.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/sql.min.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const conteudoEl = document.getElementById('conteudo-artigo');
        const conteudoOriginal = conteudoEl.textContent.trim();

        // Configura o marked
        marked.setOptions({
            breaks: true,
            gfm: true,
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    return hljs.highlight(code, { language: lang }).value;
                }
                return code;
            }
        });

        // Renderiza o Markdown
        conteudoEl.innerHTML = marked.parse(conteudoOriginal);

        // Aplica highlight em blocos de código sem linguagem especificada
        document.querySelectorAll('pre code:not([class*="hljs"])').forEach((block) => {
            hljs.highlightElement(block);
        });
    });
</script>
{% endblock %}
```

> **Nota sobre Markdown:** Os templates de cadastro e edição usam o **EasyMDE** como editor visual de Markdown. O template de leitura usa o **Marked.js** para renderizar o Markdown em HTML e o **Highlight.js** para destacar blocos de código.

### Salvando seu progresso

Após concluir as alterações desta seção, é importante salvar seu progresso no repositório:

1. Abra o painel **Source Control** do VS Code (Ctrl + Shift + G)
2. Revise as alterações realizadas
3. Digite a seguinte mensagem de commit:
   ```
   criação dos templates de Artigos
   ```
4. Clique no botão **Commit** (ícone ✓) para confirmar as alterações
5. Clique no botão **Sync Changes** para sincronizar com o GitHub

> **Dica:** Manter commits frequentes facilita o acompanhamento do progresso e permite reverter alterações caso necessário.

---

## 12. Registrando o CRUD de Artigos

Antes de testar o CRUD de Artigos, precisamos registrá-lo no `main.py` para que a aplicação reconheça as novas rotas e crie a tabela no banco de dados.

### 12.1. Adicionar import do repositório

No início do arquivo `main.py`, localize a linha de importação dos repositórios (aproximadamente linha 27) e adicione `artigo_repo`. A linha ficará assim:

```python
from repo import chat_sala_repo, chat_participante_repo, chat_mensagem_repo, categoria_repo, artigo_repo
```

### 12.2. Adicionar import das rotas

Ainda no `main.py`, na seção de importação de rotas, logo depois da linha 40, adicione a linha a seguir:

```python
from routes.artigos_routes import router as artigos_router
```

### 12.3. Adicionar tabela na lista TABELAS

No arquivo `main.py`, localize a lista `TABELAS` e adicione a nova tabela `artigo` ao final da listagem, logo após a linha 81:

```python
TABELAS = [
    (usuario_repo, "usuario"),
    (configuracao_repo, "configuracao"),
    (chamado_repo, "chamado"),
    (chamado_interacao_repo, "chamado_interacao"),
    (chat_sala_repo, "chat_sala"),
    (chat_participante_repo, "chat_participante"),
    (chat_mensagem_repo, "chat_mensagem"),
    (categoria_repo, "categoria"),
    (artigo_repo, "artigo"),  # NOVA TABELA
]
```

### 12.4. Adicionar router na lista ROUTERS

Localize a lista `ROUTERS` e adicione o novo router após a linha do `admin_categorias_router`, logo após a linha 121:

```python
    (artigos_router, ["Artigos"], "artigos"),  # NOVO ROUTER
```

O bloco `ROUTERS` ficará assim:

```python
ROUTERS = [
    (auth_router, ["Autenticação"], "autenticação"),
    (chamados_router, ["Chamados"], "chamados"),
    (admin_usuarios_router, ["Admin - Usuários"], "admin de usuários"),
    (admin_config_router, ["Admin - Configurações"], "admin de configurações"),
    (admin_backups_router, ["Admin - Backups"], "admin de backups"),
    (admin_chamados_router, ["Admin - Chamados"], "admin de chamados"),
    (admin_categorias_router, ["Admin - Categorias"], "admin de categorias"),
    (artigos_router, ["Artigos"], "artigos"),  # NOVO ROUTER
    (usuario_router, ["Usuário"], "usuário"),
    (chat_router, ["Chat"], "chat"),
    (public_router, ["Público"], "público"),  # Deve ficar por último
    (examples_router, ["Exemplos"], "exemplos"),  # Deve ficar por último
]
```

> **IMPORTANTE**: Os routers `public_router` e `examples_router` devem ser incluídos **por último** para evitar conflitos de rotas com "/".

### Salvando seu progresso

Após concluir as alterações desta seção, é importante salvar seu progresso no repositório:

1. Abra o painel **Source Control** do VS Code (Ctrl + Shift + G)
2. Revise as alterações realizadas
3. Digite a seguinte mensagem de commit:
   ```
   registro do CRUD de Artigos no main.py
   ```
4. Clique no botão **Commit** (ícone ✓) para confirmar as alterações
5. Clique no botão **Sync Changes** para sincronizar com o GitHub

> **Dica:** Manter commits frequentes facilita o acompanhamento do progresso e permite reverter alterações caso necessário.

---

## 13. Adicionando Menu e Card de Artigos no Dashboard

Agora vamos adicionar o acesso ao CRUD de Artigos no painel do autor.

### 13.1. Adicionando o link no menu de navegação

No arquivo `templates/base_privada.html`, localize a seção de navegação. Após o bloco do administrador (que termina com `{% endif %}`), após a linha 124, adicione uma verificação para autores e administradores terem acesso a "Meus Artigos":

```html
                    {% if usuario_logado and usuario_logado.perfil == 'Autor' %}
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if '/artigos/meus' in request.path else '' }}"
                            href="/artigos/meus"
                            {{ 'aria-current=page' if '/artigos/meus' in request.path else '' }}>Meus Artigos</a>
                    </li>
                    {% endif %}
```

### 13.2. Adicionando o card no dashboard do autor

No arquivo `templates/dashboard.html`, adicione uma seção para autores logo após a seção do administrador. Localize o fechamento do bloco `{% endif %}` do administrador, logo após a linha 173, e adicione:

```html
    {# Cards do Autor #}
    {% if usuario_logado and usuario_logado.perfil == 'Autor' %}
    <!-- Card Meus Artigos -->
    <div class="col">
        <div class="card h-100 shadow-sm shadow-hover">
            <div class="card-body text-center">
                <div class="mb-3">
                    <i class="bi bi-pencil-square text-success" style="font-size: 3rem;"></i>
                </div>
                <h5 class="card-title">Meus Artigos</h5>
                <p class="card-text text-muted">
                    Crie e gerencie seus artigos do blog
                </p>
                <a href="/artigos/meus" class="btn btn-success">
                    <i class="bi bi-pencil-square"></i> Acessar
                </a>
            </div>
        </div>
    </div>
    {% endif %}
```

> **Resultado esperado:** O autor verá o link "Meus Artigos" no menu superior e um card de acesso rápido na página inicial (dashboard).

### Salvando seu progresso

Após concluir as alterações desta seção, é importante salvar seu progresso no repositório:

1. Abra o painel **Source Control** do VS Code (Ctrl + Shift + G)
2. Revise as alterações realizadas
3. Digite a seguinte mensagem de commit:
   ```
   adição do menu e card de Artigos no dashboard
   ```
4. Clique no botão **Commit** (ícone ✓) para confirmar as alterações
5. Clique no botão **Sync Changes** para sincronizar com o GitHub

> **Dica:** Manter commits frequentes facilita o acompanhamento do progresso e permite reverter alterações caso necessário.

---

## 14. Testando o CRUD de Artigos

Agora vamos testar se o CRUD de Artigos está funcionando corretamente.

### 14.1. Iniciando a aplicação

No VS Code, pressione **Ctrl+F5** para executar a aplicação sem depuração (ou execute `python main.py` no terminal).

Você deverá ver algo como:

```
============================================================
                    BLOG DO FULANO
============================================================
Modo de execução: Development
============================================================

INFO:     Tabela 'categoria' verificada/criada com sucesso.
INFO:     Tabela 'artigo' verificada/criada com sucesso.
...
INFO:     Uvicorn running on http://0.0.0.0:8400 (Press CTRL+C to quit)
```

### 14.2. Acessando como Autor

1. Acesse http://localhost:8400 no navegador
2. Clique em **Entrar** ou acesse http://localhost:8400/login
3. Faça login com as credenciais do autor padrão:
   - **E-mail:** `padrao@autor.com`
   - **Senha:** `1234aA@#`

### 14.3. Testando as funcionalidades

Após o login, teste as seguintes funcionalidades:

1. **Verificar o menu:** O link "Meus Artigos" deve aparecer no menu superior
2. **Verificar o dashboard:** O card "Meus Artigos" deve aparecer na página inicial
3. **Listar artigos:** Clique em "Meus Artigos" - a lista deve estar vazia inicialmente
4. **Cadastrar artigo:** Clique em "Novo Artigo" e cadastre um artigo de teste com os seguintes dados:

   **Título:**
   ```
   Introdução ao Python: Primeiros Passos na Programação
   ```

   **Categoria:** Selecione "Tecnologia" (ou outra categoria que você criou anteriormente)

   **Resumo:**
   ```
   Descubra por que Python é a linguagem ideal para iniciantes e aprenda os conceitos básicos para começar a programar hoje mesmo.
   ```

   **Conteúdo (Markdown):**
   ````markdown
   Python é uma das linguagens de programação mais populares do mundo, conhecida por sua sintaxe simples e legibilidade.

   ## Por que aprender Python?

   - **Fácil de aprender:** A sintaxe é clara e intuitiva
   - **Versátil:** Usado em web, dados, IA e automação
   - **Grande comunidade:** Milhares de bibliotecas disponíveis

   ## Seu primeiro código

   Veja como é simples exibir uma mensagem:

   ```python
   print("Olá, mundo!")
   ```

   ## Próximos passos

   Após dominar o básico, você pode explorar:

   1. Estruturas de dados (listas, dicionários)
   2. Funções e módulos
   3. Orientação a objetos

   Comece hoje mesmo e descubra o poder do Python!
   ````

5. **Salvar o artigo:** Clique em "Cadastrar" para salvar o artigo
6. **Editar artigo:** Na lista, clique no botão de edição do artigo criado, altere o título para "Python para Iniciantes: Guia Completo" e salve
7. **Visualizar artigo:** Clique no botão de visualização para ver como o artigo ficará para os leitores
8. **Excluir artigo de teste:** Crie um novo artigo chamado "Artigo de Teste para Exclusão" e depois exclua-o para testar a funcionalidade de exclusão

> **Dica:** Se encontrar erros, verifique o terminal onde a aplicação está rodando para ver as mensagens de log.

---

## 15. Templates Base e Home Page

Agora vamos modificar os templates base do boilerplate para incluir a navegação do blog e criar a página inicial.

> **IMPORTANTE**: NÃO substitua os templates base inteiros! Adicione apenas os novos itens de menu conforme instruído abaixo.

### 15.1 Atualizando o Template Base Pública

O template `templates/base_publica.html` é usado para páginas públicas. Você precisa adicionar o link para **Artigos** na navegação.

#### Passo único: Adicionar link de Artigos

No arquivo `templates/base_publica.html`, localize a seção de navegação (`<ul class="navbar-nav me-auto">`).

Após o link de **Início** e ANTES do link de **Sobre**, adicione o link para **Artigos**:

```html
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if '/artigos' in request.path and '/meus' not in request.path else '' }}"
                            href="/artigos"><i class="bi bi-newspaper"></i> Artigos</a>
                    </li>
```

> **Resultado esperado:** O menu público terá os links: Início → **Artigos** → Sobre

### 15.2 Criando a Home Page do Blog

Crie ou substitua o arquivo `templates/index.html` com o template da home page do blog:

```html
{% extends "base_publica.html" %}

{% block titulo %}Blog - {{ APP_NAME }}{% endblock %}

{% block content %}
<!-- Hero Section - Blog -->
<div class="mb-5">
    <div class="bg-primary text-white rounded-4 shadow-lg p-5">
        <div class="row align-items-center">
            <div class="col-lg-8">
                <h1 class="display-4 fw-bold mb-3">
                    <i class="bi bi-newspaper"></i> {{ APP_NAME }}
                </h1>
                <p class="lead mb-4">
                    Bem-vindo ao nosso blog! Aqui você encontra artigos sobre diversos temas,
                    escritos por nossos autores. Faça login para ler os artigos completos.
                </p>
                <div class="d-flex gap-3 flex-wrap">
                    <a href="/artigos" class="btn btn-light btn-lg">
                        <i class="bi bi-search"></i> Buscar Artigos
                    </a>
                    {% if not usuario_logado %}
                    <a href="/login" class="btn btn-outline-light btn-lg">
                        <i class="bi bi-box-arrow-in-right"></i> Entrar
                    </a>
                    <a href="/cadastrar" class="btn btn-outline-light btn-lg">
                        <i class="bi bi-person-plus"></i> Criar Conta
                    </a>
                    {% else %}
                    <a href="/usuario" class="btn btn-outline-light btn-lg">
                        <i class="bi bi-person-circle"></i> Minha Conta
                    </a>
                    {% endif %}
                </div>
            </div>
            <div class="col-lg-4 text-center mt-4 mt-lg-0 d-none d-lg-block">
                <i class="bi bi-journal-richtext" style="font-size: 8rem; opacity: 0.3;"></i>
            </div>
        </div>
    </div>
</div>

<!-- Seção de Artigos Recentes -->
<div class="mb-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold mb-0">
            <i class="bi bi-clock-history text-primary"></i> Artigos Recentes
        </h2>
        <a href="/artigos" class="btn btn-outline-primary">
            Ver todos <i class="bi bi-arrow-right"></i>
        </a>
    </div>

    {% if ultimos_artigos %}
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
        {% for artigo in ultimos_artigos %}
        <div class="col">
            <div class="card h-100 shadow-sm shadow-hover">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span class="badge bg-primary">{{ artigo.categoria_nome or 'Geral' }}</span>
                        <small class="text-muted">
                            <i class="bi bi-eye"></i> {{ artigo.qtde_visualizacoes or 0 }}
                        </small>
                    </div>
                    <h5 class="card-title">{{ artigo.titulo }}</h5>
                    <p class="card-text text-muted">
                        {% if artigo.resumo %}
                            {{ artigo.resumo[:120] }}{% if artigo.resumo|length > 120 %}...{% endif %}
                        {% else %}
                            {{ artigo.conteudo[:120]|striptags }}{% if artigo.conteudo|length > 120 %}...{% endif %}
                        {% endif %}
                    </p>
                </div>
                <div class="card-footer bg-transparent border-top-0">
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="bi bi-person"></i> {{ artigo.usuario_nome or 'Anônimo' }}
                            <br>
                            <i class="bi bi-calendar3"></i> {{ artigo.data_publicacao|data_br if artigo.data_publicacao else artigo.data_cadastro|data_br }}
                        </small>
                        {% if usuario_logado %}
                        <a href="/artigos/ler/{{ artigo.id }}" class="btn btn-sm btn-primary">
                            Ler <i class="bi bi-arrow-right"></i>
                        </a>
                        {% else %}
                        <a href="/login?next=/artigos/ler/{{ artigo.id }}" class="btn btn-sm btn-outline-secondary" title="Faça login para ler">
                            <i class="bi bi-lock"></i> Login
                        </a>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="card shadow-sm">
        <div class="card-body text-center py-5">
            <i class="bi bi-journal-x display-1 text-muted mb-3"></i>
            <h4 class="text-muted">Nenhum artigo publicado ainda</h4>
            <p class="text-muted">Em breve teremos novos conteúdos para você!</p>
        </div>
    </div>
    {% endif %}
</div>

<!-- Categorias -->
{% if categorias %}
<div class="mb-5">
    <h2 class="fw-bold mb-4">
        <i class="bi bi-folder text-primary"></i> Categorias
    </h2>
    <div class="d-flex flex-wrap gap-2">
        {% for cat in categorias %}
        <a href="/artigos?categoria={{ cat.id }}" class="btn btn-outline-secondary">
            <i class="bi bi-tag"></i> {{ cat.nome }}
        </a>
        {% endfor %}
    </div>
</div>
{% endif %}

<!-- CTA para não logados -->
{% if not usuario_logado %}
<div class="mb-5">
    <div class="card bg-primary text-white shadow-lg">
        <div class="card-body text-center p-5">
            <h2 class="fw-bold mb-3">Quer ler os artigos completos?</h2>
            <p class="lead mb-4">
                Crie sua conta gratuitamente e tenha acesso a todo o conteúdo do blog!
            </p>
            <div class="d-flex justify-content-center gap-3 flex-wrap">
                <a href="/cadastrar" class="btn btn-light btn-lg">
                    <i class="bi bi-person-plus"></i> Criar Conta Grátis
                </a>
                <a href="/login" class="btn btn-outline-light btn-lg">
                    <i class="bi bi-box-arrow-in-right"></i> Já tenho conta
                </a>
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- Informações do Blog -->
<div class="row g-4 mb-5">
    <div class="col-md-4">
        <div class="card h-100 shadow-sm text-center">
            <div class="card-body p-4">
                <i class="bi bi-file-earmark-text text-primary display-4 mb-3"></i>
                <h5 class="card-title">Artigos de Qualidade</h5>
                <p class="card-text text-muted">
                    Conteúdo escrito por autores especializados em diversos temas.
                </p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card h-100 shadow-sm text-center">
            <div class="card-body p-4">
                <i class="bi bi-search text-info display-4 mb-3"></i>
                <h5 class="card-title">Fácil de Encontrar</h5>
                <p class="card-text text-muted">
                    Busque por título, filtre por categoria e ordene como preferir.
                </p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card h-100 shadow-sm text-center">
            <div class="card-body p-4">
                <i class="bi bi-phone text-success display-4 mb-3"></i>
                <h5 class="card-title">Leia em Qualquer Lugar</h5>
                <p class="card-text text-muted">
                    Design responsivo que funciona perfeitamente em qualquer dispositivo.
                </p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Salvando seu progresso

Após concluir as alterações desta seção, é importante salvar seu progresso no repositório:

1. Abra o painel **Source Control** do VS Code (Ctrl + Shift + G)
2. Revise as alterações realizadas
3. Digite a seguinte mensagem de commit:
   ```
   criação dos templates base e home page do blog
   ```
4. Clique no botão **Commit** (ícone ✓) para confirmar as alterações
5. Clique no botão **Sync Changes** para sincronizar com o GitHub

> **Dica:** Manter commits frequentes facilita o acompanhamento do progresso e permite reverter alterações caso necessário.

---

## 16. Rotas Públicas e Configuração do main.py

Agora vamos atualizar as rotas públicas para exibir os artigos na home page e configurar o `main.py` para integrar todos os módulos.

### 16.1 Atualizando as Rotas Públicas

O arquivo `routes/public_routes.py` precisa ser atualizado para carregar os artigos e categorias na página inicial. Abaixo está o arquivo completo com as modificações necessárias:

> **Modificações importantes em relação ao arquivo original:**
> - Adicionado import de `obter_usuario_logado` do `util.auth_decorator`
> - Adicionado import de `artigo_repo` e `categoria_repo`
> - Rotas `/` e `/index` agora buscam artigos e categorias

```python
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.template_util import criar_templates
from util.auth_decorator import obter_usuario_logado  # NOVO
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.flash_messages import informar_erro
from util.logger_config import logger
from repo import artigo_repo, categoria_repo  # NOVO

router = APIRouter()
templates_public = criar_templates()

# Rate limiter para páginas públicas (proteção contra DDoS)
public_limiter = DynamicRateLimiter(
    chave_max="rate_limit_public_max",
    chave_minutos="rate_limit_public_minutos",
    padrao_max=100,
    padrao_minutos=1,
    nome="public_pages",
)


@router.get("/")
async def home(request: Request):
    """
    Rota inicial - Landing Page pública com os últimos artigos
    """
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, "Muitas requisições. Aguarde alguns minutos.")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Obtém os 6 últimos artigos publicados
    ultimos_artigos = artigo_repo.obter_ultimos_publicados(6)
    categorias = categoria_repo.obter_todos()
    usuario_logado = obter_usuario_logado(request)

    return templates_public.TemplateResponse(
        "index.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "ultimos_artigos": ultimos_artigos,
            "categorias": categorias,
        }
    )


@router.get("/index")
async def index(request: Request):
    """
    Página pública inicial (Landing Page)
    Sempre exibe a página pública, independentemente de autenticação
    """
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, "Muitas requisições. Aguarde alguns minutos.")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Obtém os 6 últimos artigos publicados
    ultimos_artigos = artigo_repo.obter_ultimos_publicados(6)
    categorias = categoria_repo.obter_todos()
    usuario_logado = obter_usuario_logado(request)

    return templates_public.TemplateResponse(
        "index.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "ultimos_artigos": ultimos_artigos,
            "categorias": categorias,
        }
    )


@router.get("/sobre")
async def sobre(request: Request):
    """
    Página "Sobre" com informações do projeto acadêmico
    """
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, "Muitas requisições. Aguarde alguns minutos.")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

    return templates_public.TemplateResponse(
        "sobre.html",
        {"request": request}
    )
```

> **Modificações importantes:**
> - Importados os repositórios `artigo_repo` e `categoria_repo`
> - As rotas `/` e `/index` agora buscam os últimos 6 artigos publicados
> - Categorias são carregadas para exibir os filtros na home

### 16.2 Atualizando o Menu Público

O template `templates/base_publica.html` contém o menu de navegação público. Vamos substituir o link "Exemplos" pelo link "Artigos", que levará à página de busca de artigos.

No arquivo `templates/base_publica.html`, localize o item de menu "Exemplos" (por volta da linha 49):

```html
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if '/exemplos' in request.path else '' }}"
                            href="/exemplos">Exemplos</a>
                    </li>
```

Substitua por:

```html
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if '/artigos' in request.path else '' }}"
                            href="/artigos">Artigos</a>
                    </li>
```

> **Resultado esperado:** O menu público agora exibe: **Início** → **Sobre** → **Artigos**. O link "Artigos" direciona para a página de busca/listagem pública de artigos (`/artigos`).

### Salvando seu progresso

Após concluir as alterações desta seção, é importante salvar seu progresso no repositório:

1. Abra o painel **Source Control** do VS Code (Ctrl + Shift + G)
2. Revise as alterações realizadas
3. Digite a seguinte mensagem de commit:
   ```
   configuração das rotas públicas e finalização do main.py
   ```
4. Clique no botão **Commit** (ícone ✓) para confirmar as alterações
5. Clique no botão **Sync Changes** para sincronizar com o GitHub

> **Dica:** Manter commits frequentes facilita o acompanhamento do progresso e permite reverter alterações caso necessário.

---

## 17. Testando a Aplicação Completa

Agora que todos os arquivos foram criados, vamos testar a aplicação completa.

### 17.1 Iniciando a Aplicação

Execute a aplicação:

```bash
python main.py
```

Você deverá ver algo como:

```
============================================================
Iniciando BlogSimples v1.0.0
============================================================
Servidor rodando em http://0.0.0.0:8400
Hot reload: Ativado
Documentação API: http://0.0.0.0:8400/docs
============================================================
```

### 17.2 Testando o Fluxo Completo

#### Passo 1: Criar um Administrador

1. Acesse `http://127.0.0.1:8400/cadastrar`
2. Crie uma conta com os dados:
   - Nome: Admin
   - E-mail: admin@blog.com
   - Senha: (escolha uma senha segura)
3. Após cadastrar, o sistema criará um usuário com perfil **Leitor** por padrão

> **Nota:** Para ter acesso administrativo, você precisará alterar o perfil do usuário no banco de dados para "Administrador".

#### Passo 2: Criar Categorias (como Admin)

1. Faça login como Administrador
2. Acesse **Categorias** no menu
3. Clique em **Nova Categoria**
4. Crie algumas categorias:
   - Tecnologia
   - Programação
   - Tutoriais
   - Notícias

#### Passo 3: Criar um Autor

1. Acesse `http://127.0.0.1:8400/cadastrar`
2. Crie uma conta com os dados:
   - Nome: Autor Teste
   - E-mail: autor@blog.com
   - Senha: (escolha uma senha segura)
3. Como Administrador, acesse a lista de usuários e altere o perfil para "Autor"

#### Passo 4: Criar Artigos (como Autor)

1. Faça login como Autor
2. Acesse **Meus Artigos** no menu
3. Clique em **Novo Artigo**
4. Preencha o formulário:
   - Título: Meu Primeiro Artigo
   - Categoria: (selecione uma)
   - Resumo: Um breve resumo do artigo
   - Conteúdo: Use Markdown para escrever o conteúdo

````markdown
# Introdução

Este é meu primeiro artigo no blog!

## Seção 1

Aqui vai o conteúdo da primeira seção.

### Código de Exemplo

```python
def hello():
    print("Hello, World!")
```
````

## Conclusão

Espero que tenham gostado!
```

5. Selecione o status **Publicado** ou clique em **Publicar**

#### Passo 5: Visualizar como Leitor

1. Faça logout
2. Acesse a home page em `http://127.0.0.1:8400`
3. Você verá os artigos publicados na seção "Artigos Recentes"
4. Clique em um artigo - será solicitado login para ler
5. Cadastre-se como leitor e faça login para ler o artigo completo

### 17.3 Funcionalidades Implementadas

#### Para Administradores:
- Gerenciar categorias (CRUD completo)
- Acessar todas as funcionalidades do sistema

#### Para Autores:
- Criar, editar e excluir seus próprios artigos
- Publicar artigos
- Ver estatísticas de visualizações

#### Para Leitores:
- Navegar pelos artigos publicados
- Buscar artigos por título
- Filtrar por categoria
- Ordenar por data ou visualizações
- Ler artigos completos (requer login)

#### Para Visitantes (não logados):
- Ver a home page com artigos recentes
- Ver resumos dos artigos
- Acessar a página de busca
- Criar conta ou fazer login

---

## 18. Resumo dos Arquivos Criados

### Models (Camada de Dados)
- `model/categoria_model.py` - Dataclass Categoria
- `model/artigo_model.py` - Dataclass Artigo

### SQL (Queries)
- `sql/categoria_sql.py` - Queries SQL para categorias
- `sql/artigo_sql.py` - Queries SQL para artigos

### Repositories (Acesso a Dados)
- `repo/categoria_repo.py` - Funções de repositório para categorias
- `repo/artigo_repo.py` - Funções de repositório para artigos

### DTOs (Validação de Dados)
- `dtos/categoria_dto.py` - DTOs Pydantic para categorias
- `dtos/artigo_dto.py` - DTOs Pydantic para artigos

### Routes (Rotas da API)
- `routes/admin_categorias_routes.py` - Rotas CRUD de categorias (admin)
- `routes/artigos_routes.py` - Rotas de artigos (autores e leitores)
- `routes/public_routes.py` - Atualização para exibir artigos na home

### Templates (Interface)
- `templates/admin/categorias/listar.html`
- `templates/admin/categorias/cadastrar.html`
- `templates/admin/categorias/editar.html`
- `templates/artigos/listar.html`
- `templates/artigos/cadastrar.html`
- `templates/artigos/editar.html`
- `templates/artigos/buscar.html`
- `templates/artigos/ler.html`
- `templates/index.html` - Home page do blog
- `templates/base_publica.html` - Atualização da navegação
- `templates/base_privada.html` - Atualização da navegação

### Configuração
- `util/perfis.py` - Perfis de usuário (ADMIN, AUTOR, LEITOR)
- `main.py` - Ponto de entrada da aplicação

---

## 19. Conclusão

Parabéns! Você concluiu a implementação do **BlogSimples**, um sistema de blog completo construído com:

- **FastAPI** - Framework web moderno e rápido
- **SQLite** - Banco de dados leve e embutido
- **Jinja2** - Motor de templates
- **Bootstrap 5** - Framework CSS responsivo
- **EasyMDE** - Editor Markdown visual
- **Marked.js** - Renderização de Markdown
- **Highlight.js** - Syntax highlighting para código

### Funcionalidades Principais:
1. Sistema de autenticação com três perfis (Admin, Autor, Leitor)
2. CRUD completo de categorias
3. CRUD completo de artigos com suporte a Markdown
4. Sistema de busca e filtros
5. Contagem de visualizações
6. Interface responsiva e moderna

### Possíveis Melhorias Futuras:
- Sistema de comentários nos artigos
- Upload de imagens
- Tags para artigos
- Paginação na listagem
- Sistema de favoritos
- Notificações por e-mail
- API REST para integração

Este tutorial demonstrou a arquitetura em camadas utilizada no projeto:
1. **Model** - Estrutura de dados
2. **SQL** - Queries do banco
3. **Repository** - Acesso a dados
4. **DTO** - Validação de entrada
5. **Routes** - Endpoints da API
6. **Templates** - Interface do usuário

Essa separação de responsabilidades facilita a manutenção e evolução do código.
