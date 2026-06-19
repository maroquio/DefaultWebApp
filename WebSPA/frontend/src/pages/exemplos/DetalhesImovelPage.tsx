// Detalhe de imóvel (portado de detalhes_imovel.html).
import { Link } from 'react-router-dom'

interface Caracteristica {
  icon: string
  valor: string
  label: string
}

const CARACTERISTICAS: Caracteristica[] = [
  { icon: 'rulers', valor: '120m²', label: 'Área' },
  { icon: 'door-closed', valor: '3', label: 'Quartos' },
  { icon: 'droplet', valor: '2', label: 'Banheiros' },
  { icon: 'car-front', valor: '2', label: 'Vagas' },
]

const DESTAQUES = [
  'Sacada com vista para o mar',
  'Cozinha planejada e mobiliada',
  'Ar-condicionado em todos os quartos',
  'Armários embutidos',
]

const CARACTERISTICAS_GERAIS: [string, string][] = [
  ['Tipo', 'Apartamento'],
  ['Área Total', '120m²'],
  ['Quartos', '3 (1 suíte)'],
  ['Banheiros', '3'],
  ['Vagas de Garagem', '2 vagas cobertas'],
  ['Andar', '12º andar'],
  ['Elevadores', '3 elevadores'],
  ['Ano de Construção', '2015'],
]

const COMODIDADES = [
  'Ar-condicionado', 'Armários embutidos', 'Sacada', 'Vista para o mar',
  'Cozinha planejada', 'Piso porcelanato', 'Interfone', 'Gás encanado', 'Elevador', 'Portaria 24h',
]

const LAZER = ['Piscina', 'Academia', 'Sauna', 'Salão de festas', 'Playground', 'Churrasqueira']

interface Proximidade {
  icon: string
  titulo: string
  itens: string[]
}

const PROXIMIDADES: Proximidade[] = [
  {
    icon: 'shop',
    titulo: 'Comércio',
    itens: ['Shopping Cassino Atlântico - 500m', 'Supermercados - 200m', 'Farmácias - 100m', 'Restaurantes e cafés - ao redor'],
  },
  {
    icon: 'hospital',
    titulo: 'Saúde',
    itens: ['Hospital Samaritano - 1.2km', 'Clínica médica - 300m', 'Laboratórios - 400m', 'Academia - no condomínio'],
  },
  {
    icon: 'book',
    titulo: 'Educação',
    itens: ['Escola Municipal - 600m', 'Colégio Particular - 800m', 'Universidade - 2km', 'Biblioteca pública - 1km'],
  },
  {
    icon: 'bus-front',
    titulo: 'Transporte',
    itens: ['Metrô Cardeal Arcoverde - 800m', 'Ponto de ônibus - 50m', 'Táxi/Uber - fácil acesso', 'Aeroporto Santos Dumont - 8km'],
  },
]

interface Similar {
  seed: string
  nome: string
  bairro: string
  area: string
  quartos: string
  vagas: string
  preco: string
}

const SIMILARES: Similar[] = [
  { seed: 'imovelsim1', nome: 'Apartamento em Ipanema', bairro: 'Ipanema, RJ', area: '95m²', quartos: '2', vagas: '1', preco: 'R$ 1.450.000' },
  { seed: 'imovelsim2', nome: 'Cobertura Copacabana', bairro: 'Copacabana, RJ', area: '180m²', quartos: '4', vagas: '3', preco: 'R$ 2.850.000' },
  { seed: 'imovelsim3', nome: 'Apartamento Leblon', bairro: 'Leblon, RJ', area: '110m²', quartos: '3', vagas: '2', preco: 'R$ 2.100.000' },
  { seed: 'imovelsim4', nome: 'Apartamento Leme', bairro: 'Leme, RJ', area: '105m²', quartos: '3', vagas: '2', preco: 'R$ 1.650.000' },
]

