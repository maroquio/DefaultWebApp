# CLAUDE.md

Este arquivo orienta o Claude Code (claude.ai/code) ao trabalhar **neste backend**.

## Visão Geral do Projeto

**WebSPA / backend** é uma **API JSON pura** em FastAPI, derivada do boilerplate
`WebStandard` (FastAPI + Jinja) e convertida para servir um **frontend SPA em React**
(que será construído **depois** — **ainda não existe** neste repositório).

A API expõe todos os endpoints sob o prefixo **`/api`**, autentica por **cookie de
sessão** e segue um **contrato REST idiomático** com schemas Pydantic de resposta.
A pilha é: Python 3.11+, FastAPI, Pydantic 2, SQLite **sem ORM** (SQL puro).

> A fonte da verdade das decisões de arquitetura é
> [`../docs/PLANO_BACKEND.md`](../docs/PLANO_BACKEND.md). Leia-o antes de mudanças
> estruturais.

**Não existe mais** (foi removido na conversão para SPA): templates Jinja, flash
messages, redirect-after-post (PRG), troca de tema Bootswatch, assets de página
(CSS/JS), Cropper.js, `ErroValidacaoFormulario`, rotas públicas/exemplos e testes
e2e (Playwright).

## Executando a Aplicação

### Desenvolvimento (hot reload)
```bash
python main.py
```
Sobe em `http://{HOST}:{PORT}` (default `localhost:8000`). Em dev, o SPA roda
separado pelo Vite, que faz proxy de `/api` para o backend (same-origin).
Documentação OpenAPI interativa em `/docs`.

### Testes
```bash
pytest                              # Todos os testes
pytest tests/unit/                  # Unitários
pytest tests/integration/           # Integração (asserem JSON/status)
pytest -k test_login                # Por padrão de nome
pytest -m auth                      # Por marcador
```
Não há `tests/e2e/` — os testes Playwright foram removidos e voltarão com o front.

### Banco de Dados
```bash
sqlite3 dados.db ".tables"
sqlite3 dados.db "SELECT * FROM usuario;"
```

## Arquitetura

Camadas (mantidas do boilerplate, sem a parte de view):

```
Routes (JSON) → DTOs (entrada) → Repositories → SQL → SQLite
       ↓
Response Schemas (dtos/responses/) → JSON de saída
```

1. **Routes** (`routes/`): handlers HTTP que recebem DTO no body e retornam schema de resposta.
2. **DTOs de entrada** (`dtos/`): modelos Pydantic de validação (body/query).
3. **Models** (`model/`): dataclasses de domínio.
4. **Repositories** (`repo/`): acesso ao banco (CRUD).
5. **SQL** (`sql/`): queries como constantes (prepared statements com `?`).
6. **Response Schemas** (`dtos/responses/`): modelos Pydantic de **saída** (`response_model=`).
7. **Utilities** (`util/`): auth, CSRF, rate limit, e-mail, fotos, datetime, etc.

### Contrato da API (resumo — detalhe em `../docs/PLANO_BACKEND.md`)

**Sucesso:** recurso puro com status correto.
- `GET` único → `200` + schema do recurso.
- `GET` lista → `200` + `PaginaResponse[T]`.
- `POST` criação → `201` + recurso criado.
- `PUT/PATCH` → `200` + recurso atualizado.
- `DELETE` → `204` sem corpo.
- Ação sem recurso (ex: logout) → `200` + `MensagemResponse` (`{message}`).

**Erro (formato único):** todos os handlers em `util/exception_handlers.py` retornam
```json
{ "detail": "mensagem", "type": "validation_error|not_found|unauthorized|forbidden|conflict|rate_limited|internal_error", "errors": { "campo": ["msg"] } }
```
- `errors` é preenchido em erros de validação (422); nos demais vem `null`.
- Status usados: `400, 401, 403, 404, 409, 422, 429, 500`.
- Para devolver erro com `errors` de uma rota, lance
  `HTTPException(status_code=..., detail={"detail":..., "type":..., "errors":{...}})`
  — o `http_exception_handler` reconhece `detail` como dict (ver `auth_routes.post_cadastrar`).

**Entrada:**
- JSON body via DTO Pydantic como parâmetro da rota (não mais `Form()`).
- Upload de imagem (foto de perfil) vai como **base64 dentro do JSON** (`AtualizarFotoDTO.foto_base64`), não multipart.

