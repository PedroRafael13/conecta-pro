'use client';

import { useState, useEffect } from 'react';
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

interface ContratoFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  contrato?: any | null;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

export function ContratoFormModal({
  isOpen,
  onClose,
  contrato,
  onSubmit,
  isLoading,
}: ContratoFormModalProps) {
  const isEditing = !!contrato;
  const [form, setForm] = useState({
    numero: '',
    titulo: '',
    client_id: '',
    contract_type: 'servico_vigilancia',
    valor_mensal: 0,
    data_inicio: '',
    data_fim: '',
    observacoes: '',
  });

  useEffect(() => {
    if (contrato) {
      setForm({
        numero: contrato.numero || '',
        titulo: contrato.titulo || contrato.title || '',
        client_id: contrato.client_id || '',
        contract_type: contrato.contract_type || 'servico_vigilancia',
        valor_mensal: contrato.valor_mensal || contrato.monthly_value || 0,
        data_inicio: contrato.data_inicio || contrato.start_date || '',
        data_fim: contrato.data_fim || contrato.end_date || '',
        observacoes: contrato.observacoes || contrato.notes || '',
      });
    } else {
      setForm({
        numero: '',
        titulo: '',
        client_id: '',
        contract_type: 'servico_vigilancia',
        valor_mensal: 0,
        data_inicio: '',
        data_fim: '',
        observacoes: '',
      });
    }
  }, [contrato, isOpen]);

  const handleSubmit = async () => {
    await onSubmit(form);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Contrato' : 'Novo Contrato'}
      size="lg"
    >
      <div className="grid gap-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="numero">Numero</Label>
            <Input
              id="numero"
              value={form.numero}
              onChange={(e) => setForm({ ...form, numero: e.target.value })}
              placeholder="CT-001"
              disabled={isEditing}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="titulo">Titulo</Label>
            <Input
              id="titulo"
              value={form.titulo}
              onChange={(e) => setForm({ ...form, titulo: e.target.value })}
              placeholder="Titulo do contrato"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="client_id">Cliente ID</Label>
            <Input
              id="client_id"
              value={form.client_id}
              onChange={(e) => setForm({ ...form, client_id: e.target.value })}
              placeholder="ID do cliente"
            />
          </div>
          <div className="grid gap-2">
            <Label>Tipo de Contrato</Label>
            <Select
              value={form.contract_type}
              onValueChange={(v) => setForm({ ...form, contract_type: v })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="servico_vigilancia">Servico de Vigilancia</SelectItem>
                <SelectItem value="servico_portaria">Servico de Portaria</SelectItem>
                <SelectItem value="servico_limpeza">Servico de Limpeza</SelectItem>
                <SelectItem value="misto">Misto</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="valor_mensal">Valor Mensal (R$)</Label>
            <Input
              id="valor_mensal"
              type="number"
              value={form.valor_mensal}
              onChange={(e) => setForm({ ...form, valor_mensal: Number(e.target.value) })}
              placeholder="0,00"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="data_inicio">Data Inicio</Label>
            <Input
              id="data_inicio"
              type="date"
              value={form.data_inicio}
              onChange={(e) => setForm({ ...form, data_inicio: e.target.value })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="data_fim">Data Fim</Label>
            <Input
              id="data_fim"
              type="date"
              value={form.data_fim}
              onChange={(e) => setForm({ ...form, data_fim: e.target.value })}
            />
          </div>
        </div>
        <div className="grid gap-2">
          <Label htmlFor="observacoes">Observacoes</Label>
          <Textarea
            id="observacoes"
            value={form.observacoes}
            onChange={(e) => setForm({ ...form, observacoes: e.target.value })}
            placeholder="Observacoes sobre o contrato..."
            rows={3}
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