export default function DetalhesImovelPage() {
  return (
    <div className="container">
      <div className="row mb-4">
        <div className="col-12">
          <h1 className="display-4 mb-2">Detalhes do Imóvel</h1>
          <p className="text-muted">
            Exemplo de página de detalhes de imóvel com características, localização e imóveis
            similares.
          </p>
          <hr />
        </div>
      </div>

      <div className="row g-4 mb-5">
        <div className="col-12 col-md-6">
          <img
            src="https://picsum.photos/seed/imovel-main/600/400"
            className="img-fluid rounded shadow-sm mb-3 w-100"
            alt="Vista externa do edifício em Copacabana"
          />
          <div className="row row-cols-4 g-2">
            {['imovel-01', 'imovel-02', 'imovel-03', 'imovel-04'].map((s) => (
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
              <span className="badge bg-primary me-2">Apartamento</span>
              <span className="badge bg-success">Disponível</span>
            </div>

            <h2 className="display-6 fw-bold mb-2">Apartamento Luxuoso com Vista para o Mar</h2>
            <p className="text-muted fs-5 mb-3">
              <i className="bi bi-geo-alt-fill me-1" />
              Av. Atlântica, 1500 - Copacabana, Rio de Janeiro - RJ
            </p>

            <div className="d-flex align-items-center mb-3">
              <div className="text-warning me-2">
                <i className="bi bi-star-fill" />
                <i className="bi bi-star-fill" />
                <i className="bi bi-star-fill" />
                <i className="bi bi-star-fill" />
                <i className="bi bi-star-half" />
              </div>
              <span className="fw-bold me-2">4.6</span>
              <span className="text-muted">Avaliação do bairro</span>
            </div>

            <div className="mb-4">
              <div className="display-4 fw-bold text-primary">R$ 1.850.000</div>
              <p className="text-muted mb-0">Valor de venda</p>
              <p className="text-muted small">Condomínio: R$ 1.200/mês • IPTU: R$ 450/mês</p>
            </div>

            <div className="row g-3 mb-4">
              {CARACTERISTICAS.map((c) => (
                <div className="col-3" key={c.label}>
                  <div className="text-center p-3 bg-light rounded">
                    <i className={`bi bi-${c.icon} fs-3 text-primary`} />
                    <div className="fw-bold mt-2">{c.valor}</div>
                    <small className="text-muted">{c.label}</small>
                  </div>
                </div>
              ))}
            </div>

            <p className="lead mb-4">
              Apartamento espetacular com vista privilegiada para o mar. Totalmente reformado com
              acabamentos de primeira linha. Localização nobre em Copacabana, próximo a comércio,
              transporte e lazer.
            </p>

            <div className="list-group list-group-flush mb-4">
              {DESTAQUES.map((d) => (
                <div className="list-group-item px-0 d-flex align-items-center" key={d}>
                  <i className="bi bi-check-circle-fill text-success me-2" />
                  <span>{d}</span>
                </div>
              ))}
            </div>

            <div className="d-grid gap-3 mb-3">
              <button className="btn btn-primary btn-lg">
                <i className="bi bi-calendar-check me-2" />
                Agendar Visita
              </button>
              <button className="btn btn-outline-primary">
                <i className="bi bi-file-earmark-text me-2" />
                Fazer Proposta
              </button>
            </div>

            <div className="text-muted small">
              <i className="bi bi-eye me-1" />
              432 visualizações nos últimos 7 dias
            </div>
          </div>
        </div>
      </div>

      <div className="row mb-5">
        <div className="col-12">
          <ul className="nav nav-tabs" role="tablist">
            <li className="nav-item" role="presentation">
              <button className="nav-link active" data-bs-toggle="tab" data-bs-target="#details" type="button" role="tab">
                <i className="bi bi-info-circle me-2" />
                Descrição
              </button>
            </li>
            <li className="nav-item" role="presentation">
              <button className="nav-link" data-bs-toggle="tab" data-bs-target="#features" type="button" role="tab">
                <i className="bi bi-list-check me-2" />
                Características
              </button>
            </li>
            <li className="nav-item" role="presentation">
              <button className="nav-link" data-bs-toggle="tab" data-bs-target="#location" type="button" role="tab">
                <i className="bi bi-pin-map me-2" />
                Localização
              </button>
            </li>
          </ul>
          <div className="tab-content border border-top-0 p-4">
            <div className="tab-pane fade show active" id="details" role="tabpanel">
              <h4 className="mb-3">Descrição Completa</h4>
              <p>
                Apartamento espetacular localizado em uma das áreas mais nobres de Copacabana, com
                vista privilegiada para o mar. Este imóvel único oferece uma combinação perfeita de
                localização, conforto e sofisticação.
              </p>
              <p>
                Totalmente reformado com materiais de alta qualidade, o apartamento conta com piso em
                porcelanato, iluminação em LED, e acabamentos modernos em todos os ambientes.
              </p>
              <h5 className="mt-4 mb-3">Ambientes:</h5>
              <ul>
                <li>
                  <strong>Sala de estar/jantar:</strong> Ampla e integrada, com sacada e vista para o mar
                </li>
                <li>
                  <strong>Cozinha:</strong> Planejada e totalmente equipada com eletrodomésticos de primeira linha
                </li>
                <li>
                  <strong>Suíte master:</strong> Closet, banheiro com hidromassagem e sacada privativa
                </li>
                <li>
                  <strong>2 Quartos:</strong> Com armários embutidos e ar-condicionado
                </li>
                <li>
                  <strong>2 Banheiros sociais:</strong> Revestimento em mármore e metais importados
                </li>
              </ul>
              <h5 className="mt-4 mb-3">Condomínio:</h5>
              <p>O edifício oferece infraestrutura completa de lazer e segurança:</p>
              <ul>
                <li>Portaria 24h com segurança</li>
                <li>Piscina adulto e infantil</li>
                <li>Sauna e sala de massagem</li>
                <li>Academia equipada</li>
                <li>Salão de festas e Playground</li>
              </ul>
            </div>

            <div className="tab-pane fade" id="features" role="tabpanel">
              <h4 className="mb-3">Características do Imóvel</h4>
              <div className="row">
                <div className="col-md-6">
                  <h5 className="mb-3">Características Gerais:</h5>
                  <table className="table table-sm">
                    <tbody>
                      {CARACTERISTICAS_GERAIS.map(([k, v]) => (
                        <tr key={k}>
                          <th scope="row" className="w-50">
                            {k}
                          </th>
                          <td>{v}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="col-md-6">
                  <h5 className="mb-3">Comodidades:</h5>
                  <div className="row g-2">
                    {COMODIDADES.map((c) => (
                      <div className="col-6" key={c}>
                        <div className="p-2 bg-light rounded small">
                          <i className="bi bi-check-circle-fill text-success me-1" />
                          {c}
                        </div>
                      </div>
                    ))}
                  </div>
                  <h5 className="mt-4 mb-3">Lazer:</h5>
                  <div className="row g-2">
                    {LAZER.map((l) => (
                      <div className="col-6" key={l}>
                        <div className="p-2 bg-light rounded small">
                          <i className="bi bi-check-circle-fill text-success me-1" />
                          {l}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="tab-pane fade" id="location" role="tabpanel">
              <h4 className="mb-3">Localização Privilegiada</h4>
              <div className="alert alert-info mb-4">
                <i className="bi bi-geo-alt-fill me-2" />
                <strong>Endereço:</strong> Av. Atlântica, 1500 - Copacabana, Rio de Janeiro - RJ,
                22021-001
              </div>
              <h5 className="mb-3">Região e Vizinhança:</h5>
              <p>
                Copacabana é um dos bairros mais famosos do Rio de Janeiro, conhecido mundialmente
                por sua praia, vida cultural vibrante e infraestrutura completa. O imóvel está
                localizado em uma das principais avenidas do bairro, com fácil acesso a transporte
                público, comércio e serviços.
              </p>
              <h5 className="mt-4 mb-3">Proximidades:</h5>
              <div className="row g-3">
                {PROXIMIDADES.map((p) => (
                  <div className="col-md-6" key={p.titulo}>
                    <div className="card">
                      <div className="card-body">
                        <h6 className="card-title">
                          <i className={`bi bi-${p.icon} text-primary me-2`} />
                          {p.titulo}
                        </h6>
                        <ul className="list-unstyled small mb-0">
                          {p.itens.map((item) => (
                            <li className="mb-1" key={item}>
                              • {item}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 p-3 bg-light rounded text-center">
                <i className="bi bi-map fs-1 text-primary" />
                <p className="mb-0 mt-2 text-muted">Mapa de localização seria exibido aqui</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row mb-4">
        <div className="col-12">
          <h3 className="mb-3">Imóveis Similares</h3>
          <hr />
        </div>
      </div>

      <div className="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
        {SIMILARES.map((s) => (
          <div className="col" key={s.seed}>
            <div className="card h-100 shadow-sm shadow-hover">
              <img
                src={`https://picsum.photos/seed/${s.seed}/400/400`}
                className="card-img-top"
                alt={s.nome}
              />
              <div className="card-body">
                <h6 className="card-title">{s.nome}</h6>
                <p className="card-text small text-muted">
                  <i className="bi bi-geo-alt me-1" />
                  {s.bairro}
                </p>
                <div className="small mb-2">
                  <span className="me-2">
                    <i className="bi bi-rulers me-1" />
                    {s.area}
                  </span>
                  <span className="me-2">
                    <i className="bi bi-door-closed me-1" />
                    {s.quartos}
                  </span>
                  <span>
                    <i className="bi bi-car-front me-1" />
                    {s.vagas}
                  </span>
                </div>
                <div className="fw-bold text-primary">{s.preco}</div>
              </div>
              <div className="card-footer bg-transparent border-top">
                <Link to="/exemplos/detalhes-imovel" className="btn btn-sm btn-outline-primary w-100">
                  Ver Detalhes
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
