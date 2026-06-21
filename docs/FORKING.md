# FORKING.md — Como criar um projeto novo a partir deste starter kit

Este repositório é um **starter kit**: um boilerplate de SaaS (FastAPI + SPA React) sobre
o qual outros projetos são construídos. Este documento é a **fonte da verdade** sobre o que
muda ao iniciar um projeto novo a partir dele.

A aplicação starter kit roda em **dwa.ifes.site** (porta de host **8410** no VPS). Projetos
novos serão deployados em **outros domínios e outras portas**, com o container e os volumes
renomeados para o projeto.

> As Seções 5–11 foram extraídas comparando o starter kit (`maroquio/DefaultWebApp`) com o
> primeiro projeto real construído a partir dele (**CAVI** — catálogos de imóveis para
> corretores). Elas documentam o trabalho **SaaS-agnóstico** que qualquer fork repete,
> usando o CAVI apenas como exemplo trabalhado.

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

> **Convenção +1 confirmada na prática:** o CAVI publica `8411:8000` (starter publica `8410:8000`).
> Ao escolher a porta de host, ajuste em **DOIS lugares**: `deploy/docker-compose.yml`
> (`ports: ["<porta>:8000"]`) **e** o comentário informativo do `deploy/Jenkinsfile`
> (`o compose publica <porta>:8000`), que duplica o valor e fica enganoso se esquecido.

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
- `backend/data/admin_seed.json`: o admin inicial.

> O configurador cobre só o **dev local**. O deploy (abaixo) é editado à mão.

### 2b. Deploy — edite à mão
**`deploy/docker-compose.yml`**:
- **`name: <slug>` (topo do arquivo) — OBRIGATÓRIO e o mais esquecido.** (hoje `name: dwa`)
- `container_name: <slug>.<dominio>`  (hoje `dwa.ifes.site`)
- `ports: ["<porta_host>:8000"]`  (hoje `8410:8000`)
- volumes (montagem, declaração no fim **e o `name:` físico de cada volume**):
  `<slug>_data:/app/data` e `<slug>_uploads:/app/static/uploads`, com `name: <slug>_data`/`<slug>_uploads`
  na declaração  (hoje `dwa_data`/`dwa_uploads`)

> 🚨 **CORREÇÃO 3 — `name: <slug>` no compose é OBRIGATÓRIO (causa de 502 em massa).**
> Sem o `name:` no topo, o Compose deriva o nome do projeto da **pasta** do arquivo (`deploy/`),
> então **todo fork vira o mesmo projeto `deploy`** no host. Como o `Jenkinsfile` roda
> `docker compose down --remove-orphans` antes do `up`, **cada deploy DERRUBA os containers dos
> outros forks** → 502 Bad Gateway em todos, menos o último deployado. O `name` precisa ser
> **único por projeto** no VPS. Confirmado na prática (06/2026): cavi/girochoffer/lancebet
> colidiam todos no projeto `deploy`; só ficava de pé o último deploy.

> ⚠️ Renomear os volumes é **obrigatório**: dois projetos com `dwa_data` no mesmo host Docker
> compartilhariam/colidiriam o banco SQLite e os uploads. Fixe o `name:` de cada volume (nome
> físico no host) para os dados **não dependerem** do project name — assim renomear o projeto
> nunca cria um volume vazio por engano.

**`deploy/Jenkinsfile`** (gera o `backend/.env` de produção no CI) — define as variáveis abaixo:

| Variável | Valor a definir | Hoje (starter) |
|---|---|---|
| `APP_NAME` | `<nome do projeto>` | `DefaultWebApp` |
| `BASE_URL` | `https://<dominio-publico>` (HTTPS, **sem porta**) | `http://localhost:8410` |
| `RESEND_FROM_EMAIL` | `<slug>@ifes.site` (ou endereço do seu domínio verificado) | `noreply@ifes.site` |
| `RESEND_FROM_NAME` | `"<nome do projeto>"` | `"Default Web App"` |

A porta **interna** (`PORT=8000`) e o healthcheck (`localhost:8000`) **não mudam**.

> ⚠️ **CORREÇÃO 1 — `BASE_URL` de produção é o domínio público HTTPS, não `localhost`.**
> `BASE_URL` alimenta os links dos e-mails (redefinição de senha, CTA de boas-vindas) e as
> `back_urls`/webhooks dos gateways de pagamento. Se ficar em `localhost`, todo link enviado ao
> usuário aponta para um endereço inacessível. Use `https://<dominio-publico>` (sem porta).
> O CAVI usa `BASE_URL=https://cavi.ifes.site`. `localhost:porta` só serve para o `.env` de dev.

