'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { getErrorMessage } from '@/lib/api';
import { AlertCircle, Loader2, User, Phone, MapPin, Briefcase, DollarSign, CheckCircle } from 'lucide-react';

interface DiaristFormData {
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

interface DiaristFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const TIPOS_SERVICO = [
  { value: 'limpeza', label: 'Limpeza' },
  { value: 'portaria', label: 'Portaria' },
  { value: 'manutencao', label: 'Manutencao' },
  { value: 'jardinagem', label: 'Jardinagem' },
  { value: 'outros', label: 'Outros' },
];

const DIAS_SEMANA = [
  { value: 'segunda', label: 'Segunda' },
  { value: 'terca', label: 'Terca' },
  { value: 'quarta', label: 'Quarta' },
  { value: 'quinta', label: 'Quinta' },
  { value: 'sexta', label: 'Sexta' },
  { value: 'sabado', label: 'Sabado' },
  { value: 'domingo', label: 'Domingo' },
];

const ESTADOS = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
  'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
  'SP', 'SE', 'TO',
];

export function DiaristFormModal({ isOpen, onClose, onSuccess }: DiaristFormModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingCPF, setIsFetchingCPF] = useState(false);
  const [cpfStatus, setCpfStatus] = useState<'idle' | 'found' | 'not_found'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'dados' | 'servicos' | 'pagamento'>('dados');

  const [formData, setFormData] = useState<DiaristFormData>({
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
  });

  useEffect(() => {
    if (isOpen) {
      setFormData({
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
      });
      setError(null);
      setActiveTab('dados');
    }
  }, [isOpen]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
    } else if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: parseFloat(value) || 0 }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleTipoServicoChange = (tipo: string) => {
    setFormData((prev) => ({
      ...prev,
      tipos_servico: prev.tipos_servico.includes(tipo)
        ? prev.tipos_servico.filter((t) => t !== tipo)
        : [...prev.tipos_servico, tipo],
    }));
  };

  const handleDiaDisponivelChange = (dia: string) => {
    setFormData((prev) => ({
      ...prev,
      dias_disponiveis: prev.dias_disponiveis.includes(dia)
        ? prev.dias_disponiveis.filter((d) => d !== dia)
        : [...prev.dias_disponiveis, dia],
    }));
  };

  const formatCPF = (value: string): string => {
    const cleaned = value.replace(/\D/g, '');
    if (cleaned.length <= 3) return cleaned;
    if (cleaned.length <= 6) return `${cleaned.slice(0, 3)}.${cleaned.slice(3)}`;
    if (cleaned.length <= 9)
      return `${cleaned.slice(0, 3)}.${cleaned.slice(3, 6)}.${cleaned.slice(6)}`;
    return `${cleaned.slice(0, 3)}.${cleaned.slice(3, 6)}.${cleaned.slice(6, 9)}-${cleaned.slice(9, 11)}`;
  };

  const formatCEP = (value: string): string => {
    const cleaned = value.replace(/\D/g, '');
    if (cleaned.length <= 5) return cleaned;
    return `${cleaned.slice(0, 5)}-${cleaned.slice(5, 8)}`;
  };

  const formatPhone = (value: string): string => {
    const cleaned = value.replace(/\D/g, '');
    if (cleaned.length <= 2) return cleaned;
    if (cleaned.length <= 7) return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2)}`;
    return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7, 11)}`;
  };

  const fetchCPFData = async (cpf: string) => {
    const cleaned = cpf.replace(/\D/g, '');
    if (cleaned.length !== 11) return;

    setIsFetchingCPF(true);
    setCpfStatus('idle');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/operacional/diaristas/consulta-cpf/${cleaned}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.found && data.nome) {
          setFormData((prev) => ({
            ...prev,
            nome: prev.nome || data.nome,
            email: prev.email || data.email || '',
            telefone: prev.telefone || data.telefone || '',
            data_nascimento: prev.data_nascimento || data.data_nascimento || '',
          }));
          setCpfStatus('found');
          if (data.aviso) {
            setError(data.aviso);
          }
        } else {
          setCpfStatus('not_found');
        }
      } else {
        setCpfStatus('not_found');
      }
    } catch {
      setCpfStatus('not_found');
    } finally {
      setIsFetchingCPF(false);
    }
  };

  const handleCPFChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCPF(e.target.value);
    setFormData((prev) => ({ ...prev, cpf: formatted }));
    setCpfStatus('idle');

    // Auto-consultar quando CPF completo
    const cleaned = formatted.replace(/\D/g, '');
    if (cleaned.length === 11) {
      fetchCPFData(cleaned);
    }
  };

  const handleCEPChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCEP(e.target.value);
    setFormData((prev) => ({ ...prev, cep: formatted }));
  };

  const handlePhoneChange = (field: 'telefone' | 'telefone_emergencia') => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const formatted = formatPhone(e.target.value);
    setFormData((prev) => ({ ...prev, [field]: formatted }));
  };

  const validateForm = (): boolean => {
    if (!formData.nome.trim()) {
      setError('Nome e obrigatorio');
      setActiveTab('dados');
      return false;
    }
    if (!formData.cpf || formData.cpf.replace(/\D/g, '').length !== 11) {
      setError('CPF invalido');
      setActiveTab('dados');
      return false;
    }
    if (formData.valor_diaria <= 0) {
      setError('Valor da diaria deve ser maior que zero');
      setActiveTab('pagamento');
      return false;
    }
    if (formData.tipos_servico.length === 0) {
      setError('Selecione pelo menos um tipo de servico');
      setActiveTab('servicos');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!validateForm()) return;

    setIsLoading(true);

    try {
      const token = localStorage.getItem('access_token');

      // Preparar dados para API
      const apiData = {
        nome: formData.nome.trim(),
        cpf: formData.cpf.replace(/\D/g, ''),
        rg: formData.rg || undefined,
        data_nascimento: formData.data_nascimento || undefined,
        email: formData.email || undefined,
        telefone: formData.telefone || undefined,
        telefone_emergencia: formData.telefone_emergencia || undefined,
        endereco: formData.endereco || undefined,
        cidade: formData.cidade || undefined,
        estado: formData.estado || undefined,
        cep: formData.cep?.replace(/\D/g, '') || undefined,
        tipos_servico: formData.tipos_servico,
        especialidades: formData.especialidades,
        experiencia_anos: formData.experiencia_anos,
        dias_disponiveis: formData.dias_disponiveis,
        hora_inicio_disponivel: formData.hora_inicio_disponivel || undefined,
        hora_fim_disponivel: formData.hora_fim_disponivel || undefined,
        aceita_hora_extra: formData.aceita_hora_extra,
        valor_diaria: formData.valor_diaria,
        valor_hora_extra: formData.valor_hora_extra || undefined,
        banco: formData.banco || undefined,
        agencia: formData.agencia || undefined,
        conta: formData.conta || undefined,
        tipo_conta: formData.tipo_conta || undefined,
        pix: formData.pix || undefined,
      };

      const response = await fetch('/api/v1/operacional/diaristas/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(apiData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ${response.status}`);
      }

      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const tabs = [
    { id: 'dados', label: 'Dados Pessoais', icon: User },
    { id: 'servicos', label: 'Servicos', icon: Briefcase },
    { id: 'pagamento', label: 'Pagamento', icon: DollarSign },
  ] as const;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Novo Diarista"
      description="Cadastre um novo diarista no sistema"
      size="xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-start gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span className="flex-1">{error}</span>
          </div>
        )}

        {/* Tabs */}
        <div className="flex border-b border-[hsl(var(--border))]">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
                activeTab === tab.id
                  ? 'border-[hsl(var(--primary))] text-[hsl(var(--primary))]'
                  : 'border-transparent text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="min-h-[350px]">
          {activeTab === 'dados' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                    Nome Completo *
                  </label>
                  <Input
                    name="nome"
                    value={formData.nome}
                    onChange={handleChange}
                    placeholder="Nome completo do diarista"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                    CPF * {cpfStatus === 'found' && <span className="text-green-500 text-xs ml-1">- Dados encontrados</span>}
                  </label>
                  <div className="relative">
                    <Input
                      value={formData.cpf}
                      onChange={handleCPFChange}
                      placeholder="000.000.000-00"
                      maxLength={14}
                      required
                    />
                    {isFetchingCPF && (
                      <div className="absolute right-3 top-1/2 -translate-y-1/2">
                        <Loader2 className="w-4 h-4 animate-spin text-[hsl(var(--muted-foreground))]" />
                      </div>
                    )}
                    {!isFetchingCPF && cpfStatus === 'found' && (
                      <div className="absolute right-3 top-1/2 -translate-y-1/2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      </div>
                    )}
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                    RG
                  </label>
                  <Input
                    name="rg"
                    value={formData.rg}
                    onChange={handleChange}
                    placeholder="RG"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                    Data de Nascimento
                  </label>
                  <Input
                    type="date"
                    name="data_nascimento"
                    value={formData.data_nascimento}
                    onChange={handleChange}
                  />
                </div>
                <div>
                  <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                    Email
                  </label>
                  <Input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="email@exemplo.com"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                    Telefone
                  </label>
                  <Input
                    value={formData.telefone}
                    onChange={handlePhoneChange('telefone')}
                    placeholder="(00) 00000-0000"
                    maxLength={15}
                  />
                </div>
                <div>
                  <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                    Telefone Emergencia
                  </label>
                  <Input
                    value={formData.telefone_emergencia}
                    onChange={handlePhoneChange('telefone_emergencia')}
                    placeholder="(00) 00000-0000"
                    maxLength={15}
                  />
                </div>
              </div>

              <div className="border-t border-[hsl(var(--border))] pt-4 mt-4">
                <div className="flex items-center gap-2 mb-3">
                  <MapPin className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                  <span className="text-sm font-medium text-[hsl(var(--foreground))]">Endereco</span>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                      CEP
                    </label>
                    <Input
                      value={formData.cep}
                      onChange={handleCEPChange}
                      placeholder="00000-000"
                      maxLength={9}
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                      Endereco
                    </label>
                    <Input
                      name="endereco"
                      value={formData.endereco}
                      onChange={handleChange}
                      placeholder="Rua, numero, bairro"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                      Cidade
                    </label>
                    <Input
                      name="cidade"
                      value={formData.cidade}
                      onChange={handleChange}
                      placeholder="Cidade"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                      Estado
                    </label>
                    <select
                      name="estado"
                      value={formData.estado}
                      onChange={handleChange}
                      className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
                    >
                      <option value="">Selecione</option>
                      {ESTADOS.map((uf) => (
                        <option key={uf} value={uf}>
                          {uf}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'servicos' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-3">
                  Tipos de Servico *
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {TIPOS_SERVICO.map((tipo) => (
                    <label
                      key={tipo.value}
                      className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-colors ${
                        formData.tipos_servico.includes(tipo.value)
                          ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/10'
                          : 'border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={formData.tipos_servico.includes(tipo.value)}
                        onChange={() => handleTipoServicoChange(tipo.value)}
                        className="w-4 h-4 rounded"
                      />
                      <span className="text-sm text-[hsl(var(--foreground))]">{tipo.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-3">
                  Dias Disponiveis
                </label>
                <div className="flex flex-wrap gap-2">
                  {DIAS_SEMANA.map((dia) => (
                    <label
                      key={dia.value}
                      className={`px-3 py-2 rounded-lg border cursor-pointer transition-colors ${
                        formData.dias_disponiveis.includes(dia.value)
                          ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/10 text-[hsl(var(--primary))]'
                          : 'border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))] text-[hsl(var(--foreground))]'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={formData.dias_disponiveis.includes(dia.value)}
                        onChange={() => handleDiaDisponivelChange(dia.value)}
                        className="sr-only"
                      />
                      <span className="text-sm">{dia.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                    Horario Inicio
                  </label>
                  <Input
                    type="time"
                    name="hora_inicio_disponivel"
                    value={formData.hora_inicio_disponivel}
                    onChange={handleChange}
                  />
                </div>
                <div>
                  <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                    Horario Fim
                  </label>
                  <Input
                    type="time"
                    name="hora_fim_disponivel"
                    value={formData.hora_fim_disponivel}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Anos de Experiencia
                </label>
                <Input
                  type="number"
                  name="experiencia_anos"
                  value={formData.experiencia_anos}
                  onChange={handleChange}
                  min={0}
                />
              </div>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="aceita_hora_extra"
                  checked={formData.aceita_hora_extra}
                  onChange={handleChange}
                  className="w-4 h-4 rounded"
                />
                <span className="text-sm text-[hsl(var(--foreground))]">Aceita hora extra</span>
              </label>
            </div>
          )}

          {activeTab === 'pagamento' && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                    Valor da Diaria (R$) *
                  </label>
                  <Input
                    type="number"
                    name="valor_diaria"
                    value={formData.valor_diaria}
                    onChange={handleChange}
                    min={0}
                    step={0.01}
                    placeholder="0.00"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                    Valor Hora Extra (R$)
                  </label>
                  <Input
                    type="number"
                    name="valor_hora_extra"
                    value={formData.valor_hora_extra}
                    onChange={handleChange}
                    min={0}
                    step={0.01}
                    placeholder="25.00"
                  />
                </div>
              </div>

              <div className="border-t border-[hsl(var(--border))] pt-4">
                <div className="flex items-center gap-2 mb-3">
                  <DollarSign className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                  <span className="text-sm font-medium text-[hsl(var(--foreground))]">
                    Dados Bancarios
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                      Banco
                    </label>
                    <Input
                      name="banco"
                      value={formData.banco}
                      onChange={handleChange}
                      placeholder="Nome do banco"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                      Tipo de Conta
                    </label>
                    <select
                      name="tipo_conta"
                      value={formData.tipo_conta}
                      onChange={handleChange}
                      className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
                    >
                      <option value="">Selecione</option>
                      <option value="corrente">Corrente</option>
                      <option value="poupanca">Poupanca</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                      Agencia
                    </label>
                    <Input
                      name="agencia"
                      value={formData.agencia}
                      onChange={handleChange}
                      placeholder="0000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                      Conta
                    </label>
                    <Input
                      name="conta"
                      value={formData.conta}
                      onChange={handleChange}
                      placeholder="00000-0"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                      Chave PIX
                    </label>
                    <Input
                      name="pix"
                      value={formData.pix}
                      onChange={handleChange}
                      placeholder="CPF, Email, Telefone ou Chave Aleatoria"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={isLoading}>
            {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            Cadastrar Diarista
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
