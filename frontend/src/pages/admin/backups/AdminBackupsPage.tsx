import { useState } from 'react'
import { api, ApiError } from '../../../lib/api'
import type { BackupInfo } from '../../../lib/types'
import { useFetch } from '../../../hooks/useFetch'
import { toast, useUIStore } from '../../../store/uiStore'
import { formatarBytes, formatarDataHora } from '../../../lib/format'
import { Badge } from '../../../components/ui/Badges'
import EmptyState from '../../../components/ui/EmptyState'
import Spinner from '../../../components/ui/Spinner'

export default function AdminBackupsPage() {
  const pedirConfirmacao = useUIStore((s) => s.pedirConfirmacao)
  const [criando, setCriando] = useState(false)

  const { data, carregando, erro, recarregar } = useFetch<BackupInfo[]>(
    (signal) => api.get('/admin/backups', { signal }),
    [],
  )

  async function criarBackup() {
    setCriando(true)
    try {
      await api.post<BackupInfo>('/admin/backups')
      toast.sucesso('Backup criado com sucesso.')
      recarregar()
    } catch (e) {
      toast.erro(e instanceof ApiError ? e.message : 'Erro ao criar backup.')
    } finally {
      setCriando(false)
    }
  }

  function baixar(nome: string) {
    window.location.href = '/api/admin/backups/' + encodeURIComponent(nome) + '/download'
  }

  function restaurar(backup: BackupInfo) {
    pedirConfirmacao({
      titulo: 'Confirmar Restauração',
      mensagem: 'ATENÇÃO: Esta operação irá sobrescrever o banco de dados atual!',
      detalhes:
        `${backup.nome_arquivo} — criado em ${formatarDataHora(backup.data_criacao)}. ` +
        'Um backup de segurança do estado atual será criado automaticamente antes da restauração.',
      tipo: 'danger',
      textoConfirmar: 'Restaurar Backup',
      onConfirmar: async () => {
        try {
          await api.post(`/admin/backups/${encodeURIComponent(backup.nome_arquivo)}/restaurar`)
          toast.sucesso('Backup restaurado com sucesso.')
          recarregar()
        } catch (e) {
          toast.erro(e instanceof ApiError ? e.message : 'Erro ao restaurar backup.')
        }
      },
    })
  }

  function excluir(backup: BackupInfo) {
    pedirConfirmacao({
      titulo: 'Excluir Backup',
      mensagem: 'Você tem certeza que deseja excluir este backup?',
      detalhes: `${backup.nome_arquivo} — criado em ${formatarDataHora(backup.data_criacao)}`,
      tipo: 'danger',
      textoConfirmar: 'Excluir',
      onConfirmar: async () => {
        try {
          await api.delete(`/admin/backups/${encodeURIComponent(backup.nome_arquivo)}`)
          toast.sucesso('Backup excluído com sucesso.')
          recarregar()
        } catch (e) {
          toast.erro(e instanceof ApiError ? e.message : 'Erro ao excluir backup.')
        }
      },
    })
  }

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>
            <i className="bi bi-database" /> Backup do Banco de Dados
          </h2>
          <button type="button" className="btn btn-primary" onClick={criarBackup} disabled={criando}>
            {criando ? (
              <>
                <span className="spinner-border spinner-border-sm me-1" role="status" /> Criando...
              </>
            ) : (
              <>
                <i className="bi bi-plus-circle" /> Criar Novo Backup
              </>
            )}
          </button>
        </div>

        <div className="alert alert-info" role="alert">
          <i className="bi bi-info-circle" /> <strong>Sobre os Backups:</strong>
          <ul className="mb-0 mt-2">
            <li>Os backups são cópias completas do banco de dados SQLite</li>
            <li>
              <strong>Backups Manuais:</strong> Criados por você ao clicar em "Criar Novo Backup"{' '}
              <Badge texto="Manual" cor="primary" icon="person-check" />
            </li>
            <li>
              <strong>Backups Automáticos:</strong> Criados automaticamente pelo sistema antes de
              restaurar outro backup <Badge texto="Automático" cor="warning text-dark" icon="shield-check" />
            </li>
            <li>
              <strong>IMPORTANTE:</strong> Ao restaurar um backup, um backup automático de segurança do
              estado atual é sempre criado antes da restauração
            </li>
            <li>Você pode baixar os arquivos de backup para armazenamento externo</li>
            <li>É recomendado manter backups manuais regulares do sistema</li>
          </ul>
        </div>

        <div className="card shadow-sm">
          <div className="card-body">
            {carregando ? (
              <Spinner />
            ) : erro ? (
              <div className="alert alert-danger mb-0">{erro.message}</div>
            ) : !data || data.length === 0 ? (
              <EmptyState
                icon="inbox"
                titulo="Nenhum backup encontrado"
                mensagem="Nenhum backup encontrado. Crie o primeiro backup!"
              />
            ) : (
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th scope="col">Arquivo</th>
                      <th scope="col" className="text-center">
                        Tipo
                      </th>
                      <th scope="col" className="text-center">
                        Data/Hora
                      </th>
                      <th scope="col" className="text-center">
                        Tamanho
                      </th>
                      <th scope="col" className="text-center">
                        Ações
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.map((backup) => (
                      <tr key={backup.nome_arquivo}>
                        <td>
                          <code>{backup.nome_arquivo}</code>
                        </td>
                        <td className="text-center">
                          {backup.tipo === 'automatico' ? (
                            <Badge texto="Automático" cor="warning text-dark" icon="shield-check" />
                          ) : (
                            <Badge texto="Manual" cor="primary" icon="person-check" />
                          )}
                        </td>
                        <td className="text-center">{formatarDataHora(backup.data_criacao)}</td>
                        <td className="text-center">
                          <Badge texto={formatarBytes(backup.tamanho_bytes)} cor="secondary" />
                        </td>
                        <td className="text-center">
                          <div className="btn-group btn-group-sm" role="group">
                            <button
                              type="button"
                              className="btn btn-outline-primary"
                              title="Baixar backup"
                              aria-label={`Baixar backup ${backup.nome_arquivo}`}
                              onClick={() => baixar(backup.nome_arquivo)}
                            >
                              <i className="bi bi-download" />
                            </button>
                            <button
                              type="button"
                              className="btn btn-outline-warning"
                              title="Restaurar backup"
                              aria-label={`Restaurar backup ${backup.nome_arquivo}`}
                              onClick={() => restaurar(backup)}
                            >
                              <i className="bi bi-arrow-clockwise" />
                            </button>
                            <button
                              type="button"
                              className="btn btn-outline-danger"
                              title="Excluir backup"
                              aria-label={`Excluir backup ${backup.nome_arquivo}`}
                              onClick={() => excluir(backup)}
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
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
