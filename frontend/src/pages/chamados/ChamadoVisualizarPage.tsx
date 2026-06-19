import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { z } from 'zod'
import { api, ApiError } from '../../lib/api'
import type { Chamado, ChamadoInteracao, TipoInteracao } from '../../lib/types'
import { StatusChamado } from '../../lib/types'
import { useFetch } from '../../hooks/useFetch'
import { toast, useUIStore } from '../../store/uiStore'
import { StatusChamadoBadge, PrioridadeBadge } from '../../components/ui/Badges'
import { TextAreaField, SubmitButton } from '../../components/form/Field'
import Spinner from '../../components/ui/Spinner'
import { formatarDataHora } from '../../lib/format'

const schema = z.object({
  mensagem: z
    .string()
    .trim()
    .min(10, 'A mensagem deve ter no mínimo 10 caracteres.')
    .max(2000, 'A mensagem deve ter no máximo 2000 caracteres.'),
})

// O backend serializa `tipo` com os VALORES do enum (rótulos PT-BR), não os nomes.
const ROTULO_TIPO: Record<TipoInteracao, string> = {
  Abertura: 'Abertura',
  'Resposta do Usuário': 'Resposta do Usuário',
  'Resposta do Administrador': 'Resposta do Suporte',
}

function ehDoSuporte(tipo: TipoInteracao): boolean {
  return tipo === 'Resposta do Administrador'
}

