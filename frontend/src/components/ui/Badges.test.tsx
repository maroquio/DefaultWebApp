import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import {
  StatusChamadoBadge,
  PrioridadeBadge,
  PerfilBadge,
  StatusPagamentoBadge,
  MensagensNaoLidasBadge,
} from './Badges'

describe('Badges', () => {
  it('StatusChamadoBadge mapeia cor por status', () => {
    const { rerender } = render(<StatusChamadoBadge status="Aberto" />)
    expect(screen.getByText('Aberto').className).toContain('bg-primary')
    rerender(<StatusChamadoBadge status="Resolvido" />)
    expect(screen.getByText('Resolvido').className).toContain('bg-success')
  })

  it('PrioridadeBadge: Urgente -> danger, Alta -> warning', () => {
    const { rerender } = render(<PrioridadeBadge prioridade="Urgente" />)
    expect(screen.getByText('Urgente').className).toContain('bg-danger')
    rerender(<PrioridadeBadge prioridade="Alta" />)
    expect(screen.getByText('Alta').className).toContain('bg-warning')
  })

  it('PerfilBadge: Administrador -> danger', () => {
    render(<PerfilBadge perfil="Administrador" />)
    expect(screen.getByText('Administrador').className).toContain('bg-danger')
  })

  it('StatusPagamentoBadge: Aprovado -> success', () => {
    render(<StatusPagamentoBadge status="Aprovado" />)
    expect(screen.getByText('Aprovado').className).toContain('bg-success')
  })

  it('MensagensNaoLidasBadge oculta quando count <= 0 e pluraliza', () => {
    const { container, rerender } = render(<MensagensNaoLidasBadge count={0} />)
    expect(container).toBeEmptyDOMElement()
    rerender(<MensagensNaoLidasBadge count={1} />)
    expect(screen.getByText(/1 não lida$/)).toBeInTheDocument()
    rerender(<MensagensNaoLidasBadge count={3} />)
    expect(screen.getByText(/3 não lidas$/)).toBeInTheDocument()
  })
})
