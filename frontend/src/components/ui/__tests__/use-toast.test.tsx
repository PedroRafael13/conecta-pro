import { describe, it, expect, vi, beforeEach } from 'vitest';
import { reducer } from '../use-toast';

describe('use-toast', () => {
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
});
