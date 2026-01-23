'use client';

import { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2, AlertTriangle } from 'lucide-react';
import { SignaturePad } from './signature-pad';
import { disciplinaryService } from '@/lib/services/disciplinary';
import { getErrorMessage } from '@/lib/api';
import {
  ACTION_TYPE_LABELS,
  STATUS_LABELS,
  SIGNER_TYPE_LABELS,
  type DisciplinaryAction,
  type SignerType,
} from '@/types/disciplinary';

interface DisciplinarySignatureModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  action: DisciplinaryAction | null;
  signerType?: SignerType;
}

export function DisciplinarySignatureModal({
  isOpen,
  onClose,
  onSuccess,
  action,
  signerType = 'employee',
}: DisciplinarySignatureModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRefuseForm, setShowRefuseForm] = useState(false);
  const [witness1Name, setWitness1Name] = useState('');
  const [witness1Cpf, setWitness1Cpf] = useState('');
  const [witness2Name, setWitness2Name] = useState('');
  const [witness2Cpf, setWitness2Cpf] = useState('');

  if (!action) return null;

  const handleSign = async (
    signatureData: string,
    location?: { latitude: number; longitude: number }
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      await disciplinaryService.sign(action.id, {
        signature_data: signatureData,
        signer_type: signerType,
        latitude: location?.latitude,
        longitude: location?.longitude,
      });

      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
      setIsLoading(false);
    }
  };

  const handleRefuse = async () => {
    if (!witness1Name.trim() || !witness1Cpf.trim() || !witness2Name.trim() || !witness2Cpf.trim()) {
      setError('Todos os dados das testemunhas são obrigatórios');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await disciplinaryService.refuseSignature(action.id, {
        witness_1_name: witness1Name,
        witness_1_cpf: witness1Cpf,
        witness_2_name: witness2Name,
        witness_2_cpf: witness2Cpf,
      });

      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Assinatura Digital - ${action.code}`}
      description="Assine o documento digitalmente"
      size="lg"
    >
      <div className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Resumo do Documento */}
        <div className="bg-[hsl(var(--muted))] rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-semibold">
              {ACTION_TYPE_LABELS[action.action_type] || action.action_type}
            </span>
            <span className="px-2 py-1 text-xs rounded-full bg-[hsl(var(--background))] text-[hsl(var(--foreground))]">
              {STATUS_LABELS[action.status]}
            </span>
          </div>
          <div className="text-sm text-[hsl(var(--muted-foreground))]">
            <p><strong>Funcionário:</strong> {action.employee_name}</p>
            <p><strong>CPF:</strong> {action.employee_cpf}</p>
            <p><strong>Data do Incidente:</strong> {new Date(action.incident_date).toLocaleDateString('pt-BR')}</p>
          </div>
          <div className="text-sm mt-2 p-2 bg-[hsl(var(--background))] rounded">
            <strong>Motivo:</strong> {action.reason_description.substring(0, 200)}
            {action.reason_description.length > 200 && '...'}
          </div>
        </div>

        {/* Tipo de Signatário */}
        <div className="flex items-center gap-2 text-sm">
          <span className="text-[hsl(var(--muted-foreground))]">Assinando como:</span>
          <span className="px-2 py-1 rounded-full bg-blue-500/10 text-blue-500 text-xs font-medium">
            {SIGNER_TYPE_LABELS[signerType]}
          </span>
        </div>

        {!showRefuseForm ? (
          <>
            {/* Pad de Assinatura */}
            <SignaturePad
              onSign={handleSign}
              onCancel={onClose}
              disabled={isLoading}
              showLocationRequest={true}
              signerName={action.employee_name}
              documentTitle={`${ACTION_TYPE_LABELS[action.action_type]} - ${action.code}`}
            />

            {/* Opção de Recusar (apenas para funcionário) */}
            {signerType === 'employee' && (
              <div className="border-t border-[hsl(var(--border))] pt-4">
                <Button
                  variant="outline"
                  className="w-full text-yellow-500 border-yellow-500/50 hover:bg-yellow-500/10"
                  onClick={() => setShowRefuseForm(true)}
                >
                  <AlertTriangle className="w-4 h-4 mr-2" />
                  Funcionário se recusa a assinar
                </Button>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mt-2 text-center">
                  Em caso de recusa, será necessário registrar duas testemunhas conforme CLT.
                </p>
              </div>
            )}
          </>
        ) : (
          /* Formulário de Recusa com Testemunhas */
          <div className="space-y-4">
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
              <div className="flex items-center gap-2 text-yellow-500 mb-2">
                <AlertTriangle className="w-5 h-5" />
                <span className="font-semibold">Registro de Recusa de Assinatura</span>
              </div>
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                Conforme Art. 477 da CLT, em caso de recusa do funcionário em assinar o documento,
                é necessário o registro de duas testemunhas para validar a ciência da medida.
              </p>
            </div>

            {/* Testemunha 1 */}
            <div className="border border-[hsl(var(--border))] rounded-lg p-4 space-y-3">
              <h4 className="font-medium">Testemunha 1</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="block text-sm text-[hsl(var(--muted-foreground))]">
                    Nome Completo *
                  </label>
                  <Input
                    value={witness1Name}
                    onChange={(e) => setWitness1Name(e.target.value)}
                    placeholder="Nome da testemunha"
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm text-[hsl(var(--muted-foreground))]">
                    CPF *
                  </label>
                  <Input
                    value={witness1Cpf}
                    onChange={(e) => setWitness1Cpf(e.target.value)}
                    placeholder="000.000.000-00"
                  />
                </div>
              </div>
            </div>

            {/* Testemunha 2 */}
            <div className="border border-[hsl(var(--border))] rounded-lg p-4 space-y-3">
              <h4 className="font-medium">Testemunha 2</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="block text-sm text-[hsl(var(--muted-foreground))]">
                    Nome Completo *
                  </label>
                  <Input
                    value={witness2Name}
                    onChange={(e) => setWitness2Name(e.target.value)}
                    placeholder="Nome da testemunha"
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm text-[hsl(var(--muted-foreground))]">
                    CPF *
                  </label>
                  <Input
                    value={witness2Cpf}
                    onChange={(e) => setWitness2Cpf(e.target.value)}
                    placeholder="000.000.000-00"
                  />
                </div>
              </div>
            </div>

            {/* Ações */}
            <ModalFooter>
              <Button
                variant="outline"
                onClick={() => setShowRefuseForm(false)}
                disabled={isLoading}
              >
                Voltar
              </Button>
              <Button
                variant="primary"
                onClick={handleRefuse}
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : null}
                Registrar Recusa com Testemunhas
              </Button>
            </ModalFooter>
          </div>
        )}
      </div>
    </Modal>
  );
}
