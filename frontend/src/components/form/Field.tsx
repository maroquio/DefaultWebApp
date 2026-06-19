// Campos de formulário reutilizáveis (espelham templates/macros/form_fields.html).
// Renderizam label, input Bootstrap, texto de ajuda e mensagem de erro (is-invalid).
import type { ChangeEvent, ReactNode } from 'react'

interface BaseProps {
  label: string
  name: string
  erro?: string
  ajuda?: string
  obrigatorio?: boolean
  disabled?: boolean
  icon?: string
}

function Rotulo({ label, name, obrigatorio }: { label: string; name: string; obrigatorio?: boolean }) {
  return (
    <label htmlFor={name} className="form-label">
      {label}
      {obrigatorio && <span className="text-danger"> *</span>}
    </label>
  )
}

function Feedback({ erro, ajuda }: { erro?: string; ajuda?: string }) {
  return (
    <>
      {erro && <div className="invalid-feedback">{erro}</div>}
      {ajuda && !erro && <div className="form-text">{ajuda}</div>}
    </>
  )
}

interface TextFieldProps extends BaseProps {
  value: string
  onChange: (v: string) => void
  type?: 'text' | 'email' | 'password' | 'number' | 'date' | 'tel'
  placeholder?: string
  autoComplete?: string
  maxLength?: number
}

export function TextField({
  label,
  name,
  value,
  onChange,
  erro,
  ajuda,
  obrigatorio,
  disabled,
  icon,
  type = 'text',
  placeholder,
  autoComplete,
  maxLength,
}: TextFieldProps) {
  const input = (
    <input
      id={name}
      name={name}
      type={type}
      className={`form-control ${erro ? 'is-invalid' : ''}`}
      value={value}
      onChange={(e: ChangeEvent<HTMLInputElement>) => onChange(e.target.value)}
      placeholder={placeholder}
      autoComplete={autoComplete}
      maxLength={maxLength}
      disabled={disabled}
    />
  )
  return (
    <div className="mb-3">
      <Rotulo label={label} name={name} obrigatorio={obrigatorio} />
      {icon ? (
        <div className="input-group">
          <span className="input-group-text">
            <i className={`bi bi-${icon}`} />
          </span>
          {input}
          <Feedback erro={erro} ajuda={ajuda} />
        </div>
      ) : (
        <>
          {input}
          <Feedback erro={erro} ajuda={ajuda} />
        </>
      )}
    </div>
  )
}

interface TextAreaProps extends BaseProps {
  value: string
  onChange: (v: string) => void
  rows?: number
  placeholder?: string
  maxLength?: number
}

export function TextAreaField({
  label,
  name,
  value,
  onChange,
  erro,
  ajuda,
  obrigatorio,
  disabled,
  rows = 4,
  placeholder,
  maxLength,
}: TextAreaProps) {
  return (
    <div className="mb-3">
      <Rotulo label={label} name={name} obrigatorio={obrigatorio} />
      <textarea
        id={name}
        name={name}
        className={`form-control ${erro ? 'is-invalid' : ''}`}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={rows}
        placeholder={placeholder}
        maxLength={maxLength}
        disabled={disabled}
      />
      <Feedback erro={erro} ajuda={ajuda} />
    </div>
  )
}

interface SelectProps extends BaseProps {
  value: string
  onChange: (v: string) => void
  opcoes: { valor: string; rotulo: string }[]
  placeholder?: string
}

export function SelectField({
  label,
  name,
  value,
  onChange,
  erro,
  ajuda,
  obrigatorio,
  disabled,
  opcoes,
  placeholder,
}: SelectProps) {
  return (
    <div className="mb-3">
      <Rotulo label={label} name={name} obrigatorio={obrigatorio} />
      <select
        id={name}
        name={name}
        className={`form-select ${erro ? 'is-invalid' : ''}`}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {opcoes.map((o) => (
          <option key={o.valor} value={o.valor}>
            {o.rotulo}
          </option>
        ))}
      </select>
      <Feedback erro={erro} ajuda={ajuda} />
    </div>
  )
}

// Botão de submit com estado de carregamento padronizado.
export function SubmitButton({
  carregando,
  children,
  className = 'btn btn-primary',
  icon,
}: {
  carregando?: boolean
  children: ReactNode
  className?: string
  icon?: string
}) {
  return (
    <button type="submit" className={className} disabled={carregando}>
      {carregando ? (
        <span className="spinner-border spinner-border-sm me-2" />
      ) : (
        icon && <i className={`bi bi-${icon} me-2`} />
      )}
      {children}
    </button>
  )
}
