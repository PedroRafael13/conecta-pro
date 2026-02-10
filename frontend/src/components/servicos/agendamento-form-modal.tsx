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

interface AgendamentoFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  agendamento?: any | null;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

// Initial form state factory
const createInitialForm = (agendamento?: any | null) => ({
  titulo: agendamento?.titulo || '',
  descricao: agendamento?.descricao || '',
  data: agendamento?.data || '',
  hora_inicio: agendamento?.hora_inicio || '',
  hora_fim: agendamento?.hora_fim || '',
  tipo: agendamento?.tipo || 'visita',
  responsavel: agendamento?.responsavel || '',
});

export function AgendamentoFormModal({
  isOpen,
  onClose,
  agendamento,
  onSubmit,
  isLoading,
}: AgendamentoFormModalProps) {
  const isEditing = !!agendamento;

  const formKey = useMemo(() => {
    return agendamento?.id || agendamento?.codigo || 'new';
  }, [agendamento]);

  const [form, setForm] = useState(createInitialForm(agendamento));

  useEffect(() => {
    if (isOpen) {

      setForm(createInitialForm(agendamento));
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
      title={isEditing ? 'Editar Agendamento' : 'Novo Agendamento'}
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
              placeholder="Titulo do agendamento"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="responsavel">Responsavel</Label>
            <Input
              id="responsavel"
              value={form.responsavel}
              onChange={(e) => setForm({ ...form, responsavel: e.target.value })}
              placeholder="Nome do responsavel"
            />
          </div>
        </div>
        <div className="grid gap-2">
          <Label htmlFor="descricao">Descricao</Label>
          <Textarea
            id="descricao"
            value={form.descricao}
            onChange={(e) => setForm({ ...form, descricao: e.target.value })}
            placeholder="Descricao do agendamento..."
            rows={3}
          />
        </div>
        <div className="grid grid-cols-4 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="data">Data</Label>
            <Input
              id="data"
              type="date"
              value={form.data}
              onChange={(e) => setForm({ ...form, data: e.target.value })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="hora_inicio">Hora Inicio</Label>
            <Input
              id="hora_inicio"
              type="time"
              value={form.hora_inicio}
              onChange={(e) => setForm({ ...form, hora_inicio: e.target.value })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="hora_fim">Hora Fim</Label>
            <Input
              id="hora_fim"
              type="time"
              value={form.hora_fim}
              onChange={(e) => setForm({ ...form, hora_fim: e.target.value })}
            />
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
                <SelectItem value="visita">Visita</SelectItem>
                <SelectItem value="manutencao">Manutencao</SelectItem>
                <SelectItem value="instalacao">Instalacao</SelectItem>
                <SelectItem value="auditoria">Auditoria</SelectItem>
              </SelectContent>
            </Select>
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
