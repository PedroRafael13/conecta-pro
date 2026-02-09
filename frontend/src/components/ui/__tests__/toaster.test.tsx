import { describe, it, expect } from 'vitest';
import { Toaster } from '../toaster';
import { ToastProvider } from '../toast';

describe('Toaster', () => {
  it('deve exportar Toaster', () => {
    expect(Toaster).toBeDefined();
    expect(typeof Toaster).toBe('function');
  });

  it('deve exportar ToastProvider', () => {
    expect(ToastProvider).toBeDefined();
    expect(typeof ToastProvider).toBe('function');
  });
});
