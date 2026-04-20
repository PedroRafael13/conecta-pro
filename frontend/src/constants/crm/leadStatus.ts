// LeadStatus e LeadSource — mapeados para English (backend) e PT (legado)

export const LEAD_STATUS_LABELS: Record<string, { label: string; color: string }> = {
  // English — valores reais do backend (LeadStatus enum)
  new:         { label: 'Novo',        color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  contacted:   { label: 'Em contato',  color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30' },
  qualified:   { label: 'Qualificado', color: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30' },
  proposal:    { label: 'Proposta',    color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
  negotiation: { label: 'Negociação',  color: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
  won:         { label: 'Convertido',  color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' },
  lost:        { label: 'Perdido',     color: 'bg-red-500/20 text-red-400 border-red-500/30' },
  // Portuguese — fallback para leads criados via frontend legado
  novo:        { label: 'Novo',        color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  qualificado: { label: 'Qualificado', color: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30' },
  proposta:    { label: 'Proposta',    color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
  negociacao:  { label: 'Negociação',  color: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
  ganho:       { label: 'Convertido',  color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' },
  perdido:     { label: 'Perdido',     color: 'bg-red-500/20 text-red-400 border-red-500/30' },
};

export const LEAD_SOURCE_LABELS: Record<string, string> = {
  website:      'Website',
  referral:     'Indicação',
  social_media: 'Redes sociais',
  cold_call:    'Ligação fria',
  event:        'Evento',
  other:        'Outros',
};

export const leadStatusConfig = (status?: string | null) =>
  LEAD_STATUS_LABELS[status ?? ''] ?? {
    label: status || '—',
    color: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  };
