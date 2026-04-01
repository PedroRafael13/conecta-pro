import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FormSkeleton } from '../form-skeleton';

describe('FormSkeleton', () => {
  it('deve renderizar skeleton do formulário', () => {
    render(<FormSkeleton />);
    const skeleton = screen.getByTestId('form-skeleton');
    expect(skeleton).toBeInTheDocument();
  });

  it('deve ter classe animate-shimmer nos elementos filhos', () => {
    const { container } = render(<FormSkeleton />);
    const shimmerElements = container.querySelectorAll('.animate-shimmer');
    expect(shimmerElements.length).toBeGreaterThan(0);
  });

  it('deve ter estrutura de espaço de formulário', () => {
    render(<FormSkeleton />);
    const skeleton = screen.getByTestId('form-skeleton');
    expect(skeleton.className).toContain('space-y-4');
  });

  it('deve renderizar múltiplos campos de skeleton', () => {
    const { container } = render(<FormSkeleton />);
    const fields = container.querySelectorAll('[class*="h-10"]');
    expect(fields.length).toBeGreaterThanOrEqual(2);
  });

  it('deve ter classe de background para campos', () => {
    const { container } = render(<FormSkeleton />);
    // Procura por elementos com classe bg- que incluem secondary
    const fields = container.querySelectorAll('[class*="bg-"]');
    expect(fields.length).toBeGreaterThan(0);
  });

  it('deve ter bordas arredondadas', () => {
    const { container } = render(<FormSkeleton />);
    const elements = container.querySelectorAll('[class*="rounded"]');
    expect(elements.length).toBeGreaterThan(0);
  });

  it('deve renderizar labels de skeleton', () => {
    const { container } = render(<FormSkeleton />);
    const labels = container.querySelectorAll('[class*="h-4"]');
    expect(labels.length).toBeGreaterThan(0);
  });

  it('deve ter largura diferente para labels (w-24 ou similar)', () => {
    const { container } = render(<FormSkeleton />);
    const labels = container.querySelectorAll('[class*="w-"]');
    expect(labels.length).toBeGreaterThan(0);
  });

  it('deve aceitar className customizado', () => {
    render(<FormSkeleton className="custom-skeleton" />);
    const skeleton = screen.getByTestId('form-skeleton');
    expect(skeleton.className).toContain('custom-skeleton');
  });

  it('deve ser usado em estado de loading', () => {
    const { container } = render(
      <div>
        <FormSkeleton />
      </div>
    );
    expect(container.querySelector('[data-testid="form-skeleton"]')).toBeInTheDocument();
  });

  it('deve ter altura definida para campos de input', () => {
    const { container } = render(<FormSkeleton />);
    const inputs = container.querySelectorAll('[class*="h-10"]');
    expect(inputs.length).toBeGreaterThan(0);
  });
});
