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

interface OrdemFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  ordem?: any | null;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

// Initial form state factory
const createInitialForm = (ordem?: any | null) => ({
  titulo: ordem?.titulo || '',
  descricao: ordem?.descricao || '',
  cliente: ordem?.cliente || '',
  prioridade: ordem?.prioridade || 'media',
  tipo: ordem?.tipo || 'corretiva',
  data_prevista: ordem?.data_prevista || '',
});

export function OrdemFormModal({
  isOpen,
  onClose,
  ordem,
  onSubmit,
  isLoading,
}: OrdemFormModalProps) {
  const isEditing = !!ordem;

  const formKey = useMemo(() => {
    return ordem?.id || ordem?.codigo || 'new';
  }, [ordem]);

  const [form, setForm] = useState(createInitialForm(ordem));

  useEffect(() => {
    if (isOpen) {

      setForm(createInitialForm(ordem));
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
      title={isEditing ? 'Editar Ordem de Servico' : 'Nova Ordem de Servico'}
      size="lg"
    >
      <div className="grid gap-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="titulo">Titulo</Label>
            <Input
              id="titulo"
              value={form.titulo}
              onChange={(e) => setForm({ ...form, titulo: e.target.value })}
              placeholder="Titulo da ordem de servico"
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
        <div className="grid gap-2">
          <Label htmlFor="descricao">Descricao</Label>
          <Textarea
            id="descricao"
            value={form.descricao}
            onChange={(e) => setForm({ ...form, descricao: e.target.value })}
            placeholder="Descreva o servico a ser realizado..."
            rows={3}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="grid gap-2">
            <Label>Prioridade</Label>
            <Select
              value={form.prioridade}
              onValueChange={(v) => setForm({ ...form, prioridade: v })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="baixa">Baixa</SelectItem>
                <SelectItem value="media">Media</SelectItem>
                <SelectItem value="alta">Alta</SelectItem>
                <SelectItem value="urgente">Urgente</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <Label>Tipo</Label>
            <Select
              value={form.tipo}
              onValueChange={(v) => setForm({ ...form, tipo: v })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="corretiva">Corretiva</SelectItem>
                <SelectItem value="preventiva">Preventiva</SelectItem>
                <SelectItem value="instalacao">Instalacao</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="data_prevista">Data Prevista</Label>
            <Input
              id="data_prevista"
              type="date"
              value={form.data_prevista}
              onChange={(e) => setForm({ ...form, data_prevista: e.target.value })}
            />
          </div>
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
