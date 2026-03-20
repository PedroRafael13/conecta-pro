export interface DiaristFormData {
  nome: string;
  cpf: string;
  rg?: string;
  data_nascimento?: string;
  email?: string;
  telefone?: string;
  telefone_emergencia?: string;
  endereco?: string;
  cidade?: string;
  estado?: string;
  cep?: string;
  tipos_servico: string[];
  especialidades: string[];
  experiencia_anos: number;
  dias_disponiveis: string[];
  hora_inicio_disponivel?: string;
  hora_fim_disponivel?: string;
  aceita_hora_extra: boolean;
  valor_diaria: number;
  valor_hora_extra?: number;
  banco?: string;
  agencia?: string;
  conta?: string;
  tipo_conta?: string;
  pix?: string;
}

export const INITIAL_FORM_DATA: DiaristFormData = {
  nome: '',
  cpf: '',
  rg: '',
  data_nascimento: '',
  email: '',
  telefone: '',
  telefone_emergencia: '',
  endereco: '',
  cidade: '',
  estado: '',
  cep: '',
  tipos_servico: [],
  especialidades: [],
  experiencia_anos: 0,
  dias_disponiveis: [],
  hora_inicio_disponivel: '08:00',
  hora_fim_disponivel: '17:00',
  aceita_hora_extra: true,
  valor_diaria: 0,
  valor_hora_extra: 25,
  banco: '',
  agencia: '',
  conta: '',
  tipo_conta: '',
  pix: '',
};

export const TIPOS_SERVICO = [
  { value: 'limpeza', label: 'Limpeza' },
  { value: 'portaria', label: 'Portaria' },
  { value: 'manutencao', label: 'Manutencao' },
  { value: 'jardinagem', label: 'Jardinagem' },
  { value: 'outros', label: 'Outros' },
];

export const DIAS_SEMANA = [
  { value: 'segunda', label: 'Segunda' },
  { value: 'terca', label: 'Terca' },
  { value: 'quarta', label: 'Quarta' },
  { value: 'quinta', label: 'Quinta' },
  { value: 'sexta', label: 'Sexta' },
  { value: 'sabado', label: 'Sabado' },
  { value: 'domingo', label: 'Domingo' },
];

export const ESTADOS = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
  'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
  'SP', 'SE', 'TO',
];

export function formatCPF(value: string): string {
  const cleaned = value.replace(/\D/g, '');
  if (cleaned.length <= 3) return cleaned;
  if (cleaned.length <= 6) return `${cleaned.slice(0, 3)}.${cleaned.slice(3)}`;
  if (cleaned.length <= 9)
    return `${cleaned.slice(0, 3)}.${cleaned.slice(3, 6)}.${cleaned.slice(6)}`;
  return `${cleaned.slice(0, 3)}.${cleaned.slice(3, 6)}.${cleaned.slice(6, 9)}-${cleaned.slice(9, 11)}`;
}

export function formatCEP(value: string): string {
  const cleaned = value.replace(/\D/g, '');
  if (cleaned.length <= 5) return cleaned;
  return `${cleaned.slice(0, 5)}-${cleaned.slice(5, 8)}`;
}

export function formatPhone(value: string): string {
  const cleaned = value.replace(/\D/g, '');
  if (cleaned.length <= 2) return cleaned;
  if (cleaned.length <= 7) return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2)}`;
  return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7, 11)}`;
}

export type FormChangeHandler = (
  e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
) => void;
