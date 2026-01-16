import { useMemo } from 'react';
import { useAuthStore } from '@stores/authStore';
import { PERMISSIONS } from '@utils/constants';

export function usePermissions() {
  const { user } = useAuthStore();

  const permissions = useMemo(() => {
    if (!user) return [];
    return user.permissions;
  }, [user]);

  const isAdmin = useMemo(() => {
    return user?.role === 'admin' || permissions.includes(PERMISSIONS.ADMIN);
  }, [user, permissions]);

  const hasPermission = (permission: string): boolean => {
    if (isAdmin) return true;
    return permissions.includes(permission);
  };

  const hasAnyPermission = (perms: string[]): boolean => {
    if (isAdmin) return true;
    return perms.some((p) => permissions.includes(p));
  };

  const hasAllPermissions = (perms: string[]): boolean => {
    if (isAdmin) return true;
    return perms.every((p) => permissions.includes(p));
  };

  // Module-specific permission checks
  const can = {
    // Audit
    viewAudit: () => hasPermission(PERMISSIONS.AUDIT_VIEW),
    manageAudit: () =>
      hasAnyPermission([
        PERMISSIONS.AUDIT_CREATE,
        PERMISSIONS.AUDIT_EDIT,
        PERMISSIONS.AUDIT_DELETE,
      ]),

    // LGPD
    viewLGPD: () => hasPermission(PERMISSIONS.LGPD_VIEW),
    manageLGPD: () => hasPermission(PERMISSIONS.LGPD_MANAGE),

    // GED
    viewGED: () => hasPermission(PERMISSIONS.GED_VIEW),
    uploadGED: () => hasPermission(PERMISSIONS.GED_UPLOAD),
    deleteGED: () => hasPermission(PERMISSIONS.GED_DELETE),

    // CRM
    viewCRM: () => hasPermission(PERMISSIONS.CRM_VIEW),
    editCRM: () => hasPermission(PERMISSIONS.CRM_EDIT),
    deleteCRM: () => hasPermission(PERMISSIONS.CRM_DELETE),

    // Operations
    viewOperations: () => hasPermission(PERMISSIONS.OPERATIONS_VIEW),
    manageOperations: () => hasPermission(PERMISSIONS.OPERATIONS_MANAGE),

    // Finance
    viewFinance: () => hasPermission(PERMISSIONS.FINANCE_VIEW),
    manageFinance: () => hasPermission(PERMISSIONS.FINANCE_MANAGE),

    // HR
    viewHR: () => hasPermission(PERMISSIONS.HR_VIEW),
    manageHR: () => hasPermission(PERMISSIONS.HR_MANAGE),

    // Admin
    manageUsers: () => hasPermission(PERMISSIONS.USERS_MANAGE),
    manageSettings: () => hasPermission(PERMISSIONS.SETTINGS_MANAGE),
  };

  return {
    permissions,
    isAdmin,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    can,
  };
}

export default usePermissions;
