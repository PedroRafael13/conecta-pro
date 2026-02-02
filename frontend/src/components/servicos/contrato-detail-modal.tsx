'use client';

import { Modal } from '@/components/ui/modal';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';

interface ContratoDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  contrato: any | null;
}

const statusConfig: Record<string, { label: string; className: string }> = {
  draft: { label: 'Rascunho', className: 'bg-gray-100 text-gray-800' },
  submitted: { label: 'Submetido', className: 'bg-blue-100 text-blue-800' },
  active: { label: 'Ativo', className: 'bg-green-100 text-green-800' },
  suspended: { label: 'Suspenso', className: 'bg-yellow-100 text-yellow-800' },
  terminated: { label: 'Encerrado', className: 'bg-red-100 text-red-800' },
};

const tipoConfig: Record<string, string> = {
  servico_vigilancia: 'Vigilancia',
  servico_portaria: 'Portaria',
  servico_limpeza: 'Limpeza',
  misto: 'Misto',
};

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-';
  try {
    return new Date(dateStr).toLocaleDateString('pt-BR');
  } catch {
    return dateStr;
  }
}

export function ContratoDetailModal({
  isOpen,
  onClose,
  contrato,
}: ContratoDetailModalProps) {
  if (!contrato) return null;

  const status = statusConfig[contrato.status] || { label: contrato.status, className: 'bg-gray-100 text-gray-800' };
  const tipo = tipoConfig[contrato.contract_type] || contrato.contract_type || '-';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={contrato.titulo || contrato.title || 'Detalhes do Contrato'}
      description={contrato.numero ? `Contrato ${contrato.numero}` : undefined}
      size="lg"
    >
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label className="text-muted-foreground text-xs">Numero</Label>
            <p className="font-mono text-sm">{contrato.numero || '-'}</p>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Titulo</Label>
            <p className="text-sm">{contrato.titulo || contrato.title || '-'}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label className="text-muted-foreground text-xs">Tipo</Label>
            <div className="mt-1">
              <Badge className="bg-indigo-100 text-indigo-800">{tipo}</Badge>
            </div>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Status</Label>
            <div className="mt-1">
              <Badge className={status.className}>{status.label}</Badge>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label className="text-muted-foreground text-xs">Valor Mensal</Label>
            <p className="text-sm font-semibold">
              {formatCurrency(contrato.valor_mensal || contrato.monthly_value || 0)}
            </p>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Cliente ID</Label>
            <p className="text-sm font-mono">{contrato.client_id || '-'}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label className="text-muted-foreground text-xs">Data Inicio</Label>
            <p className="text-sm">{formatDate(contrato.data_inicio || contrato.start_date)}</p>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Data Fim</Label>
            <p className="text-sm">{formatDate(contrato.data_fim || contrato.end_date)}</p>
          </div>
        </div>

        {(contrato.observacoes || contrato.notes) && (
          <div>
            <Label className="text-muted-foreground text-xs">Observacoes</Label>
            <p className="text-sm mt-1 whitespace-pre-wrap">
              {contrato.observacoes || contrato.notes}
            </p>
          </div>
        )}

        {contrato.created_at && (
          <div className="border-t pt-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-muted-foreground text-xs">Criado em</Label>
                <p className="text-sm">{formatDate(contrato.created_at)}</p>
              </div>
              {contrato.updated_at && (
                <div>
                  <Label className="text-muted-foreground text-xs">Atualizado em</Label>
                  <p className="text-sm">{formatDate(contrato.updated_at)}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}
