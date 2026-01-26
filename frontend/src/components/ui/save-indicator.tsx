'use client';

import { Check, Loader2, AlertCircle, RotateCcw } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface SaveIndicatorProps {
  saving: boolean;
  lastSaved: Date | null;
  error: string | null;
  onRetry?: () => void;
}

/**
 * Componente indicador de status de salvamento
 *
 * @example
 * <SaveIndicator
 *   saving={autoSave.saving}
 *   lastSaved={autoSave.lastSaved}
 *   error={autoSave.error}
 * />
 */
export function SaveIndicator({ saving, lastSaved, error, onRetry }: SaveIndicatorProps) {
  if (error) {
    return (
      <div className="flex items-center gap-2 text-xs text-red-500">
        <AlertCircle className="w-4 h-4" />
        <span>Erro ao salvar</span>
        {onRetry && (
          <button
            onClick={onRetry}
            className="underline hover:no-underline"
            type="button"
          >
            Tentar novamente
          </button>
        )}
      </div>
    );
  }

  if (saving) {
    return (
      <div className="flex items-center gap-2 text-xs text-[hsl(var(--muted-foreground))]">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span>Salvando rascunho...</span>
      </div>
    );
  }

  if (lastSaved) {
    const timeAgo = formatDistanceToNow(lastSaved, { addSuffix: true, locale: ptBR });

    return (
      <div className="flex items-center gap-2 text-xs text-green-500">
        <Check className="w-4 h-4" />
        <span>Rascunho salvo {timeAgo}</span>
      </div>
    );
  }

  return null;
}
