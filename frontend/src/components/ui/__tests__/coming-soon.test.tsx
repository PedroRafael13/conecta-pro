import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ComingSoon } from '../coming-soon';

// Mock do next/navigation
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

describe('ComingSoon', () => {
  beforeEach(() => {
    mockPush.mockClear();
  });

  it('deve renderizar título', () => {
    render(<ComingSoon title="Módulo em Breve" />);
    expect(screen.getByText('Módulo em Breve')).toBeInTheDocument();
  });

  it('deve renderizar descrição padrão quando não fornecida', () => {
    render(<ComingSoon title="Teste" />);
    expect(
      screen.getByText('Este módulo está em desenvolvimento e estará disponível em breve.')
    ).toBeInTheDocument();
  });

  it('deve renderizar descrição customizada', () => {
    render(
      <ComingSoon
        title="Teste"
        description="Descrição personalizada do módulo."
      />
    );
    expect(screen.getByText('Descrição personalizada do módulo.')).toBeInTheDocument();
  });

  it('deve renderizar ícone de construção', () => {
    const { container } = render(<ComingSoon title="Teste" />);
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('deve ter container com fundo brand', () => {
    const { container } = render(<ComingSoon title="Teste" />);
    const iconContainer = container.querySelector('.bg-brand-500\\/10');
    expect(iconContainer).toBeInTheDocument();
  });

  it('deve navegar para dashboard ao clicar no botão primário', () => {
    render(<ComingSoon title="Teste" />);
    const dashboardButton = screen.getByText('Ir para Dashboard');
    fireEvent.click(dashboardButton);
    expect(mockPush).toHaveBeenCalledWith('/dashboard');
  });

  it('deve mostrar botão de voltar quando moduleHref é fornecido', () => {
    render(<ComingSoon title="Teste" moduleHref="/modulo/anterior" />);
    expect(screen.getByText('Voltar ao Módulo')).toBeInTheDocument();
  });

  it('deve navegar para módulo ao clicar no botão de voltar', () => {
    render(<ComingSoon title="Teste" moduleHref="/modulo/anterior" />);
    const backButton = screen.getByText('Voltar ao Módulo');
    fireEvent.click(backButton);
    expect(mockPush).toHaveBeenCalledWith('/modulo/anterior');
  });

  it('deve ter layout centralizado', () => {
    const { container } = render(<ComingSoon title="Teste" />);
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('flex');
    expect(wrapper.className).toContain('items-center');
    expect(wrapper.className).toContain('justify-center');
  });

  it('deve ter altura mínima definida', () => {
    const { container } = render(<ComingSoon title="Teste" />);
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('min-h-[60vh]');
  });

  it('deve renderizar título com tipografia correta', () => {
    render(<ComingSoon title="Título Teste" />);
    const title = screen.getByText('Título Teste');
    expect(title.tagName).toBe('H1');
    expect(title.className).toContain('text-2xl');
    expect(title.className).toContain('font-bold');
  });

  it('deve ter padding horizontal', () => {
    const { container } = render(<ComingSoon title="Teste" />);
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('px-4');
  });

  it('deve renderizar dois botões quando moduleHref é fornecido', () => {
    render(<ComingSoon title="Teste" moduleHref="/modulo" />);
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBe(2);
  });

  it('deve renderizar apenas um botão quando moduleHref não é fornecido', () => {
    render(<ComingSoon title="Teste" />);
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBe(1);
  });
});
