'use client';

import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { LogIn, MapPin, Clock, User, FileText } from 'lucide-react';

interface CheckinDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  checkin: any;
}

export function CheckinDetailModal({ isOpen, onClose, checkin }: CheckinDetailModalProps) {
  if (!checkin) return null;

  const formatDateTime = (date: string | null | undefined) => {
    if (!date) return '-';
    return new Date(date).toLocaleString('pt-BR');
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; className: string }> = {
      ativo: { label: 'Ativo', className: 'bg-green-100 text-green-800' },
      finalizado: { label: 'Finalizado', className: 'bg-blue-100 text-blue-800' },
      pendente: { label: 'Pendente', className: 'bg-yellow-100 text-yellow-800' },
    };
    const config = statusMap[status] || { label: status || 'Desconhecido', className: 'bg-gray-100 text-gray-800' };
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Check-in"
      description="Informacoes completas do registro"
      size="lg"
    >
      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <User className="w-3 h-3" />
            Colaborador
          </Label>
          <p className="text-sm font-medium text-[hsl(var(--foreground))]">
            {checkin.colaborador || checkin.nome || '-'}
          </p>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            Posto
          </Label>
          <p className="text-sm font-medium text-[hsl(var(--foreground))]">
            {checkin.posto || checkin.local || '-'}
          </p>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <LogIn className="w-3 h-3" />
            Data Check-in
          </Label>
          <p className="text-sm text-[hsl(var(--foreground))]">
            {formatDateTime(checkin.data_checkin || checkin.checkin_at)}
          </p>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Data Check-out
          </Label>
          <p className="text-sm text-[hsl(var(--foreground))]">
            {formatDateTime(checkin.data_checkout || checkin.checkout_at)}
          </p>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs">Status</Label>
          <div className="mt-1">
            {getStatusBadge(checkin.status)}
          </div>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            Localizacao
          </Label>
          <p className="text-sm text-[hsl(var(--foreground))]">
            {checkin.localizacao || checkin.latitude
              ? `${checkin.latitude ?? ''}, ${checkin.longitude ?? ''}`
              : '-'}
          </p>
        </div>
      </div>

      {/* Observacoes */}
      <div className="mt-6 space-y-1">
        <Label className="text-muted-foreground text-xs flex items-center gap-1">
          <FileText className="w-3 h-3" />
          Observacoes
        </Label>
        <div className="p-3 rounded-lg bg-[hsl(var(--muted))]/30 border border-[hsl(var(--border))]">
          <p className="text-sm text-[hsl(var(--foreground))]">
            {checkin.observacoes || checkin.observacao || 'Nenhuma observacao registrada.'}
          </p>
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
