// Grid de cards responsivo (portado de grade_cartoes.html).
import { Link } from 'react-router-dom'

interface CartaoDemo {
  seed: string
  titulo: string
  descricao: string
  status: { texto: string; cor: string }
}

const CARTOES: CartaoDemo[] = [
  {
    seed: 'card1',
    titulo: 'Projeto Alpha',
    descricao:
      'Este é um projeto inovador que está transformando a maneira como as pessoas interagem com a tecnologia. Com funcionalidades avançadas e interface intuitiva, o Projeto Alpha representa o futuro do desenvolvimento web. Milhares de usuários já estão aproveitando seus benefícios diariamente.',
    status: { texto: 'Ativo', cor: 'bg-success' },
  },
  {
    seed: 'card2',
    titulo: 'Sistema Beta',
    descricao:
      'O Sistema Beta oferece uma solução completa para gerenciamento empresarial. Com módulos integrados de controle financeiro, estoque e vendas, você terá total controle do seu negócio. A plataforma é constantemente atualizada com novas funcionalidades baseadas no feedback dos usuários.',
    status: { texto: 'Em Desenvolvimento', cor: 'bg-warning text-dark' },
  },
  {
    seed: 'card3',
    titulo: 'Plataforma Gamma',
    descricao:
      'A Plataforma Gamma é a escolha perfeita para equipes que precisam de colaboração em tempo real. Com recursos de comunicação integrados, compartilhamento de arquivos e gestão de projetos, sua equipe será mais produtiva do que nunca. Experimente gratuitamente por 30 dias!',
    status: { texto: 'Ativo', cor: 'bg-success' },
  },
  {
    seed: 'card4',
    titulo: 'Aplicativo Delta',
    descricao:
      'O Aplicativo Delta revoluciona a forma como você organiza suas categorias diárias. Com sincronização em nuvem, notificações inteligentes e interface minimalista, você terá tudo que precisa ao alcance das mãos. Disponível para iOS e Android.',
    status: { texto: 'Pausado', cor: 'bg-danger' },
  },
  {
    seed: 'card5',
    titulo: 'Framework Epsilon',
    descricao:
      'Framework Epsilon é a base perfeita para construir aplicações web modernas e escaláveis. Com arquitetura modular, documentação completa e comunidade ativa, você poderá desenvolver projetos incríveis em tempo recorde. Totalmente open source!',
    status: { texto: 'Ativo', cor: 'bg-success' },
  },
  {
    seed: 'card6',
    titulo: 'API Omega',
    descricao:
      'A API Omega fornece acesso a dados em tempo real de múltiplas fontes através de uma interface RESTful simples e poderosa. Com autenticação segura, rate limiting inteligente e documentação interativa, integrar sua aplicação nunca foi tão fácil. Planos gratuitos e pagos disponíveis.',
    status: { texto: 'Beta Público', cor: 'bg-info text-dark' },
  },
  {
    seed: 'card7',
    titulo: 'Dashboard Analytics',
    descricao:
      'Visualize dados complexos de forma simples e intuitiva com nosso dashboard de analytics. Gráficos interativos, relatórios personalizados e insights em tempo real. Integração com múltiplas fontes de dados e exportação em diversos formatos.',
    status: { texto: 'Ativo', cor: 'bg-success' },
  },
  {
    seed: 'card8',
    titulo: 'CRM Suite',
    descricao:
      'Gerencie relacionamentos com clientes de forma eficiente e organizada. Acompanhe vendas, oportunidades e histórico de interações em um único lugar. Automação de marketing e funil de vendas personalizável inclusos.',
    status: { texto: 'Em Desenvolvimento', cor: 'bg-warning text-dark' },
  },
  {
    seed: 'card9',
    titulo: 'E-commerce Platform',
    descricao:
      'Plataforma completa de e-commerce com carrinho de compras, checkout seguro e gestão de produtos. Múltiplas formas de pagamento, controle de estoque e painel administrativo completo. Responsivo e otimizado para conversão em todos os dispositivos.',
    status: { texto: 'Ativo', cor: 'bg-success' },
  },
  {
    seed: 'card10',
    titulo: 'Learning Management',
    descricao:
      'Sistema de gestão de aprendizagem para cursos online e treinamentos corporativos. Videoaulas, quizzes interativos, certificados automáticos e acompanhamento de progresso. Gamificação e sistema de pontos para aumentar o engajamento dos alunos.',
    status: { texto: 'Beta Público', cor: 'bg-info text-dark' },
  },
  {
    seed: 'card11',
    titulo: 'Task Manager Pro',
    descricao:
      'Gerencie projetos e categorias com metodologias ágeis como Kanban e Scrum. Quadros personalizáveis, sprints, backlogs e relatórios de produtividade. Colaboração em tempo real com notificações e comentários em cada categoria.',
    status: { texto: 'Ativo', cor: 'bg-success' },
  },
  {
    seed: 'card12',
    titulo: 'Cloud Storage',
    descricao:
      'Armazenamento em nuvem seguro e escalável para seus arquivos e documentos. Sincronização automática entre dispositivos, compartilhamento com controle de permissões. Backup automático, versionamento de arquivos e recuperação de dados excluídos.',
    status: { texto: 'Pausado', cor: 'bg-danger' },
  },
]

export default function GradeCartoesPage() {
  return (
    <div className="container">
      <div className="row mb-4">
        <div className="col-12">
          <h1 className="display-4 mb-2">Grid de Cards Responsivo</h1>
          <p className="text-muted">
            Exemplo de grid de cards usando Bootstrap 5.3.8 com imagens, títulos, descrições
            truncadas, status e botões de ação.
          </p>
          <hr />
        </div>
      </div>

      <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 row-cols-xl-4 row-cols-xxl-6 g-4">
        {CARTOES.map((c) => (
          <div className="col" key={c.seed}>
            <div className="card h-100 shadow-sm">
              <img
                src={`https://picsum.photos/seed/${c.seed}/400/400`}
                className="card-img-top"
                alt={c.titulo}
              />
              <div className="card-body d-flex flex-column">
                <h5 className="card-title">{c.titulo}</h5>
                <p className="card-text line-clamp-3 flex-grow-1">{c.descricao}</p>
                <div className="mb-3">
                  <span className={`badge ${c.status.cor}`}>{c.status.texto}</span>
                </div>
              </div>
              <div className="card-footer bg-transparent border-top">
                <Link to="/exemplos/detalhes-produto" className="btn btn-primary w-100">
                  Ver Detalhes
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="row mt-5">
        <div className="col-12">
          <div className="alert alert-info">
            <h5 className="alert-heading">
              <i className="bi bi-info-circle" /> Recursos Utilizados
            </h5>
            <ul className="mb-0">
              <li>
                <strong>Grid System:</strong> <code>row-cols-1</code>, <code>row-cols-md-2</code>,{' '}
                <code>row-cols-lg-3</code>, <code>row-cols-xl-4</code>, <code>row-cols-xxl-6</code>
              </li>
              <li>
                <strong>Cards:</strong> <code>card</code>, <code>card-img-top</code>,{' '}
                <code>card-body</code>, <code>card-title</code>, <code>card-text</code>,{' '}
                <code>card-footer</code>
              </li>
              <li>
                <strong>Custom CSS:</strong> <code>line-clamp-3</code> para truncar texto em 3 linhas
              </li>
              <li>
                <strong>Breakpoints:</strong> 1 coluna (≤sm), 2 colunas (≥md), 3 colunas (≥lg), 4
                colunas (≥xl), 6 colunas (≥xxl)
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
