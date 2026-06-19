import { Link, useParams } from 'react-router-dom'
import { api } from '../../../lib/api'
import type { DadosProvider } from '../../../lib/types'
import { useFetch } from '../../../hooks/useFetch'
import { formatarDataHora, formatarMoeda } from '../../../lib/format'
import { StatusPagamentoBadge } from '../../../components/ui/Badges'
import Spinner from '../../../components/ui/Spinner'

function formatarValorProvider(valor: unknown): string {
  if (valor === null || valor === undefined) return '—'
  if (typeof valor === 'object') return JSON.stringify(valor, null, 2)
  return String(valor)
}

export default function AdminPagamentoDetalhesPage() {
  const { id } = useParams<{ id: string }>()

  const { data, carregando, erro } = useFetch<DadosProvider>(
    (signal) => api.get(`/admin/pagamentos/${id}`, { signal }),
    [id],
  )

  if (carregando) return <Spinner />
  if (erro) return <div className="alert alert-danger">{erro.message}</div>
  if (!data) return <div className="alert alert-warning">Pagamento não encontrado.</div>

  const { pagamento, provider_nome, dados_provider } = data
  const entradasProvider = Object.entries(dados_provider ?? {})

  return (
    <div className="row">
      <div className="col-12 col-lg-8">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-receipt" /> Pagamento #{pagamento.id}
          </h2>
          <Link to="/admin/pagamentos" className="btn btn-outline-secondary btn-sm">
            <i className="bi bi-arrow-left" /> Voltar
          </Link>
        </div>

        {/* Dados do pagamento */}
        <div className="card shadow-sm mb-4">
          <div className="card-header d-flex justify-content-between align-items-center">
            <span className="fw-semibold">Dados do Pagamento</span>
            <StatusPagamentoBadge status={pagamento.status} />
          </div>
          <div className="card-body">
            <div className="row g-3">
              <div className="col-sm-6">
                <label className="text-muted small">Usuário</label>
                <p className="mb-0">
                  <small className="text-muted">ID: {pagamento.usuario_id}</small>
                </p>
              </div>
              <div className="col-sm-6">
                <label className="text-muted small">Descrição</label>
                <p className="fw-semibold mb-0">{pagamento.descricao}</p>
              </div>
              <div className="col-sm-6">
                <label className="text-muted small">Valor</label>
                <p className="fw-bold text-success fs-5 mb-0">{formatarMoeda(pagamento.valor)}</p>
              </div>
              <div className="col-sm-6">
                <label className="text-muted small">Provedor</label>
                <p className="mb-0">
                  <span className="badge bg-secondary">{provider_nome}</span>
                </p>
              </div>
              <div className="col-sm-6">
                <label className="text-muted small">Data de Criação</label>
                <p className="mb-0">{formatarDataHora(pagamento.data_criacao)}</p>
              </div>
              <div className="col-sm-6">
                <label className="text-muted small">Última Atualização</label>
                <p className="mb-0">{formatarDataHora(pagamento.data_atualizacao)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* IDs do provedor */}
        <div className="card shadow-sm mb-4">
          <div className="card-header">
            <span className="fw-semibold">
              <i className="bi bi-credit-card-2-front" /> IDs do {provider_nome}
            </span>
          </div>
          <div className="card-body">
            <div className="row g-3">
              <div className="col-12">
                <label className="text-muted small">Preference / Session ID</label>
                <p className="font-monospace small mb-0">{pagamento.preference_id || '—'}</p>
              </div>
              <div className="col-12">
                <label className="text-muted small">Payment ID</label>
                <p className="font-monospace small mb-0">{pagamento.payment_id || '—'}</p>
              </div>
              {pagamento.url_checkout && (
                <div className="col-12">
                  <label className="text-muted small">URL de Checkout</label>
                  <p className="mb-0">
                    <a
                      href={pagamento.url_checkout}
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-sm btn-outline-primary"
                    >
                      <i className="bi bi-box-arrow-up-right" /> Abrir Checkout
                    </a>
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Dados em tempo real do provedor */}
        {entradasProvider.length > 0 && (
          <div className="card shadow-sm">
            <div className="card-header">
              <span className="fw-semibold">
                <i className="bi bi-cloud-download" /> Dados do {provider_nome} (tempo real)
              </span>
            </div>
            <div className="card-body">
              <div className="table-responsive">
                <table className="table table-sm align-middle mb-0">
                  <tbody>
                    {entradasProvider.map(([chave, valor]) => (
                      <tr key={chave}>
                        <th scope="row" className="text-muted small text-nowrap">
                          {chave}
                        </th>
                        <td className="font-monospace small">
                          <pre className="mb-0" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                            {formatarValorProvider(valor)}
                          </pre>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
