import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { api, ApiError } from '../../../lib/api'
import type { PaginaResponse, Usuario } from '../../../lib/types'
import { Perfil } from '../../../lib/types'
import { useFetch } from '../../../hooks/useFetch'
import { toast, useUIStore } from '../../../store/uiStore'
import { formatarData } from '../../../lib/format'
import { PerfilBadge } from '../../../components/ui/Badges'
import Pagination from '../../../components/ui/Pagination'
import EmptyState from '../../../components/ui/EmptyState'
import Spinner from '../../../components/ui/Spinner'

const POR_PAGINA = 10

export default function AdminUsuariosListarPage() {
  const navigate = useNavigate()
  const pedirConfirmacao = useUIStore((s) => s.pedirConfirmacao)
  const [searchParams, setSearchParams] = useSearchParams()

  const pagina = Number(searchParams.get('pagina')) || 1
  const perfil = searchParams.get('perfil') ?? ''
  const q = searchParams.get('q') ?? ''

  const [busca, setBusca] = useState(q)

  const { data, carregando, erro, recarregar } = useFetch<PaginaResponse<Usuario>>(
    (signal) =>
      api.get('/admin/usuarios', {
        params: { pagina, por_pagina: POR_PAGINA, perfil: perfil || undefined, q: q || undefined },
        signal,
      }),
    [pagina, perfil, q],
  )

  function atualizarParams(next: Record<string, string | number | undefined>) {
    const params: Record<string, string> = {}
    if (q) params.q = q
    if (perfil) params.perfil = perfil
    if (pagina > 1) params.pagina = String(pagina)
    for (const [k, v] of Object.entries(next)) {
      if (v === undefined || v === '' || v === 0) delete params[k]
      else params[k] = String(v)
    }
    setSearchParams(params)
  }

  function aplicarFiltros(e: React.FormEvent) {
    e.preventDefault()
    atualizarParams({ q: busca.trim() || undefined, pagina: undefined })
  }

  function excluir(usuario: Usuario) {
    pedirConfirmacao({
      titulo: 'Excluir Usuário',
      mensagem: `Deseja realmente excluir o usuário ${usuario.nome}?`,
      detalhes: usuario.email,
      tipo: 'danger',
      textoConfirmar: 'Excluir',
      onConfirmar: async () => {
        try {
          await api.delete(`/admin/usuarios/${usuario.id}`)
          toast.sucesso('Usuário excluído com sucesso.')
          recarregar()
        } catch (e) {
          toast.erro(e instanceof ApiError ? e.message : 'Erro ao excluir usuário.')
        }
      },
    })
  }

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-people" /> Gerenciar Usuários
          </h2>
          <Link to="/admin/usuarios/cadastrar" className="btn btn-primary">
            <i className="bi bi-plus-circle" /> Novo Usuário
          </Link>
        </div>

        <div className="card shadow-sm mb-4">
          <div className="card-body">
            <form className="row g-2 align-items-end" onSubmit={aplicarFiltros}>
              <div className="col-md-6">
                <label htmlFor="q" className="form-label">
                  Buscar
                </label>
                <input
                  id="q"
                  type="text"
                  className="form-control"
                  placeholder="Nome ou email..."
                  value={busca}
                  onChange={(e) => setBusca(e.target.value)}
                />
              </div>
              <div className="col-md-4">
                <label htmlFor="perfil" className="form-label">
                  Perfil
                </label>
                <select
                  id="perfil"
                  className="form-select"
                  value={perfil}
                  onChange={(e) => atualizarParams({ perfil: e.target.value || undefined, pagina: undefined })}
                >
                  <option value="">Todos os perfis</option>
                  {Object.values(Perfil).map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </div>
              <div className="col-md-2 d-grid">
                <button type="submit" className="btn btn-outline-primary">
                  <i className="bi bi-search" /> Filtrar
                </button>
              </div>
            </form>
          </div>
        </div>

        <div className="card shadow-sm">
          <div className="card-body">
            {carregando ? (
              <Spinner />
            ) : erro ? (
              <div className="alert alert-danger mb-0">{erro.message}</div>
            ) : !data || data.items.length === 0 ? (
              <EmptyState
                icon="people"
                titulo="Nenhum usuário encontrado"
                mensagem="Nenhum usuário corresponde aos filtros aplicados."
              >
                <Link to="/admin/usuarios/cadastrar" className="btn btn-primary">
                  <i className="bi bi-plus-circle" /> Cadastrar Usuário
                </Link>
              </EmptyState>
            ) : (
              <>
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0">
                    <thead className="table-light">
                      <tr>
                        <th scope="col">ID</th>
                        <th scope="col">Nome</th>
                        <th scope="col">Email</th>
                        <th scope="col">Perfil</th>
                        <th scope="col">Data Cadastro</th>
                        <th scope="col" className="text-center">
                          Ações
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.items.map((usuario) => (
                        <tr key={usuario.id}>
                          <td>{usuario.id}</td>
                          <td>{usuario.nome}</td>
                          <td>{usuario.email}</td>
                          <td>
                            <PerfilBadge perfil={usuario.perfil} />
                          </td>
                          <td>{formatarData(usuario.data_cadastro)}</td>
                          <td className="text-center">
                            <div className="btn-group btn-group-sm" role="group">
                              <button
                                type="button"
                                className="btn btn-outline-primary"
                                title="Editar"
                                onClick={() => navigate(`/admin/usuarios/editar/${usuario.id}`)}
                              >
                                <i className="bi bi-pencil" />
                              </button>
                              <button
                                type="button"
                                className="btn btn-outline-danger"
                                title="Excluir"
                                onClick={() => excluir(usuario)}
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

                <div className="d-flex justify-content-between align-items-center mt-3">
                  <small className="text-muted">Total: {data.total} usuário(s)</small>
                  <Pagination
                    pagina={data.pagina}
                    totalPaginas={data.total_paginas}
                    onPagina={(p) => atualizarParams({ pagina: p })}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
