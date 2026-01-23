'use client';

import { useMemo } from 'react';
import { useAuth } from './useAuth';

/**
 * Roles do modulo operacional
 */
export enum OperacionalRole {
  ADMINISTRADOR = 'administrador',
  GERENTE_OPERACIONAL = 'gerente_operacional',
  SUPERVISOR = 'supervisor',
  INSPETOR = 'inspetor',
  LIDER = 'lider',
  AGENTE = 'agente',
}

/**
 * Permissoes do modulo operacional
 */
export enum Permission {
  // Postos
  POSTS_CREATE = 'posts:create',
  POSTS_EDIT = 'posts:edit',
  POSTS_DELETE = 'posts:delete',
  POSTS_VIEW = 'posts:view',

  // Escalas
  SCALES_CREATE = 'scales:create',
  SCALES_APPROVE = 'scales:approve',
  SCALES_PUBLISH = 'scales:publish',
  SCALES_VIEW_ALL = 'scales:view_all',
  SCALES_VIEW_OWN = 'scales:view_own',

  // Alocacoes
  ALLOCATIONS_CREATE = 'allocations:create',
  ALLOCATIONS_EDIT = 'allocations:edit',
  ALLOCATIONS_VIEW = 'allocations:view',

  // Turnos
  SHIFTS_CREATE = 'shifts:create',
  SHIFTS_CHECKIN = 'shifts:checkin',
  SHIFTS_MARK_MISSED = 'shifts:mark_missed',
  SHIFTS_VIEW_ALL = 'shifts:view_all',
  SHIFTS_VIEW_OWN = 'shifts:view_own',

  // Substituicoes
  SUBSTITUTIONS_CREATE = 'substitutions:create',
  SUBSTITUTIONS_APPROVE = 'substitutions:approve',

  // Banco de Horas
  TIMEBANK_CREATE = 'timebank:create',
  TIMEBANK_APPROVE = 'timebank:approve',
  TIMEBANK_VIEW_ALL = 'timebank:view_all',
  TIMEBANK_VIEW_OWN = 'timebank:view_own',

  // Relatorios
  REPORTS_VIEW = 'reports:view',

  // Funcionarios
  EMPLOYEES_VIEW = 'employees:view',
}

/**
 * Hierarquia de poder dos roles (maior = mais poder)
 */
const ROLE_POWER: Record<string, number> = {
  [OperacionalRole.ADMINISTRADOR]: 100,
  [OperacionalRole.GERENTE_OPERACIONAL]: 80,
  [OperacionalRole.SUPERVISOR]: 60,
  [OperacionalRole.INSPETOR]: 40,
  [OperacionalRole.LIDER]: 20,
  [OperacionalRole.AGENTE]: 10,
};

/**
 * Mapeamento de roles para permissoes
 */
