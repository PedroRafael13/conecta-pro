import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

interface FlexProps {
  children: React.ReactNode;
  direction?: 'row' | 'col' | 'row-reverse' | 'col-reverse';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
  align?: 'start' | 'center' | 'end' | 'stretch' | 'baseline';
  wrap?: 'nowrap' | 'wrap' | 'wrap-reverse';
  gap?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const Flex: React.FC<FlexProps> = ({
  children,
  direction = 'row',
  justify = 'start',
  align = 'stretch',
  wrap = 'nowrap',
  gap = 'none',
  className
}) => {
  const directionClasses = {
    row: 'flex-row',
    col: 'flex-col',
    'row-reverse': 'flex-row-reverse',
    'col-reverse': 'flex-col-reverse'
  };

  const justifyClasses = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between',
    around: 'justify-around',
    evenly: 'justify-evenly'
  };

  const alignClasses = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
    stretch: 'items-stretch',
    baseline: 'items-baseline'
  };

  const wrapClasses = {
    nowrap: 'flex-nowrap',
    wrap: 'flex-wrap',
    'wrap-reverse': 'flex-wrap-reverse'
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
      className={`flex ${directionClasses[direction]} ${justifyClasses[justify]} ${alignClasses[align]} ${wrapClasses[wrap]} ${gapClasses[gap]} ${className || ''}`}
      data-testid="flex"
    >
      {children}
    </div>
  );
};

Flex.displayName = 'Flex';

describe('Flex', () => {
  it('renderiza flex com children', () => {
    render(
      <Flex>
        <div data-testid="item">Item</div>
      </Flex>
    );
    expect(screen.getByTestId('item')).toBeInTheDocument();
  });

  it('tem classe flex', () => {
    const { container } = render(<Flex>Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('flex');
  });

  it('aplica direção row (padrão)', () => {
    const { container } = render(<Flex>Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('flex-row');
  });

  it('aplica direção col', () => {
    const { container } = render(<Flex direction="col">Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('flex-col');
  });

  it('aplica direção row-reverse', () => {
    const { container } = render(<Flex direction="row-reverse">Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('flex-row-reverse');
  });

  it('aplica direção col-reverse', () => {
    const { container } = render(<Flex direction="col-reverse">Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('flex-col-reverse');
  });

  it('aplica justify start (padrão)', () => {
    const { container } = render(<Flex>Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('justify-start');
  });

  it('aplica justify center', () => {
    const { container } = render(<Flex justify="center">Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('justify-center');
  });

  it('aplica justify between', () => {
    const { container } = render(<Flex justify="between">Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('justify-between');
  });

  it('aplica justify around', () => {
    const { container } = render(<Flex justify="around">Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('justify-around');
  });

  it('aplica justify evenly', () => {
    const { container } = render(<Flex justify="evenly">Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('justify-evenly');
  });

  it('aplica align center', () => {
    const { container } = render(<Flex align="center">Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('items-center');
  });

  it('aplica align end', () => {
    const { container } = render(<Flex align="end">Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('items-end');
  });

  it('aplica align stretch (padrão)', () => {
    const { container } = render(<Flex>Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('items-stretch');
  });

  it('aplica wrap', () => {
    const { container } = render(<Flex wrap="wrap">Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('flex-wrap');
  });

  it('aplica gap', () => {
    const { container } = render(<Flex gap="md">Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('gap-4');
  });

  it('aplica classe customizada', () => {
    const { container } = render(<Flex className="custom-flex">Test</Flex>);
    const flex = container.firstChild as HTMLElement;
    expect(flex.className).toContain('custom-flex');
  });

  it('tem displayName correto', () => {
    expect(Flex.displayName).toBe('Flex');
  });

  it('renderiza múltiplos itens', () => {
    render(
      <Flex gap="md">
        <div>Item 1</div>
        <div>Item 2</div>
        <div>Item 3</div>
      </Flex>
    );
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 2')).toBeInTheDocument();
    expect(screen.getByText('Item 3')).toBeInTheDocument();
  });
});
