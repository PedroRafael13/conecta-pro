'use client';

import { Award, Calendar, Building2, Hash, CheckCircle, Clock, AlertCircle, XCircle } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
;

interface CertidaoData {
  id?: string;
  tipo?: string;
  orgao?: string;
  numero?: string;
  data_emissao?: string;
  data_validade?: string;
  status?: string;
  arquivo_url?: string;
  observacoes?: string;
  [key: string]: any;
}

interface CertidaoDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  certidao: CertidaoData | null;
}

const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  valida: {
    label: 'Valida',
    color: 'bg-green-100 text-green-800',
    icon: <CheckCircle className="w-4 h-4" />,
  },
  vencendo: {
    label: 'Vencendo',
    color: 'bg-yellow-100 text-yellow-800',
    icon: <Clock className="w-4 h-4" />,
  },
  vencida: {
    label: 'Vencida',
    color: 'bg-red-100 text-red-800',
    icon: <XCircle className="w-4 h-4" />,
  },
  pendente: {
    label: 'Pendente',
    color: 'bg-blue-100 text-blue-800',
    icon: <Clock className="w-4 h-4" />,
  },
};

export function CertidaoDetailModal({ isOpen, onClose, certidao }: CertidaoDetailModalProps) {
  if (!certidao) return null;

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const getStatus = () => {
    if (certidao.status) {
      return statusConfig[certidao.status] || statusConfig.pendente;
    }

    // Calcular status com base na validade
    if (certidao.data_validade) {
      const validade = new Date(certidao.data_validade);
      const hoje = new Date();
      const diasRestantes = Math.ceil(
        (validade.getTime() - hoje.getTime()) / (1000 * 60 * 60 * 24)
      );

      if (diasRestantes < 0) return statusConfig.vencida;
      if (diasRestantes <= 30) return statusConfig.vencendo;
      return statusConfig.valida;
    }

    return statusConfig.pendente;
  };

  const status = getStatus()!;

  // Calcular dias restantes
  const getDiasRestantes = () => {
    if (!certidao.data_validade) return null;
    const validade = new Date(certidao.data_validade);
    const hoje = new Date();
    return Math.ceil((validade.getTime() - hoje.getTime()) / (1000 * 60 * 60 * 24));
  };

  const diasRestantes = getDiasRestantes();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da Certidao"
      description={certidao.tipo || 'Certidao'}
      size="lg"
    >
      <div className="space-y-6">
        {/* Status */}
        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${status.color}`}>
            {status.icon}
            {status.label}
          </span>
          {diasRestantes !== null && (
            <span className={`text-sm ${
              diasRestantes < 0
                ? 'text-red-500'
                : diasRestantes <= 30
                ? 'text-yellow-500'
                : 'text-green-500'
            }`}>
              {diasRestantes < 0
                ? `Vencida ha ${Math.abs(diasRestantes)} dias`
                : diasRestantes === 0
                ? 'Vence hoje'
                : `${diasRestantes} dias restantes`}
            </span>
          )}
        </div>

        {/* Dados */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Award className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Tipo</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{certidao.tipo || '-'}</p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Building2 className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Orgao Emissor</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{certidao.orgao || '-'}</p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Hash className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Numero</span>
            </div>
            <p className="text-[hsl(var(--foreground))] font-mono">{certidao.numero || '-'}</p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Data Emissao</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{formatDate(certidao.data_emissao)}</p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4 md:col-span-2">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Data Validade</span>
            </div>
            <p className={`text-[hsl(var(--foreground))] font-medium ${
              diasRestantes !== null && diasRestantes < 0
                ? 'text-red-500'
                : diasRestantes !== null && diasRestantes <= 30
                ? 'text-yellow-500'
                : ''
            }`}>
              {formatDate(certidao.data_validade)}
            </p>
          </div>
        </div>

        {/* Observações */}
        {certidao.observacoes && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <span className="text-sm font-medium text-[hsl(var(--foreground))]">Observações</span>
            <p className="text-sm text-[hsl(var(--foreground))] mt-2 whitespace-pre-wrap">
              {certidao.observacoes}
            </p>
          </div>
        )}
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Fechar
        </Button>
      </ModalFooter>
    </Modal>
  );
}
