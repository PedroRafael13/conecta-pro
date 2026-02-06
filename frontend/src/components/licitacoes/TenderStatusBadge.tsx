'use client';

/**
 * Badge de Status de Edital
 * Componente visual para exibir status de editais com cores
 */

import {
  AlertCircle,
  Clock,
  CheckCircle,
  XCircle,
  Archive,
  Eye,
  FileCheck,
  Ban
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export type TenderStatus =
  | 'aberto'
  | 'em_andamento'
  | 'em_analise'
  | 'participando'
  | 'interesse'
  | 'homologado'
  | 'cancelado'
  | 'deserto'
  | 'fracassado'
  | 'arquivado';

interface TenderStatusBadgeProps {
  status: string;
  showIcon?: boolean;
  className?: string;
}

const STATUS_CONFIG: Record<
  TenderStatus,
  { label: string; color: string; icon: any }
> = {
  aberto: {
    label: 'Aberto',
    color: 'bg-green-500/10 text-green-500 border-green-500/20',
    icon: AlertCircle,
  },
  em_andamento: {
    label: 'Em Andamento',
    color: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
    icon: Clock,
  },
  em_analise: {
    label: 'Em Análise',
    color: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
    icon: Eye,
  },
  participando: {
    label: 'Participando',
    color: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
    icon: FileCheck,
  },
  interesse: {
    label: 'Interesse',
    color: 'bg-cyan-500/10 text-cyan-500 border-cyan-500/20',
    icon: Eye,
  },
  homologado: {
    label: 'Homologado',
    color: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    icon: CheckCircle,
  },
  cancelado: {
    label: 'Cancelado',
    color: 'bg-red-500/10 text-red-500 border-red-500/20',
    icon: XCircle,
  },
  deserto: {
    label: 'Deserto',
    color: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
    icon: Ban,
  },
  fracassado: {
    label: 'Fracassado',
    color: 'bg-red-600/10 text-red-600 border-red-600/20',
    icon: XCircle,
  },
  arquivado: {
    label: 'Arquivado',
    color: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
    icon: Archive,
  },
};

export function TenderStatusBadge({
  status,
  showIcon = true,
  className = '',
}: TenderStatusBadgeProps) {
  const config = STATUS_CONFIG[status as TenderStatus] || {
    label: status,
    color: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
    icon: AlertCircle,
  };

  const Icon = config.icon;

  return (
    <Badge
      variant="outline"
      className={`inline-flex items-center gap-1 ${config.color} ${className}`}
    >
      {showIcon && <Icon className="w-3 h-3" />}
      {config.label}
    </Badge>
  );
}
