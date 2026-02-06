'use client';

import { Modal } from '@/components/ui/modal';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';

interface WebhookDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  webhook: any;
}

export function WebhookDetailModal({
  isOpen,
  onClose,
  webhook,
}: WebhookDetailModalProps) {
  if (!webhook) return null;

  const getStatusBadge = (status: string) => {
    const map: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      error: 'bg-red-100 text-red-800',
    };
    const labels: Record<string, string> = {
      active: 'Ativo',
      inactive: 'Inativo',
      error: 'Erro',
    };
    return <Badge className={map[status] || 'bg-gray-100 text-gray-800'}>{labels[status] || status}</Badge>;
  };

  const maskSecret = (secret: string | null | undefined) => {
    if (!secret) return '-';
    if (secret.length <= 8) return '********';
    return secret.substring(0, 4) + '****' + secret.substring(secret.length - 4);
  };

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('pt-BR');
  };

  const formatHeaders = (headers: any) => {
    if (!headers) return '-';
    if (typeof headers === 'string') return headers;
    return JSON.stringify(headers, null, 2);
  };

  const events = Array.isArray(webhook.events)
    ? webhook.events
    : typeof webhook.events === 'string'
      ? webhook.events.split(',').map((e: string) => e.trim())
      : [];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={webhook.name}
      description="Detalhes do webhook"
      size="lg"
    >
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label className="text-muted-foreground text-xs">Nome</Label>
            <p className="text-sm font-medium">{webhook.name}</p>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Status</Label>
            <div className="mt-1">
              {getStatusBadge(webhook.status)}
            </div>
          </div>
        </div>

        <div>
          <Label className="text-muted-foreground text-xs">URL</Label>
          <p className="text-sm font-mono break-all">{webhook.url}</p>
        </div>

        <div>
          <Label className="text-muted-foreground text-xs">Eventos</Label>
          <div className="flex flex-wrap gap-1.5 mt-1">
            {events.length > 0 ? (
              events.map((event: string, idx: number) => (
                <Badge key={idx} variant="outline" className="font-mono text-xs">
                  {event}
                </Badge>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">Nenhum evento configurado</p>
            )}
          </div>
        </div>

        <div>
          <Label className="text-muted-foreground text-xs">Secret</Label>
          <p className="text-sm font-mono">{maskSecret(webhook.secret)}</p>
        </div>

        <div>
          <Label className="text-muted-foreground text-xs">Headers</Label>
          {webhook.headers ? (
            <pre className="text-xs font-mono bg-muted/50 rounded-md p-3 mt-1 overflow-x-auto">
              {formatHeaders(webhook.headers)}
            </pre>
          ) : (
            <p className="text-sm text-muted-foreground">Nenhum header customizado</p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4 pt-2 border-t">
          <div>
            <Label className="text-muted-foreground text-xs">Ultimo disparo</Label>
            <p className="text-sm">{formatDate(webhook.last_triggered_at)}</p>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Criado em</Label>
            <p className="text-sm">{formatDate(webhook.created_at)}</p>
          </div>
        </div>
      </div>
    </Modal>
  );
}
