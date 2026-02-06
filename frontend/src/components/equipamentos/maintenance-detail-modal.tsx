'use client';

import { Wrench, Calendar, User, FileText } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
;

// Status badges
const STATUS_CONFIG: Record<string, { className: string; label: string }> = {
  scheduled: { className: 'bg-blue-100 text-blue-800', label: 'Agendada' },
  in_progress: { className: 'bg-yellow-100 text-yellow-800', label: 'Em Andamento' },
  completed: { className: 'bg-green-100 text-green-800', label: 'Concluída' },
  cancelled: { className: 'bg-gray-100 text-gray-800', label: 'Cancelada' },
  waiting_parts: { className: 'bg-orange-100 text-orange-800', label: 'Aguard. Peças' },
};

// Type badges
const TYPE_CONFIG: Record<string, { className: string; label: string }> = {
  preventiva: { className: 'bg-blue-100 text-blue-800', label: 'Preventiva' },
  corretiva: { className: 'bg-orange-100 text-orange-800', label: 'Corretiva' },
  emergencial: { className: 'bg-red-100 text-red-800', label: 'Emergencial' },
};

// Priority badges
const PRIORITY_CONFIG: Record<string, { className: string; label: string }> = {
  low: { className: 'bg-gray-100 text-gray-800', label: 'Baixa' },
  medium: { className: 'bg-blue-100 text-blue-800', label: 'Média' },
  high: { className: 'bg-orange-100 text-orange-800', label: 'Alta' },
  critical: { className: 'bg-red-100 text-red-800', label: 'Crítica' },
};

interface MaintenanceDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  maintenance: any;
}

export function MaintenanceDetailModal({
  isOpen,
  onClose,
  maintenance,
}: MaintenanceDetailModalProps) {
  if (!maintenance) return null;

  const statusCfg = STATUS_CONFIG[maintenance.status] ?? { className: 'bg-gray-100 text-gray-800', label: maintenance.status };
  const typeCfg = TYPE_CONFIG[maintenance.maintenance_type] ?? { className: 'bg-gray-100 text-gray-800', label: maintenance.maintenance_type };
  const priorityCfg = PRIORITY_CONFIG[maintenance.priority] ?? { className: 'bg-gray-100 text-gray-800', label: maintenance.priority };

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da Manutenção"
      description={maintenance.codigo || maintenance.equipment_name}
      size="lg"
    >
      <div className="space-y-6">
        {/* Código e Badges */}
        <div className="flex items-center justify-between flex-wrap gap-2">
          {maintenance.codigo && (
            <span className="text-sm font-mono text-[hsl(var(--muted-foreground))]">
              {maintenance.codigo}
            </span>
          )}
          <div className="flex items-center gap-2">
            <Badge className={typeCfg.className}>{typeCfg.label}</Badge>
            <Badge className={statusCfg.className}>{statusCfg.label}</Badge>
            <Badge className={priorityCfg.className}>{priorityCfg.label}</Badge>
          </div>
        </div>

        {/* Equipamento */}
        <div className="border border-[hsl(var(--border))] rounded-lg p-4 space-y-3">
          <h3 className="font-medium flex items-center gap-2 text-sm">
            <Wrench className="w-4 h-4" />
            Equipamento
          </h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-[hsl(var(--muted-foreground))]">Nome:</span>
              <p className="font-medium">{maintenance.equipment_name || '-'}</p>
            </div>
            <div>
              <span className="text-[hsl(var(--muted-foreground))]">Tipo:</span>
              <p className="font-medium">
                <Badge className={typeCfg.className}>{typeCfg.label}</Badge>
              </p>
            </div>
          </div>
        </div>

        {/* Técnico e Data */}
        <div className="border border-[hsl(var(--border))] rounded-lg p-4 space-y-3">
          <h3 className="font-medium flex items-center gap-2 text-sm">
            <User className="w-4 h-4" />
            Responsável e Agenda
          </h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-[hsl(var(--muted-foreground))]">Técnico:</span>
              <p className="font-medium">{maintenance.technician_name || '-'}</p>
            </div>
            <div>
              <span className="text-[hsl(var(--muted-foreground))]">Data Agendada:</span>
              <p className="font-medium">{formatDate(maintenance.scheduled_date)}</p>
            </div>
            <div>
              <span className="text-[hsl(var(--muted-foreground))]">Status:</span>
              <p className="font-medium">
                <Badge className={statusCfg.className}>{statusCfg.label}</Badge>
              </p>
            </div>
            <div>
              <span className="text-[hsl(var(--muted-foreground))]">Prioridade:</span>
              <p className="font-medium">
                <Badge className={priorityCfg.className}>{priorityCfg.label}</Badge>
              </p>
            </div>
          </div>
        </div>

        {/* Descrição */}
        {maintenance.description && (
          <div className="border border-[hsl(var(--border))] rounded-lg p-4 space-y-3">
            <h3 className="font-medium flex items-center gap-2 text-sm">
              <FileText className="w-4 h-4" />
              Descrição
            </h3>
            <p className="text-sm p-3 bg-[hsl(var(--muted))] rounded-lg whitespace-pre-wrap">
              {maintenance.description}
            </p>
          </div>
        )}

        {/* Observações */}
        {maintenance.observacoes && (
          <div className="border border-[hsl(var(--border))] rounded-lg p-4 space-y-3">
            <h3 className="font-medium flex items-center gap-2 text-sm">
              <Calendar className="w-4 h-4" />
              Observações
            </h3>
            <p className="text-sm p-3 bg-[hsl(var(--muted))] rounded-lg whitespace-pre-wrap">
              {maintenance.observacoes}
            </p>
          </div>
        )}

        <ModalFooter>
          <Button variant="outline" onClick={onClose}>
            Fechar
          </Button>
        </ModalFooter>
      </div>
    </Modal>
  );
}
