import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../lib/api'
import type { NaoLidasResumo } from '../../lib/types'

// Sino de notificações com polling a cada 30s (espelha navbar_user_dropdown.html).
export default function NotificationBell() {
  const [total, setTotal] = useState(0)

  useEffect(() => {
    let ativo = true
    async function verificar() {
      try {
        const data = await api.get<NaoLidasResumo>('/notificacoes/nao-lidas')
        if (ativo) setTotal(data.total ?? 0)
      } catch {
        // silencioso em erros de rede
      }
    }
    verificar()
    const id = setInterval(verificar, 30000)
    return () => {
      ativo = false
      clearInterval(id)
    }
  }, [])

  const texto = total > 99 ? '99+' : String(total)

  return (
    <li className="nav-item me-1">
      <Link className="nav-link position-relative" to="/notificacoes" title="Notificações">
        <i className="bi bi-bell fs-5" />
        {total > 0 && (
          <span
            className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
            style={{ fontSize: '0.6rem' }}
          >
            {texto}
          </span>
        )}
      </Link>
    </li>
  )
}
