# FORKING.md — Como criar um projeto novo a partir deste starter kit

Este repositório é um **starter kit**: um boilerplate de SaaS (FastAPI + SPA React) sobre
o qual outros projetos são construídos. Este documento é a **fonte da verdade** sobre o que
muda ao iniciar um projeto novo a partir dele.

A aplicação starter kit roda em **dwa.ifes.site** (porta de host **8410** no VPS). Projetos
novos serão deployados em **outros domínios e outras portas**, com o container e os volumes
renomeados para o projeto.

---

## 1. Conceito de portas (3 camadas — não confundir)

| Porta | Papel | Onde |
|------|-------|------|
| **8000** | Porta **interna** do container (Uvicorn dentro do Docker). **Imutável**, igual em todo projeto. | `deploy/Dockerfile` (`EXPOSE`/`CMD`), `deploy/Jenkinsfile` (`PORT=8000`), healthcheck |
| **8400** | **Dev local**: default do backend, alvo do proxy Vite, default do `configurar_projeto.py`. | `backend/.env.example`, `backend/util/config.py`, `frontend/vite.config.ts`, `configurar_projeto.py` |
| **8410** | Porta **publicada no VPS** para o starter kit. | `deploy/docker-compose.yml` (`8410:8000`), `deploy/Jenkinsfile` (`BASE_URL=...:8410`) |

**Projeto novo**: porta de host segue convenção **+1** a partir de 8410 (8411, 8412, ...),
podendo ser escolhida manualmente. **Evite colisão** com containers já no VPS. A porta interna
continua **8000** — só muda o lado esquerdo do mapeamento `HOST:8000` no compose.

---

## 2. Checklist de rename (por projeto)

Defina três valores: **`<slug>`** (curto, ex. `dwa`), **`<dominio>`** (ex. `meuprojeto.com`),
**`<porta_host>`** (ex. `8411`). Depois aplique:

### 2a. Dev local — rode o configurador
```bash
cd backend && .venv/bin/python scripts/configurar_projeto.py
```
Ele reescreve, sem apagar arquivos existentes sem confirmação:
- `backend/.env` (a partir de `.env.example`): `APP_NAME`, `SECRET_KEY` (gerada), `PORT`, `RESEND_*`.
- `backend/util/perfis.py`: o enum `Perfil` com os perfis do novo projeto (Administrador + extras).
- `backend/data/usuarios_seed.json`: o admin inicial.

> O configurador cobre só o **dev local**. O deploy (abaixo) é editado à mão.

### 2b. Deploy — edite à mão
**`deploy/docker-compose.yml`**:
- `container_name: <slug>.<dominio>`  (hoje `dwa.ifes.site`)
- `ports: ["<porta_host>:8000"]`  (hoje `8410:8000`)
- volumes (montagem **e** declaração no fim do arquivo):
  `<slug>_data:/app/data` e `<slug>_uploads:/app/static/uploads`  (hoje `dwa_data`/`dwa_uploads`)

> ⚠️ Renomear os volumes é **obrigatório**: dois projetos com `dwa_data` no mesmo host Docker
> compartilhariam/colidiriam o banco SQLite e os uploads.

**`deploy/Jenkinsfile`** (gera o `backend/.env` de produção no CI):
- `APP_NAME=<nome do projeto>`  (hoje `DefaultWebApp`)
- `BASE_URL=http://localhost:<porta_host>` ou o domínio público https  (hoje `:8410`)
- `RESEND_FROM_EMAIL=noreply@<dominio>`  (hoje `noreply@ifes.site`)
- `RESEND_FROM_NAME="<nome do projeto>"`

A porta **interna** (`PORT=8000`) e o healthcheck (`localhost:8000`) **não mudam**.

---

## 3. Frontend — descartável no fork

O design novo de cada projeto **substitui o frontend atual**. Não há regra fixa de fronteira:
**decida caso a caso quando o design chegar** se a cola-de-contrato (`lib/api.ts`, `types.ts`,
`schemas.ts`, `store/`, gates do `router.tsx`) é mantida ou refeita — depende do stack que o
design trouxer.

