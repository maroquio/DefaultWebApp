import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import EmptyState from './EmptyState'

describe('EmptyState', () => {
  it('renderiza título, mensagem e filhos', () => {
    render(
      <EmptyState titulo="Nada aqui" mensagem="Lista vazia">
        <button>Adicionar</button>
      </EmptyState>,
    )
    expect(screen.getByText('Nada aqui')).toBeInTheDocument()
    expect(screen.getByText('Lista vazia')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Adicionar' })).toBeInTheDocument()
  })
})
