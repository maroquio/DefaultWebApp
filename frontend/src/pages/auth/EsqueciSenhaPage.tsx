import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import type { MensagemResponse } from '../../lib/types'
import { TextField, SubmitButton } from '../../components/form/Field'
import { esqueciSenhaSchema } from '../../lib/schemas'

const MENSAGEM_GENERICA =
  'Se o e-mail informado estiver cadastrado, enviaremos um link para redefinição de senha. Verifique sua caixa de entrada.'

export default function EsqueciSenhaPage() {
  const [email, setEmail] = useState('')
  const [erros, setErros] = useState<Record<string, string[]>>({})
  const [enviando, setEnviando] = useState(false)
  const [enviado, setEnviado] = useState(false)

  async function aoEnviar(e: FormEvent) {
    e.preventDefault()
    setErros({})

    const parsed = esqueciSenhaSchema.safeParse({ email })
    if (!parsed.success) {
      setErros(parsed.error.flatten().fieldErrors)
      return
    }

    setEnviando(true)
    try {
      await api.post<MensagemResponse>('/esqueci-senha', parsed.data)
      setEnviado(true)
    } catch (err) {
      // Por privacidade, mostramos a mensagem genérica mesmo em caso de erro,
      // exceto quando o backend devolve erro de validação por campo.
      if (err instanceof ApiError && err.errors) setErros(err.errors)
      else setEnviado(true)
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
                  <i className="bi bi-key" /> Recuperar Senha
                </h3>

                {enviado ? (
                  <div className="alert alert-success mb-0" role="alert">
                    <i className="bi bi-check-circle me-2" />
                    {MENSAGEM_GENERICA}
                  </div>
                ) : (
                  <>
                    <p className="text-muted text-center mb-4">
                      Não se preocupe! Basta informar seu e-mail cadastrado e enviaremos um
                      link para redefinição de senha.
                    </p>

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
                  </>
                )}
              </div>
              <div className="card-footer p-4">
                <div className="d-grid gap-2">
                  {!enviado && (
                    <SubmitButton carregando={enviando} icon="envelope">
                      Enviar Link de Recuperação
                    </SubmitButton>
                  )}

                  {!enviado && <hr className="my-2" />}

                  <Link to="/login" className="btn btn-outline-secondary">
                    <i className="bi bi-arrow-left me-2" /> Voltar ao Login
                  </Link>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
