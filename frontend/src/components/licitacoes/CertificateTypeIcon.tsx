import { FileText, Building2, Landmark, Users, Shield } from 'lucide-react';

interface CertificateTypeIconProps {
  tipo: string;
  className?: string;
}

export function CertificateTypeIcon({ tipo, className = 'h-5 w-5' }: CertificateTypeIconProps) {
  const tipoLower = tipo.toLowerCase();

  if (tipoLower.includes('federal')) {
    return <Landmark className={className} />;
  }
  if (tipoLower.includes('estadual')) {
    return <Building2 className={className} />;
  }
  if (tipoLower.includes('municipal')) {
    return <Building2 className={className} />;
  }
  if (tipoLower.includes('trabalhista') || tipoLower.includes('tst')) {
    return <Users className={className} />;
  }
  if (tipoLower.includes('fgts') || tipoLower.includes('inss')) {
    return <Shield className={className} />;
  }

  return <FileText className={className} />;
}
