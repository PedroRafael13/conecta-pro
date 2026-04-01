import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
  fluid?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const PageContainer: React.FC<PageContainerProps> = ({
  children,
  className,
  fluid = false,
  padding = 'md'
}) => {
  const paddingClasses = {
    none: 'p-0',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };

  return (
    <main
      className={`page-container min-h-screen ${paddingClasses[padding]} ${fluid ? 'w-full' : 'container mx-auto'} ${className || ''}`}
      data-testid="page-container"
    >
      {children}
    </main>
  );
};

PageContainer.displayName = 'PageContainer';

describe('PageContainer', () => {
  it('renderiza container com children', () => {
    render(
      <PageContainer>
        <div data-testid="content">Conteúdo da Página</div>
      </PageContainer>
    );
    expect(screen.getByTestId('content')).toBeInTheDocument();
  });

  it('é um elemento main', () => {
    const { container } = render(<PageContainer>Test</PageContainer>);
    const main = container.querySelector('main');
    expect(main).toBeInTheDocument();
  });

  it('tem altura mínima de tela', () => {
    const { container } = render(<PageContainer>Test</PageContainer>);
    const main = container.firstChild as HTMLElement;
    expect(main.className).toContain('min-h-screen');
  });

  it('aplica padding sm', () => {
    const { container } = render(<PageContainer padding="sm">Test</PageContainer>);
    const main = container.firstChild as HTMLElement;
    expect(main.className).toContain('p-4');
  });

  it('aplica padding md (padrão)', () => {
    const { container } = render(<PageContainer>Test</PageContainer>);
    const main = container.firstChild as HTMLElement;
    expect(main.className).toContain('p-6');
  });

  it('aplica padding lg', () => {
    const { container } = render(<PageContainer padding="lg">Test</PageContainer>);
    const main = container.firstChild as HTMLElement;
    expect(main.className).toContain('p-8');
  });

  it('aplica padding none', () => {
    const { container } = render(<PageContainer padding="none">Test</PageContainer>);
    const main = container.firstChild as HTMLElement;
    expect(main.className).toContain('p-0');
  });

  it('aplica container com margem centralizada quando fluid é false', () => {
    const { container } = render(<PageContainer>Test</PageContainer>);
    const main = container.firstChild as HTMLElement;
    expect(main.className).toContain('container');
    expect(main.className).toContain('mx-auto');
  });

  it('applica largura total quando fluid é true', () => {
    const { container } = render(<PageContainer fluid>Test</PageContainer>);
    const main = container.firstChild as HTMLElement;
    expect(main.className).toContain('w-full');
  });

  it('aplica classe customizada', () => {
    const { container } = render(
      <PageContainer className="custom-page">Test</PageContainer>
    );
    const main = container.firstChild as HTMLElement;
    expect(main.className).toContain('custom-page');
  });

  it('tem displayName correto', () => {
    expect(PageContainer.displayName).toBe('PageContainer');
  });

  it('renderiza conteúdo complexo', () => {
    render(
      <PageContainer>
        <header>Cabeçalho</header>
        <section>Seção 1</section>
        <section>Seção 2</section>
      </PageContainer>
    );
    expect(screen.getByText('Cabeçalho')).toBeInTheDocument();
    expect(screen.getByText('Seção 1')).toBeInTheDocument();
    expect(screen.getByText('Seção 2')).toBeInTheDocument();
  });
});
