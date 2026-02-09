import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

interface ContainerProps {
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  className?: string;
  centered?: boolean;
}

const Container: React.FC<ContainerProps> = ({
  children,
  size = 'lg',
  className,
  centered = false
}) => {
  const sizeClasses = {
    sm: 'max-w-screen-sm',
    md: 'max-w-screen-md',
    lg: 'max-w-screen-lg',
    xl: 'max-w-screen-xl',
    full: 'max-w-full'
  };

  return (
    <div
      className={`container mx-auto px-4 ${sizeClasses[size]} ${centered ? 'flex justify-center' : ''} ${className || ''}`}
      data-testid="container"
    >
      {children}
    </div>
  );
};

Container.displayName = 'Container';

describe('Container', () => {
  it('renderiza container com children', () => {
    render(
      <Container>
        <div data-testid="content">Conteúdo</div>
      </Container>
    );
    expect(screen.getByTestId('content')).toBeInTheDocument();
  });

  it('tem classe mx-auto', () => {
    const { container } = render(<Container>Test</Container>);
    const div = container.firstChild as HTMLElement;
    expect(div.className).toContain('mx-auto');
  });

  it('tem padding horizontal padrão', () => {
    const { container } = render(<Container>Test</Container>);
    const div = container.firstChild as HTMLElement;
    expect(div.className).toContain('px-4');
  });

  it('aplica tamanho sm', () => {
    const { container } = render(<Container size="sm">Test</Container>);
    const div = container.firstChild as HTMLElement;
    expect(div.className).toContain('max-w-screen-sm');
  });

  it('aplica tamanho md', () => {
    const { container } = render(<Container size="md">Test</Container>);
    const div = container.firstChild as HTMLElement;
    expect(div.className).toContain('max-w-screen-md');
  });

  it('aplica tamanho lg (padrão)', () => {
    const { container } = render(<Container>Test</Container>);
    const div = container.firstChild as HTMLElement;
    expect(div.className).toContain('max-w-screen-lg');
  });

  it('aplica tamanho xl', () => {
    const { container } = render(<Container size="xl">Test</Container>);
    const div = container.firstChild as HTMLElement;
    expect(div.className).toContain('max-w-screen-xl');
  });

  it('aplica tamanho full', () => {
    const { container } = render(<Container size="full">Test</Container>);
    const div = container.firstChild as HTMLElement;
    expect(div.className).toContain('max-w-full');
  });

  it('aplica classe customizada', () => {
    const { container } = render(
      <Container className="custom-container">Test</Container>
    );
    const div = container.firstChild as HTMLElement;
    expect(div.className).toContain('custom-container');
  });

  it('aplica classe de centralização quando centered é true', () => {
    const { container } = render(<Container centered>Test</Container>);
    const div = container.firstChild as HTMLElement;
    expect(div.className).toContain('flex');
    expect(div.className).toContain('justify-center');
  });

  it('não aplica classe de centralização quando centered é false', () => {
    const { container } = render(<Container centered={false}>Test</Container>);
    const div = container.firstChild as HTMLElement;
    expect(div.className).not.toContain('flex');
  });

  it('tem displayName correto', () => {
    expect(Container.displayName).toBe('Container');
  });

  it('renderiza múltiplos containers', () => {
    render(
      <>
        <Container data-testid="c1">Container 1</Container>
        <Container data-testid="c2">Container 2</Container>
      </>
    );
    expect(screen.getByText('Container 1')).toBeInTheDocument();
    expect(screen.getByText('Container 2')).toBeInTheDocument();
  });

  it('acepta children complexos', () => {
    render(
      <Container>
        <header>Cabeçalho</header>
        <main>Conteúdo Principal</main>
        <footer>Rodapé</footer>
      </Container>
    );
    expect(screen.getByText('Cabeçalho')).toBeInTheDocument();
    expect(screen.getByText('Conteúdo Principal')).toBeInTheDocument();
    expect(screen.getByText('Rodapé')).toBeInTheDocument();
  });
});
