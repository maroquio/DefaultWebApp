import { useMemo, useState } from 'react'
import { api, ApiError } from '../../../lib/api'
import type { ConfigLista, SalvarConfigResultado } from '../../../lib/types'
import { useFetch } from '../../../hooks/useFetch'
import { toast } from '../../../store/uiStore'
import { TextField } from '../../../components/form/Field'
import Spinner from '../../../components/ui/Spinner'
import EmptyState from '../../../components/ui/EmptyState'

export default function AdminConfiguracoesPage() {
  const { data, carregando, erro, recarregar } = useFetch<ConfigLista>(
    (signal) => api.get('/admin/configuracoes', { signal }),
    [],
  )

  // Valores editados pelo usuário (chave -> valor). Vazio = nada alterado ainda.
  const [editados, setEditados] = useState<Record<string, string>>({})
  const [abaAtiva, setAbaAtiva] = useState(0)
  const [salvando, setSalvando] = useState(false)

  const categorias = data?.categorias ?? []

  const totalConfigs = useMemo(
    () => categorias.reduce((acc, c) => acc + c.itens.length, 0),
    [categorias],
  )

  // Mapa de valores originais por chave, para detectar alterações.
  const originais = useMemo(() => {
    const m: Record<string, string> = {}
    for (const cat of categorias) {
      for (const cfg of cat.itens) m[cfg.chave] = cfg.valor
    }
    return m
  }, [categorias])

  function valorAtual(chave: string): string {
    return chave in editados ? editados[chave] : (originais[chave] ?? '')
  }

  function alterar(chave: string, valor: string) {
    setEditados((prev) => ({ ...prev, [chave]: valor }))
  }

  const alteradas = Object.entries(editados).filter(
    ([chave, valor]) => valor !== (originais[chave] ?? ''),
  )

  async function salvar() {
    if (alteradas.length === 0) {
      toast.info('Nenhuma alteração para salvar.')
      return
    }
    setSalvando(true)
    try {
      const resultado = await api.put<SalvarConfigResultado>('/admin/configuracoes', {
        configs: alteradas.map(([chave, valor]) => ({ chave, valor })),
      })
      toast.sucesso(resultado.message || `${resultado.atualizadas} configuração(ões) salva(s).`)
      if (resultado.chaves_nao_encontradas?.length) {
        toast.aviso(`Chaves não encontradas: ${resultado.chaves_nao_encontradas.join(', ')}`)
      }
      setEditados({})
      recarregar()
    } catch (e) {
      if (e instanceof ApiError) toast.erro(e.message)
      else toast.erro((e as Error).message)
    } finally {
      setSalvando(false)
    }
  }

  if (carregando) return <Spinner />
  if (erro) return <div className="alert alert-danger">{erro.message}</div>

  const categoriaAtiva = categorias[abaAtiva]

  return (
    <div className="container-fluid">
      <div className="row mb-4">
        <div className="col-12">
          <h1 className="mb-0">
            <i className="bi bi-gear-fill" /> Configurações do Sistema
          </h1>
          <p className="text-muted mt-2 mb-0">
            Gerencie as configurações editáveis da aplicação. Total:{' '}
            <strong>{totalConfigs}</strong> configurações
          </p>
        </div>
      </div>

      {totalConfigs === 0 ? (
        <EmptyState
          icon="exclamation-triangle"
          titulo="Nenhuma configuração encontrada"
          mensagem="Não há configurações editáveis cadastradas no sistema."
        />
      ) : (
        <>
          {/* Navegação com Abas */}
          <ul className="nav nav-tabs mb-4" role="tablist">
            {categorias.map((cat, i) => (
              <li className="nav-item" role="presentation" key={cat.categoria}>
                <button
                  type="button"
                  className={`nav-link ${i === abaAtiva ? 'active' : ''}`}
                  onClick={() => setAbaAtiva(i)}
                  role="tab"
                  aria-selected={i === abaAtiva}
                >
                  <i className="bi bi-sliders" /> {cat.categoria}
                  <span className="badge bg-secondary ms-1">{cat.itens.length}</span>
                </button>
              </li>
            ))}
          </ul>

          {/* Conteúdo da aba ativa */}
          {categoriaAtiva && (
            <div className="row">
              {categoriaAtiva.itens.map((cfg) => (
                <div className="col-md-6" key={cfg.chave}>
                  <TextField
                    label={cfg.descricao || cfg.chave}
                    name={cfg.chave}
                    value={valorAtual(cfg.chave)}
                    onChange={(v) => alterar(cfg.chave, v)}
                    ajuda={cfg.descricao ? cfg.chave : undefined}
                  />
                </div>
              ))}
            </div>
          )}

          <div className="d-flex justify-content-between align-items-center mt-3">
            <small className="text-muted">
              {alteradas.length > 0
                ? `${alteradas.length} alteração(ões) pendente(s)`
                : 'Nenhuma alteração pendente'}
            </small>
            <button
              type="button"
              className="btn btn-primary btn-lg"
              onClick={salvar}
              disabled={salvando || alteradas.length === 0}
            >
              {salvando ? (
                <span className="spinner-border spinner-border-sm me-2" />
              ) : (
                <i className="bi bi-save me-2" />
              )}
              Salvar Configurações
            </button>
          </div>
        </>
      )}
    </div>
  )
}
