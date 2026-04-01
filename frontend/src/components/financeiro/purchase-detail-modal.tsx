'use client';

import { ShoppingCart, ClipboardList, FileText } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
;

interface PurchaseDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  item: any;
  type: 'requisition' | 'order';
}

const formatCurrency = (value: number | undefined | null) => {
  if (value == null) return 'R$ 0,00';
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatDate = (date: string | undefined | null) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('pt-BR');
};

const STATUS_LABELS: Record<string, string> = {
  pending: 'Pendente',
  approved: 'Aprovada',
  rejected: 'Rejeitada',
  in_progress: 'Em Andamento',
  completed: 'Concluida',
  draft: 'Rascunho',
  sent: 'Enviada',
  confirmed: 'Confirmada',
  delivered: 'Entregue',
  cancelled: 'Cancelada',
};

const URGENCY_LABELS: Record<string, string> = {
  low: 'Baixa',
  medium: 'Media',
  high: 'Alta',
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'pending':
    case 'draft':
      return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
    case 'approved':
    case 'confirmed':
    case 'delivered':
    case 'completed':
      return 'bg-green-500/10 text-green-500 border-green-500/20';
    case 'rejected':
    case 'cancelled':
      return 'bg-red-500/10 text-red-500 border-red-500/20';
    case 'in_progress':
    case 'sent':
      return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
    default:
      return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
  }
};

const getUrgencyColor = (urgency: string) => {
  switch (urgency) {
    case 'low':
      return 'bg-green-500/10 text-green-500 border-green-500/20';
    case 'medium':
      return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
    case 'high':
      return 'bg-red-500/10 text-red-500 border-red-500/20';
    default:
      return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
  }
};

export function PurchaseDetailModal({ isOpen, onClose, item, type }: PurchaseDetailModalProps) {
  if (!item) return null;

  const Icon = type === 'requisition' ? ClipboardList : FileText;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={type === 'requisition' ? 'Detalhes da Requisicao' : 'Detalhes da Ordem de Compra'}
      size="lg"
    >
      <div className="space-y-6">
        {/* Header info */}
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-orange-500/10 flex items-center justify-center">
            <Icon className="w-6 h-6 text-orange-500" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-[hsl(var(--foreground))]">
              {item.code || item.id?.slice(0, 8)}
            </h3>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              {item.description || 'Sem descricao'}
            </p>
          </div>
          <Badge className={getStatusColor(item.status)}>
            {STATUS_LABELS[item.status] || item.status}
          </Badge>
        </div>

        {/* Details grid */}
        <div className="grid grid-cols-2 gap-4">
          {type === 'requisition' ? (
            <>
              <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Solicitante</p>
                <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                  {item.requester || '-'}
                </p>
              </div>
              <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Departamento</p>
                <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                  {item.department || '-'}
                </p>
              </div>
              <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Urgencia</p>
                <Badge className={getUrgencyColor(item.urgency)}>
                  {URGENCY_LABELS[item.urgency] || item.urgency || '-'}
                </Badge>
              </div>
              <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Data de Criação</p>
                <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                  {formatDate(item.created_at)}
                </p>
              </div>
              {item.items_description && (
                <div className="col-span-2 bg-[hsl(var(--muted))]/50 rounded-lg p-3">
                  <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Itens Solicitados</p>
                  <p className="text-sm text-[hsl(var(--foreground))] whitespace-pre-wrap">
                    {item.items_description}
                  </p>
                </div>
              )}
            </>
          ) : (
            <>
              <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Fornecedor</p>
                <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                  {item.supplier_name || '-'}
                </p>
              </div>
              <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Valor Total</p>
                <p className="text-sm font-bold text-green-500">
                  {formatCurrency(item.total_amount)}
                </p>
              </div>
              <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Data de Entrega</p>
                <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                  {formatDate(item.delivery_date)}
                </p>
              </div>
              <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Condicoes de Pagamento</p>
                <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                  {item.payment_terms || '-'}
                </p>
              </div>
              <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Data de Criação</p>
                <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                  {formatDate(item.created_at)}
                </p>
              </div>
              <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Última Atualização</p>
                <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                  {formatDate(item.updated_at)}
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Fechar
        </Button>
      </ModalFooter>
    </Modal>
  );
}
