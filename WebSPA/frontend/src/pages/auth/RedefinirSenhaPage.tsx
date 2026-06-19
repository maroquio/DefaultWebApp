import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import type { MensagemResponse } from '../../lib/types'
import { toast } from '../../store/uiStore'
import { TextField, SubmitButton } from '../../components/form/Field'
import { redefinirSenhaSchema } from '../../lib/schemas'

export default function RedefinirSenhaPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''

  const [senha, setSenha] = useState('')
  const [confirmarSenha, setConfirmarSenha] = useState('')
  const [erros, setErros] = useState<Record<string, string[]>>({})
  const [enviando, setEnviando] = useState(false)

  async function aoEnviar(e: FormEvent) {
    e.preventDefault()
    setErros({})

    const parsed = redefinirSenhaSchema.safeParse({
      senha,
      confirmar_senha: confirmarSenha,
    })
    if (!parsed.success) {
      setErros(parsed.error.flatten().fieldErrors)
      return
    }

    setEnviando(true)
    try {
      await api.post<MensagemResponse>('/redefinir-senha', { token, ...parsed.data })
      toast.sucesso('Senha redefinida com sucesso! Faça login com a nova senha.')
      navigate('/login', { replace: true })
    } catch (err) {
      if (err instanceof ApiError && err.errors) setErros(err.errors)
      else toast.erro(err instanceof Error ? err.message : 'Falha ao redefinir a senha.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="d-flex flex-column flex-fill justify-content-center">
      <div className="row align-items-center justify-content-center">
        <div className="col-12 col-md-6 col-lg-5">
          <div className="card shadow">
            <form onSubmit={aoEnviar} noValidate>
              <div className="card-body p-4">
                <h3 className="card-title text-center mb-4">
                  <i className="bi bi-shield-lock" /> Redefinir Senha
                </h3>

                {token ? (
                  <>
                    <p className="text-muted text-center mb-4">Digite sua nova senha abaixo.</p>

                    {erros.token?.[0] && (
                      <div className="alert alert-danger" role="alert">
                        <i className="bi bi-exclamation-triangle me-2" />
                        {erros.token[0]}
                      </div>
                    )}

                    <TextField
                      label="Nova Senha"
                      name="senha"
                      type="password"
                      value={senha}
                      onChange={setSenha}
                      erro={erros.senha?.[0]}
                      autoComplete="new-password"
                      obrigatorio
                    />

                    <TextField
                      label="Confirmar Nova Senha"
                      name="confirmar_senha"
                      type="password"
                      value={confirmarSenha}
                      onChange={setConfirmarSenha}
                      erro={erros.confirmar_senha?.[0]}
                      autoComplete="new-password"
                      obrigatorio
                    />

                    <div className="alert alert-info mb-0">
                      <strong>
                        <i className="bi bi-info-circle" /> Requisitos da senha:
                      </strong>
                      <ul className="mb-0 mt-2">
                        <li>Mínimo de 8 caracteres</li>
                        <li>Pelo menos 1 letra maiúscula</li>
                        <li>Pelo menos 1 letra minúscula</li>
                        <li>Pelo menos 1 número</li>
                      </ul>
                    </div>
                  </>
                ) : (
                  <div className="alert alert-danger mb-0" role="alert">
                    <i className="bi bi-exclamation-triangle me-2" />
                    Link de redefinição inválido ou expirado. Solicite um novo link de
                    recuperação.
                  </div>
                )}
              </div>
              <div className="card-footer p-4">
                {token ? (
                  <div className="d-grid">
                    <SubmitButton carregando={enviando} icon="shield-lock">
                      Redefinir Senha
                    </SubmitButton>
                  </div>
                ) : (
                  <div className="d-grid">
                    <Link to="/esqueci-senha" className="btn btn-primary">
                      <i className="bi bi-key me-2" /> Solicitar Novo Link
                    </Link>
                  </div>
                )}

                <hr className="my-4" />

                <p className="text-center mb-0">
                  <Link to="/login" className="text-decoration-none">
                    <i className="bi bi-arrow-left me-2" /> Voltar ao Login
                  </Link>
                </p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
