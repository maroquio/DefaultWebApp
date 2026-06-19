# Convenções do Frontend (LEIA ANTES DE EDITAR QUALQUER PÁGINA)

Stack: **React 19 + React Router 7 + Zod + Zustand + TypeScript + Vite**, estilo
**Bootstrap 5.3.8 + Bootstrap Icons** (empacotados via npm, já importados em `main.tsx`).
Visual deve replicar os templates Jinja do `WebStandard`.

A infraestrutura (api, tipos, stores, componentes, layouts, router) **já existe**.
Você só implementa páginas em `src/pages/**`. **NÃO** edite o router, os layouts nem a
infra, salvo instrução explícita. Use SEMPRE o que já existe — não recrie helpers.

## Cliente HTTP — `src/lib/api.ts`

```ts
import { api, ApiError } from '@/lib/api' // (ou caminho relativo)
const usuario = await api.get<Usuario>('/usuario/perfil')
await api.post<Chamado>('/chamados', { titulo, descricao, prioridade })
await api.put<Usuario>('/usuario/perfil', { nome, email })
await api.patch('/notificacoes/marcar-todas')
await api.delete(`/chamados/${id}`)
```

- Caminhos são **relativos a `/api`** (não inclua o prefixo `/api`).
- `credentials: include` e header **`X-CSRF-Token`** são automáticos. Não se preocupe com CSRF.
- Query string: `api.get('/chamados', { params: { pagina, q } })`.
- Erros lançam `ApiError` com `.status`, `.type`, `.message` (detail), `.errors` (por campo),
  `.retryAfter`. Para erro de validação (422): `err.errors?.campo?.[0]` ou `err.campo('campo')`.

## Tipos — `src/lib/types.ts`

Todos os shapes de resposta já estão lá: `Usuario`, `Chamado`, `ChamadoInteracao`,
`Notificacao`, `Pagamento`, `PaginaResponse<T>`, `BackupInfo`, `AuditoriaRegistro`,
`ConfigLista`, `Conversa`, `ChatMensagem`, etc. Enums como objetos const:
`Perfil`, `StatusChamado`, `PrioridadeChamado`, `StatusPagamento`. **Importe daqui**, não redefina.

## Estado global — `src/store/`

```ts
import { useAuthStore } from '@/store/authStore'
const usuario = useAuthStore((s) => s.usuario)        // Usuario | null
const isAdmin = useAuthStore((s) => s.isAdmin())
const setUsuario = useAuthStore((s) => s.setUsuario)  // após editar perfil/foto

import { toast, useUIStore } from '@/store/uiStore'
toast.sucesso('Salvo!'); toast.erro('Falhou'); toast.info('...'); toast.aviso('...')
const pedirConfirmacao = useUIStore((s) => s.pedirConfirmacao)
const mostrarAlerta = useUIStore((s) => s.mostrarAlerta)
```

## Feedback ao usuário (REGRAS)

- **NUNCA** use `alert()`, `confirm()`, `prompt()` nativos.
- Notificações rápidas → `toast.sucesso/erro/aviso/info(msg)`.
- Confirmação de ação destrutiva → `pedirConfirmacao({ mensagem, tipo:'danger', onConfirmar })`.
- Aviso modal → `mostrarAlerta({ mensagem, tipo })`.

## Componentes prontos — `src/components/`

- `ui/Badges.tsx`: `<StatusChamadoBadge status/>`, `<PrioridadeBadge prioridade/>`,
  `<PerfilBadge perfil/>`, `<StatusPagamentoBadge status/>`, `<MensagensNaoLidasBadge count/>`, `<Badge texto cor icon/>`.
- `ui/Pagination.tsx` (default): `<Pagination pagina totalPaginas onPagina={(p)=>...} />`.
- `ui/EmptyState.tsx` (default): `<EmptyState icon titulo mensagem>{children}</EmptyState>`.
- `ui/Spinner.tsx` (default): `<Spinner texto?/>`.
- `form/Field.tsx`: `TextField`, `TextAreaField`, `SelectField`, `SubmitButton` (named exports).
  Campos controlados: `<TextField label name value onChange={(v)=>...} erro={err.campo('x')} obrigatorio />`.

## Leitura de dados — `src/hooks/useFetch.ts`

```ts
import { useFetch } from '@/hooks/useFetch'
const { data, carregando, erro, recarregar } = useFetch<PaginaResponse<Chamado>>(
  (signal) => api.get('/chamados', { params: { pagina }, signal }),
  [pagina],
)
```
Renderize `<Spinner/>` quando `carregando`, trate `erro`, depois use `data`.

## Formatação — `src/lib/format.ts`

`formatarData`, `formatarDataHora`, `formatarHora`, `formatarMoeda`, `formatarBytes`.

## Validação de formulários — Zod

Defina o schema com Zod, valide no submit, mapeie erros para os campos. Padrão:

```ts
import { z } from 'zod'
const schema = z.object({ email: z.string().email('E-mail inválido'), senha: z.string().min(8) })
type Form = z.infer<typeof schema>
// no submit:
const parsed = schema.safeParse(form)
if (!parsed.success) { setErros(parsed.error.flatten().fieldErrors); return }
try { await api.post('/login', parsed.data) }
catch (e) { if (e instanceof ApiError && e.errors) setErros(e.errors); else toast.erro((e as Error).message) }
```
Schemas reutilizáveis podem ir em `src/lib/schemas.ts` (crie se precisar).

## Navegação

`import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'`.
Use `<Link to>` em vez de `<a href>`. Rotas já registradas no router (não altere).

## Visual / paridade com WebStandard

- Cards: `card h-100 shadow-sm shadow-hover`. Botões e cores Bootstrap padrão.
- Ícones: `<i className="bi bi-..." />`.
- Páginas de formulário (auth) costumam ser um `card` centralizado em coluna estreita
  (`col-md-6 col-lg-5 mx-auto`). Listagens usam `table table-hover` ou grid de cards.
- Replique títulos, textos e estrutura dos templates Jinja correspondentes em
  `WebStandard/templates/`. Leia o template da sua área antes de implementar.

## Regras de saída

- Cada página é **default export**, nome do componente = nome do arquivo.
- TypeScript **strict** + `noUnusedLocals/Parameters`: não deixe imports/vars sem uso.
- Não use `any` implícito; tipe tudo. O build roda `tsc -b` — precisa passar.
