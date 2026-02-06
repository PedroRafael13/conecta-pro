'use client';

import { Monitor, MapPin, Clock, User, FileText, Activity } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
;

interface MonitoramentoDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  evento: any;
}

export function MonitoramentoDetailModal({ isOpen, onClose, evento }: MonitoramentoDetailModalProps) {
  if (!evento) return null;

  const formatDateTime = (date: string | null | undefined) => {
    if (!date) return '-';
    return new Date(date).toLocaleString('pt-BR');
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; className: string }> = {
      online: { label: 'Online', className: 'bg-green-100 text-green-800' },
      offline: { label: 'Offline', className: 'bg-red-100 text-red-800' },
      alerta: { label: 'Alerta', className: 'bg-yellow-100 text-yellow-800' },
      normal: { label: 'Normal', className: 'bg-green-100 text-green-800' },
      critico: { label: 'Critico', className: 'bg-red-100 text-red-800' },
    };
    const config = statusMap[status] || { label: status || 'Desconhecido', className: 'bg-gray-100 text-gray-800' };
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  const getTipoEventoBadge = (tipo: string) => {
    const tipoMap: Record<string, { label: string; className: string }> = {
      checkin: { label: 'Check-in', className: 'bg-cyan-100 text-cyan-800' },
      checkout: { label: 'Check-out', className: 'bg-blue-100 text-blue-800' },
      alerta: { label: 'Alerta', className: 'bg-yellow-100 text-yellow-800' },
      ocorrencia: { label: 'Ocorrencia', className: 'bg-orange-100 text-orange-800' },
      ronda: { label: 'Ronda', className: 'bg-violet-100 text-violet-800' },
      panico: { label: 'Panico', className: 'bg-red-100 text-red-800' },
    };
    const config = tipoMap[tipo] || { label: tipo || '-', className: 'bg-gray-100 text-gray-800' };
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Evento"
      description="Informacoes do evento de monitoramento"
      size="lg"
    >
      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <User className="w-3 h-3" />
            Agente
          </Label>
          <p className="text-sm font-medium text-[hsl(var(--foreground))]">
            {evento.agente || evento.nome || evento.tecnico || '-'}
          </p>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <Activity className="w-3 h-3" />
            Tipo de Evento
          </Label>
          <div className="mt-1">
            {getTipoEventoBadge(evento.tipo_evento || evento.tipo)}
          </div>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Data / Hora
          </Label>
          <p className="text-sm text-[hsl(var(--foreground))]">
            {formatDateTime(evento.data || evento.created_at || evento.timestamp)}
          </p>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            Localizacao
          </Label>
          <p className="text-sm text-[hsl(var(--foreground))]">
            {evento.localizacao || evento.local ||
              (evento.latitude ? `${evento.latitude}, ${evento.longitude}` : '-')}
          </p>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <Monitor className="w-3 h-3" />
            Status
          </Label>
          <div className="mt-1">
            {getStatusBadge(evento.status)}
          </div>
        </div>
      </div>

      {/* Descricao */}
      <div className="mt-6 space-y-1">
        <Label className="text-muted-foreground text-xs flex items-center gap-1">
          <FileText className="w-3 h-3" />
          Descricao
        </Label>
        <div className="p-3 rounded-lg bg-[hsl(var(--muted))]/30 border border-[hsl(var(--border))]">
          <p className="text-sm text-[hsl(var(--foreground))]">
            {evento.descricao || evento.description || 'Sem descricao disponivel.'}
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
