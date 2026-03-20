'use client';

import { useEffect, useRef, useCallback, useState } from 'react';

export interface UseAutoSaveOptions<T> {
  key: string;
  data: T;
  onSave?: (data: T) => Promise<void>;
  debounceMs?: number;
  enabled?: boolean;
  excludeFields?: (keyof T)[];
}

export interface UseAutoSaveReturn {
  saving: boolean;
  lastSaved: Date | null;
  error: string | null;
  restore: () => any | null;
  clear: () => void;
  hasDraft: boolean;
}

const DRAFT_PREFIX = 'draft_';
const DRAFT_TIMESTAMP_PREFIX = 'draft_ts_';
const DRAFT_EXPIRY_DAYS = 7;

/**
 * Hook para auto-save de formularios com localStorage e opcao de backup no backend
 *
 * @example
 * const autoSave = useAutoSave({
 *   key: 'posto_form',
 *   data: formData,
 *   debounceMs: 2000,
 *   enabled: isOpen && !isEditing,
 *   excludeFields: ['password', 'token']
 * });
 */
export function useAutoSave<T extends Record<string, any>>({
  key,
  data,
  onSave,
  debounceMs = 2000,
  enabled = true,
  excludeFields = [],
}: UseAutoSaveOptions<T>): UseAutoSaveReturn {
  const [saving, setSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hasDraft, setHasDraft] = useState(false);

  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastDataRef = useRef<string>('');

  const storageKey = `${DRAFT_PREFIX}${key}`;
  const timestampKey = `${DRAFT_TIMESTAMP_PREFIX}${key}`;

  // Verificar se existe rascunho ao montar
  useEffect(() => {
    const draft = localStorage.getItem(storageKey);
    setHasDraft(!!draft);
  }, [storageKey]);

  // Funcao para limpar campos sensiveis
  const sanitizeData = useCallback((rawData: T): Partial<T> => {
    // Criar objeto sem os campos excluidos usando reduce
    const allFieldsToExclude = new Set([
      ...excludeFields,
      'password',
      'senha',
      'token',
      'secret',
      'api_key',
      'apiKey',
    ]);

    return Object.entries(rawData).reduce((acc, [key, value]) => {
      if (!allFieldsToExclude.has(key)) {
        acc[key as keyof T] = value;
      }
      return acc;
    }, {} as Partial<T>);
  }, [excludeFields]);

  // Funcao para salvar no localStorage
  const saveToLocalStorage = useCallback(async (dataToSave: T) => {
    try {
      setSaving(true);
      setError(null);

      const sanitized = sanitizeData(dataToSave);
      const serialized = JSON.stringify(sanitized);

      // Nao salvar se os dados nao mudaram
      if (serialized === lastDataRef.current) {
        setSaving(false);
        return;
      }

      localStorage.setItem(storageKey, serialized);
      localStorage.setItem(timestampKey, new Date().toISOString());

      lastDataRef.current = serialized;
      setLastSaved(new Date());

      // Opcional: salvar no backend
      if (onSave) {
        await onSave(sanitized as T);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao salvar');
    } finally {
      setSaving(false);
    }
  }, [storageKey, timestampKey, sanitizeData, onSave]);

  // Auto-save com debounce
  useEffect(() => {
    if (!enabled) return;

    // Limpar timer anterior
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Criar novo timer
    debounceTimerRef.current = setTimeout(() => {
      saveToLocalStorage(data);
    }, debounceMs);

    // Cleanup
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [data, enabled, debounceMs, saveToLocalStorage]);

  // Funcao para restaurar rascunho
  const restore = useCallback((): any | null => {
    try {
      const draft = localStorage.getItem(storageKey);
      const timestamp = localStorage.getItem(timestampKey);

      if (!draft) return null;

      // Verificar se o rascunho expirou
      if (timestamp) {
        const savedDate = new Date(timestamp);
        const now = new Date();
        const daysDiff = (now.getTime() - savedDate.getTime()) / (1000 * 60 * 60 * 24);

        if (daysDiff > DRAFT_EXPIRY_DAYS) {
          // Rascunho expirado, limpar
          localStorage.removeItem(storageKey);
          localStorage.removeItem(timestampKey);
          return null;
        }
      }

      const parsed = JSON.parse(draft);
      setLastSaved(timestamp ? new Date(timestamp) : null);
      return parsed;
    } catch (err) {
      return null;
    }
  }, [storageKey, timestampKey]);

  // Funcao para limpar rascunho
  const clear = useCallback(() => {
    localStorage.removeItem(storageKey);
    localStorage.removeItem(timestampKey);
    setLastSaved(null);
    setHasDraft(false);
    lastDataRef.current = '';
  }, [storageKey, timestampKey]);

  return {
    saving,
    lastSaved,
    error,
    restore,
    clear,
    hasDraft,
  };
}

/**
 * Funcao utilitaria para limpar rascunhos antigos
 * Deve ser chamada na inicializacao da aplicacao
 */
export function cleanupExpiredDrafts(): void {
  try {
    const now = new Date();
    const keysToRemove: string[] = [];

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);

      if (key?.startsWith(DRAFT_TIMESTAMP_PREFIX)) {
        const timestamp = localStorage.getItem(key);
        if (timestamp) {
          const savedDate = new Date(timestamp);
          const daysDiff = (now.getTime() - savedDate.getTime()) / (1000 * 60 * 60 * 24);

          if (daysDiff > DRAFT_EXPIRY_DAYS) {
            keysToRemove.push(key);
            // Remover tambem o draft correspondente
            const draftKey = key.replace(DRAFT_TIMESTAMP_PREFIX, DRAFT_PREFIX);
            keysToRemove.push(draftKey);
          }
        }
      }
    }

    // Remover chaves expiradas
    keysToRemove.forEach((key) => localStorage.removeItem(key));

    // Rascunhos expirados removidos silenciosamente
  } catch {
    // cleanup failed silently
  }
}
