import { describe, it, expect, beforeEach } from 'vitest'
import { useUIStore, toast } from './uiStore'

function reset() {
  useUIStore.setState({ toasts: [], confirm: null, alert: null })
}

describe('uiStore', () => {
  beforeEach(reset)

  it('adiciona e remove toasts', () => {
    const { mostrarToast } = useUIStore.getState()
    mostrarToast('Salvo', 'success')
    mostrarToast('Erro', 'danger')

    let toasts = useUIStore.getState().toasts
    expect(toasts).toHaveLength(2)
    expect(toasts[0]).toMatchObject({ mensagem: 'Salvo', tipo: 'success' })

    useUIStore.getState().removerToast(toasts[0].id)
    toasts = useUIStore.getState().toasts
    expect(toasts).toHaveLength(1)
    expect(toasts[0].mensagem).toBe('Erro')
  })

  it('atalhos toast.* aplicam o tipo correto', () => {
    toast.sucesso('a')
    toast.erro('b')
    toast.aviso('c')
    toast.info('d')
    const tipos = useUIStore.getState().toasts.map((t) => t.tipo)
    expect(tipos).toEqual(['success', 'danger', 'warning', 'info'])
  })

  it('gerencia o modal de confirmação', () => {
    const onConfirmar = () => {}
    useUIStore.getState().pedirConfirmacao({ mensagem: 'Excluir?', onConfirmar })
    expect(useUIStore.getState().confirm?.mensagem).toBe('Excluir?')

    useUIStore.getState().fecharConfirmacao()
    expect(useUIStore.getState().confirm).toBeNull()
  })

  it('gerencia o modal de alerta', () => {
    useUIStore.getState().mostrarAlerta({ mensagem: 'Atenção', tipo: 'warning' })
    expect(useUIStore.getState().alert).toMatchObject({ mensagem: 'Atenção', tipo: 'warning' })

    useUIStore.getState().fecharAlerta()
    expect(useUIStore.getState().alert).toBeNull()
  })
})
