// Detalhe de serviço profissional (portado de detalhes_servico.html).
import { Link } from 'react-router-dom'

interface Trabalho {
  seed: string
  titulo: string
  descricao: string
  tag: string
}

const PORTFOLIO: Trabalho[] = [
  { seed: 'work1', titulo: 'Redesign de E-commerce', descricao: 'Aumento de 35% nas conversões após redesign completo da interface.', tag: 'UI/UX' },
  { seed: 'work2', titulo: 'App Mobile Fitness', descricao: 'Design completo de aplicativo com mais de 50 telas.', tag: 'Mobile' },
  { seed: 'work3', titulo: 'Identidade Visual Startup', descricao: 'Branding completo incluindo logo, cores e guidelines.', tag: 'Branding' },
  { seed: 'work4', titulo: 'Dashboard Analytics', descricao: 'Interface de análise de dados com visualizações interativas.', tag: 'Dashboard' },
  { seed: 'work5', titulo: 'Site Institucional', descricao: 'Website responsivo com animações e interações customizadas.', tag: 'Web Design' },
  { seed: 'work6', titulo: 'Sistema SaaS', descricao: 'Design system completo para plataforma de gestão empresarial.', tag: 'SaaS' },
]

interface Depoimento {
  seed: string
  nome: string
  cargo: string
  data: string
  texto: string
}

const DEPOIMENTOS: Depoimento[] = [
  {
    seed: 'client1',
    nome: 'Ana Paula Costa',
    cargo: 'CEO - TechStart',
    data: '20/09/2024',
    texto:
      'Carlos é extremamente profissional e criativo. Entregou o projeto antes do prazo e superou todas as nossas expectativas. O redesign da nossa marca foi fundamental para nosso crescimento. Recomendo sem hesitar!',
  },
  {
    seed: 'client2',
    nome: 'Ricardo Mendes',
    cargo: 'Diretor de Marketing - ShopOnline',
    data: '15/09/2024',
    texto:
      'Trabalho impecável! O redesign do nosso e-commerce resultou em um aumento de 35% nas conversões. Carlos tem um olhar único para UX e entende profundamente as necessidades do negócio.',
  },
  {
    seed: 'client3',
    nome: 'Juliana Ferreira',
    cargo: 'Fundadora - HealthApp',
    data: '08/09/2024',
    texto:
      'Excelente comunicação e atenção aos detalhes. O design do nosso app ficou lindo e funcional. Já estamos planejando novos projetos juntos!',
  },
]

interface ProRelacionado {
  seed: string
  nome: string
  cargo: string
  estrelas: string
  avaliacoes: number
  preco: string
}

const OUTROS: ProRelacionado[] = [
  { seed: 'servpro1', nome: 'Marina Oliveira', cargo: 'Desenvolvedora Frontend', estrelas: '★★★★★', avaliacoes: 67, preco: 'R$ 120/h' },
  { seed: 'servpro2', nome: 'Pedro Santos', cargo: 'Fotógrafo Profissional', estrelas: '★★★★☆', avaliacoes: 134, preco: 'R$ 200/h' },
  { seed: 'servpro3', nome: 'Camila Rodrigues', cargo: 'Redatora & Copywriter', estrelas: '★★★★★', avaliacoes: 92, preco: 'R$ 80/h' },
  { seed: 'servpro4', nome: 'Lucas Almeida', cargo: 'Desenvolvedor Full Stack', estrelas: '★★★★★', avaliacoes: 156, preco: 'R$ 180/h' },
]

const ESPECIALIDADES = [
  'Design de Interfaces (UI)',
  'Experiência do Usuário (UX)',
  'Identidade Visual',
  'Design de Logotipos',
  'Prototipagem',
  'Design Responsivo',
]

const FERRAMENTAS = ['Figma', 'Adobe XD', 'Photoshop', 'Illustrator', 'Sketch', 'InVision', 'After Effects']

