'use client';

import { useState, useEffect, useCallback } from 'react';
import { X, Save } from 'lucide-react';
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';

interface ContractAddendumModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  contractId: string;
  isLoading?: boolean;
}

const defaultFormData = {
  tipo_aditivo: 'prazo',
  novo_valor: 0,
  nova_data_fim: '',
  justificativa: '',
  data_aditivo: '',
};

export function ContractAddendumModal({
  isOpen,
  onClose,
  onSubmit,
  contractId,
  isLoading,
}: ContractAddendumModalProps) {
  const [formData, setFormData] = useState(defaultFormData);

  // Reset form when modal closes
  const resetForm = useCallback(() => {
    setFormData(defaultFormData);
  }, []);

  useEffect(() => {
    if (!isOpen) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- Form sync
      resetForm();
    }
  }, [isOpen, resetForm]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      contract_id: contractId,
      tipo_aditivo: formData.tipo_aditivo,
      ...(formData.tipo_aditivo === 'valor' && { novo_valor: formData.novo_valor }),
      ...(formData.tipo_aditivo === 'prazo' && { nova_data_fim: formData.nova_data_fim }),
      justificativa: formData.justificativa,
      data_aditivo: formData.data_aditivo,
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Criar Aditivo de Contrato</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="tipo_aditivo">Tipo de Aditivo *</Label>
            <Select
              value={formData.tipo_aditivo}
              onValueChange={(value) =>
                setFormData({ ...formData, tipo_aditivo: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="prazo">Aditivo de Prazo</SelectItem>
                <SelectItem value="valor">Aditivo de Valor</SelectItem>
                <SelectItem value="escopo">Aditivo de Escopo</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {formData.tipo_aditivo === 'valor' && (
            <div className="space-y-2">
              <Label htmlFor="novo_valor">Novo Valor Total (R$) *</Label>
              <Input
                id="novo_valor"
                type="number"
                step="0.01"
                value={formData.novo_valor}
                onChange={(e) =>
                  setFormData({ ...formData, novo_valor: Number(e.target.value) })
                }
                required
                placeholder="0.00"
              />
            </div>
          )}

          {formData.tipo_aditivo === 'prazo' && (
            <div className="space-y-2">
              <Label htmlFor="nova_data_fim">Nova Data de Término *</Label>
              <Input
                id="nova_data_fim"
                type="date"
                value={formData.nova_data_fim}
                onChange={(e) =>
                  setFormData({ ...formData, nova_data_fim: e.target.value })
                }
                required
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="data_aditivo">Data do Aditivo *</Label>
            <Input
              id="data_aditivo"
              type="date"
              value={formData.data_aditivo}
              onChange={(e) =>
                setFormData({ ...formData, data_aditivo: e.target.value })
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="justificativa">Justificativa *</Label>
            <Textarea
              id="justificativa"
              value={formData.justificativa}
              onChange={(e) =>
                setFormData({ ...formData, justificativa: e.target.value })
              }
              required
              placeholder="Descreva a justificativa para o aditivo"
              rows={4}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
            >
              <X className="h-4 w-4 mr-2" />
              Cancelar
            </Button>
            <Button type="submit" disabled={isLoading}>
              <Save className="h-4 w-4 mr-2" />
              {isLoading ? 'Criando...' : 'Criar Aditivo'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
