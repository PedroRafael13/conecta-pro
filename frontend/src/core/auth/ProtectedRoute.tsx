import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './useAuth';

interface ProtectedRouteProps {
  requiredPermissions?: string[];
  requireAll?: boolean;
  redirectTo?: string;
}

export function ProtectedRoute({
  requiredPermissions,
  requireAll = false,
  redirectTo = '/login',
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, hasAnyPermission, hasAllPermissions } =
    useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-conecta-escuro" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  if (requiredPermissions && requiredPermissions.length > 0) {
    const hasPermission = requireAll
      ? hasAllPermissions(requiredPermissions)
      : hasAnyPermission(requiredPermissions);

    if (!hasPermission) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Acesso Negado
            </h1>
            <p className="text-gray-600">
              Voce nao tem permissao para acessar esta pagina.
            </p>
          </div>
        </div>
      );
    }
  }

  return <Outlet />;
}

export default ProtectedRoute;
