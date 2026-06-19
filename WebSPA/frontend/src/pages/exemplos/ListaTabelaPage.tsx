// Tabela com paginação em memória (portado de lista_tabela.html).
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import Pagination from '../../components/ui/Pagination'
import { useUIStore, toast } from '../../store/uiStore'
import { formatarMoeda } from '../../lib/format'

interface ProdutoDemo {
  id: number
  nome: string
  categoria: string
  preco: number
  estoque: number
  ativo: boolean
}

const PRODUTOS: ProdutoDemo[] = [
  { id: 1, nome: 'Notebook Pro 15', categoria: 'Informática', preco: 5499.9, estoque: 73, ativo: true },
  { id: 2, nome: 'Mouse Sem Fio', categoria: 'Acessórios', preco: 89.9, estoque: 34, ativo: true },
  { id: 3, nome: 'Teclado Mecânico', categoria: 'Acessórios', preco: 349.0, estoque: 12, ativo: true },
  { id: 4, nome: 'Monitor 27" 4K', categoria: 'Monitores', preco: 2199.0, estoque: 58, ativo: true },
  { id: 5, nome: 'Headset Gamer', categoria: 'Áudio', preco: 459.9, estoque: 8, ativo: false },
  { id: 6, nome: 'Webcam Full HD', categoria: 'Acessórios', preco: 279.0, estoque: 45, ativo: true },
  { id: 7, nome: 'SSD 1TB NVMe', categoria: 'Armazenamento', preco: 599.0, estoque: 90, ativo: true },
  { id: 8, nome: 'Hub USB-C', categoria: 'Acessórios', preco: 159.9, estoque: 22, ativo: false },
  { id: 9, nome: 'Cadeira Ergonômica', categoria: 'Móveis', preco: 1299.0, estoque: 15, ativo: true },
]

const POR_PAGINA = 3

function badgeEstoque(estoque: number) {
  if (estoque > 50) return <span className="badge bg-success">{estoque} un.</span>
  if (estoque > 20) return <span className="badge bg-warning text-dark">{estoque} un.</span>
  return <span className="badge bg-danger">{estoque} un.</span>
}

