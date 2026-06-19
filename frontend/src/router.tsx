import { createBrowserRouter } from 'react-router-dom'

import RootGate from './components/routing/RootGate'
import RouteError from './components/routing/RouteError'
import ProtectedRoute from './components/routing/ProtectedRoute'
import AdminRoute from './components/routing/AdminRoute'
import PublicLayout from './components/layout/PublicLayout'
import PrivateLayout from './components/layout/PrivateLayout'

// Páginas públicas
import HomePage from './pages/public/HomePage'
import SobrePage from './pages/public/SobrePage'
import NotFoundPage from './pages/public/NotFoundPage'
import LoginPage from './pages/auth/LoginPage'
import CadastroPage from './pages/auth/CadastroPage'
import EsqueciSenhaPage from './pages/auth/EsqueciSenhaPage'
import RedefinirSenhaPage from './pages/auth/RedefinirSenhaPage'

// Exemplos
import ExemplosIndexPage from './pages/exemplos/ExemplosIndexPage'
import CamposFormularioPage from './pages/exemplos/CamposFormularioPage'
import GradeCartoesPage from './pages/exemplos/GradeCartoesPage'
import ListaTabelaPage from './pages/exemplos/ListaTabelaPage'
import DetalhesProdutoPage from './pages/exemplos/DetalhesProdutoPage'
import DetalhesServicoPage from './pages/exemplos/DetalhesServicoPage'
import DetalhesPerfilPage from './pages/exemplos/DetalhesPerfilPage'
import DetalhesImovelPage from './pages/exemplos/DetalhesImovelPage'

// Usuário
import DashboardPage from './pages/usuario/DashboardPage'
import PerfilVisualizarPage from './pages/usuario/PerfilVisualizarPage'
import PerfilEditarPage from './pages/usuario/PerfilEditarPage'
import AlterarSenhaPage from './pages/usuario/AlterarSenhaPage'

// Chamados
import ChamadosListarPage from './pages/chamados/ChamadosListarPage'
import ChamadoCadastrarPage from './pages/chamados/ChamadoCadastrarPage'
import ChamadoVisualizarPage from './pages/chamados/ChamadoVisualizarPage'

// Notificações
import NotificacoesPage from './pages/notificacoes/NotificacoesPage'

// Pagamentos
import PagamentosListarPage from './pages/pagamentos/PagamentosListarPage'
import PagamentoCriarPage from './pages/pagamentos/PagamentoCriarPage'
import PagamentoDetalhesPage from './pages/pagamentos/PagamentoDetalhesPage'
import PagamentoSucessoPage from './pages/pagamentos/PagamentoSucessoPage'
import PagamentoPendentePage from './pages/pagamentos/PagamentoPendentePage'
import PagamentoFalhaPage from './pages/pagamentos/PagamentoFalhaPage'

// Admin
import AdminUsuariosListarPage from './pages/admin/usuarios/AdminUsuariosListarPage'
import AdminUsuarioCadastrarPage from './pages/admin/usuarios/AdminUsuarioCadastrarPage'
import AdminUsuarioEditarPage from './pages/admin/usuarios/AdminUsuarioEditarPage'
import AdminChamadosListarPage from './pages/admin/chamados/AdminChamadosListarPage'
import AdminChamadoResponderPage from './pages/admin/chamados/AdminChamadoResponderPage'
import AdminPagamentosListarPage from './pages/admin/pagamentos/AdminPagamentosListarPage'
import AdminPagamentoDetalhesPage from './pages/admin/pagamentos/AdminPagamentoDetalhesPage'
import AdminBackupsPage from './pages/admin/backups/AdminBackupsPage'
import AdminConfiguracoesPage from './pages/admin/config/AdminConfiguracoesPage'
import AdminAuditoriaLogsPage from './pages/admin/auditoria/AdminAuditoriaLogsPage'
import AdminAuditoriaRegistrosPage from './pages/admin/auditoria/AdminAuditoriaRegistrosPage'

