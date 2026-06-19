import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock do cliente de API usado pelo authStore.
vi.mock('../lib/api', () => {
  class ApiError extends Error {
    status: number
    constructor(status: number, msg: string) {
      super(msg)
      this.status = status
    }
  }
  return {
    api: { get: vi.fn(), post: vi.fn() },
    ApiError,
    garantirCsrf: vi.fn().mockResolvedValue('tok'),
    limparCsrf: vi.fn(),
  }
})

import { useAuthStore } from './authStore'
import { api, ApiError, limparCsrf } from '../lib/api'

const admin = { id: 1, nome: 'Admin', email: 'a@x.com', perfil: 'Administrador', foto_url: '', data_cadastro: '' }
const cliente = { ...admin, id: 2, perfil: 'Cliente' }

const mGet = api.get as unknown as ReturnType<typeof vi.fn>
const mPost = api.post as unknown as ReturnType<typeof vi.fn>

describe('authStore', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useAuthStore.setState({ usuario: null, carregando: true })
  })

  it('login define o usuário e retorna o objeto', async () => {
    mPost.mockResolvedValueOnce(admin)
    const u = await useAuthStore.getState().login('a@x.com', 'senha')
    expect(u).toEqual(admin)
    expect(useAuthStore.getState().usuario).toEqual(admin)
    expect(mPost).toHaveBeenCalledWith('/login', { email: 'a@x.com', senha: 'senha' })
  })

  it('isAdmin reflete o perfil', () => {
    useAuthStore.setState({ usuario: admin })
    expect(useAuthStore.getState().isAdmin()).toBe(true)
    useAuthStore.setState({ usuario: cliente })
    expect(useAuthStore.getState().isAdmin()).toBe(false)
    useAuthStore.setState({ usuario: null })
    expect(useAuthStore.getState().isAdmin()).toBe(false)
  })

  it('logout limpa usuário e o token CSRF', async () => {
    useAuthStore.setState({ usuario: admin })
    mPost.mockResolvedValueOnce({ message: 'ok' })
    await useAuthStore.getState().logout()
    expect(useAuthStore.getState().usuario).toBeNull()
    expect(limparCsrf).toHaveBeenCalled()
  })

  it('carregarSessao define usuário quando /me responde', async () => {
    mGet.mockResolvedValueOnce(admin)
    await useAuthStore.getState().carregarSessao()
    const s = useAuthStore.getState()
    expect(s.usuario).toEqual(admin)
    expect(s.carregando).toBe(false)
  })

  it('carregarSessao deixa usuário nulo em 401', async () => {
    mGet.mockRejectedValueOnce(new ApiError(401, 'Não autorizado'))
    await useAuthStore.getState().carregarSessao()
    const s = useAuthStore.getState()
    expect(s.usuario).toBeNull()
    expect(s.carregando).toBe(false)
  })
})
