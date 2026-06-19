import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Footer from './Footer'
import Toasts from '../ui/Toasts'
import ConfirmModal from '../ui/ConfirmModal'
import AlertModal from '../ui/AlertModal'
import ChatWidget from '../chat/ChatWidget'
import { useAuthStore } from '../../store/authStore'

// Layout das páginas públicas (espelha base_publica.html).
export default function PublicLayout() {
  const usuario = useAuthStore((s) => s.usuario)
  return (
    <>
      <Navbar variant="publica" />
      <main className="container d-flex flex-column flex-fill my-4">
        <Outlet />
      </main>
      <Footer />
      <Toasts />
      <ConfirmModal />
      <AlertModal />
      {usuario && <ChatWidget />}
    </>
  )
}
