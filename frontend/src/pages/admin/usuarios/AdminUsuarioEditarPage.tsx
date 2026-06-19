import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, ApiError } from '../../../lib/api'
import type { Usuario } from '../../../lib/types'
import { Perfil } from '../../../lib/types'
import { adminUsuarioEdicaoSchema } from '../../../lib/schemas'
import { useFetch } from '../../../hooks/useFetch'
import { toast } from '../../../store/uiStore'
import { TextField, SelectField, SubmitButton } from '../../../components/form/Field'
import Spinner from '../../../components/ui/Spinner'

type Erros = Record<string, string[]>

export default function AdminUsuarioEditarPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data, carregando, erro } = useFetch<Usuario>(
    (signal) => api.get(`/admin/usuarios/${id}`, { signal }),
    [id],
  )

  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [perfil, setPerfil] = useState<string>(Perfil.CLIENTE)
  const [erros, setErros] = useState<Erros>({})
  const [enviando, setEnviando] = useState(false)

  useEffect(() => {
    if (data) {
      setNome(data.nome)
      setEmail(data.email)
      setPerfil(data.perfil)
    }
  }, [data])

  function campo(nome: string): string | undefined {
    return erros[nome]?.[0]
  }

  async function enviar(e: React.FormEvent) {
    e.preventDefault()
    setErros({})

    const parsed = adminUsuarioEdicaoSchema.safeParse({ nome, email, perfil })
    if (!parsed.success) {
      setErros(parsed.error.flatten().fieldErrors as Erros)
      return
    }

    setEnviando(true)
    try {
      await api.put<Usuario>(`/admin/usuarios/${id}`, { id: Number(id), ...parsed.data })
      toast.sucesso('Usuário atualizado com sucesso.')
      navigate('/admin/usuarios/listar')
    } catch (err) {
      if (err instanceof ApiError && err.errors) setErros(err.errors)
      else toast.erro(err instanceof ApiError ? err.message : 'Erro ao atualizar usuário.')
    } finally {
      setEnviando(false)
    }
  }

  if (carregando) return <Spinner />
  if (erro || !data)
    return <div className="alert alert-danger">{erro?.message ?? 'Usuário não encontrado.'}</div>

  return (
    <div className="row justify-content-center">
      <div className="col-lg-8">
        <div className="d-flex align-items-center mb-4">
          <h2 className="mb-0">
            <i className="bi bi-person-gear" /> Alterar Usuário
          </h2>
        </div>

        <div className="card shadow-sm">
          <form onSubmit={enviar}>
            <div className="card-body p-4">
              <SelectField
                label="Perfil de Acesso"
                name="perfil"
                value={perfil}
                onChange={setPerfil}
                erro={campo('perfil')}
                obrigatorio
                opcoes={Object.values(Perfil).map((p) => ({ valor: p, rotulo: p }))}
              />
              <TextField
                label="Nome Completo"
                name="nome"
                value={nome}
                onChange={setNome}
                erro={campo('nome')}
                obrigatorio
              />
              <TextField
                label="Email"
                name="email"
                type="email"
                value={email}
                onChange={setEmail}
                erro={campo('email')}
                obrigatorio
                autoComplete="off"
              />
            </div>
            <div className="card-footer p-4">
              <div className="d-flex gap-3">
                <SubmitButton carregando={enviando} icon="check-circle">
                  Salvar Alterações
                </SubmitButton>
                <Link to="/admin/usuarios/listar" className="btn btn-secondary">
                  <i className="bi bi-x-circle me-2" /> Cancelar
                </Link>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
