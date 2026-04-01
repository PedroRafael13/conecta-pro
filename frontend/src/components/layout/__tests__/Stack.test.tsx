import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

interface StackProps {
  children: React.ReactNode;
  spacing?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  align?: 'start' | 'center' | 'end' | 'stretch';
  className?: string;
  divider?: boolean;
}

const Stack: React.FC<StackProps> = ({
  children,
  spacing = 'md',
  align = 'stretch',
  className,
  divider = false
}) => {
  const spacingClasses = {
    none: 'space-y-0',
    xs: 'space-y-1',
    sm: 'space-y-2',
    md: 'space-y-4',
    lg: 'space-y-6',
    xl: 'space-y-8'
  };

  const alignClasses = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
    stretch: 'items-stretch'
  };

  return (
    <div
      className={`flex flex-col ${spacingClasses[spacing]} ${alignClasses[align]} ${className || ''}`}
      data-testid="stack"
    >
      {React.Children.map(children, (child, index) => (
        <React.Fragment key={index}>
          {child}
          {divider && index < React.Children.count(children) - 1 && (
            <hr className="border-t border-border" data-testid="divider" />
          )}
        </React.Fragment>
      ))}
    </div>
  );
};

Stack.displayName = 'Stack';

describe('Stack', () => {
  it('renderiza stack com children', () => {
    render(
      <Stack>
        <div data-testid="item">Item</div>
      </Stack>
    );
    expect(screen.getByTestId('item')).toBeInTheDocument();
  });

  it('tem classe flex e flex-col', () => {
    const { container } = render(<Stack>Test</Stack>);
    const stack = container.firstChild as HTMLElement;
    expect(stack.className).toContain('flex');
    expect(stack.className).toContain('flex-col');
  });

  it('aplica espaçamento none', () => {
    const { container } = render(<Stack spacing="none">Test</Stack>);
    const stack = container.firstChild as HTMLElement;
    expect(stack.className).toContain('space-y-0');
  });

  it('aplica espaçamento xs', () => {
    const { container } = render(<Stack spacing="xs">Test</Stack>);
    const stack = container.firstChild as HTMLElement;
    expect(stack.className).toContain('space-y-1');
  });

  it('aplica espaçamento sm', () => {
    const { container } = render(<Stack spacing="sm">Test</Stack>);
    const stack = container.firstChild as HTMLElement;
    expect(stack.className).toContain('space-y-2');
  });

  it('aplica espaçamento md (padrão)', () => {
    const { container } = render(<Stack>Test</Stack>);
    const stack = container.firstChild as HTMLElement;
    expect(stack.className).toContain('space-y-4');
  });

  it('aplica espaçamento lg', () => {
    const { container } = render(<Stack spacing="lg">Test</Stack>);
    const stack = container.firstChild as HTMLElement;
    expect(stack.className).toContain('space-y-6');
  });

  it('aplica espaçamento xl', () => {
    const { container } = render(<Stack spacing="xl">Test</Stack>);
    const stack = container.firstChild as HTMLElement;
    expect(stack.className).toContain('space-y-8');
  });

  it('aplica align start', () => {
    const { container } = render(<Stack align="start">Test</Stack>);
    const stack = container.firstChild as HTMLElement;
    expect(stack.className).toContain('items-start');
  });

  it('aplica align center', () => {
    const { container } = render(<Stack align="center">Test</Stack>);
    const stack = container.firstChild as HTMLElement;
    expect(stack.className).toContain('items-center');
  });

  it('aplica align end', () => {
    const { container } = render(<Stack align="end">Test</Stack>);
    const stack = container.firstChild as HTMLElement;
    expect(stack.className).toContain('items-end');
  });

  it('aplica align stretch (padrão)', () => {
    const { container } = render(<Stack>Test</Stack>);
    const stack = container.firstChild as HTMLElement;
    expect(stack.className).toContain('items-stretch');
  });

  it('aplica classe customizada', () => {
    const { container } = render(<Stack className="custom-stack">Test</Stack>);
    const stack = container.firstChild as HTMLElement;
    expect(stack.className).toContain('custom-stack');
  });

  it('renderiza dividers quando divider é true', () => {
    render(
      <Stack divider>
        <div>Item 1</div>
        <div>Item 2</div>
        <div>Item 3</div>
      </Stack>
    );
    const dividers = screen.getAllByTestId('divider');
    expect(dividers).toHaveLength(2);
  });

  it('não renderiza dividers quando divider é false', () => {
    render(
      <Stack>
        <div>Item 1</div>
        <div>Item 2</div>
        <div>Item 3</div>
      </Stack>
    );
    expect(screen.queryByTestId('divider')).not.toBeInTheDocument();
  });

  it('tem displayName correto', () => {
    expect(Stack.displayName).toBe('Stack');
  });

  it('renderiza múltiplos itens empilhados', () => {
    render(
      <Stack spacing="md">
        <div>Item 1</div>
        <div>Item 2</div>
        <div>Item 3</div>
        <div>Item 4</div>
      </Stack>
    );
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 4')).toBeInTheDocument();
  });
});
