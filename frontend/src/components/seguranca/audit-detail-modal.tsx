'use client';

import { Eye, User, Globe, Calendar, FileText, Shield, Monitor } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
;

interface AuditDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  log: any;
}

// Labels de acao
const ACTION_LABELS: Record<string, string> = {
  data_access: 'Acesso a Dados',
  data_modification: 'Modificacao de Dados',
  data_deletion: 'Exclusão de Dados',
  data_export: 'Exportacao de Dados',
  security_incident: 'Incidente de Seguranca',
};

// Cores dos badges de acao
const ACTION_BADGE_COLORS: Record<string, string> = {
  data_access: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  data_modification: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  data_deletion: 'bg-red-500/10 text-red-500 border-red-500/20',
  data_export: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
  security_incident: 'bg-red-500/10 text-red-500 border-red-500/20',
};

// Labels de recurso
const RESOURCE_LABELS: Record<string, string> = {
  user: 'Usuario',
  customer: 'Cliente',
  employee: 'Colaborador',
  document: 'Documento',
};

export function AuditDetailModal({ isOpen, onClose, log }: AuditDetailModalProps) {
  if (!log) return null;

  const formatDateTime = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatDetails = (details: any) => {
    if (!details) return '-';
    if (typeof details === 'string') return details;
    try {
      return JSON.stringify(details, null, 2);
    } catch {
      return String(details);
    }
  };

  const actionColorClass =
    ACTION_BADGE_COLORS[log.action] || 'bg-gray-500/10 text-gray-500 border-gray-500/20';
  const actionLabel = ACTION_LABELS[log.action] || log.action;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Log de Auditoria"
      description={`ID: ${log.id || '-'}`}
      size="lg"
    >
      <div className="space-y-6">
        {/* Action Badge */}
        <div className="flex items-center gap-3">
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border ${actionColorClass}`}
          >
            <Shield className="w-4 h-4" />
            {actionLabel}
          </span>
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* ID */}
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                ID
              </span>
            </div>
            <p className="text-sm font-mono text-[hsl(var(--foreground))] break-all">
              {log.id || '-'}
            </p>
          </div>

          {/* Data/Hora */}
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                Data/Hora
              </span>
            </div>
            <p className="text-sm text-[hsl(var(--foreground))]">
              {formatDateTime(log.timestamp || log.created_at)}
            </p>
          </div>

          {/* Recurso */}
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                Recurso
              </span>
            </div>
            <p className="text-sm text-[hsl(var(--foreground))]">
              {RESOURCE_LABELS[log.resource_type] || log.resource_type || '-'}
            </p>
          </div>

          {/* Usuario */}
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <User className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                Usuario
              </span>
            </div>
            <p className="text-sm text-[hsl(var(--foreground))]">
              {log.user_name || log.user_id || '-'}
            </p>
          </div>

          {/* IP */}
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Globe className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                Endereco IP
              </span>
            </div>
            <p className="text-sm font-mono text-[hsl(var(--foreground))]">
              {log.ip_address || '-'}
            </p>
          </div>

          {/* User Agent */}
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Monitor className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                User Agent
              </span>
            </div>
            <p className="text-sm text-[hsl(var(--foreground))] break-all">
              {log.user_agent || '-'}
            </p>
          </div>
        </div>

        {/* Detalhes completos */}
        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Eye className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
            <span className="text-sm font-medium text-[hsl(var(--foreground))]">
              Detalhes
            </span>
          </div>
          <pre className="text-sm text-[hsl(var(--foreground))] whitespace-pre-wrap break-all bg-[hsl(var(--muted))] rounded-lg p-4 max-h-64 overflow-y-auto font-mono">
            {formatDetails(log.details)}
          </pre>
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
