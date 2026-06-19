import { create } from 'zustand'
import { api, ApiError, garantirCsrf, limparCsrf } from '../lib/api'
import type { Usuario } from '../lib/types'
import { Perfil } from '../lib/types'

interface AuthState {
  usuario: Usuario | null
  /** true até a verificação inicial de sessão terminar. */
  carregando: boolean
  isAdmin: () => boolean
  /** Verifica a sessão atual no backend (GET /api/me). Chamado no boot. */
  carregarSessao: () => Promise<void>
  login: (email: string, senha: string) => Promise<Usuario>
  logout: () => Promise<void>
  /** Atualiza o usuário em memória (após editar perfil/foto). */
  setUsuario: (u: Usuario) => void
}

export const useAuthStore = create<AuthState>((set, get) => ({
  usuario: null,
  carregando: true,

  isAdmin: () => get().usuario?.perfil === Perfil.ADMIN,

  carregarSessao: async () => {
    try {
      await garantirCsrf()
      const usuario = await api.get<Usuario>('/me')
      set({ usuario, carregando: false })
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        set({ usuario: null, carregando: false })
      } else {
        set({ usuario: null, carregando: false })
      }
    }
  },

  login: async (email, senha) => {
    const usuario = await api.post<Usuario>('/login', { email, senha })
    set({ usuario })
    return usuario
  },

  logout: async () => {
    try {
      await api.post('/logout')
    } finally {
      limparCsrf()
      set({ usuario: null })
    }
  },

  setUsuario: (usuario) => set({ usuario }),
}))
