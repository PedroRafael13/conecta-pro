'use client';

import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import {
  FileCode, Calendar, Hash, CheckCircle,
  Clock, AlertCircle, DollarSign,
} from 'lucide-react';

interface ReinfData {
  id?: string;
  tipo_evento?: string;
  competencia?: string;
  status?: string;
  data_envio?: string;
  protocolo?: string;
  cnpj_prestador?: string;
  nome_prestador?: string;
  valor_bruto?: number;
  valor_retencao?: number;
  dados?: Record<string, any>;
  mensagem_retorno?: string;
  [key: string]: any;
}

interface ReinfDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  evento: ReinfData | null;
}

const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  pendente: {
    label: 'Pendente',
    color: 'bg-yellow-100 text-yellow-800',
    icon: <Clock className="w-4 h-4" />,
  },
  enviado: {
    label: 'Enviado',
    color: 'bg-blue-100 text-blue-800',
    icon: <CheckCircle className="w-4 h-4" />,
  },
  aceito: {
    label: 'Aceito',
    color: 'bg-green-100 text-green-800',
    icon: <CheckCircle className="w-4 h-4" />,
  },
  rejeitado: {
    label: 'Rejeitado',
    color: 'bg-red-100 text-red-800',
    icon: <AlertCircle className="w-4 h-4" />,
  },
  erro: {
    label: 'Erro',
    color: 'bg-red-100 text-red-800',
    icon: <AlertCircle className="w-4 h-4" />,
  },
};

const tipoEventoLabels: Record<string, string> = {
  'R-1000': 'R-1000 - Informacoes do Contribuinte',
  'R-2010': 'R-2010 - Retencao Contribuicao Previdenciaria',
  'R-2099': 'R-2099 - Fechamento dos Eventos',
  'R-4010': 'R-4010 - Pagamentos/Creditos PF',
  'R-4020': 'R-4020 - Pagamentos/Creditos PJ',
};

export function ReinfDetailModal({ isOpen, onClose, evento }: ReinfDetailModalProps) {
  if (!evento) return null;

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

  const status = (statusConfig[evento.status || ''] || statusConfig.pendente)!;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Evento EFD-Reinf"
      description={tipoEventoLabels[evento.tipo_evento || ''] || evento.tipo_evento || 'Evento'}
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
              <FileCode className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Tipo Evento</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">
              {tipoEventoLabels[evento.tipo_evento || ''] || evento.tipo_evento || '-'}
            </p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Competencia</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{evento.competencia || '-'}</p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Hash className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Protocolo</span>
            </div>
            <p className="text-[hsl(var(--foreground))] font-mono">{evento.protocolo || '-'}</p>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Data Envio</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{formatDate(evento.data_envio)}</p>
          </div>
        </div>

        {/* Prestador */}
        {(evento.cnpj_prestador || evento.nome_prestador) && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <span className="text-sm font-medium text-[hsl(var(--foreground))]">Prestador</span>
            <p className="text-[hsl(var(--foreground))] mt-1">{evento.nome_prestador || '-'}</p>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              CNPJ: {evento.cnpj_prestador || '-'}
            </p>
          </div>
        )}

        {/* Valores */}
        {(evento.valor_bruto !== undefined || evento.valor_retencao !== undefined) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {evento.valor_bruto !== undefined && (
              <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                  <span className="text-sm font-medium text-[hsl(var(--foreground))]">Valor Bruto</span>
                </div>
                <p className="text-xl font-bold text-[hsl(var(--foreground))]">
                  {formatCurrency(evento.valor_bruto)}
                </p>
              </div>
            )}
            {evento.valor_retencao !== undefined && (
              <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                  <span className="text-sm font-medium text-[hsl(var(--foreground))]">Valor Retencao</span>
                </div>
                <p className="text-xl font-bold text-[hsl(var(--foreground))]">
                  {formatCurrency(evento.valor_retencao)}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Dados extras */}
        {evento.dados && Object.keys(evento.dados).length > 0 && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <span className="text-sm font-medium text-[hsl(var(--foreground))]">Dados Adicionais</span>
            <div className="space-y-2 mt-2">
              {Object.entries(evento.dados).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm">
                  <span className="text-[hsl(var(--muted-foreground))]">{key}</span>
                  <span className="text-[hsl(var(--foreground))] font-mono">
                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Mensagem de Retorno */}
        {evento.mensagem_retorno && (
          <div className={`rounded-lg p-4 border ${
            evento.status === 'rejeitado' || evento.status === 'erro'
              ? 'bg-red-500/10 border-red-500/20'
              : 'bg-blue-500/10 border-blue-500/20'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className={`w-4 h-4 ${
                evento.status === 'rejeitado' || evento.status === 'erro'
                  ? 'text-red-500'
                  : 'text-blue-500'
              }`} />
              <span className={`text-sm font-medium ${
                evento.status === 'rejeitado' || evento.status === 'erro'
                  ? 'text-red-500'
                  : 'text-blue-500'
              }`}>
                Mensagem de Retorno
              </span>
            </div>
            <p className="text-sm text-[hsl(var(--foreground))]">{evento.mensagem_retorno}</p>
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
