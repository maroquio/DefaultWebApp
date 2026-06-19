// Detalhe de perfil de usuário (portado de detalhes_perfil.html).
import { Link } from 'react-router-dom'

interface Experiencia {
  cargo: string
  empresa: string
  periodo: string
  cor: string
  descricao: string
}

const EXPERIENCIAS: Experiencia[] = [
  {
    cargo: 'Engenheira de Software Sênior',
    empresa: 'TechCorp Solutions',
    periodo: '2021 - Atual',
    cor: 'bg-primary',
    descricao:
      'Liderança técnica de equipe, arquitetura de microsserviços, mentoria de desenvolvedores juniores.',
  },
  {
    cargo: 'Desenvolvedora Backend Pleno',
    empresa: 'StartupTech',
    periodo: '2018 - 2021',
    cor: 'bg-secondary',
    descricao:
      'Desenvolvimento de APIs RESTful, integração com serviços externos, otimização de performance.',
  },
  {
    cargo: 'Desenvolvedora Full Stack Júnior',
    empresa: 'WebSolutions',
    periodo: '2016 - 2018',
    cor: 'bg-secondary',
    descricao: 'Desenvolvimento web full stack, manutenção de sistemas legados, suporte técnico.',
  },
]

interface Skill {
  nome: string
  nivel: string
  cor: string
  largura: string
}

const SKILLS: Skill[] = [
  { nome: 'Python', nivel: 'Avançado', cor: 'bg-success', largura: '95%' },
  { nome: 'JavaScript/TypeScript', nivel: 'Avançado', cor: 'bg-success', largura: '85%' },
  { nome: 'Java', nivel: 'Intermediário', cor: 'bg-primary', largura: '70%' },
  { nome: 'Go', nivel: 'Intermediário', cor: 'bg-primary', largura: '65%' },
]

const TECNOLOGIAS = [
  'FastAPI', 'Django', 'Flask', 'React', 'Node.js', 'Docker', 'Kubernetes',
  'PostgreSQL', 'MongoDB', 'Redis', 'AWS', 'Git', 'CI/CD',
]

interface Certificacao {
  titulo: string
  origem: string
}

const CERTIFICACOES: Certificacao[] = [
  { titulo: 'AWS Certified Solutions Architect', origem: 'Amazon Web Services - 2023' },
  { titulo: 'Professional Scrum Master I', origem: 'Scrum.org - 2022' },
  { titulo: 'Python Institute PCPP1', origem: 'Python Institute - 2021' },
]

interface Atividade {
  icon: string
  cor: string
  titulo: string
  quando: string
  texto: string
  rodape: string
}

const ATIVIDADES: Atividade[] = [
  {
    icon: 'file-earmark-code',
    cor: 'bg-primary text-white',
    titulo: 'Publicou um artigo',
    quando: '2 horas atrás',
    texto: '"Arquitetura de Microsserviços com FastAPI e Docker"',
    rodape: '234 visualizações • 45 curtidas',
  },
  {
    icon: 'code-slash',
    cor: 'bg-success text-white',
    titulo: 'Contribuiu para projeto open source',
    quando: '1 dia atrás',
    texto: 'Pull Request aceito no projeto "awesome-fastapi"',
    rodape: 'Adicionou suporte para autenticação JWT',
  },
  {
    icon: 'trophy',
    cor: 'bg-warning text-dark',
    titulo: 'Conquistou uma nova conquista',
    quando: '3 dias atrás',
    texto: 'Código Limpo: 50 pull requests aprovados',
    rodape: 'Conquista Desbloqueada',
  },
  {
    icon: 'chat-dots',
    cor: 'bg-info text-white',
    titulo: 'Respondeu uma discussão',
    quando: '5 dias atrás',
    texto: '"Melhores práticas para testes em Python"',
    rodape: '12 curtidas • 3 respostas',
  },
]

interface Conexao {
  seed: string
  nome: string
  cargo: string
  comuns: number
}

const CONEXOES: Conexao[] = [
  { seed: 'perfilcon1', nome: 'Rafael Costa', cargo: 'DevOps Engineer', comuns: 15 },
  { seed: 'perfilcon2', nome: 'Amanda Silva', cargo: 'Data Scientist', comuns: 8 },
  { seed: 'perfilcon3', nome: 'Bruno Oliveira', cargo: 'Frontend Developer', comuns: 23 },
  { seed: 'perfilcon4', nome: 'Carolina Santos', cargo: 'Product Manager', comuns: 12 },
]