export const router = createBrowserRouter([
  {
    element: <RootGate />,
    errorElement: <RouteError />,
    children: [
      // ===== Público =====
      {
        element: <PublicLayout />,
        children: [
          { path: '/', element: <HomePage /> },
          { path: '/index', element: <HomePage /> },
          { path: '/sobre', element: <SobrePage /> },
          { path: '/login', element: <LoginPage /> },
          { path: '/cadastrar', element: <CadastroPage /> },
          { path: '/esqueci-senha', element: <EsqueciSenhaPage /> },
          { path: '/redefinir-senha', element: <RedefinirSenhaPage /> },
          { path: '/exemplos', element: <ExemplosIndexPage /> },
          { path: '/exemplos/campos-formulario', element: <CamposFormularioPage /> },
          { path: '/exemplos/grade-cartoes', element: <GradeCartoesPage /> },
          { path: '/exemplos/lista-tabela', element: <ListaTabelaPage /> },
          { path: '/exemplos/detalhes-produto', element: <DetalhesProdutoPage /> },
          { path: '/exemplos/detalhes-servico', element: <DetalhesServicoPage /> },
          { path: '/exemplos/detalhes-perfil', element: <DetalhesPerfilPage /> },
          { path: '/exemplos/detalhes-imovel', element: <DetalhesImovelPage /> },
        ],
      },

      // ===== Autenticado (qualquer perfil) =====
      {
        element: <ProtectedRoute />,
        children: [
          {
            element: <PrivateLayout />,
            children: [
              { path: '/usuario', element: <DashboardPage /> },
              { path: '/usuario/perfil/visualizar', element: <PerfilVisualizarPage /> },
              { path: '/usuario/perfil/editar', element: <PerfilEditarPage /> },
              { path: '/usuario/perfil/alterar-senha', element: <AlterarSenhaPage /> },
              { path: '/chamados/listar', element: <ChamadosListarPage /> },
              { path: '/chamados/cadastrar', element: <ChamadoCadastrarPage /> },
              { path: '/chamados/:id/visualizar', element: <ChamadoVisualizarPage /> },
              { path: '/notificacoes', element: <NotificacoesPage /> },
              { path: '/pagamentos/listar', element: <PagamentosListarPage /> },
              { path: '/pagamentos/criar', element: <PagamentoCriarPage /> },
              { path: '/pagamentos/sucesso', element: <PagamentoSucessoPage /> },
              { path: '/pagamentos/paypal/capturar', element: <PagamentoSucessoPage /> },
              { path: '/pagamentos/pendente', element: <PagamentoPendentePage /> },
              { path: '/pagamentos/falha', element: <PagamentoFalhaPage /> },
              { path: '/pagamentos/:id', element: <PagamentoDetalhesPage /> },
            ],
          },
        ],
      },

      // ===== Administrador =====
      {
        element: <AdminRoute />,
        children: [
          {
            element: <PrivateLayout />,
            children: [
              { path: '/admin/usuarios/listar', element: <AdminUsuariosListarPage /> },
              { path: '/admin/usuarios/cadastrar', element: <AdminUsuarioCadastrarPage /> },
              { path: '/admin/usuarios/editar/:id', element: <AdminUsuarioEditarPage /> },
              { path: '/admin/chamados/listar', element: <AdminChamadosListarPage /> },
              { path: '/admin/chamados/:id/responder', element: <AdminChamadoResponderPage /> },
              { path: '/admin/pagamentos', element: <AdminPagamentosListarPage /> },
              { path: '/admin/pagamentos/:id', element: <AdminPagamentoDetalhesPage /> },
              { path: '/admin/backups/listar', element: <AdminBackupsPage /> },
              { path: '/admin/configuracoes', element: <AdminConfiguracoesPage /> },
              { path: '/admin/auditoria', element: <AdminAuditoriaLogsPage /> },
              { path: '/admin/auditoria/registros', element: <AdminAuditoriaRegistrosPage /> },
            ],
          },
        ],
      },

      // ===== 404 =====
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