> ⚠️ **CORREÇÃO 2 — `RESEND_FROM_EMAIL` na prática usa `<slug>@ifes.site`, não `noreply@<dominio>`.**
> A prática real abandonou o prefixo `noreply@` e usa `<slug>@ifes.site` (domínio compartilhado e
> verificado no Resend). O CAVI usa `cavi@ifes.site`. **Antes de escolher o remetente, confirme
> qual domínio está verificado no Resend** (ver Seção 6).

**Segredos via credenciais do Jenkins (não regrida):** `SECRET_KEY` e `RESEND_API_KEY` (e tokens de
pagamento, se usar) são injetados como `${VAR}` interpolado de credenciais do Jenkins — **nunca**
hardcodados. Cadastre no Jenkins as credenciais com os mesmos `credentialsId` já referenciados, e
confirme que `backend/.env` continua no `.gitignore`. A `SECRET_KEY` de **dev** é gerada pelo
`configurar_projeto.py`.

> O `configurar_projeto.py` **não toca** em `BASE_URL` nem em nada do `deploy/`. Toda a tabela acima
> é edição **manual** no Jenkinsfile.

---

## 3. Frontend — descartável no fork, com infra a preservar

O design novo de cada projeto **substitui o frontend atual**. Não há regra fixa de fronteira:
**decida caso a caso quando o design chegar** se a cola-de-contrato (`lib/api.ts`, `types.ts`,
`schemas.ts`, `store/`, gates do `router.tsx`) é mantida ou refeita — depende do stack que o
design trouxer.

- `frontend/src/pages/exemplos/` (8 páginas demo) é **demonstração pura** — remova as páginas e suas
  rotas em `router.tsx` ao iniciar o desenvolvimento real.
- Qualquer convenção/documentação sobre o **design visual atual** (incl. `frontend/CONVENTIONS.md`)
  é um **default temporário**: ignore e aplique o design novo quando ele chegar.

> Não existe `routes/examples_routes.py` no backend — `exemplos` é só frontend.

> **Além de remover `exemplos`:** o CAVI também **deletou** do disco e do router os módulos de
> frontend não usados (`chamados`, `pagamentos`, `notificacoes`, `usuario`). Decida quais módulos do
> starter seu domínio usa e remova o resto para manter bundle/router enxutos. Use os exemplos como
> referência de UI **antes** de deletar.

### 3.1. `lib/api.ts` é infra **congelada** — NUNCA reescrever
O `git diff` do CAVI em `frontend/src/lib/api.ts` é **vazio**: todas as features de domínio passaram
por ele sem tocá-lo. Não altere `api.ts` ao adicionar features — toda chamada de domínio usa o cliente
central (`api.get/post/put/delete`, caminhos relativos a `/api`, **sem** o prefixo). Só altere se mudar
o contrato de erro/CSRF do backend (raro).

### 3.2. `authStore` — única edição é o conjunto de perfis
`authStore.ts` mudou só 2 linhas no CAVI (adição de `isCorretor()`). Padrão: **um helper `isX()` por
perfil + um Route guard que o lê**.
1. Redefina `Perfil` em `types.ts` (bate EXATO com `backend/util/perfis.py`).
2. Para cada perfil com área protegida, adicione `isX()` no `authStore` espelhando `isAdmin()`.
3. Crie `components/routing/XRoute.tsx` (copie `AdminRoute`: `!usuario → /login`; `!isX → fallback`).
   O `ProtectedRoute` genérico foi **removido** no CAVI em favor de guards por-perfil.

### 3.3. Router reestruturado por ÁREA (subtrees com layout + guard)
O starter usa `PublicLayout`/`PrivateLayout` para tudo. Padrão recomendado: **subtrees por área**.
Esqueleto: `{ path: '/prefixo', element: <XLayout/>, children: [{ index: true, ... }, { path: 'sub', ... }] }`
com children em paths **relativos**. No CAVI: `RootGate` raiz (com `errorElement={<RouteError/>}`) →
rotas auth/institucionais planas + 3 subtrees: `/v/:slug` (`SiteLayout`, catálogo público),
`/app` (`CorretorRoute > BrokerLayout`), `/admin` (`AdminRoute > AdminLayout`). Cada área tem
`components/layout/XLayout.tsx`, guard quando protegida e `index: true` na rota raiz da área.

### 3.4. `RootGate` é host global de overlays + spinner de boot tematizado
Monte os portais de feedback (`Toasts`, `AlertModal`, `ConfirmModal` de `components/ui`) **uma vez**,
irmãos do `<Outlet/>` dentro do `RootGate` — nunca por página. O `RootGate` também faz `carregarSessao()`
no boot. Ao trocar o tema, ajuste o spinner de boot para usar seus tokens (`colors.*`); o keyframe
`cavi-spin` vive em `src/styles/custom.css`.

