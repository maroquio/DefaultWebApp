// Paginação portada de templates/macros/paginacao.html.
export default function Pagination({
  pagina,
  totalPaginas,
  onPagina,
}: {
  pagina: number
  totalPaginas: number
  onPagina: (p: number) => void
}) {
  if (totalPaginas <= 1) return null

  const paginas: number[] = []
  const inicio = Math.max(1, pagina - 2)
  const fim = Math.min(totalPaginas, pagina + 2)
  for (let i = inicio; i <= fim; i++) paginas.push(i)

  return (
    <nav aria-label="Paginação">
      <ul className="pagination justify-content-center mb-0">
        <li className={`page-item ${pagina <= 1 ? 'disabled' : ''}`}>
          <button className="page-link" onClick={() => onPagina(pagina - 1)} disabled={pagina <= 1}>
            <i className="bi bi-chevron-left" /> Anterior
          </button>
        </li>
        {inicio > 1 && (
          <li className="page-item">
            <button className="page-link" onClick={() => onPagina(1)}>
              1
            </button>
          </li>
        )}
        {inicio > 2 && (
          <li className="page-item disabled">
            <span className="page-link">…</span>
          </li>
        )}
        {paginas.map((p) => (
          <li key={p} className={`page-item ${p === pagina ? 'active' : ''}`}>
            <button className="page-link" onClick={() => onPagina(p)}>
              {p}
            </button>
          </li>
        ))}
        {fim < totalPaginas - 1 && (
          <li className="page-item disabled">
            <span className="page-link">…</span>
          </li>
        )}
        {fim < totalPaginas && (
          <li className="page-item">
            <button className="page-link" onClick={() => onPagina(totalPaginas)}>
              {totalPaginas}
            </button>
          </li>
        )}
        <li className={`page-item ${pagina >= totalPaginas ? 'disabled' : ''}`}>
          <button
            className="page-link"
            onClick={() => onPagina(pagina + 1)}
            disabled={pagina >= totalPaginas}
          >
            Próxima <i className="bi bi-chevron-right" />
          </button>
        </li>
      </ul>
    </nav>
  )
}
