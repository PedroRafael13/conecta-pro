import { Badge } from '@/components/ui/badge';

interface ContractStatusBadgeProps {
  status: string;
}

export function ContractStatusBadge({ status }: ContractStatusBadgeProps) {
  const statusMap: Record<
    string,
    { label: string; className: string }
  > = {
    vigente: {
      label: 'Vigente',
      className: 'bg-green-100 text-green-800 border-green-300',
    },
    vencendo: {
      label: 'Vencendo',
      className: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    },
    vencido: {
      label: 'Vencido',
      className: 'bg-red-100 text-red-800 border-red-300',
    },
    suspenso: {
      label: 'Suspenso',
      className: 'bg-gray-100 text-gray-800 border-gray-300',
    },
    rescindido: {
      label: 'Rescindido',
      className: 'bg-orange-100 text-orange-800 border-orange-300',
    },
    executado: {
      label: 'Executado',
      className: 'bg-blue-100 text-blue-800 border-blue-300',
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
