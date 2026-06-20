# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é

Boilerplate educacional (projetos integradores) com **arquitetura SPLIT**: API REST JSON em FastAPI + SPA React, repos separados na mesma raiz.

- `backend/` — FastAPI (Python 3.11+, SQLite **sem ORM**, SQL puro com prepared statements). Serve **apenas JSON** sob `/api` + `static/`. Em produção também serve o `index.html` do SPA buildado.
- `frontend/` — SPA React 19 + React Router 7 + TypeScript + Zod + Zustand + Vite. UI Bootstrap 5.3.8 + bootstrap-icons.
- Deploy: **dwa.ifes.site**. Em dev, Vite faz proxy de `/api`, `/static`, `/health` → backend (same-origin, sem CORS).
- `projects/` e `.lesson-bridge/` são **workspace externo** (specs de outros projetos, plugins) — não fazem parte deste app; **ignore-os** ao analisar/editar o código.

> **Esquema de portas (3 camadas)**: **8000** = porta interna do container (Uvicorn no Docker; imutável). **8400** = dev local (default do backend, alvo do proxy Vite, default do `configurar_projeto.py`). **8410** = porta publicada no VPS para o starter kit (`deploy/docker-compose.yml` mapeia `8410:8000`). Novos projetos forkados publicam em **outra** porta de host (8420, 8430, ...).

## Comandos

### Backend (rodar a partir de `backend/`)
O `.python-version` aponta para 3.14 (não instalado) — **sempre** usar o interpretador do venv:

```bash
backend/.venv/bin/python main.py                    # sobe API (porta via .env PORT; default dev 8400)
backend/.venv/bin/python -m pytest                  # todos os testes
backend/.venv/bin/python -m pytest tests/unit       # só unitários
backend/.venv/bin/python -m pytest tests/integration/test_x.py::TestClasse::test_metodo  # um teste
backend/.venv/bin/python -m pytest -m "not slow"    # markers: slow, integration, unit, auth, crud
```
Docs interativas em `/docs`. `pytest.ini` usa `asyncio_mode=auto`.

### Frontend (rodar a partir de `frontend/`)
```bash
npm run dev          # Vite dev server na porta 5180 (proxy /api -> VITE_BACKEND_URL, fallback 8400)
npm run build        # tsc -b && vite build  (saída em dist/, servida pelo backend em prod)
npm run test         # vitest run
npx tsc -b --noEmit  # typecheck isolado
npm run lint         # eslint
```

## Contrato de API — eixo central da conformidade backend↔frontend

Mudou algo de um lado, espelhe no outro. Os dois lados têm que bater **exato**.

- **Prefixo único `/api`**: backend monta todos os routers sob `API_PREFIX="/api"` (`backend/main.py`); frontend `src/lib/api.ts` usa `BASE='/api'`. Caminhos no front são **relativos a `/api`** (não incluir o prefixo).
- **Cliente HTTP central**: `frontend/src/lib/api.ts` — `credentials:'include'`, header `X-CSRF-Token` automático, classe `ApiError` (`.status`, `.type`, `.message`, `.errors`, `.retryAfter`). **Toda** chamada passa por aqui — exceto o chat SSE.
- **Contrato de erro**: `{detail, type, errors}` via handlers globais em `backend/util/exception_handlers.py`. Validação 422 → `util/validation_util.py:processar_erros_validacao_lista` chaveia erros por `loc[-1]` (último segmento; body aninhado vira chave simples). Traceback de dev fica fora do contrato.
- **Paginação**: envelope `PaginaResponse[T]` (`backend/dtos/responses/comum.py`: `items/pagina/por_pagina/total/total_paginas`) ↔ `PaginaResponse<T>` em `frontend/src/lib/types.ts`. Params `pagina`/`por_pagina`.
- **CSRF**: mutações enviam `X-CSRF-Token`; `GET /api/csrf-token` → `{token}`; webhooks de pagamento isentos.
- **Tipos espelhados**: Response DTOs em `backend/dtos/responses/*.py` ↔ tipos em `frontend/src/lib/types.ts` ↔ validação Zod em `frontend/src/lib/schemas.ts`.
- **Enums batem exato dos dois lados**: Perfil (Administrador/Cliente/Vendedor), StatusChamado, PrioridadeChamado, StatusPagamento, TipoInteracao, TipoNotificacao.
- **Chat = SSE**, FORA do cliente central: `EventSource` em `GET /chat/stream`. Payload tipado em `backend/dtos/responses/chat_response.py` (fonte única; espelhado em `ChatWidget.tsx`).

## Arquitetura backend (`backend/`)

