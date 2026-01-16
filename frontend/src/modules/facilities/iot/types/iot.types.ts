// Types para IoT Sensors - Facilities Module
// Conecta PRO

export type SensorType = 'temperatura' | 'umidade' | 'pressao' | 'movimento' | 'energia' | 'luminosidade' | 'co2' | 'ruido';

export type SensorStatus = 'online' | 'offline' | 'alerta';

export type AlertSeverity = 'critica' | 'alta' | 'media' | 'baixa';

export type AlertType = 'limite_excedido' | 'offline' | 'bateria_baixa' | 'anomalia';

export interface Sensor {
  id: string;
  nome: string;
  tipo: SensorType;
  localizacao: string;
  status: SensorStatus;
  valor_atual: number;
  unidade: string;
  limite_min?: number;
  limite_max?: number;
  ultima_leitura: string;
  bateria_nivel?: number;
  firmware_versao?: string;
  modelo?: string;
  fabricante?: string;
  ip_address?: string;
  mac_address?: string;
  intervalo_leitura?: number;
  created_at?: string;
  updated_at?: string;
}

export interface SensorReading {
  id?: string;
  sensor_id: string;
  timestamp: string;
  valor: number;
  unidade?: string;
}

export interface SensorReadingAggregated {
  periodo: string;
  media: number;
  minimo: number;
  maximo: number;
  contagem: number;
}

export interface Alert {
  id: string;
  sensor_id: string;
  sensor_nome?: string;
  tipo: AlertType;
  mensagem: string;
  severidade: AlertSeverity;
  valor_detectado?: number;
  limite_violado?: number;
  created_at: string;
  acknowledged: boolean;
  acknowledged_at?: string;
  acknowledged_by?: string;
  resolved: boolean;
  resolved_at?: string;
}

export interface SensorThreshold {
  sensor_id: string;
  limite_min?: number;
  limite_max?: number;
  alerta_delay_segundos?: number;
  notificar_email?: boolean;
  notificar_sms?: boolean;
  notificar_push?: boolean;
}

export interface SensorFilter {
  search?: string;
  tipo?: SensorType[];
  status?: SensorStatus[];
  localizacao?: string[];
  com_alerta?: boolean;
  bateria_baixa?: boolean;
}

export interface SensorStats {
  total: number;
  online: number;
  offline: number;
  em_alerta: number;
  alertas_ativos: number;
  alertas_criticos: number;
  leituras_24h: number;
}

export interface IoTDashboardData {
  sensors: Sensor[];
  alerts: Alert[];
  stats: SensorStats;
  readings_recentes: SensorReading[];
}

export interface CreateSensorDTO {
  nome: string;
  tipo: SensorType;
  localizacao: string;
  limite_min?: number;
  limite_max?: number;
  modelo?: string;
  fabricante?: string;
  intervalo_leitura?: number;
}

export interface UpdateSensorDTO extends Partial<CreateSensorDTO> {
  status?: SensorStatus;
}
