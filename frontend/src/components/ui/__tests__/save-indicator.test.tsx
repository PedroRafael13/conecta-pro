import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SaveIndicator } from '../save-indicator';

describe('SaveIndicator', () => {
  it('deve renderizar null quando não há estado', () => {
    const { container } = render(
      <SaveIndicator saving={false} lastSaved={null} error={null} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('deve mostrar indicador de salvamento quando saving é true', () => {
    render(<SaveIndicator saving={true} lastSaved={null} error={null} />);
    expect(screen.getByText('Salvando rascunho...')).toBeInTheDocument();
  });

  it('deve mostrar spinner animado quando saving', () => {
    const { container } = render(
      <SaveIndicator saving={true} lastSaved={null} error={null} />
    );
    const spinner = container.querySelector('svg');
    expect(spinner).toBeInTheDocument();
    expect(spinner?.classList.contains('animate-spin')).toBe(true);
  });

  it('deve mostrar tempo desde o último salvamento', () => {
    const lastSaved = new Date(Date.now() - 5 * 60 * 1000); // 5 minutos atrás
    render(<SaveIndicator saving={false} lastSaved={lastSaved} error={null} />);
    expect(screen.getByText(/Rascunho salvo/)).toBeInTheDocument();
  });

  it('deve mostrar ícone de check quando salvo', () => {
    const lastSaved = new Date();
    const { container } = render(
      <SaveIndicator saving={false} lastSaved={lastSaved} error={null} />
    );
    const checkIcon = container.querySelector('svg');
    expect(checkIcon).toBeInTheDocument();
  });

  it('deve mostrar mensagem de erro quando error é fornecido', () => {
    render(
      <SaveIndicator saving={false} lastSaved={null} error="Erro ao salvar" />
    );
    expect(screen.getByText('Erro ao salvar')).toBeInTheDocument();
  });

  it('deve mostrar ícone de alerta quando há erro', () => {
    const { container } = render(
      <SaveIndicator saving={false} lastSaved={null} error="Erro" />
    );
    const alertIcon = container.querySelector('svg');
    expect(alertIcon).toBeInTheDocument();
  });

  it('deve mostrar botão de retry quando onRetry é fornecido e há erro', () => {
    const handleRetry = vi.fn();
    render(
      <SaveIndicator
        saving={false}
        lastSaved={null}
        error="Erro ao salvar"
        onRetry={handleRetry}
      />
    );
    expect(screen.getByText('Tentar novamente')).toBeInTheDocument();
  });

  it('deve chamar onRetry quando clicar no botão', () => {
    const handleRetry = vi.fn();
    render(
      <SaveIndicator
        saving={false}
        lastSaved={null}
        error="Erro ao salvar"
        onRetry={handleRetry}
      />
    );
    fireEvent.click(screen.getByText('Tentar novamente'));
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });

  it('deve priorizar erro sobre salvamento', () => {
    render(
      <SaveIndicator saving={true} lastSaved={null} error="Erro ao salvar" />
    );
    expect(screen.getByText('Erro ao salvar')).toBeInTheDocument();
    expect(screen.queryByText('Salvando rascunho...')).not.toBeInTheDocument();
  });

  it('deve priorizar salvamento sobre lastSaved', () => {
    const lastSaved = new Date();
    render(<SaveIndicator saving={true} lastSaved={lastSaved} error={null} />);
    expect(screen.getByText('Salvando rascunho...')).toBeInTheDocument();
    expect(screen.queryByText(/Rascunho salvo/)).not.toBeInTheDocument();
  });

  it('deve ter layout flexível', () => {
    render(<SaveIndicator saving={true} lastSaved={null} error={null} />);
    const { container } = render(
      <SaveIndicator saving={true} lastSaved={null} error={null} />
    );
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper?.className).toContain('flex');
    expect(wrapper?.className).toContain('items-center');
    expect(wrapper?.className).toContain('gap-2');
  });

  it('deve mostrar tempo formatado em português', () => {
    const lastSaved = new Date(Date.now() - 60 * 1000); // 1 minuto atrás
    render(<SaveIndicator saving={false} lastSaved={lastSaved} error={null} />);
    const text = screen.getByText(/Rascunho salvo/);
    expect(text.textContent).toMatch(/há \d+ minuto/);
  });

  it('não deve mostrar botão retry quando onRetry não é fornecido', () => {
    render(
      <SaveIndicator saving={false} lastSaved={null} error="Erro ao salvar" />
    );
    expect(screen.queryByText('Tentar novamente')).not.toBeInTheDocument();
  });

  it('deve ter classe text-xs na div container', () => {
    const { rerender, container } = render(
      <SaveIndicator saving={true} lastSaved={null} error={null} />
    );
    let wrapper = container.firstChild as HTMLElement;
    expect(wrapper?.className).toContain('text-xs');

    rerender(
      <SaveIndicator
        saving={false}
        lastSaved={new Date()}
        error={null}
      />
    );
    wrapper = container.firstChild as HTMLElement;
    expect(wrapper?.className).toContain('text-xs');

    rerender(
      <SaveIndicator saving={false} lastSaved={null} error="Erro" />
    );
    wrapper = container.firstChild as HTMLElement;
    expect(wrapper?.className).toContain('text-xs');
  });
});
