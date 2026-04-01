'use client';

import { Database, Calendar, FileText, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
;

interface SpedData {
  id?: string;
  tipo?: string;
  mes_referencia?: string;
  ano_referencia?: number;
  status?: string;
  data_geracao?: string;
  arquivo?: string;
  registros?: number;
  observacoes?: string;
  validacao?: {
    valido?: boolean;
    erros?: string[];
    avisos?: string[];
  };
  [key: string]: any;
}

interface SpedDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  sped: SpedData | null;
}

const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  gerado: {
    label: 'Gerado',
    color: 'bg-blue-100 text-blue-800',
    icon: <CheckCircle className="w-4 h-4" />,
  },
  validado: {
    label: 'Validado',
    color: 'bg-green-100 text-green-800',
    icon: <CheckCircle className="w-4 h-4" />,
  },
  pendente: {
    label: 'Pendente',
    color: 'bg-yellow-100 text-yellow-800',
    icon: <Clock className="w-4 h-4" />,
  },
  erro: {
    label: 'Erro',
    color: 'bg-red-100 text-red-800',
    icon: <AlertCircle className="w-4 h-4" />,
  },
  enviado: {
    label: 'Enviado',
    color: 'bg-emerald-100 text-emerald-800',
    icon: <CheckCircle className="w-4 h-4" />,
  },
};

const tipoLabels: Record<string, string> = {
  fiscal: 'SPED Fiscal',
  contabil: 'SPED Contabil',
  reinf: 'EFD-Reinf',
};

export function SpedDetailModal({ isOpen, onClose, sped }: SpedDetailModalProps) {
  if (!sped) return null;

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const status = (statusConfig[sped.status || ''] || statusConfig.pendente)!;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Arquivo SPED"
      description={tipoLabels[sped.tipo || ''] || sped.tipo || 'SPED'}
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
              <Database className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Tipo</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">
              {tipoLabels[sped.tipo || ''] || sped.tipo || '-'}
            </p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Periodo</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">
              {sped.mes_referencia || '-'}/{sped.ano_referencia || '-'}
            </p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Data Geracao</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{formatDate(sped.data_geracao)}</p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Registros</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">
              {sped.registros !== undefined ? sped.registros.toLocaleString('pt-BR') : '-'}
            </p>
          </div>
        </div>

        {/* Arquivo */}
        {sped.arquivo && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Arquivo</span>
            </div>
            <p className="text-sm text-[hsl(var(--foreground))] font-mono">{sped.arquivo}</p>
          </div>
        )}

        {/* Validacao */}
        {sped.validacao && (
          <div className="space-y-3">
            {sped.validacao.erros && sped.validacao.erros.length > 0 && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-4 h-4 text-red-500" />
                  <span className="text-sm font-medium text-red-500">Erros de Validacao</span>
                </div>
                <ul className="space-y-1">
                  {sped.validacao.erros.map((erro, i) => (
                    <li key={i} className="text-sm text-[hsl(var(--foreground))]">- {erro}</li>
                  ))}
                </ul>
              </div>
            )}

            {sped.validacao.avisos && sped.validacao.avisos.length > 0 && (
              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm font-medium text-yellow-500">Avisos</span>
                </div>
                <ul className="space-y-1">
                  {sped.validacao.avisos.map((aviso, i) => (
                    <li key={i} className="text-sm text-[hsl(var(--foreground))]">- {aviso}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Observações */}
        {sped.observacoes && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Observações</span>
            </div>
            <p className="text-sm text-[hsl(var(--foreground))] whitespace-pre-wrap">
              {sped.observacoes}
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
