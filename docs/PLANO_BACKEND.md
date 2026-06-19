# Plano de Implementação — Backend WebSPA

> Backend FastAPI puramente JSON, derivado do `WebStandard` (FastAPI + Jinja),
> destinado a um frontend SPA (React + React Router + Zod + Zustand) que será
> construído **depois**. Esta fase NÃO toca em nada de frontend.

---

## 1. Decisões travadas (sessão de grilling)

| # | Tema | Decisão |
|---|------|---------|
| 1 | Origem do backend | **Copiar `WebStandard/` → `WebSPA/backend/`** e desacoplar a camada Jinja; manter models/DTOs/validators/repos/SQL/auth/rate-limit. |
| 2 | Autenticação | **Cookie de sessão** (mantém `SessionMiddleware` + `UsuarioLogado`). React usa `fetch(..., {credentials:'include'})`. |
| 3 | Origem/CORS | **Vite proxy em dev** (`/api` → `:8000`, same-origin), **FastAPI serve `dist/` em prod** (same-origin). Sem CORS cross-site; cookie `SameSite=Lax`. |
| 4 | CSRF | **Mantido via header** `X-CSRF-Token`. `GET /api/csrf-token` expõe o token. Defesa em camadas com `SameSite=Lax`. |
| 5 | Escopo | **Todos os módulos** convertidos nesta leva (auth, usuários, config, chamados+interações, chat SSE, notificações, auditoria, pagamentos, backups). |
| 6 | Contrato JSON | **REST idiomático**: sucesso = recurso puro + status correto (200/201/204). Erro = `{detail, type, errors:{campo:[msgs]}}` + 4xx/5xx. |
| 7 | Serialização | **Schemas Pydantic de resposta** dedicados (`response_model=`). OpenAPI forte → permite codegen no front depois. |
| 8 | Entrada | **JSON body** (DTO Pydantic como body); **multipart só para upload** (`UploadFile`). |
| 9 | Prefixo | **`/api`** em todos os routers. Catch-all serve SPA fora de `/api` e `/static`. |
| 10 | Tempo real | **Manter SSE** (chat, GET + cookie via `EventSource`) + **polling** (notificações 30s). |
| 11 | Pagamento MP | `POST /api/pagamentos` → `{init_point}`; `back_urls` apontam pro SPA; webhook = `POST /api/pagamentos/webhook` (sem auth/CSRF), fonte da verdade. |
| 12 | Erros de validação | **422 nativo do FastAPI reformatado** pro contrato de erro. Aposenta `ErroValidacaoFormulario`. |
| 13 | Guardas | **401** (não logado) / **403** (perfil) / **429** (rate limit, + `Retry-After`), todos JSON. |
| 14 | Testes | **unit** intacto; **integration** reescrito p/ asserir JSON/status; **e2e Playwright removido** (volta com o front). |
| 15 | Links de e-mail | Apontam pro **SPA** (`{BASE_URL}/redefinir-senha?token=`); API só valida token. Nova config `BASE_URL`/`FRONTEND_URL`. |
| 16 | Estáticos/uploads | Mantém mount `/static` (uploads incluídos); `*_url` no response. Ordem prod: `/api` → `/static` → catch-all `index.html`. |
| 17 | Paginação | Envelope `PaginaResponse[T] = {items, pagina, por_pagina, total, total_paginas}`. Filtros/página via query string. |
| 18 | Frontend | **Nada** nesta fase. |

---

## 2. Contrato da API (fonte da verdade pro front futuro)

### 2.1 Sucesso
- `GET` recurso único → `200` + corpo = schema do recurso.
- `GET` lista → `200` + `PaginaResponse[T]`.
- `POST` criação → `201` + recurso criado (com `id`).
- `PUT/PATCH` → `200` + recurso atualizado.
- `DELETE` → `204` sem corpo.
- Ações sem recurso (ex: logout) → `200` + `{message}` opcional.

