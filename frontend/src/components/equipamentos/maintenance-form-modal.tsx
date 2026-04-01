'use client';

import { AlertCircle, Loader2, Save } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
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

const defaultFormData: FormData = {
  equipment_name: '',
  maintenance_type: 'preventiva',
  priority: 'medium',
  technician_name: '',
  scheduled_date: '',
  description: '',
  observacoes: '',
};

// Form state factory
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
  const [formData, setFormData] = useState<FormData>(defaultFormData);
  const [error, setError] = useState<string | null>(null);

  const isEditing = !!maintenance;

  const formKey = useMemo(() => {
    return maintenance?.id || maintenance?.codigo || 'new';
  }, [maintenance]);

  useEffect(() => {
    if (isOpen) {
      if (maintenance) {

        setFormData(createFormData(maintenance));
      } else {

        setFormData(defaultFormData);
      }

      setError(null);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps -- Intentional deps
  }, [isOpen, formKey]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError(null);
  };

  const validateForm = (): boolean => {
    if (!formData.equipment_name.trim()) {
      setError('Nome do equipamento é obrigatório');
      return false;
    }
    if (!formData.maintenance_type) {
      setError('Tipo de manutenção é obrigatório');
      return false;
    }
    if (!formData.priority) {
      setError('Prioridade é obrigatória');
      return false;
    }
    if (!formData.scheduled_date) {
      setError('Data agendada é obrigatória');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setError(null);
    try {
      await onSubmit(formData);
    } catch (err: any) {
      setError(err?.message || 'Erro ao salvar manutenção');
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
      <form onSubmit={handleSubmit} className="space-y-5">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-center gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Equipamento */}
        <div className="space-y-2">
          <Label htmlFor="equipment_name">Equipamento *</Label>
          <Input
            id="equipment_name"
            name="equipment_name"
            value={formData.equipment_name}
            onChange={handleChange}
            placeholder="Nome do equipamento"
           aria-label="Nome do equipamento" />
        </div>

        {/* Tipo e Prioridade */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Tipo de Manutenção *</Label>
            <Select
              value={formData.maintenance_type}
              onValueChange={(value) => handleSelectChange('maintenance_type', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Selecione o tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="preventiva">Preventiva</SelectItem>
                <SelectItem value="corretiva">Corretiva</SelectItem>
                <SelectItem value="emergencial">Emergencial</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Prioridade *</Label>
            <Select
              value={formData.priority}
              onValueChange={(value) => handleSelectChange('priority', value)}
            >
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
          </div>
        </div>

        {/* Técnico e Data */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="technician_name">Técnico Responsável</Label>
            <Input
              id="technician_name"
              name="technician_name"
              value={formData.technician_name}
              onChange={handleChange}
              placeholder="Nome do técnico"
             aria-label="Nome do técnico" />
          </div>

          <div className="space-y-2">
            <Label htmlFor="scheduled_date">Data Agendada *</Label>
            <Input
              id="scheduled_date"
              name="scheduled_date"
              type="date"
              value={formData.scheduled_date}
              onChange={handleChange}
             aria-label="Scheduled Date" />
          </div>
        </div>

        {/* Descrição */}
        <div className="space-y-2">
          <Label htmlFor="description">Descrição</Label>
          <Textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Descreva a manutenção a ser realizada..."
            rows={3}
           aria-label="Descreva a manutenção a ser realizada..." />
        </div>

        {/* Observações */}
        <div className="space-y-2">
          <Label htmlFor="observacoes">Observações</Label>
          <Textarea
            id="observacoes"
            name="observacoes"
            value={formData.observacoes}
            onChange={handleChange}
            placeholder="Observações adicionais..."
            rows={3}
           aria-label="Observações adicionais..." />
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
