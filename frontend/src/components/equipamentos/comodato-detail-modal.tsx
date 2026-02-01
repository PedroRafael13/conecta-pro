'use client';

import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar, User, Package, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ComodatoDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  comodato: any;
}

const statusConfig: Record<string, { label: string; className: string }> = {
  draft: { label: 'Rascunho', className: 'bg-gray-100 text-gray-800' },
  pending_signature: { label: 'Aguard. Assinatura', className: 'bg-yellow-100 text-yellow-800' },
  active: { label: 'Ativo', className: 'bg-green-100 text-green-800' },
  pending_return: { label: 'Aguard. Devolucao', className: 'bg-orange-100 text-orange-800' },
  terminated: { label: 'Encerrado', className: 'bg-red-100 text-red-800' },
  expired: { label: 'Expirado', className: 'bg-gray-100 text-gray-800' },
};

export function ComodatoDetailModal({
  isOpen,
  onClose,
  comodato,
}: ComodatoDetailModalProps) {
  if (!comodato) return null;

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

  const status = statusConfig[comodato.status] ?? statusConfig.draft;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Comodato"
      description={comodato.codigo}
      size="lg"
    >
      <div className="space-y-6">
        {/* Status */}
        <div className="flex items-start justify-between">
          <Badge className={cn('border-0', status.className)}>
            {status.label}
          </Badge>
          <span className="text-xs text-[hsl(var(--muted-foreground))]">
            ID: {comodato.id}
          </span>
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
              <FileText className="w-4 h-4" />
              Codigo
            </div>
            <p className="text-[hsl(var(--foreground))] font-medium mt-2">
              {comodato.codigo ?? '-'}
            </p>
          </div>

          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
              <User className="w-4 h-4" />
              Cliente
            </div>
            <p className="text-[hsl(var(--foreground))] font-medium mt-2">
              {comodato.client_name ?? '-'}
            </p>
          </div>

          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
              <Package className="w-4 h-4" />
              Equipamento
            </div>
            <p className="text-[hsl(var(--foreground))] font-medium mt-2">
              {comodato.equipment_name ?? '-'}
            </p>
          </div>

          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
              <Calendar className="w-4 h-4" />
              Vigencia
            </div>
            <p className="text-[hsl(var(--foreground))] font-medium mt-2">
              {formatDate(comodato.start_date)} - {formatDate(comodato.end_date)}
            </p>
          </div>
        </div>

        {/* Terms */}
        {comodato.terms && (
          <div>
            <h3 className="text-sm font-medium text-[hsl(var(--foreground))] mb-2">
              Termos do Contrato
            </h3>
            <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3 text-sm text-[hsl(var(--foreground))] whitespace-pre-wrap">
              {comodato.terms}
            </div>
          </div>
        )}

        {/* Observacoes */}
        {comodato.observacoes && (
          <div>
            <h3 className="text-sm font-medium text-[hsl(var(--foreground))] mb-2">
              Observacoes
            </h3>
            <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3 text-sm text-[hsl(var(--foreground))] whitespace-pre-wrap">
              {comodato.observacoes}
            </div>
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