### 2.2 Erro (formato único)
```json
{
  "detail": "Mensagem legível geral",
  "type": "validation_error | not_found | unauthorized | forbidden | rate_limited | conflict | internal_error",
  "errors": { "email": ["E-mail inválido"], "senha": ["Mínimo 8 caracteres"] }
}
```
- `errors` presente só em erros de campo (422). Demais erros podem trazer `errors: null`.
- Status codes: `400, 401, 403, 404, 409, 422, 429, 500`.

### 2.3 Paginação
```json
{ "items": [ ... ], "pagina": 2, "por_pagina": 10, "total": 57, "total_paginas": 6 }
```
Query: `?pagina=&por_pagina=&q=&<filtros específicos>`.

### 2.4 Datas e enums
- Datas: ISO 8601 com timezone do app (ex `2026-06-17T10:30:00-03:00`).
- Enums: serializados como **string do valor** (ex `"Aberto"`), nunca índice.

### 2.5 Auth/CSRF (handshake do front)
1. `GET /api/csrf-token` → `{token}` (também seta cookie de sessão se ainda não houver).
2. Mutações (`POST/PUT/PATCH/DELETE`) enviam header `X-CSRF-Token`.
3. `POST /api/login` seta cookie de sessão; `POST /api/logout` limpa.
4. `GET /api/me` → usuário logado atual ou `401`.

---

## 3. O que copiar / alterar / remover

### 3.1 Copiar intacto (ou quase)
- `model/` — todos (dataclasses de domínio).
- `dtos/` (entrada) — `validators.py` + DTOs de entrada (revisar p/ uso como body).
- `repo/` — todos.
- `sql/` — todos.
- `util/` reaproveitados: `enum_base.py`, `perfis.py`, `db_util.py`, `datetime_util.py`,
  `security.py`, `senha_util.py`, `config.py`, `config_cache.py`, `rate_limiter.py`,
  `permission_helpers.py`, `repository_helpers.py`, `validation_helpers.py`,
  `validation_util.py`, `logger_config.py`, `email_service.py`, `foto_util.py`,
  `upload_util.py`, `paginacao_util.py`, `notificacao_util.py`, `auditoria_decorator.py`,
  `chat_manager.py`, `backup_util.py`, `mercadopago_util.py`, `payment_*`, `seed_data.py`,
  `security_headers.py`, `migrar_config.py`.
- `tests/unit/`, `tests/helpers/`, `tests/conftest.py` (ajustar fixtures p/ JSON).
- Infra: `requirements.txt`, `pyproject.toml`, `pytest.ini`, `.flake8`,
  `.python-version`, `Dockerfile`, `docker-compose.yml`, `.env.example`, `.gitignore`.

### 3.2 Alterar
- **`main.py`**: remover setup Jinja/templates; remover handlers que renderizam template;
  registrar routers sob `/api`; adicionar `/api/csrf-token`, `/api/me`;
  manter `/static`; adicionar catch-all SPA **só em produção**.
- **`util/auth_decorator.py`**: `@requer_autenticacao()` lança `HTTPException(401)`
  (não logado) / `HTTPException(403)` (perfil) em vez de `RedirectResponse`.
  Mantém injeção de `usuario_logado` e `criar_sessao`/`destruir_sessao`.
- **`util/csrf_protection.py`**: validar exclusivamente via header `X-CSRF-Token`;
  manter `CSRF_EXEMPT_PATHS` (webhook MP). Garantir rota `/api/csrf-token`.
- **`util/exception_handlers.py`**: reescrever os 4 handlers para `JSONResponse`
  no formato §2.2. O de `RequestValidationError` (422) usa `processar_erros_validacao`
  de `validation_util.py` para preencher `errors`.
- **`util/rate_limit_decorator.py`** (e checagens inline nas rotas): retornar
  `JSONResponse(429)` + header `Retry-After` em vez de template.
