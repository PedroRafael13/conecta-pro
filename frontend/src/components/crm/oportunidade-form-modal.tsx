'use client';

import { useState, useEffect, useMemo } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface OportunidadeFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  oportunidade?: any | null;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

// Initial form state factory
const createInitialForm = (oportunidade?: any | null) => ({
  nome: oportunidade?.nome || '',
  cliente: oportunidade?.cliente || '',
  valor_estimado: oportunidade?.valor_estimado || 0,
  status: oportunidade?.status || 'novo',
  responsavel: oportunidade?.responsavel || '',
  observacoes: oportunidade?.observacoes || '',
});

export function OportunidadeFormModal({
  isOpen,
  onClose,
  oportunidade,
  onSubmit,
  isLoading,
}: OportunidadeFormModalProps) {
  const isEditing = !!oportunidade;

  const formKey = useMemo(() => {
    return oportunidade?.id || oportunidade?.codigo || 'new';
  }, [oportunidade]);

  const [form, setForm] = useState(createInitialForm(oportunidade));

  useEffect(() => {
    if (isOpen) {

      setForm(createInitialForm(oportunidade));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps -- Intentional deps
  }, [isOpen, formKey]);

  const handleSubmit = async () => {
    await onSubmit(form);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Oportunidade' : 'Nova Oportunidade'}
      size="lg"
    >
      <div className="grid gap-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="nome">Nome</Label>
            <Input
              id="nome"
              value={form.nome}
              onChange={(e) => setForm({ ...form, nome: e.target.value })}
              placeholder="Nome da oportunidade"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="cliente">Cliente</Label>
            <Input
              id="cliente"
              value={form.cliente}
              onChange={(e) => setForm({ ...form, cliente: e.target.value })}
              placeholder="Nome do cliente"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="valor_estimado">Valor Estimado (R$)</Label>
            <Input
              id="valor_estimado"
              type="number"
              value={form.valor_estimado}
              onChange={(e) => setForm({ ...form, valor_estimado: Number(e.target.value) })}
              placeholder="0,00"
            />
          </div>
          <div className="grid gap-2">
            <Label>Status</Label>
            <Select value={form.status} onValueChange={(v) => setForm({ ...form, status: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="novo">Novo</SelectItem>
                <SelectItem value="qualificado">Qualificado</SelectItem>
                <SelectItem value="proposta">Proposta</SelectItem>
                <SelectItem value="negociacao">Negociação</SelectItem>
                <SelectItem value="ganho">Ganho</SelectItem>
                <SelectItem value="perdido">Perdido</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="grid gap-2">
          <Label htmlFor="responsavel">Responsável</Label>
          <Input
            id="responsavel"
            value={form.responsavel}
            onChange={(e) => setForm({ ...form, responsavel: e.target.value })}
            placeholder="Nome do responsável"
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="observacoes">Observações</Label>
          <textarea
            id="observacoes"
            value={form.observacoes}
            onChange={(e) => setForm({ ...form, observacoes: e.target.value })}
            placeholder="Observações sobre a oportunidade..."
            rows={3}
            className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          />
        </div>
      </div>
      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isLoading}>
          Cancelar
        </Button>
        <Button onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? 'Salvando...' : isEditing ? 'Salvar' : 'Criar'}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
