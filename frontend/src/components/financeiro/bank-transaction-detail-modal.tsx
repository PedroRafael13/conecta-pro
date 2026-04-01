'use client';

import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { cn, formatCurrency, formatDate } from '@/lib/utils';

interface BankTransactionDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  transaction: any;
}

export function BankTransactionDetailModal({
  isOpen,
  onClose,
  transaction,
}: BankTransactionDetailModalProps) {
  if (!transaction) return null;

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'credit':
        return 'bg-green-500/10 text-green-500 border-green-500/30';
      case 'debit':
        return 'bg-red-500/10 text-red-500 border-red-500/30';
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/30';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'matched':
        return 'bg-green-500/10 text-green-500 border-green-500/30';
      case 'unmatched':
      case 'pending':
        return 'bg-orange-500/10 text-orange-500 border-orange-500/30';
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/30';
    }
  };

  const fields = [
    {
      label: 'Data',
      value: transaction.date ? formatDate(transaction.date) : '-',
    },
    {
      label: 'Descricao',
      value: transaction.description || '-',
    },
    {
      label: 'Valor',
      value: formatCurrency(Math.abs(transaction.amount || 0)),
      className: transaction.transaction_type === 'credit' ? 'text-green-500' : 'text-red-500',
    },
    {
      label: 'Tipo',
      value: transaction.transaction_type === 'credit' ? 'Credito' : 'Debito',
      badge: true,
      badgeColor: getTypeColor(transaction.transaction_type),
    },
    {
      label: 'Banco',
      value: transaction.bank_name || transaction.bank_account_name || '-',
    },
    {
      label: 'Status',
      value:
        transaction.match_status === 'matched'
          ? 'Conciliado'
          : 'Pendente',
      badge: true,
      badgeColor: getStatusColor(transaction.match_status || 'pending'),
    },
    {
      label: 'Referencia',
      value: transaction.reference || transaction.external_id || '-',
    },
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da Transacao"
      description="Informações completas da transacao bancaria"
      size="md"
    >
      <div className="space-y-4">
        {/* Valor em destaque */}
        <div className="bg-[hsl(var(--muted))] rounded-lg p-4 text-center">
          <p className="text-sm text-[hsl(var(--muted-foreground))] mb-1">Valor</p>
          <p
            className={cn(
              'text-3xl font-bold',
              transaction.transaction_type === 'credit'
                ? 'text-green-500'
                : 'text-red-500'
            )}
          >
            {transaction.transaction_type === 'credit' ? '+' : '-'}
            {formatCurrency(Math.abs(transaction.amount || 0))}
          </p>
        </div>

        {/* Campos */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {fields.map((field) => (
            <div key={field.label}>
              <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">
                {field.label}
              </p>
              {field.badge ? (
                <span
                  className={cn(
                    'inline-flex px-2 py-1 text-xs font-medium rounded-full border',
                    field.badgeColor
                  )}
                >
                  {field.value}
                </span>
              ) : (
                <p
                  className={cn(
                    'text-sm font-medium text-[hsl(var(--foreground))]',
                    field.className
                  )}
                >
                  {field.value}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-4 border-t border-[hsl(var(--border))]">
          <Button variant="outline" onClick={onClose}>
            Fechar
          </Button>
        </div>
      </div>
    </Modal>
  );
}
