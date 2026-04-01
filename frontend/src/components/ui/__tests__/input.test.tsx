import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '../input';

describe('Input', () => {
  it('deve renderizar input vazio', () => {
    render(<Input />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('deve renderizar com label', () => {
    render(<Input label="Nome" />);
    expect(screen.getByText('Nome')).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('deve renderizar com placeholder', () => {
    render(<Input placeholder="Digite seu nome" />);
    expect(screen.getByPlaceholderText('Digite seu nome')).toBeInTheDocument();
  });

  it('deve renderizar mensagem de erro', () => {
    render(<Input error="Campo obrigatório" />);
    expect(screen.getByText('Campo obrigatório')).toBeInTheDocument();
    expect(screen.getByText('Campo obrigatório')).toHaveClass('text-[hsl(var(--destructive))]');
  });

  it('deve aplicar classe de erro no input', () => {
    const { container } = render(<Input error="Erro" />);
    const input = container.querySelector('input');
    expect(input?.className).toContain('border-[hsl(var(--destructive))]');
  });

  it('deve renderizar com ícone', () => {
    const { container } = render(<Input icon={<span data-testid="icon">🔍</span>} />);
    expect(screen.getByTestId('icon')).toBeInTheDocument();
    expect(container.querySelector('.absolute.left-3')).toBeInTheDocument();
  });

  it('deve aplicar padding extra quando tem ícone', () => {
    const { container } = render(<Input icon={<span>🔍</span>} />);
    const input = container.querySelector('input');
    expect(input?.className).toContain('pl-10');
  });

  it('deve chamar onChange ao digitar', () => {
    const handleChange = vi.fn();
    render(<Input onChange={handleChange} />);
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'teste' } });
    expect(handleChange).toHaveBeenCalled();
  });

  it('deve estar desabilitado quando disabled', () => {
    render(<Input disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('deve renderizar diferentes tipos de input', () => {
    const { rerender, container } = render(<Input type="text" />);
    expect(container.querySelector('input')).toHaveAttribute('type', 'text');

    rerender(<Input type="email" />);
    expect(container.querySelector('input')).toHaveAttribute('type', 'email');

    rerender(<Input type="password" />);
    expect(container.querySelector('input')).toHaveAttribute('type', 'password');
  });

  it('deve aplicar classe customizada', () => {
    const { container } = render(<Input className="custom-class" />);
    const input = container.querySelector('input');
    expect(input?.className).toContain('custom-class');
  });

  it('deve encaminhar ref corretamente', () => {
    const ref = { current: null as HTMLInputElement | null };
    render(<Input ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });

  it('deve ter displayName correto', () => {
    expect(Input.displayName).toBe('Input');
  });

  it('deve suportar value controlado', () => {
    const { rerender } = render(<Input value="inicial" readOnly />);
    expect(screen.getByRole('textbox')).toHaveValue('inicial');

    rerender(<Input value="atualizado" readOnly />);
    expect(screen.getByRole('textbox')).toHaveValue('atualizado');
  });
});