### 3.5. `masks.ts` — util agnóstico de máscaras de input (reaproveitar inteiro)
`frontend/src/lib/masks.ts` (novo, ~50 linhas) é 100% agnóstico (CPF/telefone/moeda BR). **Reaproveite
inteiro.** Funções: `apenasDigitos`, `mascararCpf`, `mascararTelefone`, `mascararMoeda`,
`formatarNumeroComoMoedaInput`, `moedaParaNumero` (usa `Intl.NumberFormat` pt-BR).
- Separe responsabilidades: **`masks.ts` = entrada** (máscara enquanto digita); **`format.ts` = saída**
  (exibição: `formatarData/DataHora/Hora/Moeda/Bytes`).
- Em campos controlados: `onChange` aplica `mascararX`; `moedaParaNumero`/`apenasDigitos` ao montar o DTO.
- Helpers genéricos novos (ex.: `urlMidia`, `linkWhatsApp`) vão em `format.ts`; deixe os de domínio
  claramente comentados.

---

## 4. Inventário de endpoints (todos sob `/api`)

Todo o **backend é infra reutilizável** (endpoints comuns à maioria dos SaaS) — **nada a remover**
no fork. O trabalho do projeto novo é **ADICIONAR** os endpoints do seu domínio, seguindo o padrão
Routes → DTOs → Repos → SQL (ver `../CLAUDE.md` e a **Seção 9** abaixo).

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
Crie novos módulos seguindo o padrão existente. A **Seção 9** documenta a anatomia completa com
exemplo trabalhado (`conta_site_*.py` para entidade simples, `imovel_*.py` para entidade composta).

---

## 5. Identidade e branding

Tudo que muda a marca visível (aba, favicon, fontes, design system, assets, nome do produto).

### 5a. Shell HTML (`frontend/index.html`) — **obrigatório**
Primeiro ponto de marca visível no navegador. Edite:

| O quê | Onde | Starter | CAVI (exemplo) |
|---|---|---|---|
| Título da aba | `<title>` | `Sistema Web` | `CAVI :: Catálogos de Imóveis` |
| Favicon | `<link rel="icon">` | ausente | `<link rel="icon" type="image/svg+xml" href="/assets/logo-icon-orange.svg">` |
| Fontes | `<link>`/`preconnect` Google Fonts | ausentes | Jost + Hanken Grotesk |
| Classes do `<body>` | atributo `class` | utilitários Bootstrap (`d-flex flex-column min-vh-100`) | sem classes (limpo) |

> ⚠️ **Armadilha do nome do produto:** apesar de existir `APP_NAME=SeuProjeto` em
> `backend/.env.example` (linha 7), o nome textual da aba está **hardcoded** em `index.html`, **não**
> vem da env. Decida a estratégia: (a) consumir `APP_NAME`, ou (b) hardcodar como o CAVI fez. De
> qualquer modo, atualize `APP_NAME` no `.env.example` para o nome real (ele é usado nos e-mails —
> ver Seção 6) e faça `grep` por `"Sistema Web"` e `"SeuProjeto"` para não deixar placeholders.

### 5b. Módulo de tokens visuais — `frontend/src/lib/theme.ts` (**novo, recomendado**)
Fonte única tipada de cores e fontes, evitando hex espalhados. Não existe no starter.
- Exporta `const colors {bg, ink, orange, ...} as const`, `const fonts {display:'Jost', body:'Hanken Grotesk'}`
  e `type ColorToken`.
- Consumido por ~30 arquivos via `import { colors, fonts } from '@/lib/theme'`, aplicados em `style` inline.
- **Trocar os valores aqui propaga para toda a UI.** Mantenha os tokens `as const` para preservar `ColorToken`.

### 5c. Remover o design system Bootstrap (**obrigatório** se quiser identidade própria)
A decisão mais estrutural de branding. **4 pontos de remoção** (úteis de conhecer mesmo se mantiver
Bootstrap — é onde ele é plugado):
1. `frontend/package.json`: remover `"bootstrap"` e `"bootstrap-icons"` das `dependencies` e rodar `bun install`.
2. `frontend/src/main.tsx`: apagar os 3 imports de Bootstrap (CSS, ícones e `bootstrap.bundle.min.js`).
   No CAVI, `main.tsx` só importa `./styles/custom.css`.
3. `frontend/src/styles/custom.css`: reescrever como reset/base próprio (no starter é construído sobre
   variáveis Bootstrap `--primary-color:#0d6efd`). **Alternativa:** manter Bootstrap e só trocar `:root`.
4. **O gerenciador de pacotes é o `bun`** (lockfile `frontend/bun.lock` versionado, **não** há npm). Use `bun install`.

