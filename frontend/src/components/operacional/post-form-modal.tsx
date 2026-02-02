'use client';

import { AlertCircle, Loader2, ChevronLeft, ChevronRight, FileText } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Stepper, type Step } from '@/components/ui/stepper';
import { RestoreAlert } from '@/components/ui/restore-alert';
import { SaveIndicator } from '@/components/ui/save-indicator';
import { getErrorMessage } from '@/lib/api';
import type { Post, PostCreate, PostUpdate, PostType, ShiftType } from '@/types/operacional';
import { POST_TYPE_LABELS, SHIFT_TYPE_LABELS } from '@/types/operacional';
;
import { useAutoSave } from '@/hooks/useAutoSave';

interface PostFormModalProps {
  post?: Post | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  templateData?: Partial<Post> | null;
}

const STATES = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
  'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
  'SP', 'SE', 'TO',
];

const WIZARD_STEPS: Step[] = [
  { id: 1, label: 'Dados Básicos', description: 'Informações gerais' },
  { id: 2, label: 'Localização', description: 'Endereço e CEP' },
  { id: 3, label: 'Configuração', description: 'Turnos e efetivo' },
  { id: 4, label: 'Requisitos', description: 'Experiência e recursos' },
  { id: 5, label: 'Financeiro', description: 'Custos e adicionais' },
  { id: 6, label: 'Contatos', description: 'Supervisor e emergência' },
];

