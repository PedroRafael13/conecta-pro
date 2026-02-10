'use client';

import { useState, useEffect, useMemo } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface ReceivableFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  receivable?: any;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

const CATEGORIES = [
  { value: 'service', label: 'Servico' },
  { value: 'product', label: 'Produto' },
  { value: 'subscription', label: 'Assinatura' },
  { value: 'rental', label: 'Aluguel' },
  { value: 'other', label: 'Outros' },
];

// Initial form state factory
const createInitialForm = (receivable?: any) => ({
  description: receivable?.description || '',
  customer_name: receivable?.customer_name || '',
  amount: receivable?.amount ? String(receivable.amount) : '',
  due_date: receivable?.due_date ? receivable.due_date.split('T')[0] : '',
  category: receivable?.category || '',
  observacoes: receivable?.observacoes || '',
});

export function ReceivableFormModal({
  isOpen,
  onClose,
  receivable,
  onSubmit,
  isLoading = false,
}: ReceivableFormModalProps) {
  const isEditing = !!receivable?.id;

  const formKey = useMemo(() => {
    return receivable?.id || 'new';
  }, [receivable]);

  const [form, setForm] = useState(createInitialForm(receivable));

  useEffect(() => {
    if (isOpen) {

      setForm(createInitialForm(receivable));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps -- Intentional deps
  }, [isOpen, formKey]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload = {
      description: form.description,
      customer_name: form.customer_name,
      amount: parseFloat(form.amount) || 0,
      due_date: form.due_date,
      category: form.category,
      observacoes: form.observacoes || null,
    };

    await onSubmit(payload);
  };

  const updateField = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const isValid =
    form.description.trim() !== '' &&
    form.customer_name.trim() !== '' &&
    form.amount !== '' &&
    parseFloat(form.amount) > 0 &&
    form.due_date !== '';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Conta a Receber' : 'Nova Conta a Receber'}
      description={isEditing ? 'Atualize as informacoes da conta' : 'Preencha os dados da nova conta a receber'}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="description">Descricao *</Label>
            <Input
              id="description"
              value={form.description}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder="Descricao da conta a receber"
              required
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="customer_name">Cliente *</Label>
            <Input
              id="customer_name"
              value={form.customer_name}
              onChange={(e) => updateField('customer_name', e.target.value)}
              placeholder="Nome do cliente"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="amount">Valor (R$) *</Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                min="0.01"
                value={form.amount}
                onChange={(e) => updateField('amount', e.target.value)}
                placeholder="0,00"
                required
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="due_date">Vencimento *</Label>
              <Input
                id="due_date"
                type="date"
                value={form.due_date}
                onChange={(e) => updateField('due_date', e.target.value)}
                required
              />
            </div>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="category">Categoria</Label>
            <Select value={form.category} onValueChange={(v) => updateField('category', v)}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione a categoria" />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES.map((cat) => (
                  <SelectItem key={cat.value} value={cat.value}>
                    {cat.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="observacoes">Observacoes</Label>
            <Textarea
              id="observacoes"
              value={form.observacoes}
              onChange={(e) => updateField('observacoes', e.target.value)}
              placeholder="Observacoes adicionais..."
              rows={3}
            />
          </div>
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isLoading || !isValid}>
            {isLoading ? 'Salvando...' : isEditing ? 'Salvar Alteracoes' : 'Criar Conta'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
