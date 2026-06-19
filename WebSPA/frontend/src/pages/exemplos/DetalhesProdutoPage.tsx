// Detalhe de produto e-commerce (portado de detalhes_produto.html).
import { Link } from 'react-router-dom'

interface Relacionado {
  seed: string
  nome: string
  estrelas: string
  avaliacoes: number
  preco: string
}

const RELACIONADOS: Relacionado[] = [
  { seed: 'prodrel1', nome: 'Fone Bluetooth Pro', estrelas: '★★★★★', avaliacoes: 89, preco: 'R$ 299,00' },
  { seed: 'prodrel2', nome: 'Carregador Rápido 65W', estrelas: '★★★★☆', avaliacoes: 156, preco: 'R$ 149,00' },
  { seed: 'prodrel3', nome: 'Capa Protetora Premium', estrelas: '★★★★★', avaliacoes: 203, preco: 'R$ 79,00' },
  { seed: 'prodrel4', nome: 'Película de Vidro 3D', estrelas: '★★★★☆', avaliacoes: 412, preco: 'R$ 49,00' },
]

const ESPECIFICACOES: [string, string][] = [
  ['Display', '6.8" AMOLED, 3200x1440px, 120Hz'],
  ['Processador', 'Qualcomm Snapdragon 8 Gen 3, Octa-core'],
  ['Memória RAM', '12GB LPDDR5'],
  ['Armazenamento', '256GB UFS 4.0'],
  ['Câmera Traseira', 'Tripla: 108MP + 12MP + 10MP'],
  ['Câmera Frontal', '32MP'],
  ['Bateria', '5000mAh, carregamento rápido 65W'],
  ['Sistema Operacional', 'Android 14'],
  ['Conectividade', '5G, Wi-Fi 6E, Bluetooth 5.3, NFC'],
  ['Dimensões', '163.3 x 77.9 x 8.9 mm'],
  ['Peso', '228g'],
]

const NOTAS: { estrela: string; cor: string; largura: string; qtd: number }[] = [
  { estrela: '5★', cor: 'bg-success', largura: '70%', qtd: 105 },
  { estrela: '4★', cor: 'bg-primary', largura: '20%', qtd: 30 },
  { estrela: '3★', cor: 'bg-warning', largura: '6%', qtd: 9 },
  { estrela: '2★', cor: 'bg-danger', largura: '3%', qtd: 4 },
  { estrela: '1★', cor: 'bg-dark', largura: '1%', qtd: 2 },
]

