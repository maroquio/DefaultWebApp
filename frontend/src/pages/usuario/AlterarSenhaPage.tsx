// Alteracao de senha do usuario logado.
// Replica templates/perfil/alterar-senha.html.
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { api, ApiError } from '../../lib/api'
import { toast } from '../../store/uiStore'
import { TextField, SubmitButton } from '../../components/form/Field'

const schema = z
  .object({
    senha_atual: z.string().min(1, 'Informe a senha atual.'),
    senha_nova: z.string().min(8, 'A nova senha deve ter no mínimo 8 caracteres.'),
    confirmar_nova: z.string().min(1, 'Confirme a nova senha.'),
  })
  .refine((d) => d.senha_nova === d.confirmar_nova, {
    message: 'As senhas não coincidem.',
    path: ['confirmar_nova'],
  })

export default function AlterarSenhaPage() {
  const navigate = useNavigate()

  const [senhaAtual, setSenhaAtual] = useState('')
  const [senhaNova, setSenhaNova] = useState('')
  const [confirmarNova, setConfirmarNova] = useState('')
  const [erros, setErros] = useState<Record<string, string[]>>({})
  const [salvando, setSalvando] = useState(false)

  const erroDe = (campo: string) => erros[campo]?.[0]

  async function aoEnviar(e: React.FormEvent) {
    e.preventDefault()
    setErros({})

    const parsed = schema.safeParse({
      senha_atual: senhaAtual,
      senha_nova: senhaNova,
      confirmar_nova: confirmarNova,
    })
    if (!parsed.success) {
      setErros(parsed.error.flatten().fieldErrors)
      return
    }

    setSalvando(true)
    try {
      await api.put('/usuario/senha', parsed.data)
      toast.sucesso('Senha alterada com sucesso!')
      navigate('/usuario/perfil/visualizar')
    } catch (err) {
      if (err instanceof ApiError && err.errors) setErros(err.errors)
      else if (err instanceof ApiError) toast.erro(err.message)
      else toast.erro((err as Error).message)
    } finally {
      setSalvando(false)
    }
  }

  return (
    <div className="row">
      <div className="col-md-8 mx-auto">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-key-fill" /> Alterar Senha
          </h2>
        </div>

        <div className="card shadow-sm">
          <form onSubmit={aoEnviar} autoComplete="off">
            <div className="card-body p-4">
              <TextField
                label="Senha Atual"
                name="senha_atual"
                type="password"
                value={senhaAtual}
                onChange={setSenhaAtual}
                erro={erroDe('senha_atual')}
                obrigatorio
                autoComplete="current-password"
              />
              <div className="row">
                <div className="col-lg-6">
                  <TextField
                    label="Nova Senha"
                    name="senha_nova"
                    type="password"
                    value={senhaNova}
                    onChange={setSenhaNova}
                    erro={erroDe('senha_nova')}
                    obrigatorio
                    autoComplete="new-password"
                  />
                </div>
                <div className="col-lg-6">
                  <TextField
                    label="Confirmar Nova Senha"
                    name="confirmar_nova"
                    type="password"
                    value={confirmarNova}
                    onChange={setConfirmarNova}
                    erro={erroDe('confirmar_nova')}
                    obrigatorio
                    autoComplete="new-password"
                  />
                </div>
              </div>

              <div className="alert alert-warning mb-0" role="alert">
                <i className="bi bi-shield-exclamation" /> <strong>Dica de Segurança:</strong>
                <ul className="mb-0 mt-2">
                  <li>Use uma senha forte e única</li>
                  <li>Não compartilhe sua senha</li>
                  <li>Altere sua senha periodicamente</li>
                  <li>Não reutilize senhas antigas</li>
                </ul>
              </div>
            </div>
            <div className="card-footer p-4 d-flex justify-content-start">
              <div className="d-flex gap-3 mb-0">
                <SubmitButton carregando={salvando} icon="key-fill">
                  Alterar Senha
                </SubmitButton>
                <Link to="/usuario/perfil/visualizar" className="btn btn-outline-secondary">
                  Cancelar
                </Link>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
