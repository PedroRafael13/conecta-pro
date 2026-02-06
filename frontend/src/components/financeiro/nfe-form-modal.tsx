'use client';

import { Landmark } from 'lucide-react';
import { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
;

interface NFeFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  isLoading?: boolean;
}

export function NFeFormModal({ isOpen, onClose, onSubmit, isLoading = false }: NFeFormModalProps) {
  const [formData, setFormData] = useState({
    tipo: 'nfe',
    recipient_name: '',
    recipient_document: '',
    description: '',
    amount: '',
    items_description: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      tipo: formData.tipo,
      recipient_name: formData.recipient_name,
      recipient_document: formData.recipient_document,
      description: formData.description,
      amount: parseFloat(formData.amount) || 0,
      items_description: formData.items_description,
    });
  };

  const handleClose = () => {
    setFormData({
      tipo: 'nfe',
      recipient_name: '',
      recipient_document: '',
      description: '',
      amount: '',
      items_description: '',
    });
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Nova Nota Fiscal"
      description="Preencha os dados para emissao da nota fiscal"
      size="lg"
    >
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
              Tipo *
            </label>
            <Select value={formData.tipo} onValueChange={(value) => handleChange('tipo', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione o tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="nfe">NF-e (Nota Fiscal Eletronica)</SelectItem>
                <SelectItem value="nfse">NFS-e (Nota Fiscal de Servico)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                Destinatario *
              </label>
              <Input
                value={formData.recipient_name}
                onChange={(e) => handleChange('recipient_name', e.target.value)}
                placeholder="Nome ou razao social"
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                CPF/CNPJ *
              </label>
              <Input
                value={formData.recipient_document}
                onChange={(e) => handleChange('recipient_document', e.target.value)}
                placeholder="000.000.000-00"
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
              placeholder="Descricao da nota fiscal"
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
              Valor Total *
            </label>
            <Input
              type="number"
              step="0.01"
              min="0"
              value={formData.amount}
              onChange={(e) => handleChange('amount', e.target.value)}
              placeholder="0,00"
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
              Itens / Servicos
            </label>
            <textarea
              value={formData.items_description}
              onChange={(e) => handleChange('items_description', e.target.value)}
              placeholder="Descreva os itens ou servicos incluidos na nota fiscal..."
              rows={4}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] resize-none"
            />
          </div>
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={handleClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={isLoading}>
            {isLoading ? 'Emitindo...' : 'Emitir Nota Fiscal'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
