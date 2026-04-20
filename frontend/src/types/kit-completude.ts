/**
 * Tipos TypeScript — FASE 4 BLOCO 3 / T3 (§29).
 * Refletem 1:1 o response JSON dos endpoints §27.4 (snake_case conforme API FastAPI).
 */

export type DocScope = 'condominio' | 'empresa_matriz' | 'funcionario';

export type TipoServico =
  | 'kit_mensal'
  | 'portaria_remota'
  | 'portaria_autonoma'
  | 'manutencao_cftv'
  | 'administrativo';

export type Periodicidade = 'mensal' | 'eventual' | 'anual';

export type MotivoFaltante =
  | 'nao_encontrado_onvio'
  | 'aguarda_fase_1_cnd'
  | 'aguarda_fase_2_banco'
  | 'nao_sincronizado';

export interface DocumentoPresente {
  tipo_documento: string;
  escopo: DocScope;
  onvio_document_id: string;
  nome_arquivo: string;
  revisao_pendente: boolean;
}

export interface DocumentoFaltante {
  tipo_documento: string;
  escopo: DocScope;
  obrigatorio: boolean;
  periodicidade: Periodicidade;
  motivo: MotivoFaltante;
}

export interface MetricasKit {
  total_esperado: number;
  total_presente_confirmado: number;
  total_presente_pendente_revisao: number;
  total_faltante: number;
  pct_completude_confirmada: number;
  pct_completude_total: number;
}

export interface CompletudeKit {
  condominio_id: string;
  condominio_nome: string;
  tipo_servico: TipoServico;
  mes_ref: string;
  gerado_em: string;
  docs_presentes: DocumentoPresente[];
  docs_faltantes: DocumentoFaltante[];
  metricas: MetricasKit;
}
