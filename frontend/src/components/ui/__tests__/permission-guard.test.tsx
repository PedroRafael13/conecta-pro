import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PermissionGuard, PageGuard } from '../permission-guard';
import { Permission, OperacionalRole } from '@/hooks/usePermission';

// Estado do mock que pode ser alterado entre testes
const mockState = {
  hasPermission: vi.fn(),
  hasRole: vi.fn(),
  hasMinimumRole: vi.fn(),
  isLoading: false,
  isAuthenticated: true,
};

// Mock do usePermission
vi.mock('@/hooks/usePermission', () => ({
  Permission: {
    POSTS_CREATE: 'posts:create',
    POSTS_EDIT: 'posts:edit',
    POSTS_DELETE: 'posts:delete',
    POSTS_VIEW: 'posts:view',
  },
  OperacionalRole: {
    ADMINISTRADOR: 'administrador',
    GERENTE_OPERACIONAL: 'gerente_operacional',
    SUPERVISOR: 'supervisor',
    INSPETOR: 'inspetor',
    LIDER: 'lider',
    AGENTE: 'agente',
  },
  usePermission: () => mockState,
}));

describe('PermissionGuard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Resetar estado padrão
    mockState.hasPermission.mockReturnValue(true);
    mockState.hasRole.mockReturnValue(true);
    mockState.hasMinimumRole.mockReturnValue(true);
    mockState.isLoading = false;
    mockState.isAuthenticated = true;
  });

  it('deve renderizar children quando tem permissão', () => {
    mockState.hasPermission.mockReturnValue(true);
    render(
      <PermissionGuard permission={Permission.POSTS_CREATE}>
        <div data-testid="protected-content">Conteúdo Protegido</div>
      </PermissionGuard>
    );
    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
  });

  it('deve renderizar fallback quando não tem permissão', () => {
    mockState.hasPermission.mockReturnValue(false);
    render(
      <PermissionGuard
        permission={Permission.POSTS_CREATE}
        fallback={<div data-testid="fallback">Acesso Negado</div>}
      >
        <div data-testid="protected-content">Conteúdo Protegido</div>
      </PermissionGuard>
    );
    expect(screen.getByTestId('fallback')).toBeInTheDocument();
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  it('deve renderizar null quando não tem permissão e não há fallback', () => {
    mockState.hasPermission.mockReturnValue(false);
    const { container } = render(
      <PermissionGuard permission={Permission.POSTS_CREATE}>
        <div>Conteúdo Protegido</div>
      </PermissionGuard>
    );
    expect(container.firstChild).toBeNull();
  });

  it('deve verificar múltiplas permissões com OR lógico', () => {
    mockState.hasPermission.mockReturnValue(true);
    render(
      <PermissionGuard permission={[Permission.POSTS_CREATE, Permission.POSTS_EDIT]}>
        <div data-testid="protected-content">Conteúdo</div>
      </PermissionGuard>
    );
    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
  });

  it('deve verificar role quando permission não é fornecida', () => {
    mockState.hasRole.mockReturnValue(true);
    render(
      <PermissionGuard role="admin">
        <div data-testid="protected-content">Conteúdo</div>
      </PermissionGuard>
    );
    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
  });

  it('deve verificar múltiplos roles com OR lógico', () => {
    mockState.hasRole.mockReturnValue(true);
    render(
      <PermissionGuard role={['admin', 'supervisor']}>
        <div data-testid="protected-content">Conteúdo</div>
      </PermissionGuard>
    );
    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
  });

  it('deve verificar role mínimo na hierarquia', () => {
    mockState.hasMinimumRole.mockReturnValue(true);
    render(
      <PermissionGuard minimumRole={OperacionalRole.SUPERVISOR}>
        <div data-testid="protected-content">Conteúdo</div>
      </PermissionGuard>
    );
    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
  });

  it('deve mostrar loading quando showLoading é true e está carregando', () => {
    mockState.isLoading = true;
    const { container } = render(
      <PermissionGuard permission={Permission.POSTS_CREATE} showLoading>
        <div>Conteúdo</div>
      </PermissionGuard>
    );
    const loadingElement = container.querySelector('.animate-pulse');
    expect(loadingElement).toBeInTheDocument();
  });

  it('deve passar array de permissões para hasPermission', () => {
    mockState.hasPermission.mockReturnValue(true);
    render(
      <PermissionGuard permission={[Permission.POSTS_CREATE, Permission.POSTS_EDIT]}>
        <div>Conteúdo</div>
      </PermissionGuard>
    );
    expect(mockState.hasPermission).toHaveBeenCalledWith([
      Permission.POSTS_CREATE,
      Permission.POSTS_EDIT,
    ]);
  });

  it('deve passar permissão única para hasPermission', () => {
    mockState.hasPermission.mockReturnValue(true);
    render(
      <PermissionGuard permission={Permission.POSTS_CREATE}>
        <div>Conteúdo</div>
      </PermissionGuard>
    );
    expect(mockState.hasPermission).toHaveBeenCalledWith(Permission.POSTS_CREATE);
  });
});

