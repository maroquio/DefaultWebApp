import { Link } from 'react-router-dom'
import { api } from '../../lib/api'
import type { Pagamento } from '../../lib/types'
import { useFetch } from '../../hooks/useFetch'
import { formatarMoeda, formatarDataHora } from '../../lib/format'
import { StatusPagamentoBadge } from '../../components/ui/Badges'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'

export default function PagamentosListarPage() {
  const { data, carregando, erro } = useFetch<Pagamento[]>(
    (signal) => api.get('/pagamentos', { signal }),
    [],
  )

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-credit-card" /> Meus Pagamentos
          </h2>
          <Link to="/pagamentos/criar" className="btn btn-success">
            <i className="bi bi-plus-circle" /> Novo Pagamento
          </Link>
        </div>

        {carregando && <Spinner />}

        {!carregando && erro && (
          <div className="alert alert-danger" role="alert">
            <i className="bi bi-exclamation-triangle" /> {erro.message}
          </div>
        )}

        {!carregando && !erro && data && data.length === 0 && (
          <EmptyState
            icon="credit-card"
            titulo="Nenhum pagamento encontrado"
            mensagem="Você ainda não realizou nenhum pagamento. Clique no botão abaixo para iniciar."
          >
            <Link to="/pagamentos/criar" className="btn btn-success">
              <i className="bi bi-plus-circle" /> Fazer Primeiro Pagamento
            </Link>
          </EmptyState>
        )}

        {!carregando && !erro && data && data.length > 0 && (
          <div className="card shadow-sm">
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>#</th>
                      <th>Descrição</th>
                      <th>Valor</th>
                      <th>Status</th>
                      <th>Data</th>
                      <th className="text-center">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.map((pagamento) => (
                      <tr key={pagamento.id}>
                        <td className="text-muted small">{pagamento.id}</td>
                        <td>
                          <span className="fw-semibold">{pagamento.descricao}</span>
                          {pagamento.payment_id && (
                            <>
                              <br />
                              <small className="text-muted font-monospace">
                                MP: {pagamento.payment_id}
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
                          <div className="d-flex justify-content-center gap-2">
                            <Link
                              to={`/pagamentos/${pagamento.id}`}
                              className="btn btn-sm btn-outline-primary"
                              title="Ver detalhes"
                            >
                              <i className="bi bi-eye" />
                            </Link>
                            {pagamento.url_checkout &&
                              (pagamento.status === 'Pendente' ||
                                pagamento.status === 'Em Processamento') && (
                                <a
                                  href={pagamento.url_checkout}
                                  className="btn btn-sm btn-warning"
                                  title="Continuar pagamento"
                                >
                                  <i className="bi bi-credit-card" /> Pagar
                                </a>
                              )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="card-footer text-muted small">
              Total: {data.length} pagamento(s)
              {(() => {
                const aprovados = data.filter((p) => p.status === 'Aprovado').length
                return aprovados > 0 ? ` | Aprovados: ${aprovados}` : ''
              })()}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
