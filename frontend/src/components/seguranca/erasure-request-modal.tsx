'use client';

import { Loader2, AlertTriangle } from 'lucide-react';
import { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
;

interface ErasureRequestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    holder_name: string;
    holder_email: string;
    reason: string;
  }) => void;
  isLoading?: boolean;
  erasureType: 'full' | 'personal' | 'transactional';
}

const typeLabels: Record<string, string> = {
  full: 'Exclusao Completa',
  personal: 'Exclusao de Dados Pessoais',
  transactional: 'Exclusao de Dados Transacionais',
};

const typeDescriptions: Record<string, string> = {
  full: 'Remove todos os dados do titular, incluindo historico e transacoes. Esta acao e irreversivel.',
  personal:
    'Remove dados de identificacao pessoal, mantendo transacoes anonimizadas para compliance.',
  transactional:
    'Remove dados transacionais, mantendo apenas dados necessarios para cumprimento de obrigacoes legais.',
};

export function ErasureRequestModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
  erasureType,
}: ErasureRequestModalProps) {
  const [formData, setFormData] = useState({
    holder_name: '',
    holder_email: '',
    reason: '',
  });
  const [confirmed, setConfirmed] = useState(false);

  const handleSubmit = () => {
    onSubmit(formData);
    setFormData({ holder_name: '', holder_email: '', reason: '' });
    setConfirmed(false);
  };

  const handleClose = () => {
    setFormData({ holder_name: '', holder_email: '', reason: '' });
    setConfirmed(false);
    onClose();
  };

  const isValid =
    formData.holder_name.trim().length > 0 &&
    formData.holder_email.trim().length > 0 &&
    formData.reason.trim().length >= 10 &&
    confirmed;

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={typeLabels[erasureType] || 'Nova Solicitacao'}
      description={typeDescriptions[erasureType]}
      size="lg"
    >
      <div className="space-y-4">
        {erasureType === 'full' && (
          <div className="flex items-start gap-3 p-3 rounded-lg bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-900">
            <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-red-700 dark:text-red-400">
              <p className="font-semibold">Atencao: Acao irreversivel</p>
              <p className="mt-1">
                A exclusao completa remove permanentemente todos os dados do
                titular. Esta acao nao pode ser desfeita.
              </p>
            </div>
          </div>
        )}

        <div className="space-y-2">
          <Label htmlFor="erasure-holder-name">Nome do Titular</Label>
          <Input
            id="erasure-holder-name"
            value={formData.holder_name}
            onChange={(e) =>
              setFormData({ ...formData, holder_name: e.target.value })
            }
            placeholder="Nome completo do titular dos dados"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="erasure-holder-email">Email do Titular</Label>
          <Input
            id="erasure-holder-email"
            type="email"
            value={formData.holder_email}
            onChange={(e) =>
              setFormData({ ...formData, holder_email: e.target.value })
            }
            placeholder="email@exemplo.com.br"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="erasure-reason">Motivo</Label>
          <Textarea
            id="erasure-reason"
            value={formData.reason}
            onChange={(e) =>
              setFormData({ ...formData, reason: e.target.value })
            }
            placeholder="Descreva o motivo da solicitacao de exclusao (minimo 10 caracteres)"
            rows={3}
          />
          {formData.reason.length > 0 && formData.reason.length < 10 && (
            <p className="text-xs text-red-500">
              Motivo deve ter no minimo 10 caracteres ({formData.reason.length}/10)
            </p>
          )}
        </div>

        <div className="flex items-start gap-2 pt-2">
          <input
            type="checkbox"
            id="erasure-confirm"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
            className="rounded mt-1"
          />
          <Label htmlFor="erasure-confirm" className="text-sm font-normal cursor-pointer">
            Confirmo que esta acao e irreversivel e que os dados do titular
            serao permanentemente removidos conforme a LGPD Art. 18.
          </Label>
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={handleClose} disabled={isLoading}>
          Cancelar
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={!isValid || isLoading}
          className={
            erasureType === 'full'
              ? 'bg-red-500 hover:bg-red-600 text-white'
              : undefined
          }
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Processando...
            </>
          ) : (
            'Solicitar Exclusao'
          )}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
