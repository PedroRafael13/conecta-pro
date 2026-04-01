import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TableSkeleton } from '../table-skeleton';

describe('TableSkeleton', () => {
  it('deve renderizar skeleton da tabela', () => {
    render(<TableSkeleton />);
    const skeleton = screen.getByTestId('table-skeleton');
    expect(skeleton).toBeInTheDocument();
  });

  it('deve renderizar 5 linhas por padrão', () => {
    const { container } = render(<TableSkeleton />);
    const rows = container.querySelectorAll('[data-testid="table-skeleton-row"]');
    expect(rows.length).toBe(5);
  });

  it('deve renderizar número customizado de linhas', () => {
    const { container } = render(<TableSkeleton rows={3} />);
    const rows = container.querySelectorAll('[data-testid="table-skeleton-row"]');
    expect(rows.length).toBe(3);
  });

  it('deve ter classe de animação shimmer', () => {
    const { container } = render(<TableSkeleton />);
    const shimmerElements = container.querySelectorAll('.animate-shimmer');
    expect(shimmerElements.length).toBeGreaterThan(0);
  });

  it('deve ter divisor entre linhas', () => {
    const { container } = render(<TableSkeleton />);
    const divider = container.querySelector('.divide-y');
    expect(divider).toBeInTheDocument();
  });

  it('deve ter cor de fundo secundária nos elementos', () => {
    const { container } = render(<TableSkeleton />);
    const elements = container.querySelectorAll('[class*="bg-"]');
    expect(elements.length).toBeGreaterThan(0);
  });

  it('deve ter layout flexbox em cada linha', () => {
    const { container } = render(<TableSkeleton />);
    const rows = container.querySelectorAll('.flex');
    expect(rows.length).toBeGreaterThan(0);
  });

  it('deve ter padding em cada linha', () => {
    const { container } = render(<TableSkeleton />);
    const rows = container.querySelectorAll('.p-4');
    expect(rows.length).toBeGreaterThan(0);
  });

  it('deve ter gap entre elementos', () => {
    const { container } = render(<TableSkeleton />);
    const rows = container.querySelectorAll('.gap-4');
    expect(rows.length).toBeGreaterThan(0);
  });

  it('deve ter elementos com larguras diferentes', () => {
    const { container } = render(<TableSkeleton />);
    const w48 = container.querySelector('.w-48');
    const w32 = container.querySelector('.w-32');
    const w24 = container.querySelector('.w-24');
    const w20 = container.querySelector('.w-20');

    expect(w48 || w32 || w24 || w20).toBeTruthy();
  });

  it('deve ter alturas definidas para os elementos', () => {
    const { container } = render(<TableSkeleton />);
    const h4 = container.querySelectorAll('.h-4');
    const h3 = container.querySelectorAll('.h-3');
    const h6 = container.querySelectorAll('.h-6');

    expect(h4.length + h3.length + h6.length).toBeGreaterThan(0);
  });

  it('deve ter bordas arredondadas nos elementos', () => {
    const { container } = render(<TableSkeleton />);
    const rounded = container.querySelectorAll('.rounded');
    expect(rounded.length).toBeGreaterThan(0);
  });

  it('deve renderizar espaçamento vertical entre elementos da linha', () => {
    const { container } = render(<TableSkeleton />);
    const spaceY = container.querySelectorAll('.space-y-2');
    expect(spaceY.length).toBeGreaterThan(0);
  });

  it('deve renderizar múltiplos skeletons simultaneamente', () => {
    const { container } = render(
      <>
        <TableSkeleton rows={2} />
        <TableSkeleton rows={3} />
      </>
    );
    const dividers = container.querySelectorAll('.divide-y');
    expect(dividers.length).toBe(2);
  });

  it('deve aceitar 1 linha', () => {
    const { container } = render(<TableSkeleton rows={1} />);
    const rows = container.querySelectorAll('[data-testid="table-skeleton-row"]');
    expect(rows.length).toBe(1);
  });

  it('deve aceitar 10 linhas', () => {
    const { container } = render(<TableSkeleton rows={10} />);
    const rows = container.querySelectorAll('[data-testid="table-skeleton-row"]');
    expect(rows.length).toBe(10);
  });

  it('deve ter flex-1 no container de texto', () => {
    const { container } = render(<TableSkeleton />);
    const flex1 = container.querySelector('.flex-1');
    expect(flex1).toBeInTheDocument();
  });

  it('deve ter flex-1 para ocupar espaço disponível', () => {
    const { container } = render(<TableSkeleton />);
    const flex1Elements = container.querySelectorAll('.flex-1');
    expect(flex1Elements.length).toBeGreaterThan(0);
  });
});
