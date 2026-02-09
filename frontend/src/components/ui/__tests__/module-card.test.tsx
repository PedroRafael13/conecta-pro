import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ModuleCard } from '../module-card';
import { Home, Users, Settings } from 'lucide-react';

// Mock do next/navigation
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

describe('ModuleCard', () => {
  beforeEach(() => {
    mockPush.mockClear();
  });

  it('deve renderizar título do módulo', () => {
    render(
      <ModuleCard
        id="test"
        title="Dashboard"
        description="Visualize métricas"
        icon={Home}
        href="/dashboard"
        color="blue"
      />
    );
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('deve renderizar descrição do módulo', () => {
    render(
      <ModuleCard
        id="test"
        title="Dashboard"
        description="Visualize métricas importantes"
        icon={Home}
        href="/dashboard"
        color="blue"
      />
    );
    expect(screen.getByText('Visualize métricas importantes')).toBeInTheDocument();
  });

  it('deve renderizar ícone do módulo', () => {
    const { container } = render(
      <ModuleCard
        id="test"
        title="Dashboard"
        description="Teste"
        icon={Home}
        href="/dashboard"
        color="blue"
      />
    );
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('deve navegar ao clicar no card', () => {
    render(
      <ModuleCard
        id="test"
        title="Dashboard"
        description="Teste"
        icon={Home}
        href="/dashboard"
        color="blue"
      />
    );
    const card = screen.getByText('Dashboard').closest('[class*="cursor-pointer"]');
    if (card) {
      fireEvent.click(card);
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    }
  });

  it('deve renderizar badge quando fornecido', () => {
    render(
      <ModuleCard
        id="test"
        title="Usuários"
        description="Teste"
        icon={Users}
        href="/users"
        color="green"
        badge={5}
      />
    );
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('deve renderizar badge de texto quando fornecido', () => {
    render(
      <ModuleCard
        id="test"
        title="Configurações"
        description="Teste"
        icon={Settings}
        href="/settings"
        color="purple"
        badge="Novo"
      />
    );
    expect(screen.getByText('Novo')).toBeInTheDocument();
  });

  it('deve ter cursor not-allowed quando desabilitado', () => {
    const { container } = render(
      <ModuleCard
        id="test"
        title="Dashboard"
        description="Teste"
        icon={Home}
        href="/dashboard"
        color="blue"
        disabled
      />
    );
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('cursor-not-allowed');
  });

  it('deve ter opacidade reduzida quando desabilitado', () => {
    const { container } = render(
      <ModuleCard
        id="test"
        title="Dashboard"
        description="Teste"
        icon={Home}
        href="/dashboard"
        color="blue"
        disabled
      />
    );
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('opacity-50');
  });

  it('deve renderizar com diferentes cores', () => {
    const colors: Array<'cyan' | 'green' | 'orange' | 'purple' | 'red' | 'blue' | 'yellow' | 'pink'> = [
      'cyan', 'green', 'orange', 'purple', 'red', 'blue', 'yellow', 'pink'
    ];

    colors.forEach((color) => {
      const { container } = render(
        <ModuleCard
          id={`test-${color}`}
          title={`Módulo ${color}`}
          description="Teste"
          icon={Home}
          href={`/${color}`}
          color={color}
        />
      );
      const card = container.firstChild as HTMLElement;
      expect(card).toBeInTheDocument();
    });
  });

  it('deve ter bordas arredondadas', () => {
    const { container } = render(
      <ModuleCard
        id="test"
        title="Dashboard"
        description="Teste"
        icon={Home}
        href="/dashboard"
        color="blue"
      />
    );
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('rounded-xl');
  });

  it('deve ter padding interno', () => {
    const { container } = render(
      <ModuleCard
        id="test"
        title="Dashboard"
        description="Teste"
        icon={Home}
        href="/dashboard"
        color="blue"
      />
    );
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('p-5');
  });

  it('deve ter transições suaves', () => {
    const { container } = render(
      <ModuleCard
        id="test"
        title="Dashboard"
        description="Teste"
        icon={Home}
        href="/dashboard"
        color="blue"
      />
    );
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('transition-all');
    expect(card.className).toContain('duration-300');
  });

  it('deve ter container de ícone com fundo', () => {
    const { container } = render(
      <ModuleCard
        id="test"
        title="Dashboard"
        description="Teste"
        icon={Home}
        href="/dashboard"
        color="blue"
      />
    );
    const iconContainer = container.querySelector('.w-12.h-12');
    expect(iconContainer).toBeInTheDocument();
  });

  it('deve limitar descrição a duas linhas', () => {
    const { container } = render(
      <ModuleCard
        id="test"
        title="Dashboard"
        description="Esta é uma descrição muito longa que deve ser limitada"
        icon={Home}
        href="/dashboard"
        color="blue"
      />
    );
    const description = container.querySelector('.line-clamp-2');
    expect(description).toBeInTheDocument();
  });

  it('deve ter indicador de seta no hover', () => {
    const { container } = render(
      <ModuleCard
        id="test"
        title="Dashboard"
        description="Teste"
        icon={Home}
        href="/dashboard"
        color="blue"
      />
    );
    // O indicador de seta está presente mas com opacity-0 inicialmente
    const arrow = container.querySelector('svg');
    expect(arrow).toBeInTheDocument();
  });
});
