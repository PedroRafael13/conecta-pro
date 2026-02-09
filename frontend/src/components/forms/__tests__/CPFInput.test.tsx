import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React, { useState } from 'react';

interface CPFInputProps {
  value?: string;
  onChange?: (value: string) => void;
  label?: string;
  error?: string;
  placeholder?: string;
}

const formatCPF = (value: string): string => {
  const numbers = value.replace(/\D/g, '').slice(0, 11);
  return numbers
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
};

const isValidCPF = (cpf: string): boolean => {
  const numbers = cpf.replace(/\D/g, '');
  if (numbers.length !== 11) return false;
  if (/^(\d)\1{10}$/.test(numbers)) return false;

  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(numbers.charAt(i)) * (10 - i);
  }
  let rev = 11 - (sum % 11);
  if (rev === 10 || rev === 11) rev = 0;
  if (rev !== parseInt(numbers.charAt(9))) return false;

  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(numbers.charAt(i)) * (11 - i);
  }
  rev = 11 - (sum % 11);
  if (rev === 10 || rev === 11) rev = 0;

  return rev === parseInt(numbers.charAt(10));
};

const CPFInput: React.FC<CPFInputProps> = ({
  value = '',
  onChange,
  label,
  error,
  placeholder
}) => {
  const [displayValue, setDisplayValue] = useState(formatCPF(value));

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCPF(e.target.value);
    setDisplayValue(formatted);
    onChange?.(formatted);
  };

  return (
    <div className="cpf-input" data-testid="cpf-input">
      {label && <label className="cpf-label">{label}</label>}
      <input
        type="text"
        value={displayValue}
        onChange={handleChange}
        placeholder={placeholder || '000.000.000-00'}
        data-testid="cpf-field"
        maxLength={14}
        className={error ? 'has-error' : ''}
      />
      {error && <span className="error-message" data-testid="error">{error}</span>}
    </div>
  );
};

CPFInput.displayName = 'CPFInput';

describe('CPFInput', () => {
  it('renderiza input de CPF', () => {
    render(<CPFInput />);
    expect(screen.getByTestId('cpf-field')).toBeInTheDocument();
  });

  it('renderiza com label', () => {
    render(<CPFInput label="CPF" />);
    expect(screen.getByText('CPF')).toBeInTheDocument();
  });

  it('formata CPF completo', () => {
    render(<CPFInput value="12345678901" />);
    const input = screen.getByTestId('cpf-field') as HTMLInputElement;
    expect(input.value).toBe('123.456.789-01');
  });

  it('formata entrada em tempo real', () => {
    render(<CPFInput />);
    const input = screen.getByTestId('cpf-field');
    fireEvent.change(input, { target: { value: '12345678901' } });
    expect((input as HTMLInputElement).value).toBe('123.456.789-01');
  });

  it('chama onChange com valor formatado', () => {
    const handleChange = vi.fn();
    render(<CPFInput onChange={handleChange} />);
    const input = screen.getByTestId('cpf-field');
    fireEvent.change(input, { target: { value: '52998224725' } });
    expect(handleChange).toHaveBeenCalledWith('529.982.247-25');
  });

  it('ignora caracteres não numéricos', () => {
    render(<CPFInput />);
    const input = screen.getByTestId('cpf-field');
    fireEvent.change(input, { target: { value: 'abc123.456.789-01' } });
    expect((input as HTMLInputElement).value).toBe('123.456.789-01');
  });

  it('limita a 11 dígitos', () => {
    render(<CPFInput />);
    const input = screen.getByTestId('cpf-field');
    fireEvent.change(input, { target: { value: '123456789012345' } });
    expect((input as HTMLInputElement).value.length).toBeLessThanOrEqual(14);
  });

  it('mostra placeholder', () => {
    render(<CPFInput placeholder="Digite o CPF" />);
    const input = screen.getByTestId('cpf-field');
    expect(input).toHaveAttribute('placeholder', 'Digite o CPF');
  });

  it('mostra erro quando fornecido', () => {
    render(<CPFInput error="CPF inválido" />);
    expect(screen.getByText('CPF inválido')).toBeInTheDocument();
  });

  it('aplica classe de erro', () => {
    render(<CPFInput error="Erro" />);
    const input = screen.getByTestId('cpf-field');
    expect(input).toHaveClass('has-error');
  });

  it('formata número incompleto', () => {
    render(<CPFInput value="123456" />);
    const input = screen.getByTestId('cpf-field') as HTMLInputElement;
    expect(input.value).toBe('123.456');
  });

  it('tem displayName correto', () => {
    expect(CPFInput.displayName).toBe('CPFInput');
  });

  it('limita tamanho máximo do input', () => {
    render(<CPFInput />);
    const input = screen.getByTestId('cpf-field');
    expect(input).toHaveAttribute('maxLength', '14');
  });
});

describe('CPF Validation', () => {
  it('valida CPF correto', () => {
    expect(isValidCPF('52998224725')).toBe(true);
    expect(isValidCPF('529.982.247-25')).toBe(true);
  });

  it('rejeita CPF com dígitos repetidos', () => {
    expect(isValidCPF('11111111111')).toBe(false);
    expect(isValidCPF('00000000000')).toBe(false);
  });

  it('rejeita CPF incompleto', () => {
    expect(isValidCPF('1234567890')).toBe(false);
  });

  it('rejeita CPF inválido', () => {
    expect(isValidCPF('12345678901')).toBe(false);
  });
});
