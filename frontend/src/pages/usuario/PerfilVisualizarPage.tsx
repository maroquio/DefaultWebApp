// Visualizacao do perfil do usuario logado.
// Replica templates/perfil/visualizar.html. Upload de foto simples (sem cropper).
import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import { useAuthStore } from '../../store/authStore'
import { toast } from '../../store/uiStore'
import { formatarData } from '../../lib/format'
import { PerfilBadge } from '../../components/ui/Badges'
import type { Usuario } from '../../lib/types'

const FOTO_FALLBACK = '/static/img/user.jpg'

// Espelha o contrato do backend (PUT /usuario/foto): máx 10MB e tipos de imagem.
// Pré-validar no cliente evita round-trips que só retornariam 413/400.
const FOTO_MAX_BYTES = 10 * 1024 * 1024
const FOTO_TIPOS = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

function lerComoBase64(arquivo: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = () => reject(new Error('Falha ao ler o arquivo.'))
    reader.readAsDataURL(arquivo)
  })
}

export default function PerfilVisualizarPage() {
  const usuario = useAuthStore((s) => s.usuario)
  const setUsuario = useAuthStore((s) => s.setUsuario)
  const inputRef = useRef<HTMLInputElement>(null)
  const [enviando, setEnviando] = useState(false)

  // A store já traz o usuário do /api/me do boot; aqui buscamos dados frescos
  // do servidor (GET /usuario/perfil) para refletir alterações fora desta aba.
  useEffect(() => {
    api.get<Usuario>('/usuario/perfil').then(setUsuario).catch(() => {})
  }, [setUsuario])

  if (!usuario) return null

  async function aoSelecionarArquivo(e: React.ChangeEvent<HTMLInputElement>) {
    const arquivo = e.target.files?.[0]
    e.target.value = ''
    if (!arquivo) return
    if (!FOTO_TIPOS.includes(arquivo.type)) {
      toast.erro('Formato inválido. Use JPG, PNG, GIF ou WEBP.')
      return
    }
    if (arquivo.size > FOTO_MAX_BYTES) {
      toast.erro('Imagem muito grande. O tamanho máximo é 10MB.')
      return
    }
    setEnviando(true)
    try {
      const foto_base64 = await lerComoBase64(arquivo)
      const atualizado = await api.put<Usuario>('/usuario/foto', { foto_base64 })
      setUsuario(atualizado)
      toast.sucesso('Foto atualizada com sucesso!')
    } catch (err) {
      if (err instanceof ApiError) toast.erro(err.message)
      else toast.erro((err as Error).message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="row g-4">
      {/* Card de identidade */}
      <div className="col-12">
        <div className="card shadow-sm border-0">
          <div className="card-body p-4">
            <div className="row align-items-center g-4">
              <div className="col-12 col-md-auto text-center">
                <img
                  src={usuario.foto_url}
                  alt="Foto de Perfil"
                  className="rounded-circle border border-3 border-primary object-fit-cover"
                  width={120}
                  height={120}
                  onError={(e) => {
                    const img = e.currentTarget
                    if (img.src.endsWith(FOTO_FALLBACK)) return
                    img.src = FOTO_FALLBACK
                  }}
                />
              </div>
              <div className="col-12 col-md text-center text-md-start">
                <h2 className="fw-bold mb-1">{usuario.nome}</h2>
                <p className="text-muted mb-3">
                  <i className="bi bi-envelope me-1" />
                  {usuario.email}
                </p>
                <div className="d-flex flex-wrap gap-2 justify-content-center justify-content-md-start">
                  <PerfilBadge perfil={usuario.perfil} />
                  {usuario.data_cadastro && (
                    <span className="badge bg-light text-muted border px-3 py-2">
                      <i className="bi bi-calendar-check me-1" />
                      Membro desde {formatarData(usuario.data_cadastro)}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Card: Editar Dados */}
      <div className="col-12 col-md-4">
        <div className="card shadow-sm border-0 h-100">
          <div className="card-body d-flex flex-column align-items-center text-center p-4 gap-3">
            <div className="rounded-circle bg-primary bg-opacity-10 p-3">
              <i className="bi bi-pencil-square fs-3 text-primary" />
            </div>
            <div>
              <h5 className="mb-1">Editar Dados</h5>
              <p className="text-muted small mb-0">Atualize seu nome e e-mail</p>
            </div>
            <Link to="/usuario/perfil/editar" className="btn btn-primary w-100 mt-auto">
              <i className="bi bi-pencil-square me-1" />
              Editar Dados
            </Link>
          </div>
        </div>
      </div>

      {/* Card: Alterar Senha */}
      <div className="col-12 col-md-4">
        <div className="card shadow-sm border-0 h-100">
          <div className="card-body d-flex flex-column align-items-center text-center p-4 gap-3">
            <div className="rounded-circle bg-warning bg-opacity-10 p-3">
              <i className="bi bi-key-fill fs-3 text-warning" />
            </div>
            <div>
              <h5 className="mb-1">Alterar Senha</h5>
              <p className="text-muted small mb-0">Mantenha sua conta segura</p>
            </div>
            <Link to="/usuario/perfil/alterar-senha" className="btn btn-warning w-100 mt-auto">
              <i className="bi bi-key-fill me-1" />
              Alterar Senha
            </Link>
          </div>
        </div>
      </div>

      {/* Card: Alterar Foto */}
      <div className="col-12 col-md-4">
        <div className="card shadow-sm border-0 h-100">
          <div className="card-body d-flex flex-column align-items-center text-center p-4 gap-3">
            <div className="rounded-circle bg-info bg-opacity-10 p-3">
              <i className="bi bi-camera-fill fs-3 text-info" />
            </div>
            <div>
              <h5 className="mb-1">Alterar Foto</h5>
              <p className="text-muted small mb-0">Personalize seu avatar</p>
            </div>
            <button
              type="button"
              className="btn btn-info w-100 mt-auto"
              disabled={enviando}
              onClick={() => inputRef.current?.click()}
            >
              {enviando ? (
                <span className="spinner-border spinner-border-sm me-2" />
              ) : (
                <i className="bi bi-camera-fill me-1" />
              )}
              {enviando ? 'Enviando...' : 'Alterar Foto'}
            </button>
          </div>
        </div>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.gif,.webp"
        className="d-none"
        onChange={aoSelecionarArquivo}
      />
    </div>
  )
}
