import { Badge } from '@/components/ui/badge';

interface CertificateStatusBadgeProps {
  status: string;
}

export function CertificateStatusBadge({ status }: CertificateStatusBadgeProps) {
  const statusMap: Record<
    string,
    { label: string; className: string }
  > = {
    valida: {
      label: 'Válida',
      className: 'bg-green-100 text-green-800 border-green-300',
    },
    vencendo: {
      label: 'Vencendo',
      className: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    },
    vencida: {
      label: 'Vencida',
      className: 'bg-red-100 text-red-800 border-red-300',
    },
    pendente: {
      label: 'Pendente',
      className: 'bg-gray-100 text-gray-800 border-gray-300',
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
