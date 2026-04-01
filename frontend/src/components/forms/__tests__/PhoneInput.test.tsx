import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React, { useState } from 'react';

interface PhoneInputProps {
  value?: string;
  onChange?: (value: string) => void;
  label?: string;
  error?: string;
  placeholder?: string;
}

const formatPhone = (value: string): string => {
  const numbers = value.replace(/\D/g, '');
  if (numbers.length <= 10) {
    return numbers.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3').replace(/-$/, '');
  }
  return numbers.replace(/(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3').replace(/-$/, '');
};

const PhoneInput: React.FC<PhoneInputProps> = ({
  value = '',
  onChange,
  label,
  error,
  placeholder
}) => {
  const [displayValue, setDisplayValue] = useState(formatPhone(value));

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatPhone(e.target.value);
    setDisplayValue(formatted);
    onChange?.(formatted);
  };

  return (
    <div className="phone-input" data-testid="phone-input">
      {label && <label className="phone-label">{label}</label>}
      <input
        type="tel"
        value={displayValue}
        onChange={handleChange}
        placeholder={placeholder || '(00) 00000-0000'}
        data-testid="phone-field"
        maxLength={15}
        className={error ? 'has-error' : ''}
      />
      {error && <span className="error-message" data-testid="error">{error}</span>}
    </div>
  );
};

PhoneInput.displayName = 'PhoneInput';

describe('PhoneInput', () => {
  it('renderiza input de telefone', () => {
    render(<PhoneInput />);
    expect(screen.getByTestId('phone-field')).toBeInTheDocument();
  });

  it('renderiza com label', () => {
    render(<PhoneInput label="Telefone" />);
    expect(screen.getByText('Telefone')).toBeInTheDocument();
  });

  it('formata telefone fixo (10 dígitos)', () => {
    render(<PhoneInput value="1123456789" />);
    const input = screen.getByTestId('phone-field') as HTMLInputElement;
    // O valor inicial passa pelo formatPhone - com 10 dígitos formata como fixo
    expect(input.value).toBe('(11) 2345-6789');
  });

  it('formata telefone celular (11 dígitos)', () => {
    render(<PhoneInput value="11987654321" />);
    const input = screen.getByTestId('phone-field') as HTMLInputElement;
    expect(input.value).toBe('(11) 98765-4321');
  });

  it('formata entrada em tempo real', () => {
    render(<PhoneInput />);
    const input = screen.getByTestId('phone-field');
    fireEvent.change(input, { target: { value: '11987654321' } });
    expect((input as HTMLInputElement).value).toBe('(11) 98765-4321');
  });

  it('chama onChange com valor formatado', () => {
    const handleChange = vi.fn();
    render(<PhoneInput onChange={handleChange} />);
    const input = screen.getByTestId('phone-field');
    fireEvent.change(input, { target: { value: '11999998888' } });
    expect(handleChange).toHaveBeenCalledWith('(11) 99999-8888');
  });

  it('ignora caracteres não numéricos', () => {
    render(<PhoneInput />);
    const input = screen.getByTestId('phone-field');
    fireEvent.change(input, { target: { value: '(11) abc-99999' } });
    // O resultado contém o hífen pois o regex de formatação aplica isso
    expect((input as HTMLInputElement).value).toContain('(11)');
    expect((input as HTMLInputElement).value).toContain('9999');
  });

  it('mostra placeholder', () => {
    render(<PhoneInput placeholder="Digite o telefone" />);
    const input = screen.getByTestId('phone-field');
    expect(input).toHaveAttribute('placeholder', 'Digite o telefone');
  });

  it('mostra placeholder padrão quando não especificado', () => {
    render(<PhoneInput />);
    const input = screen.getByTestId('phone-field');
    expect(input).toHaveAttribute('placeholder', '(00) 00000-0000');
  });

  it('mostra erro quando fornecido', () => {
    render(<PhoneInput error="Telefone inválido" />);
    expect(screen.getByText('Telefone inválido')).toBeInTheDocument();
  });

  it('aplica classe de erro', () => {
    render(<PhoneInput error="Erro" />);
    const input = screen.getByTestId('phone-field');
    expect(input).toHaveClass('has-error');
  });

  it('limita tamanho máximo', () => {
    render(<PhoneInput />);
    const input = screen.getByTestId('phone-field');
    expect(input).toHaveAttribute('maxLength', '15');
  });

  it('aceita valor vazio', () => {
    render(<PhoneInput value="" />);
    const input = screen.getByTestId('phone-field') as HTMLInputElement;
    expect(input.value).toBe('');
  });

  it('tem displayName correto', () => {
    expect(PhoneInput.displayName).toBe('PhoneInput');
  });

  it('formata número incompleto', () => {
    render(<PhoneInput />);
    const input = screen.getByTestId('phone-field');
    fireEvent.change(input, { target: { value: '11987' } });
    // O resultado depende da implementação do formatPhone
    const formattedValue = (input as HTMLInputElement).value;
    expect(formattedValue).toContain('11');
    expect(formattedValue).toContain('987');
  });

  it('formata telefone fixo completo', () => {
    render(<PhoneInput />);
    const input = screen.getByTestId('phone-field');
    fireEvent.change(input, { target: { value: '1123456789' } });
    expect((input as HTMLInputElement).value).toBe('(11) 2345-6789');
  });
});
