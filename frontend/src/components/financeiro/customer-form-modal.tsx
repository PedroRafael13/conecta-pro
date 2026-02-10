'use client';

import { AlertCircle, Loader2 } from 'lucide-react';
import { useState, useEffect, useCallback } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface CustomerFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  customer?: any;
  onSubmit: (data: CustomerFormData) => Promise<void>;
  isLoading?: boolean;
}

interface CustomerFormData {
  name: string;
  email: string;
  phone: string;
  document: string;
  address: string;
}

const defaultFormData: CustomerFormData = {
  name: '',
  email: '',
  phone: '',
  document: '',
  address: '',
};

export function CustomerFormModal({
  isOpen,
  onClose,
  customer,
  onSubmit,
  isLoading = false,
}: CustomerFormModalProps) {
  const isEditing = !!customer;
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<CustomerFormData>(defaultFormData);

  // Create form data from customer
  const createFormData = useCallback((cust?: any): CustomerFormData => ({
    name: cust?.name || '',
    email: cust?.email || '',
    phone: cust?.phone || '',
    document: cust?.document || '',
    address: cust?.address || '',
  }), []);

  useEffect(() => {
    if (isOpen) {
      if (customer) {
        // eslint-disable-next-line react-hooks/set-state-in-effect -- Form sync
        setFormData(createFormData(customer));
      } else {

        setFormData(defaultFormData);
      }

      setError(null);
    }
  }, [isOpen, customer, createFormData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Mascara para CNPJ/CPF
  const handleDocumentChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '');

    if (value.length <= 11) {
      // CPF: 000.000.000-00
      value = value
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d{1,2})/, '$1-$2')
        .replace(/(-\d{2})\d+?$/, '$1');
    } else {
      // CNPJ: 00.000.000/0000-00
      value = value
        .replace(/(\d{2})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d)/, '$1/$2')
        .replace(/(\d{4})(\d{1,2})/, '$1-$2')
        .replace(/(-\d{2})\d+?$/, '$1');
    }

    setFormData((prev) => ({ ...prev, document: value }));
  };

  // Mascara para telefone
  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '');

    if (value.length <= 10) {
      // Fixo: (00) 0000-0000
      value = value
        .replace(/(\d{2})(\d)/, '($1) $2')
        .replace(/(\d{4})(\d)/, '$1-$2');
    } else {
      // Celular: (00) 00000-0000
      value = value
        .replace(/(\d{2})(\d)/, '($1) $2')
        .replace(/(\d{5})(\d)/, '$1-$2')
        .replace(/(-\d{4})\d+?$/, '$1');
    }

    setFormData((prev) => ({ ...prev, phone: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validacao
    if (!formData.name.trim()) {
      setError('Nome e obrigatorio');
      return;
    }

    try {
      await onSubmit(formData);
    } catch (err: any) {
      setError(err?.message || 'Erro ao salvar cliente');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Cliente' : 'Novo Cliente'}
      description={isEditing ? `Editando ${customer?.name}` : 'Cadastre um novo cliente'}
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-start gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span className="flex-1">{error}</span>
          </div>
        )}

        {/* Nome */}
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Nome *
          </label>
          <Input
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Nome completo ou razao social"
            required
          />
        </div>

        {/* Email e Documento */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Email
            </label>
            <Input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="cliente@email.com"
            />
          </div>
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              CPF/CNPJ
            </label>
            <Input
              name="document"
              value={formData.document}
              onChange={handleDocumentChange}
              placeholder="000.000.000-00"
              maxLength={18}
            />
          </div>
        </div>

        {/* Telefone */}
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Telefone
          </label>
          <Input
            name="phone"
            value={formData.phone}
            onChange={handlePhoneChange}
            placeholder="(00) 00000-0000"
            maxLength={15}
          />
        </div>

        {/* Endereco */}
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Endereco
          </label>
          <Input
            name="address"
            value={formData.address}
            onChange={handleChange}
            placeholder="Rua, numero, bairro, cidade - UF"
          />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={isLoading}>
            {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            {isEditing ? 'Salvar Alteracoes' : 'Cadastrar Cliente'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
