import { create } from 'zustand'

// ===== Toasts (substitui window.App.Toasts do WebStandard) =====
export type ToastTipo = 'success' | 'danger' | 'warning' | 'info'
export interface Toast {
  id: number
  mensagem: string
  tipo: ToastTipo
}

// ===== Modal de confirmação (substitui abrirModalConfirmacao) =====
export interface ConfirmConfig {
  titulo?: string
  mensagem: string
  detalhes?: string
  textoConfirmar?: string
  textoCancelar?: string
  tipo?: 'danger' | 'warning'
  onConfirmar: () => void | Promise<void>
}

// ===== Modal de alerta (substitui window.App.Modal) =====
export interface AlertConfig {
  titulo?: string
  mensagem: string
  detalhes?: string
  tipo?: 'danger' | 'warning' | 'info' | 'success'
}

interface UIState {
  toasts: Toast[]
  confirm: ConfirmConfig | null
  alert: AlertConfig | null
  mostrarToast: (mensagem: string, tipo?: ToastTipo) => void
  removerToast: (id: number) => void
  pedirConfirmacao: (config: ConfirmConfig) => void
  fecharConfirmacao: () => void
  mostrarAlerta: (config: AlertConfig) => void
  fecharAlerta: () => void
}

let seq = 1

export const useUIStore = create<UIState>((set) => ({
  toasts: [],
  confirm: null,
  alert: null,

  mostrarToast: (mensagem, tipo = 'info') =>
    set((s) => ({ toasts: [...s.toasts, { id: seq++, mensagem, tipo }] })),
  removerToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),

  pedirConfirmacao: (confirm) => set({ confirm }),
  fecharConfirmacao: () => set({ confirm: null }),

  mostrarAlerta: (alert) => set({ alert }),
  fecharAlerta: () => set({ alert: null }),
}))

// Atalhos convenientes para uso fora de componentes.
export const toast = {
  sucesso: (m: string) => useUIStore.getState().mostrarToast(m, 'success'),
  erro: (m: string) => useUIStore.getState().mostrarToast(m, 'danger'),
  aviso: (m: string) => useUIStore.getState().mostrarToast(m, 'warning'),
  info: (m: string) => useUIStore.getState().mostrarToast(m, 'info'),
}
