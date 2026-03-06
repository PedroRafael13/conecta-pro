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

  describe('Sanitização de Dados Sensíveis', () => {
    it('deve remover campos password automaticamente', () => {
      renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John', password: 'secret123' },
        })
      );

      act(() => {
        vi.advanceTimersByTime(2000);
      });

      const saved = JSON.parse(localStorage.getItem('draft_test-form')!);
      expect(saved.password).toBeUndefined();
      expect(saved.name).toBe('John');
    });

    it('deve remover campos token automaticamente', () => {
      renderHook(() =>
        useAutoSave({
          key: 'test-form',
          data: { name: 'John', token: 'abc123', api_key: 'xyz789' },
        })
      );

      act(() => {
        vi.advanceTimersByTime(2000);
      });

      const saved = JSON.parse(localStorage.getItem('draft_test-form')!);
      expect(saved.token).toBeUndefined();
      expect(saved.api_key).toBeUndefined();
      expect(saved.name).toBe('John');
    });
  });

  describe('Sincronização entre Abas', () => {
    it('deve sincronizar via storage event', () => {
      renderHook(() =>
        useAutoSave({
          key: 'sync-test',
          data: { name: 'Initial' },
        })
      );

      act(() => {
        vi.advanceTimersByTime(2000);
      });

      // Primeiro salva o valor inicial
      expect(localStorage.getItem('draft_sync-test')).toBeTruthy();

      act(() => {
        // Simula mudança de outra aba
        localStorage.setItem('draft_sync-test', JSON.stringify({ name: 'Updated from other tab' }));
        const event = new StorageEvent('storage', {
          key: 'draft_sync-test',
          newValue: JSON.stringify({ name: 'Updated from other tab' }),
        });
        window.dispatchEvent(event);
      });

      // Deve continuar existindo
      expect(localStorage.getItem('draft_sync-test')).toBeTruthy();
    });
  });

  describe('Restore - Limpeza de Rascunhos Expirados', () => {
    it('deve remover rascunho expirado ao restaurar', () => {
      const oldDate = new Date();
      oldDate.setDate(oldDate.getDate() - 8); // 8 dias atrás (mais que DRAFT_EXPIRY_DAYS)

      localStorage.setItem('draft_expired-test', JSON.stringify({ name: 'Old' }));
      localStorage.setItem('draft_ts_expired-test', oldDate.toISOString());

      const { result } = renderHook(() =>
        useAutoSave({
          key: 'expired-test',
          data: { name: 'New' },
        })
      );

      let restored: any;
      act(() => {
        restored = result.current.restore();
      });

      expect(restored).toBeNull();
      expect(localStorage.getItem('draft_expired-test')).toBeNull();
      expect(localStorage.getItem('draft_ts_expired-test')).toBeNull();
    });

    it('deve restaurar rascunho não expirado', () => {
      const recentDate = new Date();
      recentDate.setHours(recentDate.getHours() - 2); // 2 horas atrás

      localStorage.setItem('draft_recent-test', JSON.stringify({ name: 'Recent' }));
      localStorage.setItem('draft_ts_recent-test', recentDate.toISOString());

      const { result } = renderHook(() =>
        useAutoSave({
          key: 'recent-test',
          data: { name: 'New' },
        })
      );

      let restored: any;
      act(() => {
        restored = result.current.restore();
      });

      expect(restored).toEqual({ name: 'Recent' });
      expect(localStorage.getItem('draft_recent-test')).toBeTruthy();
    });
  });

  describe('Restore - sem timestamp', () => {
    it('deve restaurar rascunho mesmo sem timestamp', () => {
      // Draft exists but no timestamp key
      localStorage.setItem('draft_no-ts-test', JSON.stringify({ name: 'NoTimestamp' }));
      // Não setando draft_ts_no-ts-test

      const { result } = renderHook(() =>
        useAutoSave({
          key: 'no-ts-test',
          data: { name: 'Current' },
        })
      );

      let restored: any;
      act(() => {
        restored = result.current.restore();
      });

      expect(restored).toEqual({ name: 'NoTimestamp' });
      // lastSaved deve ser null porque não tem timestamp
      expect(result.current.lastSaved).toBeNull();
    });
  });

  describe('cleanupExpiredDrafts - timestamp key sem valor', () => {
    it('deve ignorar timestamp keys sem valor', () => {
      // Set a timestamp key with null value (getItem returns null)
      localStorage.setItem('draft_ts_null-test', '');
      localStorage.setItem('draft_null-test', JSON.stringify({ data: 'test' }));

      // Should not throw and should not remove the draft
      expect(() => cleanupExpiredDrafts()).not.toThrow();
    });
  });

  describe('Error Handling no saveToLocalStorage', () => {
    it('deve setar mensagem de erro quando saveToLocalStorage falha com Error instance', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
        throw new Error('Storage full');
      });

      const { result } = renderHook(() =>
        useAutoSave({
          key: 'error-test',
          data: { name: 'John' },
        })
      );

      act(() => {
        vi.advanceTimersByTime(2000);
      });

      expect(result.current.error).toBe('Storage full');
      expect(consoleSpy).toHaveBeenCalled();

      consoleSpy.mockRestore();
      setItemSpy.mockRestore();
    });

    it('deve setar mensagem genérica quando saveToLocalStorage falha com non-Error', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
        throw 'string error'; // non-Error throw
      });

      const { result } = renderHook(() =>
        useAutoSave({
          key: 'error-test-2',
          data: { name: 'John' },
        })
      );

      act(() => {
        vi.advanceTimersByTime(2000);
      });

      expect(result.current.error).toBe('Erro ao salvar');
      expect(consoleSpy).toHaveBeenCalled();

      consoleSpy.mockRestore();
      setItemSpy.mockRestore();
    });
  });

  describe('cleanupExpiredDrafts - Error Handling', () => {
    it('deve lidar com erro no cleanupExpiredDrafts', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const keySpy = vi.spyOn(Storage.prototype, 'key').mockImplementation(() => {
        throw new Error('Storage access error');
      });
      // Mock length to trigger the loop
      Object.defineProperty(localStorage, 'length', { value: 1, writable: true, configurable: true });

      // Should not throw
      expect(() => cleanupExpiredDrafts()).not.toThrow();
      expect(consoleSpy).toHaveBeenCalled();

      consoleSpy.mockRestore();
      keySpy.mockRestore();
      Object.defineProperty(localStorage, 'length', { value: 0, writable: true, configurable: true });
    });
  });

  describe('Error Handling no Restore', () => {
    it('deve retornar null quando JSON.parse falha', () => {
      localStorage.setItem('draft_invalid-json', 'not-json-{{{');
      localStorage.setItem('draft_ts_invalid-json', new Date().toISOString());

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const { result } = renderHook(() =>
        useAutoSave({
          key: 'invalid-json',
          data: { name: 'New' },
        })
      );

      let restored: any;
      act(() => {
        restored = result.current.restore();
      });

      expect(restored).toBeNull();
      expect(consoleSpy).toHaveBeenCalled();

      consoleSpy.mockRestore();
    });
  });
});
