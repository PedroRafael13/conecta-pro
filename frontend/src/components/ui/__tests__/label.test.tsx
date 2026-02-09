import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Label } from '../label';

describe('Label', () => {
  it('deve renderizar label com texto', () => {
    render(<Label>Nome</Label>);
    expect(screen.getByText('Nome')).toBeInTheDocument();
  });

  it('deve renderizar como elemento label', () => {
    render(<Label>Email</Label>);
    const label = screen.getByText('Email');
    expect(label.tagName.toLowerCase()).toBe('label');
  });

  it('deve ter tamanho de texto sm', () => {
    render(<Label>Tamanho</Label>);
    const label = screen.getByText('Tamanho');
    expect(label.className).toContain('text-sm');
  });

  it('deve ter fonte medium', () => {
    render(<Label>Fonte</Label>);
    const label = screen.getByText('Fonte');
    expect(label.className).toContain('font-medium');
  });

  it('deve aplicar classe customizada', () => {
    render(<Label className="custom-label">Custom</Label>);
    const label = screen.getByText('Custom');
    expect(label.className).toContain('custom-label');
  });

  it('deve aceitar atributo htmlFor', () => {
    render(<Label htmlFor="input-name">Nome</Label>);
    const label = screen.getByText('Nome');
    expect(label).toHaveAttribute('for', 'input-name');
  });

  it('deve associar com input via htmlFor', () => {
    render(
      <>
        <Label htmlFor="email">Email</Label>
        <input id="email" type="email" />
      </>
    );
    const label = screen.getByText('Email');
    expect(label).toHaveAttribute('for', 'email');
  });

  it('deve ter displayName correto', () => {
    expect(Label.displayName).toBe('Label');
  });

  it('deve encaminhar ref corretamente', () => {
    const ref = { current: null as HTMLLabelElement | null };
    render(<Label ref={ref}>Com Ref</Label>);
    expect(ref.current).toBeInstanceOf(HTMLLabelElement);
  });

  it('deve renderizar múltiplos labels', () => {
    render(
      <>
        <Label htmlFor="nome">Nome</Label>
        <Label htmlFor="email">Email</Label>
        <Label htmlFor="telefone">Telefone</Label>
      </>
    );
    expect(screen.getByText('Nome')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByText('Telefone')).toBeInTheDocument();
  });

  it('deve suportar children complexos', () => {
    render(
      <Label>
        <span data-testid="icon">*</span>
        Campo Obrigatório
      </Label>
    );
    expect(screen.getByTestId('icon')).toBeInTheDocument();
    expect(screen.getByText('Campo Obrigatório')).toBeInTheDocument();
  });

  it('deve aplicar estilo de leading-none', () => {
    render(<Label>Leading</Label>);
    const label = screen.getByText('Leading');
    expect(label.className).toContain('leading-none');
  });

  it('deve ter estilos para estado disabled do peer', () => {
    render(<Label>Peer Disabled</Label>);
    const label = screen.getByText('Peer Disabled');
    expect(label.className).toContain('peer-disabled:cursor-not-allowed');
    expect(label.className).toContain('peer-disabled:opacity-70');
  });
});
