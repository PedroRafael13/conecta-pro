'use client';

import { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Calculator } from 'lucide-react';

interface JournalEntryFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  isLoading?: boolean;
}

export function JournalEntryFormModal({ isOpen, onClose, onSubmit, isLoading = false }: JournalEntryFormModalProps) {
  const [formData, setFormData] = useState({
    date: '',
    description: '',
    debit_account: '',
    credit_account: '',
    amount: '',
    observacoes: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      date: formData.date,
      description: formData.description,
      debit_account: formData.debit_account,
      credit_account: formData.credit_account,
      amount: parseFloat(formData.amount) || 0,
      observacoes: formData.observacoes,
    });
  };

  const handleClose = () => {
    setFormData({
      date: '',
      description: '',
      debit_account: '',
      credit_account: '',
      amount: '',
      observacoes: '',
    });
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Novo Lancamento Contabil"
      description="Registre um lancamento no diario contabil"
      size="lg"
    >
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                Data *
              </label>
              <Input
                type="date"
                value={formData.date}
                onChange={(e) => handleChange('date', e.target.value)}
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                Valor *
              </label>
              <Input
                type="number"
                step="0.01"
                min="0.01"
                value={formData.amount}
                onChange={(e) => handleChange('amount', e.target.value)}
                placeholder="0,00"
                required
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
              Descricao *
            </label>
            <Input
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              placeholder="Descricao do lancamento"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                Conta Debito *
              </label>
              <Input
                value={formData.debit_account}
                onChange={(e) => handleChange('debit_account', e.target.value)}
                placeholder="Codigo ou nome da conta"
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                Conta Credito *
              </label>
              <Input
                value={formData.credit_account}
                onChange={(e) => handleChange('credit_account', e.target.value)}
                placeholder="Codigo ou nome da conta"
                required
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
              Observacoes
            </label>
            <textarea
              value={formData.observacoes}
              onChange={(e) => handleChange('observacoes', e.target.value)}
              placeholder="Observacoes adicionais sobre o lancamento..."
              rows={3}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] resize-none"
            />
          </div>
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={handleClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={isLoading}>
            {isLoading ? 'Registrando...' : 'Registrar Lancamento'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
