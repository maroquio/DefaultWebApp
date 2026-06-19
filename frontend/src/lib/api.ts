// Cliente HTTP central para a API JSON do backend FastAPI.
//
// Regras do contrato (ver backend/CLAUDE.md):
// - Sempre `credentials: 'include'` para enviar o cookie de sessão.
// - Mutações (POST/PUT/PATCH/DELETE) exigem header `X-CSRF-Token`, obtido
//   via GET /api/csrf-token e mantido na sessão do backend.
// - Erros seguem o contrato { detail, type, errors }.

const BASE = '/api'

export type ErroTipo =
  | 'validation_error'
  | 'not_found'
  | 'unauthorized'
  | 'forbidden'
  | 'conflict'
  | 'rate_limited'
  | 'internal_error'
  | string

/** Erro padronizado lançado por todas as chamadas à API. */
export class ApiError extends Error {
  status: number
  type: ErroTipo
  /** Erros de validação por campo (preenchido em 422). */
  errors: Record<string, string[]> | null
  retryAfter?: number

  constructor(
    status: number,
    detail: string,
    type: ErroTipo,
    errors: Record<string, string[]> | null = null,
    retryAfter?: number,
  ) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
    this.type = type
    this.errors = errors
    this.retryAfter = retryAfter
  }

  /** Retorna a primeira mensagem de erro de um campo, se houver. */
  campo(nome: string): string | undefined {
    return this.errors?.[nome]?.[0]
  }
}

// ===== Gerência do token CSRF =====
let csrfToken: string | null = null
let csrfPromise: Promise<string> | null = null

/** Obtém (e cacheia) o token CSRF. Idempotente sob concorrência. */
export async function garantirCsrf(): Promise<string> {
  if (csrfToken) return csrfToken
  if (!csrfPromise) {
    csrfPromise = fetch(`${BASE}/csrf-token`, { credentials: 'include' })
      .then(async (r) => {
        if (!r.ok) throw new Error('Falha ao obter token CSRF')
        const data = (await r.json()) as { token: string }
        csrfToken = data.token
        return csrfToken
      })
      .finally(() => {
        csrfPromise = null
      })
  }
  return csrfPromise
}

/** Limpa o token CSRF em cache (ex: após logout). */
export function limparCsrf(): void {
  csrfToken = null
}

const METODOS_COM_CSRF = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

interface RequestOpts {
  /** Query string como objeto (valores undefined/null/'' são omitidos). */
  params?: Record<string, string | number | boolean | undefined | null>
  /** Corpo JSON (serializado automaticamente). */
  body?: unknown
  signal?: AbortSignal
}

function montarUrl(path: string, params?: RequestOpts['params']): string {
  const url = `${BASE}${path}`
  if (!params) return url
  const qs = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === '') continue
    qs.append(k, String(v))
  }
  const s = qs.toString()
  return s ? `${url}?${s}` : url
}

async function request<T>(method: string, path: string, opts: RequestOpts = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json' }

  if (opts.body !== undefined) headers['Content-Type'] = 'application/json'
  if (METODOS_COM_CSRF.has(method)) headers['X-CSRF-Token'] = await garantirCsrf()

  let resp: Response
  try {
    resp = await fetch(montarUrl(path, opts.params), {
      method,
      headers,
      credentials: 'include',
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
      signal: opts.signal,
    })
  } catch (e) {
    if ((e as Error).name === 'AbortError') throw e
    throw new ApiError(0, 'Falha de conexão com o servidor.', 'internal_error')
  }

  // 204 No Content / corpo vazio
  if (resp.status === 204) return undefined as T

  const texto = await resp.text()
  const data = texto ? safeJson(texto) : null

  if (!resp.ok) {
    // Token CSRF pode ter expirado: zera para forçar novo handshake.
    if (resp.status === 403) limparCsrf()
    const retryAfter = resp.headers.get('Retry-After')
    throw new ApiError(
      resp.status,
      (data?.detail as string) || resp.statusText || 'Erro na requisição.',
      (data?.type as ErroTipo) || 'internal_error',
      (data?.errors as Record<string, string[]>) ?? null,
      retryAfter ? Number(retryAfter) : undefined,
    )
  }

  return data as T
}

function safeJson(texto: string): Record<string, unknown> | null {
  try {
    return JSON.parse(texto)
  } catch {
    return null
  }
}

export const api = {
  get: <T>(path: string, opts?: Omit<RequestOpts, 'body'>) => request<T>('GET', path, opts),
  post: <T>(path: string, body?: unknown, opts?: RequestOpts) =>
    request<T>('POST', path, { ...opts, body }),
  put: <T>(path: string, body?: unknown, opts?: RequestOpts) =>
    request<T>('PUT', path, { ...opts, body }),
  patch: <T>(path: string, body?: unknown, opts?: RequestOpts) =>
    request<T>('PATCH', path, { ...opts, body }),
  delete: <T>(path: string, opts?: RequestOpts) => request<T>('DELETE', path, opts),
}
