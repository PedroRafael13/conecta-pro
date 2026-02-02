'use client';

import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import {
  Users, Calendar, FileText, Hash, CheckCircle,
  Clock, AlertCircle, XCircle,
} from 'lucide-react';

interface EventoData {
  id?: string;
  tipo_evento?: string;
  status?: string;
  dados?: Record<string, any>;
  data_envio?: string;
  protocolo?: string;
  created_at?: string;
  updated_at?: string;
  mensagem_retorno?: string;
  [key: string]: any;
}

interface EsocialDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  evento: EventoData | null;
  onReenviar?: (evento: EventoData) => void;
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
    icon: <XCircle className="w-4 h-4" />,
  },
  erro: {
    label: 'Erro',
    color: 'bg-red-100 text-red-800',
    icon: <AlertCircle className="w-4 h-4" />,
  },
};

export function EsocialDetailModal({
  isOpen,
  onClose,
  evento,
  onReenviar,
}: EsocialDetailModalProps) {
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

  const status = (statusConfig[evento.status || ''] || statusConfig.pendente)!;
  const canReenviar = evento.status === 'rejeitado' || evento.status === 'erro';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes do Evento eSocial"
      description={evento.tipo_evento || 'Evento'}
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

        {/* Dados do Evento */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Tipo Evento</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{evento.tipo_evento || '-'}</p>
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

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Atualizado em</span>
            </div>
            <p className="text-[hsl(var(--foreground))]">{formatDate(evento.updated_at)}</p>
          </div>
        </div>

        {/* Dados do Evento (JSON) */}
        {evento.dados && Object.keys(evento.dados).length > 0 && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Dados do Evento</span>
            </div>
            <div className="space-y-2">
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
        {canReenviar && onReenviar && (
          <Button
            onClick={() => {
              onClose();
              onReenviar(evento);
            }}
          >
            Reenviar Evento
          </Button>
        )}
      </ModalFooter>
    </Modal>
  );
}
