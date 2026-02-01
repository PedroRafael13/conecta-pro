'use client';

import { useState, useEffect } from 'react';
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
import type { TenantResponse } from '@/types/generated/config/conectaPROCONFIGModuleAPI.schemas';

interface TenantFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  tenant?: TenantResponse | null;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

export function TenantFormModal({
  isOpen,
  onClose,
  tenant,
  onSubmit,
  isLoading,
}: TenantFormModalProps) {
  const isEditing = !!tenant;
  const [form, setForm] = useState({
    codigo: '',
    nome: '',
    email: '',
    cnpj: '',
    telefone: '',
    plan: 'free',
    tenant_type: '',
    max_users: 10,
    max_units: 5,
  });

  useEffect(() => {
    if (tenant) {
      setForm({
        codigo: tenant.codigo || '',
        nome: tenant.nome || '',
        email: tenant.email || '',
        cnpj: tenant.cnpj || '',
        telefone: tenant.telefone || '',
        plan: tenant.plan || 'free',
        tenant_type: tenant.tenant_type || '',
        max_users: tenant.max_users || 10,
        max_units: tenant.max_units || 5,
      });
    } else {
      setForm({
        codigo: '',
        nome: '',
        email: '',
        cnpj: '',
        telefone: '',
        plan: 'free',
        tenant_type: '',
        max_users: 10,
        max_units: 5,
      });
    }
  }, [tenant, isOpen]);

  const handleSubmit = async () => {
    await onSubmit(form);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Tenant' : 'Novo Tenant'}
      size="lg"
    >
      <div className="grid gap-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="codigo">Codigo</Label>
            <Input
              id="codigo"
              value={form.codigo}
              onChange={(e) => setForm({ ...form, codigo: e.target.value })}
              placeholder="tenant-001"
              disabled={isEditing}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="nome">Nome</Label>
            <Input
              id="nome"
              value={form.nome}
              onChange={(e) => setForm({ ...form, nome: e.target.value })}
              placeholder="Nome do tenant"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="admin@tenant.com"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="cnpj">CNPJ</Label>
            <Input
              id="cnpj"
              value={form.cnpj}
              onChange={(e) => setForm({ ...form, cnpj: e.target.value })}
              placeholder="00.000.000/0000-00"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label htmlFor="telefone">Telefone</Label>
            <Input
              id="telefone"
              value={form.telefone}
              onChange={(e) => setForm({ ...form, telefone: e.target.value })}
              placeholder="(11) 99999-9999"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="tenant_type">Tipo</Label>
            <Input
              id="tenant_type"
              value={form.tenant_type}
              onChange={(e) => setForm({ ...form, tenant_type: e.target.value })}
              placeholder="condominio, empresa..."
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="grid gap-2">
            <Label>Plano</Label>
            <Select value={form.plan} onValueChange={(v) => setForm({ ...form, plan: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="free">Free</SelectItem>
                <SelectItem value="starter">Starter</SelectItem>
                <SelectItem value="pro">Pro</SelectItem>
                <SelectItem value="enterprise">Enterprise</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="max_users">Max Usuarios</Label>
            <Input
              id="max_users"
              type="number"
              value={form.max_users}
              onChange={(e) => setForm({ ...form, max_users: Number(e.target.value) })}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="max_units">Max Unidades</Label>
            <Input
              id="max_units"
              type="number"
              value={form.max_units}
              onChange={(e) => setForm({ ...form, max_units: Number(e.target.value) })}
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
