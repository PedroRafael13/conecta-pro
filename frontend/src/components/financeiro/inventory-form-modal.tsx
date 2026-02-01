'use client';

import { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Package } from 'lucide-react';

interface InventoryFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  isLoading?: boolean;
}

export function InventoryFormModal({ isOpen, onClose, onSubmit, isLoading = false }: InventoryFormModalProps) {
  const [formData, setFormData] = useState({
    item_name: '',
    movement_type: 'entry',
    quantity: '',
    warehouse: '',
    reason: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      item_name: formData.item_name,
      movement_type: formData.movement_type,
      quantity: parseInt(formData.quantity) || 0,
      warehouse: formData.warehouse,
      reason: formData.reason,
    });
  };

  const handleClose = () => {
    setFormData({
      item_name: '',
      movement_type: 'entry',
      quantity: '',
      warehouse: '',
      reason: '',
    });
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Nova Movimentacao de Estoque"
      description="Registre uma entrada, saida ou transferencia"
      size="lg"
    >
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
              Item *
            </label>
            <Input
              value={formData.item_name}
              onChange={(e) => handleChange('item_name', e.target.value)}
              placeholder="Nome do item"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                Tipo de Movimentacao *
              </label>
              <Select value={formData.movement_type} onValueChange={(value) => handleChange('movement_type', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="entry">Entrada</SelectItem>
                  <SelectItem value="exit">Saida</SelectItem>
                  <SelectItem value="transfer">Transferencia</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                Quantidade *
              </label>
              <Input
                type="number"
                min="1"
                value={formData.quantity}
                onChange={(e) => handleChange('quantity', e.target.value)}
                placeholder="0"
                required
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
              Armazem *
            </label>
            <Input
              value={formData.warehouse}
              onChange={(e) => handleChange('warehouse', e.target.value)}
              placeholder="Nome ou codigo do armazem"
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
              Motivo
            </label>
            <textarea
              value={formData.reason}
              onChange={(e) => handleChange('reason', e.target.value)}
              placeholder="Descreva o motivo da movimentacao..."
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
            {isLoading ? 'Registrando...' : 'Registrar Movimentacao'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
