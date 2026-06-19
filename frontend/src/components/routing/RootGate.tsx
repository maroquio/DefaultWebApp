import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

// Componente raiz: verifica a sessão (GET /api/me) uma vez no boot e
// segura a renderização até saber se há usuário logado.
export default function RootGate() {
  const carregando = useAuthStore((s) => s.carregando)
  const carregarSessao = useAuthStore((s) => s.carregarSessao)

  useEffect(() => {
    carregarSessao()
  }, [carregarSessao])

  if (carregando) {
    return (
      <div className="d-flex vh-100 align-items-center justify-content-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Carregando...</span>
        </div>
      </div>
    )
  }

  return <Outlet />
}