### 5d. Assets de marca — `frontend/public/assets/` (**obrigatório**)
O starter **não tem** `frontend/public/`. Crie `frontend/public/assets/` e coloque logos/favicon.
- Sugestão de nomenclatura do CAVI: `logo-icon-<cor>.svg` e `logo-name-<cor>.svg` (variantes black/cream/orange/white).
- Referencie por caminho absoluto `/assets/...` no `index.html` (favicon) e nos componentes (`<img src="/assets/...">`).
- Faça `grep` por `/assets/logo` e troque pelos seus nomes.

### 5e. Diretório `design/` como bundle de referência (**opcional**)
Workflow de handoff visual. Existe só no CAVI. Contém protótipos HTML/CSS/JS, assets, um app React de
referência (`design/cavi-react/`) e spec de domínio. **Não é runtime** (não buildado, não servido);
`theme.ts` e `custom.css` foram **portados** dele. Considere `.gitignore` se não quiser carregar o peso no repo.

---

## 6. Serviço de e-mail (`backend/util/email_service.py` + Resend)

### 6a. Provisionamento no Resend (pré-requisito de infra, nenhum código resolve sozinho)
1. Crie conta no `resend.com` e gere a API key → `RESEND_API_KEY`.
2. **Verifique seu domínio** no painel do Resend e publique os registros DNS (SPF/DKIM/DMARC).
3. Aponte `RESEND_FROM_EMAIL` para `@dominio-verificado` e `RESEND_FROM_NAME` para o nome do produto.

> Sem domínio verificado os e-mails caem em spam ou são recusados. **Degradação graciosa:** sem
> `RESEND_API_KEY`, `enviar_email` loga warning e retorna `False` — cadastro/recuperação **não quebram**.

### 6b. Nome do produto via `APP_NAME` (não literais "Sistema")
O CAVI passou a ler `self.app_name = os.getenv('APP_NAME', self.from_name)` e interpola em assuntos,
títulos e rodapés (ex.: `f'Bem-vindo ao {self.app_name}'`). Defina `APP_NAME` no `backend/.env`
(fallback: `RESEND_FROM_NAME`) e não deixe textos genéricos como "Bem-vindo ao Sistema".

### 6c. `BASE_URL` é a origem dos links clicáveis nos e-mails
Os links de ação (redefinir senha; CTA "Acessar o app" no e-mail de boas-vindas) são montados a partir
de `os.getenv('BASE_URL', 'http://localhost:8000')`. Em produção, aponte para a URL pública HTTPS (ver
Correção 1 na Seção 2b). ⚠️ Note a divergência de fallback: o código usa `localhost:8000`, mas o `.env`
de dev usa `8400` — em dev confie sempre no `.env`.

### 6d. Multipart text+html é obrigatório em todo e-mail transacional
E-mail só-HTML pontua mais alto como spam. O CAVI injeta `params['text']` quando `texto` é fornecido.
> **Atenção (não há derivação automática):** **não** existe geração automática de texto a partir do
> HTML. Cada método monta a string `texto=` à mão. **Métodos novos que esquecerem `texto=` voltam a
> ser só-HTML.** Sempre passe `texto=` com um corpo plaintext equivalente. Use
> `enviar_recuperacao_senha`/`enviar_boas_vindas` como modelo.

### 6e. Template HTML com CSS inline + rodapé de compliance
Clientes de e-mail não suportam `<style>`/CSS externo de forma confiável. Padrão estabelecido (siga ao
criar novos e-mails):
- CSS sempre **inline** (`style=` em cada tag, nunca `<style>`).
- Botão CTA estilizado inline + **link copiável de fallback** ("Ou copie e cole este endereço").
- Rodapé padrão (`<hr>` + `<p style="font-size:12px;color:#888">`) explicando **por que** o usuário
  recebeu o e-mail + aviso "e-mail automático, não responda" (anti-spam / LGPD).
- Considere extrair cabeçalho/rodapé para um helper de template em vez de repetir em cada método.

---

## 7. Perfis, autenticação e cadastro

O enum `Perfil` é a fonte única da verdade (CLAUDE.md: "NUNCA strings literais").

### 7a. Customizar o enum `Perfil` e propagar em TODOS os pontos acoplados (**obrigatório**)
O starter entrega `ADMIN + Cliente + Vendedor` (placeholders); o CAVI reduziu para `ADMIN + CORRETOR`. Ao trocar:
1. `backend/util/perfis.py`: mantenha `ADMIN`, troque os exemplos pelos seus papéis.
2. `backend/model/usuario_logado_model.py`: recrie os helpers `is_<perfil>()`. `is_admin()` e
   `tem_perfil(*perfis)` são agnósticos e **não mudam**. Para rotas multi-perfil, prefira `tem_perfil(...)`.
