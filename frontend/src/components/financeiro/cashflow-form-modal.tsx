'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { AlertCircle, Loader2 } from 'lucide-react';

interface CashflowFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CashflowFormData) => Promise<void>;
  isLoading?: boolean;
}

interface CashflowFormData {
  description: string;
  entry_type: 'income' | 'expense';
  amount: number;
  date: string;
  category: string;
  observacoes: string;
}

const CATEGORIES = [
  'Receita Operacional',
  'Receita Financeira',
  'Folha de Pagamento',
  'Fornecedores',
  'Impostos',
  'Aluguel',
  'Servicos',
  'Manutencao',
  'Investimentos',
  'Outros',
];

export function CashflowFormModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
}: CashflowFormModalProps) {
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<CashflowFormData>({
    description: '',
    entry_type: 'income',
    amount: 0,
    date: new Date().toISOString().split('T')[0],
    category: '',
    observacoes: '',
  });

  // Reset form ao abrir/fechar
  useEffect(() => {
    if (isOpen) {
      setFormData({
        description: '',
        entry_type: 'income',
        amount: 0,
        date: new Date().toISOString().split('T')[0],
        category: '',
        observacoes: '',
      });
      setError(null);
    }
  }, [isOpen]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: parseFloat(value) || 0 }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validacao
    if (!formData.description.trim()) {
      setError('Descricao e obrigatoria');
      return;
    }
    if (formData.amount <= 0) {
      setError('Valor deve ser maior que zero');
      return;
    }
    if (!formData.date) {
      setError('Data e obrigatoria');
      return;
    }

    try {
      await onSubmit(formData);
    } catch (err: any) {
      setError(err?.message || 'Erro ao salvar lancamento');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Novo Lancamento"
      description="Registre uma nova entrada ou saida no fluxo de caixa"
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-start gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span className="flex-1">{error}</span>
          </div>
        )}

        {/* Descricao */}
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Descricao *
          </label>
          <Input
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Ex: Pagamento de fornecedor X"
            required
          />
        </div>

        {/* Tipo e Valor */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Tipo *
            </label>
            <select
              name="entry_type"
              value={formData.entry_type}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
              required
            >
              <option value="income">Entrada</option>
              <option value="expense">Saida</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Valor (R$) *
            </label>
            <Input
              type="number"
              name="amount"
              value={formData.amount || ''}
              onChange={handleChange}
              placeholder="0,00"
              min={0.01}
              step={0.01}
              required
            />
          </div>
        </div>

        {/* Data e Categoria */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Data *
            </label>
            <Input
              type="date"
              name="date"
              value={formData.date}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Categoria
            </label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
            >
              <option value="">Selecione...</option>
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Observacoes */}
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Observacoes
          </label>
          <textarea
            name="observacoes"
            value={formData.observacoes}
            onChange={handleChange}
            rows={3}
            placeholder="Observacoes adicionais sobre o lancamento..."
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
          />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={isLoading}>
            {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            Salvar Lancamento
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
