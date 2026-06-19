import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../../lib/api'
import type { Chamado, PaginaResponse } from '../../../lib/types'
import { StatusChamado, PrioridadeChamado } from '../../../lib/types'
import { useFetch } from '../../../hooks/useFetch'
import {
  StatusChamadoBadge,
  PrioridadeBadge,
  MensagensNaoLidasBadge,
} from '../../../components/ui/Badges'
import Pagination from '../../../components/ui/Pagination'
import EmptyState from '../../../components/ui/EmptyState'
import Spinner from '../../../components/ui/Spinner'
import { formatarDataHora } from '../../../lib/format'

const POR_PAGINA = 10

export default function AdminChamadosListarPage() {
  // Campos do formulário (controlados) e filtros efetivamente aplicados.
  const [busca, setBusca] = useState('')
  const [statusFiltroCampo, setStatusFiltroCampo] = useState('')
  const [prioridadeCampo, setPrioridadeCampo] = useState('')

  const [q, setQ] = useState('')
  const [statusFiltro, setStatusFiltro] = useState('')
  const [prioridade, setPrioridade] = useState('')
  const [pagina, setPagina] = useState(1)

  const { data, carregando, erro } = useFetch<PaginaResponse<Chamado>>(
    (signal) =>
      api.get('/admin/chamados', {
        params: {
          pagina,
          por_pagina: POR_PAGINA,
          q: q || undefined,
          status_filtro: statusFiltro || undefined,
          prioridade: prioridade || undefined,
        },
        signal,
      }),
    [pagina, q, statusFiltro, prioridade],
  )

  function aplicarFiltros(e: React.FormEvent) {
    e.preventDefault()
    setQ(busca.trim())
    setStatusFiltro(statusFiltroCampo)
    setPrioridade(prioridadeCampo)
    setPagina(1)
  }

  function limparFiltros() {
    setBusca('')
    setStatusFiltroCampo('')
    setPrioridadeCampo('')
    setQ('')
    setStatusFiltro('')
    setPrioridade('')
    setPagina(1)
  }

  const chamados = data?.items ?? []

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-headset" /> Gerenciar Chamados
          </h2>
        </div>

        {/* Filtros */}
        <div className="card shadow-sm mb-4">
          <div className="card-body">
            <form onSubmit={aplicarFiltros}>
              <div className="row g-3 align-items-end">
                <div className="col-md-5">
                  <label htmlFor="busca" className="form-label">
                    Buscar
                  </label>
                  <input
                    id="busca"
                    type="text"
                    className="form-control"
                    placeholder="Título, usuário ou e-mail..."
                    value={busca}
                    onChange={(e) => setBusca(e.target.value)}
                  />
                </div>
                <div className="col-md-3">
                  <label htmlFor="statusFiltro" className="form-label">
                    Status
                  </label>
                  <select
                    id="statusFiltro"
                    className="form-select"
                    value={statusFiltroCampo}
                    onChange={(e) => setStatusFiltroCampo(e.target.value)}
                  >
                    <option value="">Todos</option>
                    {Object.values(StatusChamado).map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-md-2">
                  <label htmlFor="prioridade" className="form-label">
                    Prioridade
                  </label>
                  <select
                    id="prioridade"
                    className="form-select"
                    value={prioridadeCampo}
                    onChange={(e) => setPrioridadeCampo(e.target.value)}
                  >
                    <option value="">Todas</option>
                    {Object.values(PrioridadeChamado).map((p) => (
                      <option key={p} value={p}>
                        {p}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-md-2 d-flex gap-2">
                  <button type="submit" className="btn btn-primary flex-grow-1">
                    <i className="bi bi-search" /> Filtrar
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={limparFiltros}
                    title="Limpar filtros"
                  >
                    <i className="bi bi-x-lg" />
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>

        {carregando ? (
          <Spinner />
        ) : erro ? (
          <div className="alert alert-danger">{erro.message}</div>
        ) : chamados.length > 0 ? (
          <>
            <div className="card shadow-sm">
              <div className="card-body">
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0">
                    <thead className="table-light">
                      <tr>
                        <th scope="col">#</th>
                        <th scope="col">Título</th>
                        <th scope="col">Usuário</th>
                        <th scope="col">Status</th>
                        <th scope="col">Prioridade</th>
                        <th scope="col">Data Abertura</th>
                        <th scope="col" className="text-center">
                          Ações
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {chamados.map((chamado) => {
                        const nome = chamado.usuario_nome ?? '—'
                        return (
                          <tr key={chamado.id}>
                            <td>
                              <strong>#{chamado.id}</strong>
                            </td>
                            <td>
                              <div
                                className="text-truncate"
                                style={{ maxWidth: 300 }}
                                title={chamado.titulo}
                              >
                                {chamado.titulo}
                              </div>
                              {chamado.mensagens_nao_lidas ? (
                                <div className="mt-1">
                                  <MensagensNaoLidasBadge count={chamado.mensagens_nao_lidas} />
                                </div>
                              ) : null}
                            </td>
                            <td>
                              <div>{nome}</div>
                              {chamado.usuario_email && (
                                <small className="text-muted">{chamado.usuario_email}</small>
                              )}
                            </td>
                            <td>
                              <StatusChamadoBadge status={chamado.status} />
                            </td>
                            <td>
                              <PrioridadeBadge prioridade={chamado.prioridade} />
                            </td>
                            <td>{formatarDataHora(chamado.data_abertura)}</td>
                            <td className="text-center">
                              <Link
                                to={`/admin/chamados/${chamado.id}/responder`}
                                className="btn btn-sm btn-outline-primary"
                                title="Responder"
                                aria-label={`Responder chamado #${chamado.id}`}
                              >
                                <i className="bi bi-reply" /> Responder
                              </Link>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div className="mt-3">
              <small className="text-muted">Total: {data?.total ?? 0} chamado(s)</small>
            </div>

            <div className="mt-3">
              <Pagination
                pagina={pagina}
                totalPaginas={data?.total_paginas ?? 1}
                onPagina={setPagina}
              />
            </div>
          </>
        ) : (
          <EmptyState
            icon="headset"
            titulo="Nenhum chamado cadastrado"
            mensagem="Ainda não há chamados no sistema. Aguarde os usuários abrirem chamados de suporte."
          />
        )}
      </div>
    </div>
  )
}
