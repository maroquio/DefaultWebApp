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
export type TipoInteracao = 'Abertura' | 'Resposta do Usuário' | 'Resposta do Administrador'

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
  data_cadastro?: string | null
  data_atualizacao?: string | null
}
export interface DashboardData {
  chamados_pendentes?: number | null
  chamados_abertos?: number | null
}

// ===== Chamados =====
export interface ChamadoInteracao {
  id: number
  chamado_id: number
  usuario_id: number
  mensagem: string
  tipo: TipoInteracao
  data_interacao?: string | null
  status_resultante?: string | null
  data_leitura?: string | null
  usuario_nome?: string | null
  usuario_email?: string | null
}
export interface Chamado {
  id: number
  titulo: string
  status: string
  prioridade: string
  usuario_id: number
  data_abertura?: string | null
  data_fechamento?: string | null
  usuario_nome?: string | null
  usuario_email?: string | null
  mensagens_nao_lidas?: number
  tem_resposta_admin?: boolean
  interacoes?: ChamadoInteracao[] | null
}

// ===== Notificações =====
export interface Notificacao {
  id: number
  usuario_id: number
  titulo: string
  mensagem: string
  tipo: TipoNotificacao
  lida: boolean
  url_acao?: string | null
  data_criacao?: string | null
}
export interface NaoLidasResumo {
  total: number
  items: {
    id: number
    titulo: string
    mensagem: string
    tipo: TipoNotificacao
    url_acao?: string | null
    data_criacao?: string | null
  }[]
}

// ===== Pagamentos =====
export interface Pagamento {
  id: number
  usuario_id: number
  descricao: string
  valor: number
  status: string
  provider: string
  preference_id?: string | null
  payment_id?: string | null
  external_reference?: string | null
  url_checkout?: string | null
  data_criacao?: string | null
  data_atualizacao?: string | null
  usuario_nome?: string | null
}
export interface CriarPagamentoResultado {
  init_point: string
  pagamento_id: number
}
export interface DadosProvider {
  pagamento: Pagamento
  provider_nome: string
  dados_provider: Record<string, unknown> | null
}

// ===== Chat =====
export interface ChatSala {
  sala_id: string
}
export interface ChatMensagem {
  id: number
  sala_id: string
  usuario_id: number
  mensagem: string
  data_envio?: string | null
  lida_em?: string | null
}
export interface Conversa {
  sala_id: string
  outro_usuario: { id: number; nome: string; email: string; foto_url: string }
  ultima_mensagem?: {
    mensagem: string
    data_envio?: string | null
    usuario_id: number
  } | null
  nao_lidas: number
  ultima_atividade?: string | null
}
export interface UsuarioBusca {
  id: number
  nome: string
  email: string
  foto_url: string
}

// ===== Configurações / Auditoria / Backups =====
export interface ConfigItem {
  chave: string
  valor: string
  descricao?: string | null
  categoria: string
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
  usuario_id?: number | null
  usuario_nome?: string | null
  acao: string
  entidade: string
  entidade_id?: number | null
  dados_antes?: string | null
  dados_depois?: string | null
  ip?: string | null
  data?: string | null
}
export interface BackupInfo {
  nome_arquivo: string
  caminho_completo: string
  tipo: 'manual' | 'automatico'
  tamanho_bytes: number
  tamanho_formatado: string
  data_criacao: string
}
