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

interface PayableFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  payable?: any;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

const CATEGORIES = [
  { value: 'utilities', label: 'Utilidades' },
  { value: 'rent', label: 'Aluguel' },
  { value: 'payroll', label: 'Folha de Pagamento' },
  { value: 'supplies', label: 'Suprimentos' },
  { value: 'services', label: 'Servicos' },
  { value: 'taxes', label: 'Impostos' },
  { value: 'other', label: 'Outros' },
];

// Initial form state factory
const createInitialForm = (payable?: any) => ({
  description: payable?.description || '',
  supplier_name: payable?.supplier_name || '',
  amount: payable?.amount ? String(payable.amount) : '',
  due_date: payable?.due_date ? payable.due_date.split('T')[0] : '',
  category: payable?.category || '',
  observacoes: payable?.observacoes || '',
});

export function PayableFormModal({
  isOpen,
  onClose,
  payable,
  onSubmit,
  isLoading = false,
}: PayableFormModalProps) {
  const isEditing = !!payable?.id;

  const formKey = useMemo(() => {
    return payable?.id || 'new';
  }, [payable]);

  const [form, setForm] = useState(createInitialForm(payable));

  useEffect(() => {
    if (isOpen) {

      setForm(createInitialForm(payable));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps -- Intentional deps
  }, [isOpen, formKey]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload = {
      description: form.description,
      supplier_name: form.supplier_name,
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
    form.supplier_name.trim() !== '' &&
    form.amount !== '' &&
    parseFloat(form.amount) > 0 &&
    form.due_date !== '';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Conta a Pagar' : 'Nova Conta a Pagar'}
      description={isEditing ? 'Atualize as informacoes da conta' : 'Preencha os dados da nova conta a pagar'}
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
              placeholder="Descricao da conta a pagar"
              required
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="supplier_name">Fornecedor *</Label>
            <Input
              id="supplier_name"
              value={form.supplier_name}
              onChange={(e) => updateField('supplier_name', e.target.value)}
              placeholder="Nome do fornecedor"
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
