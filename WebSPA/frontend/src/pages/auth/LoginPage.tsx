import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { ApiError } from '../../lib/api'
import { useAuthStore } from '../../store/authStore'
import { toast } from '../../store/uiStore'
import { TextField, SubmitButton } from '../../components/form/Field'
import { loginSchema } from '../../lib/schemas'

interface LocationState {
  from?: string
}

export default function LoginPage() {
  const login = useAuthStore((s) => s.login)
  const navigate = useNavigate()
  const location = useLocation()
  const destino = (location.state as LocationState | null)?.from ?? '/usuario'

  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erros, setErros] = useState<Record<string, string[]>>({})
  const [enviando, setEnviando] = useState(false)

  async function aoEnviar(e: FormEvent) {
    e.preventDefault()
    setErros({})

    const parsed = loginSchema.safeParse({ email, senha })
    if (!parsed.success) {
      setErros(parsed.error.flatten().fieldErrors)
      return
    }

    setEnviando(true)
    try {
      await login(parsed.data.email, parsed.data.senha)
      toast.sucesso('Login realizado com sucesso!')
      navigate(destino, { replace: true })
    } catch (err) {
      if (err instanceof ApiError && err.errors) setErros(err.errors)
      else toast.erro(err instanceof Error ? err.message : 'Falha ao entrar.')
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
                  <i className="bi bi-box-arrow-in-right" /> Login
                </h3>

                <TextField
                  label="E-mail"
                  name="email"
                  type="email"
                  value={email}
                  onChange={setEmail}
                  erro={erros.email?.[0]}
                  autoComplete="email"
                  obrigatorio
                />

                <TextField
                  label="Senha"
                  name="senha"
                  type="password"
                  value={senha}
                  onChange={setSenha}
                  erro={erros.senha?.[0]}
                  autoComplete="current-password"
                  obrigatorio
                />

                <div className="mb-0">
                  <Link to="/esqueci-senha" className="text-decoration-none small">
                    Esqueceu sua senha?
                  </Link>
                </div>
              </div>
              <div className="card-footer p-4">
                <div className="d-grid">
                  <SubmitButton carregando={enviando} icon="box-arrow-in-right">
                    Entrar
                  </SubmitButton>
                </div>

                <hr className="my-4" />

                <p className="text-center mb-0">
                  Não tem uma conta?{' '}
                  <Link to="/cadastrar" className="text-decoration-none">
                    Cadastre-se aqui
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
