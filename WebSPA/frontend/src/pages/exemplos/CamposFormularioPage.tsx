// Demonstração dos campos de formulário (portado de demo_campos_formulario.html).
import { useState } from 'react'
import type { FormEvent } from 'react'
import { TextField, TextAreaField, SelectField, SubmitButton } from '../../components/form/Field'
import { toast } from '../../store/uiStore'

export default function CamposFormularioPage() {
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [telefone, setTelefone] = useState('')
  const [site, setSite] = useState('')
  const [senha, setSenha] = useState('')
  const [descricao, setDescricao] = useState('')
  const [estado, setEstado] = useState('')
  const [dataNascimento, setDataNascimento] = useState('')
  const [idade, setIdade] = useState('')

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    toast.sucesso('Formulário enviado! (demonstração)')
  }

  const onReset = () => {
    setNome('')
    setEmail('')
    setTelefone('')
    setSite('')
    setSenha('')
    setDescricao('')
    setEstado('')
    setDataNascimento('')
    setIdade('')
  }

  return (
    <div className="container my-5">
      <div className="row">
        <div className="col-lg-10 mx-auto">
          <h1 className="mb-4">Demonstração dos Campos de Formulário</h1>
          <p className="lead mb-5">
            Exemplos dos tipos de campos disponíveis nos componentes de formulário reutilizáveis.
          </p>

          <form onSubmit={onSubmit} onReset={onReset}>
            <h3 className="mt-5 mb-3">Campos de Texto</h3>
            <TextField
              name="nome"
              label="Nome Completo"
              value={nome}
              onChange={setNome}
              obrigatorio
              maxLength={100}
              placeholder="Digite seu nome completo"
            />
            <TextField
              name="email"
              label="E-mail"
              type="email"
              value={email}
              onChange={setEmail}
              obrigatorio
              placeholder="seu@email.com"
            />
            <TextField
              name="telefone"
              label="Telefone"
              type="tel"
              value={telefone}
              onChange={setTelefone}
              icon="telephone"
              placeholder="(00) 00000-0000"
            />
            <TextField
              name="site"
              label="Website"
              value={site}
              onChange={setSite}
              icon="globe"
              placeholder="https://exemplo.com"
            />

            <h3 className="mt-5 mb-3">Senha</h3>
            <TextField
              name="senha"
              label="Senha"
              type="password"
              value={senha}
              onChange={setSenha}
              obrigatorio
              icon="lock"
              autoComplete="new-password"
            />

            <h3 className="mt-5 mb-3">Área de Texto</h3>
            <TextAreaField
              name="descricao"
              label="Descrição"
              value={descricao}
              onChange={setDescricao}
              rows={5}
              ajuda="Descreva em detalhes o que você precisa."
            />

            <h3 className="mt-5 mb-3">Select (Dropdown)</h3>
            <SelectField
              name="estado"
              label="Estado"
              value={estado}
              onChange={setEstado}
              obrigatorio
              placeholder="Selecione..."
              opcoes={[
                { valor: 'SP', rotulo: 'São Paulo' },
                { valor: 'RJ', rotulo: 'Rio de Janeiro' },
                { valor: 'MG', rotulo: 'Minas Gerais' },
                { valor: 'RS', rotulo: 'Rio Grande do Sul' },
              ]}
            />

            <h3 className="mt-5 mb-3">Data e Números</h3>
            <div className="row">
              <div className="col-md-6">
                <TextField
                  name="data_nascimento"
                  label="Data de Nascimento"
                  type="date"
                  value={dataNascimento}
                  onChange={setDataNascimento}
                  obrigatorio
                />
              </div>
              <div className="col-md-6">
                <TextField
                  name="idade"
                  label="Idade"
                  type="number"
                  value={idade}
                  onChange={setIdade}
                  placeholder="18"
                />
              </div>
            </div>

            <h3 className="mt-5 mb-3">Campo com Erro (Simulação)</h3>
            <TextField
              name="campo_erro"
              label="Campo com Erro"
              value="valor inválido"
              onChange={() => undefined}
              erro="Este campo contém um erro de validação."
            />

            <div className="d-flex gap-3 mt-5">
              <SubmitButton icon="check-circle">Enviar Formulário</SubmitButton>
              <button type="reset" className="btn btn-secondary">
                <i className="bi bi-x-circle me-2" /> Limpar
              </button>
            </div>
          </form>

          <div className="card mt-5 mb-5">
            <div className="card-body">
              <h4 className="card-title">Como Usar os Componentes</h4>
              <p>Importe os campos no topo do seu componente:</p>
              <pre className="bg-light p-3 rounded">
                <code>
                  {`import { TextField, TextAreaField, SelectField } from '../../components/form/Field'`}
                </code>
              </pre>
              <p className="mt-3">Campos controlados via estado local:</p>
              <ul>
                <li>
                  <code>TextField</code> — texto, email, senha, número, data, telefone
                </li>
                <li>
                  <code>TextAreaField</code> — áreas de texto multilinhas
                </li>
                <li>
                  <code>SelectField</code> — dropdowns com lista de opções
                </li>
              </ul>
              <p className="mb-0">
                Todos os campos suportam <code>label</code>, <code>erro</code>, <code>ajuda</code>,{' '}
                <code>obrigatorio</code> e <code>disabled</code>.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
