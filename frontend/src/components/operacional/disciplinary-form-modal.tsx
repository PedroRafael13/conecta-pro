'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { disciplinaryService } from '@/lib/services/disciplinary';
import { getErrorMessage } from '@/lib/api';
import {
  ACTION_TYPE_LABELS,
  REASON_CATEGORY_LABELS,
  type DisciplinaryAction,
  type DisciplinaryActionType,
  type ReasonCategory,
} from '@/types/disciplinary';
import { AlertCircle, Loader2, Save, Send, User } from 'lucide-react';

interface DisciplinaryFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  editData?: DisciplinaryAction | null;
}

interface FormData {
  action_type: DisciplinaryActionType;
  employee_id: string;
  employee_name: string;
  employee_cpf: string;
  employee_position: string;
  reason_category: ReasonCategory;
  reason_description: string;
  incident_date: string;
  suspension_days?: number;
  suspension_start_date?: string;
}

const initialFormData: FormData = {
  action_type: 'advertencia_verbal',
  employee_id: '',
  employee_name: '',
  employee_cpf: '',
  employee_position: '',
  reason_category: 'indisciplina',
  reason_description: '',
  incident_date: new Date().toISOString().split('T')[0],
};

export function DisciplinaryFormModal({
  isOpen,
  onClose,
  onSuccess,
  editData,
}: DisciplinaryFormModalProps) {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditing = !!editData;

  useEffect(() => {
    if (editData) {
      setFormData({
        action_type: editData.action_type,
        employee_id: editData.employee_id,
        employee_name: editData.employee_name || '',
        employee_cpf: editData.employee_cpf || '',
        employee_position: editData.employee_position || '',
        reason_category: editData.reason_category,
        reason_description: editData.reason_description,
        incident_date: editData.incident_date,
        suspension_days: editData.suspension_days,
        suspension_start_date: editData.suspension_start_date,
      });
    } else {
      setFormData(initialFormData);
    }
    setError(null);
  }, [editData, isOpen]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;

    if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: parseInt(value) || 0 }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
    setError(null);
  };

  // Formatar CPF automaticamente
  const handleCpfChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length > 11) value = value.slice(0, 11);

    if (value.length > 9) {
      value = `${value.slice(0, 3)}.${value.slice(3, 6)}.${value.slice(6, 9)}-${value.slice(9)}`;
    } else if (value.length > 6) {
      value = `${value.slice(0, 3)}.${value.slice(3, 6)}.${value.slice(6)}`;
    } else if (value.length > 3) {
      value = `${value.slice(0, 3)}.${value.slice(3)}`;
    }

    setFormData((prev) => ({ ...prev, employee_cpf: value }));
    setError(null);
  };

  const validateForm = (): boolean => {
    if (!formData.employee_name.trim()) {
      setError('Nome do funcionário é obrigatório');
      return false;
    }
    if (!formData.employee_cpf.trim()) {
      setError('CPF do funcionário é obrigatório');
      return false;
    }
    if (formData.employee_cpf.replace(/\D/g, '').length !== 11) {
      setError('CPF deve ter 11 dígitos');
      return false;
    }
    if (!formData.reason_description.trim()) {
      setError('Descrição do motivo é obrigatória');
      return false;
    }
    if (!formData.incident_date) {
      setError('Data do incidente é obrigatória');
      return false;
    }
    if (formData.action_type === 'suspensao') {
      if (!formData.suspension_days || formData.suspension_days < 1 || formData.suspension_days > 30) {
        setError('Suspensão deve ter entre 1 e 30 dias (Art. 474 CLT)');
        return false;
      }
    }
    return true;
  };

  const handleSave = async (submit: boolean = false) => {
    if (!validateForm()) return;

    setIsLoading(true);
    setError(null);

    try {
      let action: DisciplinaryAction;

      // Gerar employee_id se não existir (para novos registros)
      const employeeId = formData.employee_id || crypto.randomUUID();

      const dataToSend = {
        action_type: formData.action_type,
        employee_id: employeeId,
        employee_name: formData.employee_name,
        employee_cpf: formData.employee_cpf,
        employee_position: formData.employee_position || undefined,
        reason_category: formData.reason_category,
        reason_description: formData.reason_description,
        incident_date: formData.incident_date,
        suspension_days: formData.action_type === 'suspensao' ? formData.suspension_days : undefined,
        suspension_start_date: formData.action_type === 'suspensao' ? formData.suspension_start_date : undefined,
      };

      if (isEditing && editData?.id) {
        action = await disciplinaryService.update(editData.id, {
          reason_description: dataToSend.reason_description,
          incident_date: dataToSend.incident_date,
          suspension_days: dataToSend.suspension_days,
          suspension_start_date: dataToSend.suspension_start_date,
        });
      } else {
        action = await disciplinaryService.create(dataToSend);
      }

      if (submit && action.status === 'rascunho') {
        setIsSubmitting(true);
        await disciplinaryService.submit(action.id);
      }

      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
      setIsSubmitting(false);
    }
  };

  const isSuspension = formData.action_type === 'suspensao';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Medida Administrativa' : 'Nova Medida Administrativa'}
      description={isEditing ? `Editando ${editData?.code}` : 'Preencha os dados da medida disciplinar'}
      size="xl"
    >
      <form onSubmit={(e) => { e.preventDefault(); handleSave(false); }} className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-center gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Tipo de Medida */}
        <div>
          <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
            Tipo de Medida *
          </label>
          <select
            name="action_type"
            value={formData.action_type}
            onChange={handleChange}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
            disabled={isEditing}
          >
            {Object.entries(ACTION_TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {/* Dados do Funcionário */}
        <div className="border border-[hsl(var(--border))] rounded-lg p-4 space-y-4">
          <h3 className="font-medium text-sm text-[hsl(var(--foreground))] flex items-center gap-2">
            <User className="w-4 h-4" />
            Dados do Funcionário
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Nome Completo *
              </label>
              <Input
                name="employee_name"
                value={formData.employee_name}
                onChange={handleChange}
                placeholder="Nome completo do funcionário"
                disabled={isEditing}
              />
            </div>

            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                CPF *
              </label>
              <Input
                name="employee_cpf"
                value={formData.employee_cpf}
                onChange={handleCpfChange}
                placeholder="000.000.000-00"
                maxLength={14}
                disabled={isEditing}
              />
            </div>

            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Cargo
              </label>
              <Input
                name="employee_position"
                value={formData.employee_position}
                onChange={handleChange}
                placeholder="Cargo do funcionário"
                disabled={isEditing}
              />
            </div>
          </div>
        </div>

        {/* Motivo da Medida */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
              Categoria do Motivo (Art. 482 CLT) *
            </label>
            <select
              name="reason_category"
              value={formData.reason_category}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
            >
              {Object.entries(REASON_CATEGORY_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Descrição Detalhada do Motivo *
            </label>
            <textarea
              name="reason_description"
              value={formData.reason_description}
              onChange={handleChange}
              placeholder="Descreva detalhadamente o fato que motivou a medida disciplinar, incluindo data, hora, local e circunstâncias..."
              rows={4}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
            />
          </div>

          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Data do Incidente *
            </label>
            <Input
              type="date"
              name="incident_date"
              value={formData.incident_date}
              onChange={handleChange}
              max={new Date().toISOString().split('T')[0]}
            />
          </div>
        </div>

        {/* Campos de Suspensão */}
        {isSuspension && (
          <div className="border border-yellow-500/30 bg-yellow-500/5 rounded-lg p-4 space-y-4">
            <h3 className="font-medium text-sm text-yellow-500">
              Dados da Suspensão (Art. 474 CLT - máximo 30 dias)
            </h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Dias de Suspensão *
                </label>
                <Input
                  type="number"
                  name="suspension_days"
                  value={formData.suspension_days || ''}
                  onChange={handleChange}
                  min={1}
                  max={30}
                  placeholder="1-30"
                />
              </div>

              <div>
                <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                  Data de Início da Suspensão
                </label>
                <Input
                  type="date"
                  name="suspension_start_date"
                  value={formData.suspension_start_date || ''}
                  onChange={handleChange}
                />
              </div>
            </div>
          </div>
        )}

        {/* Informações sobre o fluxo */}
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-sm text-blue-400">
          <p><strong>Fluxo:</strong> Rascunho → Pendente Aprovação → Aprovada → Pendente Assinatura → Assinada</p>
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>

          <Button
            type="button"
            variant="outline"
            onClick={() => handleSave(false)}
            disabled={isLoading}
          >
            {isLoading && !isSubmitting ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Salvar Rascunho
          </Button>

          <Button
            type="button"
            variant="primary"
            onClick={() => handleSave(true)}
            disabled={isLoading}
          >
            {isSubmitting ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Send className="w-4 h-4 mr-2" />
            )}
            Salvar e Submeter
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
