// Máscaras de ENTRADA (aplicadas enquanto o usuário digita).
//
// Responsabilidade separada de `format.ts` (que é SAÍDA/exibição):
//   - masks.ts  → onChange de campos controlados; máscara em tempo real.
//   - format.ts → formatarData/DataHora/Hora/Moeda/Bytes para exibir.
//
// Util 100% agnóstico de domínio (pt-BR). Em campos controlados, aplique
// `mascararX` no onChange e, ao montar o DTO, normalize com `apenasDigitos`
// (CPF/telefone) ou `moedaParaNumero` (valores monetários).

/** Remove tudo que não for dígito. */
export function apenasDigitos(valor: string): string {
  return valor.replace(/\D/g, '')
}

/** Máscara de CPF: 000.000.000-00 (limita a 11 dígitos). */
export function mascararCpf(valor: string): string {
  const d = apenasDigitos(valor).slice(0, 11)
  return d
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2')
}

/**
 * Máscara de telefone BR: (00) 0000-0000 (fixo) ou (00) 00000-0000 (celular).
 * Limita a 11 dígitos e alterna o formato conforme o comprimento.
 */
export function mascararTelefone(valor: string): string {
  const d = apenasDigitos(valor).slice(0, 11)
  if (d.length <= 10) {
    return d
      .replace(/(\d{2})(\d)/, '($1) $2')
      .replace(/(\d{4})(\d)/, '$1-$2')
  }
  return d
    .replace(/(\d{2})(\d)/, '($1) $2')
    .replace(/(\d{5})(\d)/, '$1-$2')
}

/**
 * Máscara de moeda BR enquanto digita: interpreta os dígitos como centavos
 * e devolve "1.234,56" (sem o prefixo "R$"). Use no onChange do input.
 */
export function mascararMoeda(valor: string): string {
  const d = apenasDigitos(valor)
  if (d === '') return ''
  const numero = Number(d) / 100
  return formatarNumeroComoMoedaInput(numero)
}

/** Formata um número como string de input monetário pt-BR ("1.234,56"). */
export function formatarNumeroComoMoedaInput(numero: number): string {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numero)
}

/**
 * Converte uma string monetária pt-BR ("1.234,56" ou "R$ 1.234,56") em número
 * (1234.56). Retorna 0 para entrada vazia/sem dígitos. Use ao montar o DTO.
 */
export function moedaParaNumero(valor: string): number {
  const d = apenasDigitos(valor)
  if (d === '') return 0
  return Number(d) / 100
}