const ROLE_PERMISSIONS: Record<string, Permission[]> = {
  [OperacionalRole.ADMINISTRADOR]: Object.values(Permission),

  [OperacionalRole.GERENTE_OPERACIONAL]: [
    Permission.POSTS_CREATE,
    Permission.POSTS_EDIT,
    Permission.POSTS_DELETE,
    Permission.POSTS_VIEW,
    Permission.SCALES_CREATE,
    Permission.SCALES_APPROVE,
    Permission.SCALES_PUBLISH,
    Permission.SCALES_VIEW_ALL,
    Permission.SCALES_VIEW_OWN,
    Permission.ALLOCATIONS_CREATE,
    Permission.ALLOCATIONS_EDIT,
    Permission.ALLOCATIONS_VIEW,
    Permission.SHIFTS_CREATE,
    Permission.SHIFTS_CHECKIN,
    Permission.SHIFTS_MARK_MISSED,
    Permission.SHIFTS_VIEW_ALL,
    Permission.SHIFTS_VIEW_OWN,
    Permission.SUBSTITUTIONS_CREATE,
    Permission.SUBSTITUTIONS_APPROVE,
    Permission.TIMEBANK_CREATE,
    Permission.TIMEBANK_APPROVE,
    Permission.TIMEBANK_VIEW_ALL,
    Permission.TIMEBANK_VIEW_OWN,
    Permission.REPORTS_VIEW,
    Permission.EMPLOYEES_VIEW,
  ],

  [OperacionalRole.SUPERVISOR]: [
    Permission.POSTS_VIEW,
    Permission.SCALES_CREATE,
    Permission.SCALES_APPROVE,
    Permission.SCALES_PUBLISH,
    Permission.SCALES_VIEW_ALL,
    Permission.SCALES_VIEW_OWN,
    Permission.ALLOCATIONS_CREATE,
    Permission.ALLOCATIONS_EDIT,
    Permission.ALLOCATIONS_VIEW,
    Permission.SHIFTS_CREATE,
    Permission.SHIFTS_CHECKIN,
    Permission.SHIFTS_MARK_MISSED,
    Permission.SHIFTS_VIEW_ALL,
    Permission.SHIFTS_VIEW_OWN,
    Permission.SUBSTITUTIONS_CREATE,
    Permission.SUBSTITUTIONS_APPROVE,
    Permission.TIMEBANK_CREATE,
    Permission.TIMEBANK_APPROVE,
    Permission.TIMEBANK_VIEW_ALL,
    Permission.TIMEBANK_VIEW_OWN,
    Permission.REPORTS_VIEW,
    Permission.EMPLOYEES_VIEW,
  ],

  [OperacionalRole.INSPETOR]: [
    Permission.POSTS_VIEW,
    Permission.SCALES_VIEW_ALL,
    Permission.SCALES_VIEW_OWN,
    Permission.ALLOCATIONS_VIEW,
    Permission.SHIFTS_CHECKIN,
    Permission.SHIFTS_MARK_MISSED,
    Permission.SHIFTS_VIEW_ALL,
    Permission.SHIFTS_VIEW_OWN,
    Permission.SUBSTITUTIONS_CREATE,
    Permission.SUBSTITUTIONS_APPROVE,
    Permission.TIMEBANK_VIEW_ALL,
    Permission.TIMEBANK_VIEW_OWN,
    Permission.REPORTS_VIEW,
    Permission.EMPLOYEES_VIEW,
  ],

  [OperacionalRole.LIDER]: [
    Permission.POSTS_VIEW,
    Permission.SCALES_VIEW_ALL,
    Permission.SCALES_VIEW_OWN,
    Permission.ALLOCATIONS_VIEW,
    Permission.SHIFTS_CHECKIN,
    Permission.SHIFTS_VIEW_ALL,
    Permission.SHIFTS_VIEW_OWN,
    Permission.SUBSTITUTIONS_CREATE,
    Permission.TIMEBANK_VIEW_OWN,
    Permission.EMPLOYEES_VIEW,
  ],

  [OperacionalRole.AGENTE]: [
    Permission.SCALES_VIEW_OWN,
    Permission.SHIFTS_CHECKIN,
    Permission.SHIFTS_VIEW_OWN,
    Permission.TIMEBANK_VIEW_OWN,
  ],
};

// Roles que tem acesso total
const ADMIN_ROLES = ['admin', 'super_admin', 'administrador'];

/**
 * Hook para verificar permissoes do usuario
 */
