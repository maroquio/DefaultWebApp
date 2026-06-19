import { Link, useParams } from 'react-router-dom'
import { api } from '../../lib/api'
import type { Pagamento } from '../../lib/types'
import { useFetch } from '../../hooks/useFetch'
import { formatarMoeda, formatarDataHora } from '../../lib/format'
import { StatusPagamentoBadge } from '../../components/ui/Badges'
import Spinner from '../../components/ui/Spinner'

export default function PagamentoDetalhesPage() {
  const { id } = useParams<{ id: string }>()
  const { data, carregando, erro } = useFetch<Pagamento>(
    (signal) => api.get(`/pagamentos/${id}`, { signal }),
    [id],
  )

  if (carregando) return <Spinner />

  if (erro || !data) {
    return (
      <div className="row justify-content-center">
        <div className="col-12 col-lg-8">
          <div className="alert alert-danger" role="alert">
            <i className="bi bi-exclamation-triangle" /> {erro?.message ?? 'Pagamento não encontrado.'}
          </div>
          <Link to="/pagamentos/listar" className="btn btn-outline-secondary btn-sm">
            <i className="bi bi-arrow-left" /> Voltar
          </Link>
        </div>
      </div>
    )
  }

  const pagamento = data

  return (
    <div className="row justify-content-center">
      <div className="col-12 col-lg-8">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-receipt" /> Pagamento #{pagamento.id}
          </h2>
          <Link to="/pagamentos/listar" className="btn btn-outline-secondary btn-sm">
            <i className="bi bi-arrow-left" /> Voltar
          </Link>
        </div>

        <div className="card shadow-sm">
          <div className="card-header d-flex justify-content-between align-items-center">
            <span className="fw-semibold">Informações do Pagamento</span>
            <StatusPagamentoBadge status={pagamento.status} />
          </div>
          <div className="card-body">
            <div className="row g-3">
              <div className="col-sm-6">
                <label className="text-muted small">Descrição</label>
                <p className="fw-semibold mb-0">{pagamento.descricao}</p>
              </div>
              <div className="col-sm-6">
                <label className="text-muted small">Valor</label>
                <p className="fw-bold text-success fs-5 mb-0">{formatarMoeda(pagamento.valor)}</p>
              </div>
              <div className="col-sm-6">
                <label className="text-muted small">Data de Criação</label>
                <p className="mb-0">{formatarDataHora(pagamento.data_criacao)}</p>
              </div>
              <div className="col-sm-6">
                <label className="text-muted small">Última Atualização</label>
                <p className="mb-0">{formatarDataHora(pagamento.data_atualizacao)}</p>
              </div>

              {pagamento.provider && (
                <div className="col-sm-6">
                  <label className="text-muted small">Provedor</label>
                  <p className="text-capitalize mb-0">{pagamento.provider}</p>
                </div>
              )}

              {pagamento.preference_id && (
                <div className="col-12">
                  <label className="text-muted small">ID da Sessão / Referência</label>
                  <p className="font-monospace small mb-0">{pagamento.preference_id}</p>
                </div>
              )}

              {pagamento.payment_id && (
                <div className="col-sm-6">
                  <label className="text-muted small">ID do Pagamento</label>
                  <p className="font-monospace small mb-0">{pagamento.payment_id}</p>
                </div>
              )}
            </div>
          </div>

          {(pagamento.status === 'Pendente' || pagamento.status === 'Em Processamento') &&
          pagamento.url_checkout ? (
            <div className="card-footer">
              <a href={pagamento.url_checkout} className="btn btn-warning">
                <i className="bi bi-credit-card" /> Continuar Pagamento
              </a>
              <span className="text-muted small ms-2">Clique para acessar o checkout</span>
            </div>
          ) : pagamento.status === 'Aprovado' ? (
            <div className="card-footer bg-success bg-opacity-10">
              <i className="bi bi-check-circle-fill text-success" />{' '}
              <span className="text-success fw-semibold">Pagamento aprovado com sucesso!</span>
            </div>
          ) : pagamento.status === 'Recusado' ? (
            <div className="card-footer bg-danger bg-opacity-10">
              <i className="bi bi-x-circle-fill text-danger" />{' '}
              <span className="text-danger fw-semibold">Pagamento não aprovado.</span>
              <Link to="/pagamentos/criar" className="btn btn-sm btn-outline-danger ms-2">
                Tentar novamente
              </Link>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