export default function ChamadoVisualizarPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const pedirConfirmacao = useUIStore((s) => s.pedirConfirmacao)

  const [mensagem, setMensagem] = useState('')
  const [erroMensagem, setErroMensagem] = useState<string | undefined>()
  const [enviando, setEnviando] = useState(false)

  const { data, carregando, erro, recarregar } = useFetch<Chamado>(
    (signal) => api.get(`/chamados/${id}`, { signal }),
    [id],
  )

  async function responder(e: React.FormEvent) {
    e.preventDefault()
    setErroMensagem(undefined)

    const parsed = schema.safeParse({ mensagem })
    if (!parsed.success) {
      setErroMensagem(parsed.error.flatten().fieldErrors.mensagem?.[0])
      return
    }

    setEnviando(true)
    try {
      await api.post<Chamado>(`/chamados/${id}/interacoes`, parsed.data)
      toast.sucesso('Mensagem enviada com sucesso.')
      setMensagem('')
      recarregar()
    } catch (err) {
      if (err instanceof ApiError && err.errors) {
        setErroMensagem(err.campo('mensagem'))
      } else {
        toast.erro(err instanceof ApiError ? err.message : 'Erro ao enviar mensagem.')
      }
    } finally {
      setEnviando(false)
    }
  }

  function excluir(chamado: Chamado) {
    pedirConfirmacao({
      titulo: 'Excluir chamado',
      mensagem: `Tem certeza que deseja excluir o chamado #${chamado.id} - "${chamado.titulo}"?`,
      tipo: 'danger',
      textoConfirmar: 'Excluir',
      onConfirmar: async () => {
        try {
          await api.delete(`/chamados/${chamado.id}`)
          toast.sucesso('Chamado excluído com sucesso.')
          navigate('/chamados/listar')
        } catch (e) {
          toast.erro(e instanceof ApiError ? e.message : 'Erro ao excluir chamado.')
        }
      },
    })
  }

  if (carregando) return <Spinner />
  if (erro) return <div className="alert alert-danger">{erro.message}</div>
  if (!data) return <div className="alert alert-warning">Chamado não encontrado.</div>

  const chamado = data
  const interacoes: ChamadoInteracao[] = chamado.interacoes ?? []
  const fechado = chamado.status === StatusChamado.FECHADO
  const podeExcluir = chamado.status === StatusChamado.ABERTO && !chamado.tem_resposta_admin

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-ticket-detailed" /> Chamado #{chamado.id}
          </h2>
          <div className="d-flex gap-2">
            {podeExcluir && (
              <button type="button" className="btn btn-danger" onClick={() => excluir(chamado)}>
                <i className="bi bi-trash" /> Excluir
              </button>
            )}
            <Link to="/chamados/listar" className="btn btn-secondary">
              <i className="bi bi-arrow-left" /> Voltar
            </Link>
          </div>
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
            <div className="row">
              <div className="col-md-6 mb-3">
                <small className="text-muted d-block mb-1">
                  <i className="bi bi-calendar3" /> Data de Abertura
                </small>
                <strong>{formatarDataHora(chamado.data_abertura)}</strong>
              </div>
              {chamado.data_fechamento && (
                <div className="col-md-6 mb-3">
                  <small className="text-muted d-block mb-1">
                    <i className="bi bi-check2-circle" /> Data de Fechamento
                  </small>
                  <strong>{formatarDataHora(chamado.data_fechamento)}</strong>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Histórico de Interações */}
        <div className="card shadow-sm mb-4">
          <div className="card-header">
            <h5 className="mb-0">
              <i className="bi bi-chat-dots" /> Histórico de Mensagens
            </h5>
          </div>
          <div className="card-body">
            {interacoes.length > 0 ? (
              interacoes.map((interacao, idx) => {
                const suporte = ehDoSuporte(interacao.tipo)
                return (
                  <div
                    key={interacao.id}
                    className={`mb-4 pb-4 ${idx < interacoes.length - 1 ? 'border-bottom' : ''}`}
                  >
                    <div
                      className={`d-flex align-items-start gap-3 ${suporte ? 'flex-row-reverse text-end' : ''}`}
                    >
                      <div>
                        <div
                          className={`${suporte ? 'bg-success' : 'bg-primary'} text-white rounded-circle d-flex align-items-center justify-content-center`}
                          style={{ width: '45px', height: '45px' }}
                        >
                          <i className={`bi ${suporte ? 'bi-headset' : 'bi-person-fill'} fs-5`} />
                        </div>
                      </div>
                      <div className="flex-grow-1">
                        <div className="d-flex justify-content-between align-items-center mb-2">
                          <span
                            className={`badge ${suporte ? 'bg-success' : 'bg-secondary'}`}
                          >
                            {ROTULO_TIPO[interacao.tipo]}
                          </span>
                          <small className="text-muted text-nowrap ms-2">
                            <i className="bi bi-clock" />{' '}
                            {formatarDataHora(interacao.data_interacao)}
                          </small>
                        </div>
                        <div className="bg-light rounded p-3 text-start">
                          <p className="mb-0" style={{ whiteSpace: 'pre-wrap' }}>
                            {interacao.mensagem}
                          </p>
                        </div>
                        {interacao.status_resultante && (
                          <small className="text-muted d-block mt-2">
                            <i className="bi bi-arrow-right" /> Status:{' '}
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
        {fechado ? (
          <div className="alert alert-secondary mb-4" role="alert">
            <i className="bi bi-lock-fill" /> <strong>Chamado Fechado</strong>
            <p className="mb-0 mt-2">Este chamado foi fechado e não aceita mais mensagens.</p>
          </div>
        ) : (
          <div className="card shadow-sm mb-4">
            <div className="card-header bg-light">
              <h5 className="mb-0">
                <i className="bi bi-reply" /> Adicionar Mensagem
              </h5>
            </div>
            <div className="card-body">
              <form onSubmit={responder}>
                <TextAreaField
                  label="Sua Mensagem"
                  name="mensagem"
                  value={mensagem}
                  onChange={setMensagem}
                  erro={erroMensagem}
                  ajuda="Mínimo 10 caracteres, máximo 2000 caracteres"
                  placeholder="Digite sua mensagem..."
                  rows={5}
                  maxLength={2000}
                  obrigatorio
                />
                <div className="d-flex justify-content-end gap-2">
                  <Link to="/chamados/listar" className="btn btn-secondary">
                    Cancelar
                  </Link>
                  <SubmitButton carregando={enviando} className="btn btn-primary" icon="send">
                    Enviar Mensagem
                  </SubmitButton>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
