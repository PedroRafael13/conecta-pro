'use client';

import { AlertCircle, Loader2, CheckCircle, AlertTriangle } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { getErrorMessage } from '@/lib/api';
import {
  OCCURRENCE_TYPE_LABELS,
  OCCURRENCE_SEVERITY_LABELS,
  type Occurrence,
} from '@/types/operacional';
import { occurrencesService } from '@/services/occurrences';

interface OccurrenceResolveModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  occurrence: Occurrence | null;
}

interface FormData {
  resolution_notes: string;
  corrective_action: string;
}

const initialFormData: FormData = {
  resolution_notes: '',
  corrective_action: '',
};

// Sugestoes de acoes corretivas baseadas na severidade
const CORRECTIVE_ACTION_SUGGESTIONS: Record<string, string[]> = {
  leve: [
    'Advertencia verbal aplicada',
    'Orientacao e esclarecimento sobre procedimentos',
    'Conversa de conscientizacao com o funcionario',
  ],
  moderada: [
    'Advertencia escrita aplicada',
    'Treinamento de reciclagem agendado',
    'Assinatura de termo de compromisso',
  ],
  grave: [
    'Suspensao de 1 a 3 dias aplicada',
    'Realocacao temporaria de posto',
    'Acompanhamento disciplinar iniciado',
  ],
  gravissima: [
    'Encaminhado para analise do RH',
    'Processo disciplinar instaurado',
    'Suspensao preventiva aplicada',
  ],
};

export function OccurrenceResolveModal({
  isOpen,
  onClose,
  onSuccess,
  occurrence,
}: OccurrenceResolveModalProps) {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setFormData(initialFormData);
      setError(null);
    }
  }, [isOpen]);

  if (!occurrence) return null;

  const handleChange = (
    e: React.ChangeEvent<HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setFormData((prev) => ({
      ...prev,
      corrective_action: prev.corrective_action
        ? `${prev.corrective_action}\n${suggestion}`
        : suggestion,
    }));
  };

  const validateForm = (): boolean => {
    if (!formData.resolution_notes.trim()) {
      setError('Observacoes da resolucao sao obrigatorias');
      return false;
    }
    return true;
  };

  const handleResolve = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    setError(null);

    try {
      await occurrencesService.resolve(occurrence.id, {
        resolution_notes: formData.resolution_notes,
        corrective_action: formData.corrective_action || undefined,
      });

      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const suggestions = CORRECTIVE_ACTION_SUGGESTIONS[occurrence.severity] || [];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Resolver Ocorrencia"
      description={`Resolvendo ${occurrence.code}`}
      size="lg"
    >
      <div className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 flex items-center gap-2 text-red-500 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Resumo da Ocorrencia */}
        <div className="bg-[hsl(var(--muted))] rounded-lg p-4 space-y-2">
          <div className="flex items-center gap-2 text-[hsl(var(--foreground))]">
            <AlertTriangle className="w-4 h-4 text-orange-500" />
            <span className="font-medium">{occurrence.title}</span>
          </div>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            <strong>Tipo:</strong> {OCCURRENCE_TYPE_LABELS[occurrence.occurrence_type]}
          </p>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            <strong>Severidade:</strong> {OCCURRENCE_SEVERITY_LABELS[occurrence.severity]}
          </p>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            <strong>Funcionario:</strong> {occurrence.employee_name || 'N/A'}
          </p>
        </div>

        {/* Observacoes da Resolucao */}
        <div>
          <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
            Observacoes da Resolucao *
          </label>
          <textarea
            name="resolution_notes"
            value={formData.resolution_notes}
            onChange={handleChange}
            placeholder="Descreva como a ocorrencia foi tratada, acoes tomadas, conversas realizadas..."
            rows={4}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none text-sm"
           aria-label="Descreva como a ocorrencia foi tratada, acoes tomadas, conversas realizadas..." />
        </div>

        {/* Acao Corretiva */}
        <div>
          <label className="block text-sm font-medium text-[hsl(var(--foreground))] mb-1">
            Acao Corretiva Aplicada
          </label>
          <textarea
            name="corrective_action"
            value={formData.corrective_action}
            onChange={handleChange}
            placeholder="Descreva a acao corretiva ou medida disciplinar aplicada..."
            rows={3}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] resize-none text-sm"
           aria-label="Descreva a acao corretiva ou medida disciplinar aplicada..." />
        </div>

        {/* Sugestoes */}
        {suggestions.length > 0 && (
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-2">
              Sugestoes para severidade &quot;{occurrence.severity}&quot;:
            </label>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((suggestion, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="px-3 py-1.5 text-xs rounded-full bg-[hsl(var(--muted))] text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]/80 transition-colors border border-[hsl(var(--border))]"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Aviso */}
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 text-sm text-yellow-400">
          <p>
            <strong>Atencao:</strong> Ao resolver a ocorrencia, o status sera alterado para &quot;Resolvida&quot;.
            Esta acao sera registrada com seu usuario e data/hora.
          </p>
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isLoading}>
          Cancelar
        </Button>

        <Button
          variant="primary"
          onClick={handleResolve}
          disabled={isLoading}
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <CheckCircle className="w-4 h-4 mr-2" />
          )}
          Resolver Ocorrencia
        </Button>
      </ModalFooter>
    </Modal>
  );
}
