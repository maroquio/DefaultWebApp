import { describe, it, expect } from 'vitest'
import {
  apenasDigitos,
  mascararCpf,
  mascararTelefone,
  mascararMoeda,
  formatarNumeroComoMoedaInput,
  moedaParaNumero,
} from './masks'

describe('apenasDigitos', () => {
  it('remove tudo que não é dígito', () => {
    expect(apenasDigitos('(27) 99999-0000')).toBe('27999990000')
    expect(apenasDigitos('abc')).toBe('')
  })
})

describe('mascararCpf', () => {
  it('formata 000.000.000-00 e limita a 11 dígitos', () => {
    expect(mascararCpf('12345678901')).toBe('123.456.789-01')
    expect(mascararCpf('123456789012345')).toBe('123.456.789-01')
    expect(mascararCpf('123')).toBe('123')
  })
})

describe('mascararTelefone', () => {
  it('alterna entre fixo (10) e celular (11)', () => {
    expect(mascararTelefone('2733334444')).toBe('(27) 3333-4444')
    expect(mascararTelefone('27999990000')).toBe('(27) 99999-0000')
  })
})

describe('moeda', () => {
  it('mascararMoeda interpreta dígitos como centavos', () => {
    expect(mascararMoeda('123456')).toBe('1.234,56')
    expect(mascararMoeda('')).toBe('')
  })
  it('formatarNumeroComoMoedaInput formata sem prefixo', () => {
    expect(formatarNumeroComoMoedaInput(1234.56)).toBe('1.234,56')
  })
  it('moedaParaNumero faz o caminho inverso', () => {
    expect(moedaParaNumero('R$ 1.234,56')).toBe(1234.56)
    expect(moedaParaNumero('')).toBe(0)
  })
})
