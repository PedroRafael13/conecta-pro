import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useLocalStorage } from '../useLocalStorage';

describe('useLocalStorage', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Get/Set/Remove', () => {
    it('deve retornar valor inicial quando não há valor no localStorage', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
      expect(result.current[0]).toBe('default-value');
    });

    it('deve retornar valor do localStorage quando existe', () => {
      localStorage.setItem('test-key', JSON.stringify('stored-value'));

      const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
      expect(result.current[0]).toBe('stored-value');
    });

    it('deve atualizar valor no localStorage', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', ''));

      act(() => {
        result.current[1]('novo-valor');
      });

      expect(result.current[0]).toBe('novo-valor');
      expect(localStorage.getItem('test-key')).toBe(JSON.stringify('novo-valor'));
    });

    it('deve remover valor do localStorage', () => {
      localStorage.setItem('test-key', JSON.stringify('valor-existente'));

      const { result } = renderHook(() => useLocalStorage('test-key', ''));

      act(() => {
        result.current[2]();
      });

      expect(result.current[0]).toBe(''); // Volta ao valor inicial
      expect(localStorage.getItem('test-key')).toBeNull();
    });

    it('deve permitir atualização com função', () => {
      const { result } = renderHook(() => useLocalStorage('counter', 0));

      act(() => {
        result.current[1]((prev) => prev + 1);
      });

      expect(result.current[0]).toBe(1);
      expect(localStorage.getItem('counter')).toBe('1');
    });

    it('deve manter valores separados para diferentes chaves', () => {
      const { result: result1 } = renderHook(() => useLocalStorage('key1', 'value1'));
      const { result: result2 } = renderHook(() => useLocalStorage('key2', 'value2'));

      expect(result1.current[0]).toBe('value1');
      expect(result2.current[0]).toBe('value2');

      act(() => {
        result1.current[1]('novo-value1');
      });

      expect(result1.current[0]).toBe('novo-value1');
      expect(result2.current[0]).toBe('value2');
    });
  });

  describe('JSON Parsing', () => {
    it('deve armazenar e recuperar objetos', () => {
      const obj = { name: 'John', age: 30 };
      const { result } = renderHook(() => useLocalStorage('user', obj));

      act(() => {
        result.current[1]({ name: 'Jane', age: 25 });
      });

      expect(result.current[0]).toEqual({ name: 'Jane', age: 25 });
      expect(JSON.parse(localStorage.getItem('user')!)).toEqual({ name: 'Jane', age: 25 });
    });

    it('deve armazenar e recuperar arrays', () => {
      const { result } = renderHook(() => useLocalStorage('items', [1, 2, 3]));

      act(() => {
        result.current[1]([4, 5, 6]);
      });

      expect(result.current[0]).toEqual([4, 5, 6]);
      expect(JSON.parse(localStorage.getItem('items')!)).toEqual([4, 5, 6]);
    });

    it('deve armazenar e recuperar números', () => {
      const { result } = renderHook(() => useLocalStorage('count', 0));

      act(() => {
        result.current[1](42);
      });

      expect(result.current[0]).toBe(42);
      expect(localStorage.getItem('count')).toBe('42');
    });

    it('deve armazenar e recuperar booleanos', () => {
      const { result } = renderHook(() => useLocalStorage('flag', false));

      act(() => {
        result.current[1](true);
      });

      expect(result.current[0]).toBe(true);
      expect(localStorage.getItem('flag')).toBe('true');
    });

    it('deve lidar com valores nulos', () => {
      const { result } = renderHook(() => useLocalStorage('nullable', 'value'));

      act(() => {
        result.current[1](null as any);
      });

      expect(result.current[0]).toBeNull();
      expect(localStorage.getItem('nullable')).toBe('null');
    });

    it('deve lidar com dados JSON inválidos no localStorage', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      localStorage.setItem('invalid', 'not-valid-json');

      const { result } = renderHook(() => useLocalStorage('invalid', 'default'));

      // Deve retornar o valor inicial quando JSON é inválido
      expect(result.current[0]).toBe('default');
      expect(consoleSpy).toHaveBeenCalled();

      consoleSpy.mockRestore();
    });
  });

  describe('Eventos de Storage', () => {
    it('deve sincronizar entre abas quando storage event é disparado', () => {
      const { result } = renderHook(() => useLocalStorage('sync-key', 'initial'));

      act(() => {
        // Simular evento de storage de outra aba
        const storageEvent = new StorageEvent('storage', {
          key: 'sync-key',
          newValue: JSON.stringify('from-other-tab'),
        });
        window.dispatchEvent(storageEvent);
      });

      expect(result.current[0]).toBe('from-other-tab');
    });

    it('não deve sincronizar quando a chave é diferente', () => {
      const { result } = renderHook(() => useLocalStorage('my-key', 'initial'));

      act(() => {
        const storageEvent = new StorageEvent('storage', {
          key: 'other-key',
          newValue: JSON.stringify('other-value'),
        });
        window.dispatchEvent(storageEvent);
      });

      expect(result.current[0]).toBe('initial');
    });

    it('deve resetar para valor inicial quando storage event remove o valor', () => {
      const { result } = renderHook(() => useLocalStorage('reset-key', 'default'));

      act(() => {
        result.current[1]('changed');
      });
      expect(result.current[0]).toBe('changed');

      act(() => {
        const storageEvent = new StorageEvent('storage', {
          key: 'reset-key',
          newValue: null,
        });
        window.dispatchEvent(storageEvent);
      });

      expect(result.current[0]).toBe('default');
    });

    it('deve disparar storage event ao atualizar valor', () => {
      const dispatchEventSpy = vi.spyOn(window, 'dispatchEvent');

      const { result } = renderHook(() => useLocalStorage('emit-key', 'initial'));

      act(() => {
        result.current[1]('new-value');
      });

      expect(dispatchEventSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'storage',
          key: 'emit-key',
        })
      );

      dispatchEventSpy.mockRestore();
    });
  });

  describe('Edge Cases', () => {
    it('deve lidar com localStorage indisponível (SSR)', () => {
      const originalLocalStorage = window.localStorage;
      // @ts-expect-error - Simulando SSR
      window.localStorage = undefined;

      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      const { result } = renderHook(() => useLocalStorage('ssr-key', 'default'));

      expect(result.current[0]).toBe('default');

      window.localStorage = originalLocalStorage;
      consoleSpy.mockRestore();
    });

    it('deve lidar com erro ao salvar no localStorage', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
        throw new Error('Storage full');
      });

      const { result } = renderHook(() => useLocalStorage('error-key', 'default'));

      act(() => {
        result.current[1]('new-value');
      });

      // Deve manter o valor no estado mesmo se localStorage falhar
      expect(result.current[0]).toBe('new-value');
      expect(consoleSpy).toHaveBeenCalled();

      consoleSpy.mockRestore();
      setItemSpy.mockRestore();
    });

    it('deve atualizar quando a chave muda (não recomendado, mas deve funcionar)', () => {
      const { result, rerender } = renderHook(
        ({ storageKey }) => useLocalStorage(storageKey, 'default'),
        { initialProps: { storageKey: 'key1' } }
      );

      localStorage.setItem('key2', JSON.stringify('value2'));

      rerender({ storageKey: 'key2' });

      expect(result.current[0]).toBe('value2');
    });
  });

  describe('Remove Function', () => {
    it('deve remover valor usando função remove', () => {
      localStorage.setItem('remove-key', JSON.stringify('existing-value'));

      const { result } = renderHook(() => useLocalStorage('remove-key', 'default'));

      expect(result.current[0]).toBe('existing-value');

      act(() => {
        result.current[2](); // remove function
      });

      expect(result.current[0]).toBe('default');
      expect(localStorage.getItem('remove-key')).toBeNull();
    });
  });

  describe('SSR Handling', () => {
    it('deve retornar valor inicial quando localStorage não está disponível', () => {
      const originalLocalStorage = window.localStorage;
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      Object.defineProperty(window, 'localStorage', {
        value: undefined,
        writable: true,
      });

      const { result } = renderHook(() => useLocalStorage('ssr-test', 'fallback'));

      expect(result.current[0]).toBe('fallback');

      Object.defineProperty(window, 'localStorage', {
        value: originalLocalStorage,
        writable: true,
      });
      consoleSpy.mockRestore();
    });
  });

  describe('Remove Function - Additional Tests', () => {
    it('deve disparar storage event ao remover', () => {
      const dispatchEventSpy = vi.spyOn(window, 'dispatchEvent');
      localStorage.setItem('remove-event-test', JSON.stringify('value'));

      const { result } = renderHook(() => useLocalStorage('remove-event-test', 'default'));

      act(() => {
        result.current[2](); // removeValue
      });

      expect(dispatchEventSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'storage',
          key: 'remove-event-test',
          newValue: null,
        })
      );

      dispatchEventSpy.mockRestore();
    });
  });

  describe('Remove Function - Error Handling', () => {
    it('deve lidar com erro ao remover do localStorage', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      localStorage.setItem('remove-error-key', JSON.stringify('value'));

      const { result } = renderHook(() => useLocalStorage('remove-error-key', 'default'));

      expect(result.current[0]).toBe('value');

      // Mock removeItem to throw via prototype spy
      const removeItemSpy = vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => {
        throw new Error('Remove failed');
      });

      act(() => {
        result.current[2](); // removeValue
      });

      // O catch da linha 68 deve ser atingido
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error removing localStorage key'),
        expect.any(Error)
      );

      removeItemSpy.mockRestore();
      consoleSpy.mockRestore();
    });
  });

  describe('Storage Event - Edge Cases', () => {
    it('deve lidar com erro ao parsear storage event', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      const { result } = renderHook(() => useLocalStorage('parse-error-key', 'default'));

      act(() => {
        const storageEvent = new StorageEvent('storage', {
          key: 'parse-error-key',
          newValue: 'invalid-json-{{{',
        });
        window.dispatchEvent(storageEvent);
      });

      // Deve manter o valor atual quando parsing falha
      expect(result.current[0]).toBe('default');
      expect(consoleSpy).toHaveBeenCalled();

      consoleSpy.mockRestore();
    });
  });
});
