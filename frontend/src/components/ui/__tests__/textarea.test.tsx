import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Textarea } from '../textarea';

describe('Textarea', () => {
  it('deve renderizar textarea vazio', () => {
    render(<Textarea />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('deve renderizar com placeholder', () => {
    render(<Textarea placeholder="Digite aqui..." />);
    expect(screen.getByPlaceholderText('Digite aqui...')).toBeInTheDocument();
  });

  it('deve chamar onChange ao digitar', () => {
    const handleChange = vi.fn();
    render(<Textarea onChange={handleChange} />);
    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: 'Texto de teste' } });
    expect(handleChange).toHaveBeenCalled();
  });

  it('deve renderizar com valor inicial', () => {
    render(<Textarea value="Valor inicial" readOnly />);
    expect(screen.getByRole('textbox')).toHaveValue('Valor inicial');
  });

  it('deve estar desabilitado quando disabled', () => {
    render(<Textarea disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('deve ter altura mínima de 80px', () => {
    render(<Textarea />);
    const textarea = screen.getByRole('textbox');
    expect(textarea.className).toContain('min-h-[80px]');
  });

  it('deve ter largura total', () => {
    render(<Textarea />);
    const textarea = screen.getByRole('textbox');
    expect(textarea.className).toContain('w-full');
  });

  it('deve aplicar classe customizada', () => {
    render(<Textarea className="custom-textarea" />);
    const textarea = screen.getByRole('textbox');
    expect(textarea.className).toContain('custom-textarea');
  });

  it('deve ter borda arredondada', () => {
    render(<Textarea />);
    const textarea = screen.getByRole('textbox');
    expect(textarea.className).toContain('rounded-md');
  });

  it('deve ter estilo de borda', () => {
    render(<Textarea />);
    const textarea = screen.getByRole('textbox');
    expect(textarea.className).toContain('border');
    expect(textarea.className).toContain('border-input');
  });

  it('deve encaminhar ref corretamente', () => {
    const ref = { current: null as HTMLTextAreaElement | null };
    render(<Textarea ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLTextAreaElement);
  });

  it('deve ter displayName correto', () => {
    expect(Textarea.displayName).toBe('Textarea');
  });

  it('deve aceitar atributo rows', () => {
    render(<Textarea rows={5} />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveAttribute('rows', '5');
  });

  it('deve aceitar atributo cols', () => {
    render(<Textarea cols={50} />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveAttribute('cols', '50');
  });

  it('deve aceitar atributo maxLength', () => {
    render(<Textarea maxLength={100} />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveAttribute('maxLength', '100');
  });

  it('deve aceitar atributo required', () => {
    render(<Textarea required />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveAttribute('required');
  });

  it('deve aceitar atributo name', () => {
    render(<Textarea name="descricao" />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveAttribute('name', 'descricao');
  });

  it('deve aceitar atributo id', () => {
    render(<Textarea id="descricao-id" />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveAttribute('id', 'descricao-id');
  });

  it('deve suportar value controlado', () => {
    const { rerender } = render(<Textarea value="inicial" readOnly />);
    expect(screen.getByRole('textbox')).toHaveValue('inicial');

    rerender(<Textarea value="atualizado" readOnly />);
    expect(screen.getByRole('textbox')).toHaveValue('atualizado');
  });

  it('deve renderizar com foco', () => {
    render(<Textarea autoFocus />);
    const textarea = screen.getByRole('textbox');
    expect(document.activeElement).toBe(textarea);
  });

  it('deve ter estilos para estado disabled', () => {
    render(<Textarea disabled />);
    const textarea = screen.getByRole('textbox');
    expect(textarea.className).toContain('disabled:cursor-not-allowed');
    expect(textarea.className).toContain('disabled:opacity-50');
  });

  it('deve ter estilos de focus-visible', () => {
    render(<Textarea />);
    const textarea = screen.getByRole('textbox');
    expect(textarea.className).toContain('focus-visible:outline-none');
    expect(textarea.className).toContain('focus-visible:ring-2');
  });

  it('deve renderizar múltiplos textareas', () => {
    render(
      <>
        <Textarea placeholder="Textarea 1" />
        <Textarea placeholder="Textarea 2" />
        <Textarea placeholder="Textarea 3" />
      </>
    );
    expect(screen.getByPlaceholderText('Textarea 1')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Textarea 2')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Textarea 3')).toBeInTheDocument();
  });
});