export default function ListaTabelaPage() {
  const [pagina, setPagina] = useState(1)
  const pedirConfirmacao = useUIStore((s) => s.pedirConfirmacao)
  const mostrarAlerta = useUIStore((s) => s.mostrarAlerta)

  const totalPaginas = Math.ceil(PRODUTOS.length / POR_PAGINA)
  const itens = useMemo(() => {
    const inicio = (pagina - 1) * POR_PAGINA
    return PRODUTOS.slice(inicio, inicio + POR_PAGINA)
  }, [pagina])

  const excluir = (p: ProdutoDemo) => {
    pedirConfirmacao({
      titulo: 'Excluir Produto',
      mensagem: `Tem certeza que deseja excluir "${p.nome}"?`,
      detalhes: `ID: ${p.id} • Categoria: ${p.categoria}`,
      tipo: 'danger',
      textoConfirmar: 'Excluir',
      onConfirmar: () => {
        toast.sucesso('Produto excluído com sucesso! (demonstração)')
      },
    })
  }

  return (
    <div className="container">
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2>
                <i className="bi bi-table" /> Exemplo de Tabela Responsiva
              </h2>
              <p className="text-muted mb-0">
                Demonstração de tabela com listagem de dados, badges de status e botões de ação
              </p>
            </div>
            <Link to="/exemplos" className="btn btn-outline-secondary">
              <i className="bi bi-arrow-left" /> Voltar
            </Link>
          </div>

          <div className="card shadow-sm">
            <div className="card-header bg-primary text-white">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">
                  <i className="bi bi-list-ul" /> Lista de Produtos
                </h5>
                <button
                  className="btn btn-light btn-sm"
                  onClick={() =>
                    mostrarAlerta({
                      titulo: 'Novo Produto',
                      mensagem: 'Exemplo de ação de adicionar produto.',
                      tipo: 'info',
                    })
                  }
                >
                  <i className="bi bi-plus-circle" /> Novo Produto
                </button>
              </div>
            </div>
            <div className="card-body">
              <div className="table-responsive">
                <table className="table table-hover align-middle">
                  <thead className="table-light">
                    <tr>
                      <th scope="col">ID</th>
                      <th scope="col">Nome</th>
                      <th scope="col">Categoria</th>
                      <th scope="col">Preço</th>
                      <th scope="col">Estoque</th>
                      <th scope="col">Status</th>
                      <th scope="col" className="text-center">
                        Ações
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {itens.map((p) => (
                      <tr key={p.id}>
                        <td>{p.id}</td>
                        <td>
                          <div className="d-flex align-items-center">
                            <i className="bi bi-box-seam text-primary me-2 fs-5" />
                            <strong>{p.nome}</strong>
                          </div>
                        </td>
                        <td>{p.categoria}</td>
                        <td>
                          <span className="text-success fw-bold">{formatarMoeda(p.preco)}</span>
                        </td>
                        <td>{badgeEstoque(p.estoque)}</td>
                        <td>
                          <span className={`badge ${p.ativo ? 'bg-success' : 'bg-secondary'}`}>
                            {p.ativo ? 'Ativo' : 'Inativo'}
                          </span>
                        </td>
                        <td className="text-center">
                          <div className="btn-group btn-group-sm" role="group">
                            <button
                              type="button"
                              className="btn btn-outline-info"
                              title="Visualizar"
                              aria-label={`Visualizar produto ${p.nome}`}
                              onClick={() =>
                                mostrarAlerta({
                                  titulo: `Visualizar: ${p.nome}`,
                                  mensagem: 'Exemplo de visualização de detalhes.',
                                  tipo: 'info',
                                })
                              }
                            >
                              <i className="bi bi-eye" />
                            </button>
                            <button
                              type="button"
                              className="btn btn-outline-primary"
                              title="Editar"
                              aria-label={`Editar produto ${p.nome}`}
                              onClick={() =>
                                mostrarAlerta({
                                  titulo: `Editar: ${p.nome}`,
                                  mensagem: 'Exemplo de edição de produto.',
                                  tipo: 'info',
                                })
                              }
                            >
                              <i className="bi bi-pencil" />
                            </button>
                            <button
                              type="button"
                              className="btn btn-outline-danger"
                              title="Excluir"
                              aria-label={`Excluir produto ${p.nome}`}
                              onClick={() => excluir(p)}
                            >
                              <i className="bi bi-trash" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-3">
                <Pagination pagina={pagina} totalPaginas={totalPaginas} onPagina={setPagina} />
              </div>
            </div>
          </div>

          <div className="card mt-4 border-primary">
            <div className="card-header bg-primary text-white">
              <h5 className="mb-0">
                <i className="bi bi-code-square" /> Recursos Demonstrados
              </h5>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-12 col-md-6">
                  <h6 className="text-primary">
                    <i className="bi bi-check2-circle" /> Componentes
                  </h6>
                  <ul className="small">
                    <li>
                      <code>table table-hover</code> - Tabela responsiva
                    </li>
                    <li>
                      <code>badge</code> - Badges de status coloridas
                    </li>
                    <li>
                      <code>btn-group</code> - Grupo de botões de ação
                    </li>
                    <li>
                      <code>Pagination</code> - Paginação em memória
                    </li>
                  </ul>
                </div>
                <div className="col-12 col-md-6">
                  <h6 className="text-primary">
                    <i className="bi bi-check2-circle" /> Funcionalidades
                  </h6>
                  <ul className="small">
                    <li>Listagem de dados em tabela</li>
                    <li>Badges de status condicionais (cores dinâmicas)</li>
                    <li>Formatação de valores monetários</li>
                    <li>Botões de ação (visualizar, editar, excluir)</li>
                    <li>Modal de confirmação para exclusão</li>
                    <li>
                      <strong>Paginação em memória</strong> ({POR_PAGINA} itens por página)
                    </li>
                  </ul>
                </div>
              </div>
              <hr />
              <div className="alert alert-warning mb-0">
                <i className="bi bi-lightbulb" /> <strong>Dica:</strong> Esta é uma demonstração com
                dados fictícios. Em uma aplicação real, os dados viriam da API.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
