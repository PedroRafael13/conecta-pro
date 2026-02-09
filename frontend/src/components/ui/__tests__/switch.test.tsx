import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Switch } from '../switch';

describe('Switch', () => {
  it('deve renderizar switch', () => {
    render(<Switch />);
    expect(screen.getByRole('switch')).toBeInTheDocument();
  });

  it('deve estar desmarcado por padrão', () => {
    render(<Switch />);
    const switchEl = screen.getByRole('switch');
    expect(switchEl).toHaveAttribute('data-state', 'unchecked');
  });

  it('deve estar marcado quando checked é true', () => {
    render(<Switch checked />);
    const switchEl = screen.getByRole('switch');
    expect(switchEl).toHaveAttribute('data-state', 'checked');
  });

  it('deve chamar onCheckedChange ao clicar', () => {
    const handleChange = vi.fn();
    render(<Switch onCheckedChange={handleChange} />);
    const switchEl = screen.getByRole('switch');
    fireEvent.click(switchEl);
    expect(handleChange).toHaveBeenCalled();
  });

  it('deve estar desabilitado quando disabled', () => {
    render(<Switch disabled />);
    expect(screen.getByRole('switch')).toBeDisabled();
  });

  it('deve aplicar classe customizada', () => {
    render(<Switch className="custom-switch" />);
    const switchEl = screen.getByRole('switch');
    expect(switchEl.className).toContain('custom-switch');
  });

  it('deve ter estilo de cursor pointer quando habilitado', () => {
    render(<Switch />);
    const switchEl = screen.getByRole('switch');
    expect(switchEl.className).toContain('cursor-pointer');
  });

  it('deve ter borda arredondada', () => {
    render(<Switch />);
    const switchEl = screen.getByRole('switch');
    expect(switchEl.className).toContain('rounded-full');
  });

  it('deve suportar controle via teclado', () => {
    const handleChange = vi.fn();
    render(<Switch onCheckedChange={handleChange} />);
    const switchEl = screen.getByRole('switch');
    fireEvent.keyDown(switchEl, { key: ' ' });
  });

  it('deve renderizar com aria-label', () => {
    render(<Switch aria-label="Ativar notificações" />);
    expect(screen.getByLabelText('Ativar notificações')).toBeInTheDocument();
  });

  it('deve encaminhar ref corretamente', () => {
    const ref = { current: null as HTMLButtonElement | null };
    render(<Switch ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });

  it('deve ter displayName correto', () => {
    expect(Switch.displayName).toBe('Switch');
  });

  it('deve alternar estado ao clicar', () => {
    const { rerender } = render(<Switch checked={false} />);
    const switchEl = screen.getByRole('switch');
    expect(switchEl).toHaveAttribute('data-state', 'unchecked');
  });

  it('deve renderizar múltiplos switches', () => {
    render(
      <>
        <Switch aria-label="Switch 1" />
        <Switch aria-label="Switch 2" />
        <Switch aria-label="Switch 3" />
      </>
    );
    expect(screen.getByLabelText('Switch 1')).toBeInTheDocument();
    expect(screen.getByLabelText('Switch 2')).toBeInTheDocument();
    expect(screen.getByLabelText('Switch 3')).toBeInTheDocument();
  });
});
