import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React, { useState } from 'react';

interface CurrencyInputProps {
  value?: number;
  onChange?: (value: number) => void;
  label?: string;
  error?: string;
  placeholder?: string;
  disabled?: boolean;
}

const CurrencyInput: React.FC<CurrencyInputProps> = ({
  value,
  onChange,
  label,
  error,
  placeholder,
  disabled
}) => {
  const [displayValue, setDisplayValue] = useState(
    value ? `R$ ${value.toFixed(2).replace('.', ',')}` : ''
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/[^\d]/g, '');
    const numeric = parseInt(raw, 10) / 100;

    if (!isNaN(numeric)) {
      setDisplayValue(`R$ ${numeric.toFixed(2).replace('.', ',')}`);
      onChange?.(numeric);
    } else {
      setDisplayValue('');
      onChange?.(0);
    }
  };

  return (
    <div className="currency-input" data-testid="currency-input">
      {label && <label className="currency-label">{label}</label>}
      <input
        type="text"
        value={displayValue}
        onChange={handleChange}
        placeholder={placeholder || 'R$ 0,00'}
        disabled={disabled}
        data-testid="currency-field"
        className={error ? 'has-error' : ''}
      />
      {error && <span className="error-message" data-testid="error">{error}</span>}
    </div>
  );
};

CurrencyInput.displayName = 'CurrencyInput';

describe('CurrencyInput', () => {
  it('renderiza input de moeda', () => {
    render(<CurrencyInput />);
    expect(screen.getByTestId('currency-field')).toBeInTheDocument();
  });

  it('renderiza com label', () => {
    render(<CurrencyInput label="Valor" />);
    expect(screen.getByText('Valor')).toBeInTheDocument();
  });

  it('renderiza valor inicial formatado', () => {
    render(<CurrencyInput value={100.5} />);
    const input = screen.getByTestId('currency-field') as HTMLInputElement;
    expect(input.value).toBe('R$ 100,50');
  });

  it('formata entrada de valor', () => {
    render(<CurrencyInput />);
    const input = screen.getByTestId('currency-field');
    fireEvent.change(input, { target: { value: '10050' } });
    expect((input as HTMLInputElement).value).toBe('R$ 100,50');
  });

  it('chama onChange com valor numérico', () => {
    const handleChange = vi.fn();
    render(<CurrencyInput onChange={handleChange} />);
    const input = screen.getByTestId('currency-field');
    fireEvent.change(input, { target: { value: '5000' } });
    expect(handleChange).toHaveBeenCalledWith(50);
  });

  it('mostra placeholder', () => {
    render(<CurrencyInput placeholder="Digite o valor" />);
    const input = screen.getByTestId('currency-field');
    expect(input).toHaveAttribute('placeholder', 'Digite o valor');
  });

  it('mostra erro quando fornecido', () => {
    render(<CurrencyInput error="Valor inválido" />);
    expect(screen.getByText('Valor inválido')).toBeInTheDocument();
  });

  it('aplica classe de erro', () => {
    render(<CurrencyInput error="Erro" />);
    const input = screen.getByTestId('currency-field');
    expect(input).toHaveClass('has-error');
  });

  it('pode ser desabilitado', () => {
    render(<CurrencyInput disabled />);
    const input = screen.getByTestId('currency-field');
    expect(input).toBeDisabled();
  });

  it('ignora caracteres não numéricos', () => {
    const handleChange = vi.fn();
    render(<CurrencyInput onChange={handleChange} />);
    const input = screen.getByTestId('currency-field');
    fireEvent.change(input, { target: { value: 'abc100xyz' } });
    expect(handleChange).toHaveBeenCalledWith(1);
  });

  it('formata valores grandes corretamente', () => {
    render(<CurrencyInput value={1234567.89} />);
    const input = screen.getByTestId('currency-field') as HTMLInputElement;
    expect(input.value).toBe('R$ 1234567,89');
  });

  it('formata centavos corretamente', () => {
    const handleChange = vi.fn();
    render(<CurrencyInput onChange={handleChange} />);
    const input = screen.getByTestId('currency-field');
    fireEvent.change(input, { target: { value: '99' } });
    expect(handleChange).toHaveBeenCalledWith(0.99);
  });

  it('tem displayName correto', () => {
    expect(CurrencyInput.displayName).toBe('CurrencyInput');
  });
});
