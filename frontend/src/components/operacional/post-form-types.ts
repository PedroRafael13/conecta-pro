import type { Step } from '@/components/ui/stepper';
import type { PostCreate, PostType, ShiftType } from '@/types/operacional';

export const STATES = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
  'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
  'SP', 'SE', 'TO',
];

export const WIZARD_STEPS: Step[] = [
  { id: 1, label: 'Dados Básicos', description: 'Informações gerais' },
  { id: 2, label: 'Localização', description: 'Endereço e CEP' },
  { id: 3, label: 'Configuração', description: 'Turnos e efetivo' },
  { id: 4, label: 'Requisitos', description: 'Experiência e recursos' },
  { id: 5, label: 'Financeiro', description: 'Custos e adicionais' },
  { id: 6, label: 'Contatos', description: 'Supervisor e emergência' },
];

export const DEFAULT_FORM_DATA: PostCreate = {
  name: '',
  description: '',
  post_type: 'vigilante' as PostType,
  shift_type: 'diurno' as ShiftType,
  address: '',
  city: '',
  state: '',
  zip_code: '',
  required_headcount: 1,
  hourly_rate: 0,
  monthly_cost: 0,
  break_duration_minutes: 60,
  night_shift_bonus_percent: 20,
  hazard_pay_percent: 0,
  requires_experience_months: 0,
  requires_armed: false,
  requires_vehicle: false,
  supervisor_name: '',
  supervisor_phone: '',
  emergency_contact: '',
  emergency_phone: '',
  notes: '',
};

export type PostFormChangeHandler = (
  e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
) => void;
