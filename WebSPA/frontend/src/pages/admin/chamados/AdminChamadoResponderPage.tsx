import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { z } from 'zod'
import { api, ApiError } from '../../../lib/api'
import type { Chamado, ChamadoInteracao } from '../../../lib/types'
import { StatusChamado } from '../../../lib/types'
import { useFetch } from '../../../hooks/useFetch'
import { toast, useUIStore } from '../../../store/uiStore'
import { StatusChamadoBadge, PrioridadeBadge } from '../../../components/ui/Badges'
import { TextAreaField, SelectField, SubmitButton } from '../../../components/form/Field'
import Spinner from '../../../components/ui/Spinner'
import { formatarDataHora } from '../../../lib/format'

// O backend serializa campos extras não presentes nos tipos base; estendemos
// localmente para acessá-los com segurança.
type InteracaoAdmin = Omit<ChamadoInteracao, 'tipo'> & {
  // O backend serializa `tipo` como o rótulo em português (ex: "Resposta do Administrador").
  tipo: string
  usuario_nome?: string | null
  data_leitura?: string | null
}
type ChamadoAdmin = Omit<Chamado, 'interacoes'> & {
  usuario_nome?: string | null
  usuario_email?: string | null
  interacoes?: InteracaoAdmin[]
}

// Valor de `tipo` serializado para respostas do administrador.
const TIPO_RESPOSTA_ADMIN = 'Resposta do Administrador'

const respostaSchema = z.object({
  mensagem: z
    .string()
    .trim()
    .min(10, 'A mensagem deve ter no mínimo 10 caracteres.')
    .max(2000, 'A mensagem deve ter no máximo 2000 caracteres.'),
  status: z.string().min(1, 'Selecione o novo status.'),
})

