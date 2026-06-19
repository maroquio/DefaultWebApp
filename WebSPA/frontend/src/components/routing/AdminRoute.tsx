import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

// Exige usuário autenticado E perfil Administrador.
export default function AdminRoute() {
  const usuario = useAuthStore((s) => s.usuario)
  const isAdmin = useAuthStore((s) => s.isAdmin())

  if (!usuario) return <Navigate to="/login" replace />
  if (!isAdmin) return <Navigate to="/usuario" replace />
  return <Outlet />
}
