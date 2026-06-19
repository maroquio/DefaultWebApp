const APP_NAME = 'Sistema Web'

interface Tecnologia {
  nome: string
  cor: string
}

const tecnologias: Tecnologia[] = [
  { nome: 'Python 3.10+', cor: 'bg-primary' },
  { nome: 'FastAPI', cor: 'bg-success' },
  { nome: 'Jinja2', cor: 'bg-info' },
  { nome: 'Bootstrap 5.3.8', cor: 'bg-primary' },
  { nome: 'SQLite', cor: 'bg-secondary' },
  { nome: 'Pydantic', cor: 'bg-warning text-dark' },
  { nome: 'Bcrypt', cor: 'bg-danger' },
  { nome: 'Pillow', cor: 'bg-dark' },
  { nome: 'Resend', cor: 'bg-info' },
  { nome: 'Pytest', cor: 'bg-success' },
]

interface MembroEquipe {
  nome: string
  papel: string
  icone: string
}

const equipe: MembroEquipe[] = [
  { nome: 'Alan Turing', papel: 'Desenvolvedor', icone: 'bi-code-slash' },
  { nome: 'Albert Einstein', papel: 'Desenvolvedor', icone: 'bi-code-slash' },
  { nome: 'Anders Hejlsberg', papel: 'Desenvolvedor', icone: 'bi-code-slash' },
  { nome: 'Steve Jobs', papel: 'Desenvolvedor', icone: 'bi-code-slash' },
  { nome: 'Prof. Ricardo Maroquio', papel: 'Professor Orientador', icone: 'bi-mortarboard' },
]

export default function SobrePage() {
  return (
    <>
      {/* Hero Section */}
      <div className="row mb-4">
        <div className="col-12">
          <h1 className="display-4 mb-2">Sobre o Projeto {APP_NAME}</h1>
          <p className="text-muted">
            Projeto Acadêmico desenvolvido no Ifes Campus Cachoeiro de Itapemirim
          </p>
          <hr />
        </div>
      </div>

      {/* Informações do Projeto */}
      <div className="row mb-5">
        <div className="col-12">
          <div className="card border-0 shadow-sm shadow-hover">
            <div className="card-body p-4">
              <h4 className="card-title text-primary mb-4">
                <i className="bi bi-mortarboard-fill me-2" />
                Informações Acadêmicas
              </h4>
              <p className="text-muted">
                Este projeto foi desenvolvido no{' '}
                <strong>Instituto Federal do Espírito Santo</strong>, Campus{' '}
                <strong>Cachoeiro de Itapemirim</strong>, como parte da disciplina{' '}
                <strong>Projeto Integrador</strong> do curso{' '}
                <strong>Técnico em Informática para Internet</strong>. O período de desenvolvimento
                compreende os meses de <strong>fevereiro a dezembro de 2026</strong>.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stack Tecnológica */}
      <div className="row mb-5">
        <div className="col-12">
          <div className="card border-0 shadow-sm shadow-hover">
            <div className="card-body p-4">
              <h4 className="card-title text-primary mb-4">
                <i className="bi bi-stack me-2" />
                Stack Tecnológica
              </h4>
              <div className="d-flex flex-wrap gap-2">
                {tecnologias.map((tec) => (
                  <span key={tec.nome} className={`badge ${tec.cor} fs-6 py-2 px-3`}>
                    {tec.nome}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Equipe */}
      <div className="row mb-5">
        <div className="col-12">
          <div className="card border-0 shadow-sm shadow-hover">
            <div className="card-body p-4">
              <h4 className="card-title text-primary mb-4">
                <i className="bi bi-people-fill me-2" />
                Equipe do Projeto
              </h4>

              <div className="row g-4 mb-0 row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-5">
                {equipe.map((membro) => (
                  <div className="col" key={membro.nome}>
                    <div className="card h-100 shadow-sm shadow-hover">
                      <div className="card-body text-center p-4">
                        <div className="d-inline-flex align-items-center justify-content-center mb-3">
                          <span
                            className="rounded-circle bg-light d-inline-flex align-items-center justify-content-center"
                            style={{ width: 80, height: 80 }}
                          >
                            <i className="bi bi-person-fill text-secondary fs-1" />
                          </span>
                        </div>
                        <h4 className="h6 card-title mb-2">{membro.nome}</h4>
                        <p className="text-muted small mb-0">
                          <i className={`bi ${membro.icone} me-1`} />
                          {membro.papel}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
