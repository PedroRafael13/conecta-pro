import { Badge } from '@/components/ui/badge';

interface DocumentStatusBadgeProps {
  status: string;
}

export function DocumentStatusBadge({ status }: DocumentStatusBadgeProps) {
  const statusMap: Record<
    string,
    { label: string; className: string }
  > = {
    pendente: {
      label: 'Pendente',
      className: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    },
    aprovado: {
      label: 'Aprovado',
      className: 'bg-green-100 text-green-800 border-green-300',
    },
    rejeitado: {
      label: 'Rejeitado',
      className: 'bg-red-100 text-red-800 border-red-300',
    },
    vencido: {
      label: 'Vencido',
      className: 'bg-orange-100 text-orange-800 border-orange-300',
    },
  };

  const config = statusMap[status] || {
    label: status,
    className: 'bg-gray-100 text-gray-800 border-gray-300',
  };

  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  );
}
