import { Link } from 'react-router-dom'

export default function PagamentoFalhaPage() {
  return (
    <div className="row justify-content-center">
      <div className="col-12 col-lg-6 text-center py-5">
        <div className="mb-4">
          <i className="bi bi-x-circle-fill text-danger" style={{ fontSize: '5rem' }} />
        </div>

        <h1 className="text-danger mb-3">Pagamento Não Aprovado</h1>

        <div className="alert alert-danger text-start mb-4">
          <i className="bi bi-exclamation-triangle" /> <strong>Possíveis motivos:</strong>
          <ul className="mb-0 mt-2">
            <li>Dados do cartão incorretos</li>
            <li>Saldo insuficiente</li>
            <li>Cartão bloqueado para compras online</li>
            <li>Limite de crédito excedido</li>
          </ul>
        </div>

        <p className="text-muted mb-4">
          Você pode tentar novamente com outro método de pagamento.
        </p>

        <div className="d-flex gap-3 justify-content-center flex-wrap">
          <Link to="/pagamentos/criar" className="btn btn-success btn-lg">
            <i className="bi bi-arrow-repeat" /> Tentar Novamente
          </Link>
          <Link to="/pagamentos/listar" className="btn btn-outline-primary">
            <i className="bi bi-list" /> Meus Pagamentos
          </Link>
        </div>
      </div>
    </div>
  )
}
