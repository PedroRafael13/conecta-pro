'use client';

import { Modal } from '@/components/ui/modal';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';

interface AgendamentoDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  agendamento: any | null;
}

const tipoConfig: Record<string, { label: string; className: string }> = {
  visita: { label: 'Visita', className: 'bg-blue-100 text-blue-800' },
  manutencao: { label: 'Manutencao', className: 'bg-orange-100 text-orange-800' },
  instalacao: { label: 'Instalacao', className: 'bg-purple-100 text-purple-800' },
  auditoria: { label: 'Auditoria', className: 'bg-cyan-100 text-cyan-800' },
};

const statusConfig: Record<string, { label: string; className: string }> = {
  agendado: { label: 'Agendado', className: 'bg-blue-100 text-blue-800' },
  confirmado: { label: 'Confirmado', className: 'bg-green-100 text-green-800' },
  em_andamento: { label: 'Em Andamento', className: 'bg-yellow-100 text-yellow-800' },
  concluido: { label: 'Concluido', className: 'bg-green-100 text-green-800' },
  cancelado: { label: 'Cancelado', className: 'bg-red-100 text-red-800' },
};

function formatDate(dateStr: string): string {
  if (!dateStr) return '-';
  try {
    return new Date(dateStr).toLocaleDateString('pt-BR');
  } catch {
    return dateStr;
  }
}

export function AgendamentoDetailModal({
  isOpen,
  onClose,
  agendamento,
}: AgendamentoDetailModalProps) {
  if (!agendamento) return null;

  const tipo = tipoConfig[agendamento.tipo] || { label: agendamento.tipo, className: 'bg-gray-100 text-gray-800' };
  const status = statusConfig[agendamento.status] || { label: agendamento.status, className: 'bg-gray-100 text-gray-800' };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={agendamento.titulo || 'Detalhes do Agendamento'}
      size="lg"
    >
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label className="text-muted-foreground text-xs">Titulo</Label>
            <p className="text-sm font-medium">{agendamento.titulo || '-'}</p>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Responsavel</Label>
            <p className="text-sm">{agendamento.responsavel || '-'}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label className="text-muted-foreground text-xs">Tipo</Label>
            <div className="mt-1">
              <Badge className={tipo.className}>{tipo.label}</Badge>
            </div>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Status</Label>
            <div className="mt-1">
              <Badge className={status.className}>{status.label}</Badge>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <Label className="text-muted-foreground text-xs">Data</Label>
            <p className="text-sm">{formatDate(agendamento.data)}</p>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Hora Inicio</Label>
            <p className="text-sm">{agendamento.hora_inicio || '-'}</p>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Hora Fim</Label>
            <p className="text-sm">{agendamento.hora_fim || '-'}</p>
          </div>
        </div>

        {agendamento.descricao && (
          <div>
            <Label className="text-muted-foreground text-xs">Descricao</Label>
            <p className="text-sm mt-1 whitespace-pre-wrap">{agendamento.descricao}</p>
          </div>
        )}

        {agendamento.created_at && (
          <div className="border-t pt-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-muted-foreground text-xs">Criado em</Label>
                <p className="text-sm">{formatDate(agendamento.created_at)}</p>
              </div>
              {agendamento.updated_at && (
                <div>
                  <Label className="text-muted-foreground text-xs">Atualizado em</Label>
                  <p className="text-sm">{formatDate(agendamento.updated_at)}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}
