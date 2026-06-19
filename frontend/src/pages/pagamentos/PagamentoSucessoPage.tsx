import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import type { Pagamento } from '../../lib/types'

type Fase = 'capturando' | 'aprovado' | 'erro'

/**
 * Página de retorno de checkout.
 *
 * Dois fluxos convivem nesta rota:
 *
 * 1. Retorno do PayPal — o PayPal redireciona com `?token=ORDER_ID&PayerID=...`
 *    (e `pagamento_id`, repassado via return_url). A aprovação no PayPal apenas
 *    AUTORIZA a cobrança; sem a captura o dinheiro não é transferido. Por isso,
 *    ao detectar `token` na URL, chamamos
 *    `POST /pagamentos/{id}/paypal/capturar?token=ORDER_ID` para efetivar.
 *
 * 2. Demais provedores (Mercado Pago / Stripe) — não há `token`; a confirmação
 *    de status é feita pelo webhook (fonte da verdade). Mantemos a página
 *    estática de sucesso.
 */
export default function PagamentoSucessoPage() {
  const [searchParams] = useSearchParams()

  // PayPal devolve o order_id em `token` e o pagador em `PayerID`.
  const token = searchParams.get('token')
  // O id do pagamento é repassado pela return_url do adapter PayPal.
  const pagamentoId = searchParams.get('pagamento_id') ?? searchParams.get('id')

  const ehRetornoPaypal = Boolean(token && pagamentoId)

  const [fase, setFase] = useState<Fase>(ehRetornoPaypal ? 'capturando' : 'aprovado')
  const [pagamento, setPagamento] = useState<Pagamento | null>(null)
  const [mensagemErro, setMensagemErro] = useState<string>('')

  // Evita captura duplicada (StrictMode monta o efeito duas vezes em dev).
  const capturaIniciada = useRef(false)

  useEffect(() => {
    if (!ehRetornoPaypal || !token || !pagamentoId) return
    if (capturaIniciada.current) return
    capturaIniciada.current = true

    async function capturar() {
      try {
        const resultado = await api.post<Pagamento>(
          `/pagamentos/${pagamentoId}/paypal/capturar`,
          undefined,
          { params: { token } },
        )
        setPagamento(resultado)
        setFase('aprovado')
      } catch (err) {
        if (err instanceof ApiError && err.status === 402) {
          // 402: o pagamento não foi concluído/aprovado no PayPal.
          setMensagemErro(
            err.message ||
              'O pagamento não foi concluído no PayPal. Nenhum valor foi cobrado.',
          )
        } else {
          setMensagemErro(
            err instanceof Error
              ? err.message
              : 'Não foi possível confirmar o pagamento. Tente novamente.',
          )
        }
        setFase('erro')
      }
    }

    void capturar()
  }, [ehRetornoPaypal, token, pagamentoId])

  if (fase === 'capturando') {
    return (
      <div className="row justify-content-center">
        <div className="col-12 col-lg-6 text-center py-5">
          <div className="mb-4">
            <div className="spinner-border text-primary" style={{ width: '4rem', height: '4rem' }}>
              <span className="visually-hidden">Confirmando pagamento...</span>
            </div>
          </div>
          <h1 className="mb-3">Confirmando pagamento...</h1>
          <p className="lead text-muted mb-0">
            Estamos finalizando a cobrança junto ao PayPal. Por favor, não feche esta página.
          </p>
        </div>
      </div>
    )
  }

  if (fase === 'erro') {
    return (
      <div className="row justify-content-center">
        <div className="col-12 col-lg-6 text-center py-5">
          <div className="mb-4">
            <i className="bi bi-x-circle-fill text-danger" style={{ fontSize: '5rem' }} />
          </div>

          <h1 className="text-danger mb-3">Pagamento não confirmado</h1>

          <p className="lead text-muted mb-4">{mensagemErro}</p>

          <div className="d-flex gap-3 justify-content-center flex-wrap">
            {pagamentoId && (
              <Link to={`/pagamentos/${pagamentoId}`} className="btn btn-primary">
                <i className="bi bi-receipt" /> Ver Pagamento
              </Link>
            )}
            <Link to="/pagamentos/listar" className="btn btn-outline-secondary">
              <i className="bi bi-list" /> Meus Pagamentos
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // fase === 'aprovado'
  return (
    <div className="row justify-content-center">
      <div className="col-12 col-lg-6 text-center py-5">
        <div className="mb-4">
          <i className="bi bi-check-circle-fill text-success" style={{ fontSize: '5rem' }} />
        </div>

        <h1 className="text-success mb-3">Pagamento Aprovado!</h1>

        <p className="lead text-muted mb-4">
          Seu pagamento foi processado com sucesso pelo gateway de pagamento.
        </p>

        <p className="text-muted mb-4">
          <i className="bi bi-bell" /> Você receberá uma notificação de confirmação em breve.
        </p>

        <div className="d-flex gap-3 justify-content-center flex-wrap">
          {pagamento ? (
            <Link to={`/pagamentos/${pagamento.id}`} className="btn btn-primary">
              <i className="bi bi-receipt" /> Ver Pagamento
            </Link>
          ) : (
            <Link to="/pagamentos/listar" className="btn btn-primary">
              <i className="bi bi-list" /> Meus Pagamentos
            </Link>
          )}
          <Link to="/dashboard" className="btn btn-outline-secondary">
            <i className="bi bi-house" /> Ir para o Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}
