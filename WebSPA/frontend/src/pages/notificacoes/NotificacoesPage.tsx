import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import type { Notificacao, PaginaResponse, TipoNotificacao } from '../../lib/types'
import { useFetch } from '../../hooks/useFetch'
import { toast, useUIStore } from '../../store/uiStore'
import { formatarDataHora } from '../../lib/format'
import Spinner from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'
import Pagination from '../../components/ui/Pagination'

const TIPO_CLASSES: Record<TipoNotificacao, { cor: string; icone: string }> = {
  info: { cor: 'info', icone: 'bi-info-circle' },
  sucesso: { cor: 'success', icone: 'bi-check-circle' },
  aviso: { cor: 'warning', icone: 'bi-exclamation-triangle' },
  erro: { cor: 'danger', icone: 'bi-x-circle' },
}

function classesTipo(tipo: TipoNotificacao): { cor: string; icone: string } {
  return TIPO_CLASSES[tipo] ?? { cor: 'secondary', icone: 'bi-bell' }
}

export default function NotificacoesPage() {
  const [pagina, setPagina] = useState(1)
  const pedirConfirmacao = useUIStore((s) => s.pedirConfirmacao)

  const { data, carregando, erro, recarregar } = useFetch<PaginaResponse<Notificacao>>(
    (signal) => api.get('/notificacoes', { params: { pagina }, signal }),
    [pagina],
  )

  function tratarErro(e: unknown) {
    toast.erro(e instanceof ApiError ? e.message : (e as Error).message)
  }

  async function marcarComoLida(id: number) {
    try {
      await api.patch(`/notificacoes/${id}/lida`)
      recarregar()
    } catch (e) {
      tratarErro(e)
    }
  }

  async function marcarTodas() {
    try {
      await api.patch('/notificacoes/marcar-todas')
      toast.sucesso('Todas as notificações foram marcadas como lidas.')
      recarregar()
    } catch (e) {
      tratarErro(e)
    }
  }

  function excluir(id: number) {
    pedirConfirmacao({
      titulo: 'Excluir notificação',
      mensagem: 'Tem certeza que deseja excluir esta notificação?',
      tipo: 'danger',
      textoConfirmar: 'Excluir',
      onConfirmar: async () => {
        try {
          await api.delete(`/notificacoes/${id}`)
          toast.sucesso('Notificação excluída.')
          recarregar()
        } catch (e) {
          tratarErro(e)
        }
      },
    })
  }

  function excluirLidas() {
    pedirConfirmacao({
      titulo: 'Excluir lidas',
      mensagem: 'Tem certeza que deseja excluir todas as notificações lidas?',
      tipo: 'danger',
      textoConfirmar: 'Excluir lidas',
      onConfirmar: async () => {
        try {
          await api.delete('/notificacoes/lidas')
          toast.sucesso('Notificações lidas excluídas.')
          recarregar()
        } catch (e) {
          tratarErro(e)
        }
      },
    })
  }

  const notificacoes = data?.items ?? []

  return (
    <div className="row">
      <div className="col-lg-8 col-xl-7 mx-auto">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2>
              <i className="bi bi-bell" /> Minhas Notificações
            </h2>
            <p className="text-muted mb-0">Acompanhe alertas e avisos importantes</p>
          </div>
          {notificacoes.length > 0 && (
            <div className="d-flex gap-2">
              <button
                type="button"
                className="btn btn-outline-secondary btn-sm"
                onClick={marcarTodas}
              >
                <i className="bi bi-check2-all" /> Marcar todas como lidas
              </button>
              <button type="button" className="btn btn-outline-danger btn-sm" onClick={excluirLidas}>
                <i className="bi bi-trash" /> Excluir lidas
              </button>
            </div>
          )}
        </div>

        {carregando ? (
          <Spinner />
        ) : erro ? (
          <div className="alert alert-danger">{erro.message}</div>
        ) : notificacoes.length === 0 ? (
          <EmptyState
            icon="bell-slash"
            titulo="Nenhuma notificação"
            mensagem="Você não tem notificações no momento. Elas aparecerão aqui quando houver novidades."
          />
        ) : (
          <>
            <div className="list-group shadow-sm mb-3">
              {notificacoes.map((notif) => {
                const { cor, icone } = classesTipo(notif.tipo)
                return (
                  <div
                    key={notif.id}
                    className={`list-group-item list-group-item-action ${
                      !notif.lida ? `border-start border-${cor} border-3 bg-${cor}-subtle` : ''
                    }`}
                  >
                    <div className="d-flex align-items-start gap-3">
                      <div className="mt-1">
                        <i className={`bi ${icone} text-${cor} fs-5`} />
                      </div>

                      <div className="flex-grow-1">
                        <div className="d-flex justify-content-between align-items-center mb-1">
                          <h6 className={`mb-0 ${!notif.lida ? 'fw-bold' : ''}`}>
                            {notif.titulo}
                            {!notif.lida && (
                              <span
                                className={`badge bg-${cor} ms-1`}
                                style={{ fontSize: '0.6rem' }}
                              >
                                NOVA
                              </span>
                            )}
                          </h6>
                          <small className="text-muted">
                            {formatarDataHora(notif.data_criacao)}
                          </small>
                        </div>
                        <p className="mb-2 text-muted small">{notif.mensagem}</p>

                        <div className="d-flex gap-2">
                          {!notif.lida ? (
                            notif.url_acao ? (
                              <Link
                                to={notif.url_acao}
                                className={`btn btn-${cor} btn-sm`}
                                onClick={() => marcarComoLida(notif.id)}
                              >
                                <i className="bi bi-check2" /> Ver detalhes
                              </Link>
                            ) : (
                              <button
                                type="button"
                                className={`btn btn-${cor} btn-sm`}
                                onClick={() => marcarComoLida(notif.id)}
                              >
                                <i className="bi bi-check2" /> Marcar como lida
                              </button>
                            )
                          ) : (
                            notif.url_acao && (
                              <Link
                                to={notif.url_acao}
                                className={`btn btn-outline-${cor} btn-sm`}
                              >
                                <i className="bi bi-arrow-right" /> Ver detalhes
                              </Link>
                            )
                          )}

                          <button
                            type="button"
                            className="btn btn-outline-danger btn-sm"
                            onClick={() => excluir(notif.id)}
                          >
                            <i className="bi bi-trash" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            <Pagination
              pagina={data?.pagina ?? pagina}
              totalPaginas={data?.total_paginas ?? 1}
              onPagina={setPagina}
            />
          </>
        )}
      </div>
    </div>
  )
}
