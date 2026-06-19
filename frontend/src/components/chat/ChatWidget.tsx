// Widget de chat flutuante em tempo real (SSE). Réplica do
// WebStandard/templates/components/chat_widget.html + widget-chat.js.
import { useCallback, useEffect, useRef, useState } from 'react'
import { api, ApiError } from '../../lib/api'
import type { ChatMensagem, ChatSala, Conversa, UsuarioBusca } from '../../lib/types'
import { formatarHora } from '../../lib/format'
import { useAuthStore } from '../../store/authStore'
import { toast } from '../../store/uiStore'

// Evento recebido pelo EventSource (ver chat_routes.enviar_mensagem / marcar_como_lidas).
// O backend emite `sala_id` como string (formato "menor_id_maior_id") e o payload
// da mensagem traz `data_envio` e `lida_em` possivelmente nulos.
interface EventoSSE {
  tipo: 'nova_mensagem' | 'atualizar_contador'
  sala_id: string
  mensagem?: ChatMensagem
}

export default function ChatWidget() {
  const usuario = useAuthStore((s) => s.usuario)

  const [aberto, setAberto] = useState(false)
  const [totalNaoLidas, setTotalNaoLidas] = useState(0)

  const [conversas, setConversas] = useState<Conversa[]>([])
  const [salaAtual, setSalaAtual] = useState<string | null>(null)
  const [nomeOutro, setNomeOutro] = useState<string>('')
  const [mensagens, setMensagens] = useState<ChatMensagem[]>([])
  const [carregandoMensagens, setCarregandoMensagens] = useState(false)

  const [busca, setBusca] = useState('')
  const [sugestoes, setSugestoes] = useState<UsuarioBusca[]>([])

  const [texto, setTexto] = useState('')
  const [enviando, setEnviando] = useState(false)

  // Refs para acesso atualizado dentro do handler do EventSource.
  const salaAtualRef = useRef<string | null>(null)
  const abertoRef = useRef(false)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)
  const buscaDebounce = useRef<ReturnType<typeof setTimeout> | null>(null)

  salaAtualRef.current = salaAtual
  abertoRef.current = aberto

  // ===== Carregamento de dados =====

  const carregarTotalNaoLidas = useCallback(async (signal?: AbortSignal) => {
    try {
      const { total } = await api.get<{ total: number }>('/chat/mensagens/nao-lidas/total', {
        signal,
      })
      setTotalNaoLidas(total)
    } catch (e) {
      if ((e as Error).name !== 'AbortError') {
        // Silencioso: contador é secundário.
      }
    }
  }, [])

  const carregarConversas = useCallback(async (signal?: AbortSignal) => {
    try {
      const lista = await api.get<Conversa[]>('/chat/conversas', {
        params: { limit: 50, offset: 0 },
        signal,
      })
      setConversas(lista)
    } catch (e) {
      if ((e as Error).name !== 'AbortError') {
        toast.erro(e instanceof ApiError ? e.message : 'Falha ao carregar conversas.')
      }
    }
  }, [])

  const marcarLidas = useCallback(
    async (salaId: string) => {
      try {
        await api.post(`/chat/mensagens/lidas/${salaId}`)
        setConversas((cs) =>
          cs.map((c) => (c.sala_id === salaId ? { ...c, nao_lidas: 0 } : c)),
        )
        await carregarTotalNaoLidas()
      } catch {
        // Silencioso.
      }
    },
    [carregarTotalNaoLidas],
  )

  const abrirSala = useCallback(
    async (salaId: string, nome: string) => {
      setSalaAtual(salaId)
      setNomeOutro(nome)
      setMensagens([])
      setSugestoes([])
      setBusca('')
      setCarregandoMensagens(true)
      try {
        const msgs = await api.get<ChatMensagem[]>(`/chat/mensagens/${salaId}`, {
          params: { limit: 50, offset: 0 },
        })
        setMensagens(msgs)
        await marcarLidas(salaId)
      } catch (e) {
        toast.erro(e instanceof ApiError ? e.message : 'Falha ao carregar mensagens.')
      } finally {
        setCarregandoMensagens(false)
      }
    },
    [marcarLidas],
  )

  // ===== EventSource (SSE) =====

  useEffect(() => {
    if (!usuario) return
    const es = new EventSource('/api/chat/stream')

    es.onmessage = (e: MessageEvent<string>) => {
      let evento: EventoSSE
      try {
        evento = JSON.parse(e.data) as EventoSSE
      } catch {
        return
      }

      if (evento.tipo === 'nova_mensagem' && evento.mensagem) {
        const msg = evento.mensagem
        const salaId = evento.sala_id
        const ehDaSalaAberta = abertoRef.current && salaAtualRef.current === salaId

        if (ehDaSalaAberta) {
          setMensagens((prev) =>
            prev.some((m) => m.id === msg.id) ? prev : [...prev, msg],
          )
          // Mensagem do outro chegou na sala aberta: marca como lida.
          if (msg.usuario_id !== usuario.id) {
            void marcarLidas(salaId)
          }
        }
        void carregarConversas()
        void carregarTotalNaoLidas()
      } else if (evento.tipo === 'atualizar_contador') {
        void carregarConversas()
        void carregarTotalNaoLidas()
      }
    }

    es.onerror = () => {
      // O browser reconecta automaticamente.
    }

    return () => {
      es.close()
    }
  }, [usuario, carregarConversas, carregarTotalNaoLidas, marcarLidas])

  // Carga inicial do contador (mesmo com o painel fechado).
  useEffect(() => {
    if (!usuario) return
    const ctrl = new AbortController()
    void carregarTotalNaoLidas(ctrl.signal)
    return () => ctrl.abort()
  }, [usuario, carregarTotalNaoLidas])

  // Ao abrir o painel, carrega conversas.
  useEffect(() => {
    if (!aberto || !usuario) return
    const ctrl = new AbortController()
    void carregarConversas(ctrl.signal)
    return () => ctrl.abort()
  }, [aberto, usuario, carregarConversas])

  // Busca de usuários com debounce.
  useEffect(() => {
    if (buscaDebounce.current) clearTimeout(buscaDebounce.current)
    if (busca.trim().length < 2) {
      setSugestoes([])
      return
    }
    buscaDebounce.current = setTimeout(async () => {
      try {
        const res = await api.get<UsuarioBusca[]>('/chat/usuarios/buscar', {
          params: { q: busca.trim() },
        })
        setSugestoes(res)
      } catch {
        setSugestoes([])
      }
    }, 300)
    return () => {
      if (buscaDebounce.current) clearTimeout(buscaDebounce.current)
    }
  }, [busca])

  // Scroll automático para a última mensagem.
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [mensagens])

  // ===== Ações =====

  async function iniciarConversa(u: UsuarioBusca) {
    try {
      const sala = await api.post<ChatSala>('/chat/salas', { outro_usuario_id: u.id })
      setBusca('')
      setSugestoes([])
      await carregarConversas()
      await abrirSala(sala.sala_id, u.nome)
    } catch (e) {
      toast.erro(e instanceof ApiError ? e.message : 'Falha ao iniciar conversa.')
    }
  }

  async function enviarMensagem() {
    const conteudo = texto.trim()
    if (!conteudo || salaAtual === null || enviando) return
    setEnviando(true)
    try {
      const nova = await api.post<ChatMensagem>('/chat/mensagens', {
        sala_id: salaAtual,
        mensagem: conteudo,
      })
      setMensagens((prev) =>
        prev.some((m) => m.id === nova.id) ? prev : [...prev, nova],
      )
      setTexto('')
      void carregarConversas()
    } catch (e) {
      if (e instanceof ApiError && e.errors) {
        toast.erro(e.campo('mensagem') ?? e.message)
      } else {
        toast.erro(e instanceof ApiError ? e.message : 'Falha ao enviar mensagem.')
      }
    } finally {
      setEnviando(false)
    }
  }

  function handleTextareaKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void enviarMensagem()
    }
  }

  // Não renderiza para visitantes não autenticados.
  if (!usuario) return null

  return (
    <>
      {/* Botão flutuante */}
      {!aberto && (
        <div className="position-fixed bottom-0 end-0 m-3" style={{ zIndex: 1050 }}>
          <button
            type="button"
            className="btn btn-primary rounded-circle position-relative d-flex align-items-center justify-content-center"
            style={{ width: 60, height: 60 }}
            onClick={() => setAberto(true)}
            aria-label="Abrir chat"
          >
            <i className="bi bi-chat-dots-fill fs-4" />
            {totalNaoLidas > 0 && (
              <span className="position-absolute top-0 start-0 translate-middle badge rounded-pill bg-danger">
                {totalNaoLidas > 99 ? '99+' : totalNaoLidas}
                <span className="visually-hidden">mensagens não lidas</span>
              </span>
            )}
          </button>
        </div>
      )}

      {/* Painel expandido */}
      {aberto && (
        <div
          className="position-fixed bottom-0 end-0 m-3 border rounded shadow-lg bg-white d-flex flex-column"
          style={{ width: 585, height: 600, maxWidth: 'calc(100vw - 2rem)', zIndex: 1049 }}
        >
          {/* Cabeçalho */}
          <div className="d-flex align-items-center justify-content-between p-3 border-bottom bg-primary text-white">
            <h5 className="mb-0">
              <i className="bi bi-chat-dots me-2" />
              Chat
            </h5>
            <button
              type="button"
              className="btn btn-sm btn-primary"
              onClick={() => setAberto(false)}
              aria-label="Minimizar"
            >
              <i className="bi bi-dash-lg" />
            </button>
          </div>

          {/* Corpo */}
          <div className="d-flex flex-grow-1 overflow-hidden">
            {/* Painel de conversas */}
            <div
              className="border-end bg-light d-flex flex-column"
              style={{ width: 234, flexShrink: 0 }}
            >
              {/* Busca */}
              <div className="p-2">
                <div className="position-relative">
                  <input
                    type="text"
                    className="form-control form-control-sm"
                    placeholder="Buscar usuário..."
                    autoComplete="off"
                    aria-label="Buscar usuário"
                    value={busca}
                    onChange={(e) => setBusca(e.target.value)}
                  />
                  {sugestoes.length > 0 && (
                    <div
                      className="position-absolute w-100 bg-white border rounded-bottom shadow-sm"
                      style={{ zIndex: 1000, maxHeight: 200, overflowY: 'auto' }}
                    >
                      {sugestoes.map((u) => (
                        <button
                          key={u.id}
                          type="button"
                          className="d-flex align-items-center gap-2 w-100 text-start border-0 bg-transparent p-2 chat-user-suggestion"
                          onClick={() => void iniciarConversa(u)}
                        >
                          {u.foto_url ? (
                            <img
                              src={u.foto_url}
                              alt=""
                              className="rounded-circle"
                              width={28}
                              height={28}
                              style={{ objectFit: 'cover' }}
                            />
                          ) : (
                            <i className="bi bi-person-circle fs-5 text-secondary" />
                          )}
                          <span className="text-truncate small">{u.nome}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Lista de conversas */}
              <div className="flex-grow-1 overflow-auto">
                {conversas.length === 0 ? (
                  <p className="text-muted small text-center p-3 mb-0">
                    Nenhuma conversa ainda.
                  </p>
                ) : (
                  conversas.map((c) => (
                    <button
                      key={c.sala_id}
                      type="button"
                      className={`d-flex align-items-center gap-2 w-100 text-start border-0 bg-transparent p-2 border-bottom chat-conversation-item${
                        salaAtual === c.sala_id ? ' bg-white' : ''
                      }`}
                      onClick={() => void abrirSala(c.sala_id, c.outro_usuario.nome)}
                    >
                      {c.outro_usuario.foto_url ? (
                        <img
                          src={c.outro_usuario.foto_url}
                          alt=""
                          className="rounded-circle flex-shrink-0"
                          width={36}
                          height={36}
                          style={{ objectFit: 'cover' }}
                        />
                      ) : (
                        <i className="bi bi-person-circle fs-3 text-secondary flex-shrink-0" />
                      )}
                      <div className="flex-grow-1 overflow-hidden">
                        <div className="d-flex justify-content-between align-items-center">
                          <span className="fw-semibold small text-truncate">
                            {c.outro_usuario.nome}
                          </span>
                          {c.nao_lidas > 0 && (
                            <span className="badge rounded-pill bg-danger ms-1">
                              {c.nao_lidas}
                            </span>
                          )}
                        </div>
                        <span className="d-block text-muted text-truncate" style={{ fontSize: '0.75rem' }}>
                          {c.ultima_mensagem?.mensagem || 'Sem mensagens'}
                        </span>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Painel de mensagens */}
            <div className="d-flex flex-column flex-grow-1 overflow-hidden">
              {salaAtual === null ? (
                <div className="d-flex flex-column align-items-center justify-content-center h-100 text-muted p-3 text-center">
                  <i className="bi bi-chat-square-text fs-1 mb-2" />
                  <p className="mb-0 small">
                    Selecione uma conversa ou busque um usuário para começar.
                  </p>
                </div>
              ) : (
                <>
                  {/* Cabeçalho da conversa */}
                  <div className="px-3 py-2 border-bottom bg-white">
                    <span className="fw-semibold">
                      <i className="bi bi-person-circle me-2 text-secondary" />
                      {nomeOutro}
                    </span>
                  </div>

                  {/* Mensagens */}
                  <div className="flex-grow-1 overflow-auto p-3" style={{ backgroundColor: '#f8f9fa' }}>
                    {carregandoMensagens ? (
                      <div className="text-center text-muted small py-3">
                        <span className="spinner-border spinner-border-sm me-2" role="status" />
                        Carregando...
                      </div>
                    ) : mensagens.length === 0 ? (
                      <p className="text-muted small text-center mb-0">
                        Nenhuma mensagem ainda. Diga olá!
                      </p>
                    ) : (
                      mensagens.map((m) => {
                        const propria = m.usuario_id === usuario.id
                        return (
                          <div
                            key={m.id}
                            className={`d-flex mb-2 ${propria ? 'justify-content-end' : 'justify-content-start'}`}
                          >
                            <div
                              className="px-3 py-2"
                              style={{
                                maxWidth: '75%',
                                backgroundColor: propria ? '#0d6efd' : '#e9ecef',
                                color: propria ? '#fff' : '#212529',
                                borderRadius: propria
                                  ? '1rem 1rem 0 1rem'
                                  : '1rem 1rem 1rem 0',
                              }}
                            >
                              <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                                {m.mensagem}
                              </div>
                              <div
                                className={`text-end ${propria ? 'text-white-50' : 'text-muted'}`}
                                style={{ fontSize: '0.65rem' }}
                              >
                                {formatarHora(m.data_envio)}
                              </div>
                            </div>
                          </div>
                        )
                      })
                    )}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Form de envio */}
                  <div className="p-2 border-top bg-white">
                    <form
                      onSubmit={(e) => {
                        e.preventDefault()
                        void enviarMensagem()
                      }}
                    >
                      <div className="input-group">
                        <textarea
                          className="form-control"
                          placeholder="Digite sua mensagem..."
                          rows={2}
                          aria-label="Mensagem"
                          style={{ resize: 'none' }}
                          value={texto}
                          onChange={(e) => setTexto(e.target.value)}
                          onKeyDown={handleTextareaKeyDown}
                        />
                        <button
                          type="submit"
                          className="btn btn-primary"
                          aria-label="Enviar mensagem"
                          disabled={enviando || !texto.trim()}
                        >
                          <i className="bi bi-send-fill" />
                        </button>
                      </div>
                      <small className="text-muted" style={{ fontSize: '0.7rem' }}>
                        <kbd>Enter</kbd> envia • <kbd>Shift+Enter</kbd> quebra linha
                      </small>
                    </form>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
