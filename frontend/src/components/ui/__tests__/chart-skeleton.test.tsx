import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ChartSkeleton } from '../chart-skeleton';

describe('ChartSkeleton', () => {
  it('deve renderizar skeleton do gráfico', () => {
    render(<ChartSkeleton />);
    expect(screen.getByText('Carregando gráfico...')).toBeInTheDocument();
  });

  it('deve aplicar altura padrão de 300px', () => {
    const { container } = render(<ChartSkeleton />);
    const skeleton = container.firstChild as HTMLElement;
    expect(skeleton.style.height).toBe('300px');
  });

  it('deve aplicar altura customizada', () => {
    const { container } = render(<ChartSkeleton height={500} />);
    const skeleton = container.firstChild as HTMLElement;
    expect(skeleton.style.height).toBe('500px');
  });

  it('deve ter classe de animação pulse', () => {
    const { container } = render(<ChartSkeleton />);
    const pulseElement = container.querySelector('.animate-pulse');
    expect(pulseElement).toBeInTheDocument();
  });

  it('deve ter classes de layout flexbox', () => {
    const { container } = render(<ChartSkeleton />);
    const skeleton = container.firstChild as HTMLElement;
    expect(skeleton.className).toContain('flex');
    expect(skeleton.className).toContain('items-center');
    expect(skeleton.className).toContain('justify-center');
  });

  it('deve ter fundo com opacidade', () => {
    const { container } = render(<ChartSkeleton />);
    const skeleton = container.firstChild as HTMLElement;
    expect(skeleton.className).toContain('bg-');
  });

  it('deve ter bordas arredondadas', () => {
    const { container } = render(<ChartSkeleton />);
    const skeleton = container.firstChild as HTMLElement;
    expect(skeleton.className).toContain('rounded-lg');
  });

  it('deve renderizar texto com tamanho pequeno', () => {
    const { container } = render(<ChartSkeleton />);
    const text = container.querySelector('.text-sm');
    expect(text).toBeInTheDocument();
  });

  it('deve aceitar diferentes valores de altura', () => {
    const { rerender, container } = render(<ChartSkeleton height={200} />);
    let skeleton = container.firstChild as HTMLElement;
    expect(skeleton.style.height).toBe('200px');

    rerender(<ChartSkeleton height={400} />);
    skeleton = container.firstChild as HTMLElement;
    expect(skeleton.style.height).toBe('400px');
  });

  it('deve renderizar múltiplos skeletons com alturas diferentes', () => {
    const { container } = render(
      <>
        <ChartSkeleton height={200} />
        <ChartSkeleton height={300} />
        <ChartSkeleton height={400} />
      </>
    );
    const skeletons = container.querySelectorAll('.flex');
    expect(skeletons.length).toBe(3);
  });
});
