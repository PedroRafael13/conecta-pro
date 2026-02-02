'use client';

import { FileSpreadsheet, Calendar, DollarSign, Hash, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
;

interface DctfwebData {
  id?: string;
  competencia?: string;
  tipo?: string;
  valor?: number;
  status?: string;
  data_envio?: string;
  data_vencimento?: string;
  numero_recibo?: string;
  tributos?: Array<{ nome: string; valor: number; codigo: string }>;
  observacoes?: string;
  [key: string]: any;
}

interface DctfwebDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  declaracao: DctfwebData | null;
}

const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  pendente: {
    label: 'Pendente',
    color: 'bg-yellow-100 text-yellow-800',
    icon: <Clock className="w-4 h-4" />,
  },
  enviada: {
    label: 'Enviada',
    color: 'bg-green-100 text-green-800',
    icon: <CheckCircle className="w-4 h-4" />,
  },
  retificada: {
    label: 'Retificada',
    color: 'bg-blue-100 text-blue-800',
    icon: <CheckCircle className="w-4 h-4" />,
  },
  erro: {
    label: 'Erro',
    color: 'bg-red-100 text-red-800',
    icon: <AlertCircle className="w-4 h-4" />,
  },
};

export function DctfwebDetailModal({ isOpen, onClose, declaracao }: DctfwebDetailModalProps) {
  if (!declaracao) return null;

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const formatCurrency = (value: number | undefined) => {
    if (value === undefined || value === null) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const status = (statusConfig[declaracao.status || ''] || statusConfig.pendente)!;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da DCTFWeb"
      description={`Competencia: ${declaracao.competencia || '-'}`}
      size="lg"
    >
      <div className="space-y-6">
        {/* Status */}
        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${status.color}`}>
            {status.icon}
            {status.label}
          </span>
        </div>

        {/* Dados */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Competencia</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{declaracao.competencia || '-'}</p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <FileSpreadsheet className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Tipo</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{declaracao.tipo || '-'}</p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Valor Total</span>
            </div>
            <p className="text-xl font-bold text-[hsl(var(--foreground))]">
              {formatCurrency(declaracao.valor)}
            </p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Data Envio</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{formatDate(declaracao.data_envio)}</p>
          </div>

          {declaracao.data_vencimento && (
            <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                <span className="text-sm font-medium text-[hsl(var(--foreground))]">Vencimento</span>
              </div>
              <p className="text-[hsl(var(--foreground))]">{formatDate(declaracao.data_vencimento)}</p>
            </div>
          )}

          {declaracao.numero_recibo && (
            <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Hash className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                <span className="text-sm font-medium text-[hsl(var(--foreground))]">Recibo</span>
              </div>
              <p className="text-[hsl(var(--foreground))] font-mono">{declaracao.numero_recibo}</p>
            </div>
          )}
        </div>

        {/* Tributos */}
        {declaracao.tributos && declaracao.tributos.length > 0 && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <DollarSign className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Tributos</span>
            </div>
            <div className="space-y-2">
              {declaracao.tributos.map((tributo, i) => (
                <div key={i} className="flex items-center justify-between text-sm py-2 border-b border-[hsl(var(--border))] last:border-0">
                  <div>
                    <span className="text-[hsl(var(--foreground))]">{tributo.nome}</span>
                    <span className="text-[hsl(var(--muted-foreground))] ml-2 font-mono text-xs">
                      ({tributo.codigo})
                    </span>
                  </div>
                  <span className="font-mono text-[hsl(var(--foreground))]">
                    {formatCurrency(tributo.valor)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Observacoes */}
        {declaracao.observacoes && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <span className="text-sm font-medium text-[hsl(var(--foreground))]">Observacoes</span>
            <p className="text-sm text-[hsl(var(--foreground))] mt-2 whitespace-pre-wrap">
              {declaracao.observacoes}
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
