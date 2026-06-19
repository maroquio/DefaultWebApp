# WebSPA — Backend (API JSON)

Backend **FastAPI** que expõe uma **API JSON pura** para um frontend **SPA em React**.
Derivado do boilerplate `WebStandard` (FastAPI + Jinja) e convertido para servir apenas
JSON: sem templates, sem HTML renderizado no servidor.

> **Arquitetura SPLIT.** O SPA em React (React Router 7 + Zod + Zustand) vive em
> [`../frontend`](../frontend) e consome esta API via `fetch(..., { credentials: 'include' })`.
> Em dev o Vite faz proxy de `/api`, `/static` e `/health` para este backend (same-origin,
> sem CORS). Em produção o FastAPI também serve o build do SPA (`index.html` + assets).

A referência completa de arquitetura e do contrato da API está no
**[`../CLAUDE.md`](../CLAUDE.md)** (raiz do repositório).

## Stack

- **Python 3.11+**, **FastAPI**, **Uvicorn** (ASGI)
- **Pydantic 2** — validação de entrada e schemas de resposta (OpenAPI forte)
- **SQLite** sem ORM (SQL puro com prepared statements)
- **bcrypt** (hash de senhas), **Pillow** (processamento de imagem de perfil)
- **SSE** (Server-Sent Events) para o chat em tempo real
- **Resend** (e-mail transacional), **Mercado Pago / Stripe / PayPal** (pagamentos)

## Conceitos do Contrato

- **Prefixo único `/api`** para todos os endpoints.
- **Autenticação por cookie de sessão** (`SessionMiddleware`, `SameSite=Lax`).
- **CSRF por header**: `GET /api/csrf-token` devolve `{token}`; mutações enviam
  `X-CSRF-Token`. Webhooks de pagamento são isentos.
- **Sucesso** = recurso puro (`200/201/204`). **Erro** = `{detail, type, errors}`
  (`400/401/403/404/409/422/429/500`).
- **Entrada** em JSON via DTO Pydantic; foto de perfil vai em **base64** no JSON.
- **Saída** via schemas Pydantic (`dtos/responses/`): enums como string, datetime ISO
  com timezone, listas como `PaginaResponse {items, pagina, por_pagina, total, total_paginas}`.

## Como Rodar

### Pré-requisitos
- Python 3.11+ e pip.

> O arquivo `.python-version` aponta para 3.14 (pode não estar instalado). As versões
> em `requirements.txt` (Pydantic 2.13, httpx 0.28) já têm wheels para 3.14, mas
> 3.11–3.13 funcionam. Use sempre o interpretador do venv local (`.venv/bin/python`).

### Instalação
```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux/Mac  (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
cp .env.example .env             # edite ao menos SECRET_KEY e APP_NAME
```

### Desenvolvimento
```bash
.venv/bin/python main.py         # ou: source .venv/bin/activate && python main.py
```
Sobe em `http://localhost:8000` por padrão (configurável via `HOST`/`PORT` no `.env`).
Documentação interativa da API em `/docs`.

Com o SPA presente em dev, o **Vite** roda separado (porta 5180) e faz **proxy de `/api`,
`/static` e `/health`** para este backend (mesma origem) — sem CORS. O Vite proxia para
`VITE_BACKEND_URL` (fallback `http://127.0.0.1:8400`); se o backend subir em outra porta,
ajuste `PORT` no `.env` **e** o alvo do proxy para que batam.

### Produção
- Construa o build do React em `SPA_DIST_PATH` (default `../frontend/dist`).
- Rode o backend com `RUNNING_MODE=Production`. O FastAPI serve o `index.html` do SPA
  via catch-all (todas as rotas fora de `/api` e `/static`) e os assets em `/assets`.

### Docker
```bash
docker compose build
docker compose up -d
docker compose logs -f
```

## Estrutura de Pastas

