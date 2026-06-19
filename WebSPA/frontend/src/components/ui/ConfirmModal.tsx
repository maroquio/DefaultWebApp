import { useState } from 'react'
import { useUIStore } from '../../store/uiStore'

// Modal de confirmação global (substitui abrirModalConfirmacao do WebStandard).
// Disparado por useUIStore().pedirConfirmacao({ mensagem, onConfirmar, ... }).
export default function ConfirmModal() {
  const confirm = useUIStore((s) => s.confirm)
  const fechar = useUIStore((s) => s.fecharConfirmacao)
  const [processando, setProcessando] = useState(false)

  if (!confirm) return null

  const tipo = confirm.tipo ?? 'danger'
  const icone = tipo === 'danger' ? 'exclamation-triangle-fill' : 'exclamation-circle-fill'

  async function confirmar() {
    try {
      setProcessando(true)
      await confirm!.onConfirmar()
      fechar()
    } finally {
      setProcessando(false)
    }
  }

  return (
    <>
      <div className="modal fade show d-block" tabIndex={-1} role="dialog">
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            <div className={`modal-header text-bg-${tipo}`}>
              <h5 className="modal-title">
                <i className={`bi bi-${icone} me-2`} />
                {confirm.titulo ?? 'Confirmar ação'}
              </h5>
              <button
                type="button"
                className="btn-close btn-close-white"
                onClick={fechar}
                disabled={processando}
              />
            </div>
            <div className="modal-body">
              <p className="mb-0">{confirm.mensagem}</p>
              {confirm.detalhes && <p className="text-muted small mt-2 mb-0">{confirm.detalhes}</p>}
            </div>
            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={fechar}
                disabled={processando}
              >
                {confirm.textoCancelar ?? 'Cancelar'}
              </button>
              <button
                type="button"
                className={`btn btn-${tipo}`}
                onClick={confirmar}
                disabled={processando}
              >
                {processando && <span className="spinner-border spinner-border-sm me-2" />}
                {confirm.textoConfirmar ?? 'Confirmar'}
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="modal-backdrop fade show" />
    </>
  )
}
