'use client';

import { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ShoppingCart } from 'lucide-react';

interface PurchaseFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  isLoading?: boolean;
  type: 'requisition' | 'order';
}

export function PurchaseFormModal({ isOpen, onClose, onSubmit, isLoading = false, type }: PurchaseFormModalProps) {
  const [formData, setFormData] = useState({
    // Requisition fields
    description: '',
    requester: '',
    department: '',
    items_description: '',
    urgency: 'medium',
    // Order fields
    supplier_name: '',
    total_amount: '',
    delivery_date: '',
    payment_terms: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (type === 'requisition') {
      onSubmit({
        description: formData.description,
        requester: formData.requester,
        department: formData.department,
        items_description: formData.items_description,
        urgency: formData.urgency,
      });
    } else {
      onSubmit({
        supplier_name: formData.supplier_name,
        description: formData.description,
        total_amount: parseFloat(formData.total_amount) || 0,
        delivery_date: formData.delivery_date,
        payment_terms: formData.payment_terms,
      });
    }
  };

  const handleClose = () => {
    setFormData({
      description: '',
      requester: '',
      department: '',
      items_description: '',
      urgency: 'medium',
      supplier_name: '',
      total_amount: '',
      delivery_date: '',
      payment_terms: '',
    });
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={type === 'requisition' ? 'Nova Requisicao de Compra' : 'Nova Ordem de Compra'}
      description={type === 'requisition' ? 'Preencha os dados da requisicao' : 'Preencha os dados da ordem de compra'}
      size="lg"
    >
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          {type === 'requisition' ? (
            <>
              <div>
                <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                  Descricao *
                </label>
                <Input
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  placeholder="Descricao da requisicao"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                    Solicitante *
                  </label>
                  <Input
                    value={formData.requester}
                    onChange={(e) => handleChange('requester', e.target.value)}
                    placeholder="Nome do solicitante"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                    Departamento
                  </label>
                  <Input
                    value={formData.department}
                    onChange={(e) => handleChange('department', e.target.value)}
                    placeholder="Departamento"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                  Itens Solicitados *
                </label>
                <textarea
                  value={formData.items_description}
                  onChange={(e) => handleChange('items_description', e.target.value)}
                  placeholder="Descreva os itens solicitados, quantidades e especificacoes..."
                  rows={4}
                  required
                  className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] resize-none"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                  Urgencia
                </label>
                <Select value={formData.urgency} onValueChange={(value) => handleChange('urgency', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione a urgencia" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Baixa</SelectItem>
                    <SelectItem value="medium">Media</SelectItem>
                    <SelectItem value="high">Alta</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </>
          ) : (
            <>
              <div>
                <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                  Fornecedor *
                </label>
                <Input
                  value={formData.supplier_name}
                  onChange={(e) => handleChange('supplier_name', e.target.value)}
                  placeholder="Nome do fornecedor"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                  Descricao *
                </label>
                <Input
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  placeholder="Descricao da ordem de compra"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                    Valor Total *
                  </label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.total_amount}
                    onChange={(e) => handleChange('total_amount', e.target.value)}
                    placeholder="0,00"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                    Data de Entrega
                  </label>
                  <Input
                    type="date"
                    value={formData.delivery_date}
                    onChange={(e) => handleChange('delivery_date', e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                  Condicoes de Pagamento
                </label>
                <Input
                  value={formData.payment_terms}
                  onChange={(e) => handleChange('payment_terms', e.target.value)}
                  placeholder="Ex: 30/60/90 dias"
                />
              </div>
            </>
          )}
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={handleClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={isLoading}>
            {isLoading ? 'Salvando...' : 'Salvar'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
