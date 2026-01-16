// Types para Equipment - Facilities Module
// Conecta PRO

export type EquipmentStatus = 'operacional' | 'manutencao' | 'inativo' | 'descartado';

export interface Equipment {
  id: string;
  codigo: string;
  nome: string;
  tipo: string;
  fabricante: string;
  modelo: string;
  numero_serie: string;
  rfid_tag?: string;
  qr_code: string;
  localizacao: string;
  status: EquipmentStatus;
  data_aquisicao: string;
  garantia_ate?: string;
  ultima_manutencao?: string;
  proxima_manutencao?: string;
  valor_aquisicao?: number;
  vida_util_anos?: number;
  depreciacao_anual?: number;
  observacoes?: string;
  imagem_url?: string;
  created_at?: string;
  updated_at?: string;
}

export interface EquipmentCategory {
  id: string;
  nome: string;
  descricao?: string;
  icone?: string;
  cor?: string;
}

export interface EquipmentLifecycleEvent {
  id: string;
  equipment_id: string;
  tipo: 'aquisicao' | 'manutencao' | 'transferencia' | 'inativacao' | 'descarte';
  data: string;
  descricao: string;
  responsavel?: string;
  custo?: number;
  documentos?: string[];
}

export interface EquipmentFilter {
  search?: string;
  status?: EquipmentStatus[];
  tipo?: string[];
  localizacao?: string[];
  fabricante?: string[];
  garantia_vencida?: boolean;
  manutencao_atrasada?: boolean;
}

export interface EquipmentStats {
  total: number;
  operacionais: number;
  em_manutencao: number;
  inativos: number;
  descartados: number;
  garantia_vencendo: number;
  manutencao_proxima: number;
  valor_total: number;
}

export interface CreateEquipmentDTO {
  codigo: string;
  nome: string;
  tipo: string;
  fabricante: string;
  modelo: string;
  numero_serie: string;
  rfid_tag?: string;
  localizacao: string;
  data_aquisicao: string;
  garantia_ate?: string;
  valor_aquisicao?: number;
  vida_util_anos?: number;
  observacoes?: string;
}

export interface UpdateEquipmentDTO extends Partial<CreateEquipmentDTO> {
  status?: EquipmentStatus;
}
