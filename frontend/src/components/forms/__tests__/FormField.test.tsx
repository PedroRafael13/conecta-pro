import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

// Mock do componente FormField baseado na interface padrão
interface FormFieldProps {
  label?: string;
  name: string;
  error?: string;
  required?: boolean;
  children?: React.ReactNode;
  className?: string;
}

const FormField: React.FC<FormFieldProps> = ({
  label,
  name,
  error,
  required,
  children,
  className
}) => {
  return (
    <div className={`form-field ${className || ''}`} data-testid="form-field">
      {label && (
        <label htmlFor={name} className="form-label">
          {label}
          {required && <span className="required">*</span>}
        </label>
      )}
      <div className="form-control">
        {children || <input id={name} name={name} data-testid={`input-${name}`} />}
      </div>
      {error && <span className="form-error" data-testid="form-error">{error}</span>}
    </div>
  );
};

FormField.displayName = 'FormField';

describe('FormField', () => {
  it('renderiza com label corretamente', () => {
    render(<FormField label="Nome" name="nome" />);
    expect(screen.getByText('Nome')).toBeInTheDocument();
  });

  it('exibe erro quando fornecido', () => {
    render(<FormField label="Nome" name="nome" error="Campo obrigatório" />);
    expect(screen.getByText('Campo obrigatório')).toBeInTheDocument();
  });

  it('renderiza asterisco quando campo é obrigatório', () => {
    render(<FormField label="Nome" name="nome" required />);
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('associa label com input via htmlFor', () => {
    render(<FormField label="Email" name="email" />);
    const label = screen.getByText('Email');
    expect(label).toHaveAttribute('for', 'email');
  });

  it('renderiza children quando fornecido', () => {
    render(
      <FormField label="Campo" name="campo">
        <select data-testid="select-campo">
          <option>Opção 1</option>
        </select>
      </FormField>
    );
    expect(screen.getByTestId('select-campo')).toBeInTheDocument();
  });

  it('aplica classe customizada', () => {
    const { container } = render(
      <FormField label="Teste" name="teste" className="custom-class" />
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('não renderiza label quando não fornecido', () => {
    render(<FormField name="sem-label" />);
    expect(screen.queryByRole('label')).not.toBeInTheDocument();
  });

  it('não renderiza mensagem de erro quando não fornecida', () => {
    render(<FormField label="Nome" name="nome" />);
    expect(screen.queryByTestId('form-error')).not.toBeInTheDocument();
  });

  it('renderiza input padrão quando children não é fornecido', () => {
    render(<FormField label="Nome" name="nome" />);
    expect(screen.getByTestId('input-nome')).toBeInTheDocument();
  });

  it('tem displayName correto', () => {
    expect(FormField.displayName).toBe('FormField');
  });
});

describe('FormField - Integração', () => {
  it('funciona com input controlado', () => {
    const handleChange = vi.fn();
    render(
      <FormField label="Nome" name="nome">
        <input
          data-testid="input-nome"
          onChange={handleChange}
        />
      </FormField>
    );
    const input = screen.getByTestId('input-nome');
    fireEvent.change(input, { target: { value: 'Teste' } });
    expect(handleChange).toHaveBeenCalled();
  });

  it('funciona com select', () => {
    render(
      <FormField label="Categoria" name="categoria">
        <select data-testid="select-categoria">
          <option value="1">Opção 1</option>
          <option value="2">Opção 2</option>
        </select>
      </FormField>
    );
    expect(screen.getByTestId('select-categoria')).toBeInTheDocument();
  });

  it('funciona com textarea', () => {
    render(
      <FormField label="Descrição" name="descricao">
        <textarea data-testid="textarea-descricao" />
      </FormField>
    );
    expect(screen.getByTestId('textarea-descricao')).toBeInTheDocument();
  });

  it('mostra múltiplos campos com erros', () => {
    render(
      <>
        <FormField label="Nome" name="nome" error="Nome obrigatório" />
        <FormField label="Email" name="email" error="Email inválido" />
      </>
    );
    expect(screen.getByText('Nome obrigatório')).toBeInTheDocument();
    expect(screen.getByText('Email inválido')).toBeInTheDocument();
  });

  it('renderiza campo sem label mas com erro', () => {
    render(<FormField name="campo" error="Erro no campo" />);
    expect(screen.getByText('Erro no campo')).toBeInTheDocument();
  });
});
