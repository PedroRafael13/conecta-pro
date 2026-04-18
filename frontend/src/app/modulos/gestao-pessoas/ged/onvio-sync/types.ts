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

// ValoresFiscaisResumo e FgtsPorTipo são exportados pelo hook useValoresFiscaisResumo
export type { ValoresFiscaisResumo, FgtsPorTipo } from '@/hooks/useValoresFiscaisResumo';
