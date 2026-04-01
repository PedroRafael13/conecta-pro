'use client';

import { useEffect } from 'react';
import { useForm, Controller, SubmitHandler } from 'react-hook-form';
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

export function ConsentFormModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
}: ConsentFormModalProps) {
  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      holder_name: '',
      holder_email: '',
      purpose: '',
      legal_basis: '',
      valid_until: '',
      observacoes: '',
    },
  });

  useEffect(() => {
    if (isOpen) reset();
  }, [isOpen, reset]);

  const onFormSubmit: SubmitHandler<FormData> = (data) => {
    onSubmit({
      holder_name: data.holder_name.trim(),
      holder_email: data.holder_email.trim(),
      purpose: data.purpose,
      legal_basis: data.legal_basis,
      valid_until: new Date(data.valid_until).toISOString(),
      observacoes: data.observacoes.trim() || undefined,
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Registrar Consentimento"
      description="Registre o consentimento do titular conforme Art. 7 e 8 da LGPD"
      size="lg"
    >
      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-5">
        {/* Nome do Titular */}
        <div className="space-y-2">
          <Label htmlFor="holder_name">
            Nome do Titular <span className="text-red-500">*</span>
          </Label>
          <Input
            id="holder_name"
            placeholder="Nome completo do titular dos dados"
            aria-label="Nome completo do titular dos dados"
            className={errors.holder_name ? 'border-red-500' : ''}
            {...register('holder_name', { required: 'Nome do titular é obrigatório' })}
          />
          {errors.holder_name && (
            <p className="text-xs text-red-500">{errors.holder_name.message}</p>
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
            aria-label="E-mail do titular"
            className={errors.holder_email ? 'border-red-500' : ''}
            {...register('holder_email', {
              required: 'E-mail é obrigatório',
              pattern: {
                value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: 'E-mail inválido',
              },
            })}
          />
          {errors.holder_email && (
            <p className="text-xs text-red-500">{errors.holder_email.message}</p>
          )}
        </div>

        {/* Finalidade e Base Legal */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>
              Finalidade <span className="text-red-500">*</span>
            </Label>
            <Controller
              name="purpose"
              control={control}
              rules={{ required: 'Finalidade é obrigatória' }}
              render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
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
              )}
            />
            {errors.purpose && (
              <p className="text-xs text-red-500">{errors.purpose.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>
              Base Legal <span className="text-red-500">*</span>
            </Label>
            <Controller
              name="legal_basis"
              control={control}
              rules={{ required: 'Base legal é obrigatória' }}
              render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
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
              )}
            />
            {errors.legal_basis && (
              <p className="text-xs text-red-500">{errors.legal_basis.message}</p>
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
            aria-label="Data de validade"
            className={errors.valid_until ? 'border-red-500' : ''}
            {...register('valid_until', {
              required: 'Data de validade é obrigatória',
              validate: (v) => new Date(v) > new Date() || 'Data deve ser futura',
            })}
          />
          {errors.valid_until && (
            <p className="text-xs text-red-500">{errors.valid_until.message}</p>
          )}
        </div>

        {/* Observacoes */}
        <div className="space-y-2">
          <Label htmlFor="observacoes">Observacoes</Label>
          <Textarea
            id="observacoes"
            placeholder="Observacoes adicionais sobre o consentimento..."
            rows={3}
            {...register('observacoes')}
          />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={isLoading}>
            {isLoading ? 'Registrando...' : 'Registrar Consentimento'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
