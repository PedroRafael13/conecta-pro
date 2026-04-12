// Types baseados nos endpoints reais de billing — CPRO7 T6

export interface CobrancaClientePreview {
  nome: string
  cnpj: string
  mrr: number
  pix_key: string
  vencimento: string
}

export interface CobrancaPreview {
  modo: string
  mes: number
  ano: number
  total_clientes: number
  total_mrr: number
  sem_pix_key: string[]
  clientes: CobrancaClientePreview[]
}

export interface CrmClientItem {
  id: string
  code: string
  name: string
  trading_name: string
  cnpj: string
  email: string
  phone: string | null
  mobile: string | null
  status: 'active' | 'inactive' | string
  segment: string | null
  health_score: number | null
  total_revenue: number | null
  total_debt: number | null
  is_defaulter: boolean | null
  is_vip: boolean | null
  mrr: number | null
  contratos_ativos: number | null
}

export interface CrmResumo {
  clientes_ativos: number
  clientes_inativos: number
  inadimplentes: number
  vip: number
  originados_crm: number
  mrr_total: number
  segmentos: number
  gerado_em: string
}

export interface AiRecommendation {
  prioridade: number
  categoria: string
  titulo: string
  descricao: string
  impacto_estimado: number
  prazo_sugerido: string
  acao: string
}

export interface CollectionAction {
  id: string
  customer_name: string
  valor: number
  dias_atraso: number
  nivel: string
  acao: string
  mensagem: string
  canal: string
  prioridade: 'urgente' | 'alta' | 'media' | 'baixa' | string
  tentativas_anteriores: number
}

export interface CollectionAnalysis {
  acoes: CollectionAction[]
  total_em_atraso: number
  qtd_inadimplentes: number
  taxa_recuperacao_estimada: number
}

export interface BillingRule {
  id: number
  client_id: number
  client_name: string
  valor: number
  dia_vencimento: number
  tipo_servico: string
  forma_pagamento: 'pix' | 'boleto' | 'ted'
  ativo: boolean
  ultimo_cobrado?: string
  proximo_vencimento?: string
}

export interface ReceivableAccount {
  id: string
  descricao: string
  valor: number
  data_vencimento: string
  status: 'pendente' | 'pago' | 'atrasado' | 'cancelado' | string
  customer_name?: string
  dias_atraso?: number
}
