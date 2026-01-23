'use client';

import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import {
  OCCURRENCE_TYPE_LABELS,
  OCCURRENCE_STATUS_LABELS,
  OCCURRENCE_SEVERITY_LABELS,
  OCCURRENCE_CATEGORY_LABELS,
  type Occurrence,
  type OccurrenceStatus,
  type OccurrenceSeverity,
} from '@/types/operacional';
import {
  AlertTriangle,
  User,
  MapPin,
  Calendar,
  FileText,
  Eye,
  Edit2,
  CheckCircle,
  Clock,
  AlertCircle,
  XCircle,
  CheckSquare,
  Users,
} from 'lucide-react';

interface OccurrenceDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  occurrence: Occurrence | null;
  onResolve?: (occurrence: Occurrence) => void;
  onEdit?: (occurrence: Occurrence) => void;
}

// Cores dos status
const STATUS_COLORS: Record<OccurrenceStatus, string> = {
  aberta: 'bg-red-500/10 text-red-500 border-red-500/20',
  em_analise: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  resolvida: 'bg-green-500/10 text-green-500 border-green-500/20',
  encerrada: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  cancelada: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
};

// Cores das severidades
const SEVERITY_COLORS: Record<OccurrenceSeverity, string> = {
  leve: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  moderada: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  grave: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
  gravissima: 'bg-red-500/10 text-red-500 border-red-500/20',
};

const getStatusIcon = (status: OccurrenceStatus) => {
  switch (status) {
    case 'aberta':
      return <AlertCircle className="w-4 h-4" />;
    case 'em_analise':
      return <Clock className="w-4 h-4" />;
    case 'resolvida':
      return <CheckCircle className="w-4 h-4" />;
    case 'encerrada':
      return <CheckSquare className="w-4 h-4" />;
    case 'cancelada':
      return <XCircle className="w-4 h-4" />;
    default:
      return <AlertCircle className="w-4 h-4" />;
  }
};

export function OccurrenceDetailModal({
  isOpen,
  onClose,
  occurrence,
  onResolve,
  onEdit,
}: OccurrenceDetailModalProps) {
  if (!occurrence) return null;

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const canEdit = occurrence.status === 'aberta' || occurrence.status === 'em_analise';
  const canResolve = occurrence.status === 'aberta' || occurrence.status === 'em_analise';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da Ocorrencia"
      description={`Codigo: ${occurrence.code}`}
      size="xl"
    >
      <div className="space-y-6">
        {/* Header com Status e Severidade */}
        <div className="flex flex-wrap items-center gap-3">
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border ${
              STATUS_COLORS[occurrence.status]
            }`}
          >
            {getStatusIcon(occurrence.status)}
            {OCCURRENCE_STATUS_LABELS[occurrence.status]}
          </span>
          <span
            className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium border ${
              SEVERITY_COLORS[occurrence.severity]
            }`}
          >
            {OCCURRENCE_SEVERITY_LABELS[occurrence.severity]}
          </span>
          <span className="text-sm text-[hsl(var(--muted-foreground))]">
            {OCCURRENCE_CATEGORY_LABELS[occurrence.category]}
          </span>
        </div>

        {/* Titulo e Tipo */}
        <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
          <h3 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-2">
            {occurrence.title}
          </h3>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Tipo: {OCCURRENCE_TYPE_LABELS[occurrence.occurrence_type]}
          </p>
        </div>

        {/* Envolvidos */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <User className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">
                Funcionario Envolvido
              </span>
            </div>
            <p className="text-[hsl(var(--foreground))]">
              {occurrence.employee_name || 'Nao informado'}
            </p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <MapPin className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">
                Posto
              </span>
            </div>
            <p className="text-[hsl(var(--foreground))]">
              {occurrence.post_name || 'Nao informado'}
            </p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Eye className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">
                Registrado por
              </span>
            </div>
            <p className="text-[hsl(var(--foreground))]">
              {occurrence.inspector_name || 'Nao informado'}
            </p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">
                Data da Ocorrencia
              </span>
            </div>
            <p className="text-[hsl(var(--foreground))]">
              {formatDate(occurrence.occurred_at)}
            </p>
          </div>
        </div>

        {/* Descricao */}
        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
            <span className="text-sm font-medium text-[hsl(var(--foreground))]">
              Descricao
            </span>
          </div>
          <p className="text-[hsl(var(--foreground))] whitespace-pre-wrap">
            {occurrence.description}
          </p>
        </div>

        {/* Testemunhas */}
        {occurrence.witnesses && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">
                Testemunhas
              </span>
            </div>
            <p className="text-[hsl(var(--foreground))]">
              {occurrence.witnesses}
            </p>
          </div>
        )}

        {/* Resolucao (se houver) */}
        {occurrence.status === 'resolvida' || occurrence.status === 'encerrada' ? (
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium text-green-500">
                Resolucao
              </span>
            </div>
            <div className="space-y-2 text-sm">
              <p className="text-[hsl(var(--foreground))]">
                <strong>Resolvido por:</strong> {occurrence.resolved_by_name || '-'}
              </p>
              <p className="text-[hsl(var(--foreground))]">
                <strong>Data:</strong> {formatDate(occurrence.resolved_at)}
              </p>
              {occurrence.resolution_notes && (
                <p className="text-[hsl(var(--foreground))]">
                  <strong>Observacoes:</strong> {occurrence.resolution_notes}
                </p>
              )}
              {occurrence.corrective_action && (
                <p className="text-[hsl(var(--foreground))]">
                  <strong>Acao Corretiva:</strong> {occurrence.corrective_action}
                </p>
              )}
            </div>
          </div>
        ) : null}

        {/* Datas */}
        <div className="flex flex-wrap gap-4 text-xs text-[hsl(var(--muted-foreground))]">
          <span>Criado em: {formatDate(occurrence.created_at)}</span>
          <span>Atualizado em: {formatDate(occurrence.updated_at)}</span>
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Fechar
        </Button>

        {canEdit && onEdit && (
          <Button
            variant="outline"
            onClick={() => {
              onClose();
              onEdit(occurrence);
            }}
          >
            <Edit2 className="w-4 h-4 mr-2" />
            Editar
          </Button>
        )}

        {canResolve && onResolve && (
          <Button
            variant="primary"
            onClick={() => {
              onClose();
              onResolve(occurrence);
            }}
          >
            <CheckCircle className="w-4 h-4 mr-2" />
            Resolver
          </Button>
        )}
      </ModalFooter>
    </Modal>
  );
}
