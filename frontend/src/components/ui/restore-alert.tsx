'use client';

;
import { AlertCircle, RotateCcw, Trash2 } from 'lucide-react';
import { Button } from './button';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface RestoreAlertProps {
  onRestore: () => void;
  onDiscard: () => void;
  savedAt?: Date | null;
}

/**
 * Componente de alerta para restaurar ou descartar rascunho
 *
 * @example
 * <RestoreAlert
 *   onRestore={() => {
 *     const draft = autoSave.restore();
 *     if (draft) setFormData(draft);
 *   }}
 *   onDiscard={() => autoSave.clear()}
 *   savedAt={autoSave.lastSaved}
 * />
 */
export function RestoreAlert({ onRestore, onDiscard, savedAt }: RestoreAlertProps) {
  const timeAgo = savedAt
    ? formatDistanceToNow(savedAt, { addSuffix: true, locale: ptBR })
    : 'recentemente';

  return (
    <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 mb-4">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-blue-500 mb-1">Rascunho encontrado</h4>
          <p className="text-xs text-[hsl(var(--muted-foreground))] mb-3">
            Existe um rascunho salvo {timeAgo}. Deseja restaurar?
          </p>
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              size="sm"
              variant="primary"
              onClick={onRestore}
              className="h-8"
            >
              <RotateCcw className="w-3 h-3 mr-1" />
              Restaurar
            </Button>
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={onDiscard}
              className="h-8"
            >
              <Trash2 className="w-3 h-3 mr-1" />
              Descartar
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
