'use client';

;
import { Calendar, User, MapPin, DollarSign, FileText } from 'lucide-react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import type { Allocation, AllocationStatus } from '@/types/operacional';
import { ALLOCATION_STATUS_LABELS } from '@/types/operacional';

interface AllocationDetailModalProps {
  allocation: Allocation | null;
  isOpen: boolean;
  onClose: () => void;
  employeeName?: string;
  postName?: string;
  onTerminate?: () => void;
}

export function AllocationDetailModal({
  allocation,
  isOpen,
  onClose,
  employeeName,
  postName,
  onTerminate,
}: AllocationDetailModalProps) {
  if (!allocation) return null;

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value || 0);
  };

  const getStatusBadge = (status: AllocationStatus) => {
    const base = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium';
    switch (status) {
      case 'active':
        return `${base} bg-green-500/10 text-green-500`;
      case 'pending':
        return `${base} bg-yellow-500/10 text-yellow-500`;
      case 'suspended':
        return `${base} bg-orange-500/10 text-orange-500`;
      case 'terminated':
        return `${base} bg-red-500/10 text-red-500`;
      default:
        return `${base} bg-gray-500/10 text-gray-500`;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da Alocação"
      description={allocation.id}
      size="lg"
    >
      <div className="space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <span className={getStatusBadge(allocation.status as AllocationStatus)}>
              {ALLOCATION_STATUS_LABELS[allocation.status as AllocationStatus] || allocation.status}
            </span>
            <p className="text-sm text-[hsl(var(--muted-foreground))] mt-2">
              Alocação {allocation.is_current ? 'vigente' : 'nao vigente'}
            </p>
          </div>
          <div className="text-right text-xs text-[hsl(var(--muted-foreground))]">
            <p>Criado em {formatDate(allocation.created_at)}</p>
            <p>Atualizado em {formatDate(allocation.updated_at)}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
              <User className="w-4 h-4" />
              Funcionario
            </div>
            <p className="text-[hsl(var(--foreground))] font-medium mt-2">
              {employeeName || allocation.employee_id}
            </p>
          </div>
          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
              <MapPin className="w-4 h-4" />
              Posto
            </div>
            <p className="text-[hsl(var(--foreground))] font-medium mt-2">
              {postName || allocation.post_id}
            </p>
          </div>
          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
              <Calendar className="w-4 h-4" />
              Periodo
            </div>
            <p className="text-[hsl(var(--foreground))] font-medium mt-2">
              {formatDate(allocation.start_date)} - {formatDate(allocation.end_date)}
            </p>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
              {allocation.days_allocated} dias
            </p>
          </div>
          <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
              <DollarSign className="w-4 h-4" />
              Custos
            </div>
            <p className="text-[hsl(var(--foreground))] font-medium mt-2">
              {formatCurrency(allocation.total_monthly_cost)}
            </p>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
              Hora: {formatCurrency(allocation.hourly_rate)}
            </p>
          </div>
        </div>

        {(allocation.role || allocation.notes || allocation.termination_reason) && (
          <div>
            <h3 className="text-sm font-medium text-[hsl(var(--foreground))] mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Observações
            </h3>
            <div className="bg-[hsl(var(--muted))]/50 rounded-lg p-3 text-sm text-[hsl(var(--foreground))] space-y-2">
              {allocation.role && (
                <p>
                  <span className="text-[hsl(var(--muted-foreground))]">Função:</span> {allocation.role}
                </p>
              )}
              {allocation.notes && (
                <p>
                  <span className="text-[hsl(var(--muted-foreground))]">Notas:</span> {allocation.notes}
                </p>
              )}
              {allocation.termination_reason && (
                <p>
                  <span className="text-[hsl(var(--muted-foreground))]">Motivo:</span> {allocation.termination_reason}
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Fechar
        </Button>
        {onTerminate && allocation.status === 'active' && (
          <Button variant="primary" onClick={onTerminate}>
            Encerrar Alocação
          </Button>
        )}
      </ModalFooter>
    </Modal>
  );
}