**Saída:**
- Sempre via `response_model=` apontando para um schema de `dtos/responses/`.
- Enums serializados como **string do valor** (ex: `"Aberto"`), nunca índice.
- Datetime em **ISO 8601 com timezone** do app.
- Foto: schema expõe `foto_url` (URL relativa em `/static/...`) via `obter_caminho_foto_usuario`.

**Paginação:** `PaginaResponse[T] = {items, pagina, por_pagina, total, total_paginas}`
(`dtos/responses/comum.py`). Use `PaginaResponse.de_paginacao(paginacao, items)` com os
`items` já convertidos para o schema de resposta. Filtros/página via query string.

### Autenticação (cookie de sessão)

- `SessionMiddleware` (`SameSite=Lax`) guarda a sessão; o React usa
  `fetch(..., { credentials: 'include' })`.
- `@requer_autenticacao()` (`util/auth_decorator.py`) injeta
  `usuario_logado: UsuarioLogado` nos kwargs e lança:
  - **401** (`HTTPException`) se não houver sessão;
  - **403** se o perfil não estiver em `perfis_permitidos`.
- `@requer_autenticacao([Perfil.ADMIN.value])` restringe por perfil.
- Helpers: `criar_sessao()`, `destruir_sessao()`, `obter_usuario_logado()`, `esta_logado()`.
- Handshake do front: `GET /api/csrf-token` → `{token}`; `POST /api/login` cria a
  sessão; `GET /api/me` (em `auth_routes`) retorna o usuário atual ou 401;
  `POST /api/logout` limpa a sessão.

### CSRF (header X-CSRF-Token)

- `MiddlewareProtecaoCSRF` (`util/csrf_protection.py`) valida o header
  **`X-CSRF-Token`** em `POST/PUT/PATCH/DELETE`.
- O token vem de `GET /api/csrf-token` e fica na sessão.
- `GET` (inclusive o SSE `EventSource`) é isento de CSRF.
- `CSRF_EXEMPT_PATHS` isenta `/health` e os webhooks de pagamento
  (`/api/pagamentos/webhook` cobre, por prefixo, `mercadopago`/`stripe`/`paypal`).
  **Não** isente `/api/` inteiro — as mutações da API são protegidas pelo header.

### Rate Limiting

- `DynamicRateLimiter` (`util/rate_limiter.py`): lê limites do `config_cache` a cada
  checagem (ajustável em runtime, sem reiniciar). **Preferir** sobre `RateLimiter` estático.
- Nas rotas, chame `checar_rate_limit(limiter, request)` de `util/api_helpers.py`:
  lança **429** com header `Retry-After` quando excedido.
- `RegistroLimiters` em `rate_limiter.py` para monitoramento.

### Tempo real (SSE) e polling

- Chat: `GET /api/chat/stream` é um `StreamingResponse` `text/event-stream`
  consumido por `EventSource` (cookie enviado automaticamente; GET isento de CSRF).
  Envio de mensagem é POST com header CSRF. Gerenciado por
  `GerenciadorChat` (`util/chat_manager.py`).
- Notificações: polling do front em `GET /api/notificacoes/nao-lidas` (~30s).

## Banco de Dados

- Use sempre `with obter_conexao() as conn:` (`util/db_util.py`): commit no sucesso,
  rollback em exceção, fecha ao final. `conn.row_factory = sqlite3.Row`.
- `cursor.lastrowid` para o ID inserido; `cursor.rowcount` para linhas afetadas.
- **SQL injection:** SEMPRE `?` como placeholder, NUNCA concatenação.
- **Boolean em SQLite:** armazene INTEGER (0/1); leia com `bool(row["campo"])`.

## Data/Hora e Timezone

- **NUNCA** `datetime.now()` — use `agora()` de `util/datetime_util.py` (e `hoje()`).
- **NUNCA** use `.strftime()` ao gravar no banco — passe o objeto datetime direto.
  `.strftime()` só para exibição.
- Estratégia de armazenamento: datetimes são gravados como **UTC naive**;
  na leitura, `convert_datetime` (`util/db_util.py`) reanexa UTC e converte para
  `TIMEZONE` (`America/Sao_Paulo` por padrão). O código sempre trabalha com datetime
  *aware*. Na resposta JSON sai como ISO 8601 com offset.

## Perfis (Roles)

- **NUNCA** strings literais de perfil. Use o enum `Perfil` de `util/perfis.py`:
  `Perfil.ADMIN.value`, `Perfil.CLIENTE.value`, `Perfil.VENDEDOR.value`.
