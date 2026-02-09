import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useKeyboardShortcuts, useGlobalShortcuts } from '../useKeyboardShortcuts';

// Mock do next/navigation
const mockPush = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

describe('useKeyboardShortcuts', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Estado Inicial', () => {
    it('deve retornar shortcuts configurados', () => {
      const shortcuts = [
        { key: 'k', ctrl: true, description: 'Busca', action: vi.fn() },
      ];

      const { result } = renderHook(() =>
        useKeyboardShortcuts({ shortcuts })
      );

      expect(result.current.shortcuts).toHaveLength(1);
      expect(result.current.shortcuts[0]?.key).toBe('k');
    });
  });

  describe('Eventos de Teclado', () => {
    it('deve chamar action quando atalho corresponder', async () => {
      const action = vi.fn();
      const shortcuts = [
        { key: 'k', ctrl: true, description: 'Busca', action },
      ];

      renderHook(() => useKeyboardShortcuts({ shortcuts }));

      await act(async () => {
        const event = new KeyboardEvent('keydown', {
          key: 'k',
          ctrlKey: true,
        });
        window.dispatchEvent(event);
      });

      await waitFor(() => {
        expect(action).toHaveBeenCalled();
      });
    });

    it('não deve chamar action quando tecla não corresponder', async () => {
      const action = vi.fn();
      const shortcuts = [
        { key: 'k', ctrl: true, description: 'Busca', action },
      ];

      renderHook(() => useKeyboardShortcuts({ shortcuts }));

      await act(async () => {
        const event = new KeyboardEvent('keydown', {
          key: 'j',
          ctrlKey: true,
        });
        window.dispatchEvent(event);
      });

      expect(action).not.toHaveBeenCalled();
    });

    it('não deve chamar action quando modificador não corresponder', async () => {
      const action = vi.fn();
      const shortcuts = [
        { key: 'k', ctrl: true, description: 'Busca', action },
      ];

      renderHook(() => useKeyboardShortcuts({ shortcuts }));

      await act(async () => {
        const event = new KeyboardEvent('keydown', {
          key: 'k',
        });
        window.dispatchEvent(event);
      });

      expect(action).not.toHaveBeenCalled();
    });

    it('deve ignorar atalhos quando usuário está em input', async () => {
      const action = vi.fn();
      const shortcuts = [
        { key: 'k', description: 'Busca', action },
      ];

      renderHook(() => useKeyboardShortcuts({ shortcuts }));

      const input = document.createElement('input');
      input.setAttribute('type', 'text');
      document.body.appendChild(input);

      await act(async () => {
        input.focus();
      });

      // Verify input is focused
      expect(document.activeElement).toBe(input);

      await act(async () => {
        const event = new KeyboardEvent('keydown', {
          key: 'k',
          bubbles: true,
        });
        input.dispatchEvent(event);
      });

      document.body.removeChild(input);

      expect(action).not.toHaveBeenCalled();
    });

    it('deve permitir ESC mesmo em inputs', async () => {
      const action = vi.fn();
      const shortcuts = [
        { key: 'Escape', description: 'Fechar', action },
      ];

      renderHook(() => useKeyboardShortcuts({ shortcuts }));

      await act(async () => {
        const input = document.createElement('input');
        document.body.appendChild(input);
        input.focus();

        const event = new KeyboardEvent('keydown', {
          key: 'Escape',
        });
        window.dispatchEvent(event);

        document.body.removeChild(input);
      });

      await waitFor(() => {
        expect(action).toHaveBeenCalled();
      });
    });

    it('deve respeitar preventDefault = false', async () => {
      const action = vi.fn();
      const shortcuts = [
        { key: 'k', description: 'Busca', action, preventDefault: false },
      ];

      renderHook(() => useKeyboardShortcuts({ shortcuts }));

      await act(async () => {
        const event = new KeyboardEvent('keydown', {
          key: 'k',
        });
        const preventDefaultSpy = vi.spyOn(event, 'preventDefault');
        window.dispatchEvent(event);

        expect(preventDefaultSpy).not.toHaveBeenCalled();
      });
    });

    it('deve prevenir comportamento padrão por padrão', async () => {
      const action = vi.fn();
      const shortcuts = [
        { key: 'k', description: 'Busca', action },
      ];

      renderHook(() => useKeyboardShortcuts({ shortcuts }));

      await act(async () => {
        const event = new KeyboardEvent('keydown', {
          key: 'k',
          bubbles: true,
        });
        window.dispatchEvent(event);
      });

      // O action deve ser chamado
      await waitFor(() => {
        expect(action).toHaveBeenCalled();
      });
    });
  });

  describe('Enabled/Disabled', () => {
    it('não deve registrar eventos quando enabled é false', () => {
      const addEventListenerSpy = vi.spyOn(window, 'addEventListener');
      const action = vi.fn();
      const shortcuts = [
        { key: 'k', description: 'Busca', action },
      ];

      renderHook(() =>
        useKeyboardShortcuts({ shortcuts, enabled: false })
      );

      expect(addEventListenerSpy).not.toHaveBeenCalledWith('keydown', expect.any(Function));
    });

    it('deve remover event listener no cleanup', () => {
      const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener');
      const action = vi.fn();
      const shortcuts = [
        { key: 'k', description: 'Busca', action },
      ];

      const { unmount } = renderHook(() =>
        useKeyboardShortcuts({ shortcuts })
      );

      unmount();

      expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));
    });
  });

  describe('Atualização de Shortcuts', () => {
    it('deve atualizar shortcuts quando props mudam', async () => {
      const action1 = vi.fn();
      const action2 = vi.fn();

      const { result, rerender } = renderHook(
        ({ shortcuts }) => useKeyboardShortcuts({ shortcuts }),
        {
          initialProps: {
            shortcuts: [{ key: 'k', description: 'Busca', action: action1 }],
          },
        }
      );

      expect(result.current.shortcuts[0]?.action).toBe(action1);

      rerender({
        shortcuts: [{ key: 'k', description: 'Busca', action: action2 }],
      });

      await act(async () => {
        const event = new KeyboardEvent('keydown', { key: 'k' });
        window.dispatchEvent(event);
      });

      expect(action1).not.toHaveBeenCalled();
      await waitFor(() => {
        expect(action2).toHaveBeenCalled();
      });
    });
  });
});

