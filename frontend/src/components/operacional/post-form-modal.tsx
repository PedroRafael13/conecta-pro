'use client';

import { AlertCircle, Loader2, ChevronLeft, ChevronRight } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Stepper } from '@/components/ui/stepper';
import { RestoreAlert } from '@/components/ui/restore-alert';
import { SaveIndicator } from '@/components/ui/save-indicator';
import { getErrorMessage } from '@/lib/api';
import type { Post, PostCreate, PostUpdate, PostType, ShiftType } from '@/types/operacional';
import { postsService } from '@/services/posts';
import { useAutoSave } from '@/hooks/useAutoSave';
import { WIZARD_STEPS, DEFAULT_FORM_DATA } from './post-form-types';
import {
  StepDadosBasicos,
  StepLocalizacao,
  StepConfiguracao,
  StepRequisitos,
  StepFinanceiro,
  StepContatos,
  StepSummary,
} from './post-form-steps';

interface PostFormModalProps {
  post?: Post | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  templateData?: Partial<Post> | null;
}

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
  const [formData, setFormData] = useState<PostCreate>({ ...DEFAULT_FORM_DATA });

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
    } else if (templateData) {
      setFormData({
        ...DEFAULT_FORM_DATA,
        post_type: (templateData.post_type as PostType) || DEFAULT_FORM_DATA.post_type,
        shift_type: (templateData.shift_type as ShiftType) || DEFAULT_FORM_DATA.shift_type,
        description: templateData.description || DEFAULT_FORM_DATA.description,
        required_headcount: templateData.required_headcount ?? DEFAULT_FORM_DATA.required_headcount,
        hourly_rate: templateData.hourly_rate ?? DEFAULT_FORM_DATA.hourly_rate,
        monthly_cost: templateData.monthly_cost ?? DEFAULT_FORM_DATA.monthly_cost,
        requires_armed: templateData.requires_armed ?? DEFAULT_FORM_DATA.requires_armed,
        requires_vehicle: templateData.requires_vehicle ?? DEFAULT_FORM_DATA.requires_vehicle,
        requires_experience_months: templateData.requires_experience_months ?? DEFAULT_FORM_DATA.requires_experience_months,
      });
    } else {
      setFormData({ ...DEFAULT_FORM_DATA });
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
    if (cleaned.length <= 5) return cleaned;
    return `${cleaned.slice(0, 5)}-${cleaned.slice(5, 8)}`;
  };

  // Funcao para buscar CEP na API ViaCEP
  const fetchCep = async (cep: string) => {
    const cleanCep = cep.replace(/\D/g, '');
    if (cleanCep.length !== 8) return;

    setIsFetchingCep(true);
    setCepError(null);

    try {
      const response = await fetch(`https://viacep.com.br/ws/${cleanCep}/json/`);
      const data = await response.json();

      if (data.erro) {
        setCepError('CEP não encontrado');
        return;
      }

      setFormData((prev) => ({
        ...prev,
        address: data.logradouro || prev.address,
        city: data.localidade || prev.city,
        state: data.uf || prev.state,
      }));
    } catch (err) {
      console.error('Erro ao buscar CEP:', err);
      setCepError('Erro ao buscar CEP. Tente novamente.');
    } finally {
      setIsFetchingCep(false);
    }
  };

  // Auto-fetch CEP quando completo
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
      setFormData((prev) => ({ ...prev, [name]: formatCep(value) }));
      setCepError(null);
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1: return !!formData.name.trim();
      case 3: return (formData.required_headcount ?? 0) > 0;
      default: return true;
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

      if (!isEditing) autoSave.clear();
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
      case 1: return <StepDadosBasicos formData={formData} onChange={handleChange} />;
      case 2: return <StepLocalizacao formData={formData} onChange={handleChange} isFetchingCep={isFetchingCep} cepError={cepError} />;
      case 3: return <StepConfiguracao formData={formData} onChange={handleChange} />;
      case 4: return <StepRequisitos formData={formData} onChange={handleChange} />;
      case 5: return <StepFinanceiro formData={formData} onChange={handleChange} />;
      case 6: return <StepContatos formData={formData} onChange={handleChange} />;
      default: return null;
    }
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
          {currentStep < WIZARD_STEPS.length ? renderStepContent() : <StepSummary formData={formData} />}
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
