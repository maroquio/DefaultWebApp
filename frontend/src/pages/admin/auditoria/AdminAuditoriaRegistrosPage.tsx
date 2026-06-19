import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../../lib/api'
import type { AuditoriaRegistro, PaginaResponse } from '../../../lib/types'
import { useFetch } from '../../../hooks/useFetch'
import { Badge } from '../../../components/ui/Badges'
import Pagination from '../../../components/ui/Pagination'
import EmptyState from '../../../components/ui/EmptyState'
import Spinner from '../../../components/ui/Spinner'
import { formatarDataHora } from '../../../lib/format'

const ACOES = ['criar', 'atualizar', 'excluir', 'login', 'logout', 'exportar', 'restaurar'] as const

const ACAO_CORES: Record<string, string> = {
  criar: 'success',
  atualizar: 'primary',
  excluir: 'danger',
  login: 'info',
  logout: 'secondary',
  exportar: 'warning text-dark',
  restaurar: 'warning text-dark',
}

const ACAO_ICONES: Record<string, string> = {
  criar: 'plus',
  atualizar: 'pencil',
  excluir: 'trash',
  login: 'box-arrow-in-right',
  logout: 'box-arrow-right',
  exportar: 'download',
  restaurar: 'arrow-counterclockwise',
}

function titulo(s: string): string {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : s
}