- `Perfil` herda de `EnumEntidade` (`util/enum_base.py`).
- Para adicionar perfis, edite **somente** `util/perfis.py`.
- Helpers: `Perfil.valores()`, `Perfil.nomes()`, `Perfil.existe()`, `Perfil.from_valor()`,
  `Perfil.validar()`, `Perfil.obter_por_nome()`, `Perfil.para_opcoes_select()`.

## UsuarioLogado (dataclass)

- **SEMPRE** tipe o parâmetro `usuario_logado` como `UsuarioLogado`
  (`from model.usuario_logado_model import UsuarioLogado`).
- **NUNCA** acesse como dict (`usuario_logado["id"]`) — use atributos (`usuario_logado.id`).
- Dataclass imutável (`frozen=True`): `id`, `nome`, `email`, `perfil`.
- Helpers: `is_admin()`, `is_cliente()`, `is_vendedor()`, `tem_perfil(*perfis)`.
- Construído na sessão a partir de `UsuarioLogado.from_usuario(usuario)`.

Padrão de rota:
```python
from typing import Optional
from fastapi import APIRouter, Request, status
from model.usuario_logado_model import UsuarioLogado
from util.auth_decorator import requer_autenticacao

router = APIRouter(prefix="/usuario")

@router.get("/perfil", response_model=UsuarioResponse)
@requer_autenticacao()
async def get_perfil(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    assert usuario_logado is not None
    ...
```

## Sistema de Validação (DTOs de entrada)

- DTO de entrada é o **body** da rota (Pydantic). Validações cross-field
  (ex: senhas coincidem) via `@model_validator` sobem como `ValidationError` →
  **422 nativo** do FastAPI, reformatado pelo `validation_exception_handler`
  usando `processar_erros_validacao_lista` (`util/validation_util.py`).
- **NÃO** existe mais `ErroValidacaoFormulario` (era do fluxo Jinja).
- Validadores reutilizáveis em `dtos/validators.py` (use com `field_validator`):
  - Texto: `validar_string_obrigatoria()`, `validar_comprimento()`, `validar_nome_pessoa()`.
  - E-mail: `validar_email()`. Senha: `validar_senha_forte()`, `validar_senhas_coincidem()`.
  - BR: `validar_cpf()`, `validar_cnpj()`, `validar_telefone_br()`, `validar_cep()`.
  - Datas/números/arquivos/enums: ver o arquivo.

```python
from pydantic import BaseModel, field_validator
from dtos.validators import validar_email, validar_senha_forte

class LoginDTO(BaseModel):
    email: str
    senha: str
    _v_email = field_validator("email")(validar_email())
    _v_senha = field_validator("senha")(validar_senha_forte())
```

## Como Criar um Novo Módulo JSON

Sequência (espelha `auth_routes.py` / `usuario_routes.py`):

1. **Model** (`model/entidade_model.py`): dataclass; enums de domínio herdam `EnumEntidade`.
2. **SQL** (`sql/entidade_sql.py`): constantes UPPERCASE (CRIAR_TABELA, INSERIR, OBTER_*, ATUALIZAR, EXCLUIR), com `?`.
3. **Repository** (`repo/entidade_repo.py`): funções CRUD + `_row_to_entidade()`.
4. **DTO de entrada** (`dtos/entidade_dto.py`): `CriarDTO`/`AlterarDTO` com validadores de `dtos/validators.py`.
5. **Response schema** (`dtos/responses/entidade_response.py`): modelo de saída + classmethod
   `de_entidade(...)`; para listas, monte `PaginaResponse[EntidadeResponse]`.
6. **Route** (`routes/entidade_routes.py`): `APIRouter(prefix="/entidade")`;
   `@requer_autenticacao()`; DTO como body; `response_model=`/`status_code=`;
   `checar_rate_limit(...)` onde fizer sentido; checagens de propriedade → 403/404.
7. **Registrar em `main.py`**: importar o repo e adicioná-lo a `TABELAS` (criação da
   tabela) e importar o router adicionando-o a `ROUTERS` (incluído sob `/api`).

Regras de conversão (caso porte algo do estilo Jinja):
`Form()` → DTO body • `RedirectResponse(303)` → recurso (200/201) ou 204 •
flash → some (o status + corpo é o feedback) • `TemplateResponse(erros)` → 422 nativo •
listagens → `PaginaResponse[T]`.

## Configuração

Carregada por `util/config.py` (python-dotenv). Veja `.env.example`. Chaves principais:

- `DATABASE_PATH`, `SECRET_KEY` (≥32 chars e ≠ default fora de dev — validado no startup),
  `HOST`, `PORT` (default **8000** no contexto SPA), `RELOAD`, `RUNNING_MODE`
  (`Development`/`Production` → `IS_DEVELOPMENT`), `TIMEZONE`.
