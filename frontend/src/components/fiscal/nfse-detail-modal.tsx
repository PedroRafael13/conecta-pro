'use client';

import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { FileText, Calendar, DollarSign, Building2, Hash } from 'lucide-react';

interface NfseData {
  id?: string;
  numero?: string;
  serie?: string;
  tomador_cnpj?: string;
  tomador_nome?: string;
  descricao_servico?: string;
  valor_servico?: number;
  aliquota_iss?: number;
  codigo_servico?: string;
  status?: string;
  data_emissao?: string;
  [key: string]: any;
}

interface NfseDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  nfse: NfseData | null;
}

const statusConfig: Record<string, { label: string; color: string }> = {
  emitida: { label: 'Emitida', color: 'bg-green-100 text-green-800' },
  cancelada: { label: 'Cancelada', color: 'bg-red-100 text-red-800' },
  pendente: { label: 'Pendente', color: 'bg-yellow-100 text-yellow-800' },
  processando: { label: 'Processando', color: 'bg-blue-100 text-blue-800' },
};

export function NfseDetailModal({ isOpen, onClose, nfse }: NfseDetailModalProps) {
  if (!nfse) return null;

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

  const formatCurrency = (value: number | undefined) => {
    if (value === undefined || value === null) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const status = (statusConfig[nfse.status || ''] || statusConfig.pendente)!;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da NFS-e"
      description={`Nota Fiscal ${nfse.numero || '-'}`}
      size="lg"
    >
      <div className="space-y-6">
        {/* Status Badge */}
        <div className="flex items-center gap-3">
          <span className={`inline-flex px-3 py-1.5 rounded-full text-sm font-medium ${status.color}`}>
            {status.label}
          </span>
        </div>

        {/* Dados da Nota */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Hash className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Numero</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{nfse.numero || '-'}</p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Serie</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{nfse.serie || '-'}</p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Building2 className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Tomador</span>
            </div>
            <p className="text-[hsl(var(--foreground))] font-medium">{nfse.tomador_nome || '-'}</p>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              CNPJ: {nfse.tomador_cnpj || '-'}
            </p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Data Emissao</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{formatDate(nfse.data_emissao)}</p>
          </div>
        </div>

        {/* Servico */}
        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
            <span className="text-sm font-medium text-[hsl(var(--foreground))]">Servico</span>
          </div>
          <p className="text-[hsl(var(--foreground))] whitespace-pre-wrap">
            {nfse.descricao_servico || '-'}
          </p>
          {nfse.codigo_servico && (
            <p className="text-sm text-[hsl(var(--muted-foreground))] mt-2">
              Codigo: {nfse.codigo_servico}
            </p>
          )}
        </div>

        {/* Valores */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Valor</span>
            </div>
            <p className="text-xl font-bold text-[hsl(var(--foreground))]">
              {formatCurrency(nfse.valor_servico)}
            </p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Aliquota ISS</span>
            </div>
            <p className="text-xl font-bold text-[hsl(var(--foreground))]">
              {nfse.aliquota_iss !== undefined ? `${nfse.aliquota_iss}%` : '-'}
            </p>
          </div>
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Fechar
        </Button>
      </ModalFooter>
    </Modal>
  );
}
