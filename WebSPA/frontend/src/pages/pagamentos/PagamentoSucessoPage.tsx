import { Link } from 'react-router-dom'

export default function PagamentoSucessoPage() {
  return (
    <div className="row justify-content-center">
      <div className="col-12 col-lg-6 text-center py-5">
        <div className="mb-4">
          <i className="bi bi-check-circle-fill text-success" style={{ fontSize: '5rem' }} />
        </div>

        <h1 className="text-success mb-3">Pagamento Aprovado!</h1>

        <p className="lead text-muted mb-4">
          Seu pagamento foi processado com sucesso pelo gateway de pagamento.
        </p>

        <p className="text-muted mb-4">
          <i className="bi bi-bell" /> Você receberá uma notificação de confirmação em breve.
        </p>

        <div className="d-flex gap-3 justify-content-center flex-wrap">
          <Link to="/pagamentos/listar" className="btn btn-primary">
            <i className="bi bi-list" /> Meus Pagamentos
          </Link>
          <Link to="/dashboard" className="btn btn-outline-secondary">
            <i className="bi bi-house" /> Ir para o Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}
