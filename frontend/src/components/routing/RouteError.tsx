import { Link, useRouteError, isRouteErrorResponse } from 'react-router-dom'

// errorElement da rota raiz: isola crashes de render para que um erro em uma
// página não derrube o app inteiro (white screen). Espelha errors/500.html.
export default function RouteError() {
  const error = useRouteError()

  let titulo = 'Algo deu errado'
  let detalhe = 'Ocorreu um erro inesperado ao renderizar esta página.'

  if (isRouteErrorResponse(error)) {
    titulo = `${error.status} ${error.statusText}`
    detalhe = typeof error.data === 'string' ? error.data : detalhe
  } else if (error instanceof Error) {
    detalhe = error.message
  }

  return (
    <div className="container">
      <div className="error-container text-center">
        <div className="error-code text-danger">
          <i className="bi bi-exclamation-triangle" />
        </div>
        <h2 className="mb-3">{titulo}</h2>
        <p className="text-muted mb-4">{detalhe}</p>
        <div className="d-flex gap-2 justify-content-center">
          <Link to="/" className="btn btn-primary">
            <i className="bi bi-house me-2" /> Início
          </Link>
          <button className="btn btn-outline-secondary" onClick={() => window.location.reload()}>
            <i className="bi bi-arrow-clockwise me-2" /> Recarregar
          </button>
        </div>
      </div>
    </div>
  )
}
