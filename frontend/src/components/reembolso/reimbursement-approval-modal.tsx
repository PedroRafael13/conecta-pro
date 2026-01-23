'use client';

import { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { reimbursementService } from '@/lib/services/reimbursement';
import { getErrorMessage } from '@/lib/api';
import type { ReimbursementRequest } from '@/types/reimbursement';
import {
  EXPENSE_CATEGORY_LABELS,
  APPROVAL_LEVEL_LABELS,
} from '@/types/reimbursement';
import {
  AlertCircle,
  Loader2,
  CheckCircle,
  XCircle,
  RotateCcw,
  FileText,
  DollarSign,
  Calendar,
  User,
} from 'lucide-react';

interface ReimbursementApprovalModalProps {
  request: ReimbursementRequest | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

type ActionType = 'approve' | 'reject' | 'return' | null;

export function ReimbursementApprovalModal({
  request,
  isOpen,
  onClose,
  onSuccess,
}: ReimbursementApprovalModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionType, setActionType] = useState<ActionType>(null);
  const [comments, setComments] = useState('');
  const [rejectReason, setRejectReason] = useState('');
  const [returnReason, setReturnReason] = useState('');

  if (!request) return null;

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

  const handleApprove = async () => {
    setIsLoading(true);
    setError(null);
    setActionType('approve');

    try {
      await reimbursementService.approve(request.id, {
        comments: comments || undefined,
      });
      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
      setActionType(null);
    }
  };

  const handleReject = async () => {
    if (!rejectReason.trim()) {
      setError('Informe o motivo da rejeicao');
      return;
    }

    setIsLoading(true);
    setError(null);
    setActionType('reject');

    try {
      await reimbursementService.reject(request.id, {
        reason: rejectReason,
      });
      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
      setActionType(null);
    }
  };

  const handleReturn = async () => {
    if (!returnReason.trim()) {
      setError('Informe o motivo da devolucao');
      return;
    }

    setIsLoading(true);
    setError(null);
    setActionType('return');

    try {
      await reimbursementService.returnToDraft(request.id, {
        reason: returnReason,
      });
      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
      setActionType(null);
    }
  };

  const resetForm = () => {
    setComments('');
    setRejectReason('');
    setReturnReason('');
    setError(null);
    setActionType(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={`Aprovar Reembolso - ${request.code}`}
      description={request.title}
      size="lg"
    >
      <div className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-center gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Resumo */}
        <div className="bg-[hsl(var(--muted))] rounded-lg p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Valor Total</p>
              <p className="text-lg font-bold text-[hsl(var(--foreground))]">
                {formatCurrency(request.total_amount)}
              </p>
            </div>
            <div>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Itens</p>
              <p className="text-lg font-bold text-[hsl(var(--foreground))]">
                {request.items_count}
              </p>
            </div>
            <div>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Nivel Aprovacao</p>
              <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                {request.approval_level
                  ? APPROVAL_LEVEL_LABELS[request.approval_level]
                  : '-'}
              </p>
            </div>
            <div>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Periodo</p>
              <p className="text-sm text-[hsl(var(--foreground))]">
                {formatDate(request.expense_date_start)} - {formatDate(request.expense_date_end)}
              </p>
            </div>
          </div>
        </div>

        {/* Itens */}
        <div>
          <h4 className="text-sm font-medium text-[hsl(var(--foreground))] mb-3">
            Itens da Solicitacao
          </h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {request.items.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between bg-[hsl(var(--muted))] rounded-lg p-3"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2 py-0.5 rounded bg-[hsl(var(--background))] text-[hsl(var(--muted-foreground))]">
                      {EXPENSE_CATEGORY_LABELS[item.category_type] || item.category_type}
                    </span>
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      {formatDate(item.expense_date)}
                    </span>
                  </div>
                  <p className="text-sm text-[hsl(var(--foreground))] mt-1">
                    {item.description}
                  </p>
                  {item.merchant && (
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">{item.merchant}</p>
                  )}
                </div>
                <p className="text-sm font-bold text-[hsl(var(--foreground))]">
                  {formatCurrency(item.amount)}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Acao: Aprovar */}
        {actionType === null && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
                Comentarios (opcional)
              </label>
              <textarea
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                rows={2}
                placeholder="Adicione um comentario..."
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
              />
            </div>
          </div>
        )}

        {/* Acao: Rejeitar */}
        {actionType === 'reject' && (
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Motivo da Rejeicao *
            </label>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              rows={3}
              placeholder="Informe o motivo da rejeicao..."
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
              required
            />
          </div>
        )}

        {/* Acao: Devolver */}
        {actionType === 'return' && (
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Motivo da Devolucao *
            </label>
            <textarea
              value={returnReason}
              onChange={(e) => setReturnReason(e.target.value)}
              rows={3}
              placeholder="Informe o que precisa ser corrigido..."
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none"
              required
            />
          </div>
        )}
      </div>

      <ModalFooter>
        {actionType === null ? (
          <>
            <Button variant="outline" onClick={handleClose}>
              Cancelar
            </Button>
            <Button
              variant="outline"
              onClick={() => setActionType('return')}
              className="text-yellow-500 border-yellow-500/30 hover:bg-yellow-500/10"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Devolver
            </Button>
            <Button
              variant="outline"
              onClick={() => setActionType('reject')}
              className="text-red-500 border-red-500/30 hover:bg-red-500/10"
            >
              <XCircle className="w-4 h-4 mr-2" />
              Rejeitar
            </Button>
            <Button
              variant="primary"
              onClick={handleApprove}
              disabled={isLoading}
            >
              {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              <CheckCircle className="w-4 h-4 mr-2" />
              Aprovar
            </Button>
          </>
        ) : actionType === 'reject' ? (
          <>
            <Button variant="outline" onClick={() => setActionType(null)}>
              Voltar
            </Button>
            <Button
              variant="primary"
              onClick={handleReject}
              disabled={isLoading || !rejectReason.trim()}
              className="bg-red-500 hover:bg-red-600"
            >
              {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Confirmar Rejeicao
            </Button>
          </>
        ) : actionType === 'return' ? (
          <>
            <Button variant="outline" onClick={() => setActionType(null)}>
              Voltar
            </Button>
            <Button
              variant="primary"
              onClick={handleReturn}
              disabled={isLoading || !returnReason.trim()}
              className="bg-yellow-500 hover:bg-yellow-600"
            >
              {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Confirmar Devolucao
            </Button>
          </>
        ) : null}
      </ModalFooter>
    </Modal>
  );
}
