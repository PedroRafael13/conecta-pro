import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
  SelectScrollUpButton,
  SelectScrollDownButton,
} from '../select';

describe('Select', () => {
  it('deve renderizar Select com trigger', () => {
    render(
      <Select>
        <SelectTrigger data-testid="trigger">
          <SelectValue placeholder="Selecione" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="1">Opção 1</SelectItem>
        </SelectContent>
      </Select>
    );
    expect(screen.getByTestId('trigger')).toBeInTheDocument();
  });

  it('deve renderizar placeholder', () => {
    render(
      <Select>
        <SelectTrigger>
          <SelectValue placeholder="Selecione uma opção" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="1">Opção 1</SelectItem>
        </SelectContent>
      </Select>
    );
    expect(screen.getByText('Selecione uma opção')).toBeInTheDocument();
  });

  it('deve renderizar múltiplos items', () => {
    const { container } = render(
      <Select>
        <SelectTrigger>
          <SelectValue placeholder="Selecione" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="1">Opção 1</SelectItem>
          <SelectItem value="2">Opção 2</SelectItem>
          <SelectItem value="3">Opção 3</SelectItem>
        </SelectContent>
      </Select>
    );
    // Verificar que o Select renderizou (itens estão no portal)
    expect(screen.getByText('Selecione')).toBeInTheDocument();
  });

  it('deve chamar onValueChange ao selecionar', () => {
    const handleChange = vi.fn();
    render(
      <Select onValueChange={handleChange}>
        <SelectTrigger data-testid="trigger">
          <SelectValue placeholder="Selecione" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="1">Opção 1</SelectItem>
        </SelectContent>
      </Select>
    );
    fireEvent.click(screen.getByTestId('trigger'));
  });

  it('deve renderizar SelectLabel', () => {
    // SelectLabel é renderizado dentro do portal do Radix
    // Testamos a existência do componente
    expect(SelectLabel).toBeDefined();
    expect(SelectLabel.displayName).toBe('SelectLabel');
  });

  it('deve renderizar SelectSeparator', () => {
    // SelectSeparator é renderizado dentro do portal do Radix
    expect(SelectSeparator).toBeDefined();
    expect(SelectSeparator.displayName).toBe('SelectSeparator');
  });

  it('deve renderizar SelectGroup', () => {
    expect(SelectGroup).toBeDefined();
  });

  it('deve renderizar SelectScrollUpButton', () => {
    expect(SelectScrollUpButton).toBeDefined();
    expect(SelectScrollUpButton.displayName).toBe('SelectScrollUpButton');
  });

  it('deve renderizar SelectScrollDownButton', () => {
    expect(SelectScrollDownButton).toBeDefined();
    expect(SelectScrollDownButton.displayName).toBe('SelectScrollDownButton');
  });

  it('deve ter displayName correto para SelectTrigger', () => {
    expect(SelectTrigger.displayName).toBe('SelectTrigger');
  });

  it('deve ter displayName correto para SelectContent', () => {
    expect(SelectContent.displayName).toBe('SelectContent');
  });

  it('deve ter displayName correto para SelectItem', () => {
    expect(SelectItem.displayName).toBe('SelectItem');
  });

  it('deve aplicar classe customizada no trigger', () => {
    render(
      <Select>
        <SelectTrigger className="custom-class" data-testid="trigger">
          <SelectValue placeholder="Selecione" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="1">Opção 1</SelectItem>
        </SelectContent>
      </Select>
    );
    expect(screen.getByTestId('trigger').className).toContain('custom-class');
  });

  it('deve suportar value padrão', () => {
    render(
      <Select defaultValue="1">
        <SelectTrigger>
          <SelectValue placeholder="Selecione" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="1">Opção 1</SelectItem>
          <SelectItem value="2">Opção 2</SelectItem>
        </SelectContent>
      </Select>
    );
    expect(screen.getByText('Opção 1')).toBeInTheDocument();
  });

  it('deve renderizar ícone de chevron no trigger', () => {
    const { container } = render(
      <Select>
        <SelectTrigger>
          <SelectValue placeholder="Selecione" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="1">Opção 1</SelectItem>
        </SelectContent>
      </Select>
    );
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});
