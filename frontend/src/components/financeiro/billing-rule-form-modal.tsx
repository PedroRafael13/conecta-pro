'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Receipt } from 'lucide-react';

interface BillingRuleFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  rule?: any;
  isLoading?: boolean;
}

export function BillingRuleFormModal({ isOpen, onClose, onSubmit, rule, isLoading = false }: BillingRuleFormModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    type: 'fixed',
    value: '',
    frequency: 'monthly',
    description: '',
  });

  useEffect(() => {
    if (rule) {
      setFormData({
        name: rule.name || '',
        type: rule.type || 'fixed',
        value: rule.value?.toString() || '',
        frequency: rule.frequency || 'monthly',
        description: rule.description || '',
      });
    } else {
      setFormData({
        name: '',
        type: 'fixed',
        value: '',
        frequency: 'monthly',
        description: '',
      });
    }
  }, [rule, isOpen]);

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      name: formData.name,
      type: formData.type,
      value: parseFloat(formData.value) || 0,
      frequency: formData.frequency,
      description: formData.description,
    });
  };

  const handleClose = () => {
    setFormData({
      name: '',
      type: 'fixed',
      value: '',
      frequency: 'monthly',
      description: '',
    });
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={rule ? 'Editar Regra de Faturamento' : 'Nova Regra de Faturamento'}
      description="Configure as regras de cobranca e faturamento"
      size="lg"
    >
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
              Nome da Regra *
            </label>
            <Input
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="Ex: Taxa de administracao"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                Tipo *
              </label>
              <Select value={formData.type} onValueChange={(value) => handleChange('type', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fixed">Fixo</SelectItem>
                  <SelectItem value="variable">Variavel</SelectItem>
                  <SelectItem value="percentage">Percentual</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
                {formData.type === 'percentage' ? 'Percentual (%) *' : 'Valor (R$) *'}
              </label>
              <Input
                type="number"
                step={formData.type === 'percentage' ? '0.1' : '0.01'}
                min="0"
                value={formData.value}
                onChange={(e) => handleChange('value', e.target.value)}
                placeholder={formData.type === 'percentage' ? '0,0' : '0,00'}
                required
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
              Periodicidade *
            </label>
            <Select value={formData.frequency} onValueChange={(value) => handleChange('frequency', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione a periodicidade" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="monthly">Mensal</SelectItem>
                <SelectItem value="quarterly">Trimestral</SelectItem>
                <SelectItem value="annual">Anual</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium text-[hsl(var(--foreground))] mb-1 block">
              Descricao
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              placeholder="Descreva a regra de faturamento..."
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
            {isLoading ? 'Salvando...' : rule ? 'Salvar Alteracoes' : 'Criar Regra'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
