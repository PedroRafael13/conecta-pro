'use client';

import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface ReceivableDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  receivable: any;
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
      return <Badge className="bg-green-100 text-green-800">Recebida</Badge>;
    case 'cancelled':
      return <Badge variant="secondary">Cancelada</Badge>;
    default:
      return <Badge variant="outline">{status || '-'}</Badge>;
  }
};

const CATEGORY_LABELS: Record<string, string> = {
  service: 'Servico',
  product: 'Produto',
  subscription: 'Assinatura',
  rental: 'Aluguel',
  other: 'Outros',
};

export function ReceivableDetailModal({ isOpen, onClose, receivable }: ReceivableDetailModalProps) {
  if (!receivable) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da Conta a Receber"
      size="lg"
    >
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Descricao</p>
            <p className="font-medium">{receivable.description || '-'}</p>
          </div>
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Cliente</p>
            <p className="font-medium">{receivable.customer_name || '-'}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Valor</p>
            <p className="text-xl font-bold font-mono">{formatCurrency(receivable.amount)}</p>
          </div>
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Vencimento</p>
            <p className="font-medium">{formatDate(receivable.due_date)}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Status</p>
            <div className="mt-1">{getStatusBadge(receivable.status)}</div>
          </div>
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Categoria</p>
            <p className="font-medium">
              {receivable.category ? CATEGORY_LABELS[receivable.category] || receivable.category : '-'}
            </p>
          </div>
        </div>

        {receivable.paid_at && (
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Recebido em</p>
            <p className="font-medium">{formatDate(receivable.paid_at)}</p>
          </div>
        )}

        {receivable.observacoes && (
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Observacoes</p>
            <p className="font-medium whitespace-pre-wrap">{receivable.observacoes}</p>
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