export default function DetalhesPerfilPage() {
  return (
    <div className="container">
      <div className="row mb-4">
        <div className="col-12">
          <h1 className="display-4 mb-2">Perfil do Usuário</h1>
          <p className="text-muted">
            Exemplo de página de perfil de pessoa com informações, habilidades e atividades recentes.
          </p>
          <hr />
        </div>
      </div>

      <div className="row g-4 mb-5">
        <div className="col-12 col-md-6">
          <img
            src="https://picsum.photos/seed/perfil-01/600/400"
            className="img-fluid rounded shadow-sm w-100"
            alt="Foto de Perfil de Fernanda Almeida"
          />
        </div>

        <div className="col-12 col-md-6">
          <div className="d-flex flex-column h-100">
            <div className="mb-3">
              <span className="badge bg-success me-2">
                <i className="bi bi-circle-fill" /> Online
              </span>
              <span className="badge bg-warning text-dark">
                <i className="bi bi-patch-check-fill" /> Membro Premium
              </span>
            </div>

            <h2 className="display-5 fw-bold mb-2">Fernanda Almeida</h2>
            <p className="text-muted fs-5 mb-3">Engenheira de Software Sênior</p>

            <div className="d-flex align-items-center mb-3">
              <div className="text-warning me-2">
                <i className="bi bi-star-fill" />
                <i className="bi bi-star-fill" />
                <i className="bi bi-star-fill" />
                <i className="bi bi-star-fill" />
                <i className="bi bi-star-half" />
              </div>
              <span className="fw-bold me-2">4.7</span>
              <span className="text-muted">Reputação na comunidade</span>
            </div>

            <div className="mb-4">
              <div className="d-flex align-items-center mb-2">
                <i className="bi bi-geo-alt-fill text-primary me-2" />
                <span>Rio de Janeiro, RJ - Brasil</span>
              </div>
              <div className="d-flex align-items-center mb-2">
                <i className="bi bi-building text-primary me-2" />
                <span>TechCorp Solutions</span>
              </div>
              <div className="d-flex align-items-center">
                <i className="bi bi-calendar-check text-primary me-2" />
                <span>Membro desde Janeiro 2020</span>
              </div>
            </div>

            <p className="lead mb-4">
              Apaixonada por tecnologia e inovação. Especializada em desenvolvimento backend com
              Python e arquitetura de microsserviços. Contribuo ativamente para projetos open source
              e adoro compartilhar conhecimento através de artigos e palestras.
            </p>

            <div className="row g-3 mb-4">
              {[
                { valor: '234', label: 'Seguidores' },
                { valor: '189', label: 'Seguindo' },
                { valor: '67', label: 'Posts' },
              ].map((s) => (
                <div className="col-4" key={s.label}>
                  <div className="text-center p-3 bg-light rounded">
                    <div className="display-6 fw-bold text-primary">{s.valor}</div>
                    <small className="text-muted">{s.label}</small>
                  </div>
                </div>
              ))}
            </div>

            <div className="mb-4">
              <p className="small text-muted mb-2">Redes Sociais:</p>
              <div className="d-flex gap-3">
                {['github', 'linkedin', 'twitter', 'globe'].map((rede) => (
                  <a href="#" className="btn btn-outline-primary btn-sm" key={rede}>
                    <i className={`bi bi-${rede}`} />
                  </a>
                ))}
              </div>
            </div>

            <div className="d-grid gap-3 mb-3">
              <button className="btn btn-primary btn-lg">
                <i className="bi bi-person-plus me-2" />
                Conectar
              </button>
              <button className="btn btn-outline-primary">
                <i className="bi bi-envelope me-2" />
                Enviar Mensagem
              </button>
            </div>

            <div className="text-muted small">
              <i className="bi bi-eye me-1" />
              893 visualizações do perfil este mês
            </div>
          </div>
        </div>
      </div>

      <div className="row mb-5">
        <div className="col-12">
          <ul className="nav nav-tabs" role="tablist">
            <li className="nav-item" role="presentation">
              <button className="nav-link active" data-bs-toggle="tab" data-bs-target="#bio" type="button" role="tab">
                <i className="bi bi-person me-2" />
                Sobre
              </button>
            </li>
            <li className="nav-item" role="presentation">
              <button className="nav-link" data-bs-toggle="tab" data-bs-target="#skills" type="button" role="tab">
                <i className="bi bi-award me-2" />
                Habilidades
              </button>
            </li>
            <li className="nav-item" role="presentation">
              <button className="nav-link" data-bs-toggle="tab" data-bs-target="#activity" type="button" role="tab">
                <i className="bi bi-activity me-2" />
                Atividades Recentes
              </button>
            </li>
          </ul>
          <div className="tab-content border border-top-0 p-4">
            <div className="tab-pane fade show active" id="bio" role="tabpanel">
              <h4 className="mb-3">Sobre Mim</h4>
              <p>
                Sou uma desenvolvedora apaixonada por criar soluções elegantes para problemas
                complexos. Com mais de 8 anos de experiência na área de desenvolvimento de software,
                já trabalhei em diversos projetos desafiadores que envolvem desde aplicações web até
                sistemas distribuídos em larga escala.
              </p>
              <p>
                Acredito fortemente em código limpo, testes automatizados e colaboração em equipe.
                Busco sempre aprender novas tecnologias e compartilhar conhecimento com a comunidade.
              </p>
              <h5 className="mt-4 mb-3">Experiência Profissional:</h5>
              {EXPERIENCIAS.map((exp) => (
                <div className="mb-4" key={exp.cargo}>
                  <div className="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 className="mb-0">{exp.cargo}</h6>
                      <p className="text-muted mb-1">{exp.empresa}</p>
                    </div>
                    <span className={`badge ${exp.cor}`}>{exp.periodo}</span>
                  </div>
                  <p className="small">{exp.descricao}</p>
                </div>
              ))}
              <h5 className="mt-4 mb-3">Formação Acadêmica:</h5>
              <div className="mb-3">
                <h6 className="mb-0">Bacharelado em Ciência da Computação</h6>
                <p className="text-muted mb-0">Universidade Federal do Rio de Janeiro</p>
                <p className="small text-muted">2012 - 2016</p>
              </div>
            </div>

            <div className="tab-pane fade" id="skills" role="tabpanel">
              <h4 className="mb-3">Habilidades Técnicas</h4>
              <h5 className="mb-3">Linguagens de Programação:</h5>
              <div className="mb-4">
                {SKILLS.map((s) => (
                  <div className="mb-3" key={s.nome}>
                    <div className="d-flex justify-content-between mb-1">
                      <span>{s.nome}</span>
                      <span className="text-muted">{s.nivel}</span>
                    </div>
                    <div className="progress" style={{ height: '25px' }}>
                      <div
                        className={`progress-bar ${s.cor}`}
                        role="progressbar"
                        style={{ width: s.largura }}
                      >
                        {s.largura}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <h5 className="mb-3">Tecnologias e Frameworks:</h5>
              <div className="d-flex flex-wrap gap-3 mb-4">
                {TECNOLOGIAS.map((t) => (
                  <span className="badge bg-primary" key={t}>
                    {t}
                  </span>
                ))}
              </div>
              <h5 className="mb-3">Certificações:</h5>
              <div className="list-group list-group-flush">
                {CERTIFICACOES.map((c) => (
                  <div className="list-group-item px-0" key={c.titulo}>
                    <div className="d-flex align-items-center">
                      <i className="bi bi-award-fill text-warning fs-3 me-3" />
                      <div className="flex-fill">
                        <h6 className="mb-0">{c.titulo}</h6>
                        <small className="text-muted">{c.origem}</small>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="tab-pane fade" id="activity" role="tabpanel">
              <h4 className="mb-4">Atividades Recentes</h4>
              <div className="list-group list-group-flush">
                {ATIVIDADES.map((a) => (
                  <div className="list-group-item px-0" key={a.titulo}>
                    <div className="d-flex">
                      <div className="me-3">
                        <div
                          className={`${a.cor} rounded-circle d-flex align-items-center justify-content-center`}
                          style={{ width: '48px', height: '48px' }}
                        >
                          <i className={`bi bi-${a.icon}`} />
                        </div>
                      </div>
                      <div className="flex-fill">
                        <div className="d-flex justify-content-between">
                          <h6 className="mb-1">{a.titulo}</h6>
                          <small className="text-muted">{a.quando}</small>
                        </div>
                        <p className="mb-1">{a.texto}</p>
                        <small className="text-muted">{a.rodape}</small>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row mb-4">
        <div className="col-12">
          <h3 className="mb-3">Pessoas que Você Pode Conhecer</h3>
          <hr />
        </div>
      </div>

      <div className="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
        {CONEXOES.map((c) => (
          <div className="col" key={c.seed}>
            <div className="card h-100 shadow-sm">
              <img
                src={`https://picsum.photos/seed/${c.seed}/400/400`}
                className="card-img-top"
                alt={c.nome}
              />
              <div className="card-body text-center">
                <h6 className="card-title">{c.nome}</h6>
                <p className="card-text small text-muted">{c.cargo}</p>
                <p className="small text-muted mb-2">
                  <i className="bi bi-people me-1" />
                  {c.comuns} conexões em comum
                </p>
              </div>
              <div className="card-footer bg-transparent border-top">
                <Link to="/exemplos/detalhes-perfil" className="btn btn-sm btn-outline-primary w-100">
                  <i className="bi bi-person-plus me-1" />
                  Conectar
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
