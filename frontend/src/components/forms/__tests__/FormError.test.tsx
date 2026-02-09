import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

interface FormErrorProps {
  message?: string;
  className?: string;
}

const FormError: React.FC<FormErrorProps> = ({ message, className }) => {
  if (!message) return null;

  return (
    <span
      className={`form-error text-destructive text-sm ${className || ''}`}
      data-testid="form-error"
      role="alert"
    >
      {message}
    </span>
  );
};

FormError.displayName = 'FormError';

describe('FormError', () => {
  it('renderiza mensagem de erro', () => {
    render(<FormError message="Campo obrigatório" />);
    expect(screen.getByText('Campo obrigatório')).toBeInTheDocument();
  });

  it('retorna null quando não há mensagem', () => {
    const { container } = render(<FormError />);
    expect(container.firstChild).toBeNull();
  });

  it('tem role alert para acessibilidade', () => {
    render(<FormError message="Erro" />);
    const error = screen.getByRole('alert');
    expect(error).toBeInTheDocument();
  });

  it('aplica classe customizada', () => {
    render(<FormError message="Erro" className="custom-error" />);
    const error = screen.getByTestId('form-error');
    expect(error).toHaveClass('custom-error');
  });

  it('tem cor de erro (text-destructive)', () => {
    render(<FormError message="Erro" />);
    const error = screen.getByTestId('form-error');
    expect(error).toHaveClass('text-destructive');
  });

  it('tem tamanho de texto sm', () => {
    render(<FormError message="Erro" />);
    const error = screen.getByTestId('form-error');
    expect(error).toHaveClass('text-sm');
  });

  it('tem displayName correto', () => {
    expect(FormError.displayName).toBe('FormError');
  });

  it('renderiza mensagens longas', () => {
    const longMessage = 'Este é um erro muito longo que explica detalhadamente o que aconteceu de errado';
    render(<FormError message={longMessage} />);
    expect(screen.getByText(longMessage)).toBeInTheDocument();
  });

  it('renderiza mensagem vazia', () => {
    render(<FormError message="" />);
    expect(screen.queryByTestId('form-error')).not.toBeInTheDocument();
  });

  it('renderiza múltiplos erros', () => {
    render(
      <>
        <FormError message="Erro 1" />
        <FormError message="Erro 2" />
        <FormError message="Erro 3" />
      </>
    );
    expect(screen.getByText('Erro 1')).toBeInTheDocument();
    expect(screen.getByText('Erro 2')).toBeInTheDocument();
    expect(screen.getByText('Erro 3')).toBeInTheDocument();
  });
});
