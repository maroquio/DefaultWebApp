import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { toast } from '../../store/uiStore'

// Dropdown do usuário logado (espelha components/navbar_user_dropdown.html).
export default function UserDropdown() {
  const usuario = useAuthStore((s) => s.usuario)
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  if (!usuario) return null

  async function sair() {
    await logout()
    toast.info('Sessão encerrada.')
    navigate('/login')
  }

  return (
    <li className="nav-item dropdown">
      <a
        className="nav-link dropdown-toggle d-flex align-items-center"
        href="#"
        role="button"
        data-bs-toggle="dropdown"
      >
        <img
          src={usuario.foto_url || '/static/img/user.jpg'}
          alt="Foto do usuário"
          className="rounded-circle me-2 object-fit-cover"
          width={32}
          height={32}
          onError={(e) => {
            ;(e.target as HTMLImageElement).src = '/static/img/user.jpg'
          }}
        />
        {usuario.nome}
      </a>
      <ul className="dropdown-menu dropdown-menu-end">
        <li>
          <Link className="dropdown-item" to="/usuario">
            <i className="bi bi-speedometer2 me-2" /> Dashboard
          </Link>
        </li>
        <li>
          <Link className="dropdown-item" to="/usuario/perfil/visualizar">
            <i className="bi bi-person me-2" /> Meu Perfil
          </Link>
        </li>
        <li>
          <Link className="dropdown-item" to="/notificacoes">
            <i className="bi bi-bell me-2" /> Notificações
          </Link>
        </li>
        <li>
          <hr className="dropdown-divider" />
        </li>
        <li>
          <button className="dropdown-item" onClick={sair}>
            <i className="bi bi-box-arrow-right me-2" /> Sair
          </button>
        </li>
      </ul>
    </li>
  )
}
