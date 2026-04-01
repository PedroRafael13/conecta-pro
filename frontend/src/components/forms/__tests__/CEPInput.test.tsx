import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React, { useState } from 'react';

interface CEPInputProps {
  value?: string;
  onChange?: (value: string) => void;
  label?: string;
  error?: string;
  placeholder?: string;
  onBlur?: () => void;
}

const formatCEP = (value: string): string => {
  const numbers = value.replace(/\D/g, '').slice(0, 8);
  return numbers.replace(/(\d{5})(\d{1,3})$/, '$1-$2');
};

const isValidCEP = (cep: string): boolean => {
  const numbers = cep.replace(/\D/g, '');
  return numbers.length === 8;
};

const CEPInput: React.FC<CEPInputProps> = ({
  value = '',
  onChange,
  label,
  error,
  placeholder,
  onBlur
}) => {
  const [displayValue, setDisplayValue] = useState(formatCEP(value));

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCEP(e.target.value);
    setDisplayValue(formatted);
    onChange?.(formatted);
  };

  return (
    <div className="cep-input" data-testid="cep-input">
      {label && <label className="cep-label">{label}</label>}
      <input
        type="text"
        value={displayValue}
        onChange={handleChange}
        onBlur={onBlur}
        placeholder={placeholder || '00000-000'}
        data-testid="cep-field"
        maxLength={9}
        className={error ? 'has-error' : ''}
      />
      {error && <span className="error-message" data-testid="error">{error}</span>}
    </div>
  );
};

CEPInput.displayName = 'CEPInput';

describe('CEPInput', () => {
  it('renderiza input de CEP', () => {
    render(<CEPInput />);
    expect(screen.getByTestId('cep-field')).toBeInTheDocument();
  });

  it('renderiza com label', () => {
    render(<CEPInput label="CEP" />);
    expect(screen.getByText('CEP')).toBeInTheDocument();
  });

  it('formata CEP completo', () => {
    render(<CEPInput value="01001000" />);
    const input = screen.getByTestId('cep-field') as HTMLInputElement;
    expect(input.value).toBe('01001-000');
  });

  it('formata entrada em tempo real', () => {
    render(<CEPInput />);
    const input = screen.getByTestId('cep-field');
    fireEvent.change(input, { target: { value: '01001000' } });
    expect((input as HTMLInputElement).value).toBe('01001-000');
  });

  it('chama onChange com valor formatado', () => {
    const handleChange = vi.fn();
    render(<CEPInput onChange={handleChange} />);
    const input = screen.getByTestId('cep-field');
    fireEvent.change(input, { target: { value: '01001000' } });
    expect(handleChange).toHaveBeenCalledWith('01001-000');
  });

  it('chama onBlur quando campo perde foco', () => {
    const handleBlur = vi.fn();
    render(<CEPInput onBlur={handleBlur} />);
    const input = screen.getByTestId('cep-field');
    fireEvent.blur(input);
    expect(handleBlur).toHaveBeenCalled();
  });

  it('ignora caracteres não numéricos', () => {
    render(<CEPInput />);
    const input = screen.getByTestId('cep-field');
    fireEvent.change(input, { target: { value: 'abc01001-000' } });
    expect((input as HTMLInputElement).value).toBe('01001-000');
  });

  it('limita a 8 dígitos', () => {
    render(<CEPInput />);
    const input = screen.getByTestId('cep-field');
    fireEvent.change(input, { target: { value: '0100100012345' } });
    expect((input as HTMLInputElement).value.length).toBeLessThanOrEqual(9);
  });

  it('mostra placeholder', () => {
    render(<CEPInput placeholder="Digite o CEP" />);
    const input = screen.getByTestId('cep-field');
    expect(input).toHaveAttribute('placeholder', 'Digite o CEP');
  });

  it('mostra erro quando fornecido', () => {
    render(<CEPInput error="CEP inválido" />);
    expect(screen.getByText('CEP inválido')).toBeInTheDocument();
  });

  it('aplica classe de erro', () => {
    render(<CEPInput error="Erro" />);
    const input = screen.getByTestId('cep-field');
    expect(input).toHaveClass('has-error');
  });

  it('formata número incompleto', () => {
    render(<CEPInput value="01001" />);
    const input = screen.getByTestId('cep-field') as HTMLInputElement;
    expect(input.value).toBe('01001');
  });

  it('tem displayName correto', () => {
    expect(CEPInput.displayName).toBe('CEPInput');
  });

  it('limita tamanho máximo do input', () => {
    render(<CEPInput />);
    const input = screen.getByTestId('cep-field');
    expect(input).toHaveAttribute('maxLength', '9');
  });

  it('aceita valor vazio', () => {
    render(<CEPInput value="" />);
    const input = screen.getByTestId('cep-field') as HTMLInputElement;
    expect(input.value).toBe('');
  });
});

describe('CEP Validation', () => {
  it('valida CEP correto', () => {
    expect(isValidCEP('01001000')).toBe(true);
    expect(isValidCEP('01001-000')).toBe(true);
  });

  it('rejeita CEP incompleto', () => {
    expect(isValidCEP('01001')).toBe(false);
    expect(isValidCEP('01001-00')).toBe(false);
  });

  it('rejeita CEP vazio', () => {
    expect(isValidCEP('')).toBe(false);
  });

  it('rejeita CEP com letras', () => {
    expect(isValidCEP('01001a00')).toBe(false);
  });
});
