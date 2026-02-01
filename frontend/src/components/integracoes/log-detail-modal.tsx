'use client';

import { Modal } from '@/components/ui/modal';
import { Badge } from '@/components/ui/badge';

interface LogDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  log: any;
}

const LEVEL_BADGES: Record<string, string> = {
  info: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  warning: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  error: 'bg-red-500/10 text-red-500 border-red-500/20',
  debug: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
};

const STATUS_BADGES: Record<string, string> = {
  success: 'bg-green-500/10 text-green-500 border-green-500/20',
  failure: 'bg-red-500/10 text-red-500 border-red-500/20',
};

const LEVEL_LABELS: Record<string, string> = {
  info: 'Info',
  warning: 'Warning',
  error: 'Erro',
  debug: 'Debug',
};

const STATUS_LABELS: Record<string, string> = {
  success: 'Sucesso',
  failure: 'Falha',
};

function formatDetailsJson(details: any): string {
  if (!details) return '';
  if (typeof details === 'string') {
    try {
      return JSON.stringify(JSON.parse(details), null, 2);
    } catch {
      return details;
    }
  }
  return JSON.stringify(details, null, 2);
}

function formatTimestamp(ts: string): string {
  if (!ts) return '-';
  return new Date(ts).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

export function LogDetailModal({ isOpen, onClose, log }: LogDetailModalProps) {
  if (!log) return null;

  const hasDetails = log.details && (typeof log.details === 'object' ? Object.keys(log.details).length > 0 : log.details.length > 0);
  const hasStackTrace = log.stack_trace || log.stacktrace || log.traceback;
  const stackTrace = log.stack_trace || log.stacktrace || log.traceback;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Log"
      size="lg"
    >
      <div className="space-y-6">
        {/* Grid de informações básicas */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
              ID
            </label>
            <p className="mt-1 text-sm font-mono text-[hsl(var(--foreground))]">
              {log.id}
            </p>
          </div>

          <div>
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
              Timestamp
            </label>
            <p className="mt-1 text-sm text-[hsl(var(--foreground))]">
              {formatTimestamp(log.timestamp)}
            </p>
          </div>

          <div>
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
              Nível
            </label>
            <div className="mt-1">
              <Badge
                variant="outline"
                className={LEVEL_BADGES[log.level] || LEVEL_BADGES.debug}
              >
                {LEVEL_LABELS[log.level] || log.level}
              </Badge>
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
              Status
            </label>
            <div className="mt-1">
              <Badge
                variant="outline"
                className={STATUS_BADGES[log.status] || 'bg-gray-500/10 text-gray-500'}
              >
                {STATUS_LABELS[log.status] || log.status}
              </Badge>
            </div>
          </div>

          <div className="col-span-2">
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
              Conector
            </label>
            <p className="mt-1 text-sm font-medium text-[hsl(var(--foreground))]">
              {log.connector_name || '-'}
            </p>
          </div>
        </div>

        {/* Mensagem */}
        <div>
          <label className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
            Mensagem
          </label>
          <div className="mt-1 p-3 rounded-lg bg-[hsl(var(--muted))] border border-[hsl(var(--border))]">
            <p className="text-sm text-[hsl(var(--foreground))] whitespace-pre-wrap break-words">
              {log.message || '-'}
            </p>
          </div>
        </div>

        {/* Detalhes (JSON) */}
        {hasDetails && (
          <div>
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
              Detalhes
            </label>
            <pre className="mt-1 p-3 rounded-lg bg-[hsl(var(--muted))] border border-[hsl(var(--border))] text-xs text-[hsl(var(--foreground))] overflow-x-auto max-h-[300px] overflow-y-auto font-mono whitespace-pre-wrap break-words">
              {formatDetailsJson(log.details)}
            </pre>
          </div>
        )}

        {/* Stack Trace (se erro) */}
        {hasStackTrace && (
          <div>
            <label className="text-xs font-medium text-red-500 uppercase tracking-wider">
              Stack Trace
            </label>
            <pre className="mt-1 p-3 rounded-lg bg-red-500/5 border border-red-500/20 text-xs text-red-400 overflow-x-auto max-h-[300px] overflow-y-auto font-mono whitespace-pre-wrap break-words">
              {typeof stackTrace === 'string' ? stackTrace : JSON.stringify(stackTrace, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </Modal>
  );
}