3. **Espelho exato no frontend:** `frontend/src/lib/types.ts` (`const Perfil`) e
   `frontend/src/lib/schemas.ts` (`perfilAdminSchema = z.enum([Perfil.ADMIN, Perfil.CORRETOR])`).
4. `grep -rn 'Perfil\.\(CLIENTE\|VENDEDOR\)'` e por literais `'Cliente'`/`'Vendedor'` em **todo** o
   repo (back + front) e elimine referências mortas (ver Seção 11 sobre o efeito nos testes).

### 7b. Estado de conta/recurso — enum `StatusConta` para gating de visibilidade (padrão reutilizável)
O starter **não tem** estado de conta. O CAVI introduziu `backend/util/status_conta.py`
(`StatusConta(EnumEntidade)` com `ATIVO`/`INATIVO`).
- Herde de `EnumEntidade` (`util/enum_base.py`) → ganha `valores()`/`existe()`/`from_valor()`/`validar()` de graça.
- Use no model, no repo (filtros SQL), nas rotas públicas (esconder `INATIVO`) e admin (alternar).
- Espelhe a `const StatusConta` em `frontend/src/lib/types.ts`. **Nunca** grave strings literais de status.

### 7c. Auto-cadastro com perfil FIXO no servidor (anti-escalada de privilégio) (**obrigatório**)
O `CadastroDTO` do starter aceita `perfil` vindo do cliente — um anônimo poderia se registrar com
qualquer perfil não-admin. Endurecimento do CAVI:
- **NUNCA** aceite `perfil` do DTO no auto-cadastro público. Fixe `Perfil.<SEU_PERFIL_PADRAO>.value` no
  servidor (CAVI: `Usuario(..., perfil=Perfil.CORRETOR.value)`).
- Mantenha a escolha de perfil **apenas** em rotas admin (`perfilAdminSchema`).
- Para aprovação manual, combine com `StatusConta` inicial "Pendente" + gate no login.

### 7d. Cadastro composto multi-entidade com slug único e rollback manual
Padrão de signup que cria `Usuario` + recurso vinculado (workspace/tenant/loja/perfil público) num
único passo. Sem ORM, não há transação automática. Exemplo: `auth_routes.py` → `/cadastrar-corretor`:
1. DTO composto (`CadastroCorretorDTO`) agrupa campos das duas entidades.
2. `_gerar_slug_unico()` deriva slug com `gerar_slug()` e desambigua com sufixo `-2`/`-3` checando o repo.
3. Insere `Usuario`, depois `ContaSite`.
4. **Rollback compensatório:** se a segunda inserção falha, chama `usuario_repo.excluir(usuario_id)`.
5. Espelhe no frontend com `cadastroXSchema` em `schemas.ts`.

> Não confie em integridade automática do SQLite — a compensação é manual.

### 7e. Estender o model `Usuario` com campos de identidade (Optional, retrocompatível)
CPF/telefone/documento etc. Padrão: adicionar campos `Optional[...] = None` para não quebrar criações
existentes (admin seed, fluxos legados). CAVI: `+ cpf`, `+ telefone` em `usuario_model.py`.
- Reflita as colunas no `usuario_repo` (`CREATE TABLE` / `INSERT` / mapeamento).
- **Reaproveite os validators já prontos** em `backend/dtos/validators.py` (`validar_cpf`,
  `validar_telefone_br`, `validar_string_obrigatoria`) — já existiam no starter. Levantam `ValueError` → 422.

---

## 8. Segurança / CSP / headers (`backend/util/security_headers.py`)

### 8a. Estender a CSP para embeds/recursos de terceiros (**ao integrar qualquer terceiro**)
A CSP do starter é restritiva (`default-src 'self'`) e **não declara `frame-src`** — qualquer iframe de
terceiro (mapas, vídeo, checkout de pagamento, chat, captcha) é **silenciosamente bloqueado** em
produção (o dev server Vite pode mascarar). O CAVI adicionou `frame-src 'self' https://www.google.com https://maps.google.com`.

| Recurso de terceiro | Diretiva CSP a estender |
|---|---|
| iframes (mapas, vídeo, checkout) | `frame-src` |
| SDKs / JS externos | `script-src` |
| chamadas de rede (fetch/XHR/WebSocket/SSE) ao provedor | `connect-src` |
| imagens | `img-src` |
| fontes | `font-src` |

Regras: (1) sempre origin completo `https://dominio.com`, **nunca** `https:` genérico; (2) mantenha
`'self'` como primeiro valor; (3) não introduza `'unsafe-inline'`/`'unsafe-eval'` sem necessidade
comprovada; (4) **teste no build de produção**; (5) no console procure `Refused to ... Content Security
Policy directive` para descobrir o que falta. Comente cada origin explicando **qual feature** o exige.

