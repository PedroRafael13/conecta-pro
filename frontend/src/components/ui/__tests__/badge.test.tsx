import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge, badgeVariants } from '../badge';

describe('Badge', () => {
  it('deve renderizar badge com texto', () => {
    render(<Badge>Novo</Badge>);
    expect(screen.getByText('Novo')).toBeInTheDocument();
  });

  it('deve renderizar com variant padrão', () => {
    const { container } = render(<Badge>Default</Badge>);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('bg-primary');
    expect(badge.className).toContain('text-primary-foreground');
  });

  it('deve renderizar com variant secondary', () => {
    render(<Badge variant="secondary">Secondary</Badge>);
    const badge = screen.getByText('Secondary');
    expect(badge.className).toContain('bg-secondary');
  });

  it('deve renderizar com variant destructive', () => {
    render(<Badge variant="destructive">Destructive</Badge>);
    const badge = screen.getByText('Destructive');
    expect(badge.className).toContain('bg-destructive');
  });

  it('deve renderizar com variant success', () => {
    render(<Badge variant="success">Success</Badge>);
    const badge = screen.getByText('Success');
    expect(badge.className).toContain('bg-green-500');
  });

  it('deve renderizar com variant warning', () => {
    render(<Badge variant="warning">Warning</Badge>);
    const badge = screen.getByText('Warning');
    expect(badge.className).toContain('bg-yellow-500');
  });

  it('deve renderizar com variant outline', () => {
    render(<Badge variant="outline">Outline</Badge>);
    const badge = screen.getByText('Outline');
    expect(badge.className).toContain('text-foreground');
  });

  it('deve aplicar classe customizada', () => {
    const { container } = render(<Badge className="custom-badge">Custom</Badge>);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('custom-badge');
  });

  it('deve ter formato arredondado', () => {
    const { container } = render(<Badge>Arredondado</Badge>);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('rounded-full');
  });

  it('deve ter estilo inline-flex', () => {
    const { container } = render(<Badge>Inline</Badge>);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('inline-flex');
  });

  it('deve renderizar com ícone', () => {
    render(
      <Badge>
        <span data-testid="icon">✓</span>
        Com Ícone
      </Badge>
    );
    expect(screen.getByTestId('icon')).toBeInTheDocument();
    expect(screen.getByText('Com Ícone')).toBeInTheDocument();
  });

  it('deve ter tamanho de texto xs', () => {
    const { container } = render(<Badge>Pequeno</Badge>);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('text-xs');
  });

  it('deve ter fonte semibold', () => {
    const { container } = render(<Badge>Semibold</Badge>);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('font-semibold');
  });

  it('deve encaminhar props adicionais', () => {
    render(<Badge data-testid="custom-badge">Props</Badge>);
    expect(screen.getByTestId('custom-badge')).toBeInTheDocument();
  });
});

describe('badgeVariants', () => {
  it('deve retornar classes para variant default', () => {
    const classes = badgeVariants({ variant: 'default' });
    expect(classes).toContain('bg-primary');
  });

  it('deve retornar classes para variant secondary', () => {
    const classes = badgeVariants({ variant: 'secondary' });
    expect(classes).toContain('bg-secondary');
  });

  it('deve retornar classes para variant success', () => {
    const classes = badgeVariants({ variant: 'success' });
    expect(classes).toContain('bg-green-500');
  });

  it('deve usar variant default quando não especificado', () => {
    const classes = badgeVariants({});
    expect(classes).toContain('bg-primary');
  });
});
