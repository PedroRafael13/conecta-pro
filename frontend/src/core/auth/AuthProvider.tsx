import { useEffect, type ReactNode } from 'react';
import { useAuthStore } from '@stores/authStore';
import { setupInterceptors } from '@core/api';

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { checkAuth, isLoading, token } = useAuthStore();

  useEffect(() => {
    // Setup API interceptors
    setupInterceptors();

    // Check auth on mount
    if (token) {
      checkAuth();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (isLoading && token) {
    return (
      <div className="min-h-screen bg-conecta-gradient flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4" />
          <p className="text-white text-sm">Carregando...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

export default AuthProvider;
