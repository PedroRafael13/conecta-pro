'use client';

import { Modal } from '@/components/ui/modal';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';

interface OrdemDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  ordem: any | null;
}

const prioridadeConfig: Record<string, { label: string; className: string }> = {
  baixa: { label: 'Baixa', className: 'bg-gray-100 text-gray-800' },
  media: { label: 'Media', className: 'bg-blue-100 text-blue-800' },
  alta: { label: 'Alta', className: 'bg-orange-100 text-orange-800' },
  urgente: { label: 'Urgente', className: 'bg-red-100 text-red-800' },
};

const statusConfig: Record<string, { label: string; className: string }> = {
  aberta: { label: 'Aberta', className: 'bg-blue-100 text-blue-800' },
  em_andamento: { label: 'Em Andamento', className: 'bg-yellow-100 text-yellow-800' },
  concluida: { label: 'Concluida', className: 'bg-green-100 text-green-800' },
  cancelada: { label: 'Cancelada', className: 'bg-red-100 text-red-800' },
};

const tipoConfig: Record<string, string> = {
  corretiva: 'Corretiva',
  preventiva: 'Preventiva',
  instalacao: 'Instalacao',
};

function formatDate(dateStr: string): string {
  if (!dateStr) return '-';
  try {
    return new Date(dateStr).toLocaleDateString('pt-BR');
  } catch {
    return dateStr;
  }
}

export function OrdemDetailModal({
  isOpen,
  onClose,
  ordem,
}: OrdemDetailModalProps) {
  if (!ordem) return null;

  const prioridade = prioridadeConfig[ordem.prioridade] || { label: ordem.prioridade, className: 'bg-gray-100 text-gray-800' };
  const status = statusConfig[ordem.status] || { label: ordem.status, className: 'bg-gray-100 text-gray-800' };
  const tipo = tipoConfig[ordem.tipo] || ordem.tipo || '-';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={ordem.titulo || 'Detalhes da Ordem de Servico'}
      size="lg"
    >
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label className="text-muted-foreground text-xs">Titulo</Label>
            <p className="text-sm font-medium">{ordem.titulo || '-'}</p>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Cliente</Label>
            <p className="text-sm">{ordem.cliente || '-'}</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <Label className="text-muted-foreground text-xs">Prioridade</Label>
            <div className="mt-1">
              <Badge className={prioridade.className}>{prioridade.label}</Badge>
            </div>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Status</Label>
            <div className="mt-1">
              <Badge className={status.className}>{status.label}</Badge>
            </div>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Tipo</Label>
            <div className="mt-1">
              <Badge className="bg-indigo-100 text-indigo-800">{tipo}</Badge>
            </div>
          </div>
        </div>

        <div>
          <Label className="text-muted-foreground text-xs">Data Prevista</Label>
          <p className="text-sm">{formatDate(ordem.data_prevista)}</p>
        </div>

        {ordem.descricao && (
          <div>
            <Label className="text-muted-foreground text-xs">Descricao</Label>
            <p className="text-sm mt-1 whitespace-pre-wrap">{ordem.descricao}</p>
          </div>
        )}

        {ordem.created_at && (
          <div className="border-t pt-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-muted-foreground text-xs">Criado em</Label>
                <p className="text-sm">{formatDate(ordem.created_at)}</p>
              </div>
              {ordem.updated_at && (
                <div>
                  <Label className="text-muted-foreground text-xs">Atualizado em</Label>
                  <p className="text-sm">{formatDate(ordem.updated_at)}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}
