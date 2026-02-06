'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

export interface UseFetchOptions extends RequestInit {
  enabled?: boolean;
  useCache?: boolean;
  cacheTime?: number; // em milissegundos
  refetchInterval?: number; // em milissegundos
  onSuccess?: (data: unknown) => void;
  onError?: (error: Error) => void;
}

interface UseFetchState<T> {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
  isSuccess: boolean;
}

export interface UseFetchReturn<T> extends UseFetchState<T> {
  refetch: () => Promise<void>;
  mutate: (data: T | ((prev: T | null) => T)) => void;
}

// Cache simples em memória
const cache = new Map<string, { data: unknown; timestamp: number }>();

export function useFetch<T = unknown>(
  url: string | null,
  options: UseFetchOptions = {}
): UseFetchReturn<T> {
  const {
    enabled = true,
    useCache = false,
    cacheTime = 5 * 60 * 1000, // 5 minutos padrão
    refetchInterval,
    onSuccess,
    onError,
    ...fetchOptions
  } = options;

  const [state, setState] = useState<UseFetchState<T>>({
    data: null,
    isLoading: false,
    error: null,
    isSuccess: false,
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const executeFetch = useCallback(async () => {
    if (!url || !enabled) return;

    // Cancelar requisição anterior
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    // Verificar cache
    if (useCache) {
      const cached = cache.get(url);
      if (cached && Date.now() - cached.timestamp < cacheTime) {
        setState({
          data: cached.data as T,
          isLoading: false,
          error: null,
          isSuccess: true,
        });
        onSuccess?.(cached.data);
        return;
      }
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Salvar no cache
      if (useCache) {
        cache.set(url, { data, timestamp: Date.now() });
      }

      setState({
        data,
        isLoading: false,
        error: null,
        isSuccess: true,
      });

      onSuccess?.(data);
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return;
      }

      const errorObj = error instanceof Error ? error : new Error(String(error));

      setState({
        data: null,
        isLoading: false,
        error: errorObj,
        isSuccess: false,
      });

      onError?.(errorObj);
    }
  }, [url, enabled, useCache, cacheTime, fetchOptions, onSuccess, onError]);

  // Função para forçar refetch
  const refetch = useCallback(async () => {
    if (url && useCache) {
      cache.delete(url);
    }
    await executeFetch();
  }, [executeFetch, url, useCache]);

  // Função para atualizar dados localmente
  const mutate = useCallback((newData: T | ((prev: T | null) => T)) => {
    setState(prev => ({
      ...prev,
      data: newData instanceof Function ? newData(prev.data) : newData,
    }));
  }, []);

  // Executar fetch quando URL ou opções mudarem
  useEffect(() => {
    executeFetch();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [executeFetch]);

  // Configurar refetch interval
  useEffect(() => {
    if (refetchInterval && enabled) {
      intervalRef.current = setInterval(() => {
        executeFetch();
      }, refetchInterval);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [refetchInterval, enabled, executeFetch]);

  return {
    ...state,
    refetch,
    mutate,
  };
}

// Funções auxiliares para cache
export function invalidateCache(urlPattern: string | RegExp): void {
  if (typeof urlPattern === 'string') {
    cache.delete(urlPattern);
  } else {
    for (const key of cache.keys()) {
      if (urlPattern.test(key)) {
        cache.delete(key);
      }
    }
  }
}

export function clearCache(): void {
  cache.clear();
}

export default useFetch;
