'use client';

import { Modal } from '@/components/ui/modal';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';

interface ConnectorDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  connector: any;
}

export function ConnectorDetailModal({
  isOpen,
  onClose,
  connector,
}: ConnectorDetailModalProps) {
  if (!connector) return null;

  const getStatusBadge = (status: string) => {
    const map: Record<string, string> = {
      healthy: 'bg-green-100 text-green-800',
      degraded: 'bg-yellow-100 text-yellow-800',
      offline: 'bg-red-100 text-red-800',
    };
    const labels: Record<string, string> = {
      healthy: 'Saudavel',
      degraded: 'Degradado',
      offline: 'Offline',
    };
    return (
      <Badge className={map[status] || 'bg-gray-100 text-gray-800'}>
        {labels[status] || status}
      </Badge>
    );
  };

  const formatDateTime = (dateStr: string | null | undefined) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Conector"
      description={connector.name}
      size="md"
    >
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label className="text-muted-foreground text-xs">Nome</Label>
            <p className="text-sm font-medium">{connector.name}</p>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Tipo</Label>
            <p className="text-sm">{connector.type || '-'}</p>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Status</Label>
            <div className="mt-1">{getStatusBadge(connector.status)}</div>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Versao</Label>
            <p className="text-sm font-mono">{connector.version || '-'}</p>
          </div>
        </div>

        <div>
          <Label className="text-muted-foreground text-xs">Descricao</Label>
          <p className="text-sm mt-1">
            {connector.description || 'Sem descricao disponivel.'}
          </p>
        </div>

        <div className="border-t pt-4">
          <Label className="text-muted-foreground text-xs">
            Ultima verificacao
          </Label>
          <p className="text-sm mt-1">
            {formatDateTime(connector.last_health_check || connector.updated_at)}
          </p>
        </div>
      </div>
    </Modal>
  );
}
