'use client';

import { Badge } from '@/components/ui/badge';
import {
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Send,
  Eye,
  Archive,
  Ban,
  TrendingUp,
} from 'lucide-react';

export type ProposalStatus =
  | 'rascunho'
  | 'em_analise'
  | 'aprovada'
  | 'rejeitada'
  | 'submetida'
  | 'aguardando_documentacao'
  | 'em_negociacao'
  | 'vencedora'
  | 'perdida'
  | 'cancelada';

interface ProposalStatusBadgeProps {
  status: ProposalStatus;
  className?: string;
}

const statusConfig: Record<
  ProposalStatus,
  {
    label: string;
    variant:
      | 'default'
      | 'secondary'
      | 'destructive'
      | 'outline'
      | 'success'
      | 'warning';
    icon: React.ElementType;
  }
> = {
  rascunho: {
    label: 'Rascunho',
    variant: 'outline',
    icon: FileText,
  },
  em_analise: {
    label: 'Em Análise',
    variant: 'default',
    icon: Eye,
  },
  aprovada: {
    label: 'Aprovada',
    variant: 'success',
    icon: CheckCircle,
  },
  rejeitada: {
    label: 'Rejeitada',
    variant: 'destructive',
    icon: XCircle,
  },
  submetida: {
    label: 'Submetida',
    variant: 'default',
    icon: Send,
  },
  aguardando_documentacao: {
    label: 'Aguardando Documentação',
    variant: 'warning',
    icon: AlertTriangle,
  },
  em_negociacao: {
    label: 'Em Negociação',
    variant: 'default',
    icon: Clock,
  },
  vencedora: {
    label: 'Vencedora',
    variant: 'success',
    icon: TrendingUp,
  },
  perdida: {
    label: 'Perdida',
    variant: 'secondary',
    icon: Archive,
  },
  cancelada: {
    label: 'Cancelada',
    variant: 'destructive',
    icon: Ban,
  },
};

export function ProposalStatusBadge({
  status,
  className,
}: ProposalStatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.rascunho;
  const Icon = config.icon;

  return (
    <Badge variant={config.variant} className={className}>
      <Icon className="mr-1 h-3 w-3" />
      {config.label}
    </Badge>
  );
}

export function getStatusLabel(status: ProposalStatus): string {
  return statusConfig[status]?.label || status;
}

export const statusOptions: { value: ProposalStatus; label: string }[] = [
  { value: 'rascunho', label: 'Rascunho' },
  { value: 'em_analise', label: 'Em Análise' },
  { value: 'aprovada', label: 'Aprovada' },
  { value: 'rejeitada', label: 'Rejeitada' },
  { value: 'submetida', label: 'Submetida' },
  { value: 'aguardando_documentacao', label: 'Aguardando Documentação' },
  { value: 'em_negociacao', label: 'Em Negociação' },
  { value: 'vencedora', label: 'Vencedora' },
  { value: 'perdida', label: 'Perdida' },
  { value: 'cancelada', label: 'Cancelada' },
];
