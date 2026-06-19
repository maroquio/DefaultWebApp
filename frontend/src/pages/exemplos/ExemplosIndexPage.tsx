// Galeria de exemplos (portado de templates/exemplos/index.html).
import { Link } from 'react-router-dom'

interface ExemploBadge {
  texto: string
  icon: string
  cor: string
}

interface ExemploCard {
  to: string
  icon: string
  titulo: string
  descricao: string
  badges: ExemploBadge[]
}

const EXEMPLOS: ExemploCard[] = [
  {
    to: '/exemplos/campos-formulario',
    icon: 'ui-checks',
    titulo: 'Campos de Formulário',
    descricao:
      'Demonstração completa dos campos de formulário reutilizáveis. Inclui inputs de texto, email, datas, textareas, selects e muito mais.',
    badges: [
      { texto: 'Componentes', icon: 'puzzle', cor: 'bg-primary' },
      { texto: 'React', icon: 'file-earmark-code', cor: 'bg-info text-dark' },
      { texto: 'Bootstrap', icon: 'bootstrap', cor: 'bg-success' },
    ],
  },
  {
    to: '/exemplos/grade-cartoes',
    icon: 'grid-3x3-gap',
    titulo: 'Grid de Cards Responsivo',
    descricao:
      'Exemplo de grid responsivo com cards do Bootstrap 5.3.8. Demonstra cards com imagens, títulos, descrições truncadas em 3 linhas, badges de status e botões de ação no rodapé.',
    badges: [
      { texto: 'Grid System', icon: 'grid', cor: 'bg-primary' },
      { texto: 'Cards', icon: 'card-heading', cor: 'bg-info text-dark' },
      { texto: 'Responsive', icon: 'phone', cor: 'bg-warning text-dark' },
    ],
  },
  {
    to: '/exemplos/lista-tabela',
    icon: 'table',
    titulo: 'Tabela de Listagem',
    descricao:
      'Exemplo completo de tabela responsiva para listagem de dados. Demonstra formatação de valores, badges de status condicionais, botões de ação agrupados e modal de confirmação de exclusão.',
    badges: [
      { texto: 'Table', icon: 'table', cor: 'bg-primary' },
      { texto: 'Badges', icon: 'badge-tm', cor: 'bg-info text-dark' },
      { texto: 'Actions', icon: 'ui-radios-grid', cor: 'bg-success' },
    ],
  },
  {
    to: '/exemplos/detalhes-produto',
    icon: 'cart3',
    titulo: 'Detalhe de Produto',
    descricao:
      'Página e-commerce com galeria de imagens, preço, estoque, garantia, abas de descrição, especificações e avaliações, além de produtos relacionados.',
    badges: [
      { texto: 'Galeria', icon: 'images', cor: 'bg-success' },
      { texto: 'Avaliação', icon: 'star', cor: 'bg-info text-dark' },
      { texto: 'Tabs', icon: 'folder', cor: 'bg-primary' },
    ],
  },
  {
    to: '/exemplos/detalhes-servico',
    icon: 'briefcase',
    titulo: 'Detalhe de Serviço',
    descricao:
      'Página de prestador de serviços com portfólio fotográfico, estatísticas de projetos e satisfação, abas de sobre, portfólio e depoimentos, e profissionais relacionados.',
    badges: [
      { texto: 'Portfólio', icon: 'images', cor: 'bg-success' },
      { texto: 'Avaliação', icon: 'star', cor: 'bg-info text-dark' },
      { texto: 'Tabs', icon: 'folder', cor: 'bg-primary' },
    ],
  },
  {
    to: '/exemplos/detalhes-perfil',
    icon: 'person-circle',
    titulo: 'Detalhe de Perfil',
    descricao:
      'Página de perfil de usuário com foto, contador de seguidores, redes sociais, abas de sobre, habilidades com barras de progresso, atividade recente e sugestões de conexão.',
    badges: [
      { texto: 'Skills', icon: 'bar-chart', cor: 'bg-success' },
      { texto: 'Atividade', icon: 'activity', cor: 'bg-info text-dark' },
      { texto: 'Social', icon: 'share', cor: 'bg-primary' },
    ],
  },
  {
    to: '/exemplos/detalhes-imovel',
    icon: 'house',
    titulo: 'Detalhe de Imóvel',
    descricao:
      'Página de imóvel com características (área, quartos, banheiros, vagas), abas de descrição, comodidades e localização, informações de bairro e imóveis similares.',
    badges: [
      { texto: 'Localização', icon: 'geo-alt', cor: 'bg-success' },
      { texto: 'Tabs', icon: 'folder', cor: 'bg-info text-dark' },
      { texto: 'Responsive', icon: 'phone', cor: 'bg-primary' },
    ],
  },
]

export default function ExemplosIndexPage() {
  return (
    <div className="container">
      <div className="row mb-4">
        <div className="col-12">
          <h1 className="display-4 mb-2">Exemplos de Componentes</h1>
          <p className="text-muted">
            Explore exemplos práticos de componentes e funcionalidades do sistema.
          </p>
          <hr />
        </div>
      </div>

      <div className="row g-4">
        {EXEMPLOS.map((ex) => (
          <div className="col-12 col-md-6 col-lg-4" key={ex.to}>
            <div className="card h-100 shadow-sm">
              <div className="card-body d-flex flex-column">
                <div className="mb-3">
                  <i className={`bi bi-${ex.icon} fs-1 text-primary`} />
                </div>
                <h5 className="card-title">{ex.titulo}</h5>
                <p className="card-text flex-grow-1">{ex.descricao}</p>
                <div className="mb-3">
                  {ex.badges.map((b) => (
                    <span className={`badge ${b.cor} me-1`} key={b.texto}>
                      <i className={`bi bi-${b.icon}`} /> {b.texto}
                    </span>
                  ))}
                </div>
              </div>
              <div className="card-footer bg-transparent border-top">
                <Link to={ex.to} className="btn btn-primary w-100">
                  <i className="bi bi-arrow-right-circle" /> Visitar Exemplo
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="row mt-5">
        <div className="col-12">
          <div className="alert alert-info border-start border-4 border-info">
            <h5 className="alert-heading">
              <i className="bi bi-info-circle-fill" /> Sobre os Exemplos
            </h5>
            <p className="mb-0">
              Estes exemplos demonstram componentes e padrões reutilizáveis utilizados no sistema.
              Você pode usar estes exemplos como referência para implementar funcionalidades
              similares em suas próprias páginas. Todos os exemplos utilizam Bootstrap 5.3.8 e seguem
              as melhores práticas de desenvolvimento web.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