- `BASE_URL`: base usada em links de e-mail (redefinição de senha aponta para o SPA) e
  nas `back_urls`/`webhook_url` de pagamento.
- `SPA_DIST_PATH`: caminho do build do React em produção (default `../frontend/dist`).
  Lido em `main.py`; quando existe e `not IS_DEVELOPMENT`, o catch-all serve o `index.html`.
- E-mail: `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `RESEND_FROM_NAME`.
- Pagamento: `MERCADOPAGO_*`, `STRIPE_*`, `PAYPAL_*`.
- Foto: `FOTO_PERFIL_TAMANHO_MAX`, `FOTO_MAX_UPLOAD_BYTES`. Senha: `PASSWORD_MIN/MAX_LENGTH`.
- Rate limits: dezenas de `RATE_LIMIT_*_MAX` / `RATE_LIMIT_*_MINUTOS`.

**Configuração híbrida:** Database (tabela `configuracao`) → `.env` → default hardcoded.
Editável em runtime via `PUT /api/admin/configuracoes`; cacheada em `util/config_cache.py`
(`ConfigCache`, thread-safe). `util/migrar_config.py` semeia o banco a partir do `.env` no startup.

## Servir o SPA (produção) e estáticos

- `/static` é montado se a pasta existir (serve uploads/fotos).
- Em produção (`not IS_DEVELOPMENT`), se `SPA_DIST_PATH` existir, `main.py` monta
  `/assets` e registra um catch-all `GET /{caminho_spa:path}` que devolve `index.html`.
  O catch-all é registrado **por último** e nunca captura `/api` nem `/static`.
- Em dev, **não** há catch-all: o SPA é servido pelo Vite com proxy de `/api`.

## Seed Data

- JSON em `data/`, carregado no startup por `util/seed_data.py`.
- Admin padrão de `data/usuarios_seed.json` (ex: `admin@sistema.com` / `Admin@123`).

## Testes

- `tests/conftest.py`: fixtures globais (`client` TestClient com sessão limpa,
  `cliente_autenticado`, `admin_autenticado`, helpers `criar_usuario`/`fazer_login`,
  banco temporário).
- `tests/unit/`: unitários. `tests/integration/`: aferem JSON/status da API.
- `tests/helpers/`: helpers de teste.
- Marcadores: `@pytest.mark.auth`, `@pytest.mark.crud`, `@pytest.mark.integration`, `@pytest.mark.unit`.

## Grupos de Endpoints (todos sob `/api`)

| Router (`routes/`) | Prefixo | Endpoints principais |
|--------------------|---------|----------------------|
| `auth_routes.py` | `/api` | `GET /csrf-token`, `GET /me`, `POST /login`, `POST /logout`, `POST /cadastrar`, `POST /esqueci-senha`, `POST /redefinir-senha` |
| `usuario_routes.py` | `/api/usuario` | `GET /dashboard`, `GET/PUT /perfil`, `PUT /senha`, `PUT /foto` (base64) |
| `admin_usuarios_routes.py` | `/api/admin/usuarios` | CRUD admin (lista paginada), guard 403 |
| `admin_configuracoes_routes.py` | `/api/admin` | `GET/PUT /configuracoes`, `GET /auditoria/logs`, `GET /auditoria/registros` |
| `chamados_routes.py` | `/api/chamados` | `GET /` (paginado), `POST`, `GET /{id}`, responder, `DELETE /{id}` |
| `admin_chamados_routes.py` | `/api/admin/chamados` | lista, `GET /{id}`, responder, `PATCH /{id}/status` |
| `chat_routes.py` | `/api/chat` | `GET /stream` (SSE), `POST /salas`, `GET /conversas`, `GET /mensagens/{sala_id}`, `POST /mensagens`, `POST /mensagens/lidas/{sala_id}`, `GET /mensagens/nao-lidas/total`, `GET /usuarios/buscar` |
| `notificacao_routes.py` | `/api/notificacoes` | `GET /`, `GET /nao-lidas`, `PATCH /marcar-todas`, `PATCH /{id}/lida`, `DELETE /lidas`, `DELETE /{id}` |
| `pagamento_routes.py` | `/api/pagamentos` | `GET`, `POST` (→ `{init_point}`), `GET /{id}`, `POST /{id}/paypal/capturar`, `POST /webhook/{mercadopago\|stripe\|paypal}` (isento CSRF/auth) |
| `admin_pagamentos_routes.py` | `/api/admin/pagamentos` | lista paginada, `GET /{id}` (dados do provider) |
| `admin_backups_routes.py` | `/api/admin/backups` | listar, criar, `GET /{nome}/download`, restaurar, excluir |

## Arquivos Importantes

### Núcleo
- `main.py`: middlewares (Session + CSRF), handlers JSON, criação de tabelas/seed,
  registro de routers sob `/api`, `/static`, catch-all SPA (prod), `/health`.

### Utilities
- `util/auth_decorator.py`: `@requer_autenticacao` (401/403) + sessão.
- `util/csrf_protection.py`: `MiddlewareProtecaoCSRF` (header `X-CSRF-Token`) + `obter_token_csrf`.
- `util/exception_handlers.py`: handlers JSON do contrato de erro (`resposta_erro`).
- `util/validation_util.py`: processamento de erros de validação para o campo `errors`.
- `util/api_helpers.py`: `checar_rate_limit` (429 + `Retry-After`).
- `util/rate_limiter.py`: `RateLimiter`, `DynamicRateLimiter`, `RegistroLimiters`, `obter_identificador_cliente`.
- `util/perfis.py`: fonte única de perfis (`EnumEntidade`).
- `util/enum_base.py`: base de todos os enums de domínio.
- `util/db_util.py`: conexão + adaptação de datetime (UTC naive).
- `util/datetime_util.py`: `agora()`, `hoje()`, conversões ISO.
- `util/security.py`: hash bcrypt; `util/senha_util.py`: força de senha.
- `util/email_service.py`: envio via Resend; links de e-mail usam `BASE_URL` (SPA).
- `util/foto_util.py`: fotos de perfil; `obter_caminho_foto_usuario` devolve URL para os schemas.
- `util/config.py` / `util/config_cache.py` / `util/migrar_config.py`: config híbrida.
- `util/seed_data.py`, `util/logger_config.py`, `util/security_headers.py`.
- `util/chat_manager.py`: `GerenciadorChat` (SSE). `util/notificacao_util.py`,
  `util/auditoria_decorator.py`, `util/backup_util.py`, `util/upload_util.py`, `util/paginacao_util.py`.
- `util/mercadopago_util.py`, `util/payment_service.py`, `util/payment_provider.py`, `util/payment_adapters/`.
- `util/validation_helpers.py`: disponibilidade de e-mail.

### DTOs (entrada)
- `dtos/validators.py`, `dtos/auth_dto.py`, `dtos/usuario_dto.py`, `dtos/perfil_dto.py`
  (inclui `AtualizarFotoDTO.foto_base64`), `dtos/chamado_dto.py`,
  `dtos/chamado_interacao_dto.py`, `dtos/chat_dto.py`, `dtos/configuracao_dto.py`,
  `dtos/pagamento_dto.py`.

### Response Schemas (`dtos/responses/`)
- `comum.py`: `ErroResponse`, `MensagemResponse`, `TokenCsrfResponse`, `PaginaResponse[T]`.
- `usuario_response.py` (`UsuarioResponse`, `DashboardResponse`), `chamado_response.py`,
  `chat_response.py`, `notificacao_response.py`, `pagamento_response.py`,
  `config_response.py`, `auditoria_response.py`, `backup_response.py`.

### Models / SQL / Repos
- `model/`: `usuario_model.py`, `usuario_logado_model.py`, `chamado*`, `chat_*`,
  `notificacao_model.py`, `auditoria_model.py`, `pagamento_model.py`, `configuracao_model.py`.
- `sql/` e `repo/`: um por entidade + `indices_*` para índices de performance.

## Estilo de Código

- Dataclasses para models; type hints em tudo; constantes SQL UPPERCASE.
- Docstrings (especialmente em repos); funções privadas com `_` (ex: `_row_to_entidade`).
- Ordem de import: stdlib → terceiros → local (DTOs → Models → Repos → Utils).
- Validadores de `dtos/validators.py`; enums de domínio herdam `EnumEntidade`.

## Notas de Segurança

- Senhas com bcrypt (`util/security.py`); regras em `util/senha_util.py`.
- Rate limiting via `DynamicRateLimiter` + `checar_rate_limit`.
- Security headers em `util/security_headers.py`.
- SQL injection: prepared statements. CSRF: header `X-CSRF-Token`.
- `SECRET_KEY` validada no startup (mín. 32 chars fora de dev).
- Path traversal protegido no sistema de backups.

## Health Check

`GET /health` → `{"status": "healthy"}` (fora de `/api`; isento de CSRF).
