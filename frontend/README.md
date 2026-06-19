# WebSPA — Frontend (SPA React)

SPA que consome a **API JSON** do backend FastAPI (ver [`../backend`](../backend)).
Parte da **arquitetura SPLIT** do DefaultWebApp; a referência completa de arquitetura
e do contrato de API está no **[`../CLAUDE.md`](../CLAUDE.md)** (raiz do repositório).

> **Antes de editar páginas, leia [`CONVENTIONS.md`](./CONVENTIONS.md).** A infra (cliente
> HTTP, tipos, stores, componentes, layouts, router) **já existe** — em geral só se
> implementam páginas em `src/pages/**`. Não recrie helpers nem edite a infra sem motivo.

## Stack

- **React 19** + **React Router 7** + **TypeScript** + **Vite 6**
- **Zod** (validação de resposta) + **Zustand** (estado global)
- **Bootstrap 5.3.8** + **bootstrap-icons** (via npm, importados em `main.tsx`)
- **Vitest** + Testing Library (jsdom)

## Comandos

```bash
npm install
npm run dev            # Vite dev server na porta 5180 (proxy /api, /static, /health -> backend)
npm run build          # tsc -b && vite build  (saída em dist/)
npm run preview        # serve o build
npm run test           # vitest run
npm run test:watch     # vitest em watch
npx tsc -b --noEmit    # typecheck isolado
npm run lint           # eslint
```

> **Dev precisa do backend rodando.** O Vite proxia `/api`, `/static` e `/health` para
> `VITE_BACKEND_URL` (fallback `http://127.0.0.1:8400`), mantendo same-origin para que o
> cookie de sessão e o CSRF funcionem sem CORS. Ajuste `VITE_BACKEND_URL` se o backend
> subir em outra porta. Em produção o build de `dist/` é servido pelo próprio FastAPI.

## Estrutura (`src/`)

```
src/
├── main.tsx          # entrypoint; importa Bootstrap + bootstrap-icons
├── router.tsx        # rotas; PublicLayout/PrivateLayout, RootGate, ProtectedRoute, AdminRoute
├── lib/              # api.ts (cliente HTTP), schemas.ts (Zod), types.ts (tipos+enums), format.ts
├── store/            # Zustand: authStore (sessão/usuário), uiStore (toast/confirmação/alerta)
├── hooks/            # useFetch (fetch com estado: data/carregando/erro/recarregar)
├── components/       # chat (ChatWidget SSE), form (Field), layout, routing, ui (Badges, Pagination, ...)
├── pages/            # por domínio: auth, usuario, chamados, pagamentos, notificacoes, admin/*, exemplos, public
├── styles/
└── test/             # setup do Vitest
```

Alias `@` → `src/` (configurado em `vite.config.ts` e `tsconfig.json`).

## Regras essenciais (resumo de CONVENTIONS.md)

- **Cliente HTTP**: `import { api, ApiError } from '@/lib/api'`. Caminhos relativos a `/api`
  (não incluir o prefixo). `credentials:'include'` e header `X-CSRF-Token` são automáticos.
  Erros lançam `ApiError` (`.status`, `.type`, `.message`, `.errors`, `.retryAfter`).
- **Tipos e enums** (`Usuario`, `Chamado`, `PaginaResponse<T>`, `Perfil`, `StatusChamado`, ...):
  importe de `@/lib/types` — não redefina. Devem bater **exato** com os DTOs do backend.
- **Feedback**: `toast.sucesso/erro/aviso/info`, `pedirConfirmacao`, `mostrarAlerta`
  (de `@/store/uiStore`). **NUNCA** `alert()/confirm()/prompt()` nativos.
- **Leitura de dados**: `useFetch` + `<Spinner/>` enquanto carrega + tratar `erro`.
- **Componentes prontos**: Badges, Pagination, EmptyState, Spinner, `form/Field`
  (TextField/TextAreaField/SelectField/SubmitButton). Reutilize, não recrie.

## Documentação Adicional

- **[`CONVENTIONS.md`](./CONVENTIONS.md)** — guia detalhado para implementar páginas (LEIA antes de editar).
- **[`../CLAUDE.md`](../CLAUDE.md)** — arquitetura, contrato de API e convenções do repositório.