### 8b. Não confundir "ser embutido" com "embutir terceiros"
- **EMBUTIR terceiros no seu site** (mapas/vídeo/payment) → altere `frame-src` (8a).
- **Permitir que SEU site seja embutido** por um parceiro → altere `frame-ancestors` (CSP) e `X-Frame-Options`.

`X-Frame-Options: DENY` + `frame-ancestors 'none'` são **anti-clickjacking** — o CAVI os manteve intactos
e mexeu **só** em `frame-src`, decisão correta. Só relaxe `frame-ancestors`/`X-Frame-Options` (por origin
específico) se um parceiro precisar embutir seu site.

### 8c. `Permissions-Policy` libera o USO de capacidades do navegador
O starter nega `geolocation`/`microphone`/`camera`/`payment`/`usb`/etc. (`=()` = bloqueados). **CSP
libera o carregamento; Permissions-Policy libera o uso** — frequentemente você ajusta **ambos**.
- Liberar só o próprio site: `geolocation=(self)`.
- Liberar também um iframe de terceiro: `payment=(self "https://checkout.stripe.com")`.
- Menor privilégio: libere o mínimo, deixe o resto em `=()`.

---

## 9. Padrão de módulo de domínio (exemplo trabalhado)

Templates de referência: `conta_site_*.py` (entidade simples 1:1) e `imovel_*.py` (entidade composta com agregados).

### 9a. Anatomia: 6 arquivos em camadas
| Camada | Arquivo | Conteúdo |
|---|---|---|
| Model | `model/X_model.py` | `@dataclass` + enums herdando `EnumEntidade` (`util/enum_base.py`) |
| SQL | `sql/X_sql.py` | constantes string com SQL puro e placeholders `?` (`CRIAR_TABELA`, `INSERIR`, `ATUALIZAR`, `OBTER_*`, `EXCLUIR`) |
| Repo | `repo/X_repo.py` | `criar_tabela()` + CRUD usando `obter_conexao()` (`util/db_util`) e `agora()` (`util/datetime_util`), com helper `_row_to_X(row)` |
| DTO entrada | `dtos/X_dto.py` | Pydantic com `field_validator`/`model_validator`, reusando `dtos/validators.py` |
| DTO saída | `dtos/responses/X_response.py` | `BaseModel` com `@classmethod de_X(entidade)` mapeando model→response |
| Routes | `routes/X_routes.py` | `APIRouter(prefix='/x')` **SEM** o prefixo `/api` (o `main.py` aplica) |

SQL puro com prepared statements, **NUNCA ORM**. (Referência de tamanho: `imovel_repo.py` ~419 linhas,
`imoveis_routes.py` ~547 linhas.)

### 9b. Fiação (wiring) em `main.py` — 4 pontos, ordem de FK importa
1. `from repo import X_repo`.
2. `from routes.X_routes import router as X_router`.
3. Entrada `(X_repo, 'x')` na lista **`TABELAS`** — **respeitando a ordem de FK** (tabelas referenciadas
   primeiro; no CAVI `conta_site_repo` vem **antes** de `imovel_repo` porque imóvel referencia conta).
4. Entrada `(X_router, ['Tag'], 'descrição')` na lista **`ROUTERS`** (montada sob `API_PREFIX='/api'`).

> Se um repo cria várias tabelas (ex.: `imovel_repo.criar_tabela()` cria imóvel/endereço/foto em ordem),
> registre o repo **uma única vez**.

### 9c. Três anéis de exposição de rota
| Anel | Decorator | Padrão |
|---|---|---|
| Público | **sem** `@requer_autenticacao` | somente GET, filtra registros publicáveis (status Ativo/Publicado). Ver `publico_routes.py` (`prefix='/publico'`) |
| Autenticado (dono) | `@requer_autenticacao()` | **sempre escope ao dono** via helper que resolve a entidade-raiz e valida posse. Ver `_obter_conta_do_usuario`/`_obter_imovel_da_conta` em `imoveis_routes.py` |
| Admin | `@requer_autenticacao([Perfil.ADMIN.value])` | usa o enum, **nunca** string literal. Ver `admin_corretores_routes.py` |

Todos os handlers chamam `checar_rate_limit(limiter, request)` de `util.api_helpers`.

### 9d. Submodelos agregados (1:1 e 1:N) num único repo dono
Padrão sem ORM (ex.: `imovel` + `endereco_imovel` 1:1 + `foto_imovel` 1:N):
- No dataclass raiz: `Optional[Filho]` para 1:1; `list[Filho] = field(default_factory=list)` para 1:N.
- Carregue os filhos **só** em `obter_detalhe()`; listagens deixam vazios por performance.
- `FOREIGN KEY ... ON DELETE CASCADE` no SQL dos filhos.
- `criar_tabela()` do repo raiz executa os `CREATE TABLE` na ordem pai→filho e é registrado **uma vez** em `TABELAS`.
- **Upsert dos filhos** dentro do `inserir`/`atualizar` do pai, na mesma conexão.
- Uploads de arquivo vão para `static/uploads/<modulo>/` (ex.: `static/uploads/imoveis`).

