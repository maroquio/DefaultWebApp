import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Footer from './Footer'
import Toasts from '../ui/Toasts'
import ConfirmModal from '../ui/ConfirmModal'
import AlertModal from '../ui/AlertModal'
import ChatWidget from '../chat/ChatWidget'

// Layout das páginas autenticadas (espelha base_privada.html).
export default function PrivateLayout() {
  return (
    <>
      <Navbar variant="privada" />
      <main className="container d-flex flex-column flex-fill my-4">
        <Outlet />
      </main>
      <Footer />
      <Toasts />
      <ConfirmModal />
      <AlertModal />
      <ChatWidget />
    </>
  )
}
