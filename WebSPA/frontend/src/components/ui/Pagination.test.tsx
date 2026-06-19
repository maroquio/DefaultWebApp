import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import Pagination from './Pagination'

describe('Pagination', () => {
  it('não renderiza com uma única página', () => {
    const { container } = render(<Pagination pagina={1} totalPaginas={1} onPagina={() => {}} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('chama onPagina ao clicar em um número', () => {
    const onPagina = vi.fn()
    render(<Pagination pagina={2} totalPaginas={5} onPagina={onPagina} />)
    fireEvent.click(screen.getByRole('button', { name: '3' }))
    expect(onPagina).toHaveBeenCalledWith(3)
  })

  it('desabilita "Anterior" na primeira página', () => {
    render(<Pagination pagina={1} totalPaginas={5} onPagina={() => {}} />)
    expect(screen.getByRole('button', { name: /Anterior/ })).toBeDisabled()
    expect(screen.getByRole('button', { name: /Próxima/ })).toBeEnabled()
  })

  it('desabilita "Próxima" na última página', () => {
    render(<Pagination pagina={5} totalPaginas={5} onPagina={() => {}} />)
    expect(screen.getByRole('button', { name: /Próxima/ })).toBeDisabled()
  })
})