### 9e. Mapeamento isolado em helpers + conversão segura de enum
- Repo: `_row_to_X(row: sqlite3.Row) -> X`. Para colunas de JOIN opcional, cheque `if coluna in row.keys()`.
- Enums vindos do banco: conversor seguro estilo `_converter_status_seguro` —
  `try Enum(valor) except ValueError: logger.error(...); return DEFAULT`. **Nunca** deixe propagar.
- Response: `@classmethod de_X(entidade)` chamando `enum.value`.
- Crie **variantes de response por anel:** completa (dono/admin, com email/datas internas) e
  resumida/segura (público). Ver `ContaSiteResponse` vs `ContaSiteResumoResponse`.

### 9f. Espelhamento end-to-end no frontend
1. `lib/types.ts`: enums como objeto `const` + `export type XValor`; interfaces de Response com comentário
   `// Espelha backend/dtos/responses/<arquivo>.py`. Valores dos enums batem **EXATO** (incluindo acentos).
2. `lib/schemas.ts`: importe esses enums e construa `z.enum([Enum.A, Enum.B])` — **nunca** redeclare
   strings literais; exporte `export type XForm = z.infer<typeof xSchema>`.
3. Anel novo: atualize `Perfil` const, adicione `isX()` no `authStore` e crie
   `components/routing/XRoute.tsx` (copie `CorretorRoute.tsx`).
4. Organize páginas em `pages/<anel>/`.

---

## 10. Seed de dados (`backend/util/seed_data.py`)

### 10a. Admin vs dados de domínio — onde trocar cada coisa
- **Admin inicial:** trocar **somente** em `backend/data/admin_seed.json`
  (`{"usuarios":[{nome,email,senha,perfil:"Administrador"}]}`). O ideal é rodar
  `scripts/configurar_projeto.py`, que reescreve esse arquivo. **NÃO** edite o admin dentro de `seed_data.py`.
- **Usuários/dados de demo do domínio:** vão no **bloco de código** (constante tipo `CORRETORES_DEMO`),
  **nunca** no JSON.

> O rename `usuarios_seed.json → admin_seed.json` é infra do starter (commit `d13c99f`); o starter
> pristino já tem `admin_seed.json`.

### 10b. Padrão de seed de domínio
1. No topo de `seed_data.py`, importe seus models/repos/enums de domínio.
2. Declare uma constante `MEUS_DADOS_DEMO: list[dict]` com a árvore de entidades (raiz → filhas aninhadas).
3. Escreva `def carregar_<dominio>_demo()` que itera a constante e insere **via os repos** (que aplicam
   `agora()` nas datas) — **nunca** SQL direto no seed.
4. Registre a chamada em `inicializar_dados()` **após** `carregar_usuarios_seed()`.
5. Apenas **ACRESCENTE** — não reescreva as funções de admin/usuário.

### 10c. Idempotência (seed roda a cada boot)
`inicializar_dados()` roda no startup. Toda função de seed de domínio **DEVE** começar com guarda:
- **Guarda de tabela vazia:** `if <repo_raiz>.obter_todos(): logger.info(...); return`.
- **Reaproveitamento por chave natural:** para entidades que outro seed pode ter criado (ex.: usuário),
  busque por `obter_por_email`/`obter_por_slug` e reaproveite o id existente antes de inserir.

### 10d. Senha-padrão demo em constante documentada
Defina **uma** constante `SENHA_PADRAO_SEED` no topo de `seed_data.py` (CAVI: `"1234aA@#"`), documentada
para QA, e **sempre** armazene via `criar_hash_senha()` (bcrypt). Nunca grave senha em texto puro.

### 10e. ⚠️ Gating por ambiente — decisão consciente antes do 1º deploy
`inicializar_dados()` roda **incondicionalmente** em dev **e** prod. **O CAVI não implementou gating** —
dados de demo entrariam em produção na primeira subida com banco vazio.
- Se seu seed de domínio for DEMO (só dev/QA), proteja a chamada por flag de ambiente
  (ex.: `SEED_DEMO=true` ou `APP_ENV=development`).
- Mantenha `carregar_usuarios_seed` (admin) **sempre** ativo.
- Decida isso conscientemente **antes** do primeiro deploy.

---

## 11. Testes — o que quebra ao customizar e os buracos a não herdar

