'use client';

import { useState, useEffect, useMemo } from 'react';
import { toast } from 'sonner';
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
import { CnpjSearchButton } from '@/components/crm/CnpjSearchButton';
import { CepAutoFill } from '@/components/crm/CepAutoFill';
import type { CNPJEnrichment, CEPEnrichment } from '@/types/crm/enrichment';

interface ClienteFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  cliente?: any | null;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

// Initial form state factory
const createInitialForm = (cliente?: any | null) => ({
  nome: cliente?.nome || '',
  cnpj: cliente?.cnpj || '',
  email: cliente?.email || '',
  telefone: cliente?.telefone || '',
  tipo: cliente?.tipo || 'condominio',
  cep: cliente?.cep || '',
  endereco: cliente?.endereco || '',
});

export function ClienteFormModal({
  isOpen,
  onClose,
  cliente,
  onSubmit,
  isLoading,
}: ClienteFormModalProps) {
  const isEditing = !!cliente;

  const formKey = useMemo(() => {
    return cliente?.id || cliente?.codigo || 'new';
  }, [cliente]);

  const [form, setForm] = useState(createInitialForm(cliente));

  useEffect(() => {
    if (isOpen) {

      setForm(createInitialForm(cliente));
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
      title={isEditing ? 'Editar Cliente' : 'Novo Cliente'}
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
              placeholder="Nome do cliente"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="cnpj">CNPJ</Label>
            <div className="flex gap-2">
              <Input
                id="cnpj"
                value={form.cnpj}
                onChange={(e) => setForm({ ...form, cnpj: e.target.value })}
                placeholder="00.000.000/0000-00"
              />
              <CnpjSearchButton
                cnpj={form.cnpj}
                onSuccess={(data: CNPJEnrichment) => {
                  setForm((f: typeof form) => ({
                    ...f,
                    nome: data.razao_social ?? f.nome,
                    endereco: [
                      data.endereco.logradouro,
                      data.endereco.numero,
                      data.endereco.bairro,
                      data.endereco.municipio && data.endereco.uf
                        ? `${data.endereco.municipio}/${data.endereco.uf}`
                        : data.endereco.municipio,
                    ].filter(Boolean).join(', '),
                    telefone: data.telefone ?? f.telefone,
                  }));
                  toast.success('Dados preenchidos via Receita Federal');
                }}
                onError={(msg: string) => toast.error(msg)}
              />
            </div>
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
              placeholder="contato@empresa.com"
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="telefone">Telefone</Label>
            <Input
              id="telefone"
              value={form.telefone}
              onChange={(e) => setForm({ ...form, telefone: e.target.value })}
              placeholder="(11) 99999-9999"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-2">
            <Label>Tipo</Label>
            <Select value={form.tipo} onValueChange={(v) => setForm({ ...form, tipo: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="condominio">Condomínio</SelectItem>
                <SelectItem value="empresa">Empresa</SelectItem>
                <SelectItem value="residencial">Residencial</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="cep">CEP</Label>
            <CepAutoFill
              cep={form.cep}
              onCepChange={(v) => setForm({ ...form, cep: v })}
              onAutoFill={(data: CEPEnrichment) => {
                setForm((f: typeof form) => ({
                  ...f,
                  endereco: [
                    data.logradouro,
                    data.bairro,
                    data.cidade && data.uf ? `${data.cidade}/${data.uf}` : data.cidade,
                  ].filter(Boolean).join(', '),
                }));
                toast.success('Endereço preenchido pelo CEP');
              }}
              onError={(msg: string) => toast.error(msg)}
            />
          </div>
        </div>
        <div className="grid gap-2">
          <Label htmlFor="endereco">Endereço</Label>
          <Input
            id="endereco"
            value={form.endereco}
            onChange={(e) => setForm({ ...form, endereco: e.target.value })}
            placeholder="Rua, número, bairro, cidade"
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
