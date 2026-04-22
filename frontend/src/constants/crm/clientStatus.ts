export const CLIENT_STATUS_LABELS: Record<string, string> = {
  // EN — valores reais do backend
  active:      'Ativo',
  inactive:    'Inativo',
  blocked:     'Bloqueado',
  prospect:    'Prospecto',
  suspended:   'Suspenso',
  // PT — fallback legado
  ativo:       'Ativo',
  inativo:     'Inativo',
  bloqueado:   'Bloqueado',
  prospecto:   'Prospecto',
  suspenso:    'Suspenso',
  inadimplente:'Inadimplente',
};

export const CLIENT_STATUS_COLORS: Record<string, string> = {
  active:      'bg-green-100 text-green-800',
  inactive:    'bg-red-100 text-red-800',
  blocked:     'bg-orange-100 text-orange-800',
  prospect:    'bg-yellow-100 text-yellow-800',
  suspended:   'bg-yellow-100 text-yellow-800',
  ativo:       'bg-green-100 text-green-800',
  inativo:     'bg-red-100 text-red-800',
  bloqueado:   'bg-orange-100 text-orange-800',
  prospecto:   'bg-yellow-100 text-yellow-800',
  suspenso:    'bg-yellow-100 text-yellow-800',
  inadimplente:'bg-orange-100 text-orange-800',
};

export function clientStatusLabel(v: string | null | undefined): string {
  if (!v) return '—';
  return CLIENT_STATUS_LABELS[v] ?? v;
}
