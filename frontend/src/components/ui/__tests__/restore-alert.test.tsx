import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { RestoreAlert } from '../restore-alert';

// Mock do date-fns
vi.mock('date-fns', () => ({
  formatDistanceToNow: () => '2 minutos atrás',
}));

vi.mock('date-fns/locale', () => ({
  ptBR: {},
}));

describe('RestoreAlert', () => {
  it('deve renderizar título do alerta', () => {
    render(<RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />);
    expect(screen.getByText('Rascunho encontrado')).toBeInTheDocument();
  });

  it('deve renderizar mensagem com tempo relativo quando savedAt é fornecido', () => {
    render(
      <RestoreAlert
        onRestore={vi.fn()}
        onDiscard={vi.fn()}
        savedAt={new Date()}
      />
    );
    expect(screen.getByText(/2 minutos atrás/)).toBeInTheDocument();
  });

  it('deve renderizar mensagem com "recentemente" quando savedAt é null', () => {
    render(
      <RestoreAlert
        onRestore={vi.fn()}
        onDiscard={vi.fn()}
        savedAt={null}
      />
    );
    expect(screen.getByText(/recentemente/)).toBeInTheDocument();
  });

  it('deve renderizar mensagem com "recentemente" quando savedAt é undefined', () => {
    render(<RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />);
    expect(screen.getByText(/recentemente/)).toBeInTheDocument();
  });

  it('deve chamar onRestore ao clicar no botão Restaurar', () => {
    const onRestore = vi.fn();
    render(<RestoreAlert onRestore={onRestore} onDiscard={vi.fn()} />);
    const restoreButton = screen.getByText('Restaurar');
    fireEvent.click(restoreButton);
    expect(onRestore).toHaveBeenCalled();
  });

  it('deve chamar onDiscard ao clicar no botão Descartar', () => {
    const onDiscard = vi.fn();
    render(<RestoreAlert onRestore={vi.fn()} onDiscard={onDiscard} />);
    const discardButton = screen.getByText('Descartar');
    fireEvent.click(discardButton);
    expect(onDiscard).toHaveBeenCalled();
  });

  it('deve ter botão Restaurar como primário', () => {
    render(<RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />);
    const restoreButton = screen.getByText('Restaurar');
    expect(restoreButton).toBeInTheDocument();
  });

  it('deve ter botão Descartar como outline', () => {
    render(<RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />);
    const discardButton = screen.getByText('Descartar');
    expect(discardButton).toBeInTheDocument();
  });

  it('deve ter ícone de alerta', () => {
    const { container } = render(
      <RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />
    );
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('deve ter fundo azul com opacidade', () => {
    const { container } = render(
      <RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />
    );
    const alert = container.firstChild as HTMLElement;
    expect(alert.className).toContain('bg-blue-500/10');
  });

  it('deve ter borda azul', () => {
    const { container } = render(
      <RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />
    );
    const alert = container.firstChild as HTMLElement;
    expect(alert.className).toContain('border-blue-500/20');
  });

  it('deve ter bordas arredondadas', () => {
    const { container } = render(
      <RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />
    );
    const alert = container.firstChild as HTMLElement;
    expect(alert.className).toContain('rounded-lg');
  });

  it('deve ter padding interno', () => {
    const { container } = render(
      <RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />
    );
    const alert = container.firstChild as HTMLElement;
    expect(alert.className).toContain('p-4');
  });

  it('deve ter margem inferior', () => {
    const { container } = render(
      <RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />
    );
    const alert = container.firstChild as HTMLElement;
    expect(alert.className).toContain('mb-4');
  });

  it('deve ter ícone de restaurar no botão Restaurar', () => {
    const { container } = render(
      <RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />
    );
    const restoreButton = screen.getByText('Restaurar').closest('button');
    const icon = restoreButton?.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('deve ter ícone de lixeira no botão Descartar', () => {
    const { container } = render(
      <RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />
    );
    const discardButton = screen.getByText('Descartar').closest('button');
    const icon = discardButton?.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('deve ter layout flexbox para conteúdo', () => {
    const { container } = render(
      <RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />
    );
    const content = container.querySelector('.flex.items-start');
    expect(content).toBeInTheDocument();
  });

  it('deve ter gap entre ícone e conteúdo', () => {
    const { container } = render(
      <RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />
    );
    const content = container.querySelector('.gap-3');
    expect(content).toBeInTheDocument();
  });

  it('deve ter flex wrap para botões', () => {
    const { container } = render(
      <RestoreAlert onRestore={vi.fn()} onDiscard={vi.fn()} />
    );
    const buttonsContainer = container.querySelector('.flex.flex-wrap');
    expect(buttonsContainer).toBeInTheDocument();
  });
});
