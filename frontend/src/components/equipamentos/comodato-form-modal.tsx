'use client';

import { AlertCircle, Loader2 } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface ComodatoFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  comodato?: any;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

const defaultFormData = {
  client_name: '',
  equipment_name: '',
  start_date: '',
  end_date: '',
  terms: '',
  observacoes: '',
};

// Form state factory
const createFormData = (comodato?: any) => ({
  client_name: comodato?.client_name ?? '',
  equipment_name: comodato?.equipment_name ?? '',
  start_date: comodato?.start_date ? comodato.start_date.substring(0, 10) : '',
  end_date: comodato?.end_date ? comodato.end_date.substring(0, 10) : '',
  terms: comodato?.terms ?? '',
  observacoes: comodato?.observacoes ?? '',
});

export function ComodatoFormModal({
  isOpen,
  onClose,
  comodato,
  onSubmit,
  isLoading = false,
}: ComodatoFormModalProps) {
  const [formData, setFormData] = useState(defaultFormData);
  const [error, setError] = useState<string | null>(null);

  const isEditing = !!comodato;

  const formKey = useMemo(() => {
    return comodato?.id || comodato?.codigo || 'new';
  }, [comodato]);

  useEffect(() => {
    if (isOpen) {
      if (comodato) {

        setFormData(createFormData(comodato));
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
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.client_name.trim()) {
      setError('Informe o nome do cliente.');
      return;
    }

    if (!formData.equipment_name.trim()) {
      setError('Informe o nome do equipamento.');
      return;
    }

    if (!formData.start_date) {
      setError('Informe a data de inicio.');
      return;
    }

    if (!formData.end_date) {
      setError('Informe a data de fim.');
      return;
    }

    try {
      await onSubmit({
        ...formData,
        start_date: formData.start_date || null,
        end_date: formData.end_date || null,
        terms: formData.terms || null,
        observacoes: formData.observacoes || null,
      });
    } catch (err: any) {
      setError(err?.message || 'Erro ao salvar comodato.');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Comodato' : 'Novo Comodato'}
      description={isEditing ? `Editando comodato ${comodato?.codigo ?? ''}` : 'Preencha os dados do contrato de comodato'}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-center gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="client_name">Cliente *</Label>
            <Input
              id="client_name"
              name="client_name"
              value={formData.client_name}
              onChange={handleChange}
              placeholder="Nome do cliente"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="equipment_name">Equipamento *</Label>
            <Input
              id="equipment_name"
              name="equipment_name"
              value={formData.equipment_name}
              onChange={handleChange}
              placeholder="Nome do equipamento"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="start_date">Data de Inicio *</Label>
            <Input
              id="start_date"
              name="start_date"
              type="date"
              value={formData.start_date}
              onChange={handleChange}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="end_date">Data de Fim *</Label>
            <Input
              id="end_date"
              name="end_date"
              type="date"
              value={formData.end_date}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="terms">Termos do Contrato</Label>
          <Textarea
            id="terms"
            name="terms"
            value={formData.terms}
            onChange={handleChange}
            placeholder="Termos e condicoes do comodato..."
            rows={4}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="observacoes">Observacoes</Label>
          <Textarea
            id="observacoes"
            name="observacoes"
            value={formData.observacoes}
            onChange={handleChange}
            placeholder="Observacoes adicionais..."
            rows={3}
          />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            {isEditing ? 'Salvar Alteracoes' : 'Criar Comodato'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
