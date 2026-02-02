'use client';

/**
 * Badge de Modalidade de Licitação
 * Componente visual para exibir modalidades com cores
 */

import { Badge } from '@/components/ui/badge';

export type TenderModality =
  | 'pregao_eletronico'
  | 'pregao_presencial'
  | 'concorrencia'
  | 'tomada_precos'
  | 'convite'
  | 'concurso'
  | 'leilao'
  | 'credenciamento'
  | 'rdc'
  | 'dialogo_competitivo'
  | 'dispensa'
  | 'inexigibilidade';

interface ModalityBadgeProps {
  modality: string;
  className?: string;
}

const MODALITY_CONFIG: Record<
  TenderModality,
  { label: string; color: string }
> = {
  pregao_eletronico: {
    label: 'Pregão Eletrônico',
    color: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
  },
  pregao_presencial: {
    label: 'Pregão Presencial',
    color: 'bg-blue-600/10 text-blue-700 border-blue-600/20',
  },
  concorrencia: {
    label: 'Concorrência',
    color: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
  },
  tomada_precos: {
    label: 'Tomada de Preços',
    color: 'bg-indigo-500/10 text-indigo-600 border-indigo-500/20',
  },
  convite: {
    label: 'Convite',
    color: 'bg-cyan-500/10 text-cyan-600 border-cyan-500/20',
  },
  concurso: {
    label: 'Concurso',
    color: 'bg-teal-500/10 text-teal-600 border-teal-500/20',
  },
  leilao: {
    label: 'Leilão',
    color: 'bg-orange-500/10 text-orange-600 border-orange-500/20',
  },
  credenciamento: {
    label: 'Credenciamento',
    color: 'bg-amber-500/10 text-amber-600 border-amber-500/20',
  },
  rdc: {
    label: 'RDC',
    color: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20',
  },
  dialogo_competitivo: {
    label: 'Diálogo Competitivo',
    color: 'bg-violet-500/10 text-violet-600 border-violet-500/20',
  },
  dispensa: {
    label: 'Dispensa',
    color: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
  },
  inexigibilidade: {
    label: 'Inexigibilidade',
    color: 'bg-red-500/10 text-red-600 border-red-500/20',
  },
};

export function ModalityBadge({ modality, className = '' }: ModalityBadgeProps) {
  const config = MODALITY_CONFIG[modality as TenderModality] || {
    label: modality,
    color: 'bg-gray-500/10 text-gray-600 border-gray-500/20',
  };

  return (
    <Badge variant="outline" className={`${config.color} ${className}`}>
      {config.label}
    </Badge>
  );
}
