'use client';

import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface PayableDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  payable: any;
}

const formatCurrency = (value: number | null | undefined) =>
  (value || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

const formatDate = (date: string | null | undefined) => {
  if (!date) return '-';
  try {
    return new Date(date).toLocaleDateString('pt-BR');
  } catch {
    return date;
  }
};

const getStatusBadge = (status?: string | null) => {
  switch (status) {
    case 'pending':
      return <Badge className="bg-yellow-100 text-yellow-800">Pendente</Badge>;
    case 'overdue':
      return <Badge className="bg-red-100 text-red-800">Atrasada</Badge>;
    case 'paid':
      return <Badge className="bg-green-100 text-green-800">Paga</Badge>;
    case 'cancelled':
      return <Badge variant="secondary">Cancelada</Badge>;
    default:
      return <Badge variant="outline">{status || '-'}</Badge>;
  }
};

const CATEGORY_LABELS: Record<string, string> = {
  utilities: 'Utilidades',
  rent: 'Aluguel',
  payroll: 'Folha de Pagamento',
  supplies: 'Suprimentos',
  services: 'Servicos',
  taxes: 'Impostos',
  other: 'Outros',
};

export function PayableDetailModal({ isOpen, onClose, payable }: PayableDetailModalProps) {
  if (!payable) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da Conta a Pagar"
      size="lg"
    >
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Descricao</p>
            <p className="font-medium">{payable.description || '-'}</p>
          </div>
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Fornecedor</p>
            <p className="font-medium">{payable.supplier_name || '-'}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Valor</p>
            <p className="text-xl font-bold font-mono">{formatCurrency(payable.amount)}</p>
          </div>
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Vencimento</p>
            <p className="font-medium">{formatDate(payable.due_date)}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Status</p>
            <div className="mt-1">{getStatusBadge(payable.status)}</div>
          </div>
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Categoria</p>
            <p className="font-medium">
              {payable.category ? CATEGORY_LABELS[payable.category] || payable.category : '-'}
            </p>
          </div>
        </div>

        {payable.paid_at && (
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Pago em</p>
            <p className="font-medium">{formatDate(payable.paid_at)}</p>
          </div>
        )}

        {payable.observacoes && (
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Observacoes</p>
            <p className="font-medium whitespace-pre-wrap">{payable.observacoes}</p>
          </div>
        )}
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Fechar
        </Button>
      </ModalFooter>
    </Modal>
  );
}
