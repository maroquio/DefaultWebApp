// Indicador de carregamento centralizado.
export default function Spinner({ texto = 'Carregando...' }: { texto?: string }) {
  return (
    <div className="text-center py-5">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">{texto}</span>
      </div>
      {texto && <p className="text-muted mt-2 mb-0">{texto}</p>}
    </div>
  )
}