### 11a. Trocar perfis quebra a suíte inteira na **coleta** (substituição mecânica)
`Perfil.CLIENTE.value`/`Perfil.VENDEDOR.value` estão espalhados por conftests e ~23 arquivos de teste.
Removê-los do enum gera `AttributeError` no import → derruba a coleta do pytest antes de rodar qualquer teste.
- Logo após editar `util/perfis.py`, rode `grep -rn 'Perfil\.\(CLIENTE\|VENDEDOR\)' backend/tests` e
  substitua **toda** ocorrência **antes** de rodar a suíte.
- Mapeie: (a) perfil "default não-admin" do starter (CLIENTE) → seu perfil de usuário comum; (b) onde o
  teste precisa de um **segundo** perfil distinto → outro valor real do seu enum (ou `ADMIN` se só tiver dois).
- Fixtures afetadas: `tests/conftest.py` (`usuario_teste`, `criar_usuario`, `vendedor_teste`,
  `vendedor_autenticado`, `dois_usuarios`, `criar_usuario_direto`); `tests/integration/repos/conftest.py`;
  `tests/integration/routes/conftest.py`.
- Teste de fumaça: `pytest --collect-only` — se quebrar no import, ainda há literal de perfil órfão.

### 11b. Literais de string de perfil quebram **silenciosamente** em runtime
Asserts como `assert usuario.perfil == 'Cliente'` **não** quebram na coleta mas falham em runtime.
Rode também `grep -rni "'cliente'\|'vendedor'" backend/tests` para pegar literais soltos em mocks/asserts.
Idealmente padronize para `Perfil.X.value`.

### 11c. Fixtures legadas: manter o NOME, trocar a semântica
Ao remover um perfil que dá nome a uma fixture (`vendedor_teste`), **mantenha o nome** e troque só o
conteúdo + atualize a docstring ("nome de fixture legado"). O CAVI fez `vendedor_*` virar "segundo
corretor" sem renomear — evita rename em cascata por dezenas de consumidores.

### 11d. `is_<perfil>()` e seus testes reescritos 1:1
`model/usuario_logado_model.py`: para cada perfil, um `is_<perfil>()`; em
`tests/unit/test_usuario_logado_model.py`, uma classe `TestIs<Perfil>` com caso positivo + negativo cruzado.
> ⚠️ **Buraco do CAVI a não repetir:** `is_corretor()` foi adicionado **sem nenhum teste**. Não deixe o
> helper novo sem cobertura.

### 11e. Liberar origens externas no CSP → atualizar testes em DOIS lugares
Liberar qualquer origem (mapas, Stripe/MP, fonts) muda o CSP e quebra os asserts de segurança. Atualize **ambos**:
- `tests/integration/utils/test_security_headers.py`
- `tests/integration/routes/test_security_routes.py` (`test_csp_restringe_origens`)

### 11f. Asserts de branding parametrizados por config, não por string fixa
Conteúdo de e-mail carrega `app_name`. Compare contra a config/serviço, não contra literal:
- CAVI: `assert ... == f'Bem-vindo ao {servico.app_name}'` (antes era `== 'Bem-vindo ao Sistema'`).

### 11g. Renomear o arquivo de seed → atualizar o nome hardcoded no teste
`tests/integration/utils/test_seed_data.py` cria o arquivo de seed por nome em `tmp_path`. Se
renomear/mover o seed de admin, atualize o nome hardcoded e mantenha teste e produção apontando para o mesmo nome.

### 11h. Módulo de domínio novo → teste em TRÊS níveis (buraco do CAVI)
> ⚠️ O CAVI adicionou `imovel`/`conta_site`/`publico` mas criou **só 1** teste unitário de DTO
> (`tests/unit/test_publico_response.py`) — **sem** teste de repo nem de rota. Não herde esse gap.

Ao adicionar um módulo end-to-end, espelhe o padrão do core:
1. **Unit do Response DTO / factory** em `tests/unit/` — instancie o model, chame `de_<entidade>`, asserte
   os campos do contrato (incluindo agregados/derivados).
2. **Integration do repo** em `tests/integration/repos/test_<modulo>_repo.py`, reaproveitando
   `usuario_repo_teste` do conftest local.
3. **Integration das rotas** em `tests/integration/routes/test_<modulo>_routes.py`, usando
   `admin_autenticado`/`criar_usuario_direto` e o fluxo CSRF (`_csrf(client)`). Reaproveite factories de payload.

### 11i. Seed de domínio sem teste de idempotência (buraco do CAVI)
> ⚠️ `carregar_corretores_demo` (300+ linhas) ficou sem teste. Ao adicionar `carregar_<dominio>_demo()`,
> espelhe `test_seed_data.py`: rode a função **duas vezes** e verifique que a segunda execução **não
> duplica** (graças à guarda de tabela vazia) e que as contagens batem com a constante de dados.
