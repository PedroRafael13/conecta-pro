'use client';

import { AlertCircle, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
;

interface BankAccountFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: BankAccountFormData) => Promise<void>;
  isLoading?: boolean;
}

interface BankAccountFormData {
  name: string;
  bank_name: string;
  agency: string;
  account_number: string;
  account_type: 'checking' | 'savings';
  initial_balance: number;
}

const BANKS = [
  'Banco do Brasil',
  'Bradesco',
  'Itau Unibanco',
  'Santander',
  'Caixa Economica Federal',
  'Nubank',
  'Inter',
  'Sicoob',
  'Sicredi',
  'Banrisul',
  'BTG Pactual',
  'Safra',
  'C6 Bank',
  'Original',
  'Outro',
];

export function BankAccountFormModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
}: BankAccountFormModalProps) {
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<BankAccountFormData>({
    name: '',
    bank_name: '',
    agency: '',
    account_number: '',
    account_type: 'checking',
    initial_balance: 0,
  });

  // Reset form ao abrir/fechar
  useEffect(() => {
    if (isOpen) {
      setFormData({
        name: '',
        bank_name: '',
        agency: '',
        account_number: '',
        account_type: 'checking',
        initial_balance: 0,
      });
      setError(null);
    }
  }, [isOpen]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: parseFloat(value) || 0 }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validacao
    if (!formData.name.trim()) {
      setError('Nome da conta e obrigatorio');
      return;
    }
    if (!formData.bank_name) {
      setError('Selecione o banco');
      return;
    }

    try {
      await onSubmit(formData);
    } catch (err: any) {
      setError(err?.message || 'Erro ao salvar conta bancaria');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Nova Conta Bancaria"
      description="Cadastre uma nova conta para conciliacao bancaria"
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
            Nome da Conta *
          </label>
          <Input
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Ex: Conta Principal, Conta Operacional"
            required
          />
        </div>

        {/* Banco e Tipo */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Banco *
            </label>
            <select
              name="bank_name"
              value={formData.bank_name}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
              required
            >
              <option value="">Selecione...</option>
              {BANKS.map((bank) => (
                <option key={bank} value={bank}>
                  {bank}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Tipo de Conta *
            </label>
            <select
              name="account_type"
              value={formData.account_type}
              onChange={handleChange}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
              required
            >
              <option value="checking">Conta Corrente</option>
              <option value="savings">Poupanca</option>
            </select>
          </div>
        </div>

        {/* Agencia e Conta */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Agencia
            </label>
            <Input
              name="agency"
              value={formData.agency}
              onChange={handleChange}
              placeholder="0000"
            />
          </div>
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Numero da Conta
            </label>
            <Input
              name="account_number"
              value={formData.account_number}
              onChange={handleChange}
              placeholder="00000-0"
            />
          </div>
        </div>

        {/* Saldo Inicial */}
        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Saldo Inicial (R$)
          </label>
          <Input
            type="number"
            name="initial_balance"
            value={formData.initial_balance || ''}
            onChange={handleChange}
            placeholder="0,00"
            step={0.01}
          />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={isLoading}>
            {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            Criar Conta
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