export default function DetalhesServicoPage() {
  return (
    <div className="container">
      <div className="row mb-4">
        <div className="col-12">
          <h1 className="display-4 mb-2">Detalhes do Serviço</h1>
          <p className="text-muted">
            Exemplo de página de detalhes de serviço profissional com portfólio e depoimentos.
          </p>
          <hr />
        </div>
      </div>

      <div className="row g-4 mb-5">
        <div className="col-12 col-md-6">
          <img
            src="https://picsum.photos/seed/servico-main/600/400"
            className="img-fluid rounded shadow-sm mb-3 w-100"
            alt="Carlos Eduardo Silva - Designer UI/UX"
          />
          <div className="row row-cols-4 g-2">
            {['servico-01', 'servico-02', 'servico-03', 'servico-04'].map((s) => (
              <div className="col" key={s}>
                <img
                  src={`https://picsum.photos/seed/${s}/150/150`}
                  className="img-fluid rounded border"
                  alt={`Miniatura ${s}`}
                />
              </div>
            ))}
          </div>
        </div>

        <div className="col-12 col-md-6">
          <div className="d-flex flex-column h-100">
            <div className="mb-3">
              <span className="badge bg-success me-2">
                <i className="bi bi-patch-check-fill" /> Verificado
              </span>
              <span className="badge bg-primary">Top Rated</span>
            </div>

            <h2 className="display-5 fw-bold mb-2">Carlos Eduardo Silva</h2>
            <p className="text-muted fs-5 mb-3">Designer Gráfico & UI/UX Designer</p>

            <div className="d-flex align-items-center mb-3">
              <div className="text-warning me-2">★★★★★</div>
              <span className="fw-bold me-2">5.0</span>
              <span className="text-muted">(89 avaliações)</span>
            </div>

            <div className="mb-4">
              <div className="d-flex align-items-center mb-2">
                <i className="bi bi-geo-alt-fill text-primary me-2" />
                <span>São Paulo, SP - Brasil</span>
              </div>
              <div className="d-flex align-items-center">
                <i className="bi bi-briefcase-fill text-primary me-2" />
                <span>8 anos de experiência</span>
              </div>
            </div>

            <div className="mb-4">
              <div className="display-4 fw-bold text-primary">
                R$ 150,00<span className="fs-5 text-muted">/hora</span>
              </div>
              <p className="text-muted">Pacotes a partir de R$ 1.200,00</p>
            </div>

            <p className="lead mb-4">
              Especialista em criar experiências digitais memoráveis. Trabalho com branding, design
              de interfaces e identidade visual para empresas de todos os tamanhos.
            </p>

            <div className="row g-3 mb-4">
              {[
                { valor: '127', label: 'Projetos' },
                { valor: '98%', label: 'Satisfação' },
                { valor: '45', label: 'Clientes' },
              ].map((s) => (
                <div className="col-4" key={s.label}>
                  <div className="text-center p-3 bg-light rounded">
                    <div className="display-6 fw-bold text-primary">{s.valor}</div>
                    <span className="text-muted small">{s.label}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="d-grid gap-3 mb-3">
              <button className="btn btn-primary btn-lg">
                <i className="bi bi-briefcase me-2" />
                Contratar Serviço
              </button>
              <button className="btn btn-outline-primary">
                <i className="bi bi-chat-dots me-2" />
                Enviar Mensagem
              </button>
            </div>

            <div className="text-muted small">
              <i className="bi bi-eye me-1" />
              567 visualizações esta semana
            </div>
          </div>
        </div>
      </div>

      <div className="row mb-5">
        <div className="col-12">
          <ul className="nav nav-tabs" role="tablist">
            <li className="nav-item" role="presentation">
              <button className="nav-link active" data-bs-toggle="tab" data-bs-target="#about" type="button" role="tab">
                <i className="bi bi-person me-2" />
                Sobre
              </button>
            </li>
            <li className="nav-item" role="presentation">
              <button className="nav-link" data-bs-toggle="tab" data-bs-target="#portfolio" type="button" role="tab">
                <i className="bi bi-images me-2" />
                Portfólio
              </button>
            </li>
            <li className="nav-item" role="presentation">
              <button className="nav-link" data-bs-toggle="tab" data-bs-target="#testimonials" type="button" role="tab">
                <i className="bi bi-chat-quote me-2" />
                Depoimentos (89)
              </button>
            </li>
          </ul>
          <div className="tab-content border border-top-0 p-4">
            <div className="tab-pane fade show active" id="about" role="tabpanel">
              <h4 className="mb-3">Sobre o Profissional</h4>
              <p>
                Olá! Sou Carlos Eduardo, designer gráfico e especialista em UI/UX com mais de 8 anos
                de experiência criando soluções visuais impactantes para marcas e empresas.
              </p>
              <p>
                Minha paixão é transformar ideias em designs funcionais e esteticamente agradáveis.
                Trabalho com metodologias ágeis e sempre busco entender profundamente as necessidades
                dos meus clientes.
              </p>
              <h5 className="mt-4 mb-3">Especialidades:</h5>
              <div className="row g-2">
                {ESPECIALIDADES.map((e) => (
                  <div className="col-md-6" key={e}>
                    <div className="d-flex align-items-center p-2 bg-light rounded">
                      <i className="bi bi-check-circle-fill text-success me-2" />
                      <span>{e}</span>
                    </div>
                  </div>
                ))}
              </div>
              <h5 className="mt-4 mb-3">Ferramentas:</h5>
              <div className="d-flex flex-wrap gap-3">
                {FERRAMENTAS.map((f) => (
                  <span className="badge bg-primary" key={f}>
                    {f}
                  </span>
                ))}
              </div>
            </div>

            <div className="tab-pane fade" id="portfolio" role="tabpanel">
              <h4 className="mb-3">Portfólio de Trabalhos</h4>
              <div className="row g-4">
                {PORTFOLIO.map((t) => (
                  <div className="col-md-4" key={t.seed}>
                    <div className="card">
                      <img
                        src={`https://picsum.photos/seed/${t.seed}/400/400`}
                        className="card-img-top"
                        alt={t.titulo}
                      />
                      <div className="card-body">
                        <h6 className="card-title">{t.titulo}</h6>
                        <p className="card-text small text-muted">{t.descricao}</p>
                        <span className="badge bg-info">{t.tag}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="tab-pane fade" id="testimonials" role="tabpanel">
              <h4 className="mb-4">Depoimentos de Clientes</h4>
              {DEPOIMENTOS.map((d) => (
                <div className="card mb-3" key={d.seed}>
                  <div className="card-body">
                    <div className="d-flex align-items-center mb-3">
                      <img
                        src={`https://picsum.photos/seed/${d.seed}/100/100`}
                        className="rounded-circle me-3"
                        width={60}
                        height={60}
                        alt={d.nome}
                      />
                      <div>
                        <h6 className="mb-0">{d.nome}</h6>
                        <span className="text-muted small">{d.cargo}</span>
                        <div className="text-warning small">★★★★★</div>
                      </div>
                      <span className="text-muted ms-auto">{d.data}</span>
                    </div>
                    <p className="mb-0">&ldquo;{d.texto}&rdquo;</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="row mb-4">
        <div className="col-12">
          <h3 className="mb-3">Outros Profissionais</h3>
          <hr />
        </div>
      </div>

      <div className="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
        {OUTROS.map((p) => (
          <div className="col" key={p.seed}>
            <div className="card h-100 shadow-sm shadow-hover">
              <img
                src={`https://picsum.photos/seed/${p.seed}/400/400`}
                className="card-img-top"
                alt={p.nome}
              />
              <div className="card-body">
                <h6 className="card-title">{p.nome}</h6>
                <p className="card-text small text-muted">{p.cargo}</p>
                <div className="text-warning small mb-2">
                  {p.estrelas} <span className="text-muted">({p.avaliacoes})</span>
                </div>
                <div className="fw-bold text-primary">{p.preco}</div>
              </div>
              <div className="card-footer bg-transparent border-top">
                <Link to="/exemplos/detalhes-servico" className="btn btn-sm btn-outline-primary w-100">
                  Ver Perfil
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
