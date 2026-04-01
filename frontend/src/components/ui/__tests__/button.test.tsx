import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../button';

describe('Button', () => {
  it('deve renderizar com texto', () => {
    render(<Button>Clique aqui</Button>);
    expect(screen.getByText('Clique aqui')).toBeInTheDocument();
  });

  it('deve chamar onClick ao clicar', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Clique</Button>);
    fireEvent.click(screen.getByText('Clique'));
    expect(handleClick).toHaveBeenCalled();
  });

  it('deve estar desabilitado quando disabled', () => {
    render(<Button disabled>Desabilitado</Button>);
    expect(screen.getByText('Desabilitado')).toBeDisabled();
  });

  it('deve renderizar variantes corretamente', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>);
    expect(screen.getByText('Primary')).toBeInTheDocument();

    rerender(<Button variant="secondary">Secondary</Button>);
    expect(screen.getByText('Secondary')).toBeInTheDocument();

    rerender(<Button variant="ghost">Ghost</Button>);
    expect(screen.getByText('Ghost')).toBeInTheDocument();

    rerender(<Button variant="danger">Danger</Button>);
    expect(screen.getByText('Danger')).toBeInTheDocument();

    rerender(<Button variant="outline">Outline</Button>);
    expect(screen.getByText('Outline')).toBeInTheDocument();
  });

  it('deve renderizar tamanhos corretamente', () => {
    const { rerender } = render(<Button size="sm">Small</Button>);
    expect(screen.getByText('Small')).toBeInTheDocument();

    rerender(<Button size="md">Medium</Button>);
    expect(screen.getByText('Medium')).toBeInTheDocument();

    rerender(<Button size="lg">Large</Button>);
    expect(screen.getByText('Large')).toBeInTheDocument();

    rerender(<Button size="icon">Icon</Button>);
    expect(screen.getByText('Icon')).toBeInTheDocument();
  });

  it('deve mostrar spinner quando isLoading é true', () => {
    const { container } = render(<Button isLoading>Carregando</Button>);
    const spinner = container.querySelector('svg');
    expect(spinner).toBeInTheDocument();
    expect(spinner?.classList.contains('animate-spin')).toBe(true);
  });

  it('deve estar desabilitado quando isLoading é true', () => {
    render(<Button isLoading>Carregando</Button>);
    expect(screen.getByText('Carregando')).toBeDisabled();
  });

  it('deve aplicar classe customizada', () => {
    const { container } = render(<Button className="custom-class">Custom</Button>);
    const button = container.querySelector('button');
    expect(button?.className).toContain('custom-class');
  });

  it('deve renderizar ícones e conteúdo junto com spinner', () => {
    const { container } = render(
      <Button isLoading>
        <span data-testid="icon">Icon</span>
        Salvar
      </Button>
    );
    expect(screen.getByText('Salvar')).toBeInTheDocument();
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('deve encaminhar ref corretamente', () => {
    const ref = { current: null as HTMLButtonElement | null };
    render(<Button ref={ref}>Com Ref</Button>);
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });

  it('deve ter displayName correto', () => {
    expect(Button.displayName).toBe('Button');
  });
});
