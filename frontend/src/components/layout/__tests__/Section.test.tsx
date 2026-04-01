import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

interface SectionProps {
  children: React.ReactNode;
  id?: string;
  className?: string;
  spacing?: 'sm' | 'md' | 'lg' | 'xl';
  background?: 'default' | 'muted' | 'primary' | 'secondary';
}

const Section: React.FC<SectionProps> = ({
  children,
  id,
  className,
  spacing = 'md',
  background = 'default'
}) => {
  const spacingClasses = {
    sm: 'py-4',
    md: 'py-8',
    lg: 'py-12',
    xl: 'py-16'
  };

  const bgClasses = {
    default: 'bg-background',
    muted: 'bg-muted',
    primary: 'bg-primary text-primary-foreground',
    secondary: 'bg-secondary'
  };

  return (
    <section
      id={id}
      className={`section ${spacingClasses[spacing]} ${bgClasses[background]} ${className || ''}`}
      data-testid="section"
    >
      {children}
    </section>
  );
};

Section.displayName = 'Section';

describe('Section', () => {
  it('renderiza section com children', () => {
    render(
      <Section>
        <div data-testid="content">Conteúdo da Seção</div>
      </Section>
    );
    expect(screen.getByTestId('content')).toBeInTheDocument();
  });

  it('é um elemento section', () => {
    const { container } = render(<Section>Test</Section>);
    const section = container.querySelector('section');
    expect(section).toBeInTheDocument();
  });

  it('aceita id para navegação', () => {
    render(<Section id="sobre">Sobre</Section>);
    const section = screen.getByTestId('section');
    expect(section).toHaveAttribute('id', 'sobre');
  });

  it('applica espaçamento sm', () => {
    const { container } = render(<Section spacing="sm">Test</Section>);
    const section = container.firstChild as HTMLElement;
    expect(section.className).toContain('py-4');
  });

  it('applica espaçamento md (padrão)', () => {
    const { container } = render(<Section>Test</Section>);
    const section = container.firstChild as HTMLElement;
    expect(section.className).toContain('py-8');
  });

  it('applica espaçamento lg', () => {
    const { container } = render(<Section spacing="lg">Test</Section>);
    const section = container.firstChild as HTMLElement;
    expect(section.className).toContain('py-12');
  });

  it('applica espaçamento xl', () => {
    const { container } = render(<Section spacing="xl">Test</Section>);
    const section = container.firstChild as HTMLElement;
    expect(section.className).toContain('py-16');
  });

  it('applica background padrão', () => {
    const { container } = render(<Section>Test</Section>);
    const section = container.firstChild as HTMLElement;
    expect(section.className).toContain('bg-background');
  });

  it('applica background muted', () => {
    const { container } = render(<Section background="muted">Test</Section>);
    const section = container.firstChild as HTMLElement;
    expect(section.className).toContain('bg-muted');
  });

  it('applica background primary', () => {
    const { container } = render(<Section background="primary">Test</Section>);
    const section = container.firstChild as HTMLElement;
    expect(section.className).toContain('bg-primary');
  });

  it('applica background secondary', () => {
    const { container } = render(<Section background="secondary">Test</Section>);
    const section = container.firstChild as HTMLElement;
    expect(section.className).toContain('bg-secondary');
  });

  it('aplica classe customizada', () => {
    const { container } = render(
      <Section className="custom-section">Test</Section>
    );
    const section = container.firstChild as HTMLElement;
    expect(section.className).toContain('custom-section');
  });

  it('tem displayName correto', () => {
    expect(Section.displayName).toBe('Section');
  });

  it('renderiza múltiplas sections', () => {
    render(
      <>
        <Section id="sec1">Seção 1</Section>
        <Section id="sec2">Seção 2</Section>
      </>
    );
    expect(screen.getByText('Seção 1')).toBeInTheDocument();
    expect(screen.getByText('Seção 2')).toBeInTheDocument();
  });

  it('combina background primary com texto correto', () => {
    const { container } = render(<Section background="primary">Test</Section>);
    const section = container.firstChild as HTMLElement;
    expect(section.className).toContain('text-primary-foreground');
  });
});
