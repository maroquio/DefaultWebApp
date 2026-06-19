import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import { Perfil } from '../../lib/types'
import type { Usuario } from '../../lib/types'
import { toast } from '../../store/uiStore'
import { TextField, SubmitButton } from '../../components/form/Field'
import { cadastroSchema } from '../../lib/schemas'

interface OpcaoPerfil {
  valor: typeof Perfil.CLIENTE | typeof Perfil.VENDEDOR
  icone: string
}

const OPCOES_PERFIL: OpcaoPerfil[] = [
  { valor: Perfil.CLIENTE, icone: 'cart3' },
  { valor: Perfil.VENDEDOR, icone: 'shop' },
]

/** Calcula a força da senha (0 a 4) e devolve rótulo + classe de cor. */
function avaliarSenha(senha: string): { nivel: number; rotulo: string; cor: string } {
  let nivel = 0
  if (senha.length >= 8) nivel++
  if (/[A-Z]/.test(senha)) nivel++
  if (/[a-z]/.test(senha)) nivel++
  if (/[0-9]/.test(senha)) nivel++
  if (/[^A-Za-z0-9]/.test(senha)) nivel++
  if (senha.length === 0) return { nivel: 0, rotulo: '', cor: 'bg-secondary' }
  if (nivel <= 2) return { nivel, rotulo: 'Fraca', cor: 'bg-danger' }
  if (nivel === 3 || nivel === 4) return { nivel, rotulo: 'Média', cor: 'bg-warning' }
  return { nivel, rotulo: 'Forte', cor: 'bg-success' }
}

export default function CadastroPage() {
  const navigate = useNavigate()

  const [perfil, setPerfil] = useState<string>(Perfil.CLIENTE)
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [confirmarSenha, setConfirmarSenha] = useState('')
  const [erros, setErros] = useState<Record<string, string[]>>({})
  const [enviando, setEnviando] = useState(false)

  const forca = useMemo(() => avaliarSenha(senha), [senha])

  async function aoEnviar(e: FormEvent) {
    e.preventDefault()
    setErros({})

    const parsed = cadastroSchema.safeParse({
      perfil,
      nome,
      email,
      senha,
      confirmar_senha: confirmarSenha,
    })
    if (!parsed.success) {
      setErros(parsed.error.flatten().fieldErrors)
      return
    }

    setEnviando(true)
    try {
      await api.post<Usuario>('/cadastrar', parsed.data)
      toast.sucesso('Conta criada com sucesso! Faça login para continuar.')
      navigate('/login', { replace: true })
    } catch (err) {
      if (err instanceof ApiError && err.errors) setErros(err.errors)
      else toast.erro(err instanceof Error ? err.message : 'Falha ao criar conta.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="d-flex flex-column flex-fill justify-content-center">
      <div className="row align-items-center justify-content-center">
        <div className="col-12 col-md-8 col-lg-7">
          <div className="card shadow">
            <form onSubmit={aoEnviar} noValidate>
              <div className="card-body p-4">
                <h3 className="card-title text-center mb-4">
                  <i className="bi bi-person-plus" /> Criar Conta
                </h3>

                <div className="mb-3">
                  <label className="form-label">
                    Perfil<span className="text-danger"> *</span>
                  </label>
                  <div className="btn-group w-100" role="group" aria-label="Perfil">
                    {OPCOES_PERFIL.map((opcao) => (
                      <button
                        key={opcao.valor}
                        type="button"
                        className={`btn ${perfil === opcao.valor ? 'btn-primary' : 'btn-outline-primary'}`}
                        onClick={() => setPerfil(opcao.valor)}
                        aria-pressed={perfil === opcao.valor}
                      >
                        <i className={`bi bi-${opcao.icone} me-2`} />
                        {opcao.valor}
                      </button>
                    ))}
                  </div>
                  {erros.perfil?.[0] && (
                    <div className="text-danger small mt-1">{erros.perfil[0]}</div>
                  )}
                </div>

                <TextField
                  label="Nome Completo"
                  name="nome"
                  value={nome}
                  onChange={setNome}
                  erro={erros.nome?.[0]}
                  autoComplete="name"
                  maxLength={100}
                  obrigatorio
                />

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

                <div className="row">
                  <div className="col-12 col-lg-6">
                    <TextField
                      label="Senha"
                      name="senha"
                      type="password"
                      value={senha}
                      onChange={setSenha}
                      erro={erros.senha?.[0]}
                      autoComplete="new-password"
                      obrigatorio
                    />
                  </div>
                  <div className="col-12 col-lg-6">
                    <TextField
                      label="Confirmar Senha"
                      name="confirmar_senha"
                      type="password"
                      value={confirmarSenha}
                      onChange={setConfirmarSenha}
                      erro={erros.confirmar_senha?.[0]}
                      autoComplete="new-password"
                      obrigatorio
                    />
                  </div>
                </div>

                {senha.length > 0 && (
                  <div className="mb-3">
                    <div className="d-flex justify-content-between mb-1">
                      <small className="text-muted">Força da senha:</small>
                      <small className="text-muted">{forca.rotulo}</small>
                    </div>
                    <div className="progress" style={{ height: '6px' }}>
                      <div
                        className={`progress-bar ${forca.cor}`}
                        role="progressbar"
                        style={{ width: `${(forca.nivel / 5) * 100}%` }}
                        aria-valuenow={forca.nivel}
                        aria-valuemin={0}
                        aria-valuemax={5}
                      />
                    </div>
                  </div>
                )}

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
              </div>
              <div className="card-footer p-4">
                <div className="d-grid">
                  <SubmitButton carregando={enviando} icon="person-plus">
                    Criar Conta
                  </SubmitButton>
                </div>

                <hr className="my-4" />

                <p className="text-center mb-0">
                  Já tem uma conta?{' '}
                  <Link to="/login" className="text-decoration-none">
                    Faça login aqui
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
