import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../../lib/api'
import type { LogArquivo } from '../../../lib/types'
import { useFetch } from '../../../hooks/useFetch'
import Spinner from '../../../components/ui/Spinner'

const NIVEIS = ['TODOS', 'INFO', 'ERROR'] as const

function hojeISO(): string {
  // Data local (não UTC): evita pular para o dia seguinte à noite no fuso BRT.
  const d = new Date()
  const mes = String(d.getMonth() + 1).padStart(2, '0')
  const dia = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mes}-${dia}`
}

export default function AdminAuditoriaLogsPage() {
  // Campos do formulário (controlados) e filtros efetivamente aplicados.
  const [dataCampo, setDataCampo] = useState(hojeISO())
  const [nivelCampo, setNivelCampo] = useState<string>('TODOS')

  const [data, setData] = useState(hojeISO())
  const [nivel, setNivel] = useState('TODOS')

  const {
    data: log,
    carregando,
    erro,
  } = useFetch<LogArquivo>(
    (signal) =>
      api.get('/admin/auditoria/logs', {
        params: { data: data || undefined, nivel },
        signal,
      }),
    [data, nivel],
  )

  function aplicarFiltros(e: React.FormEvent) {
    e.preventDefault()
    setData(dataCampo)
    setNivel(nivelCampo)
  }

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-journal-text" /> Auditoria de Logs
          </h2>
          <Link to="/admin/auditoria/registros" className="btn btn-outline-primary">
            <i className="bi bi-shield-check" /> Trilha de Auditoria Estruturada
          </Link>
        </div>

        <div className="alert alert-info mb-4">
          <i className="bi bi-info-circle" /> Visualize e filtre os logs do sistema por data e nível
          de severidade. Os logs são armazenados diariamente no formato{' '}
          <code>app.YYYY.MM.DD.log</code>.
        </div>

        {/* Filtros */}
        <div className="card shadow-sm mb-4">
          <div className="card-body">
            <form onSubmit={aplicarFiltros}>
              <div className="row g-3">
                <div className="col-md-4">
                  <label htmlFor="data" className="form-label">
                    Data do Log
                  </label>
                  <input
                    id="data"
                    type="date"
                    className="form-control"
                    value={dataCampo}
                    max={hojeISO()}
                    onChange={(e) => setDataCampo(e.target.value)}
                    required
                  />
                </div>
                <div className="col-md-4">
                  <label htmlFor="nivel" className="form-label">
                    Nível de Log
                  </label>
                  <select
                    id="nivel"
                    className="form-select"
                    value={nivelCampo}
                    onChange={(e) => setNivelCampo(e.target.value)}
                  >
                    {NIVEIS.map((n) => (
                      <option key={n} value={n}>
                        {n === 'TODOS' ? 'Todos os Níveis' : n}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-md-4 d-flex align-items-end">
                  <button type="submit" className="btn btn-primary w-100 py-3">
                    <i className="bi bi-search" /> Filtrar Logs
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>

        {/* Resultado dos Logs */}
        {carregando ? (
          <Spinner />
        ) : erro ? (
          <div className="alert alert-danger">{erro.message}</div>
        ) : log ? (
          <div className="card shadow-sm">
            <div className="card-header bg-primary text-white">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">
                  <i className="bi bi-file-text" /> Resultados
                </h5>
                <span className="badge bg-light text-primary">
                  {log.total_linhas} linha{log.total_linhas !== 1 ? 's' : ''} encontrada
                  {log.total_linhas !== 1 ? 's' : ''}
                </span>
              </div>
            </div>
            <div className="card-body p-0">
              {log.erro ? (
                <div className="alert alert-warning mb-0 rounded-0">
                  <i className="bi bi-exclamation-triangle" /> {log.erro}
                </div>
              ) : log.conteudo ? (
                <pre className="error-traceback overflow-auto font-monospace small mb-0 p-3">
                  {log.conteudo}
                </pre>
              ) : (
                <div className="alert alert-warning mb-0 rounded-0">
                  <i className="bi bi-exclamation-triangle" /> Nenhum log encontrado para os filtros
                  selecionados.
                </div>
              )}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
