'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { reimbursementService } from '@/lib/services/reimbursement';
import { getErrorMessage } from '@/lib/api';
import type {
  ReimbursementRequest,
  ReimbursementRequestCreate,
  ReimbursementRequestUpdate,
  ReimbursementItemCreate,
  ExpenseCategory,
} from '@/types/reimbursement';
import { EXPENSE_CATEGORY_LABELS } from '@/types/reimbursement';
import { AlertCircle, Loader2, Plus, Trash2, DollarSign } from 'lucide-react';

interface ReimbursementFormModalProps {
  request?: ReimbursementRequest | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface ItemFormData {
  id?: string;
  category_type: ExpenseCategory;
  description: string;
  merchant: string;
  expense_date: string;
  amount: number;
  document_number: string;
  notes: string;
}

const EMPTY_ITEM: ItemFormData = {
  category_type: 'outros',
  description: '',
  merchant: '',
  expense_date: new Date().toISOString().split('T')[0],
  amount: 0,
  document_number: '',
  notes: '',
};

export function ReimbursementFormModal({
  request,
  isOpen,
  onClose,
  onSuccess,
}: ReimbursementFormModalProps) {
  const isEditing = !!request;

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    expense_date_start: new Date().toISOString().split('T')[0],
    expense_date_end: new Date().toISOString().split('T')[0],
    cost_center: '',
    project: '',
    notes: '',
    bank_code: '',
    bank_agency: '',
    bank_account: '',
    pix_key: '',
  });

  const [items, setItems] = useState<ItemFormData[]>([{ ...EMPTY_ITEM }]);

  // Populate form when editing
  useEffect(() => {
    if (request) {
      setFormData({
        title: request.title,
        description: request.description || '',
        expense_date_start: request.expense_date_start,
        expense_date_end: request.expense_date_end,
        cost_center: request.cost_center || '',
        project: request.project || '',
        notes: request.notes || '',
        bank_code: request.bank_code || '',
        bank_agency: request.bank_agency || '',
        bank_account: request.bank_account || '',
        pix_key: request.pix_key || '',
      });

      if (request.items && request.items.length > 0) {
        setItems(
          request.items.map((item) => ({
            id: item.id,
            category_type: item.category_type,
            description: item.description,
            merchant: item.merchant || '',
            expense_date: item.expense_date,
            amount: item.amount,
            document_number: item.document_number || '',
            notes: item.notes || '',
          }))
        );
      }
    } else {
      // Reset form when creating new
      setFormData({
        title: '',
        description: '',
        expense_date_start: new Date().toISOString().split('T')[0],
        expense_date_end: new Date().toISOString().split('T')[0],
        cost_center: '',
        project: '',
        notes: '',
        bank_code: '',
        bank_agency: '',
        bank_account: '',
        pix_key: '',
      });
      setItems([{ ...EMPTY_ITEM }]);
    }
    setError(null);
  }, [request, isOpen]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleItemChange = (
    index: number,
    field: keyof ItemFormData,
    value: string | number
  ) => {
    setItems((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const addItem = () => {
    setItems((prev) => [...prev, { ...EMPTY_ITEM }]);
  };

  const removeItem = (index: number) => {
    if (items.length > 1) {
      setItems((prev) => prev.filter((_, i) => i !== index));
    }
  };

  const calculateTotal = () => {
    return items.reduce((sum, item) => sum + (item.amount || 0), 0);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Validations
      if (!formData.title.trim()) {
        throw new Error('Titulo e obrigatorio');
      }
      if (items.length === 0 || !items.some((i) => i.description && i.amount > 0)) {
        throw new Error('Adicione pelo menos um item com descricao e valor');
      }

      const itemsToSend: ReimbursementItemCreate[] = items
        .filter((item) => item.description && item.amount > 0)
        .map((item) => ({
          category_type: item.category_type,
          description: item.description,
          merchant: item.merchant || undefined,
          expense_date: item.expense_date,
          amount: item.amount,
          document_number: item.document_number || undefined,
          notes: item.notes || undefined,
        }));

      if (isEditing && request) {
        // Update existing request
        await reimbursementService.update(request.id, {
          title: formData.title,
          description: formData.description || undefined,
          expense_date_start: formData.expense_date_start,
          expense_date_end: formData.expense_date_end,
          cost_center: formData.cost_center || undefined,
          project: formData.project || undefined,
          notes: formData.notes || undefined,
          bank_code: formData.bank_code || undefined,
          bank_agency: formData.bank_agency || undefined,
          bank_account: formData.bank_account || undefined,
          pix_key: formData.pix_key || undefined,
        });

        // Update items (simplified - delete and recreate)
        // In production, you'd want to diff and update individually
        for (const existingItem of request.items) {
          await reimbursementService.deleteItem(request.id, existingItem.id);
        }
        for (const newItem of itemsToSend) {
          await reimbursementService.addItem(request.id, newItem);
        }
      } else {
        // Create new request
        const createData: ReimbursementRequestCreate = {
          title: formData.title,
          description: formData.description || undefined,
          expense_date_start: formData.expense_date_start,
          expense_date_end: formData.expense_date_end,
          cost_center: formData.cost_center || undefined,
          project: formData.project || undefined,
          notes: formData.notes || undefined,
          bank_code: formData.bank_code || undefined,
          bank_agency: formData.bank_agency || undefined,
          bank_account: formData.bank_account || undefined,
          pix_key: formData.pix_key || undefined,
          items: itemsToSend,
        };

        await reimbursementService.create(createData);
      }

      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Solicitacao' : 'Nova Solicitacao de Reembolso'}
      description={isEditing ? `Editando ${request?.code}` : 'Preencha os dados da solicitacao'}
      size="xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-center gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Informacoes Basicas */}
        <div>
          <h3 className="text-sm font-medium text-[hsl(var(--foreground))] mb-4">
            Informacoes Basicas
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Titulo *
              </label>
              <Input
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Ex: Despesas Janeiro 2026"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Data Inicio *
              </label>
              <Input
                type="date"
                name="expense_date_start"
                value={formData.expense_date_start}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Data Fim *
              </label>
              <Input
                type="date"
                name="expense_date_end"
                value={formData.expense_date_end}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Centro de Custo
              </label>
              <Input
                name="cost_center"
                value={formData.cost_center}
                onChange={handleChange}
                placeholder="Centro de custo"
              />
            </div>
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Projeto
              </label>
              <Input
                name="project"
                value={formData.project}
                onChange={handleChange}
                placeholder="Projeto"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Descricao
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={2}
                placeholder="Descricao das despesas..."
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
              />
            </div>
          </div>
        </div>

        {/* Itens/Despesas */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-[hsl(var(--foreground))]">
              Itens/Despesas
            </h3>
            <Button type="button" variant="outline" size="sm" onClick={addItem}>
              <Plus className="w-4 h-4 mr-1" />
              Adicionar Item
            </Button>
          </div>

          <div className="space-y-4">
            {items.map((item, index) => (
              <div
                key={index}
                className="bg-[hsl(var(--muted))] rounded-lg p-4 relative"
              >
                {items.length > 1 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => removeItem(index)}
                    className="absolute top-2 right-2 text-red-500 hover:text-red-600 hover:bg-red-500/10"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs text-[hsl(var(--muted-foreground))] mb-1">
                      Categoria *
                    </label>
                    <select
                      value={item.category_type}
                      onChange={(e) =>
                        handleItemChange(index, 'category_type', e.target.value as ExpenseCategory)
                      }
                      className="w-full px-3 py-2 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
                    >
                      {Object.entries(EXPENSE_CATEGORY_LABELS).map(([value, label]) => (
                        <option key={value} value={value}>
                          {label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="md:col-span-2 lg:col-span-2">
                    <label className="block text-xs text-[hsl(var(--muted-foreground))] mb-1">
                      Descricao *
                    </label>
                    <Input
                      value={item.description}
                      onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                      placeholder="Descricao da despesa"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-[hsl(var(--muted-foreground))] mb-1">
                      Estabelecimento
                    </label>
                    <Input
                      value={item.merchant}
                      onChange={(e) => handleItemChange(index, 'merchant', e.target.value)}
                      placeholder="Nome do estabelecimento"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-[hsl(var(--muted-foreground))] mb-1">
                      Data *
                    </label>
                    <Input
                      type="date"
                      value={item.expense_date}
                      onChange={(e) => handleItemChange(index, 'expense_date', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-[hsl(var(--muted-foreground))] mb-1">
                      Valor (R$) *
                    </label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      value={item.amount || ''}
                      onChange={(e) =>
                        handleItemChange(index, 'amount', parseFloat(e.target.value) || 0)
                      }
                      placeholder="0,00"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-[hsl(var(--muted-foreground))] mb-1">
                      Num. Documento
                    </label>
                    <Input
                      value={item.document_number}
                      onChange={(e) => handleItemChange(index, 'document_number', e.target.value)}
                      placeholder="Numero NF/Recibo"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Total */}
          <div className="mt-4 flex items-center justify-end gap-2 p-3 bg-emerald-500/10 rounded-lg">
            <DollarSign className="w-5 h-5 text-emerald-500" />
            <span className="text-sm text-[hsl(var(--muted-foreground))]">Total:</span>
            <span className="text-lg font-bold text-emerald-500">
              {formatCurrency(calculateTotal())}
            </span>
          </div>
        </div>

        {/* Dados Bancarios */}
        <div>
          <h3 className="text-sm font-medium text-[hsl(var(--foreground))] mb-4">
            Dados Bancarios (para pagamento)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Banco
              </label>
              <Input
                name="bank_code"
                value={formData.bank_code}
                onChange={handleChange}
                placeholder="001"
                maxLength={10}
              />
            </div>
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Agencia
              </label>
              <Input
                name="bank_agency"
                value={formData.bank_agency}
                onChange={handleChange}
                placeholder="0001"
                maxLength={10}
              />
            </div>
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Conta
              </label>
              <Input
                name="bank_account"
                value={formData.bank_account}
                onChange={handleChange}
                placeholder="12345-6"
                maxLength={20}
              />
            </div>
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Chave PIX
              </label>
              <Input
                name="pix_key"
                value={formData.pix_key}
                onChange={handleChange}
                placeholder="email@exemplo.com"
              />
            </div>
          </div>
        </div>

        {/* Observacoes */}
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Observacoes
          </label>
          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows={2}
            placeholder="Observacoes adicionais..."
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
          />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={isLoading}>
            {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            {isEditing ? 'Salvar Alteracoes' : 'Criar Solicitacao'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
