import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Alert, AlertTitle, AlertDescription } from '../alert';

describe('Alert', () => {
  it('deve renderizar alert com conteúdo', () => {
    render(<Alert>Alerta importante</Alert>);
    expect(screen.getByText('Alerta importante')).toBeInTheDocument();
  });

  it('deve renderizar com variant padrão', () => {
    const { container } = render(<Alert>Default Alert</Alert>);
    const alert = container.firstChild as HTMLElement;
    expect(alert.className).toContain('bg-background');
    expect(alert.className).toContain('text-foreground');
  });

  it('deve renderizar com variant destructive', () => {
    const { container } = render(<Alert variant="destructive">Destructive Alert</Alert>);
    const alert = container.firstChild as HTMLElement;
    expect(alert.className).toContain('border-destructive');
    expect(alert.className).toContain('text-destructive');
  });

  it('deve aplicar classe customizada', () => {
    const { container } = render(<Alert className="custom-alert">Custom</Alert>);
    const alert = container.firstChild as HTMLElement;
    expect(alert.className).toContain('custom-alert');
  });

  it('deve ter borda arredondada', () => {
    const { container } = render(<Alert>Borda</Alert>);
    const alert = container.firstChild as HTMLElement;
    expect(alert.className).toContain('rounded-lg');
  });

  it('deve ter estilo de borda', () => {
    const { container } = render(<Alert>Borda</Alert>);
    const alert = container.firstChild as HTMLElement;
    expect(alert.className).toContain('border');
  });

  it('deve renderizar AlertTitle', () => {
    render(
      <Alert>
        <AlertTitle>Título do Alerta</AlertTitle>
      </Alert>
    );
    const title = screen.getByText('Título do Alerta');
    expect(title.tagName.toLowerCase()).toBe('h5');
    expect(title.className).toContain('font-medium');
  });

  it('deve renderizar AlertDescription', () => {
    render(
      <Alert>
        <AlertDescription>Descrição do alerta</AlertDescription>
      </Alert>
    );
    const desc = screen.getByText('Descrição do alerta');
    expect(desc.className).toContain('text-sm');
  });

  it('deve renderizar alert completo com título e descrição', () => {
    render(
      <Alert>
        <AlertTitle>Atenção</AlertTitle>
        <AlertDescription>Este é um alerta importante.</AlertDescription>
      </Alert>
    );
    expect(screen.getByText('Atenção')).toBeInTheDocument();
    expect(screen.getByText('Este é um alerta importante.')).toBeInTheDocument();
  });

  it('deve encaminhar ref corretamente no Alert', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(<Alert ref={ref}>Com Ref</Alert>);
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve ter displayName correto para Alert', () => {
    expect(Alert.displayName).toBe('Alert');
  });

  it('deve ter displayName correto para AlertTitle', () => {
    expect(AlertTitle.displayName).toBe('AlertTitle');
  });

  it('deve ter displayName correto para AlertDescription', () => {
    expect(AlertDescription.displayName).toBe('AlertDescription');
  });

  it('deve aplicar classe customizada no AlertTitle', () => {
    render(
      <Alert>
        <AlertTitle className="custom-title">Título</AlertTitle>
      </Alert>
    );
    const title = screen.getByText('Título');
    expect(title.className).toContain('custom-title');
  });

  it('deve aplicar classe customizada no AlertDescription', () => {
    render(
      <Alert>
        <AlertDescription className="custom-desc">Descrição</AlertDescription>
      </Alert>
    );
    const desc = screen.getByText('Descrição');
    expect(desc.className).toContain('custom-desc');
  });

  it('deve suportar children complexos', () => {
    render(
      <Alert>
        <span data-testid="icon">⚠️</span>
        <AlertTitle>Título</AlertTitle>
        <AlertDescription>Descrição</AlertDescription>
      </Alert>
    );
    expect(screen.getByTestId('icon')).toBeInTheDocument();
    expect(screen.getByText('Título')).toBeInTheDocument();
    expect(screen.getByText('Descrição')).toBeInTheDocument();
  });
});
