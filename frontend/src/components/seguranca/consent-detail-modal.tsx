'use client';

import { User, Mail, Target, Scale, Calendar, Clock, Shield } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
;

interface ConsentDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  consent: any;
}

// Labels de finalidade
const PURPOSE_LABELS: Record<string, string> = {
  marketing: 'Marketing e Publicidade',
  analytics: 'Analise e Estatisticas',
  data_sharing: 'Compartilhamento de Dados',
  profiling: 'Perfilamento',
  service_provision: 'Prestacao de Servicos',
  communication: 'Comunicacao',
};

// Labels de base legal
const LEGAL_BASIS_LABELS: Record<string, string> = {
  consent: 'Consentimento do Titular (Art. 7, I)',
  legitimate_interest: 'Interesse Legitimo (Art. 7, IX)',
  contract: 'Execucao de Contrato (Art. 7, V)',
  legal_obligation: 'Obrigacao Legal (Art. 7, II)',
};

// Cores de status
const STATUS_BADGE_COLORS: Record<string, string> = {
  active: 'bg-green-500/10 text-green-500 border-green-500/20',
  revoked: 'bg-red-500/10 text-red-500 border-red-500/20',
  expired: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
};

const STATUS_LABELS: Record<string, string> = {
  active: 'Ativo',
  revoked: 'Revogado',
  expired: 'Expirado',
};

export function ConsentDetailModal({ isOpen, onClose, consent }: ConsentDetailModalProps) {
  if (!consent) return null;

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const formatDateTime = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const statusColorClass =
    STATUS_BADGE_COLORS[consent.status] || 'bg-gray-500/10 text-gray-500 border-gray-500/20';
  const statusLabel = STATUS_LABELS[consent.status] || consent.status;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Consentimento"
      description={`ID: ${consent.id || '-'}`}
      size="lg"
    >
      <div className="space-y-6">
        {/* Status Badge */}
        <div className="flex items-center gap-3">
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border ${statusColorClass}`}
          >
            <Shield className="w-4 h-4" />
            {statusLabel}
          </span>
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Titular */}
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <User className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                Titular
              </span>
            </div>
            <p className="text-sm font-medium text-[hsl(var(--foreground))]">
              {consent.holder_name || '-'}
            </p>
          </div>

          {/* Email */}
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Mail className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                E-mail
              </span>
            </div>
            <p className="text-sm text-[hsl(var(--foreground))]">
              {consent.holder_email || '-'}
            </p>
          </div>

          {/* Finalidade */}
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Target className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                Finalidade
              </span>
            </div>
            <p className="text-sm text-[hsl(var(--foreground))]">
              {PURPOSE_LABELS[consent.purpose] || consent.purpose || '-'}
            </p>
          </div>

          {/* Base Legal */}
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Scale className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                Base Legal
              </span>
            </div>
            <p className="text-sm text-[hsl(var(--foreground))]">
              {LEGAL_BASIS_LABELS[consent.legal_basis] || consent.legal_basis || '-'}
            </p>
          </div>

          {/* Valido ate */}
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                Valido ate
              </span>
            </div>
            <p className="text-sm text-[hsl(var(--foreground))]">
              {formatDate(consent.valid_until)}
            </p>
          </div>

          {/* Registrado em */}
          <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                Registrado em
              </span>
            </div>
            <p className="text-sm text-[hsl(var(--foreground))]">
              {formatDateTime(consent.created_at)}
            </p>
          </div>
        </div>

        {/* Observacoes (se houver) */}
        {consent.observacoes && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <span className="text-sm font-medium text-[hsl(var(--foreground))] block mb-2">
              Observacoes
            </span>
            <p className="text-sm text-[hsl(var(--muted-foreground))] whitespace-pre-wrap">
              {consent.observacoes}
            </p>
          </div>
        )}

        {/* Revogacao (se revogado) */}
        {consent.status === 'revoked' && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
            <span className="text-sm font-medium text-red-500 block mb-2">
              Informacoes da Revogacao
            </span>
            <div className="space-y-1 text-sm">
              {consent.revoked_at && (
                <p className="text-[hsl(var(--foreground))]">
                  <strong>Revogado em:</strong> {formatDateTime(consent.revoked_at)}
                </p>
              )}
              {consent.revoke_reason && (
                <p className="text-[hsl(var(--foreground))]">
                  <strong>Motivo:</strong> {consent.revoke_reason}
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Fechar
        </Button>
      </ModalFooter>
    </Modal>
  );
}