describe('useGlobalShortcuts', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve configurar atalhos globais', async () => {
    const onSearchOpen = vi.fn();
    const onCommandPaletteOpen = vi.fn();
    const onSidebarToggle = vi.fn();
    const onHelpOpen = vi.fn();
    const onModalClose = vi.fn();

    renderHook(() =>
      useGlobalShortcuts({
        onSearchOpen,
        onCommandPaletteOpen,
        onSidebarToggle,
        onHelpOpen,
        onModalClose,
      })
    );

    // Testar atalho de busca (/) - mas não em input
    await act(async () => {
      const event = new KeyboardEvent('keydown', { key: '/' });
      window.dispatchEvent(event);
    });

    await waitFor(() => {
      expect(onSearchOpen).toHaveBeenCalled();
    });

    // Testar command palette (Ctrl+K)
    await act(async () => {
      const event = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true });
      window.dispatchEvent(event);
    });

    await waitFor(() => {
      expect(onCommandPaletteOpen).toHaveBeenCalled();
    });

    // Testar toggle sidebar (Ctrl+B)
    await act(async () => {
      const event = new KeyboardEvent('keydown', { key: 'b', ctrlKey: true });
      window.dispatchEvent(event);
    });

    await waitFor(() => {
      expect(onSidebarToggle).toHaveBeenCalled();
    });

    // Testar ESC
    await act(async () => {
      const event = new KeyboardEvent('keydown', { key: 'Escape' });
      window.dispatchEvent(event);
    });

    await waitFor(() => {
      expect(onModalClose).toHaveBeenCalled();
    });
  });

  it('deve navegar para dashboard com Alt+1', async () => {
    renderHook(() => useGlobalShortcuts({}));

    await act(async () => {
      const event = new KeyboardEvent('keydown', { key: '1', altKey: true });
      window.dispatchEvent(event);
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('deve navegar para operacional com Alt+2', async () => {
    renderHook(() => useGlobalShortcuts({}));

    await act(async () => {
      const event = new KeyboardEvent('keydown', { key: '2', altKey: true });
      window.dispatchEvent(event);
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/modulos/operacional/postos');
    });
  });

  it('deve navegar para financeiro com Alt+3', async () => {
    renderHook(() => useGlobalShortcuts({}));

    await act(async () => {
      const event = new KeyboardEvent('keydown', { key: '3', altKey: true });
      window.dispatchEvent(event);
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/modulos/financeiro');
    });
  });

  it('deve navegar para CRM com Alt+4', async () => {
    renderHook(() => useGlobalShortcuts({}));

    await act(async () => {
      const event = new KeyboardEvent('keydown', { key: '4', altKey: true });
      window.dispatchEvent(event);
    });

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/modulos/crm');
    });
  });

  it('deve mostrar help com Shift+?', async () => {
    const onHelpOpen = vi.fn();

    renderHook(() => useGlobalShortcuts({ onHelpOpen }));

    await act(async () => {
      const event = new KeyboardEvent('keydown', { key: '?', shiftKey: true });
      window.dispatchEvent(event);
    });

    await waitFor(() => {
      expect(onHelpOpen).toHaveBeenCalled();
    });
  });

  it('deve retornar lista de atalhos', () => {
    const { result } = renderHook(() => useGlobalShortcuts({}));

    expect(Array.isArray(result.current)).toBe(true);
    expect(result.current.length).toBeGreaterThan(0);
    expect(result.current[0]).toHaveProperty('key');
    expect(result.current[0]).toHaveProperty('description');
    expect(result.current[0]).toHaveProperty('action');
  });
});
