import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

interface DividerProps {
  orientation?: 'horizontal' | 'vertical';
  className?: string;
  spacing?: 'none' | 'sm' | 'md' | 'lg';
}

const Divider: React.FC<DividerProps> = ({
  orientation = 'horizontal',
  className,
  spacing = 'md'
}) => {
  const baseClasses = 'bg-border shrink-0';

  const orientationClasses = {
    horizontal: 'h-[1px] w-full',
    vertical: 'h-full w-[1px]'
  };

  const spacingClasses = {
    none: '',
    sm: orientation === 'horizontal' ? 'my-2' : 'mx-2',
    md: orientation === 'horizontal' ? 'my-4' : 'mx-4',
    lg: orientation === 'horizontal' ? 'my-6' : 'mx-6'
  };

  return (
    <div
      role="separator"
      aria-orientation={orientation}
      className={`${baseClasses} ${orientationClasses[orientation]} ${spacingClasses[spacing]} ${className || ''}`}
      data-testid="divider"
    />
  );
};

Divider.displayName = 'Divider';

describe('Divider', () => {
  it('renderiza divider', () => {
    render(<Divider />);
    expect(screen.getByTestId('divider')).toBeInTheDocument();
  });

  it('tem role separator', () => {
    render(<Divider />);
    const divider = screen.getByRole('separator');
    expect(divider).toBeInTheDocument();
  });

  it('aplica orientação horizontal (padrão)', () => {
    render(<Divider />);
    const divider = screen.getByTestId('divider');
    expect(divider).toHaveAttribute('aria-orientation', 'horizontal');
    expect(divider.className).toContain('h-[1px]');
    expect(divider.className).toContain('w-full');
  });

  it('aplica orientação vertical', () => {
    render(<Divider orientation="vertical" />);
    const divider = screen.getByTestId('divider');
    expect(divider).toHaveAttribute('aria-orientation', 'vertical');
    expect(divider.className).toContain('h-full');
    expect(divider.className).toContain('w-[1px]');
  });

  it('tem cor de borda', () => {
    render(<Divider />);
    const divider = screen.getByTestId('divider');
    expect(divider.className).toContain('bg-border');
  });

  it('aplica spacing horizontal sm', () => {
    render(<Divider orientation="horizontal" spacing="sm" />);
    const divider = screen.getByTestId('divider');
    expect(divider.className).toContain('my-2');
  });

  it('aplica spacing horizontal md (padrão)', () => {
    render(<Divider />);
    const divider = screen.getByTestId('divider');
    expect(divider.className).toContain('my-4');
  });

  it('aplica spacing horizontal lg', () => {
    render(<Divider orientation="horizontal" spacing="lg" />);
    const divider = screen.getByTestId('divider');
    expect(divider.className).toContain('my-6');
  });

  it('aplica spacing vertical', () => {
    render(<Divider orientation="vertical" spacing="md" />);
    const divider = screen.getByTestId('divider');
    expect(divider.className).toContain('mx-4');
  });

  it('não aplica spacing quando none', () => {
    render(<Divider spacing="none" />);
    const divider = screen.getByTestId('divider');
    expect(divider.className).not.toContain('my-');
  });

  it('aplica classe customizada', () => {
    render(<Divider className="custom-divider" />);
    const divider = screen.getByTestId('divider');
    expect(divider.className).toContain('custom-divider');
  });

  it('tem shrink-0', () => {
    render(<Divider />);
    const divider = screen.getByTestId('divider');
    expect(divider.className).toContain('shrink-0');
  });

  it('tem displayName correto', () => {
    expect(Divider.displayName).toBe('Divider');
  });

  it('renderiza múltiplos dividers', () => {
    render(
      <>
        <Divider data-testid="d1" />
        <Divider data-testid="d2" />
        <Divider data-testid="d3" />
      </>
    );
    expect(screen.getAllByTestId('divider')).toHaveLength(3);
  });
});
