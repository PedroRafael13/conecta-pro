'use client';

import { Landmark, FileText, CheckCircle, XCircle, Clock } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
;

interface NFeDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  nfe: any;
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
  draft: 'Rascunho',
  authorized: 'Autorizada',
  cancelled: 'Cancelada',
  rejected: 'Rejeitada',
  pending: 'Pendente',
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'draft':
      return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    case 'authorized':
      return 'bg-green-500/10 text-green-500 border-green-500/20';
    case 'cancelled':
      return 'bg-red-500/10 text-red-500 border-red-500/20';
    case 'rejected':
      return 'bg-orange-500/10 text-orange-500 border-orange-500/20';
    case 'pending':
      return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
    default:
      return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
  }
};

const StatusIcon = ({ status }: { status: string }) => {
  switch (status) {
    case 'authorized':
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    case 'cancelled':
    case 'rejected':
      return <XCircle className="w-5 h-5 text-red-500" />;
    default:
      return <Clock className="w-5 h-5 text-yellow-500" />;
  }
};

export function NFeDetailModal({ isOpen, onClose, nfe }: NFeDetailModalProps) {
  if (!nfe) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da Nota Fiscal"
      size="lg"
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-indigo-500/10 flex items-center justify-center">
            <FileText className="w-6 h-6 text-indigo-500" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-[hsl(var(--foreground))]">
              {nfe.tipo === 'nfse' ? 'NFS-e' : 'NF-e'} {nfe.number ? `#${nfe.number}` : ''}
            </h3>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              {nfe.description || 'Sem descricao'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <StatusIcon status={nfe.status} />
            <Badge className={getStatusColor(nfe.status)}>
              {STATUS_LABELS[nfe.status] || nfe.status}
            </Badge>
          </div>
        </div>

        {/* Details grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Numero</p>
            <p className="text-sm font-medium text-[hsl(var(--foreground))]">
              {nfe.number || '-'}
            </p>
          </div>

          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Serie</p>
            <p className="text-sm font-medium text-[hsl(var(--foreground))]">
              {nfe.series || '-'}
            </p>
          </div>

          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Tipo</p>
            <p className="text-sm font-medium text-[hsl(var(--foreground))]">
              {nfe.tipo === 'nfse' ? 'NFS-e (Servico)' : 'NF-e (Produto)'}
            </p>
          </div>

          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Valor</p>
            <p className="text-sm font-bold text-green-500">
              {formatCurrency(nfe.amount || nfe.total_amount)}
            </p>
          </div>

          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Destinatario</p>
            <p className="text-sm font-medium text-[hsl(var(--foreground))]">
              {nfe.recipient_name || '-'}
            </p>
          </div>

          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">CNPJ/CPF</p>
            <p className="text-sm font-medium text-[hsl(var(--foreground))]">
              {nfe.recipient_document || '-'}
            </p>
          </div>

          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Data de Emissao</p>
            <p className="text-sm font-medium text-[hsl(var(--foreground))]">
              {formatDate(nfe.issue_date || nfe.created_at)}
            </p>
          </div>

          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Status</p>
            <Badge className={getStatusColor(nfe.status)}>
              {STATUS_LABELS[nfe.status] || nfe.status}
            </Badge>
          </div>

          {nfe.access_key && (
            <div className="col-span-2 bg-[hsl(var(--muted))]/50 rounded-lg p-3">
              <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Chave de Acesso</p>
              <p className="text-sm font-mono text-[hsl(var(--foreground))] break-all">
                {nfe.access_key}
              </p>
            </div>
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
