import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import React from 'react';
import { reducer, toast, useToast } from '../use-toast';

describe('use-toast', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('reducer', () => {
    it('deve adicionar toast com ADD_TOAST', () => {
      const initialState = { toasts: [] };
      const action = {
        type: 'ADD_TOAST' as const,
        toast: { id: '1', title: 'Teste', open: true },
      };

      const newState = reducer(initialState, action);

      expect(newState.toasts).toHaveLength(1);
      expect(newState.toasts[0]?.id).toBe('1');
      expect(newState.toasts[0]?.title).toBe('Teste');
    });

    it('deve limitar toasts ao TOAST_LIMIT', () => {
      const initialState = {
        toasts: [
          { id: '1', title: 'Toast 1', open: true },
        ]
      };
      const action = {
        type: 'ADD_TOAST' as const,
        toast: { id: '2', title: 'Toast 2', open: true },
      };

      const newState = reducer(initialState, action);

      expect(newState.toasts).toHaveLength(1);
      expect(newState.toasts[0]?.id).toBe('2');
    });

    it('deve atualizar toast com UPDATE_TOAST', () => {
      const initialState = {
        toasts: [{ id: '1', title: 'Original', open: true }]
      };
      const action = {
        type: 'UPDATE_TOAST' as const,
        toast: { id: '1', title: 'Atualizado' },
      };

      const newState = reducer(initialState, action);

      expect(newState.toasts[0]?.title).toBe('Atualizado');
    });

    it('deve manter outros toasts ao atualizar', () => {
      const initialState = {
        toasts: [
          { id: '1', title: 'Toast 1', open: true },
          { id: '2', title: 'Toast 2', open: true },
        ]
      };
      const action = {
        type: 'UPDATE_TOAST' as const,
        toast: { id: '1', title: 'Atualizado' },
      };

      const newState = reducer(initialState, action);

      expect(newState.toasts[0]?.title).toBe('Atualizado');
      expect(newState.toasts[1]?.title).toBe('Toast 2');
    });

    it('deve fechar toast com DISMISS_TOAST e id específico', () => {
      const initialState = {
        toasts: [
          { id: '1', title: 'Toast 1', open: true },
          { id: '2', title: 'Toast 2', open: true },
        ]
      };
      const action = {
        type: 'DISMISS_TOAST' as const,
        toastId: '1',
      };

      const newState = reducer(initialState, action);

      expect(newState.toasts[0]?.open).toBe(false);
      expect(newState.toasts[1]?.open).toBe(true);
    });

    it('deve fechar todos os toasts com DISMISS_TOAST sem id', () => {
      const initialState = {
        toasts: [
          { id: '1', title: 'Toast 1', open: true },
          { id: '2', title: 'Toast 2', open: true },
        ]
      };
      const action = {
        type: 'DISMISS_TOAST' as const,
      };

      const newState = reducer(initialState, action);

      expect(newState.toasts[0]?.open).toBe(false);
      expect(newState.toasts[1]?.open).toBe(false);
    });

    it('deve remover toast específico com REMOVE_TOAST', () => {
      const initialState = {
        toasts: [
          { id: '1', title: 'Toast 1', open: true },
          { id: '2', title: 'Toast 2', open: true },
        ]
      };
      const action = {
        type: 'REMOVE_TOAST' as const,
        toastId: '1',
      };

      const newState = reducer(initialState, action);

      expect(newState.toasts).toHaveLength(1);
      expect(newState.toasts[0]?.id).toBe('2');
    });

    it('deve remover todos os toasts com REMOVE_TOAST sem id', () => {
      const initialState = {
        toasts: [
          { id: '1', title: 'Toast 1', open: true },
          { id: '2', title: 'Toast 2', open: true },
        ]
      };
      const action = {
        type: 'REMOVE_TOAST' as const,
      };

      const newState = reducer(initialState, action);

      expect(newState.toasts).toHaveLength(0);
    });
  });

  describe('toast function', () => {
    it('deve criar toast com id, dismiss e update', () => {
      const result = toast({ title: 'Teste' });

      expect(result.id).toBeDefined();
      expect(typeof result.dismiss).toBe('function');
      expect(typeof result.update).toBe('function');
    });

    it('deve criar múltiplos toasts com ids diferentes', () => {
      const toast1 = toast({ title: 'Toast 1' });
      const toast2 = toast({ title: 'Toast 2' });

      expect(toast1.id).not.toBe(toast2.id);
    });

    it('deve chamar dismiss quando onOpenChange recebe false', async () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.toast({ title: 'Teste' });
      });

      await waitFor(() => {
        expect(result.current.toasts).toHaveLength(1);
      });

      // Simular fechamento do toast
      const toastComponent = result.current.toasts[0];
      act(() => {
        toastComponent?.onOpenChange?.(false);
      });

      // O toast deve ser marcado como não aberto
      await waitFor(() => {
        expect(result.current.toasts[0]?.open).toBe(false);
      });
    });
  });

  describe('useToast hook', () => {
    it('deve retornar estado atual dos toasts', async () => {
      const { result } = renderHook(() => useToast());

      // Limpa qualquer estado residual de outros testes
      act(() => {
        result.current.dismiss();
      });

      await waitFor(() => {
        // Apenas verifica que o hook retorna um array
        expect(Array.isArray(result.current.toasts)).toBe(true);
      });
    });

    it('deve adicionar toast via toast function', async () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.toast({ title: 'Teste' });
      });

      await waitFor(() => {
        expect(result.current.toasts).toHaveLength(1);
        expect(result.current.toasts[0]?.title).toBe('Teste');
      });
    });

    it('deve remover todos os toasts quando dismiss é chamado sem id', async () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.toast({ title: 'Toast 1' });
        result.current.toast({ title: 'Toast 2' });
      });

      await waitFor(() => {
        expect(result.current.toasts).toHaveLength(1); // limitado a 1
      });

      act(() => {
        result.current.dismiss();
      });

      await waitFor(() => {
        expect(result.current.toasts[0]?.open).toBe(false);
      });
    });

    it('deve remover toast específico quando dismiss é chamado com id', async () => {
      const { result } = renderHook(() => useToast());
      let toastId: string;

      act(() => {
        const t = result.current.toast({ title: 'Teste' });
        toastId = t.id;
      });

      await waitFor(() => {
        expect(result.current.toasts).toHaveLength(1);
      });

      act(() => {
        result.current.dismiss(toastId!);
      });

      await waitFor(() => {
        expect(result.current.toasts[0]?.open).toBe(false);
      });
    });
  });

  describe('addToRemoveQueue', () => {
    it('deve remover toast após delay', async () => {
      const { result } = renderHook(() => useToast());

      act(() => {
        result.current.toast({ title: 'Teste' });
      });

      await waitFor(() => {
        expect(result.current.toasts).toHaveLength(1);
      });

      // Dismiss o toast
      act(() => {
        result.current.dismiss();
      });

      // Avançar o timer para remover o toast
      act(() => {
        vi.advanceTimersByTime(1000100); // TOAST_REMOVE_DELAY + um pouco mais
      });

      // O toast deve ser removido
      await waitFor(() => {
        expect(result.current.toasts).toHaveLength(0);
      });
    });
  });
});
