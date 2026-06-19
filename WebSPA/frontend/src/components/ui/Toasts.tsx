import { useEffect } from 'react'
import { useUIStore, type Toast } from '../../store/uiStore'

const ICONES: Record<string, string> = {
  success: 'check-circle-fill',
  danger: 'exclamation-triangle-fill',
  warning: 'exclamation-circle-fill',
  info: 'info-circle-fill',
}

function ToastItem({ toast }: { toast: Toast }) {
  const removerToast = useUIStore((s) => s.removerToast)
  useEffect(() => {
    const t = setTimeout(() => removerToast(toast.id), 5000)
    return () => clearTimeout(t)
  }, [toast.id, removerToast])

  return (
    <div className={`toast show align-items-center text-bg-${toast.tipo} border-0 mb-2`} role="alert">
      <div className="d-flex">
        <div className="toast-body">
          <i className={`bi bi-${ICONES[toast.tipo] ?? 'info-circle-fill'} me-2`} />
          {toast.mensagem}
        </div>
        <button
          type="button"
          className="btn-close btn-close-white me-2 m-auto"
          aria-label="Fechar"
          onClick={() => removerToast(toast.id)}
        />
      </div>
    </div>
  )
}

// Container de toasts (bottom-right). Renderizado uma vez nos layouts.
export default function Toasts() {
  const toasts = useUIStore((s) => s.toasts)
  return (
    <div id="toast-container" className="toast-container position-fixed">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} />
      ))}
    </div>
  )
}
