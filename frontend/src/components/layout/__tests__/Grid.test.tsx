import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

interface GridProps {
  children: React.ReactNode;
  cols?: 1 | 2 | 3 | 4 | 5 | 6 | 12;
  gap?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const Grid: React.FC<GridProps> = ({
  children,
  cols = 3,
  gap = 'md',
  className
}) => {
  const colsClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4',
    5: 'grid-cols-5',
    6: 'grid-cols-6',
    12: 'grid-cols-12'
  };

  const gapClasses = {
    none: 'gap-0',
    sm: 'gap-2',
    md: 'gap-4',
    lg: 'gap-6',
    xl: 'gap-8'
  };

  return (
    <div
      className={`grid ${colsClasses[cols]} ${gapClasses[gap]} ${className || ''}`}
      data-testid="grid"
    >
      {children}
    </div>
  );
};

Grid.displayName = 'Grid';

describe('Grid', () => {
  it('renderiza grid com children', () => {
    render(
      <Grid>
        <div data-testid="item">Item</div>
      </Grid>
    );
    expect(screen.getByTestId('item')).toBeInTheDocument();
  });

  it('tem classe grid', () => {
    const { container } = render(<Grid>Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('grid');
  });

  it('applica 1 coluna', () => {
    const { container } = render(<Grid cols={1}>Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('grid-cols-1');
  });

  it('applica 2 colunas', () => {
    const { container } = render(<Grid cols={2}>Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('grid-cols-2');
  });

  it('applica 3 colunas (padrão)', () => {
    const { container } = render(<Grid>Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('grid-cols-3');
  });

  it('applica 4 colunas', () => {
    const { container } = render(<Grid cols={4}>Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('grid-cols-4');
  });

  it('applica 6 colunas', () => {
    const { container } = render(<Grid cols={6}>Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('grid-cols-6');
  });

  it('applica 12 colunas', () => {
    const { container } = render(<Grid cols={12}>Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('grid-cols-12');
  });

  it('applica gap none', () => {
    const { container } = render(<Grid gap="none">Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('gap-0');
  });

  it('applica gap sm', () => {
    const { container } = render(<Grid gap="sm">Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('gap-2');
  });

  it('applica gap md (padrão)', () => {
    const { container } = render(<Grid>Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('gap-4');
  });

  it('applica gap lg', () => {
    const { container } = render(<Grid gap="lg">Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('gap-6');
  });

  it('applica gap xl', () => {
    const { container } = render(<Grid gap="xl">Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('gap-8');
  });

  it('aplica classe customizada', () => {
    const { container } = render(<Grid className="custom-grid">Test</Grid>);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('custom-grid');
  });

  it('tem displayName correto', () => {
    expect(Grid.displayName).toBe('Grid');
  });

  it('renderiza múltiplos itens', () => {
    render(
      <Grid cols={3}>
        <div>Item 1</div>
        <div>Item 2</div>
        <div>Item 3</div>
        <div>Item 4</div>
        <div>Item 5</div>
        <div>Item 6</div>
      </Grid>
    );
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 6')).toBeInTheDocument();
  });
});
