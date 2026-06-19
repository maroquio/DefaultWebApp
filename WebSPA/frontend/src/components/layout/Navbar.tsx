import { NavLink } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import UserDropdown from './UserDropdown'
import NotificationBell from './NotificationBell'

function linkClass({ isActive }: { isActive: boolean }) {
  return `nav-link ${isActive ? 'active' : ''}`
}

// Navbar adaptativa: cobre base_publica.html e base_privada.html do WebStandard.
export default function Navbar({ variant }: { variant: 'publica' | 'privada' }) {
  const usuario = useAuthStore((s) => s.usuario)
  const isAdmin = useAuthStore((s) => s.isAdmin())

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
      <div className="container">
        <NavLink className="navbar-brand d-flex align-middle" to="/">
          Sistema Web
        </NavLink>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span className="navbar-toggler-icon" />
        </button>

        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            {variant === 'publica' ? (
              <>
                <li className="nav-item">
                  <NavLink className={linkClass} to="/" end>
                    Início
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className={linkClass} to="/sobre">
                    Sobre
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className={linkClass} to="/exemplos">
                    Exemplos
                  </NavLink>
                </li>
              </>
            ) : (
              <>
                <li className="nav-item">
                  <NavLink className={linkClass} to="/usuario">
                    Dashboard
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className={linkClass} to="/usuario/perfil/visualizar">
                    Perfil
                  </NavLink>
                </li>
                {isAdmin ? (
                  <>
                    <li className="nav-item">
                      <NavLink className={linkClass} to="/admin/chamados/listar">
                        Chamados
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className={linkClass} to="/admin/usuarios/listar">
                        Usuários
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className={linkClass} to="/admin/pagamentos">
                        Pagamentos
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className={linkClass} to="/admin/configuracoes">
                        Configurações
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className={linkClass} to="/admin/auditoria">
                        Auditoria
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className={linkClass} to="/admin/backups/listar">
                        Backup
                      </NavLink>
                    </li>
                  </>
                ) : (
                  <>
                    <li className="nav-item">
                      <NavLink className={linkClass} to="/chamados/listar">
                        Chamados
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className={linkClass} to="/pagamentos/listar">
                        Pagamentos
                      </NavLink>
                    </li>
                  </>
                )}
              </>
            )}
          </ul>

          <ul className="navbar-nav align-items-lg-center">
            {usuario ? (
              <>
                <NotificationBell />
                <UserDropdown />
              </>
            ) : (
              <>
                <li className="nav-item">
                  <NavLink className={linkClass} to="/login">
                    Login
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className={linkClass} to="/cadastrar">
                    Cadastrar
                  </NavLink>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  )
}
