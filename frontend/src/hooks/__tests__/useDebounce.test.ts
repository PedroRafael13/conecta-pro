import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useDebounce } from '../useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Delay de Execução', () => {
    it('deve retornar o valor inicial imediatamente', () => {
      const { result } = renderHook(() => useDebounce('initial', 500));
      expect(result.current).toBe('initial');
    });

    it('deve manter o valor anterior durante o delay', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );

      rerender({ value: 'changed', delay: 500 });

      // Valor ainda deve ser o inicial antes do delay
      expect(result.current).toBe('initial');
    });

    it('deve atualizar o valor após o delay', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );

      rerender({ value: 'changed', delay: 500 });

      act(() => {
        vi.advanceTimersByTime(500);
      });

      expect(result.current).toBe('changed');
    });

    it('deve respeitar diferentes delays', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 1000 } }
      );

      rerender({ value: 'changed', delay: 1000 });

      // Após 500ms (metade do delay)
      act(() => {
        vi.advanceTimersByTime(500);
      });
      expect(result.current).toBe('initial');

      // Após o delay completo
      act(() => {
        vi.advanceTimersByTime(500);
      });
      expect(result.current).toBe('changed');
    });

    it('deve funcionar com números', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 0, delay: 300 } }
      );

      rerender({ value: 42, delay: 300 });
      expect(result.current).toBe(0);

      act(() => {
        vi.advanceTimersByTime(300);
      });
      expect(result.current).toBe(42);
    });

    it('deve funcionar com objetos', () => {
      const initialObj = { name: 'John', age: 30 };
      const newObj = { name: 'Jane', age: 25 };

      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: initialObj, delay: 300 } }
      );

      rerender({ value: newObj, delay: 300 });
      expect(result.current).toBe(initialObj);

      act(() => {
        vi.advanceTimersByTime(300);
      });
      expect(result.current).toBe(newObj);
    });

    it('deve funcionar com arrays', () => {
      const initialArray = [1, 2, 3];
      const newArray = [4, 5, 6];

      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: initialArray, delay: 300 } }
      );

      rerender({ value: newArray, delay: 300 });
      expect(result.current).toBe(initialArray);

      act(() => {
        vi.advanceTimersByTime(300);
      });
      expect(result.current).toBe(newArray);
    });
  });

  describe('Cancelamento', () => {
    it('deve cancelar o timeout anterior quando o valor muda', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );

      // Primeira mudança
      rerender({ value: 'change1', delay: 500 });

      // Segunda mudança antes do timeout
      act(() => {
        vi.advanceTimersByTime(300);
      });
      rerender({ value: 'change2', delay: 500 });

      // Avançar o restante do tempo original
      act(() => {
        vi.advanceTimersByTime(200);
      });

      // Valor ainda deve ser inicial (primeiro timeout foi cancelado)
      expect(result.current).toBe('initial');

      // Aguardar o novo timeout completo
      act(() => {
        vi.advanceTimersByTime(500);
      });
      expect(result.current).toBe('change2');
    });

    it('deve cancelar o timeout quando o componente é desmontado', () => {
      const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');

      const { rerender, unmount } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );

      rerender({ value: 'changed', delay: 500 });

      unmount();

      expect(clearTimeoutSpy).toHaveBeenCalled();
      clearTimeoutSpy.mockRestore();
    });

    it('deve reiniciar o timer quando o delay muda', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      );

      rerender({ value: 'changed', delay: 500 });

      // Mudar o delay antes do timeout original
      act(() => {
        vi.advanceTimersByTime(300);
      });
      rerender({ value: 'changed', delay: 1000 });

      // Avançar o tempo restante do delay original
      act(() => {
        vi.advanceTimersByTime(200);
      });
      expect(result.current).toBe('initial');

      // Aguardar o novo delay completo
      act(() => {
        vi.advanceTimersByTime(1000);
      });
      expect(result.current).toBe('changed');
    });
  });

  describe('Múltiplas Mudanças', () => {
    it('deve apenas usar o último valor após múltiplas mudanças rápidas', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 300 } }
      );

      // Múltiplas mudanças rápidas
      rerender({ value: 'a', delay: 300 });
      rerender({ value: 'b', delay: 300 });
      rerender({ value: 'c', delay: 300 });
      rerender({ value: 'final', delay: 300 });

      act(() => {
        vi.advanceTimersByTime(300);
      });

      expect(result.current).toBe('final');
    });

    it('deve manter o valor estável quando o mesmo valor é passado', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'same', delay: 300 } }
      );

      rerender({ value: 'same', delay: 300 });
      rerender({ value: 'same', delay: 300 });

      act(() => {
        vi.advanceTimersByTime(300);
      });

      expect(result.current).toBe('same');
    });
  });

  describe('Edge Cases', () => {
    it('deve funcionar com delay zero', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 0 } }
      );

      rerender({ value: 'changed', delay: 0 });

      act(() => {
        vi.advanceTimersByTime(0);
      });

      expect(result.current).toBe('changed');
    });

    it('deve funcionar com valores nulos', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 300 } }
      );

      rerender({ value: null as unknown as string, delay: 300 });

      act(() => {
        vi.advanceTimersByTime(300);
      });

      expect(result.current).toBeNull();
    });

    it('deve funcionar com valores undefined', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 300 } as { value: string | undefined; delay: number } }
      );

      rerender({ value: undefined, delay: 300 });

      act(() => {
        vi.advanceTimersByTime(300);
      });

      expect(result.current).toBeUndefined();
    });
  });
});
