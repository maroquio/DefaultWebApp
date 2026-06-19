import { useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../../../lib/api'
import type { PaginaResponse, Pagamento } from '../../../lib/types'
import { StatusPagamento } from '../../../lib/types'
import { useFetch } from '../../../hooks/useFetch'
import { formatarDataHora, formatarMoeda } from '../../../lib/format'
import { StatusPagamentoBadge } from '../../../components/ui/Badges'
import { SelectField } from '../../../components/form/Field'
import Pagination from '../../../components/ui/Pagination'
import EmptyState from '../../../components/ui/EmptyState'
import Spinner from '../../../components/ui/Spinner'

const POR_PAGINA = 10

export default function AdminPagamentosListarPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  const pagina = Number(searchParams.get('pagina')) || 1
  const statusFiltro = searchParams.get('status_filtro') ?? ''

  const { data, carregando, erro } = useFetch<PaginaResponse<Pagamento>>(
    (signal) =>
      api.get('/admin/pagamentos', {
        params: {
          pagina,
          por_pagina: POR_PAGINA,
          status_filtro: statusFiltro || undefined,
        },
        signal,
      }),
    [pagina, statusFiltro],
  )

  function atualizarParams(next: Record<string, string | number | undefined>) {
    const params: Record<string, string> = {}
    if (statusFiltro) params.status_filtro = statusFiltro
    if (pagina > 1) params.pagina = String(pagina)
    for (const [k, v] of Object.entries(next)) {
      if (v === undefined || v === '' || v === 0) delete params[k]
      else params[k] = String(v)
    }
    setSearchParams(params)
  }

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-credit-card" /> Gerenciar Pagamentos
          </h2>
        </div>

        <div className="card shadow-sm mb-4">
          <div className="card-body">
            <div className="row g-2 align-items-end">
              <div className="col-md-4">
                <SelectField
                  label="Filtrar por status"
                  name="status_filtro"
                  value={statusFiltro}
                  onChange={(v) => atualizarParams({ status_filtro: v || undefined, pagina: undefined })}
                  opcoes={Object.values(StatusPagamento).map((s) => ({ valor: s, rotulo: s }))}
                  placeholder="Todos os status"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="card shadow-sm">
          <div className="card-body">
            {carregando ? (
              <Spinner />
            ) : erro ? (
              <div className="alert alert-danger mb-0">{erro.message}</div>
            ) : !data || data.items.length === 0 ? (
              <EmptyState
                icon="credit-card"
                titulo="Nenhum pagamento encontrado"
                mensagem={
                  statusFiltro
                    ? `Não há pagamentos com status "${statusFiltro}".`
                    : 'Não há pagamentos.'
                }
              />
            ) : (
              <>
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0">
                    <thead className="table-light">
                      <tr>
                        <th scope="col">#</th>
                        <th scope="col">Usuário</th>
                        <th scope="col">Descrição</th>
                        <th scope="col">Valor</th>
                        <th scope="col">Status</th>
                        <th scope="col">Data</th>
                        <th scope="col" className="text-center">
                          Ações
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.items.map((pagamento) => (
                        <tr key={pagamento.id}>
                          <td className="text-muted small">{pagamento.id}</td>
                          <td>{pagamento.usuario_id}</td>
                          <td>
                            {pagamento.descricao}
                            {pagamento.payment_id && (
                              <>
                                <br />
                                <small className="text-muted font-monospace">
                                  {pagamento.payment_id}
                                </small>
                              </>
                            )}
                          </td>
                          <td className="fw-bold text-success">{formatarMoeda(pagamento.valor)}</td>
                          <td>
                            <StatusPagamentoBadge status={pagamento.status} />
                          </td>
                          <td>
                            <small className="text-muted">
                              {formatarDataHora(pagamento.data_criacao)}
                            </small>
                          </td>
                          <td className="text-center">
                            <button
                              type="button"
                              className="btn btn-sm btn-outline-primary"
                              title="Ver detalhes"
                              onClick={() => navigate(`/admin/pagamentos/${pagamento.id}`)}
                            >
                              <i className="bi bi-eye" /> Detalhes
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="d-flex justify-content-between align-items-center mt-3">
                  <small className="text-muted">Total: {data.total} pagamento(s)</small>
                  <Pagination
                    pagina={data.pagina}
                    totalPaginas={data.total_paginas}
                    onPagina={(p) => atualizarParams({ pagina: p })}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
