'use client';

import { useState, useEffect, useMemo } from 'react';
import { X, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import type { PublicContractCreate, PublicContractUpdate } from '@/types/generated/bidding';

interface ContractFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: PublicContractCreate | PublicContractUpdate) => void;
  editData?: any;
  isLoading?: boolean;
}

// Initial form state factory
const createInitialForm = (editData?: any) => ({
  numero_contrato: editData?.numero_contrato || '',
  proposta_id: editData?.proposta_id || '',
  orgao_contratante: editData?.orgao_contratante || '',
  objeto: editData?.objeto || '',
  valor_total: editData?.valor_total || 0,
  data_assinatura: editData?.data_assinatura?.split('T')[0] || '',
  data_inicio: editData?.data_inicio?.split('T')[0] || '',
  data_fim: editData?.data_fim?.split('T')[0] || '',
  observacoes: editData?.observacoes || '',
});

export function ContractFormModal({
  isOpen,
  onClose,
  onSubmit,
  editData,
  isLoading,
}: ContractFormModalProps) {
  const formKey = useMemo(() => {
    return editData?.id || editData?.codigo || 'new';
  }, [editData]);

  const [formData, setFormData] = useState(createInitialForm(editData));

  useEffect(() => {
    if (isOpen) {

      setFormData(createInitialForm(editData));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps -- Intentional deps
  }, [isOpen, formKey]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData as any);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {editData ? 'Editar Contrato' : 'Novo Contrato'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="numero_contrato">Número do Contrato *</Label>
              <Input
                id="numero_contrato"
                value={formData.numero_contrato}
                onChange={(e) =>
                  setFormData({ ...formData, numero_contrato: e.target.value })
                }
                required
                placeholder="Ex: 001/2024"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="proposta_id">ID da Proposta</Label>
              <Input
                id="proposta_id"
                value={formData.proposta_id}
                onChange={(e) =>
                  setFormData({ ...formData, proposta_id: e.target.value })
                }
                placeholder="UUID da proposta (opcional)"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="orgao_contratante">Órgão Contratante *</Label>
            <Input
              id="orgao_contratante"
              value={formData.orgao_contratante}
              onChange={(e) =>
                setFormData({ ...formData, orgao_contratante: e.target.value })
              }
              required
              placeholder="Ex: Prefeitura Municipal de São Paulo"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="objeto">Objeto *</Label>
            <Textarea
              id="objeto"
              value={formData.objeto}
              onChange={(e) =>
                setFormData({ ...formData, objeto: e.target.value })
              }
              required
              placeholder="Descrição do objeto do contrato"
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="valor_total">Valor Total (R$) *</Label>
            <Input
              id="valor_total"
              type="number"
              step="0.01"
              value={formData.valor_total}
              onChange={(e) =>
                setFormData({ ...formData, valor_total: Number(e.target.value) })
              }
              required
              placeholder="0.00"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="data_assinatura">Data Assinatura *</Label>
              <Input
                id="data_assinatura"
                type="date"
                value={formData.data_assinatura}
                onChange={(e) =>
                  setFormData({ ...formData, data_assinatura: e.target.value })
                }
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="data_inicio">Data Início *</Label>
              <Input
                id="data_inicio"
                type="date"
                value={formData.data_inicio}
                onChange={(e) =>
                  setFormData({ ...formData, data_inicio: e.target.value })
                }
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="data_fim">Data Fim *</Label>
              <Input
                id="data_fim"
                type="date"
                value={formData.data_fim}
                onChange={(e) =>
                  setFormData({ ...formData, data_fim: e.target.value })
                }
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="observacoes">Observações</Label>
            <Textarea
              id="observacoes"
              value={formData.observacoes}
              onChange={(e) =>
                setFormData({ ...formData, observacoes: e.target.value })
              }
              placeholder="Informações adicionais"
              rows={2}
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
              {isLoading ? 'Salvando...' : 'Salvar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