```
backend/
├── main.py                 # App: middlewares, handlers JSON, routers /api, /static, catch-all SPA
├── dtos/                   # DTOs de entrada (Pydantic) + validators.py
│   └── responses/          # Schemas de SAÍDA (comum.py: PaginaResponse, ErroResponse, ...)
├── model/                  # Dataclasses de domínio
├── repo/                   # Acesso ao banco (CRUD) + índices
├── sql/                    # Queries SQL como constantes (prepared statements)
├── routes/                 # Routers por módulo (todos sob /api)
├── util/                   # auth, csrf, rate limit, e-mail, fotos, datetime, config, etc.
├── data/                   # Seed data (usuarios_seed.json)
├── static/                 # Uploads/fotos de perfil servidos em /static
├── tests/                  # unit/ e integration/ (sem e2e)
├── .env.example
└── requirements.txt
```

## Endpoints por Módulo (todos sob `/api`)

| Módulo | Prefixo | Resumo |
|--------|---------|--------|
| **Autenticação** | `/api` | `GET /csrf-token`, `GET /me`, `POST /login`, `POST /logout`, `POST /cadastrar`, `POST /esqueci-senha`, `POST /redefinir-senha` |
| **Usuário** | `/api/usuario` | `GET /dashboard`, `GET/PUT /perfil`, `PUT /senha`, `PUT /foto` (base64) |
| **Admin · Usuários** | `/api/admin/usuarios` | CRUD de usuários (lista paginada) — somente admin |
| **Admin · Config/Auditoria** | `/api/admin` | `GET/PUT /configuracoes`, `GET /auditoria/logs`, `GET /auditoria/registros` |
| **Chamados** | `/api/chamados` | listar (paginado), criar, ver, responder, excluir os próprios |
| **Admin · Chamados** | `/api/admin/chamados` | listar todos, ver, responder, `PATCH /{id}/status` |
| **Chat (SSE)** | `/api/chat` | `GET /stream` (EventSource), salas, conversas, mensagens, não-lidas, busca |
| **Notificações** | `/api/notificacoes` | listar, não-lidas (polling), marcar lidas, excluir |
| **Pagamentos** | `/api/pagamentos` | `POST` → `{init_point}`, status, captura PayPal, `POST /webhook/{provider}` (isento) |
| **Admin · Pagamentos** | `/api/admin/pagamentos` | listagem paginada + detalhes do provider |
| **Admin · Backups** | `/api/admin/backups` | listar, criar, baixar, restaurar, excluir |
| **Infra** | `/health` | health check (fora de `/api`) |

## Configuração (.env)

Veja `.env.example` para a lista completa e comentada. Destaques:

- `SECRET_KEY`, `DATABASE_PATH`, `HOST`, `PORT` (default **8000**), `RUNNING_MODE`, `TIMEZONE`.
- `BASE_URL` — usada nos links de e-mail (apontam para o SPA) e nas `back_urls`/webhook de pagamento.
- `SPA_DIST_PATH` — caminho do build do React em produção (default `../frontend/dist`).
- `RESEND_*` (e-mail), `MERCADOPAGO_*` / `STRIPE_*` / `PAYPAL_*` (pagamentos).
- Diversos `RATE_LIMIT_*` — ajustáveis em runtime via `PUT /api/admin/configuracoes`
  (configuração híbrida: banco → `.env` → default).

## Usuário Padrão (seed)

Criado no startup a partir de `data/usuarios_seed.json`:

| Perfil | E-mail | Senha |
|--------|--------|-------|
| Administrador | admin@sistema.com | Admin@123 |

> Altere e-mail/senha em produção.

## Testes

```bash
.venv/bin/python -m pytest                    # tudo
.venv/bin/python -m pytest tests/unit/        # unitários
.venv/bin/python -m pytest tests/integration/ # integração (asserem JSON/status)
.venv/bin/python -m pytest -m auth            # por marcador (auth, crud, slow, integration, unit, e2e)
```
Não há testes e2e neste backend (Playwright foi removido na conversão para SPA).

## Documentação Adicional

- **[`../CLAUDE.md`](../CLAUDE.md)** — arquitetura, contrato e convenções (fonte da verdade para agentes).
- **`/docs`** (em runtime) — OpenAPI/Swagger gerado automaticamente.