export default function DetalhesProdutoPage() {
  return (
    <div className="container">
      <div className="row mb-4">
        <div className="col-12">
          <h1 className="display-4 mb-2">Detalhes do Produto</h1>
          <p className="text-muted">
            Exemplo de página de detalhes de produto e-commerce com galeria de imagens e abas de
            informação.
          </p>
          <hr />
        </div>
      </div>

      <div className="row g-4 mb-5">
        <div className="col-12 col-md-6">
          <img
            src="https://picsum.photos/seed/produto-main/600/400"
            className="img-fluid rounded shadow-sm mb-3 w-100"
            alt="Smartphone Galaxy Ultra Pro"
          />
          <div className="row row-cols-4 g-2">
            {['produto-01', 'produto-02', 'produto-03', 'produto-04'].map((s) => (
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
              <span className="badge bg-success me-2">Em Estoque</span>
              <span className="badge bg-secondary">Eletrônicos</span>
            </div>

            <h2 className="display-5 fw-bold mb-2">Smartphone Galaxy Ultra Pro</h2>
            <p className="text-muted mb-3">Modelo 2024 - 256GB - 5G</p>

            <div className="d-flex align-items-center mb-3">
              <div className="text-warning me-2">
                <i className="bi bi-star-fill" />
                <i className="bi bi-star-fill" />
                <i className="bi bi-star-fill" />
                <i className="bi bi-star-fill" />
                <i className="bi bi-star-half" />
              </div>
              <span className="fw-bold me-2">4.5</span>
              <span className="text-muted">(150 avaliações)</span>
            </div>

            <div className="mb-4">
              <div className="d-flex align-items-baseline gap-3">
                <span className="text-muted text-decoration-line-through fs-5">R$ 3.999,00</span>
                <span className="badge bg-danger">-20%</span>
              </div>
              <div className="display-4 fw-bold text-primary">R$ 3.199,00</div>
              <p className="text-muted small">ou 12x de R$ 266,58 sem juros</p>
            </div>

            <p className="lead mb-4">
              Experimente o futuro com o Galaxy Ultra Pro. Tela AMOLED de 6.8", processador
              octa-core, câmera tripla de 108MP e bateria de longa duração. Perfeito para quem busca
              performance e estilo.
            </p>

            <div className="list-group list-group-flush mb-4">
              <div className="list-group-item d-flex justify-content-between align-items-center px-0">
                <span>
                  <i className="bi bi-box-seam me-2 text-primary" />
                  Estoque disponível
                </span>
                <span className="badge bg-success rounded-pill">23 unidades</span>
              </div>
              <div className="list-group-item d-flex justify-content-between align-items-center px-0">
                <span>
                  <i className="bi bi-truck me-2 text-primary" />
                  Frete grátis
                </span>
                <span className="badge bg-primary rounded-pill">Sul e Sudeste</span>
              </div>
              <div className="list-group-item d-flex justify-content-between align-items-center px-0">
                <span>
                  <i className="bi bi-shield-check me-2 text-primary" />
                  Garantia
                </span>
                <span className="badge bg-info rounded-pill">12 meses</span>
              </div>
            </div>

            <div className="d-grid gap-3 mb-3">
              <button className="btn btn-primary btn-lg">
                <i className="bi bi-cart-plus me-2" />
                Adicionar ao Carrinho
              </button>
              <button className="btn btn-outline-primary">
                <i className="bi bi-lightning-fill me-2" />
                Comprar Agora
              </button>
            </div>

            <div className="text-muted small">
              <i className="bi bi-eye me-1" />
              1.234 visualizações nas últimas 24h
            </div>
          </div>
        </div>
      </div>

      <div className="row mb-5">
        <div className="col-12">
          <ul className="nav nav-tabs" role="tablist">
            <li className="nav-item" role="presentation">
              <button
                className="nav-link active"
                data-bs-toggle="tab"
                data-bs-target="#description"
                type="button"
                role="tab"
              >
                <i className="bi bi-file-text me-2" />
                Descrição
              </button>
            </li>
            <li className="nav-item" role="presentation">
              <button
                className="nav-link"
                data-bs-toggle="tab"
                data-bs-target="#specs"
                type="button"
                role="tab"
              >
                <i className="bi bi-list-ul me-2" />
                Especificações
              </button>
            </li>
            <li className="nav-item" role="presentation">
              <button
                className="nav-link"
                data-bs-toggle="tab"
                data-bs-target="#reviews"
                type="button"
                role="tab"
              >
                <i className="bi bi-star me-2" />
                Avaliações (150)
              </button>
            </li>
          </ul>
          <div className="tab-content border border-top-0 p-4">
            <div className="tab-pane fade show active" id="description" role="tabpanel">
              <h4 className="mb-3">Descrição do Produto</h4>
              <p>
                O <strong>Smartphone Galaxy Ultra Pro</strong> representa o que há de mais moderno em
                tecnologia móvel. Com design premium em metal e vidro, este dispositivo combina
                elegância e resistência.
              </p>
              <h5 className="mt-4 mb-3">Principais Características:</h5>
              <ul className="list-unstyled">
                {[
                  'Tela AMOLED 6.8" com taxa de atualização de 120Hz',
                  'Processador Snapdragon 8 Gen 3 - Desempenho excepcional',
                  'Câmera tripla: 108MP + 12MP + 10MP',
                  'Bateria de 5000mAh com carregamento rápido 65W',
                  '256GB de armazenamento interno',
                  'Conectividade 5G para velocidades ultra-rápidas',
                ].map((item) => (
                  <li className="mb-2" key={item}>
                    <i className="bi bi-check-circle-fill text-success me-2" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            <div className="tab-pane fade" id="specs" role="tabpanel">
              <h4 className="mb-3">Especificações Técnicas</h4>
              <table className="table table-striped">
                <tbody>
                  {ESPECIFICACOES.map(([k, v]) => (
                    <tr key={k}>
                      <th scope="row" className="w-25">
                        {k}
                      </th>
                      <td>{v}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="tab-pane fade" id="reviews" role="tabpanel">
              <h4 className="mb-4">Avaliações dos Clientes</h4>
              <div className="row mb-4">
                <div className="col-md-4 text-center border-end">
                  <div className="display-3 fw-bold text-primary">4.5</div>
                  <div className="text-warning fs-4 mb-2">
                    <i className="bi bi-star-fill" />
                    <i className="bi bi-star-fill" />
                    <i className="bi bi-star-fill" />
                    <i className="bi bi-star-fill" />
                    <i className="bi bi-star-half" />
                  </div>
                  <p className="text-muted">150 avaliações</p>
                </div>
                <div className="col-md-8">
                  {NOTAS.map((n) => (
                    <div className="mb-2" key={n.estrela}>
                      <div className="d-flex align-items-center">
                        <span className="me-2">{n.estrela}</span>
                        <div className="progress flex-fill me-2" style={{ height: '20px' }}>
                          <div
                            className={`progress-bar ${n.cor}`}
                            role="progressbar"
                            style={{ width: n.largura }}
                          />
                        </div>
                        <span className="text-muted">{n.qtd}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <hr />
              <div className="mb-4">
                <div className="d-flex mb-2">
                  <div className="text-warning me-2">★★★★★</div>
                  <strong>João Silva</strong>
                  <span className="text-muted ms-auto">15/10/2024</span>
                </div>
                <h6>Excelente produto!</h6>
                <p className="text-muted">
                  O melhor smartphone que já tive. A câmera é incrível e a bateria dura o dia todo.
                  Recomendo muito!
                </p>
              </div>
              <div className="mb-4">
                <div className="d-flex mb-2">
                  <div className="text-warning me-2">★★★★☆</div>
                  <strong>Maria Santos</strong>
                  <span className="text-muted ms-auto">10/10/2024</span>
                </div>
                <h6>Muito bom, mas poderia melhorar</h6>
                <p className="text-muted">
                  Ótimo desempenho e tela linda. Único ponto negativo é o peso, um pouco pesado para
                  uso prolongado.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row mb-4">
        <div className="col-12">
          <h3 className="mb-3">Produtos Relacionados</h3>
          <hr />
        </div>
      </div>

      <div className="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
        {RELACIONADOS.map((r) => (
          <div className="col" key={r.seed}>
            <div className="card h-100 shadow-sm shadow-hover">
              <img
                src={`https://picsum.photos/seed/${r.seed}/400/400`}
                className="card-img-top"
                alt={r.nome}
              />
              <div className="card-body">
                <h6 className="card-title">{r.nome}</h6>
                <div className="text-warning small mb-2">
                  {r.estrelas} <span className="text-muted">({r.avaliacoes})</span>
                </div>
                <div className="fw-bold text-primary">{r.preco}</div>
              </div>
              <div className="card-footer bg-transparent border-top">
                <Link to="/exemplos/detalhes-produto" className="btn btn-sm btn-outline-primary w-100">
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
