import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { usePermission, Permission, OperacionalRole } from '../usePermission';

// Mock do useAuth
vi.mock('../useAuth', () => ({
  useAuth: vi.fn(),
}));


import { useAuth } from '../useAuth';

type User = { id: string; email: string; name: string; is_active: boolean; role: string; permissions: string[] };

const createTestUser = (overrides: Partial<User> = {}): User => ({
  id: 'test-user',
  email: 'test@test.com',
  name: 'Test User',
  is_active: true,
  role: 'admin',
  permissions: [],
  ...overrides,
});

describe('usePermission', () => {
  const mockUseAuth = vi.mocked(useAuth);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Verificação de Permissões', () => {
    it('deve negar permissão quando usuário não está autenticado', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasPermission(Permission.POSTS_CREATE)).toBe(false);
      expect(result.current.hasPermission(Permission.SCALES_VIEW_ALL)).toBe(false);
    });

    it('deve conceder todas as permissões para admin', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: 'admin' }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasPermission(Permission.POSTS_CREATE)).toBe(true);
      expect(result.current.hasPermission(Permission.SCALES_CREATE)).toBe(true);
      expect(result.current.isAdmin).toBe(true);
    });

    it('deve verificar permissões específicas do role', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.SUPERVISOR }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      // Supervisor tem permissão de visualizar postos
      expect(result.current.hasPermission(Permission.POSTS_VIEW)).toBe(true);
      // Supervisor não tem permissão de deletar postos
      expect(result.current.hasPermission(Permission.POSTS_DELETE)).toBe(false);
    });

    it('deve verificar array de permissões (alguma)', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.LIDER }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      // Lider tem SCALES_VIEW_ALL mas não POSTS_CREATE
      expect(result.current.hasPermission([Permission.SCALES_VIEW_ALL, Permission.POSTS_CREATE])).toBe(true);
    });

    it('deve negar quando não tem nenhuma das permissões do array', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.AGENTE }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasPermission([Permission.POSTS_CREATE, Permission.SCALES_APPROVE])).toBe(false);
    });
  });

  describe('Verificação de Roles', () => {
    it('deve verificar role específico', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.SUPERVISOR }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasRole(OperacionalRole.SUPERVISOR)).toBe(true);
      expect(result.current.hasRole(OperacionalRole.ADMINISTRADOR)).toBe(false);
    });

    it('deve verificar múltiplos roles', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.GERENTE_OPERACIONAL }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasRole([OperacionalRole.GERENTE_OPERACIONAL, OperacionalRole.ADMINISTRADOR])).toBe(true);
    });
  });

  describe('Hierarquia de Roles', () => {
    it('deve verificar role mínimo na hierarquia', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.SUPERVISOR }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      // Supervisor (60) >= Agente (10)
      expect(result.current.hasMinimumRole(OperacionalRole.AGENTE)).toBe(true);
      // Supervisor (60) >= Lider (20)
      expect(result.current.hasMinimumRole(OperacionalRole.LIDER)).toBe(true);
      // Supervisor (60) >= Gerente (80) = false
      expect(result.current.hasMinimumRole(OperacionalRole.GERENTE_OPERACIONAL)).toBe(false);
    });

    it('admin deve passar em qualquer verificação de mínimo', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: 'admin' }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasMinimumRole(OperacionalRole.ADMINISTRADOR)).toBe(true);
    });
  });

  describe('Verificadores Específicos', () => {
    it('deve verificar permissão de gerenciar postos', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.ADMINISTRADOR }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canManagePosts).toBe(true);
    });

    it('deve verificar permissão de gerenciar escalas', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.SUPERVISOR }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canManageScales).toBe(true);
    });

    it('deve verificar permissão de aprovar escalas', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.LIDER }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canApproveScales).toBe(false);
    });

    it('deve verificar permissão de check-in', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.AGENTE }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canCheckIn).toBe(true);
    });

    it('deve verificar permissão de ver relatórios', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.INSPETOR }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canViewReports).toBe(true);
    });

    it('deve verificar permissão de marcar faltas', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.GERENTE_OPERACIONAL }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canMarkMissed).toBe(true);
    });
  });

  describe('Estado de Loading', () => {
    it('deve expor estado de loading do auth', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: true,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.isLoading).toBe(true);
    });
  });

  describe('Mapeamento de Roles', () => {
    it('Administrador deve ter todas as permissões', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.ADMINISTRADOR }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());
      const allPermissions = Object.values(Permission);

      allPermissions.forEach(permission => {
        expect(result.current.hasPermission(permission)).toBe(true);
      });
    });

    it('Agente deve ter apenas permissões básicas', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.AGENTE }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasPermission(Permission.SCALES_VIEW_OWN)).toBe(true);
      expect(result.current.hasPermission(Permission.SHIFTS_CHECKIN)).toBe(true);
      expect(result.current.hasPermission(Permission.POSTS_VIEW)).toBe(false);
    });
  });

  describe('Edge Cases - Branch Coverage', () => {
    it('deve retornar false quando hasMinimumRole e role do usuário é menor que requerido', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.AGENTE }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      // Agente (10) < Supervisor (60)
      expect(result.current.hasMinimumRole(OperacionalRole.SUPERVISOR)).toBe(false);
    });

    it('deve verificar hasRole com array de roles', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.LIDER }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasRole([OperacionalRole.LIDER, OperacionalRole.SUPERVISOR])).toBe(true);
      expect(result.current.hasRole([OperacionalRole.AGENTE, OperacionalRole.SUPERVISOR])).toBe(false);
    });

    it('deve retornar true para isAdmin quando é super_admin', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: 'super_admin' }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.isAdmin).toBe(true);
    });

    it('deve retornar false para isAdmin quando é agente', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.AGENTE }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.isAdmin).toBe(false);
    });

    it('deve retornar false para hasRole quando não está autenticado', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasRole('admin')).toBe(false);
      expect(result.current.hasRole([OperacionalRole.SUPERVISOR, OperacionalRole.AGENTE])).toBe(false);
    });

    it('deve retornar false para hasMinimumRole quando não está autenticado', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasMinimumRole(OperacionalRole.AGENTE)).toBe(false);
    });

    it('deve usar fallback 0 para ROLE_POWER de role desconhecido em hasMinimumRole', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: 'role_desconhecido' }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      // role_desconhecido tem power 0, AGENTE tem power 10 => false
      expect(result.current.hasMinimumRole(OperacionalRole.AGENTE)).toBe(false);
    });

    it('deve retornar false para permissões quando usuário não tem role definido', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: '' }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasPermission(Permission.POSTS_VIEW)).toBe(false);
      expect(result.current.hasMinimumRole(OperacionalRole.AGENTE)).toBe(false);
    });

    it('deve retornar true para hasPermission com array quando admin', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: 'admin' }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasPermission([Permission.POSTS_CREATE, Permission.SCALES_APPROVE])).toBe(true);
    });

    it('deve retornar false para hasPermission com array quando não autenticado', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.hasPermission([Permission.POSTS_VIEW, Permission.SCALES_VIEW_OWN])).toBe(false);
    });

    it('deve retornar true para isAdmin quando é administrador (OperacionalRole)', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.ADMINISTRADOR }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.isAdmin).toBe(true);
    });
  });

  describe('Verificadores Específicos - Casos Negativos', () => {
    it('canManageAllocations deve ser false para Agente', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.AGENTE }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canManageAllocations).toBe(false);
    });

    it('canManageSubstitutions deve ser true para Inspetor', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.INSPETOR }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canManageSubstitutions).toBe(true);
    });

    it('canApproveSubstitutions deve ser false para Lider', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.LIDER }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canApproveSubstitutions).toBe(false);
    });

    it('canManageTimeBank deve ser false para Agente', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.AGENTE }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canManageTimeBank).toBe(false);
    });

    it('canApproveTimeBank deve ser true para Supervisor', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.SUPERVISOR }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canApproveTimeBank).toBe(true);
    });

    it('canViewEmployees deve ser false para Agente', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.AGENTE }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canViewEmployees).toBe(false);
    });

    it('canViewEmployees deve ser true para Lider', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.LIDER }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canViewEmployees).toBe(true);
    });

    it('canMarkMissed deve ser false para Lider', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.LIDER }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.canMarkMissed).toBe(false);
    });

    it('role deve refletir o role do usuário', () => {
      mockUseAuth.mockReturnValue({
        user: createTestUser({ id: '1', role: OperacionalRole.SUPERVISOR }),
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.role).toBe(OperacionalRole.SUPERVISOR);
    });

    it('role deve ser string vazia quando usuário não está autenticado', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.role).toBe('');
    });

    it('user deve estar disponível no retorno do hook', () => {
      const testUser = createTestUser({ id: '1', role: OperacionalRole.GERENTE_OPERACIONAL });
      mockUseAuth.mockReturnValue({
        user: testUser,
        isAuthenticated: true,
        isLoading: false,
        login: vi.fn(),
        logout: vi.fn(),
      });

      const { result } = renderHook(() => usePermission());

      expect(result.current.user).toEqual(testUser);
    });
  });
});