export function PostFormModal({
  post,
  isOpen,
  onClose,
  onSuccess,
  templateData,
}: PostFormModalProps) {
  const isEditing = !!post;

  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingCep, setIsFetchingCep] = useState(false);
  const [cepError, setCepError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());
  const [showRestoreAlert, setShowRestoreAlert] = useState(false);

  // Form state
  const [formData, setFormData] = useState<PostCreate>({
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
  });

  // Auto-save hook (apenas quando criando novo, nao ao editar)
  const autoSave = useAutoSave({
    key: 'posto_form',
    data: formData,
    debounceMs: 2000,
    enabled: isOpen && !isEditing,
  });

  // Verificar rascunho ao abrir modal (apenas ao criar novo)
  useEffect(() => {
    if (isOpen && !isEditing && autoSave.hasDraft) {
      setShowRestoreAlert(true);
    } else {
      setShowRestoreAlert(false);
    }
  }, [isOpen, isEditing, autoSave.hasDraft]);

  // Populate form when editing
  useEffect(() => {
    if (post) {
      setFormData({
        name: post.name,
        description: post.description || '',
        post_type: post.post_type as PostType,
        shift_type: post.shift_type as ShiftType,
        address: post.address || '',
        city: post.city || '',
        state: post.state || '',
        zip_code: post.zip_code || '',
        required_headcount: post.required_headcount,
        hourly_rate: post.hourly_rate,
        monthly_cost: post.monthly_cost,
        break_duration_minutes: post.break_duration_minutes,
        night_shift_bonus_percent: post.night_shift_bonus_percent,
        hazard_pay_percent: post.hazard_pay_percent,
        requires_experience_months: post.requires_experience_months,
        requires_armed: post.requires_armed,
        requires_vehicle: post.requires_vehicle,
        supervisor_name: post.supervisor_name || '',
        supervisor_phone: post.supervisor_phone || '',
        emergency_contact: post.emergency_contact || '',
        emergency_phone: post.emergency_phone || '',
        notes: post.notes || '',
      });
    } else {
      // Reset form when creating new, optionally with template data
      const defaultData: PostCreate = {
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

      // Apply template data if provided
      if (templateData) {
        setFormData({
          ...defaultData,
          post_type: (templateData.post_type as PostType) || defaultData.post_type,
          shift_type: (templateData.shift_type as ShiftType) || defaultData.shift_type,
          description: templateData.description || defaultData.description,
          required_headcount: templateData.required_headcount ?? defaultData.required_headcount,
          hourly_rate: templateData.hourly_rate ?? defaultData.hourly_rate,
          monthly_cost: templateData.monthly_cost ?? defaultData.monthly_cost,
          requires_armed: templateData.requires_armed ?? defaultData.requires_armed,
          requires_vehicle: templateData.requires_vehicle ?? defaultData.requires_vehicle,
          requires_experience_months: templateData.requires_experience_months ?? defaultData.requires_experience_months,
        });
      } else {
        setFormData(defaultData);
      }
    }
    setCurrentStep(1);
    setCompletedSteps(new Set());
    setError(null);
    setCepError(null);
  }, [post, isOpen, templateData]);

  // Funcoes para restaurar e descartar rascunho
  const handleRestoreDraft = () => {
    const draft = autoSave.restore();
    if (draft) {
      setFormData({ ...formData, ...draft });
      setShowRestoreAlert(false);
    }
  };

  const handleDiscardDraft = () => {
    autoSave.clear();
    setShowRestoreAlert(false);
  };

  // Funcao para aplicar mascara no CEP
  const formatCep = (value: string): string => {
    const cleaned = value.replace(/\D/g, '');
    if (cleaned.length <= 5) {
      return cleaned;
    }
    return `${cleaned.slice(0, 5)}-${cleaned.slice(5, 8)}`;
  };

  // Funcao para buscar CEP na API ViaCEP
  const fetchCep = async (cep: string) => {
    const cleanCep = cep.replace(/\D/g, '');

    // Validar formato do CEP
    if (cleanCep.length !== 8) {
      return;
    }

    setIsFetchingCep(true);
    setCepError(null);

    try {
      const response = await fetch(`https://viacep.com.br/ws/${cleanCep}/json/`);
      const data = await response.json();

      if (data.erro) {
        setCepError('CEP não encontrado');
        return;
      }

      // Auto-preencher campos de endereco
      setFormData((prev) => ({
        ...prev,
        address: data.logradouro || prev.address,
        city: data.localidade || prev.city,
        state: data.uf || prev.state,
      }));
    } catch (error) {
      console.error('Erro ao buscar CEP:', error);
      setCepError('Erro ao buscar CEP. Tente novamente.');
    } finally {
      setIsFetchingCep(false);
    }
  };

  // useEffect para detectar CEP completo e buscar automaticamente
  useEffect(() => {
    if (!formData.zip_code) return;
    const cleanCep = formData.zip_code.replace(/\D/g, '');
    if (cleanCep.length === 8) {
      fetchCep(cleanCep);
    }
  }, [formData.zip_code]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
    } else if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: parseFloat(value) || 0 }));
    } else if (name === 'zip_code') {
      // Aplicar mascara no CEP
      const formatted = formatCep(value);
      setFormData((prev) => ({ ...prev, [name]: formatted }));
      setCepError(null);
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1: // Dados Básicos
        return !!formData.name.trim();
      case 2: // Localização (todos opcionais)
        return true;
      case 3: // Configuração
        return (formData.required_headcount ?? 0) > 0;
      case 4: // Requisitos (todos opcionais)
        return true;
      case 5: // Financeiro (todos opcionais)
        return true;
      case 6: // Contatos (todos opcionais)
        return true;
      default:
        return true;
    }
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCompletedSteps(new Set([...completedSteps, currentStep]));
      setCurrentStep((prev) => Math.min(prev + 1, WIZARD_STEPS.length));
      setError(null);
    } else {
      setError('Preencha todos os campos obrigatórios antes de continuar');
    }
  };

  const handlePrev = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
    setError(null);
  };

  const handleStepClick = (stepId: number) => {
    if (stepId < currentStep || completedSteps.has(stepId)) {
      setCurrentStep(stepId);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Clean up empty strings
      const cleanData = Object.fromEntries(
        Object.entries(formData).map(([key, value]) => [
          key,
          value === '' ? undefined : value,
        ])
      ) as PostCreate;

      if (isEditing && post) {
        await postsService.update(post.id, cleanData as PostUpdate);
      } else {
        await postsService.create(cleanData);
      }

      // Limpar rascunho apos sucesso
      if (!isEditing) {
        autoSave.clear();
      }

      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1: // Dados Básicos
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Nome do Posto *
              </label>
              <Input
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Ex: Portaria Principal - Condomínio ABC"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Tipo de Posto *
                </label>
                <select
                  name="post_type"
                  value={formData.post_type}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
                  required
                >
                  {Object.entries(POST_TYPE_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Tipo de Turno *
                </label>
                <select
                  name="shift_type"
                  value={formData.shift_type}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
                  required
                >
                  {Object.entries(SHIFT_TYPE_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Descricao
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
                placeholder="Descricao detalhada do posto..."
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
              />
            </div>
          </div>
        );

      case 2: // Localização
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Endereco
              </label>
              <Input
                name="address"
                value={formData.address}
                onChange={handleChange}
                placeholder="Rua, numero, bairro..."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Cidade
                </label>
                <Input
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  placeholder="Cidade"
                />
              </div>
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  UF
                </label>
                <select
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
                >
                  <option value="">-</option>
                  {STATES.map((uf) => (
                    <option key={uf} value={uf}>
                      {uf}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                CEP
              </label>
              <div className="relative">
                <Input
                  name="zip_code"
                  value={formData.zip_code}
                  onChange={handleChange}
                  placeholder="00000-000"
                  maxLength={9}
                  disabled={isFetchingCep}
                />
                {isFetchingCep && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    <Loader2 className="w-4 h-4 animate-spin text-[hsl(var(--muted-foreground))]" />
                  </div>
                )}
              </div>
              {cepError && (
                <p className="text-xs text-red-500 mt-1">{cepError}</p>
              )}
            </div>
          </div>
        );

      case 3: // Configuração de Turno
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Efetivo Necessario *
                </label>
                <Input
                  type="number"
                  name="required_headcount"
                  value={formData.required_headcount}
                  onChange={handleChange}
                  min={1}
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Intervalo (minutos)
                </label>
                <Input
                  type="number"
                  name="break_duration_minutes"
                  value={formData.break_duration_minutes}
                  onChange={handleChange}
                  min={0}
                />
              </div>
            </div>
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Observacoes sobre o turno
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows={4}
                placeholder="Detalhes sobre horarios, pausas, troca de turno..."
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
              />
            </div>
          </div>
        );

      case 4: // Requisitos
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Experiencia Minima (meses)
              </label>
              <Input
                type="number"
                name="requires_experience_months"
                value={formData.requires_experience_months}
                onChange={handleChange}
                min={0}
                placeholder="0 = sem requisito de experiência"
              />
            </div>
            <div className="space-y-3">
              <label className="flex items-center gap-2 cursor-pointer p-3 rounded-lg border border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))] transition-colors">
                <input
                  type="checkbox"
                  name="requires_armed"
                  checked={formData.requires_armed}
                  onChange={handleChange}
                  className="w-4 h-4 rounded border-[hsl(var(--border))]"
                />
                <div className="flex-1">
                  <div className="text-sm font-medium text-[hsl(var(--foreground))]">
                    Requer Armamento
                  </div>
                  <div className="text-xs text-[hsl(var(--muted-foreground))]">
                    Colaborador precisa estar armado
                  </div>
                </div>
              </label>
              <label className="flex items-center gap-2 cursor-pointer p-3 rounded-lg border border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))] transition-colors">
                <input
                  type="checkbox"
                  name="requires_vehicle"
                  checked={formData.requires_vehicle}
                  onChange={handleChange}
                  className="w-4 h-4 rounded border-[hsl(var(--border))]"
                />
                <div className="flex-1">
                  <div className="text-sm font-medium text-[hsl(var(--foreground))]">
                    Requer Veiculo
                  </div>
                  <div className="text-xs text-[hsl(var(--muted-foreground))]">
                    Colaborador precisa ter veículo próprio
                  </div>
                </div>
              </label>
            </div>
          </div>
        );

      case 5: // Financeiro
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Valor Hora (R$)
                </label>
                <Input
                  type="number"
                  name="hourly_rate"
                  value={formData.hourly_rate}
                  onChange={handleChange}
                  min={0}
                  step={0.01}
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Custo Mensal (R$)
                </label>
                <Input
                  type="number"
                  name="monthly_cost"
                  value={formData.monthly_cost}
                  onChange={handleChange}
                  min={0}
                  step={0.01}
                  placeholder="0.00"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Adicional Noturno (%)
                </label>
                <Input
                  type="number"
                  name="night_shift_bonus_percent"
                  value={formData.night_shift_bonus_percent}
                  onChange={handleChange}
                  min={0}
                  placeholder="20"
                />
              </div>
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Periculosidade (%)
                </label>
                <Input
                  type="number"
                  name="hazard_pay_percent"
                  value={formData.hazard_pay_percent}
                  onChange={handleChange}
                  min={0}
                  placeholder="0"
                />
              </div>
            </div>
          </div>
        );

      case 6: // Contatos
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Nome do Supervisor
                </label>
                <Input
                  name="supervisor_name"
                  value={formData.supervisor_name}
                  onChange={handleChange}
                  placeholder="Nome completo"
                />
              </div>
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Telefone do Supervisor
                </label>
                <Input
                  name="supervisor_phone"
                  value={formData.supervisor_phone}
                  onChange={handleChange}
                  placeholder="(00) 00000-0000"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Contato de Emergencia
                </label>
                <Input
                  name="emergency_contact"
                  value={formData.emergency_contact}
                  onChange={handleChange}
                  placeholder="Nome completo"
                />
              </div>
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Telefone de Emergencia
                </label>
                <Input
                  name="emergency_phone"
                  value={formData.emergency_phone}
                  onChange={handleChange}
                  placeholder="(00) 00000-0000"
                />
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const renderSummary = () => {
    return (
      <div className="space-y-6">
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <FileText className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-blue-500 mb-1">Resumo do Posto</h4>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                Revise as informações antes de salvar
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-[hsl(var(--muted-foreground))] mb-1">Nome</div>
            <div className="text-[hsl(var(--foreground))] font-medium">{formData.name || '-'}</div>
          </div>
          <div>
            <div className="text-[hsl(var(--muted-foreground))] mb-1">Tipo</div>
            <div className="text-[hsl(var(--foreground))] font-medium">
              {POST_TYPE_LABELS[formData.post_type]}
            </div>
          </div>
          <div>
            <div className="text-[hsl(var(--muted-foreground))] mb-1">Turno</div>
            <div className="text-[hsl(var(--foreground))] font-medium">
              {SHIFT_TYPE_LABELS[formData.shift_type]}
            </div>
          </div>
          <div>
            <div className="text-[hsl(var(--muted-foreground))] mb-1">Efetivo</div>
            <div className="text-[hsl(var(--foreground))] font-medium">
              {formData.required_headcount} {formData.required_headcount === 1 ? 'pessoa' : 'pessoas'}
            </div>
          </div>
          {formData.address && (
            <div className="md:col-span-2">
              <div className="text-[hsl(var(--muted-foreground))] mb-1">Endereço</div>
              <div className="text-[hsl(var(--foreground))] font-medium">
                {formData.address}
                {formData.city && `, ${formData.city}`}
                {formData.state && ` - ${formData.state}`}
              </div>
            </div>
          )}
          {((formData.hourly_rate ?? 0) > 0 || (formData.monthly_cost ?? 0) > 0) && (
            <>
              {(formData.hourly_rate ?? 0) > 0 && (
                <div>
                  <div className="text-[hsl(var(--muted-foreground))] mb-1">Valor Hora</div>
                  <div className="text-[hsl(var(--foreground))] font-medium">
                    R$ {(formData.hourly_rate ?? 0).toFixed(2)}
                  </div>
                </div>
              )}
              {(formData.monthly_cost ?? 0) > 0 && (
                <div>
                  <div className="text-[hsl(var(--muted-foreground))] mb-1">Custo Mensal</div>
                  <div className="text-[hsl(var(--foreground))] font-medium">
                    R$ {(formData.monthly_cost ?? 0).toFixed(2)}
                  </div>
                </div>
              )}
            </>
          )}
          {(formData.requires_armed || formData.requires_vehicle) && (
            <div className="md:col-span-2">
              <div className="text-[hsl(var(--muted-foreground))] mb-1">Requisitos</div>
              <div className="flex gap-2">
                {formData.requires_armed && (
                  <span className="px-2 py-1 rounded bg-orange-500/10 text-orange-500 text-xs font-medium">
                    Armado
                  </span>
                )}
                {formData.requires_vehicle && (
                  <span className="px-2 py-1 rounded bg-blue-500/10 text-blue-500 text-xs font-medium">
                    Veículo
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Posto' : 'Novo Posto'}
      description={isEditing ? `Editando ${post?.code}` : 'Preencha os dados do novo posto'}
      size="xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Restore Alert */}
        {showRestoreAlert && (
          <RestoreAlert
            onRestore={handleRestoreDraft}
            onDiscard={handleDiscardDraft}
            savedAt={autoSave.lastSaved}
          />
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-start gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span className="flex-1">{error}</span>
          </div>
        )}

        {/* Save Indicator */}
        {!isEditing && isOpen && (
          <div className="flex justify-end">
            <SaveIndicator
              saving={autoSave.saving}
              lastSaved={autoSave.lastSaved}
              error={autoSave.error}
            />
          </div>
        )}

        <Stepper steps={WIZARD_STEPS} currentStep={currentStep} onStepClick={handleStepClick} />

        <div className="min-h-[300px]">
          {currentStep < WIZARD_STEPS.length ? renderStepContent() : renderSummary()}
        </div>

        <ModalFooter>
          <div className="flex items-center justify-between w-full">
            <Button
              type="button"
              variant="outline"
              onClick={currentStep === 1 ? onClose : handlePrev}
              disabled={isLoading}
            >
              {currentStep === 1 ? (
                'Cancelar'
              ) : (
                <>
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  Voltar
                </>
              )}
            </Button>
            {currentStep < WIZARD_STEPS.length ? (
              <Button type="button" variant="primary" onClick={handleNext} disabled={isLoading}>
                Próximo
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            ) : (
              <Button type="submit" variant="primary" disabled={isLoading}>
                {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                {isEditing ? 'Salvar Alteracoes' : 'Criar Posto'}
              </Button>
            )}
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}
