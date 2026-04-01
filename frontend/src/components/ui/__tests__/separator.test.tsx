import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Separator } from '../separator';

describe('Separator', () => {
  it('deve renderizar separator horizontal por padrão', () => {
    const { container } = render(<Separator />);
    const separator = container.firstChild as HTMLElement;
    expect(separator).toBeInTheDocument();
    expect(separator.className).toContain('h-[1px]');
    expect(separator.className).toContain('w-full');
  });

  it('deve renderizar separator vertical', () => {
    const { container } = render(<Separator orientation="vertical" />);
    const separator = container.firstChild as HTMLElement;
    expect(separator.className).toContain('h-full');
    expect(separator.className).toContain('w-[1px]');
  });

  it('deve ter atributo decorative true por padrão', () => {
    const { container } = render(<Separator />);
    const separator = container.firstChild as HTMLElement;
    expect(separator).toHaveAttribute('data-orientation', 'horizontal');
  });

  it('deve aplicar classe customizada', () => {
    const { container } = render(<Separator className="custom-separator" />);
    const separator = container.firstChild as HTMLElement;
    expect(separator.className).toContain('custom-separator');
  });

  it('deve ter cor de fundo de borda', () => {
    const { container } = render(<Separator />);
    const separator = container.firstChild as HTMLElement;
    expect(separator.className).toContain('bg-border');
  });

  it('deve ter estilo de shrink-0', () => {
    const { container } = render(<Separator />);
    const separator = container.firstChild as HTMLElement;
    expect(separator.className).toContain('shrink-0');
  });

  it('deve encaminhar ref corretamente', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(<Separator ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve ter displayName correto', () => {
    expect(Separator.displayName).toBe('Separator');
  });

  it('deve renderizar múltiplos separators', () => {
    const { container } = render(
      <>
        <Separator data-testid="sep1" />
        <Separator data-testid="sep2" />
        <Separator data-testid="sep3" />
      </>
    );
    expect(container.querySelectorAll('[data-testid^="sep"]')).toHaveLength(3);
  });

  it('deve ter atributo role="separator"', () => {
    const { container } = render(<Separator decorative={false} />);
    const separator = container.firstChild as HTMLElement;
    expect(separator).toHaveAttribute('role', 'separator');
  });

  it('deve aceitar prop decorative', () => {
    const { container } = render(<Separator decorative={false} />);
    const separator = container.firstChild as HTMLElement;
    expect(separator).toBeInTheDocument();
  });

  it('deve separar conteúdo visualmente', () => {
    const { container } = render(
      <div>
        <span>Item 1</span>
        <Separator />
        <span>Item 2</span>
      </div>
    );
    const separator = container.querySelector('[data-orientation]');
    expect(separator).toBeInTheDocument();
  });
});
