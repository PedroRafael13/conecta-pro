import { useAuthStore } from '@stores/authStore';
import type { LoginCredentials, User } from '@core/types/auth.types';

export function useAuth() {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    clearError,
  } = useAuthStore();

  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    return user.permissions.includes(permission) || user.role === 'admin';
  };

  const hasAnyPermission = (permissions: string[]): boolean => {
    if (!user) return false;
    if (user.role === 'admin') return true;
    return permissions.some((p) => user.permissions.includes(p));
  };

  const hasAllPermissions = (permissions: string[]): boolean => {
    if (!user) return false;
    if (user.role === 'admin') return true;
    return permissions.every((p) => user.permissions.includes(p));
  };

  const handleLogin = async (credentials: LoginCredentials) => {
    await login(credentials);
  };

  const handleLogout = async () => {
    await logout();
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login: handleLogin,
    logout: handleLogout,
    clearError,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  };
}

export type UseAuthReturn = ReturnType<typeof useAuth>;
export type AuthUser = User;
export default useAuth;
