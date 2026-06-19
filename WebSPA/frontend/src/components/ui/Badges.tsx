// Badges portados de templates/macros/badges.html (mesmas cores).

function cls(cor: string) {
  return `badge bg-${cor}`
}

export function StatusChamadoBadge({ status }: { status: string }) {
  const cor =
    status === 'Aberto'
      ? 'primary'
      : status === 'Em Análise'
        ? 'info'
        : status === 'Resolvido'
          ? 'success'
          : 'secondary'
  return <span className={cls(cor)}>{status}</span>
}

export function PrioridadeBadge({ prioridade }: { prioridade: string }) {
  const cor =
    prioridade === 'Urgente'
      ? 'danger'
      : prioridade === 'Alta'
        ? 'warning text-dark'
        : prioridade === 'Média'
          ? 'info'
          : 'secondary'
  return <span className={cls(cor)}>{prioridade}</span>
}

export function PerfilBadge({ perfil }: { perfil: string }) {
  const cor =
    perfil === 'Administrador' ? 'danger' : perfil === 'Vendedor' ? 'warning text-dark' : 'info'
  return <span className={cls(cor)}>{perfil}</span>
}

export function StatusPagamentoBadge({ status }: { status: string }) {
  const cor =
    status === 'Aprovado'
      ? 'success'
      : status === 'Pendente'
        ? 'warning text-dark'
        : status === 'Em Processamento'
          ? 'primary'
          : status === 'Recusado'
            ? 'danger'
            : status === 'Reembolsado'
              ? 'info'
              : 'secondary'
  return <span className={cls(cor)}>{status}</span>
}

export function MensagensNaoLidasBadge({ count }: { count: number }) {
  if (!count || count <= 0) return null
  return (
    <span className="badge bg-warning text-dark">
      <i className="bi bi-envelope-fill" /> {count} não lida{count > 1 ? 's' : ''}
    </span>
  )
}

export function Badge({
  texto,
  cor = 'secondary',
  icon,
}: {
  texto: string
  cor?: string
  icon?: string
}) {
  return (
    <span className={cls(cor)}>
      {icon && <i className={`bi bi-${icon}`} />} {texto}
    </span>
  )
}
