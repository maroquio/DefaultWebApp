import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { api, ApiError, garantirCsrf, limparCsrf } from './api'

// Resposta fake no formato esperado pelo cliente (resp.text()/status/headers).
function fakeResp(opts: {
  status: number
  ok?: boolean
  body?: unknown
  retryAfter?: string
}) {
  const { status, body, retryAfter } = opts
  const ok = opts.ok ?? (status >= 200 && status < 300)
  return {
    ok,
    status,
    statusText: 'X',
    headers: { get: (h: string) => (h === 'Retry-After' ? (retryAfter ?? null) : null) },
    text: async () => (body === undefined ? '' : JSON.stringify(body)),
    json: async () => body,
  } as unknown as Response
}

describe('api client', () => {
  beforeEach(() => {
    limparCsrf()
    vi.stubGlobal('fetch', vi.fn())
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('garantirCsrf busca o token uma vez e cacheia', async () => {
    const f = fetch as unknown as ReturnType<typeof vi.fn>
    f.mockResolvedValue(fakeResp({ status: 200, body: { token: 'abc' } }))

    const t1 = await garantirCsrf()
    const t2 = await garantirCsrf()

    expect(t1).toBe('abc')
    expect(t2).toBe('abc')
    expect(f).toHaveBeenCalledTimes(1) // cacheado
    expect(f).toHaveBeenCalledWith('/api/csrf-token', expect.objectContaining({ credentials: 'include' }))
  })

  it('GET monta query string ignorando valores vazios/nulos', async () => {
    const f = fetch as unknown as ReturnType<typeof vi.fn>
    f.mockResolvedValue(fakeResp({ status: 200, body: { ok: true } }))

    await api.get('/itens', { params: { pagina: 2, q: '', filtro: undefined, ativo: true } })

    const url = f.mock.calls[0][0] as string
    expect(url).toBe('/api/itens?pagina=2&ativo=true')
  })

  it('inclui header X-CSRF-Token em mutações (POST)', async () => {
    const f = fetch as unknown as ReturnType<typeof vi.fn>
    f.mockResolvedValueOnce(fakeResp({ status: 200, body: { token: 'tok-1' } })) // csrf-token
    f.mockResolvedValueOnce(fakeResp({ status: 201, body: { id: 1 } })) // POST

    const r = await api.post<{ id: number }>('/itens', { nome: 'x' })

    expect(r).toEqual({ id: 1 })
    const postInit = f.mock.calls[1][1]
    expect(postInit.headers['X-CSRF-Token']).toBe('tok-1')
    expect(postInit.headers['Content-Type']).toBe('application/json')
    expect(postInit.body).toBe(JSON.stringify({ nome: 'x' }))
  })

  it('204 retorna undefined sem tentar parsear corpo', async () => {
    const f = fetch as unknown as ReturnType<typeof vi.fn>
    f.mockResolvedValueOnce(fakeResp({ status: 200, body: { token: 't' } })) // csrf p/ DELETE
    f.mockResolvedValueOnce(fakeResp({ status: 204 }))

    const r = await api.delete('/itens/1')
    expect(r).toBeUndefined()
  })

  it('lança ApiError com o contrato padronizado em erro', async () => {
    const f = fetch as unknown as ReturnType<typeof vi.fn>
    f.mockResolvedValue(
      fakeResp({
        status: 422,
        body: {
          detail: 'Falha de validação',
          type: 'validation_error',
          errors: { email: ['E-mail inválido'] },
        },
      }),
    )

    const erro = await api.get('/itens').catch((e) => e)
    expect(erro).toBeInstanceOf(ApiError)
    expect(erro.status).toBe(422)
    expect(erro.type).toBe('validation_error')
    expect(erro.message).toBe('Falha de validação')
    expect(erro.campo('email')).toBe('E-mail inválido')
  })

  it('propaga Retry-After em 429', async () => {
    const f = fetch as unknown as ReturnType<typeof vi.fn>
    f.mockResolvedValue(
      fakeResp({ status: 429, body: { detail: 'Muitas requisições', type: 'rate_limited' }, retryAfter: '30' }),
    )

    const erro = (await api.get('/itens').catch((e) => e)) as ApiError
    expect(erro.status).toBe(429)
    expect(erro.retryAfter).toBe(30)
  })

  it('converte falha de rede em ApiError de conexão', async () => {
    const f = fetch as unknown as ReturnType<typeof vi.fn>
    f.mockRejectedValue(new TypeError('network down'))

    const erro = (await api.get('/itens').catch((e) => e)) as ApiError
    expect(erro).toBeInstanceOf(ApiError)
    expect(erro.status).toBe(0)
    expect(erro.type).toBe('internal_error')
  })
})