export default function AdminAuditoriaRegistrosPage() {
  // Campos do formulário (controlados).
  const [acaoCampo, setAcaoCampo] = useState('')
  const [entidadeCampo, setEntidadeCampo] = useState('')
  const [dataInicioCampo, setDataInicioCampo] = useState('')
  const [dataFimCampo, setDataFimCampo] = useState('')

  // Filtros aplicados.
  const [acao, setAcao] = useState('')
  const [entidade, setEntidade] = useState('')
  const [dataInicio, setDataInicio] = useState('')
  const [dataFim, setDataFim] = useState('')
  const [pagina, setPagina] = useState(1)

  const { data, carregando, erro } = useFetch<PaginaResponse<AuditoriaRegistro>>(
    (signal) =>
      api.get('/admin/auditoria/registros', {
        params: {
          pagina,
          acao: acao || undefined,
          entidade: entidade || undefined,
          data_inicio: dataInicio || undefined,
          data_fim: dataFim || undefined,
        },
        signal,
      }),
    [pagina, acao, entidade, dataInicio, dataFim],
  )

  function aplicarFiltros(e: React.FormEvent) {
    e.preventDefault()
    setAcao(acaoCampo)
    setEntidade(entidadeCampo.trim())
    setDataInicio(dataInicioCampo)
    setDataFim(dataFimCampo)
    setPagina(1)
  }

  function limparFiltros() {
    setAcaoCampo('')
    setEntidadeCampo('')
    setDataInicioCampo('')
    setDataFimCampo('')
    setAcao('')
    setEntidade('')
    setDataInicio('')
    setDataFim('')
    setPagina(1)
  }

  const temFiltros = !!(acao || entidade || dataInicio || dataFim)
  const registros = data?.items ?? []

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2>
              <i className="bi bi-shield-check" /> Trilha de Auditoria
            </h2>
            <p className="text-muted mb-0">
              Registro estruturado de ações de negócio realizadas no sistema
            </p>
          </div>
          <Link to="/admin/auditoria" className="btn btn-outline-secondary">
            <i className="bi bi-file-text" /> Ver Log de Arquivo
          </Link>
        </div>

        {/* Filtros */}
        <div className="card shadow-sm mb-4">
          <div className="card-header">
            <h6 className="mb-0">
              <i className="bi bi-funnel" /> Filtros
            </h6>
          </div>
          <div className="card-body">
            <form onSubmit={aplicarFiltros}>
              <div className="row g-3">
                <div className="col-md-3">
                  <label htmlFor="acao" className="form-label">
                    Ação
                  </label>
                  <select
                    id="acao"
                    className="form-select"
                    value={acaoCampo}
                    onChange={(e) => setAcaoCampo(e.target.value)}
                  >
                    <option value="">Todas as ações</option>
                    {ACOES.map((a) => (
                      <option key={a} value={a}>
                        {titulo(a)}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-md-3">
                  <label htmlFor="entidade" className="form-label">
                    Entidade
                  </label>
                  <input
                    id="entidade"
                    type="text"
                    className="form-control"
                    placeholder="ex: usuario, produto"
                    value={entidadeCampo}
                    onChange={(e) => setEntidadeCampo(e.target.value)}
                  />
                </div>
                <div className="col-md-2">
                  <label htmlFor="data_inicio" className="form-label">
                    Data Início
                  </label>
                  <input
                    id="data_inicio"
                    type="date"
                    className="form-control"
                    value={dataInicioCampo}
                    onChange={(e) => setDataInicioCampo(e.target.value)}
                  />
                </div>
                <div className="col-md-2">
                  <label htmlFor="data_fim" className="form-label">
                    Data Fim
                  </label>
                  <input
                    id="data_fim"
                    type="date"
                    className="form-control"
                    value={dataFimCampo}
                    onChange={(e) => setDataFimCampo(e.target.value)}
                  />
                </div>
                <div className="col-md-2 d-flex align-items-end">
                  <button type="submit" className="btn btn-primary w-100">
                    <i className="bi bi-search" /> Filtrar
                  </button>
                </div>
              </div>
              {temFiltros && (
                <div className="mt-2">
                  <button
                    type="button"
                    className="btn btn-sm btn-outline-secondary"
                    onClick={limparFiltros}
                  >
                    <i className="bi bi-x-circle" /> Limpar filtros
                  </button>
                </div>
              )}
            </form>
          </div>
        </div>

        {/* Tabela de Registros */}
        {carregando ? (
          <Spinner />
        ) : erro ? (
          <div className="alert alert-danger">{erro.message}</div>
        ) : registros.length > 0 ? (
          <div className="card shadow-sm">
            <div className="card-header bg-primary text-white">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">
                  <i className="bi bi-list-check" /> Registros
                </h5>
                <span className="badge bg-light text-primary">
                  {data?.total ?? 0} registro(s)
                </span>
              </div>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th scope="col">ID</th>
                      <th scope="col">Ação</th>
                      <th scope="col">Entidade</th>
                      <th scope="col">ID Entidade</th>
                      <th scope="col">Usuário</th>
                      <th scope="col">Descrição</th>
                      <th scope="col">Data/Hora</th>
                    </tr>
                  </thead>
                  <tbody>
                    {registros.map((reg) => (
                      <tr key={reg.id}>
                        <td>
                          <strong>#{reg.id}</strong>
                        </td>
                        <td>
                          <Badge
                            texto={titulo(reg.acao)}
                            cor={ACAO_CORES[reg.acao] ?? 'secondary'}
                            icon={ACAO_ICONES[reg.acao] ?? 'gear'}
                          />
                        </td>
                        <td>
                          <code className="text-primary">{reg.entidade}</code>
                        </td>
                        <td>
                          {reg.entidade_id != null && reg.entidade_id !== '' ? (
                            <span className="badge bg-light text-dark border">
                              #{reg.entidade_id}
                            </span>
                          ) : (
                            <span className="text-muted">—</span>
                          )}
                        </td>
                        <td>
                          {reg.usuario_id != null ? (
                            <span className="badge bg-light text-dark border">
                              <i className="bi bi-person" /> {reg.usuario_id}
                            </span>
                          ) : (
                            <span className="text-muted small">Sistema</span>
                          )}
                        </td>
                        <td>
                          <small>{reg.descricao || '—'}</small>
                        </td>
                        <td>
                          <small className="text-muted">{formatarDataHora(reg.data_acao)}</small>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="p-3 border-top">
                <Pagination
                  pagina={pagina}
                  totalPaginas={data?.total_paginas ?? 1}
                  onPagina={setPagina}
                />
              </div>
            </div>
          </div>
        ) : (
          <EmptyState
            icon="shield-slash"
            titulo={temFiltros ? 'Nenhum registro encontrado' : 'Nenhuma ação registrada ainda'}
            mensagem={
              temFiltros
                ? 'Nenhum registro encontrado com os filtros aplicados.'
                : 'Ainda não há ações de negócio registradas na trilha de auditoria.'
            }
          />
        )}
      </div>
    </div>
  )
}
