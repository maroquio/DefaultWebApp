import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { z } from 'zod'
import { api, ApiError } from '../../lib/api'
import type { CriarPagamentoResultado } from '../../lib/types'
import { toast } from '../../store/uiStore'
import { TextField, SubmitButton } from '../../components/form/Field'

const schema = z.object({
  descricao: z
    .string()
    .trim()
    .min(5, 'A descrição deve ter ao menos 5 caracteres')
    .max(255, 'A descrição deve ter no máximo 255 caracteres'),
  valor: z
    .number({ message: 'Informe um valor válido' })
    .positive('O valor deve ser maior que zero')
    .max(999999.99, 'Valor máximo é R$ 999.999,99.'),
})

/** Converte string com vírgula ou ponto decimal em número (float). */
function parsearValor(texto: string): number {
  const normalizado = texto.trim().replace(/\./g, '').replace(',', '.')
  return Number(normalizado)
}

export default function PagamentoCriarPage() {
  const [descricao, setDescricao] = useState('')
  const [valor, setValor] = useState('')
  const [erros, setErros] = useState<Record<string, string[]>>({})
  const [enviando, setEnviando] = useState(false)

  const erro = (campo: string) => erros[campo]?.[0]

  async function aoEnviar(e: FormEvent) {
    e.preventDefault()
    setErros({})

    const parsed = schema.safeParse({ descricao: descricao.trim(), valor: parsearValor(valor) })
    if (!parsed.success) {
      setErros(parsed.error.flatten().fieldErrors)
      return
    }

    setEnviando(true)
    try {
      const resp = await api.post<CriarPagamentoResultado>('/pagamentos', {
        descricao: parsed.data.descricao,
        valor: parsed.data.valor,
      })
      // Redireciona para o checkout externo do gateway de pagamento.
      window.location.href = resp.init_point
    } catch (err) {
      if (err instanceof ApiError && err.errors) {
        setErros(err.errors)
      } else {
        toast.erro(err instanceof Error ? err.message : 'Falha ao criar o pagamento.')
      }
      setEnviando(false)
    }
  }

  return (
    <div className="row justify-content-center">
      <div className="col-12 col-lg-7">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-credit-card" /> Novo Pagamento
          </h2>
          <Link to="/pagamentos/listar" className="btn btn-outline-secondary btn-sm">
            <i className="bi bi-arrow-left" /> Voltar
          </Link>
        </div>

        <div className="alert alert-info mb-4">
          <i className="bi bi-shield-check" />{' '}
          <strong>Pagamento seguro via gateway de pagamento</strong>
          <p className="mb-0 mt-1 small">
            Após clicar em "Ir para Pagamento", você será redirecionado para a página segura do
            gateway de pagamento, onde poderá escolher sua forma de pagamento preferida.
          </p>
        </div>

        <div className="card shadow-sm">
          <form onSubmit={aoEnviar}>
            <div className="card-body p-4">
              <TextField
                label="Descrição"
                name="descricao"
                value={descricao}
                onChange={setDescricao}
                erro={erro('descricao')}
                ajuda="Descreva o item ou serviço sendo pago (5-255 caracteres)"
                placeholder="Ex: Plano Premium, Produto X, Serviço Y"
                maxLength={255}
                obrigatorio
              />

              <TextField
                label="Valor (R$)"
                name="valor"
                value={valor}
                onChange={setValor}
                erro={erro('valor')}
                ajuda="Valor em reais. Exemplo: 29,90 ou 150.00"
                placeholder="0,00"
                obrigatorio
              />
            </div>

            <div className="card-footer p-4">
              <div className="d-flex gap-3">
                <SubmitButton
                  carregando={enviando}
                  className="btn btn-success btn-lg"
                  icon="arrow-right-circle"
                >
                  Ir para Pagamento
                </SubmitButton>
                <Link to="/pagamentos/listar" className="btn btn-secondary">
                  <i className="bi bi-x-circle" /> Cancelar
                </Link>
              </div>
              <p className="text-muted small mt-3 mb-0">
                <i className="bi bi-lock" /> Seus dados estão protegidos com criptografia SSL.
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
