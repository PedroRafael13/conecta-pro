'use client';

import { AlertCircle, Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { RestoreAlert } from '@/components/ui/restore-alert';
import { SaveIndicator } from '@/components/ui/save-indicator';
import { getErrorMessage } from '@/lib/api';
import type { AllocationCreate, Employee, Post } from '@/types/operacional';
import { allocationsService } from '@/services/allocations';
import { useAutoSave } from '@/hooks/useAutoSave';

interface AllocationFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  posts: Post[];
  employees: Employee[];
}

export function AllocationFormModal({
  isOpen,
  onClose,
  onSuccess,
  posts,
  employees,
}: AllocationFormModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRestoreAlert, setShowRestoreAlert] = useState(false);

  const [formData, setFormData] = useState<AllocationCreate>({
    post_id: '',
    employee_id: '',
    start_date: '',
    end_date: null,
    is_primary: true,
    is_temporary: false,
    hourly_rate: 0,
    monthly_salary: 0,
    additional_benefits: 0,
    role: '',
    notes: '',
  });

  // Auto-save hook
  const autoSave = useAutoSave({
    key: 'alocacao_form',
    data: formData,
    debounceMs: 2000,
    enabled: isOpen,
  });

  // Verificar rascunho ao abrir modal
  useEffect(() => {
    if (isOpen && autoSave.hasDraft) {
      setShowRestoreAlert(true);
    } else {
      setShowRestoreAlert(false);
    }
  }, [isOpen, autoSave.hasDraft]);

  useEffect(() => {
    if (isOpen) {
      setFormData({
        post_id: '',
        employee_id: '',
        start_date: '',
        end_date: null,
        is_primary: true,
        is_temporary: false,
        hourly_rate: 0,
        monthly_salary: 0,
        additional_benefits: 0,
        role: '',
        notes: '',
      });
      setError(null);
    }
  }, [isOpen]);

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

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
      return;
    }

    if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: Number(value) || 0 }));
      return;
    }

    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      if (!formData.post_id || !formData.employee_id || !formData.start_date) {
        setError('Preencha posto, funcionario e data de inicio.');
        setIsLoading(false);
        return;
      }

      const payload: AllocationCreate = {
        ...formData,
        end_date: formData.end_date || null,
        role: formData.role || undefined,
        notes: formData.notes || undefined,
      };

      await allocationsService.create(payload);

      // Limpar rascunho apos sucesso
      autoSave.clear();

      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const getEmployeeLabel = (employee: Employee) => {
    return (
      employee.full_name ||
      employee.name ||
      employee.email ||
      employee.registration ||
      employee.id
    );
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Nova Alocação"
      description="Vincule um funcionario a um posto"
      size="lg"
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
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-center gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Save Indicator */}
        {isOpen && (
          <div className="flex justify-end">
            <SaveIndicator
              saving={autoSave.saving}
              lastSaved={autoSave.lastSaved}
              error={autoSave.error}
            />
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Posto de Trabalho *
            </label>
            <select
              name="post_id"
              value={formData.post_id}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm"
              required
             aria-label="Post Id">
              <option value="">Selecione um posto</option>
              {posts.map((post) => (
                <option key={post.id} value={post.id}>
                  {post.name} ({post.code})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Funcionario *
            </label>
            <select
              name="employee_id"
              value={formData.employee_id}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm"
              required
             aria-label="Employee Id">
              <option value="">Selecione um funcionario</option>
              {employees.map((employee) => (
                <option key={employee.id} value={employee.id}>
                  {getEmployeeLabel(employee)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Data de Inicio *
            </label>
            <Input
              type="date"
              name="start_date"
              value={formData.start_date}
              onChange={handleChange}
              required
             aria-label="Start Date" />
          </div>

          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Data de Fim
            </label>
            <Input
              type="date"
              name="end_date"
              value={formData.end_date || ''}
              onChange={handleChange}
             aria-label="End Date" />
          </div>

          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Função
            </label>
            <Input
              name="role"
              value={formData.role || ''}
              onChange={handleChange}
              placeholder="Ex: Agente de Portaria"
             aria-label="Ex: Agente de Portaria" />
          </div>

          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Valor Hora (R$)
            </label>
            <Input
              type="number"
              name="hourly_rate"
              value={formData.hourly_rate || 0}
              onChange={handleChange}
              min={0}
              step={0.01}
             aria-label="Hourly Rate" />
          </div>

          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Salario Mensal (R$)
            </label>
            <Input
              type="number"
              name="monthly_salary"
              value={formData.monthly_salary || 0}
              onChange={handleChange}
              min={0}
              step={0.01}
             aria-label="Monthly Salary" />
          </div>

          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Beneficios (R$)
            </label>
            <Input
              type="number"
              name="additional_benefits"
              value={formData.additional_benefits || 0}
              onChange={handleChange}
              min={0}
              step={0.01}
             aria-label="Additional Benefits" />
          </div>
        </div>

        <div className="flex flex-wrap gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              name="is_primary"
              checked={!!formData.is_primary}
              onChange={handleChange}
              className="rounded border-[hsl(var(--border))]"
             aria-label="Is Primary" />
            Alocação principal
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              name="is_temporary"
              checked={!!formData.is_temporary}
              onChange={handleChange}
              className="rounded border-[hsl(var(--border))]"
             aria-label="Is Temporary" />
            Alocação temporaria
          </label>
        </div>

        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Observações
          </label>
          <textarea
            name="notes"
            value={formData.notes || ''}
            onChange={handleChange}
            rows={3}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm resize-none"
           aria-label="Notes" />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={isLoading}>
            {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            Criar Alocação
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
