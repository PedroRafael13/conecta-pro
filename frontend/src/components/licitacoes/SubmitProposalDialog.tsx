'use client';

import { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface SubmitProposalDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (observacoes?: string) => Promise<void>;
  proposalNumber?: string;
  isSubmitting?: boolean;
}

export function SubmitProposalDialog({
  isOpen,
  onClose,
  onConfirm,
  proposalNumber,
  isSubmitting = false,
}: SubmitProposalDialogProps) {
  const [observacoes, setObservacoes] = useState('');

  const handleConfirm = async () => {
    await onConfirm(observacoes || undefined);
    setObservacoes('');
  };

  const handleCancel = () => {
    setObservacoes('');
    onClose();
  };

  return (
    <AlertDialog open={isOpen} onOpenChange={onClose}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle className="flex items-center gap-2">
            <Send className="h-5 w-5 text-blue-600" />
            Submeter Proposta
          </AlertDialogTitle>
          <AlertDialogDescription>
            {proposalNumber ? (
              <>
                Deseja submeter a proposta <strong>{proposalNumber}</strong>{' '}
                para análise?
              </>
            ) : (
              'Deseja submeter esta proposta para análise?'
            )}
            <br />
            <br />
            Esta ação irá alterar o status da proposta e notificará os
            responsáveis pela análise.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="space-y-2 py-4">
          <Label htmlFor="observacoes">
            Observações (opcional)
          </Label>
          <Textarea
            id="observacoes"
            placeholder="Adicione observações sobre esta submissão..."
            value={observacoes}
            onChange={(e) => setObservacoes(e.target.value)}
            rows={4}
            disabled={isSubmitting}
          />
        </div>

        <AlertDialogFooter>
          <AlertDialogCancel onClick={handleCancel} disabled={isSubmitting}>
            Cancelar
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            disabled={isSubmitting}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Submetendo...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Submeter Proposta
              </>
            )}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
