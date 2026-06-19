import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, ApiError } from '../../../lib/api'
import type { Usuario } from '../../../lib/types'
import { Perfil } from '../../../lib/types'
import { adminUsuarioCadastroSchema } from '../../../lib/schemas'
import { toast } from '../../../store/uiStore'
import { TextField, SelectField, SubmitButton } from '../../../components/form/Field'

type Erros = Record<string, string[]>

export default function AdminUsuarioCadastrarPage() {
  const navigate = useNavigate()

  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [perfil, setPerfil] = useState<string>(Perfil.CLIENTE)
  const [erros, setErros] = useState<Erros>({})
  const [enviando, setEnviando] = useState(false)

  function campo(nome: string): string | undefined {
    return erros[nome]?.[0]
  }

  async function enviar(e: React.FormEvent) {
    e.preventDefault()
    setErros({})

    const parsed = adminUsuarioCadastroSchema.safeParse({ nome, email, senha, perfil })
    if (!parsed.success) {
      setErros(parsed.error.flatten().fieldErrors as Erros)
      return
    }

    setEnviando(true)
    try {
      await api.post<Usuario>('/admin/usuarios', parsed.data)
      toast.sucesso('Usuário cadastrado com sucesso.')
      navigate('/admin/usuarios/listar')
    } catch (err) {
      if (err instanceof ApiError && err.errors) setErros(err.errors)
      else toast.erro(err instanceof ApiError ? err.message : 'Erro ao cadastrar usuário.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="row justify-content-center">
      <div className="col-lg-8">
        <div className="d-flex align-items-center mb-4">
          <h2 className="mb-0">
            <i className="bi bi-person-plus-fill" /> Cadastrar Novo Usuário
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
              <TextField
                label="Senha"
                name="senha"
                type="password"
                value={senha}
                onChange={setSenha}
                erro={campo('senha')}
                ajuda="Mínimo de 8 caracteres, com maiúscula, minúscula e número."
                obrigatorio
                autoComplete="new-password"
              />
            </div>
            <div className="card-footer p-4">
              <div className="d-flex gap-3">
                <SubmitButton carregando={enviando} icon="check-circle">
                  Cadastrar
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
