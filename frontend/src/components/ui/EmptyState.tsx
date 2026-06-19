import type { ReactNode } from 'react'

// Estado vazio reutilizável (espelha templates/macros/empty_states.html).
export default function EmptyState({
  icon = 'inbox',
  titulo,
  mensagem,
  children,
}: {
  icon?: string
  titulo: string
  mensagem?: string
  children?: ReactNode
}) {
  return (
    <div className="text-center text-muted py-5">
      <i className={`bi bi-${icon}`} style={{ fontSize: '3rem' }} />
      <h5 className="mt-3">{titulo}</h5>
      {mensagem && <p className="mb-3">{mensagem}</p>}
      {children}
    </div>
  )
}
