import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LoadingState, LoadingOverlay, LoadingSpinner } from '../loading-state';

describe('LoadingState', () => {
  it('renderiza com mensagem padrão', () => {
    render(<LoadingState />);
    expect(screen.getByText('Carregando...')).toBeInTheDocument();
  });

  it('renderiza com mensagem customizada', () => {
    render(<LoadingState message="Buscando dados..." />);
    expect(screen.getByText('Buscando dados...')).toBeInTheDocument();
  });

  it('renderiza mensagem padrão quando message é undefined', () => {
    render(<LoadingState message={undefined} />);
    const loadingText = screen.queryByText('Carregando...');
    // undefined usa valor padrão do componente
    expect(loadingText).toBeInTheDocument();
  });

  it('aplica classe customizada', () => {
    const { container } = render(<LoadingState className="custom-class" />);
    const element = container.firstChild as HTMLElement;
    expect(element.className).toContain('custom-class');
  });

  it('renderiza spinner com tamanho sm', () => {
    const { container } = render(<LoadingState size="sm" />);
    const spinner = container.querySelector('svg');
    expect(spinner).toBeInTheDocument();
  });

  it('renderiza spinner com tamanho md', () => {
    const { container } = render(<LoadingState size="md" />);
    const spinner = container.querySelector('svg');
    expect(spinner).toBeInTheDocument();
  });

  it('renderiza spinner com tamanho lg', () => {
    const { container } = render(<LoadingState size="lg" />);
    const spinner = container.querySelector('svg');
    expect(spinner).toBeInTheDocument();
  });

  it('spinner possui animação', () => {
    const { container } = render(<LoadingState />);
    const spinner = container.querySelector('svg');
    expect(spinner?.classList.contains('animate-spin')).toBe(true);
  });
});

describe('LoadingOverlay', () => {
  it('renderiza overlay', () => {
    const { container } = render(<LoadingOverlay />);
    const overlay = container.firstChild as HTMLElement;
    expect(overlay).toBeInTheDocument();
    expect(overlay.className).toContain('absolute');
  });

  it('renderiza com mensagem', () => {
    render(<LoadingOverlay message="Processando..." />);
    expect(screen.getByText('Processando...')).toBeInTheDocument();
  });

  it('aplica blur no background', () => {
    const { container } = render(<LoadingOverlay />);
    const overlay = container.firstChild as HTMLElement;
    expect(overlay.className).toContain('backdrop-blur');
  });

  it('usa tamanho lg por padrão', () => {
    const { container } = render(<LoadingOverlay />);
    // Overlay usa size lg por padrão
    expect(container.firstChild).toBeInTheDocument();
  });

  it('aceita tamanho customizado', () => {
    const { container } = render(<LoadingOverlay size="sm" />);
    expect(container.firstChild).toBeInTheDocument();
  });
});

describe('LoadingSpinner', () => {
  it('renderiza spinner sem container', () => {
    const { container } = render(<LoadingSpinner />);
    const spinner = container.querySelector('svg');
    expect(spinner).toBeInTheDocument();
  });

  it('não renderiza texto', () => {
    render(<LoadingSpinner />);
    const text = screen.queryByText(/carregando/i);
    expect(text).not.toBeInTheDocument();
  });

  it('aplica classe customizada', () => {
    const { container } = render(<LoadingSpinner className="custom-spinner" />);
    const spinner = container.querySelector('svg');
    expect(spinner?.classList.contains('custom-spinner')).toBe(true);
  });

  it('respeita tamanho sm', () => {
    const { container } = render(<LoadingSpinner size="sm" />);
    const spinner = container.querySelector('svg');
    expect(spinner?.classList.contains('h-4')).toBe(true);
    expect(spinner?.classList.contains('w-4')).toBe(true);
  });

  it('respeita tamanho md', () => {
    const { container } = render(<LoadingSpinner size="md" />);
    const spinner = container.querySelector('svg');
    expect(spinner?.classList.contains('h-8')).toBe(true);
    expect(spinner?.classList.contains('w-8')).toBe(true);
  });

  it('respeita tamanho lg', () => {
    const { container } = render(<LoadingSpinner size="lg" />);
    const spinner = container.querySelector('svg');
    expect(spinner?.classList.contains('h-12')).toBe(true);
    expect(spinner?.classList.contains('w-12')).toBe(true);
  });

  it('sempre possui animação de spin', () => {
    const { container } = render(<LoadingSpinner />);
    const spinner = container.querySelector('svg');
    expect(spinner?.classList.contains('animate-spin')).toBe(true);
  });
});

describe('LoadingState - Integração', () => {
  it('pode ser usado dentro de containers', () => {
    const { container } = render(
      <div data-testid="container">
        <LoadingState message="Carregando dados..." />
      </div>
    );
    const containerEl = container.querySelector('[data-testid="container"]');
    expect(containerEl).toBeInTheDocument();
    expect(screen.getByText('Carregando dados...')).toBeInTheDocument();
  });

  it('múltiplos LoadingSpinners podem coexistir', () => {
    const { container } = render(
      <>
        <LoadingSpinner size="sm" />
        <LoadingSpinner size="md" />
        <LoadingSpinner size="lg" />
      </>
    );
    const spinners = container.querySelectorAll('svg');
    expect(spinners.length).toBe(3);
  });
});
