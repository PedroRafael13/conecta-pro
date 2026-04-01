import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  children?: React.ReactNode;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  children,
  className,
  size = 'md'
}) => {
  const sizeClasses = {
    sm: 'text-xl',
    md: 'text-2xl',
    lg: 'text-3xl'
  };

  return (
    <header
      className={`page-header mb-6 border-b border-border pb-4 ${className || ''}`}
      data-testid="page-header"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className={`font-bold ${sizeClasses[size]}`} data-testid="page-title">
            {title}
          </h1>
          {subtitle && (
            <p className="text-muted-foreground mt-1" data-testid="page-subtitle">
              {subtitle}
            </p>
          )}
        </div>
        {children && <div data-testid="header-actions">{children}</div>}
      </div>
    </header>
  );
};

PageHeader.displayName = 'PageHeader';

describe('PageHeader', () => {
  it('renderiza título da página', () => {
    render(<PageHeader title="Título da Página" />);
    expect(screen.getByText('Título da Página')).toBeInTheDocument();
  });

  it('é um elemento header', () => {
    const { container } = render(<PageHeader title="Test" />);
    const header = container.querySelector('header');
    expect(header).toBeInTheDocument();
  });

  it('renderiza subtítulo quando fornecido', () => {
    render(
      <PageHeader title="Título" subtitle="Descrição da página" />
    );
    expect(screen.getByText('Descrição da página')).toBeInTheDocument();
  });

  it('não renderiza subtítulo quando não fornecido', () => {
    render(<PageHeader title="Título" />);
    expect(screen.queryByTestId('page-subtitle')).not.toBeInTheDocument();
  });

  it('aplica tamanho sm', () => {
    render(<PageHeader title="Título" size="sm" />);
    const title = screen.getByTestId('page-title');
    expect(title.className).toContain('text-xl');
  });

  it('aplica tamanho md (padrão)', () => {
    render(<PageHeader title="Título" />);
    const title = screen.getByTestId('page-title');
    expect(title.className).toContain('text-2xl');
  });

  it('aplica tamanho lg', () => {
    render(<PageHeader title="Título" size="lg" />);
    const title = screen.getByTestId('page-title');
    expect(title.className).toContain('text-3xl');
  });

  it('título tem fonte bold', () => {
    render(<PageHeader title="Título" />);
    const title = screen.getByTestId('page-title');
    expect(title.className).toContain('font-bold');
  });

  it('renderiza children como ações', () => {
    render(
      <PageHeader title="Título">
        <button>Adicionar</button>
      </PageHeader>
    );
    expect(screen.getByText('Adicionar')).toBeInTheDocument();
  });

  it('aplica classe customizada', () => {
    const { container } = render(
      <PageHeader title="Título" className="custom-header" />
    );
    const header = container.firstChild as HTMLElement;
    expect(header.className).toContain('custom-header');
  });

  it('tem margem inferior e borda', () => {
    const { container } = render(<PageHeader title="Título" />);
    const header = container.firstChild as HTMLElement;
    expect(header.className).toContain('mb-6');
    expect(header.className).toContain('border-b');
  });

  it('tem displayName correto', () => {
    expect(PageHeader.displayName).toBe('PageHeader');
  });

  it('renderiza múltiplas ações', () => {
    render(
      <PageHeader title="Título">
        <button>Botão 1</button>
        <button>Botão 2</button>
      </PageHeader>
    );
    expect(screen.getByText('Botão 1')).toBeInTheDocument();
    expect(screen.getByText('Botão 2')).toBeInTheDocument();
  });
});
