'use client';

import { AlertCircle, Loader2, Save } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';

interface MaintenanceFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  maintenance?: any;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

interface FormData {
  equipment_name: string;
  maintenance_type: string;
  priority: string;
  technician_name: string;
  scheduled_date: string;
  description: string;
  observacoes: string;
}

const createFormData = (maintenance?: any): FormData => ({
  equipment_name: maintenance?.equipment_name || '',
  maintenance_type: maintenance?.maintenance_type || 'preventiva',
  priority: maintenance?.priority || 'medium',
  technician_name: maintenance?.technician_name || '',
  scheduled_date: maintenance?.scheduled_date
    ? maintenance.scheduled_date.split('T')[0]
    : '',
  description: maintenance?.description || '',
  observacoes: maintenance?.observacoes || '',
});

export function MaintenanceFormModal({
  isOpen,
  onClose,
  maintenance,
  onSubmit,
  isLoading = false,
}: MaintenanceFormModalProps) {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const isEditing = !!maintenance;

  const formKey = useMemo(() => maintenance?.id || maintenance?.codigo || 'new', [maintenance]);

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<FormData>({ defaultValues: createFormData(maintenance) });

  useEffect(() => {
    if (isOpen) {
      reset(createFormData(maintenance));
      setSubmitError(null);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps -- Intentional deps
  }, [isOpen, formKey]);

  const onFormSubmit = async (data: FormData) => {
    setSubmitError(null);
    try {
      await onSubmit(data);
    } catch (err: any) {
      setSubmitError(err?.message || 'Erro ao salvar manutenção');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Manutenção' : 'Nova Manutenção'}
      description={
        isEditing
          ? `Editando manutenção ${maintenance?.codigo || ''}`
          : 'Preencha os dados da manutenção'
      }
      size="lg"
    >
      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-5">
        {submitError && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-center gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {submitError}
          </div>
        )}

        {/* Equipamento */}
        <div className="space-y-2">
          <Label htmlFor="equipment_name">Equipamento *</Label>
          <Input
            id="equipment_name"
            placeholder="Nome do equipamento"
            aria-label="Nome do equipamento"
            className={errors.equipment_name ? 'border-red-500' : ''}
            {...register('equipment_name', { required: 'Nome do equipamento é obrigatório' })}
          />
          {errors.equipment_name && (
            <p className="text-xs text-red-500">{errors.equipment_name.message}</p>
          )}
        </div>

        {/* Tipo e Prioridade */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Tipo de Manutenção *</Label>
            <Controller
              name="maintenance_type"
              control={control}
              rules={{ required: 'Tipo de manutenção é obrigatório' }}
              render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="preventiva">Preventiva</SelectItem>
                    <SelectItem value="corretiva">Corretiva</SelectItem>
                    <SelectItem value="emergencial">Emergencial</SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
          </div>

          <div className="space-y-2">
            <Label>Prioridade *</Label>
            <Controller
              name="priority"
              control={control}
              rules={{ required: 'Prioridade é obrigatória' }}
              render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione a prioridade" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Baixa</SelectItem>
                    <SelectItem value="medium">Média</SelectItem>
                    <SelectItem value="high">Alta</SelectItem>
                    <SelectItem value="critical">Crítica</SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
          </div>
        </div>

        {/* Técnico e Data */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="technician_name">Técnico Responsável</Label>
            <Input
              id="technician_name"
              placeholder="Nome do técnico"
              aria-label="Nome do técnico"
              {...register('technician_name')}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="scheduled_date">Data Agendada *</Label>
            <Input
              id="scheduled_date"
              type="date"
              aria-label="Data agendada"
              className={errors.scheduled_date ? 'border-red-500' : ''}
              {...register('scheduled_date', { required: 'Data agendada é obrigatória' })}
            />
            {errors.scheduled_date && (
              <p className="text-xs text-red-500">{errors.scheduled_date.message}</p>
            )}
          </div>
        </div>

        {/* Descrição */}
        <div className="space-y-2">
          <Label htmlFor="description">Descrição</Label>
          <Textarea
            id="description"
            placeholder="Descreva a manutenção a ser realizada..."
            rows={3}
            aria-label="Descrição da manutenção"
            {...register('description')}
          />
        </div>

        {/* Observações */}
        <div className="space-y-2">
          <Label htmlFor="observacoes">Observações</Label>
          <Textarea
            id="observacoes"
            placeholder="Observações adicionais..."
            rows={3}
            aria-label="Observações adicionais"
            {...register('observacoes')}
          />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            {isEditing ? 'Salvar Alterações' : 'Criar Manutenção'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