- **`dtos/` entrada**: usados diretamente como body — confirmar que validações
  cross-field (`@model_validator`, ex senhas coincidem) sobem como `ValidationError`
  → 422 nativo.
- **Routes (todas)**: ver §4 (transformação rota-a-rota).
- **`util/email_service.py`** / fluxos de e-mail: montar links com `BASE_URL` apontando
  pro SPA (redefinir senha, verificar conta).
- **`util/config.py`** / `.env.example`: adicionar `BASE_URL` (e/ou `FRONTEND_URL`),
  `IS_PRODUCTION`/`RUNNING_MODE` já existe; documentar `SPA_DIST_PATH`.
- **`util/foto_util.py`**: expor helper que devolve **URL** da foto (`/static/uploads/...`)
  para os response schemas (substitui o filtro Jinja `foto_usuario`).

### 3.3 Remover
- `templates/` inteiro.
- Componentes UI de `static/` (CSS/JS de página). **Manter** `static/uploads/` e assets
  servidos como mídia.
- `util/template_util.py`, `util/flash_messages.py`, `util/tema_css_util.py`,
  `util/toast_css_util.py`, `util/exportacao_util.py` (exportação CSV/Excel era
  download de página; reavaliar — pode virar endpoint JSON/stream depois, fora do escopo).
- `util/exceptions.py::ErroValidacaoFormulario` (e usos).
- `routes/public_routes.py` e `routes/examples_routes.py` (páginas Jinja institucionais
  e exemplos de UI) — o que for endpoint útil migra; o resto sai.
- `tests/e2e/` (Playwright sobre Jinja).

---

## 4. Transformação rota-a-rota (padrão mecânico)

Para cada rota que hoje renderiza/redireciona:

```python
# ANTES (Jinja)
@router.post("/cadastrar")
@requer_autenticacao()
async def post_cadastrar(request, titulo: str = Form(), ..., usuario_logado=None):
    try:
        dto = CriarChamadoDTO(titulo=titulo, ...)
    except ValidationError as e:
        raise ErroValidacaoFormulario(...)
    id = chamado_repo.inserir(...)
    informar_sucesso(request, "Criado")
    return RedirectResponse("/chamados/listar", 303)

# DEPOIS (JSON)
@router.post("", response_model=ChamadoResponse, status_code=201)
@requer_autenticacao()
async def criar_chamado(dto: CriarChamadoDTO, usuario_logado=None):
    id = chamado_repo.inserir(Chamado(...))
    return chamado_repo.obter_por_id(id)   # vira ChamadoResponse
```

Regras:
- `Form()` → DTO body. Upload permanece `UploadFile` em rota multipart dedicada.
- `RedirectResponse(303)` → retorno do recurso (201/200) ou `204`.
- `informar_sucesso/erro` (flash) → desaparece; feedback é o status + corpo.
- `TemplateResponse(..., {erros})` → desaparece; erro vem do 422 nativo.
- Listagens → `PaginaResponse[T]` via `obter_paginado`.
- Verificação de propriedade (`permission_helpers`) → `HTTPException(403)`.

### Mapa de routers (todos sob `/api`)
| Arquivo origem | Prefixo novo | Observações |
|----------------|--------------|-------------|
| `auth_routes.py` | `/api` (login, logout, registro, recuperar/redefinir senha) | links de e-mail → SPA; `/api/me`, `/api/csrf-token` |
| `usuario_routes.py` | `/api/usuarios` | perfil próprio, troca de senha, upload de foto (multipart) |
| `admin_usuarios_routes.py` | `/api/admin/usuarios` | CRUD admin, guard 403 |
| `admin_configuracoes_routes.py` | `/api/admin/config` | config híbrida (DB) |
| `chamados_routes.py` | `/api/chamados` | mestre-detalhe c/ interações; paginação+filtro |
| `admin_chamados_routes.py` | `/api/admin/chamados` | guard 403 |
| `chamado_interacao` (dentro de chamados) | `/api/chamados/{id}/interacoes` | sub-recurso |
| `chat_routes.py` | `/api/chat` | **SSE**: `GET /api/chat/stream/{sala}` (EventSource); envio via POST |
| `notificacao_routes.py` | `/api/notificacoes` | `GET .../nao-lidas` (polling); marcar lida |
| `pagamento_routes.py` | `/api/pagamentos` | criar→`{init_point}`; `GET /{id}` status; `POST /webhook` (isento) |
| `admin_pagamentos_routes.py` | `/api/admin/pagamentos` | guard 403 |
| `admin_backups_routes.py` | `/api/admin/backups` | criar/listar/restaurar/excluir |
| `public_routes.py` | — | avaliar caso a caso; maioria sai |
| `examples_routes.py` | — | remover |

