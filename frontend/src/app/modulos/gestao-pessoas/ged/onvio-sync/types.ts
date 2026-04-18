export interface OnvioDoc {
  id: string;
  nome: string;
  categoria: string;
  mes_ref: string | null;
  data_onvio: string | null;
}

export interface OnvioStats {
  total: number;
  por_categoria: Record<string, number>;
}

export interface SyncLog {
  id: string;
  mes_ref: string;
  status: string;
  novos: number;
  erros: number;
  duracao_s: number | null;
  created_at: string;
}

export interface SyncResult {
  message: string;
  resultado: { status: string; novos: number; erros: number; duracao: number };
}

export interface OnvioStatus {
  sessao_valida: boolean;
  redis_key?: string;
}

export interface DocumentosResponse {
  documentos: OnvioDoc[];
  total: number;
}

export interface FgtsPorTipo {
  tipo: string;
  count: number;
  soma: number;
}

export interface ValoresFiscaisResumo {
  fgts: {
    por_tipo: FgtsPorTipo[];
    total_brl: number;
    total_registros: number;
  };
  inss: {
    total_brl: number;
    total_registros: number;
  };
  consolidado: {
    valor_total_fiscal_brl: number;
    total_docs_sistema: number;
    total_docs_fiscais: number;
    docs_extraidos: number;
    taxa_extracao_pct: number;
  };
  confianca: {
    alta_auto_save: number;
    media_revisao_manual: number;
    baixa_rejeitado: number;
  };
}
