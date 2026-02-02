'use client';

import { AlertCircle, Loader2, Edit2, Send, XCircle, FileText, DollarSign, Calendar, Building2, User, Clock, CheckCircle, Paperclip, Download } from 'lucide-react';
import { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { getErrorMessage } from '@/lib/api';
import type { ReimbursementRequest, ReimbursementStatus } from '@/types/reimbursement';
import {
  REIMBURSEMENT_STATUS_LABELS,
  EXPENSE_CATEGORY_LABELS,
  STATUS_COLORS,
  APPROVAL_LEVEL_LABELS,
} from '@/types/reimbursement';
;
import { AttachmentUpload } from './attachment-upload';

interface ReimbursementDetailModalProps {
  request: ReimbursementRequest | null;
  isOpen: boolean;
  onClose: () => void;
  onEdit: () => void;
  onRefresh: () => void;
}

export function ReimbursementDetailModal({
  request,
  isOpen,
  onClose,
  onEdit,
  onRefresh,
}: ReimbursementDetailModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionType, setActionType] = useState<'submit' | 'cancel' | null>(null);

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

  const formatDateTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('pt-BR');
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    setActionType('submit');

    try {
      await reimbursementService.submit(request.id);
      onRefresh();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
      setActionType(null);
    }
  };

  const handleCancel = async () => {
    setIsLoading(true);
    setError(null);
    setActionType('cancel');

    try {
      await reimbursementService.cancel(request.id);
      onRefresh();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
      setActionType(null);
    }
  };

  const handleAttachmentUpload = async (file: File) => {
    await reimbursementService.uploadAttachment(request.id, file, {
      attachment_type: 'outros',
    });
    onRefresh();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={request.title}
      description={request.code}
      size="xl"
    >
      <div className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-center gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Status e Valores */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-[hsl(var(--muted))] rounded-lg p-3">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Status</p>
            <span
              className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                STATUS_COLORS[request.status as ReimbursementStatus]
              }`}
            >
              {REIMBURSEMENT_STATUS_LABELS[request.status as ReimbursementStatus]}
            </span>
          </div>
          <div className="bg-[hsl(var(--muted))] rounded-lg p-3">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Valor Total</p>
            <p className="text-lg font-bold text-[hsl(var(--foreground))]">
              {formatCurrency(request.total_amount)}
            </p>
          </div>
          <div className="bg-[hsl(var(--muted))] rounded-lg p-3">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Valor Aprovado</p>
            <p className="text-lg font-bold text-green-500">
              {formatCurrency(request.approved_amount)}
            </p>
          </div>
          <div className="bg-[hsl(var(--muted))] rounded-lg p-3">
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">Nivel Aprovacao</p>
            <p className="text-sm font-medium text-[hsl(var(--foreground))]">
              {request.approval_level
                ? APPROVAL_LEVEL_LABELS[request.approval_level]
                : '-'}
            </p>
          </div>
        </div>

        {/* Informacoes */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm text-[hsl(var(--muted-foreground))]">Periodo:</span>
              <span className="text-sm text-[hsl(var(--foreground))]">
                {formatDate(request.expense_date_start)} - {formatDate(request.expense_date_end)}
              </span>
            </div>
            {request.cost_center && (
              <div className="flex items-center gap-2">
                <Building2 className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                <span className="text-sm text-[hsl(var(--muted-foreground))]">Centro de Custo:</span>
                <span className="text-sm text-[hsl(var(--foreground))]">{request.cost_center}</span>
              </div>
            )}
            {request.project && (
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                <span className="text-sm text-[hsl(var(--muted-foreground))]">Projeto:</span>
                <span className="text-sm text-[hsl(var(--foreground))]">{request.project}</span>
              </div>
            )}
          </div>
          <div className="space-y-3">
            {request.submitted_at && (
              <div className="flex items-center gap-2">
                <Send className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                <span className="text-sm text-[hsl(var(--muted-foreground))]">Submetido em:</span>
                <span className="text-sm text-[hsl(var(--foreground))]">
                  {formatDateTime(request.submitted_at)}
                </span>
              </div>
            )}
            {request.approved_at && (
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-sm text-[hsl(var(--muted-foreground))]">Aprovado em:</span>
                <span className="text-sm text-[hsl(var(--foreground))]">
                  {formatDateTime(request.approved_at)}
                </span>
              </div>
            )}
            {request.rejection_reason && (
              <div className="flex items-start gap-2 text-red-500">
                <XCircle className="w-4 h-4 mt-0.5" />
                <div>
                  <span className="text-sm">Motivo Rejeicao:</span>
                  <p className="text-sm">{request.rejection_reason}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Descricao */}
        {request.description && (
          <div>
            <h4 className="text-sm font-medium text-[hsl(var(--foreground))] mb-2">Descricao</h4>
            <p className="text-sm text-[hsl(var(--muted-foreground))] bg-[hsl(var(--muted))] p-3 rounded-lg">
              {request.description}
            </p>
          </div>
        )}

        {/* Itens */}
        <div>
          <h4 className="text-sm font-medium text-[hsl(var(--foreground))] mb-3">
            Itens ({request.items.length})
          </h4>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {request.items.map((item) => (
              <div
                key={item.id}
                className={`bg-[hsl(var(--muted))] rounded-lg p-3 border-l-4 ${
                  item.is_approved
                    ? 'border-green-500'
                    : item.rejection_reason
                    ? 'border-red-500'
                    : 'border-gray-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs px-2 py-0.5 rounded bg-[hsl(var(--background))] text-[hsl(var(--muted-foreground))]">
                        {EXPENSE_CATEGORY_LABELS[item.category_type] || item.category_type}
                      </span>
                      <span className="text-xs text-[hsl(var(--muted-foreground))]">
                        {formatDate(item.expense_date)}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-[hsl(var(--foreground))] mt-1">
                      {item.description}
                    </p>
                    {item.merchant && (
                      <p className="text-xs text-[hsl(var(--muted-foreground))]">{item.merchant}</p>
                    )}
                    {item.rejection_reason && (
                      <p className="text-xs text-red-500 mt-1">
                        Rejeitado: {item.rejection_reason}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-[hsl(var(--foreground))]">
                      {formatCurrency(item.amount)}
                    </p>
                    {item.is_approved && item.approved_amount !== item.amount && (
                      <p className="text-xs text-green-500">
                        Aprovado: {formatCurrency(item.approved_amount || 0)}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Anexos */}
        <div>
          <h4 className="text-sm font-medium text-[hsl(var(--foreground))] mb-3">
            Anexos ({request.attachments.length})
          </h4>

          {request.attachments.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mb-4">
              {request.attachments.map((attachment) => (
                <div
                  key={attachment.id}
                  className="flex items-center gap-2 bg-[hsl(var(--muted))] rounded-lg p-2"
                >
                  <Paperclip className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-[hsl(var(--foreground))] truncate">
                      {attachment.original_name || attachment.file_name}
                    </p>
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">
                      {attachment.file_size_formatted}
                    </p>
                  </div>
                  <a
                    href={reimbursementService.getAttachmentDownloadUrl(attachment.id)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[hsl(var(--primary))] hover:text-[hsl(var(--primary))]/80"
                  >
                    <Download className="w-4 h-4" />
                  </a>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-[hsl(var(--muted-foreground))] mb-4">
              Nenhum anexo adicionado
            </p>
          )}

          {/* Upload de anexos (apenas em rascunho) */}
          {request.can_edit && (
            <AttachmentUpload
              onUpload={handleAttachmentUpload}
              disabled={isLoading}
            />
          )}
        </div>

        {/* Dados Bancarios */}
        {(request.bank_code || request.pix_key) && (
          <div>
            <h4 className="text-sm font-medium text-[hsl(var(--foreground))] mb-2">
              Dados Bancarios
            </h4>
            <div className="bg-[hsl(var(--muted))] rounded-lg p-3 grid grid-cols-2 md:grid-cols-4 gap-3">
              {request.bank_code && (
                <div>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">Banco</p>
                  <p className="text-sm text-[hsl(var(--foreground))]">{request.bank_code}</p>
                </div>
              )}
              {request.bank_agency && (
                <div>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">Agencia</p>
                  <p className="text-sm text-[hsl(var(--foreground))]">{request.bank_agency}</p>
                </div>
              )}
              {request.bank_account && (
                <div>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">Conta</p>
                  <p className="text-sm text-[hsl(var(--foreground))]">{request.bank_account}</p>
                </div>
              )}
              {request.pix_key && (
                <div>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">PIX</p>
                  <p className="text-sm text-[hsl(var(--foreground))]">{request.pix_key}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Observacoes */}
        {request.notes && (
          <div>
            <h4 className="text-sm font-medium text-[hsl(var(--foreground))] mb-2">Observacoes</h4>
            <p className="text-sm text-[hsl(var(--muted-foreground))] bg-[hsl(var(--muted))] p-3 rounded-lg whitespace-pre-wrap">
              {request.notes}
            </p>
          </div>
        )}
      </div>

      <ModalFooter>
        <div className="flex items-center gap-2 w-full justify-between">
          <div className="flex items-center gap-2">
            {request.can_edit && (
              <>
                <Button
                  variant="outline"
                  onClick={handleCancel}
                  disabled={isLoading}
                  className="text-red-500 border-red-500/30 hover:bg-red-500/10"
                >
                  {isLoading && actionType === 'cancel' && (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  )}
                  <XCircle className="w-4 h-4 mr-2" />
                  Cancelar
                </Button>
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={onClose}>
              Fechar
            </Button>
            {request.can_edit && (
              <>
                <Button variant="outline" onClick={onEdit}>
                  <Edit2 className="w-4 h-4 mr-2" />
                  Editar
                </Button>
                {request.can_submit && (
                  <Button
                    variant="primary"
                    onClick={handleSubmit}
                    disabled={isLoading}
                  >
                    {isLoading && actionType === 'submit' && (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    )}
                    <Send className="w-4 h-4 mr-2" />
                    Submeter
                  </Button>
                )}
              </>
            )}
          </div>
        </div>
      </ModalFooter>
    </Modal>
  );
}
