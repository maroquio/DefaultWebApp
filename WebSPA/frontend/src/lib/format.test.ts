import { describe, it, expect } from 'vitest'
import { formatarMoeda, formatarBytes, formatarData, formatarDataHora, formatarHora } from './format'

describe('formatarMoeda', () => {
  it('formata em reais (BRL) com vírgula decimal', () => {
    expect(formatarMoeda(1234.5)).toBe('R$ 1.234,50')
    expect(formatarMoeda(0)).toBe('R$ 0,00')
  })
})

describe('formatarBytes', () => {
  it('escala B/KB/MB/GB', () => {
    expect(formatarBytes(512)).toBe('512 B')
    expect(formatarBytes(2048)).toBe('2.0 KB')
    expect(formatarBytes(5 * 1024 * 1024)).toBe('5.0 MB')
    expect(formatarBytes(3 * 1024 * 1024 * 1024)).toBe('3.0 GB')
  })
})

describe('formatadores de data', () => {
  it('retorna "-" para valores ausentes ou inválidos', () => {
    expect(formatarData(null)).toBe('-')
    expect(formatarData(undefined)).toBe('-')
    expect(formatarData('texto-invalido')).toBe('-')
    expect(formatarDataHora(null)).toBe('-')
    expect(formatarHora(null)).toBe('-')
  })

  it('formata uma data ISO no padrão brasileiro', () => {
    // 2026-06-18T15:30:00-03:00 -> America/Sao_Paulo
    expect(formatarData('2026-06-18T15:30:00-03:00')).toBe('18/06/2026')
    expect(formatarHora('2026-06-18T15:30:00-03:00')).toBe('15:30')
    expect(formatarDataHora('2026-06-18T15:30:00-03:00')).toBe('18/06/2026, 15:30')
  })
})
