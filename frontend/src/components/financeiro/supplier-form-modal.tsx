'use client';

import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { AlertCircle, Loader2 } from 'lucide-react';

interface SupplierFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  supplier?: any;
  onSubmit: (data: SupplierFormData) => Promise<void>;
  isLoading?: boolean;
}

interface SupplierFormData {
  name: string;
  document: string;
  email: string;
  phone: string;
  address: string;
  category: string;
  observacoes: string;
}

const SUPPLIER_CATEGORIES = [
  'Material de Escritorio',
  'Equipamentos',
  'Servicos de Limpeza',
  'Servicos de Manutencao',
  'Servicos de Seguranca',
  'Tecnologia',
  'Alimentacao',
  'Transporte',
  'Consultoria',
  'Uniformes e EPIs',
  'Outros',
];

export function SupplierFormModal({
  isOpen,
  onClose,
  supplier,
  onSubmit,
  isLoading = false,
}: SupplierFormModalProps) {
  const isEditing = !!supplier;
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<SupplierFormData>({
    name: '',
    document: '',
    email: '',
    phone: '',
    address: '',
    category: '',
    observacoes: '',
  });

  // Populate form when editing or reset when creating
  useEffect(() => {
    if (isOpen) {
      if (supplier) {
        setFormData({
          name: supplier.name || '',
          document: supplier.document || '',
          email: supplier.email || '',
          phone: supplier.phone || '',
          address: supplier.address || '',
          category: supplier.category || '',
          observacoes: supplier.observacoes || supplier.notes || '',
        });
      } else {
        setFormData({
          name: '',
          document: '',
          email: '',
          phone: '',
          address: '',
          category: '',
          observacoes: '',
        });
      }
      setError(null);
    }
  }, [isOpen, supplier]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
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
      setError(err?.message || 'Erro ao salvar fornecedor');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Editar Fornecedor' : 'Novo Fornecedor'}
      description={isEditing ? `Editando ${supplier?.name}` : 'Cadastre um novo fornecedor'}
      size="lg"
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
            Nome / Razao Social *
          </label>
          <Input
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Nome completo ou razao social"
            required
          />
        </div>

        {/* Documento e Email */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              CNPJ/CPF
            </label>
            <Input
              name="document"
              value={formData.document}
              onChange={handleDocumentChange}
              placeholder="00.000.000/0000-00"
              maxLength={18}
            />
          </div>
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Email
            </label>
            <Input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="contato@fornecedor.com"
            />
          </div>
        </div>

        {/* Telefone e Categoria */}
        <div className="grid grid-cols-2 gap-4">
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
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Categoria
            </label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
            >
              <option value="">Selecione...</option>
              {SUPPLIER_CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
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

        {/* Observacoes */}
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Observacoes
          </label>
          <textarea
            name="observacoes"
            value={formData.observacoes}
            onChange={handleChange}
            rows={3}
            placeholder="Informacoes adicionais sobre o fornecedor..."
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
          />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={isLoading}>
            {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            {isEditing ? 'Salvar Alteracoes' : 'Cadastrar Fornecedor'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
