// Edicao de dados do perfil (nome + email).
// Replica templates/perfil/editar.html.
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { api, ApiError } from '../../lib/api'
import { useAuthStore } from '../../store/authStore'
import { toast } from '../../store/uiStore'
import { TextField, SubmitButton } from '../../components/form/Field'
import type { Usuario } from '../../lib/types'

const schema = z.object({
  nome: z
    .string()
    .trim()
    .min(4, 'O nome deve ter no mínimo 4 caracteres.')
    .max(100, 'O nome deve ter no máximo 100 caracteres.')
    .refine((v) => v.trim().split(/\s+/).length >= 2, 'Informe nome e sobrenome.'),
  email: z.string().trim().email('E-mail inválido.'),
})

export default function PerfilEditarPage() {
  const usuario = useAuthStore((s) => s.usuario)
  const setUsuario = useAuthStore((s) => s.setUsuario)
  const navigate = useNavigate()

  const [nome, setNome] = useState(usuario?.nome ?? '')
  const [email, setEmail] = useState(usuario?.email ?? '')
  const [erros, setErros] = useState<Record<string, string[]>>({})
  const [salvando, setSalvando] = useState(false)

  const erroDe = (campo: string) => erros[campo]?.[0]

  async function aoEnviar(e: React.FormEvent) {
    e.preventDefault()
    setErros({})

    const parsed = schema.safeParse({ nome, email })
    if (!parsed.success) {
      setErros(parsed.error.flatten().fieldErrors)
      return
    }

    setSalvando(true)
    try {
      const atualizado = await api.put<Usuario>('/usuario/perfil', parsed.data)
      setUsuario(atualizado)
      toast.sucesso('Perfil atualizado com sucesso!')
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
            <i className="bi bi-pencil-square" /> Editar Perfil
          </h2>
        </div>

        <div className="card shadow-sm">
          <form onSubmit={aoEnviar}>
            <div className="card-body p-4">
              <TextField
                label="Nome Completo"
                name="nome"
                value={nome}
                onChange={setNome}
                erro={erroDe('nome')}
                obrigatorio
                maxLength={100}
              />
              <TextField
                label="E-mail"
                name="email"
                type="email"
                value={email}
                onChange={setEmail}
                erro={erroDe('email')}
                obrigatorio
              />
              <TextField
                label="Perfil de Acesso"
                name="perfil"
                value={usuario?.perfil ?? ''}
                onChange={() => {}}
                disabled
              />
            </div>
            <div className="card-footer p-4">
              <div className="d-flex gap-3">
                <SubmitButton carregando={salvando} icon="check-circle">
                  Salvar Alterações
                </SubmitButton>
                <Link to="/usuario/perfil/visualizar" className="btn btn-outline-secondary">
                  Cancelar
                </Link>
              </div>
            </div>
          </form>
        </div>

        <div className="alert alert-info mt-4" role="alert">
          <i className="bi bi-info-circle" /> <strong>Dica:</strong> Ao alterar o e-mail, você
          deverá usar o novo e-mail para fazer login na próxima vez.
        </div>
      </div>
    </div>
  )
}
