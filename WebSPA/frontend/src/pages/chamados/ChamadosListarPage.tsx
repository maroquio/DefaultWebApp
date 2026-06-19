import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import type { Chamado, PaginaResponse } from '../../lib/types'
import { StatusChamado, PrioridadeChamado } from '../../lib/types'
import { useFetch } from '../../hooks/useFetch'
import { toast, useUIStore } from '../../store/uiStore'
import {
  StatusChamadoBadge,
  PrioridadeBadge,
  MensagensNaoLidasBadge,
} from '../../components/ui/Badges'
import Pagination from '../../components/ui/Pagination'
import EmptyState from '../../components/ui/EmptyState'
import Spinner from '../../components/ui/Spinner'
import { formatarDataHora } from '../../lib/format'

const POR_PAGINA = 10

export default function ChamadosListarPage() {
  const navigate = useNavigate()
  const pedirConfirmacao = useUIStore((s) => s.pedirConfirmacao)

  // Campos do formulário de filtro (controlados) e filtros efetivamente aplicados.
  const [busca, setBusca] = useState('')
  const [statusFiltro, setStatusFiltro] = useState('')
  const [prioridade, setPrioridade] = useState('')

  const [q, setQ] = useState('')
  const [status, setStatus] = useState('')
  const [prioridadeAplicada, setPrioridadeAplicada] = useState('')
  const [pagina, setPagina] = useState(1)

  const { data, carregando, erro, recarregar } = useFetch<PaginaResponse<Chamado>>(
    (signal) =>
      api.get('/chamados', {
        params: {
          pagina,
          por_pagina: POR_PAGINA,
          q: q || undefined,
          status_filtro: status || undefined,
          prioridade: prioridadeAplicada || undefined,
        },
        signal,
      }),
    [pagina, q, status, prioridadeAplicada],
  )

  function aplicarFiltros(e: React.FormEvent) {
    e.preventDefault()
    setQ(busca.trim())
    setStatus(statusFiltro)
    setPrioridadeAplicada(prioridade)
    setPagina(1)
  }

  function limparFiltros() {
    setBusca('')
    setStatusFiltro('')
    setPrioridade('')
    setQ('')
    setStatus('')
    setPrioridadeAplicada('')
    setPagina(1)
  }

  function excluir(chamado: Chamado) {
    pedirConfirmacao({
      titulo: 'Excluir chamado',
      mensagem: `Tem certeza que deseja excluir o chamado #${chamado.id} - "${chamado.titulo}"?`,
      tipo: 'danger',
      textoConfirmar: 'Excluir',
      onConfirmar: async () => {
        try {
          await api.delete(`/chamados/${chamado.id}`)
          toast.sucesso('Chamado excluído com sucesso.')
          recarregar()
        } catch (e) {
          toast.erro(e instanceof ApiError ? e.message : 'Erro ao excluir chamado.')
        }
      },
    })
  }

  const chamados = data?.items ?? []

  return (
    <div className="row">
      <div className="col-md-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-headset" /> Meus Chamados
          </h2>
          <Link to="/chamados/cadastrar" className="btn btn-success">
            <i className="bi bi-plus-circle" /> Abrir Chamado
          </Link>
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
                    placeholder="Título ou descrição..."
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
                    value={statusFiltro}
                    onChange={(e) => setStatusFiltro(e.target.value)}
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
                    value={prioridade}
                    onChange={(e) => setPrioridade(e.target.value)}
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
                <div className="list-group list-group-flush">
                  {chamados.map((chamado) => {
                    const podeExcluir =
                      chamado.status === StatusChamado.ABERTO && !chamado.tem_resposta_admin
                    return (
                      <div className="list-group-item" key={chamado.id}>
                        <div className="d-flex justify-content-between align-items-start">
                          <div className="flex-grow-1">
                            <div className="d-flex align-items-center gap-2 mb-2 flex-wrap">
                              <h5 className="mb-0">
                                <i className="bi bi-ticket-detailed" /> #{chamado.id} -{' '}
                                {chamado.titulo}
                              </h5>
                              <StatusChamadoBadge status={chamado.status} />
                              <PrioridadeBadge prioridade={chamado.prioridade} />
                              <MensagensNaoLidasBadge count={chamado.mensagens_nao_lidas ?? 0} />
                            </div>
                            <small className="text-muted">
                              <i className="bi bi-calendar3" /> Aberto em:{' '}
                              {formatarDataHora(chamado.data_abertura)}
                              {chamado.data_fechamento && (
                                <>
                                  {' '}
                                  | <i className="bi bi-check2-circle" /> Fechado em:{' '}
                                  {formatarDataHora(chamado.data_fechamento)}
                                </>
                              )}
                            </small>
                          </div>
                          <div className="d-flex gap-2 ms-3">
                            <Link
                              to={`/chamados/${chamado.id}/visualizar`}
                              className="btn btn-sm btn-primary"
                              title="Ver detalhes"
                            >
                              <i className="bi bi-eye" /> Detalhes
                            </Link>
                            {podeExcluir && (
                              <button
                                type="button"
                                className="btn btn-sm btn-danger"
                                title="Excluir chamado"
                                onClick={() => excluir(chamado)}
                              >
                                <i className="bi bi-trash" />
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>

            <div className="mt-3 d-flex justify-content-between align-items-center">
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
            titulo="Nenhum chamado encontrado"
            mensagem="Você ainda não abriu nenhum chamado. Clique no botão abaixo para começar!"
          >
            <button
              type="button"
              className="btn btn-success"
              onClick={() => navigate('/chamados/cadastrar')}
            >
              <i className="bi bi-plus-circle" /> Abrir Primeiro Chamado
            </button>
          </EmptyState>
        )}
      </div>
    </div>
  )
}
