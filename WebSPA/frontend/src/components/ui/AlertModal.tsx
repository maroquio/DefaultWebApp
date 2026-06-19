import { useUIStore } from '../../store/uiStore'

const ICONES: Record<string, string> = {
  danger: 'exclamation-triangle-fill',
  warning: 'exclamation-circle-fill',
  info: 'info-circle-fill',
  success: 'check-circle-fill',
}

// Modal de alerta global (substitui window.App.Modal do WebStandard).
export default function AlertModal() {
  const alert = useUIStore((s) => s.alert)
  const fechar = useUIStore((s) => s.fecharAlerta)
  if (!alert) return null

  const tipo = alert.tipo ?? 'info'

  return (
    <>
      <div className="modal fade show d-block" tabIndex={-1} role="dialog">
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            <div className={`modal-header text-bg-${tipo}`}>
              <h5 className="modal-title">
                <i className={`bi bi-${ICONES[tipo]} me-2`} />
                {alert.titulo ?? 'Aviso'}
              </h5>
              <button type="button" className="btn-close btn-close-white" onClick={fechar} />
            </div>
            <div className="modal-body">
              <p className="mb-0">{alert.mensagem}</p>
              {alert.detalhes && <p className="text-muted small mt-2 mb-0">{alert.detalhes}</p>}
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={fechar}>
                Fechar
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="modal-backdrop fade show" />
    </>
  )
}
