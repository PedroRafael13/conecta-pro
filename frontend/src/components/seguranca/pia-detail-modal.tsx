'use client';

import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface PIADetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  pia: any;
}

const statusLabels: Record<string, string> = {
  draft: 'Rascunho',
  in_progress: 'Em Andamento',
  completed: 'Concluida',
  archived: 'Arquivada',
};

const statusVariants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  draft: 'secondary',
  in_progress: 'default',
  completed: 'outline',
  archived: 'secondary',
};

const riskLabels: Record<string, string> = {
  low: 'Baixo',
  medium: 'Medio',
  high: 'Alto',
  critical: 'Critico',
};

const riskVariants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  low: 'outline',
  medium: 'secondary',
  high: 'default',
  critical: 'destructive',
};

const typeLabels: Record<string, string> = {
  simple: 'PIA Simplificada',
  complete: 'PIA Completa (DPIA)',
};

export function PIADetailModal({ isOpen, onClose, pia }: PIADetailModalProps) {
  if (!pia) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da Avaliacao"
      size="lg"
    >
      <div className="space-y-6">
        {/* Titulo */}
        <div>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Titulo</p>
          <p className="text-base font-semibold mt-1">{pia.title}</p>
        </div>

        {/* Tipo e Status */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Tipo</p>
            <div className="mt-1">
              <Badge variant={pia.pia_type === 'complete' ? 'default' : 'secondary'}>
                {typeLabels[pia.pia_type] || pia.pia_type}
              </Badge>
            </div>
          </div>
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Status</p>
            <div className="mt-1">
              <Badge variant={statusVariants[pia.status] || 'secondary'}>
                {statusLabels[pia.status] || pia.status}
              </Badge>
            </div>
          </div>
        </div>

        {/* Risco e Responsavel */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Nivel de Risco</p>
            <div className="mt-1">
              <Badge variant={riskVariants[pia.risk_level] || 'secondary'}>
                {riskLabels[pia.risk_level] || pia.risk_level}
              </Badge>
            </div>
          </div>
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Responsavel</p>
            <p className="text-base mt-1">{pia.responsible || '-'}</p>
          </div>
        </div>

        {/* Tipos de Dados */}
        {pia.data_types && (
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Tipos de Dados</p>
            <p className="text-base mt-1 whitespace-pre-wrap">{pia.data_types}</p>
          </div>
        )}

        {/* Finalidade */}
        {pia.processing_purpose && (
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              Finalidade do Tratamento
            </p>
            <p className="text-base mt-1 whitespace-pre-wrap">
              {pia.processing_purpose}
            </p>
          </div>
        )}

        {/* Descricao */}
        {pia.description && (
          <div>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">Descricao</p>
            <p className="text-base mt-1 whitespace-pre-wrap">{pia.description}</p>
          </div>
        )}

        {/* Data de Criação */}
        <div>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Criado em</p>
          <p className="text-base mt-1">
            {pia.created_at
              ? new Date(pia.created_at).toLocaleDateString('pt-BR', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })
              : '-'}
          </p>
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