---

## 5. Novos artefatos a criar

- `dtos/responses/` — schemas Pydantic de saída por entidade
  (`usuario_response.py`, `chamado_response.py`, `pagamento_response.py`, ...),
  + genérico `PaginaResponse` e `ErroResponse`.
- `util/respostas.py` (opcional) — helpers de montagem de erro padronizado.
- Rotas novas: `GET /api/csrf-token`, `GET /api/me`.
- Catch-all SPA em `main.py` (prod, condicional a `dist/` existir).
- Config nova: `BASE_URL`/`FRONTEND_URL`, `SPA_DIST_PATH`.

---

## 6. Ordem de execução (fases)

1. **Esqueleto**: copiar base p/ `WebSPA/backend/`, remover `templates/` e UI de `static/`,
   limpar imports de Jinja/flash. App sobe vazio (`/health`).
2. **Núcleo de plataforma**:
   - `main.py` (routers `/api`, sem Jinja, `/static`, catch-all prod).
   - `exception_handlers.py` → JSON (contrato §2.2).
   - `auth_decorator.py` → 401/403.
   - `csrf_protection.py` → header + `/api/csrf-token`.
   - `rate_limit` → 429.
3. **Auth**: login/logout/registro/recuperação + `/api/me`; links de e-mail → SPA.
4. **Schemas de resposta** + `PaginaResponse` (base do contrato).
5. **Usuários** (próprio + admin + upload foto) — valida padrão completo.
6. **Config**, **Chamados+interações**, **Notificações**, **Auditoria**.
7. **Chat (SSE)** — `EventSource`-friendly.
8. **Pagamentos** — `init_point`, `back_urls` SPA, webhook.
9. **Backups admin**.
10. **Testes**: ajustar unit; reescrever integration p/ JSON/status; remover e2e.
11. **Revisão**: OpenAPI limpo (`/docs`), `.env.example`, README do backend.

Checkpoint de revisão sugerido ao fim das fases **2** e **5**.

---

## 7. Pontos de atenção / riscos

- **`@requer_autenticacao` + assinatura de rota**: o decorator injeta `usuario_logado`
  via kwargs; com DTO como body confirmar compatibilidade de assinatura (ordem dos params,
  `request` ainda necessário onde se lê sessão/IP).
- **CSRF em SSE**: `GET` (EventSource) é isento; envio de mensagem de chat (POST) exige header.
- **Webhook MP** precisa estar em `CSRF_EXEMPT_PATHS` e sem `@requer_autenticacao`.
- **`config_cache` / migrar_config**: dependem de tabela `configuracao`; manter startup.
- **Exportação CSV/Excel**: fora do escopo desta leva; decidir formato (stream) depois.
- **`public_routes`/`examples_routes`**: triagem manual antes de remover.
- **Catch-all**: registrar **por último** e nunca capturar `/api` nem `/static`.
- **Regra de commit do projeto**: `git add` seletivo, só arquivos desta sessão.

---

## 8. Fora de escopo (explícito)

- Qualquer código de frontend (React/Router/Zod/Zustand).
- Geração de tipos TS/zod a partir do OpenAPI (fase do front).
- Deploy/CI específico do SPA.
- Migração de exportação CSV/Excel.
