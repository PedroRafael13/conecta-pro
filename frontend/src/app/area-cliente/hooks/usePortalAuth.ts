'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export function usePortalAuth() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [clientName, setClientName] = useState<string>('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const t = localStorage.getItem('portal_token');
    const name = localStorage.getItem('portal_client_name');
    if (t) {
      setToken(t);
      setClientName(name || 'Cliente');
      setIsAuthenticated(true);
    }
  }, []);

  function logout() {
    localStorage.removeItem('portal_token');
    localStorage.removeItem('portal_client_name');
    localStorage.removeItem('portal_client_id');
    setToken(null);
    setIsAuthenticated(false);
    router.push('/area-cliente/login');
  }

  return { token, clientName, isAuthenticated, logout };
}