- `frontend/src/pages/exemplos/` (8 páginas demo: campos de formulário, grade de cartões, lista/tabela,
  detalhes de produto/serviço/perfil/imóvel) é **demonstração pura** — remova as páginas e suas rotas
  em `router.tsx` ao iniciar o desenvolvimento real.
- Qualquer convenção/documentação sobre o **design visual atual** (incl. `frontend/CONVENTIONS.md`,
  que manda "replicar templates Jinja do WebStandard") é um **default temporário**: ignore e aplique
  o design novo quando ele chegar.

> Não existe `routes/examples_routes.py` no backend — `exemplos` é só frontend. (O hint em
> `configurar_projeto.py` que cita esse arquivo está corrigido.)

---

## 4. Inventário de endpoints (todos sob `/api`)

Todo o **backend é infra reutilizável** (endpoints comuns à maioria dos SaaS) — **nada a remover**
no fork. O trabalho do projeto novo é **ADICIONAR** os endpoints do seu domínio, seguindo o padrão
Routes → DTOs → Repos → SQL (ver `../CLAUDE.md`).

### Comum / reutilizável (mantém em todo projeto)

| Módulo | Endpoints |
|--------|-----------|
| **auth** (`/api`) | `GET /csrf-token`, `GET /me`, `POST /login`, `POST /logout`, `POST /cadastrar`, `POST /esqueci-senha`, `POST /redefinir-senha` |
| **usuario** (`/api/usuario`) | `GET /dashboard`, `GET/PUT /perfil`, `PUT /senha`, `PUT /foto` |
| **notificacoes** (`/api/notificacoes`) | `GET ""`, `GET /nao-lidas`, `PATCH /marcar-todas`, `PATCH /{id}/lida`, `DELETE /lidas`, `DELETE /{id}` |
| **admin · usuarios** (`/api/admin/usuarios`) | `GET ""`, `GET /{id}`, `POST ""`, `PUT /{id}`, `DELETE /{id}` |
| **admin · configuracoes/auditoria** (`/api/admin`) | `GET/PUT /configuracoes`, `GET /auditoria/logs`, `GET /auditoria/registros` |
| **admin · backups** (`/api/admin/backups`) | `GET ""`, `POST ""`, `GET /{nome}/download`, `POST /{nome}/restaurar`, `DELETE /{nome}` |
| **chamados** (`/api/chamados`) | `GET ""`, `POST ""`, `GET /{id}`, `POST /{id}` (interação), `DELETE /{id}` |
| **admin · chamados** (`/api/admin/chamados`) | `GET ""`, `GET /{id}`, `POST /{id}/interacoes` (body dual), `PATCH /{id}/status` |
| **chat** (`/api/chat`) | `GET /stream` (SSE), `POST /salas`, `GET /conversas`, `GET /mensagens/{sala_id}`, `POST /mensagens`, `POST /mensagens/lidas/{sala_id}`, `GET /mensagens/nao-lidas/total`, `GET /usuarios/buscar`, `GET /health` |
| **pagamentos** (`/api/pagamentos`) | `GET ""`, `POST ""` → `{init_point}`, `GET /{id}`, `POST /{id}/paypal/capturar`, `POST /webhook/{mercadopago\|stripe\|paypal}` (isento de CSRF/auth) |
| **infra** | `GET /health` (fora de `/api`) |

> Os módulos de domínio acima (chamados/chat/pagamentos) são **mantidos** por serem padrão de SaaS;
> remova manualmente só se o projeto comprovadamente não usar. Pagamentos: gateway Mercado Pago não
> conecta sem token em produção.

### A implementar (domínio do projeto novo)
Crie novos módulos seguindo o padrão existente: `routes/<dominio>_routes.py` (registrar em
`main.py` ROUTERS), `dtos/<dominio>_dto.py` + `dtos/responses/<dominio>_response.py`,
`repo/<dominio>_repo.py` (registrar em `main.py` TABELAS), `sql/<dominio>_sql.py`. Espelhar os
tipos/Zod no frontend novo. Manter o **contrato de API** descrito em `../CLAUDE.md`.
