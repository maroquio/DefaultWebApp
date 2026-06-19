import { Link } from 'react-router-dom'

// Página 404 (espelha errors/404.html).
export default function NotFoundPage() {
  return (
    <div className="error-container text-center m-auto">
      <div className="error-code text-primary">404</div>
      <h2 className="mb-3">Página não encontrada</h2>
      <p className="text-muted mb-4">
        A página que você procura não existe ou foi movida.
      </p>
      <Link to="/" className="btn btn-primary">
        <i className="bi bi-house me-2" /> Voltar ao início
      </Link>
    </div>
  )
}
