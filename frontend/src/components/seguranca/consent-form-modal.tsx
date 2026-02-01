'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';

interface ConsentFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  isLoading?: boolean;
}

interface FormData {
  holder_name: string;
  holder_email: string;
  purpose: string;
  legal_basis: string;
  valid_until: string;
  observacoes: string;
}

const INITIAL_FORM: FormData = {
  holder_name: '',
  holder_email: '',
  purpose: '',
  legal_basis: '',
  valid_until: '',
  observacoes: '',
};

export function ConsentFormModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
}: ConsentFormModalProps) {
  const [formData, setFormData] = useState<FormData>(INITIAL_FORM);
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});

  // Reset form ao abrir
  useEffect(() => {
    if (isOpen) {
      setFormData(INITIAL_FORM);
      setErrors({});
    }
  }, [isOpen]);

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof FormData, string>> = {};

    if (!formData.holder_name.trim()) {
      newErrors.holder_name = 'Nome do titular e obrigatorio';
    }

    if (!formData.holder_email.trim()) {
      newErrors.holder_email = 'E-mail e obrigatorio';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.holder_email)) {
      newErrors.holder_email = 'E-mail invalido';
    }

    if (!formData.purpose) {
      newErrors.purpose = 'Finalidade e obrigatoria';
    }

    if (!formData.legal_basis) {
      newErrors.legal_basis = 'Base legal e obrigatoria';
    }

    if (!formData.valid_until) {
      newErrors.valid_until = 'Data de validade e obrigatoria';
    } else {
      const selectedDate = new Date(formData.valid_until);
      if (selectedDate <= new Date()) {
        newErrors.valid_until = 'Data deve ser futura';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) return;

    onSubmit({
      holder_name: formData.holder_name.trim(),
      holder_email: formData.holder_email.trim(),
      purpose: formData.purpose,
      legal_basis: formData.legal_basis,
      valid_until: new Date(formData.valid_until).toISOString(),
      observacoes: formData.observacoes.trim() || undefined,
    });
  };

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Limpar erro ao editar
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Registrar Consentimento"
      description="Registre o consentimento do titular conforme Art. 7 e 8 da LGPD"
      size="lg"
    >
      <div className="space-y-5">
        {/* Nome do Titular */}
        <div className="space-y-2">
          <Label htmlFor="holder_name">
            Nome do Titular <span className="text-red-500">*</span>
          </Label>
          <Input
            id="holder_name"
            placeholder="Nome completo do titular dos dados"
            value={formData.holder_name}
            onChange={(e) => handleChange('holder_name', e.target.value)}
            className={errors.holder_name ? 'border-red-500' : ''}
          />
          {errors.holder_name && (
            <p className="text-xs text-red-500">{errors.holder_name}</p>
          )}
        </div>

        {/* E-mail do Titular */}
        <div className="space-y-2">
          <Label htmlFor="holder_email">
            E-mail do Titular <span className="text-red-500">*</span>
          </Label>
          <Input
            id="holder_email"
            type="email"
            placeholder="email@exemplo.com"
            value={formData.holder_email}
            onChange={(e) => handleChange('holder_email', e.target.value)}
            className={errors.holder_email ? 'border-red-500' : ''}
          />
          {errors.holder_email && (
            <p className="text-xs text-red-500">{errors.holder_email}</p>
          )}
        </div>

        {/* Finalidade e Base Legal */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Finalidade */}
          <div className="space-y-2">
            <Label>
              Finalidade <span className="text-red-500">*</span>
            </Label>
            <Select
              value={formData.purpose}
              onValueChange={(value) => handleChange('purpose', value)}
            >
              <SelectTrigger className={errors.purpose ? 'border-red-500' : ''}>
                <SelectValue placeholder="Selecione a finalidade" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="marketing">Marketing e Publicidade</SelectItem>
                <SelectItem value="analytics">Analise e Estatisticas</SelectItem>
                <SelectItem value="data_sharing">Compartilhamento de Dados</SelectItem>
                <SelectItem value="profiling">Perfilamento</SelectItem>
              </SelectContent>
            </Select>
            {errors.purpose && (
              <p className="text-xs text-red-500">{errors.purpose}</p>
            )}
          </div>

          {/* Base Legal */}
          <div className="space-y-2">
            <Label>
              Base Legal <span className="text-red-500">*</span>
            </Label>
            <Select
              value={formData.legal_basis}
              onValueChange={(value) => handleChange('legal_basis', value)}
            >
              <SelectTrigger className={errors.legal_basis ? 'border-red-500' : ''}>
                <SelectValue placeholder="Selecione a base legal" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="consent">Consentimento do Titular</SelectItem>
                <SelectItem value="legitimate_interest">Interesse Legitimo</SelectItem>
                <SelectItem value="contract">Execucao de Contrato</SelectItem>
                <SelectItem value="legal_obligation">Obrigacao Legal</SelectItem>
              </SelectContent>
            </Select>
            {errors.legal_basis && (
              <p className="text-xs text-red-500">{errors.legal_basis}</p>
            )}
          </div>
        </div>

        {/* Validade */}
        <div className="space-y-2">
          <Label htmlFor="valid_until">
            Valido ate <span className="text-red-500">*</span>
          </Label>
          <Input
            id="valid_until"
            type="date"
            value={formData.valid_until}
            onChange={(e) => handleChange('valid_until', e.target.value)}
            className={errors.valid_until ? 'border-red-500' : ''}
          />
          {errors.valid_until && (
            <p className="text-xs text-red-500">{errors.valid_until}</p>
          )}
        </div>

        {/* Observacoes */}
        <div className="space-y-2">
          <Label htmlFor="observacoes">Observacoes</Label>
          <Textarea
            id="observacoes"
            placeholder="Observacoes adicionais sobre o consentimento..."
            value={formData.observacoes}
            onChange={(e) => handleChange('observacoes', e.target.value)}
            rows={3}
          />
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isLoading}>
          Cancelar
        </Button>
        <Button variant="primary" onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? 'Registrando...' : 'Registrar Consentimento'}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
