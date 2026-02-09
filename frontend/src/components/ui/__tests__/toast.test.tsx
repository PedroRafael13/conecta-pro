import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  Toast,
  ToastTitle,
  ToastDescription,
  ToastProvider,
  ToastViewport,
  ToastClose,
  ToastAction,
} from '../toast';

describe('Toast', () => {
  it('deve renderizar toast com título', () => {
    render(
      <ToastProvider>
        <Toast>
          <ToastTitle>Título do Toast</ToastTitle>
        </Toast>
        <ToastViewport />
      </ToastProvider>
    );
    expect(screen.getByText('Título do Toast')).toBeInTheDocument();
  });

  it('deve renderizar toast com descrição', () => {
    render(
      <ToastProvider>
        <Toast>
          <ToastDescription>Descrição do toast</ToastDescription>
        </Toast>
        <ToastViewport />
      </ToastProvider>
    );
    expect(screen.getByText('Descrição do toast')).toBeInTheDocument();
  });

  it('deve renderizar toast completo', () => {
    render(
      <ToastProvider>
        <Toast>
          <ToastTitle>Sucesso!</ToastTitle>
          <ToastDescription>Operação realizada com sucesso.</ToastDescription>
        </Toast>
        <ToastViewport />
      </ToastProvider>
    );
    expect(screen.getByText('Sucesso!')).toBeInTheDocument();
    expect(screen.getByText('Operação realizada com sucesso.')).toBeInTheDocument();
  });

  it('deve aplicar classe customizada no ToastTitle', () => {
    render(
      <ToastProvider>
        <Toast>
          <ToastTitle className="custom-title">Título</ToastTitle>
        </Toast>
        <ToastViewport />
      </ToastProvider>
    );
    const title = screen.getByText('Título');
    expect(title.className).toContain('custom-title');
  });

  it('deve aplicar classe customizada no ToastDescription', () => {
    render(
      <ToastProvider>
        <Toast>
          <ToastDescription className="custom-desc">Descrição</ToastDescription>
        </Toast>
        <ToastViewport />
      </ToastProvider>
    );
    const desc = screen.getByText('Descrição');
    expect(desc.className).toContain('custom-desc');
  });

  it('deve ter displayName correto para ToastTitle', () => {
    expect(ToastTitle.displayName).toBe('ToastTitle');
  });

  it('deve ter displayName correto para ToastDescription', () => {
    expect(ToastDescription.displayName).toBe('ToastDescription');
  });

  it('deve encaminhar ref corretamente no ToastTitle', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(
      <ToastProvider>
        <Toast>
          <ToastTitle ref={ref}>Título</ToastTitle>
        </Toast>
        <ToastViewport />
      </ToastProvider>
    );
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve encaminhar ref corretamente no ToastDescription', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(
      <ToastProvider>
        <Toast>
          <ToastDescription ref={ref}>Descrição</ToastDescription>
        </Toast>
        <ToastViewport />
      </ToastProvider>
    );
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve renderizar múltiplos toasts', () => {
    render(
      <ToastProvider>
        <Toast>
          <ToastTitle>Toast 1</ToastTitle>
        </Toast>
        <Toast>
          <ToastTitle>Toast 2</ToastTitle>
        </Toast>
        <ToastViewport />
      </ToastProvider>
    );
    expect(screen.getByText('Toast 1')).toBeInTheDocument();
    expect(screen.getByText('Toast 2')).toBeInTheDocument();
  });

  it('deve renderizar ToastViewport', () => {
    render(
      <ToastProvider>
        <ToastViewport data-testid="viewport" />
      </ToastProvider>
    );
    expect(screen.getByTestId('viewport')).toBeInTheDocument();
  });

  it('deve ter estilo de posicionamento fixo no viewport', () => {
    const { container } = render(
      <ToastProvider>
        <ToastViewport />
      </ToastProvider>
    );
    const viewport = container.querySelector('[class*="fixed"]');
    expect(viewport).toBeInTheDocument();
  });
});
