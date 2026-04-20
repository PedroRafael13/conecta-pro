// OpportunityStage — valores lowercase conforme backend (OpportunityStage enum)

export const OPPORTUNITY_STAGE_OPTIONS = [
  { value: 'qualification',  label: 'Qualificação' },
  { value: 'needs_analysis', label: 'Análise de necessidades' },
  { value: 'proposal',       label: 'Proposta' },
  { value: 'negotiation',    label: 'Negociação' },
  { value: 'closed_won',    label: 'Ganho' },
  { value: 'closed_lost',   label: 'Perdido' },
] as const;

export type OpportunityStage = typeof OPPORTUNITY_STAGE_OPTIONS[number]['value'];

export const opportunityStagLabel = (stage?: string | null): string => {
  const found = OPPORTUNITY_STAGE_OPTIONS.find(o => o.value === stage);
  return found?.label ?? stage ?? '—';
};
