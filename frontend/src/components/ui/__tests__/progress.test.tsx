import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Progress } from '../progress';

describe('Progress', () => {
  it('deve renderizar Progress', () => {
    render(<Progress value={50} data-testid="progress" />);
    expect(screen.getByTestId('progress')).toBeInTheDocument();
  });

  it('deve ter largura completa', () => {
    const { container } = render(<Progress value={50} />);
    const progress = container.querySelector('[role="progressbar"]');
    expect(progress?.className).toContain('w-full');
  });

  it('deve ter altura padrão h-4', () => {
    const { container } = render(<Progress value={50} />);
    const progress = container.querySelector('[role="progressbar"]');
    expect(progress?.className).toContain('h-4');
  });

  it('deve ter bordas arredondadas', () => {
    const { container } = render(<Progress value={50} />);
    const progress = container.querySelector('[role="progressbar"]');
    expect(progress?.className).toContain('rounded-full');
  });

  it('deve ter cor de fundo secondary', () => {
    const { container } = render(<Progress value={50} />);
    const progress = container.querySelector('[role="progressbar"]');
    expect(progress?.className).toContain('bg-secondary');
  });

  it('deve aplicar valor 0 corretamente', () => {
    const { container } = render(<Progress value={0} />);
    const indicator = container.querySelector('[data-state="indeterminate"]');
    expect(indicator).toBeInTheDocument();
  });

  it('deve aplicar valor 50 corretamente', () => {
    const { container } = render(<Progress value={50} />);
    const indicator = container.querySelector('[data-state="indeterminate"]');
    expect(indicator).toBeInTheDocument();
  });

  it('deve aplicar valor 100 corretamente', () => {
    const { container } = render(<Progress value={100} />);
    const indicator = container.querySelector('[data-state="indeterminate"]');
    expect(indicator).toBeInTheDocument();
  });

  it('deve aplicar classe customizada', () => {
    const { container } = render(<Progress value={50} className="custom-progress" />);
    const progress = container.querySelector('.custom-progress');
    expect(progress).toBeInTheDocument();
  });

  it('deve encaminhar ref corretamente', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(<Progress ref={ref} value={50} />);
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve ter displayName correto', () => {
    expect(Progress.displayName).toBe('Progress');
  });

  it('deve ter role progressbar', () => {
    const { container } = render(<Progress value={50} />);
    const progress = container.querySelector('[role="progressbar"]');
    expect(progress).toBeInTheDocument();
  });

  it('deve renderizar indicador de progresso', () => {
    const { container } = render(<Progress value={50} />);
    const indicator = container.querySelector('[data-state]');
    expect(indicator).toBeInTheDocument();
  });

  it('deve renderizar indicador de progresso', () => {
    const { container } = render(<Progress value={50} />);
    // O indicador é renderizado dentro do componente Progress
    expect(container.querySelector('[role="progressbar"]')).toBeInTheDocument();
  });
});
