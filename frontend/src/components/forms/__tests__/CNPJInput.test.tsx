import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React, { useState } from 'react';

interface CNPJInputProps {
  value?: string;
  onChange?: (value: string) => void;
  label?: string;
  error?: string;
  placeholder?: string;
}

const formatCNPJ = (value: string): string => {
  const numbers = value.replace(/\D/g, '').slice(0, 14);
  return numbers
    .replace(/(\d{2})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1/$2')
    .replace(/(\d{4})(\d{1,2})$/, '$1-$2');
};

const isValidCNPJ = (cnpj: string): boolean => {
  const numbers = cnpj.replace(/\D/g, '');
  if (numbers.length !== 14) return false;
  if (/^(\d)\1{13}$/.test(numbers)) return false;

  let size = numbers.length - 2;
  let numbersStr = numbers.substring(0, size);
  const digits = numbers.substring(size);
  let sum = 0;
  let pos = size - 7;

  for (let i = size; i >= 1; i--) {
    sum += parseInt(numbersStr.charAt(size - i)) * pos--;
    if (pos < 2) pos = 9;
  }

  let result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
  if (result !== parseInt(digits.charAt(0))) return false;

  size = size + 1;
  numbersStr = numbers.substring(0, size);
  sum = 0;
  pos = size - 7;

  for (let i = size; i >= 1; i--) {
    sum += parseInt(numbersStr.charAt(size - i)) * pos--;
    if (pos < 2) pos = 9;
  }

  result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
  return result === parseInt(digits.charAt(1));
};

const CNPJInput: React.FC<CNPJInputProps> = ({
  value = '',
  onChange,
  label,
  error,
  placeholder
}) => {
  const [displayValue, setDisplayValue] = useState(formatCNPJ(value));

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCNPJ(e.target.value);
    setDisplayValue(formatted);
    onChange?.(formatted);
  };

  return (
    <div className="cnpj-input" data-testid="cnpj-input">
      {label && <label className="cnpj-label">{label}</label>}
      <input
        type="text"
        value={displayValue}
        onChange={handleChange}
        placeholder={placeholder || '00.000.000/0000-00'}
        data-testid="cnpj-field"
        maxLength={18}
        className={error ? 'has-error' : ''}
      />
      {error && <span className="error-message" data-testid="error">{error}</span>}
    </div>
  );
};

CNPJInput.displayName = 'CNPJInput';

describe('CNPJInput', () => {
  it('renderiza input de CNPJ', () => {
    render(<CNPJInput />);
    expect(screen.getByTestId('cnpj-field')).toBeInTheDocument();
  });

  it('renderiza com label', () => {
    render(<CNPJInput label="CNPJ" />);
    expect(screen.getByText('CNPJ')).toBeInTheDocument();
  });

  it('formata CNPJ completo', () => {
    render(<CNPJInput value="11222333000181" />);
    const input = screen.getByTestId('cnpj-field') as HTMLInputElement;
    expect(input.value).toBe('11.222.333/0001-81');
  });

  it('formata entrada em tempo real', () => {
    render(<CNPJInput />);
    const input = screen.getByTestId('cnpj-field');
    fireEvent.change(input, { target: { value: '11222333000181' } });
    expect((input as HTMLInputElement).value).toBe('11.222.333/0001-81');
  });

  it('chama onChange com valor formatado', () => {
    const handleChange = vi.fn();
    render(<CNPJInput onChange={handleChange} />);
    const input = screen.getByTestId('cnpj-field');
    fireEvent.change(input, { target: { value: '11222333000181' } });
    expect(handleChange).toHaveBeenCalledWith('11.222.333/0001-81');
  });

  it('ignora caracteres não numéricos', () => {
    render(<CNPJInput />);
    const input = screen.getByTestId('cnpj-field');
    fireEvent.change(input, { target: { value: 'abc11.222.333/0001-81' } });
    expect((input as HTMLInputElement).value).toBe('11.222.333/0001-81');
  });

  it('limita a 14 dígitos', () => {
    render(<CNPJInput />);
    const input = screen.getByTestId('cnpj-field');
    fireEvent.change(input, { target: { value: '1122233300018112345' } });
    expect((input as HTMLInputElement).value.length).toBeLessThanOrEqual(18);
  });

  it('mostra placeholder', () => {
    render(<CNPJInput placeholder="Digite o CNPJ" />);
    const input = screen.getByTestId('cnpj-field');
    expect(input).toHaveAttribute('placeholder', 'Digite o CNPJ');
  });

  it('mostra erro quando fornecido', () => {
    render(<CNPJInput error="CNPJ inválido" />);
    expect(screen.getByText('CNPJ inválido')).toBeInTheDocument();
  });

  it('aplica classe de erro', () => {
    render(<CNPJInput error="Erro" />);
    const input = screen.getByTestId('cnpj-field');
    expect(input).toHaveClass('has-error');
  });

  it('formata número incompleto', () => {
    render(<CNPJInput value="11222333" />);
    const input = screen.getByTestId('cnpj-field') as HTMLInputElement;
    expect(input.value).toBe('11.222.333');
  });

  it('tem displayName correto', () => {
    expect(CNPJInput.displayName).toBe('CNPJInput');
  });

  it('limita tamanho máximo do input', () => {
    render(<CNPJInput />);
    const input = screen.getByTestId('cnpj-field');
    expect(input).toHaveAttribute('maxLength', '18');
  });
});

describe('CNPJ Validation', () => {
  it('valida CNPJ correto', () => {
    expect(isValidCNPJ('11222333000181')).toBe(true);
    expect(isValidCNPJ('11.222.333/0001-81')).toBe(true);
  });

  it('rejeita CNPJ com dígitos repetidos', () => {
    expect(isValidCNPJ('11111111111111')).toBe(false);
    expect(isValidCNPJ('00000000000000')).toBe(false);
  });

  it('rejeita CNPJ incompleto', () => {
    expect(isValidCNPJ('1122233300018')).toBe(false);
  });

  it('rejeita CNPJ inválido', () => {
    expect(isValidCNPJ('11222333000182')).toBe(false);
  });
});
