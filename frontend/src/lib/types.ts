// Tipos TypeScript espelhando os schemas de resposta do backend (dtos/responses/).
// Enums são strings de valor (ex: "Aberto", "Administrador"), nunca índices.

// ===== Enums de domínio =====
export const Perfil = {
  ADMIN: 'Administrador',
  CLIENTE: 'Cliente',
  VENDEDOR: 'Vendedor',
} as const
export type PerfilValor = (typeof Perfil)[keyof typeof Perfil]

export const StatusChamado = {
  ABERTO: 'Aberto',
  EM_ANALISE: 'Em Análise',
  RESOLVIDO: 'Resolvido',
  FECHADO: 'Fechado',
} as const
export type StatusChamadoValor = (typeof StatusChamado)[keyof typeof StatusChamado]

export const PrioridadeChamado = {
  BAIXA: 'Baixa',
  MEDIA: 'Média',
  ALTA: 'Alta',
  URGENTE: 'Urgente',
} as const
export type PrioridadeValor = (typeof PrioridadeChamado)[keyof typeof PrioridadeChamado]

export const StatusPagamento = {
  PENDENTE: 'Pendente',
  EM_PROCESSAMENTO: 'Em Processamento',
  APROVADO: 'Aprovado',
  RECUSADO: 'Recusado',
  CANCELADO: 'Cancelado',
  REEMBOLSADO: 'Reembolsado',
} as const
export type StatusPagamentoValor = (typeof StatusPagamento)[keyof typeof StatusPagamento]

export type TipoNotificacao = 'info' | 'sucesso' | 'aviso' | 'erro'
export type TipoInteracao = 'ABERTURA' | 'RESPOSTA_USUARIO' | 'RESPOSTA_ADMIN'

// ===== Comuns =====
export interface MensagemResponse {
  message: string
}
export interface TokenCsrfResponse {
  token: string
}
export interface PaginaResponse<T> {
  items: T[]
  pagina: number
  por_pagina: number
  total: number
  total_paginas: number
}

// ===== Usuário =====
export interface Usuario {
  id: number
  nome: string
  email: string
  perfil: string
  foto_url: string
  data_cadastro: string
  data_atualizacao?: string | null
}
export interface DashboardData {
  chamados_pendentes?: number | null
  chamados_abertos?: number | null
}

// ===== Chamados =====
export interface ChamadoInteracao {
  id: number
  usuario_id: number
  mensagem: string
  tipo: TipoInteracao
  data_interacao: string
  status_resultante?: string | null
  lida_em?: string | null
}
export interface Chamado {
  id: number
  titulo: string
  status: string
  prioridade: string
  usuario_id: number
  data_abertura: string
  data_fechamento?: string | null
  interacoes?: ChamadoInteracao[]
  // Campos auxiliares que algumas listagens podem trazer:
  nome_usuario?: string
  mensagens_nao_lidas?: number
  tem_resposta_admin?: boolean
}

// ===== Notificações =====
export interface Notificacao {
  id: number
  usuario_id: number
  titulo: string
  mensagem: string
  tipo: TipoNotificacao
  url_acao?: string | null
  data_criacao: string
  lida: boolean
  lida_em?: string | null
}
export interface NaoLidasResumo {
  total: number
  items: { id: number; titulo: string; tipo: TipoNotificacao }[]
}

// ===== Pagamentos =====
export interface Pagamento {
  id: number
  usuario_id: number
  descricao: string
  valor: number
  status: string
  provider?: string | null
  preference_id?: string | null
  payment_id?: string | null
  url_checkout?: string | null
  data_criacao: string
  data_atualizacao?: string | null
}
export interface CriarPagamentoResultado {
  init_point: string
  pagamento_id: number
}
export interface DadosProvider {
  pagamento: Pagamento
  provider_nome: string
  dados_provider: Record<string, unknown>
}

// ===== Chat =====
export interface ChatSala {
  id: number
  criada_em: string
  ultima_atividade: string
}
export interface ChatMensagem {
  id: number
  sala_id: number
  usuario_id: number
  mensagem: string
  data_envio: string
  lida_em?: string | null
}
export interface Conversa {
  sala_id: number
  outro_usuario: { id: number; nome: string; foto_url: string }
  ultima_mensagem: { mensagem: string; data_envio?: string | null }
  nao_lidas: number
  ultima_atividade: string
}
export interface UsuarioBusca {
  id: number
  nome: string
  foto_url?: string
}

// ===== Configurações / Auditoria / Backups =====
export interface ConfigItem {
  chave: string
  valor: string
  descricao?: string
  categoria?: string
}
export interface ConfigCategoria {
  categoria: string
  itens: ConfigItem[]
}
export interface ConfigLista {
  total: number
  categorias: ConfigCategoria[]
}
export interface SalvarConfigResultado {
  atualizadas: number
  chaves_nao_encontradas: string[]
  message: string
}
export interface LogArquivo {
  data: string
  nivel: string
  total_linhas: number
  conteudo: string
  erro?: string | null
}
export interface AuditoriaRegistro {
  id: number
  acao: string
  entidade: string
  entidade_id?: number | string | null
  usuario_id?: number | null
  descricao?: string | null
  data_acao: string
}
export interface BackupInfo {
  nome_arquivo: string
  caminho_completo: string
  tipo: 'manual' | 'automatico'
  tamanho_bytes: number
  tamanho_formatado: string
  data_criacao: string
}