Camadas: **Routes → DTOs → Repos → SQL → DB**. `main.py` registra repos (criação de tabelas) e routers.

- **Auth**: decorator `@requer_autenticacao()` (`util/auth_decorator.py`) + dataclass `UsuarioLogado` (NUNCA dict). Sessão por cookie (`SessionMiddleware`, `SameSite=lax`).
- **Ordem dos middlewares importa** (último `add_middleware` é o mais externo): SegurançaHeaders (externo) → Session → CSRF. CSRF precisa de `request.session` já populado.
- **Perfis**: enum `Perfil` de `util/perfis.py` (fonte única; NUNCA strings literais). Enums de domínio herdam de `EnumEntidade` (`util/enum_base.py`).
- **DB datetime**: usar `agora()` de `util/datetime_util.py` ao salvar (NUNCA `.strftime()`).
- **Validação de form**: validators em `dtos/validators.py`; levantam `ValueError` → 422.
- **Rate limit**: `util/api_helpers.py:checar_rate_limit` (já emite header `Retry-After`), usado por todas as rotas. `util/rate_limiter.py:com_rate_limit` é decorator legado **não usado**.
- **Seed admin**: `backend/data/admin_seed.json` (perfil Administrador) — útil p/ testar páginas protegidas/admin.

## Arquitetura frontend (`frontend/src/`)

**Leia `frontend/CONVENTIONS.md` antes de editar páginas.** A infra (api, tipos, stores, componentes, layouts, router) já existe — em geral só se implementam páginas em `src/pages/**`; não recriar helpers.

- `lib/` — `api.ts` (cliente), `schemas.ts` (Zod), `types.ts` (tipos+enums const), `format.ts` (`formatarData/DataHora/Hora/Moeda/Bytes`).
- `store/` — Zustand: `authStore` (sessão/usuário, `isAdmin()`), `uiStore` (toast/confirmação/alerta). Feedback **sempre** via `toast.sucesso/erro/aviso/info` ou `pedirConfirmacao`/`mostrarAlerta` — **NUNCA** `alert()/confirm()/prompt()` nativos.
- `hooks/useFetch.ts` — fetch com `{data, carregando, erro, recarregar}`.
- `router.tsx` — `PublicLayout`/`PrivateLayout`, `RootGate` (carrega sessão via `/api/me`; 401 anônimo é esperado), `ProtectedRoute`, `AdminRoute`.
- `components/` — chat (`ChatWidget` SSE), form (`Field`: TextField/TextAreaField/SelectField/SubmitButton), layout (`NotificationBell`), ui (Badges, Pagination, EmptyState, Spinner, Toasts, modais).
- Alias `@` → `src/`.
- **Textareas controladas** NÃO populam via MCP `fill`/`fill_form`; usar setter nativo + dispatch de evento `input`.

## Módulos de domínio (rota backend ↔ página frontend)

- **auth**: login/logout/cadastrar/esqueci-senha/redefinir-senha/me/csrf-token.
- **usuario**: dashboard, perfil (ver/editar/foto base64/senha). Foto: máx 10MB, valida tipo+tamanho no cliente.
- **chamados** + **admin/chamados**: CRUD + interações. Admin responder usa body DUAL (`dto_mensagem`+`dto_status`) no `POST /admin/chamados/{id}/interacoes`. StatusChamado: Aberto/Em Análise/Resolvido/Fechado.
- **pagamentos** + **admin/pagamentos**: Mercado Pago/Stripe/PayPal, webhooks server-to-server. StatusPagamento: Pendente/Em Processamento/Aprovado/Recusado/Cancelado/Reembolsado. NOTA: gateway MP não conecta em prod (token ausente) — decisão do usuário é IGNORAR.
- **chat**: SSE 1-a-1, salas, mensagens, busca de usuários.
- **notificacoes** + `NotificationBell`: polling de não-lidas.
- **admin core**: usuarios (CRUD), configuracoes (47 configs por categoria; valida `SalvarConfiguracaoLoteDTO`), backups (criar/restaurar/download; tipo `"manual"`/`"automatico"` SEM acento no valor de contrato), auditoria (logs de arquivo + trilha estruturada).

## Convenções de commit (do usuário)

- `git add` **SELETIVO**: só os arquivos que esta sessão alterou. NUNCA `git add -A/./-u`, `git commit -a/-am`. Rodar `git status --short` e cruzar com a lista de arquivos editados antes de commitar (há múltiplos agentes paralelos no mesmo repo).
- Pedir confirmação antes de push. PR só com permissão explícita por PR. Não se identificar como Claude nos commits.
