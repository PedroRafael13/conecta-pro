'use client';

import { Modal } from '@/components/ui/modal';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';

interface OportunidadeDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  oportunidade: any | null;
}

const statusConfig: Record<string, { label: string; className: string }> = {
  novo: { label: 'Novo', className: 'bg-blue-100 text-blue-800' },
  qualificado: { label: 'Qualificado', className: 'bg-purple-100 text-purple-800' },
  proposta: { label: 'Proposta', className: 'bg-yellow-100 text-yellow-800' },
  negociacao: { label: 'Negociação', className: 'bg-orange-100 text-orange-800' },
  ganho: { label: 'Ganho', className: 'bg-green-100 text-green-800' },
  perdido: { label: 'Perdido', className: 'bg-red-100 text-red-800' },
};

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
}

export function OportunidadeDetailModal({
  isOpen,
  onClose,
  oportunidade,
}: OportunidadeDetailModalProps) {
  if (!oportunidade) return null;

  const status = statusConfig[oportunidade.status] || {
    label: oportunidade.status,
    className: 'bg-gray-100 text-gray-800',
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da Oportunidade"
      size="lg"
    >
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label className="text-muted-foreground text-xs">Nome</Label>
          <p className="text-sm font-medium">{oportunidade.nome}</p>
        </div>
        <div>
          <Label className="text-muted-foreground text-xs">Cliente</Label>
          <p className="text-sm">{oportunidade.cliente || '-'}</p>
        </div>
        <div>
          <Label className="text-muted-foreground text-xs">Valor Estimado</Label>
          <p className="text-sm font-semibold">
            {formatCurrency(oportunidade.valor_estimado || 0)}
          </p>
        </div>
        <div>
          <Label className="text-muted-foreground text-xs">Status</Label>
          <div className="mt-1">
            <Badge className={status.className}>{status.label}</Badge>
          </div>
        </div>
        <div>
          <Label className="text-muted-foreground text-xs">Responsável</Label>
          <p className="text-sm">{oportunidade.responsavel || '-'}</p>
        </div>
        <div>
          <Label className="text-muted-foreground text-xs">Criado em</Label>
          <p className="text-sm">
            {oportunidade.created_at
              ? new Date(oportunidade.created_at).toLocaleDateString('pt-BR')
              : '-'}
          </p>
        </div>
        <div className="col-span-2">
          <Label className="text-muted-foreground text-xs">Observações</Label>
          <p className="text-sm whitespace-pre-wrap">
            {oportunidade.observacoes || '-'}
          </p>
        </div>
      </div>
    </Modal>
  );
}
