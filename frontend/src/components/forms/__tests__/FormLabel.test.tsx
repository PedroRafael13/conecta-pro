import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

interface FormLabelProps {
  htmlFor: string;
  children: React.ReactNode;
  required?: boolean;
  className?: string;
}

const FormLabel: React.FC<FormLabelProps> = ({
  htmlFor,
  children,
  required,
  className
}) => {
  return (
    <label
      htmlFor={htmlFor}
      className={`form-label ${className || ''}`}
      data-testid="form-label"
    >
      {children}
      {required && <span className="required-indicator" data-testid="required">*</span>}
    </label>
  );
};

FormLabel.displayName = 'FormLabel';

describe('FormLabel', () => {
  it('renderiza texto do label', () => {
    render(<FormLabel htmlFor="nome">Nome Completo</FormLabel>);
    expect(screen.getByText('Nome Completo')).toBeInTheDocument();
  });

  it('tem atributo htmlFor correto', () => {
    render(<FormLabel htmlFor="email">Email</FormLabel>);
    const label = screen.getByText('Email');
    expect(label).toHaveAttribute('for', 'email');
  });

  it('renderiza indicador de obrigatório quando required', () => {
    render(<FormLabel htmlFor="nome" required>Nome</FormLabel>);
    expect(screen.getByTestId('required')).toBeInTheDocument();
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('não renderiza indicador quando não é required', () => {
    render(<FormLabel htmlFor="nome">Nome</FormLabel>);
    expect(screen.queryByTestId('required')).not.toBeInTheDocument();
  });

  it('aplica classe customizada', () => {
    render(
      <FormLabel htmlFor="teste" className="custom-label">Teste</FormLabel>
    );
    const label = screen.getByTestId('form-label');
    expect(label).toHaveClass('custom-label');
  });

  it('é um elemento label', () => {
    render(<FormLabel htmlFor="campo">Campo</FormLabel>);
    const label = screen.getByTestId('form-label');
    expect(label.tagName.toLowerCase()).toBe('label');
  });

  it('aceita children complexos', () => {
    render(
      <FormLabel htmlFor="campo">
        <span data-testid="icon">👤</span>
        Nome
      </FormLabel>
    );
    expect(screen.getByTestId('icon')).toBeInTheDocument();
    expect(screen.getByText('Nome')).toBeInTheDocument();
  });

  it('tem displayName correto', () => {
    expect(FormLabel.displayName).toBe('FormLabel');
  });

  it('renderiza múltiplos labels', () => {
    render(
      <>
        <FormLabel htmlFor="nome">Nome</FormLabel>
        <FormLabel htmlFor="email">Email</FormLabel>
        <FormLabel htmlFor="telefone">Telefone</FormLabel>
      </>
    );
    expect(screen.getByText('Nome')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByText('Telefone')).toBeInTheDocument();
  });

  it('associa corretamente com input', () => {
    render(
      <>
        <FormLabel htmlFor="usuario">Usuário</FormLabel>
        <input id="usuario" data-testid="input-usuario" />
      </>
    );
    const label = screen.getByText('Usuário');
    const input = screen.getByTestId('input-usuario');
    expect(label).toHaveAttribute('for', 'usuario');
    expect(input).toHaveAttribute('id', 'usuario');
  });
});
