import { Link } from 'react-router-dom'

export default function PagamentoPendentePage() {
  return (
    <div className="row justify-content-center">
      <div className="col-12 col-lg-6 text-center py-5">
        <div className="mb-4">
          <i className="bi bi-hourglass-split text-warning" style={{ fontSize: '5rem' }} />
        </div>

        <h1 className="text-warning mb-3">Pagamento em Análise</h1>

        <div className="alert alert-warning text-start mb-4">
          <i className="bi bi-info-circle" /> <strong>O que acontece agora?</strong>
          <ul className="mb-0 mt-2">
            <li>Seu pagamento está sendo analisado pelo gateway de pagamento</li>
            <li>Você receberá uma notificação quando o status for atualizado</li>
            <li>O prazo pode variar de alguns minutos a alguns dias úteis</li>
            <li>
              Dependendo da forma de pagamento escolhida, pode ser necessário realizar o pagamento
              (boleto, Pix, etc.)
            </li>
          </ul>
        </div>

        <div className="d-flex gap-3 justify-content-center flex-wrap">
          <Link to="/pagamentos/listar" className="btn btn-primary">
            <i className="bi bi-list" /> Meus Pagamentos
          </Link>
        </div>
      </div>
    </div>
  )
}
