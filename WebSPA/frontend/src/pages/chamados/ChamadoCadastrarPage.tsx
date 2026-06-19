import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { api, ApiError } from '../../lib/api'
import type { Chamado } from '../../lib/types'
import { PrioridadeChamado } from '../../lib/types'
import { toast } from '../../store/uiStore'
import { TextField, TextAreaField, SelectField, SubmitButton } from '../../components/form/Field'

const schema = z.object({
  titulo: z
    .string()
    .trim()
    .min(10, 'O título deve ter no mínimo 10 caracteres.')
    .max(200, 'O título deve ter no máximo 200 caracteres.'),
  descricao: z
    .string()
    .trim()
    .min(20, 'A descrição deve ter no mínimo 20 caracteres.')
    .max(2000, 'A descrição deve ter no máximo 2000 caracteres.'),
  prioridade: z.string().min(1, 'Selecione a prioridade.'),
})

export default function ChamadoCadastrarPage() {
  const navigate = useNavigate()

  const [titulo, setTitulo] = useState('')
  const [descricao, setDescricao] = useState('')
  const [prioridade, setPrioridade] = useState<string>(PrioridadeChamado.MEDIA)
  const [erros, setErros] = useState<Record<string, string[]>>({})
  const [enviando, setEnviando] = useState(false)

  function erroCampo(campo: string): string | undefined {
    return erros[campo]?.[0]
  }

  async function submeter(e: React.FormEvent) {
    e.preventDefault()
    setErros({})

    const parsed = schema.safeParse({ titulo, descricao, prioridade })
    if (!parsed.success) {
      setErros(parsed.error.flatten().fieldErrors)
      return
    }

    setEnviando(true)
    try {
      await api.post<Chamado>('/chamados', parsed.data)
      toast.sucesso('Chamado aberto com sucesso!')
      navigate('/chamados/listar')
    } catch (err) {
      if (err instanceof ApiError && err.errors) {
        setErros(err.errors)
      } else {
        toast.erro(err instanceof ApiError ? err.message : 'Erro ao abrir chamado.')
      }
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-headset" /> Abrir Novo Chamado
          </h2>
        </div>

        <div className="alert alert-info mb-4" role="alert">
          <i className="bi bi-info-circle" /> <strong>Antes de abrir um chamado:</strong>
          <ul className="mb-0 mt-2">
            <li>Descreva seu problema ou dúvida de forma clara e detalhada</li>
            <li>Informe a prioridade adequada para ajudar na organização</li>
            <li>Nossa equipe responderá o mais breve possível</li>
          </ul>
        </div>

        <div className="card shadow-sm">
          <form onSubmit={submeter}>
            <div className="card-body p-4">
              <TextField
                label="Título"
                name="titulo"
                value={titulo}
                onChange={setTitulo}
                erro={erroCampo('titulo')}
                ajuda="Título curto e objetivo (10-200 caracteres)"
                placeholder="Descreva brevemente o problema ou dúvida"
                maxLength={200}
                obrigatorio
              />

              <TextAreaField
                label="Descrição Detalhada"
                name="descricao"
                value={descricao}
                onChange={setDescricao}
                erro={erroCampo('descricao')}
                ajuda="Forneça o máximo de detalhes possível (20-2000 caracteres)"
                placeholder="Descreva detalhadamente seu problema, incluindo passos para reproduzir, mensagens de erro, etc."
                rows={6}
                maxLength={2000}
                obrigatorio
              />

              <SelectField
                label="Prioridade"
                name="prioridade"
                value={prioridade}
                onChange={setPrioridade}
                erro={erroCampo('prioridade')}
                ajuda="Selecione a prioridade do seu chamado"
                obrigatorio
                opcoes={[
                  { valor: PrioridadeChamado.BAIXA, rotulo: 'Baixa - Não urgente' },
                  { valor: PrioridadeChamado.MEDIA, rotulo: 'Média - Normal' },
                  { valor: PrioridadeChamado.ALTA, rotulo: 'Alta - Importante' },
                  { valor: PrioridadeChamado.URGENTE, rotulo: 'Urgente - Crítico' },
                ]}
              />
            </div>
            <div className="card-footer p-4">
              <div className="d-flex gap-3">
                <SubmitButton carregando={enviando} className="btn btn-success" icon="send">
                  Abrir Chamado
                </SubmitButton>
                <Link to="/chamados/listar" className="btn btn-secondary">
                  <i className="bi bi-x-circle" /> Cancelar
                </Link>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
