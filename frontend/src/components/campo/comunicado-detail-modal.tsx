'use client';

import { Bell, Calendar, Users, FileText, Tag } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
;

interface ComunicadoDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  comunicado: any;
}

export function ComunicadoDetailModal({ isOpen, onClose, comunicado }: ComunicadoDetailModalProps) {
  if (!comunicado) return null;

  const getTipoBadge = (tipo: string) => {
    const tipoMap: Record<string, { label: string; className: string }> = {
      informativo: { label: 'Informativo', className: 'bg-blue-100 text-blue-800' },
      urgente: { label: 'Urgente', className: 'bg-red-100 text-red-800' },
      operacional: { label: 'Operacional', className: 'bg-violet-100 text-violet-800' },
    };
    const config = tipoMap[tipo] || { label: tipo || '-', className: 'bg-gray-100 text-gray-800' };
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; className: string }> = {
      enviado: { label: 'Enviado', className: 'bg-green-100 text-green-800' },
      pendente: { label: 'Pendente', className: 'bg-yellow-100 text-yellow-800' },
      rascunho: { label: 'Rascunho', className: 'bg-gray-100 text-gray-800' },
      agendado: { label: 'Agendado', className: 'bg-blue-100 text-blue-800' },
    };
    const config = statusMap[status] || { label: status || 'Pendente', className: 'bg-gray-100 text-gray-800' };
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  const formatDate = (date: string | null | undefined) => {
    if (!date) return '-';
    return new Date(date).toLocaleDateString('pt-BR');
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Comunicado"
      description="Informações completas do comunicado"
      size="lg"
    >
      <div className="grid grid-cols-2 gap-6">
        <div className="col-span-2 space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <Bell className="w-3 h-3" />
            Titulo
          </Label>
          <p className="text-base font-semibold text-[hsl(var(--foreground))]">
            {comunicado.titulo || '-'}
          </p>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <Tag className="w-3 h-3" />
            Tipo
          </Label>
          <div className="mt-1">
            {getTipoBadge(comunicado.tipo)}
          </div>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs">Status</Label>
          <div className="mt-1">
            {getStatusBadge(comunicado.status)}
          </div>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            Data de Envio
          </Label>
          <p className="text-sm text-[hsl(var(--foreground))]">
            {formatDate(comunicado.data_envio)}
          </p>
        </div>

        <div className="space-y-1">
          <Label className="text-muted-foreground text-xs flex items-center gap-1">
            <Users className="w-3 h-3" />
            Destinatarios
          </Label>
          <p className="text-sm text-[hsl(var(--foreground))]">
            {comunicado.destinatarios || '-'}
          </p>
        </div>
      </div>

      {/* Mensagem */}
      <div className="mt-6 space-y-1">
        <Label className="text-muted-foreground text-xs flex items-center gap-1">
          <FileText className="w-3 h-3" />
          Mensagem
        </Label>
        <div className="p-4 rounded-lg bg-[hsl(var(--muted))]/30 border border-[hsl(var(--border))]">
          <p className="text-sm text-[hsl(var(--foreground))] whitespace-pre-wrap">
            {comunicado.mensagem || 'Sem conteudo.'}
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
