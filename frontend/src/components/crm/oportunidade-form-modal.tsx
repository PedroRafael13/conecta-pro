'use client';

import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
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
import { customInstance } from '@/lib/api-client';
import { OPPORTUNITY_STAGE_OPTIONS } from '@/constants/crm/opportunityStage';
import { clientLabel } from '@/utils/crm/clientLabel';

interface OportunidadeFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  oportunidade?: any | null;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

const createInitialForm = (oportunidade?: any | null) => ({
  title: oportunidade?.title || oportunidade?.nome || '',
  contact_name: oportunidade?.contact_name || oportunidade?.cliente || '',
  contact_email: oportunidade?.contact_email || '',
  contact_phone: oportunidade?.contact_phone || oportunidade?.telefone || '',
  value: oportunidade?.value ?? oportunidade?.valor_estimado ?? 0,
  stage: oportunidade?.stage || oportunidade?.status || 'qualification',
  owner_id: oportunidade?.owner_id || oportunidade?.responsavel_id || '',
  description: oportunidade?.description || oportunidade?.observacoes || '',
});

export function OportunidadeFormModal({
  isOpen,
  onClose,
  oportunidade,
  onSubmit,
  isLoading,
}: OportunidadeFormModalProps) {
  const isEditing = !!oportunidade;
  const formKey = useMemo(() => oportunidade?.id || 'new', [oportunidade]);
  const [form, setForm] = useState(createInitialForm(oportunidade));

  useEffect(() => {
    if (isOpen) setForm(createInitialForm(oportunidade));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, formKey]);

  // P0.8 — Dropdown de clientes
  const { data: clientsData } = useQuery({
    queryKey: ['crm', 'clients', 'lookup'],
    queryFn: () => customInstance<{ items: any[] }>({ url: '/api/v1/crm/clients/?limit=200', method: 'GET' }),
    staleTime: 5 * 60 * 1000,
    enabled: isOpen,
  });

  // P0.8 — Dropdown de usuários (responsáveis)
  const { data: usersData } = useQuery({
    queryKey: ['users', 'lookup'],
    queryFn: () => customInstance<{ users: any[] }>({ url: '/api/v1/users/?limit=100', method: 'GET' }),
    staleTime: 5 * 60 * 1000,
    enabled: isOpen,
  });

  const clients = clientsData?.items ?? [];
  const users = usersData?.users ?? [];

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
            <Label htmlFor="title">Nome da oportunidade *</Label>
            <Input
              id="title"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="Ex: Expansão Segurança — Cliente XYZ"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="stage">Etapa *</Label>
            <Select value={form.stage} onValueChange={(v) => setForm({ ...form, stage: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {OPPORTUNITY_STAGE_OPTIONS.map(opt => (
                  <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="contact_name">Cliente / Contato *</Label>
            {clients.length > 0 ? (
              <Select
                value={form.contact_name}
                onValueChange={(v) => setForm({ ...form, contact_name: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="— Selecione cliente —" />
                </SelectTrigger>
                <SelectContent>
                  {clients.map((c: any) => (
                    <SelectItem key={c.id} value={clientLabel(c)}>
                      {clientLabel(c)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <Input
                id="contact_name"
                value={form.contact_name}
                onChange={(e) => setForm({ ...form, contact_name: e.target.value })}
                placeholder="Nome do contato ou empresa"
              />
            )}
          </div>
          <div className="grid gap-2">
            <Label htmlFor="contact_email">E-mail do contato *</Label>
            <Input
              id="contact_email"
              type="email"
              value={form.contact_email}
              onChange={(e) => setForm({ ...form, contact_email: e.target.value })}
              placeholder="contato@empresa.com"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="value">Valor estimado (R$)</Label>
            <Input
              id="value"
              type="number"
              value={form.value}
              onChange={(e) => setForm({ ...form, value: Number(e.target.value) })}
              placeholder="0,00"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="owner_id">Responsável</Label>
            {users.length > 0 ? (
              <Select
                value={form.owner_id}
                onValueChange={(v) => setForm({ ...form, owner_id: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="— Selecione responsável —" />
                </SelectTrigger>
                <SelectContent>
                  {users.map((u: any) => (
                    <SelectItem key={u.id} value={u.id}>
                      {u.full_name || u.name || u.email}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <Input
                id="owner_id"
                value={form.owner_id}
                onChange={(e) => setForm({ ...form, owner_id: e.target.value })}
                placeholder="ID ou nome do responsável"
              />
            )}
          </div>
        </div>

        <div className="grid gap-2">
          <Label htmlFor="description">Descrição / Observações</Label>
          <textarea
            id="description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="Contexto e observações sobre a oportunidade..."
            rows={3}
            className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          />
        </div>
      </div>
      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isLoading}>
          Cancelar
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={isLoading || !form.title.trim() || !form.contact_name.trim() || !form.contact_email.trim()}
        >
          {isLoading ? 'Salvando...' : isEditing ? 'Salvar' : 'Criar'}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