describe('PageGuard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockState.hasPermission.mockReturnValue(true);
    mockState.hasRole.mockReturnValue(true);
    mockState.hasMinimumRole.mockReturnValue(true);
    mockState.isLoading = false;
    mockState.isAuthenticated = true;
  });

  it('deve renderizar children quando tem acesso', () => {
    mockState.hasPermission.mockReturnValue(true);
    render(
      <PageGuard permission={Permission.POSTS_CREATE}>
        <div data-testid="page-content">Página Protegida</div>
      </PageGuard>
    );
    expect(screen.getByTestId('page-content')).toBeInTheDocument();
  });

  it('deve mostrar loading quando está carregando', () => {
    mockState.isLoading = true;
    const { container } = render(
      <PageGuard permission={Permission.POSTS_CREATE}>
        <div>Página</div>
      </PageGuard>
    );
    const loadingElement = container.querySelector('.animate-pulse-slow');
    expect(loadingElement).toBeInTheDocument();
  });

  it('deve retornar null quando não está autenticado', () => {
    mockState.isAuthenticated = false;
    const { container } = render(
      <PageGuard permission={Permission.POSTS_CREATE}>
        <div>Página</div>
      </PageGuard>
    );
    expect(container.firstChild).toBeNull();
  });

  it('deve mostrar mensagem de acesso negado quando não tem permissão', () => {
    mockState.hasPermission.mockReturnValue(false);
    render(
      <PageGuard permission={Permission.POSTS_CREATE}>
        <div>Página</div>
      </PageGuard>
    );
    expect(screen.getByText('Acesso Negado')).toBeInTheDocument();
  });

  it('deve mostrar mensagem customizada de acesso negado', () => {
    mockState.hasPermission.mockReturnValue(false);
    render(
      <PageGuard
        permission={Permission.POSTS_CREATE}
        deniedMessage="Você precisa de permissão de administrador."
      >
        <div>Página</div>
      </PageGuard>
    );
    expect(
      screen.getByText('Você precisa de permissão de administrador.')
    ).toBeInTheDocument();
  });

  it('deve ter link para dashboard na tela de acesso negado', () => {
    mockState.hasPermission.mockReturnValue(false);
    render(
      <PageGuard permission={Permission.POSTS_CREATE}>
        <div>Página</div>
      </PageGuard>
    );
    const dashboardLink = screen.getByText('Voltar ao Dashboard');
    expect(dashboardLink).toBeInTheDocument();
    expect(dashboardLink.tagName).toBe('A');
    expect(dashboardLink.getAttribute('href')).toBe('/dashboard');
  });

  it('deve ter ícone de alerta na tela de acesso negado', () => {
    mockState.hasPermission.mockReturnValue(false);
    const { container } = render(
      <PageGuard permission={Permission.POSTS_CREATE}>
        <div>Página</div>
      </PageGuard>
    );
    const iconContainer = container.querySelector('.rounded-full');
    expect(iconContainer).toBeInTheDocument();
  });

  it('deve verificar role quando permission não é fornecida', () => {
    mockState.hasRole.mockReturnValue(false);
    render(
      <PageGuard role="admin">
        <div>Página</div>
      </PageGuard>
    );
    expect(mockState.hasRole).toHaveBeenCalledWith('admin');
  });

  it('deve verificar role mínimo quando fornecido', () => {
    mockState.hasMinimumRole.mockReturnValue(false);
    render(
      <PageGuard minimumRole={OperacionalRole.GERENTE_OPERACIONAL}>
        <div>Página</div>
      </PageGuard>
    );
    expect(mockState.hasMinimumRole).toHaveBeenCalledWith(
      OperacionalRole.GERENTE_OPERACIONAL
    );
  });
});
