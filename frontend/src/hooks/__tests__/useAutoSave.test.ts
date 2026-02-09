import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAutoSave, cleanupExpiredDrafts } from '../useAutoSave';

describe('useAutoSave', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    localStorage.clear();
  });

  describe('Estado Inicial', () => {
    it('deve iniciar com valores padrão', () => {
      const { result } = renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John' },
        })
      );

      expect(result.current.saving).toBe(false);
      expect(result.current.lastSaved).toBeNull();
      expect(result.current.error).toBeNull();
      expect(result.current.hasDraft).toBe(false);
    });

    it('deve verificar rascunho existente ao montar', () => {
      localStorage.setItem('draft_test-form', JSON.stringify({ name: 'Jane' }));

      const { result } = renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John' },
        })
      );

      expect(result.current.hasDraft).toBe(true);
    });
  });

  describe('Auto-Save', () => {
    it('deve salvar no localStorage após debounce', () => {
      const { result } = renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John' },
          debounceMs: 1000,
        })
      );

      act(() => {
        vi.advanceTimersByTime(1000);
      });

      expect(localStorage.getItem('draft_test-form')).toContain('John');
      expect(result.current.lastSaved).not.toBeNull();
    });

    it('não deve salvar quando enabled é false', () => {
      renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John' },
          enabled: false,
        })
      );

      act(() => {
        vi.advanceTimersByTime(2000);
      });

      expect(localStorage.getItem('draft_test-form')).toBeNull();
    });

    it('deve chamar onSave quando fornecido', async () => {
      const onSave = vi.fn().mockResolvedValue(undefined);

      renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John' },
          onSave,
        })
      );

      act(() => {
        vi.advanceTimersByTime(2000);
      });

      await vi.waitFor(() => {
        expect(onSave).toHaveBeenCalledWith({ name: 'John' });
      });
    });
  });

  describe('Sanitização', () => {
    it('deve remover campos excluídos', () => {
      renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John', password: 'secret', token: 'abc' },
          excludeFields: ['password'],
        })
      );

      act(() => {
        vi.advanceTimersByTime(2000);
      });

      const saved = JSON.parse(localStorage.getItem('draft_test-form')!);
      expect(saved.name).toBe('John');
      expect(saved.password).toBeUndefined();
      expect(saved.token).toBeUndefined(); // token é removido automaticamente
    });

    it('deve remover campos sensíveis automaticamente', () => {
      renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John', api_key: 'secret123', senha: 'pass' },
        })
      );

      act(() => {
        vi.advanceTimersByTime(2000);
      });

      const saved = JSON.parse(localStorage.getItem('draft_test-form')!);
      expect(saved.api_key).toBeUndefined();
      expect(saved.senha).toBeUndefined();
      expect(saved.name).toBe('John');
    });
  });

  describe('Restore', () => {
    it('deve restaurar rascunho existente', () => {
      const timestamp = new Date().toISOString();
      localStorage.setItem('draft_test-form', JSON.stringify({ name: 'Jane' }));
      localStorage.setItem('draft_ts_test-form', timestamp);

      const { result } = renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John' },
        })
      );

      let restored: any;
      act(() => {
        restored = result.current.restore();
      });

      expect(restored).toEqual({ name: 'Jane' });
    });

    it('deve retornar null quando rascunho expirou', () => {
      const oldDate = new Date();
      oldDate.setDate(oldDate.getDate() - 10); // 10 dias atrás

      localStorage.setItem('draft_test-form', JSON.stringify({ name: 'Jane' }));
      localStorage.setItem('draft_ts_test-form', oldDate.toISOString());

      const { result } = renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John' },
        })
      );

      let restored: any;
      act(() => {
        restored = result.current.restore();
      });

      expect(restored).toBeNull();
      expect(localStorage.getItem('draft_test-form')).toBeNull();
    });

    it('deve retornar null quando não há rascunho', () => {
      const { result } = renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John' },
        })
      );

      let restored: any;
      act(() => {
        restored = result.current.restore();
      });

      expect(restored).toBeNull();
    });
  });

  describe('Clear', () => {
    it('deve limpar rascunho', () => {
      localStorage.setItem('draft_test-form', JSON.stringify({ name: 'Jane' }));
      localStorage.setItem('draft_ts_test-form', new Date().toISOString());

      const { result } = renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John' },
        })
      );

      act(() => {
        result.current.clear();
      });

      expect(localStorage.getItem('draft_test-form')).toBeNull();
      expect(localStorage.getItem('draft_ts_test-form')).toBeNull();
      expect(result.current.hasDraft).toBe(false);
      expect(result.current.lastSaved).toBeNull();
    });
  });

  describe('Não salvar quando dados não mudam', () => {
    it('deve ignorar salvamento quando dados são idênticos', () => {
      const { rerender } = renderHook(
        ({ data }) =>
          useAutoSave({
            key: 'test-form',
            data,
          }),
        { initialProps: { data: { name: 'John' } } }
      );

      act(() => {
        vi.advanceTimersByTime(2000);
      });

      const firstSave = localStorage.getItem('draft_test-form');

      // Rerender com mesmos dados
      rerender({ data: { name: 'John' } });

      act(() => {
        vi.advanceTimersByTime(2000);
      });

      // Não deve ter mudado
      expect(localStorage.getItem('draft_test-form')).toBe(firstSave);
    });
  });

  describe('cleanupExpiredDrafts', () => {
    it('deve limpar rascunhos expirados', () => {
      const oldDate = new Date();
      oldDate.setDate(oldDate.getDate() - 10);

      localStorage.setItem('draft_old-form', JSON.stringify({ data: 'old' }));
      localStorage.setItem('draft_ts_old-form', oldDate.toISOString());

      const recentDate = new Date();
      localStorage.setItem('draft_recent-form', JSON.stringify({ data: 'recent' }));
      localStorage.setItem('draft_ts_recent-form', recentDate.toISOString());

      cleanupExpiredDrafts();

      expect(localStorage.getItem('draft_old-form')).toBeNull();
      expect(localStorage.getItem('draft_recent-form')).not.toBeNull();
    });
  });
});