export default function AdminChamadoResponderPage() {
  const { id } = useParams<{ id: string }>()
  const pedirConfirmacao = useUIStore((s) => s.pedirConfirmacao)

  const { data, carregando, erro, recarregar } = useFetch<ChamadoAdmin>(
    (signal) => api.get(`/admin/chamados/${id}`, { signal }),
    [id],
  )

  const [mensagem, setMensagem] = useState('')
  const [status, setStatus] = useState('')
  const [erros, setErros] = useState<Record<string, string[]>>({})
  const [enviando, setEnviando] = useState(false)
  const [alterandoStatus, setAlterandoStatus] = useState(false)

  // Quando o chamado carrega, alinha o status do form ao status atual (uma vez).
  const [statusInicializado, setStatusInicializado] = useState(false)
  if (data && !statusInicializado) {
    setStatus(data.status)
    setStatusInicializado(true)
  }

  async function enviar(e: React.FormEvent) {
    e.preventDefault()
    setErros({})
    const parsed = respostaSchema.safeParse({ mensagem, status })
    if (!parsed.success) {
      setErros(parsed.error.flatten().fieldErrors)
      return
    }
    setEnviando(true)
    try {
      await api.post(`/admin/chamados/${id}/interacoes`, {
        dto_mensagem: { mensagem: parsed.data.mensagem },
        dto_status: { status: parsed.data.status },
      })
      toast.sucesso('Resposta enviada com sucesso.')
      setMensagem('')
      recarregar()
    } catch (err) {
      if (err instanceof ApiError && err.errors) {
        // Erros do body aninhado podem vir prefixados; normaliza para 'mensagem'/'status'.
        const norm: Record<string, string[]> = {}
        for (const [campo, msgs] of Object.entries(err.errors)) {
          if (campo.includes('mensagem')) norm.mensagem = msgs
          else if (campo.includes('status')) norm.status = msgs
          else norm[campo] = msgs
        }
        setErros(norm)
      } else {
        toast.erro(err instanceof ApiError ? err.message : 'Erro ao enviar a resposta.')
      }
    } finally {
      setEnviando(false)
    }
  }

  function alterarStatusSemMensagem() {
    if (!data) return
    if (status === data.status) {
      toast.info('O status selecionado já é o status atual do chamado.')
      return
    }
    pedirConfirmacao({
      titulo: 'Alterar status',
      mensagem: `Alterar o status do chamado #${data.id} para "${status}" sem adicionar mensagem?`,
      tipo: 'warning',
      textoConfirmar: 'Alterar status',
      onConfirmar: async () => {
        setAlterandoStatus(true)
        try {
          await api.patch(`/admin/chamados/${id}/status`, { status })
          toast.sucesso('Status alterado com sucesso.')
          recarregar()
        } catch (err) {
          toast.erro(err instanceof ApiError ? err.message : 'Erro ao alterar o status.')
        } finally {
          setAlterandoStatus(false)
        }
      },
    })
  }

  if (carregando) return <Spinner />
  if (erro) return <div className="alert alert-danger">{erro.message}</div>
  if (!data) return null

  const chamado = data
  const interacoes = chamado.interacoes ?? []
  const nome = chamado.usuario_nome ?? chamado.nome_usuario ?? '-'
  const fechado = chamado.status === StatusChamado.FECHADO

  const opcoesStatus = Object.values(StatusChamado).map((s) => ({ valor: s, rotulo: s }))

  return (
    <div className="row">
      <div className="col-12">
        {/* Cabeçalho */}
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-reply-fill" /> Responder Chamado #{chamado.id}
          </h2>
          <Link to="/admin/chamados/listar" className="btn btn-secondary">
            <i className="bi bi-arrow-left" /> Voltar
          </Link>
        </div>

        {/* Card Principal */}
        <div className="card shadow-sm mb-4">
          <div className="card-header bg-primary text-white">
            <div className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">{chamado.titulo}</h5>
              <div className="d-flex gap-2">
                <StatusChamadoBadge status={chamado.status} />
                <PrioridadeBadge prioridade={chamado.prioridade} />
              </div>
            </div>
          </div>
          <div className="card-body">
            <div className="row mb-0">
              <div className="col-md-6">
                <small className="text-muted d-block mb-1">
                  <i className="bi bi-person" /> Usuário
                </small>
                <strong>{nome}</strong>
                {chamado.usuario_email && (
                  <>
                    <br />
                    <small className="text-muted">{chamado.usuario_email}</small>
                  </>
                )}
              </div>
              <div className="col-md-6">
                <small className="text-muted d-block mb-1">
                  <i className="bi bi-calendar3" /> Data de Abertura
                </small>
                <strong>{formatarDataHora(chamado.data_abertura)}</strong>
              </div>
            </div>
          </div>
        </div>

        {/* Histórico de Interações */}
        <div className="card shadow-sm mb-4">
          <div className="card-header bg-light">
            <h5 className="mb-0">
              <i className="bi bi-chat-dots" /> Histórico de Mensagens
            </h5>
          </div>
          <div className="card-body">
            {interacoes.length > 0 ? (
              interacoes.map((interacao, idx) => {
                const ehAdmin = interacao.tipo === TIPO_RESPOSTA_ADMIN
                return (
                  <div
                    key={interacao.id}
                    className={`mb-4 pb-4 ${idx < interacoes.length - 1 ? 'border-bottom' : ''}`}
                  >
                    <div className="d-flex align-items-start gap-3">
                      <div>
                        <div
                          className={`${ehAdmin ? 'bg-success' : 'bg-primary'} text-white rounded-circle d-flex align-items-center justify-content-center`}
                          style={{ width: 45, height: 45 }}
                        >
                          <i className={`bi ${ehAdmin ? 'bi-headset' : 'bi-person-fill'} fs-5`} />
                        </div>
                      </div>
                      <div className="flex-grow-1">
                        <div className="d-flex justify-content-between align-items-center mb-2">
                          <div>
                            <strong>{interacao.usuario_nome ?? (ehAdmin ? 'Administrador' : 'Usuário')}</strong>
                            <span className="badge bg-secondary ms-2">{interacao.tipo}</span>
                          </div>
                          {interacao.data_interacao && (
                            <small className="text-muted text-nowrap ms-2">
                              <i className="bi bi-clock" /> {formatarDataHora(interacao.data_interacao)}
                            </small>
                          )}
                        </div>
                        <div className="bg-light rounded p-3">
                          <p className="mb-0" style={{ whiteSpace: 'pre-wrap' }}>
                            {interacao.mensagem}
                          </p>
                        </div>
                        {interacao.status_resultante && (
                          <small className="text-muted d-block mt-2">
                            <i className="bi bi-arrow-right" /> Status alterado para:{' '}
                            <strong>{interacao.status_resultante}</strong>
                          </small>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })
            ) : (
              <p className="text-muted mb-0">Nenhuma mensagem registrada.</p>
            )}
          </div>
        </div>

        {/* Formulário de Resposta */}
        {!fechado ? (
          <div className="card shadow-sm mb-4">
            <div className="card-header bg-success text-white">
              <h5 className="mb-0">
                <i className="bi bi-reply-fill" /> Adicionar Resposta
              </h5>
            </div>
            <div className="card-body">
              <form onSubmit={enviar}>
                <TextAreaField
                  label="Mensagem"
                  name="mensagem"
                  value={mensagem}
                  onChange={setMensagem}
                  rows={5}
                  obrigatorio
                  placeholder="Digite sua resposta ao usuário..."
                  ajuda="Mínimo 10 caracteres, máximo 2000 caracteres"
                  maxLength={2000}
                  erro={erros.mensagem?.[0]}
                />

                <SelectField
                  label="Novo Status"
                  name="status"
                  value={status}
                  onChange={setStatus}
                  opcoes={opcoesStatus}
                  obrigatorio
                  ajuda="Selecione o status após sua resposta"
                  erro={erros.status?.[0]}
                />

                <div className="d-flex justify-content-end gap-2">
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={alterarStatusSemMensagem}
                    disabled={alterandoStatus || enviando}
                  >
                    {alterandoStatus ? (
                      <span className="spinner-border spinner-border-sm me-2" />
                    ) : (
                      <i className="bi bi-arrow-repeat me-2" />
                    )}
                    Só alterar status
                  </button>
                  <Link to="/admin/chamados/listar" className="btn btn-secondary">
                    Cancelar
                  </Link>
                  <SubmitButton carregando={enviando} className="btn btn-success" icon="send">
                    Enviar Resposta
                  </SubmitButton>
                </div>
              </form>
            </div>
          </div>
        ) : (
          <div className="alert alert-secondary mb-4" role="alert">
            <i className="bi bi-lock-fill" /> <strong>Chamado Fechado</strong>
            <p className="mb-0 mt-2">Este chamado foi fechado e não aceita mais respostas.</p>
            <div className="mt-3 d-flex align-items-end gap-2">
              <div style={{ minWidth: 220 }}>
                <SelectField
                  label="Reabrir como"
                  name="status_reabrir"
                  value={status}
                  onChange={setStatus}
                  opcoes={opcoesStatus}
                />
              </div>
              <button
                type="button"
                className="btn btn-success mb-3"
                onClick={alterarStatusSemMensagem}
                disabled={alterandoStatus}
              >
                {alterandoStatus ? (
                  <span className="spinner-border spinner-border-sm me-2" />
                ) : (
                  <i className="bi bi-arrow-counterclockwise me-2" />
                )}
                Alterar status
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
