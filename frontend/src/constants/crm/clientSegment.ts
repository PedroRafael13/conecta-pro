export const CLIENT_SEGMENT_LABELS: Record<string, string> = {
  // EN — valores reais do backend
  small:       'Pequeno Porte',
  medium:      'Médio Porte',
  large:       'Grande Porte',
  enterprise:  'Enterprise',
  condominium: 'Condomínio',
  pj:          'Pessoa Jurídica',
  // PT — fallback legado
  residencial: 'Residencial',
  comercial:   'Comercial',
  industrial:  'Industrial',
  publico:     'Público',
  misto:       'Misto',
};

export const CLIENT_SEGMENT_COLORS: Record<string, string> = {
  small:       'bg-sky-100 text-sky-800',
  medium:      'bg-cyan-100 text-cyan-800',
  large:       'bg-blue-100 text-blue-800',
  enterprise:  'bg-indigo-100 text-indigo-800',
  condominium: 'bg-teal-100 text-teal-800',
  pj:          'bg-purple-100 text-purple-800',
  residencial: 'bg-teal-100 text-teal-800',
  comercial:   'bg-amber-100 text-amber-800',
  industrial:  'bg-blue-100 text-blue-800',
  publico:     'bg-purple-100 text-purple-800',
  misto:       'bg-indigo-100 text-indigo-800',
};

export function clientSegmentLabel(v: string | null | undefined): string {
  if (!v) return '—';
  return CLIENT_SEGMENT_LABELS[v] ?? v;
}
