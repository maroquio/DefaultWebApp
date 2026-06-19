// Painel do usuario logado: saudacao + cards de acao rapida.
// Replica templates/dashboard.html do WebStandard.
import { Link } from 'react-router-dom'
import { api } from '../../lib/api'
import { useFetch } from '../../hooks/useFetch'
import { useAuthStore } from '../../store/authStore'
import type { DashboardData } from '../../lib/types'

export default function DashboardPage() {
  const usuario = useAuthStore((s) => s.usuario)
  const isAdmin = useAuthStore((s) => s.isAdmin())

  const { data } = useFetch<DashboardData>(
    (signal) => api.get<DashboardData>('/usuario/dashboard', { signal }),
    [],
  )

  const chamadosPendentes = data?.chamados_pendentes ?? 0
  const chamadosAbertos = data?.chamados_abertos ?? 0

  return (
    <>
      {/* Cabecalho de Boas-Vindas */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="bg-primary text-white rounded p-4 shadow-sm">
            <h1 className="mb-2">
              <i className="bi bi-house-door" /> Bem-vindo(a), {usuario?.nome}!
            </h1>
            <p className="mb-0 lead">Este é o seu painel de controle pessoal.</p>
          </div>
        </div>
      </div>

      {/* Cards de Acao Rapida */}
      <div className="row g-4 mb-4 row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4">
        {/* Meu Perfil */}
        <div className="col">
          <div className="card h-100 shadow-sm shadow-hover">
            <div className="card-body text-center">
              <div className="mb-3">
                <i className="bi bi-person-circle text-primary display-3" />
              </div>
              <h5 className="card-title">Meu Perfil</h5>
              <p className="card-text text-muted">Visualize e edite suas informações pessoais</p>
              <Link to="/usuario/perfil/visualizar" className="btn btn-primary">
                <i className="bi bi-arrow-right-circle" /> Acessar
              </Link>
            </div>
          </div>
        </div>

        {isAdmin ? (
          <>
            {/* Usuarios */}
            <div className="col">
              <div className="card h-100 shadow-sm shadow-hover">
                <div className="card-body text-center">
                  <div className="mb-3">
                    <i className="bi bi-people text-success display-3" />
                  </div>
                  <h5 className="card-title">Usuários</h5>
                  <p className="card-text text-muted">Gerencie os usuários cadastrados no sistema</p>
                  <Link to="/admin/usuarios/listar" className="btn btn-success">
                    <i className="bi bi-arrow-right-circle" /> Acessar
                  </Link>
                </div>
              </div>
            </div>

            {/* Configurações */}
            <div className="col">
              <div className="card h-100 shadow-sm shadow-hover">
                <div className="card-body text-center">
                  <div className="mb-3">
                    <i className="bi bi-gear-fill text-secondary display-3" />
                  </div>
                  <h5 className="card-title">Configurações</h5>
                  <p className="card-text text-muted">
                    Ajuste as configurações editáveis da aplicação
                  </p>
                  <Link to="/admin/configuracoes" className="btn btn-secondary">
                    <i className="bi bi-arrow-right-circle" /> Acessar
                  </Link>
                </div>
              </div>
            </div>

            {/* Auditoria de Logs */}
            <div className="col">
              <div className="card h-100 shadow-sm shadow-hover">
                <div className="card-body text-center">
                  <div className="mb-3">
                    <i className="bi bi-journal-text text-warning display-3" />
                  </div>
                  <h5 className="card-title">Auditoria de Logs</h5>
                  <p className="card-text text-muted">
                    Visualize e filtre logs do sistema por data e severidade
                  </p>
                  <Link to="/admin/auditoria" className="btn btn-warning">
                    <i className="bi bi-arrow-right-circle" /> Acessar
                  </Link>
                </div>
              </div>
            </div>

            {/* Backup do Banco */}
            <div className="col">
              <div className="card h-100 shadow-sm shadow-hover">
                <div className="card-body text-center">
                  <div className="mb-3">
                    <i className="bi bi-database text-info display-3" />
                  </div>
                  <h5 className="card-title">Backup do Banco</h5>
                  <p className="card-text text-muted">
                    Crie, gerencie e restaure backups do banco de dados
                  </p>
                  <Link to="/admin/backups/listar" className="btn btn-info">
                    <i className="bi bi-arrow-right-circle" /> Acessar
                  </Link>
                </div>
              </div>
            </div>

            {/* Chamados (admin) */}
            <div className="col">
              <div className="card h-100 shadow-sm shadow-hover">
                <div className="card-body text-center">
                  <div className="mb-3">
                    <i className="bi bi-headset text-danger display-3" />
                  </div>
                  <h5 className="card-title">Chamados</h5>
                  <p className="card-text text-muted">Gerencie chamados de suporte dos usuários</p>
                  {chamadosPendentes > 0 && (
                    <div className="mb-3">
                      <span className="badge bg-danger">{chamadosPendentes} pendente(s)</span>
                    </div>
                  )}
                  <Link to="/admin/chamados/listar" className="btn btn-danger">
                    <i className="bi bi-arrow-right-circle" /> Acessar
                  </Link>
                </div>
              </div>
            </div>
          </>
        ) : (
          /* Meus Chamados (cliente) */
          <div className="col">
            <div className="card h-100 shadow-sm shadow-hover">
              <div className="card-body text-center">
                <div className="mb-3">
                  <i className="bi bi-headset text-danger display-3" />
                </div>
                <h5 className="card-title">Meus Chamados</h5>
                <p className="card-text text-muted">
                  Abra chamados de suporte e acompanhe suas solicitações
                </p>
                {chamadosAbertos > 0 && (
                  <div className="mb-3">
                    <span className="badge bg-danger">{chamadosAbertos} em aberto</span>
                  </div>
                )}
                <Link to="/chamados/listar" className="btn btn-danger">
                  <i className="bi bi-arrow-right-circle" /> Acessar
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Dica do Dia */}
      <div className="row">
        <div className="col-12">
          <div className="alert alert-info" role="alert">
            <i className="bi bi-lightbulb" /> <strong>Dica do Dia:</strong> Mantenha suas
            informações sempre atualizadas em "Meu Perfil" para garantir uma melhor experiência no
            sistema.
          </div>
        </div>
      </div>
    </>
  )
}