export function usePermission() {
  const { user, isAuthenticated, isLoading } = useAuth();

  const userRole = user?.role || '';

  /**
   * Verifica se o usuario tem uma permissao especifica
   */
  const hasPermission = useMemo(() => {
    return (permission: Permission | Permission[]): boolean => {
      if (!isAuthenticated || !user) return false;

      // Admin tem acesso total
      if (ADMIN_ROLES.includes(userRole)) return true;

      // Buscar permissoes do role
      const rolePermissions = ROLE_PERMISSIONS[userRole] || [];

      // Se passou array, verifica se tem alguma
      if (Array.isArray(permission)) {
        return permission.some(p => rolePermissions.includes(p));
      }

      return rolePermissions.includes(permission);
    };
  }, [isAuthenticated, user, userRole]);

  /**
   * Verifica se o usuario tem um role especifico
   */
  const hasRole = useMemo(() => {
    return (roles: string | string[]): boolean => {
      if (!isAuthenticated || !user) return false;

      const roleList = Array.isArray(roles) ? roles : [roles];
      return roleList.includes(userRole);
    };
  }, [isAuthenticated, user, userRole]);

  /**
   * Verifica se o usuario tem no minimo um role na hierarquia
   */
  const hasMinimumRole = useMemo(() => {
    return (minimumRole: OperacionalRole): boolean => {
      if (!isAuthenticated || !user) return false;

      // Admin tem acesso total
      if (ADMIN_ROLES.includes(userRole)) return true;

      const userPower = ROLE_POWER[userRole] || 0;
      const requiredPower = ROLE_POWER[minimumRole] || 0;

      return userPower >= requiredPower;
    };
  }, [isAuthenticated, user, userRole]);

  /**
   * Verifica se e admin (acesso total)
   */
  const isAdmin = useMemo(() => {
    return ADMIN_ROLES.includes(userRole);
  }, [userRole]);

  /**
   * Verifica se pode gerenciar postos
   */
  const canManagePosts = useMemo(() => {
    return hasPermission(Permission.POSTS_CREATE);
  }, [hasPermission]);

  /**
   * Verifica se pode gerenciar escalas
   */
  const canManageScales = useMemo(() => {
    return hasPermission(Permission.SCALES_CREATE);
  }, [hasPermission]);

  /**
   * Verifica se pode aprovar escalas
   */
  const canApproveScales = useMemo(() => {
    return hasPermission(Permission.SCALES_APPROVE);
  }, [hasPermission]);

  /**
   * Verifica se pode gerenciar alocacoes
   */
  const canManageAllocations = useMemo(() => {
    return hasPermission(Permission.ALLOCATIONS_CREATE);
  }, [hasPermission]);

  /**
   * Verifica se pode fazer check-in/out
   */
  const canCheckIn = useMemo(() => {
    return hasPermission(Permission.SHIFTS_CHECKIN);
  }, [hasPermission]);

  /**
   * Verifica se pode marcar faltas
   */
  const canMarkMissed = useMemo(() => {
    return hasPermission(Permission.SHIFTS_MARK_MISSED);
  }, [hasPermission]);

  /**
   * Verifica se pode gerenciar substituicoes
   */
  const canManageSubstitutions = useMemo(() => {
    return hasPermission(Permission.SUBSTITUTIONS_CREATE);
  }, [hasPermission]);

  /**
   * Verifica se pode aprovar substituicoes
   */
  const canApproveSubstitutions = useMemo(() => {
    return hasPermission(Permission.SUBSTITUTIONS_APPROVE);
  }, [hasPermission]);

  /**
   * Verifica se pode gerenciar banco de horas
   */
  const canManageTimeBank = useMemo(() => {
    return hasPermission(Permission.TIMEBANK_CREATE);
  }, [hasPermission]);

  /**
   * Verifica se pode aprovar banco de horas
   */
  const canApproveTimeBank = useMemo(() => {
    return hasPermission(Permission.TIMEBANK_APPROVE);
  }, [hasPermission]);

  /**
   * Verifica se pode ver relatorios
   */
  const canViewReports = useMemo(() => {
    return hasPermission(Permission.REPORTS_VIEW);
  }, [hasPermission]);

  /**
   * Verifica se pode ver funcionarios
   */
  const canViewEmployees = useMemo(() => {
    return hasPermission(Permission.EMPLOYEES_VIEW);
  }, [hasPermission]);

  return {
    // Estado
    isLoading,
    isAuthenticated,
    role: userRole,
    user,

    // Verificadores gerais
    hasPermission,
    hasRole,
    hasMinimumRole,
    isAdmin,

    // Verificadores especificos
    canManagePosts,
    canManageScales,
    canApproveScales,
    canManageAllocations,
    canCheckIn,
    canMarkMissed,
    canManageSubstitutions,
    canApproveSubstitutions,
    canManageTimeBank,
    canApproveTimeBank,
    canViewReports,
    canViewEmployees,
  };
}
