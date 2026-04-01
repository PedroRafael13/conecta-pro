'use client';

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { customInstance } from '@/lib/api-client';

interface Condominio {
  id: string;
  nome: string;
  tipo?: string;
  status?: string;
}

interface CondominioContextType {
  condominioId: string;
  setCondominioId: (id: string) => void;
  condominios: Condominio[];
  isLoading: boolean;
  condominioAtual: Condominio | undefined;
}

const CondominioContext = createContext<CondominioContextType | undefined>(undefined);

const STORAGE_KEY = 'conecta-pro-condominio-id';

interface CondominioProviderProps {
  children: ReactNode;
}

export function CondominioProvider({ children }: CondominioProviderProps) {
  const [condominioId, setCondominioIdState] = useState<string>('a1b2c3d4-e5f6-7890-abcd-ef1234567890');
  const [condominios, setCondominios] = useState<Condominio[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Carrega condomínio salvo do localStorage
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      setCondominioIdState(saved);
    }
    setIsLoading(false);
  }, []);

  // Busca lista de condomínios disponíveis
  useEffect(() => {
    const fetchCondominios = async () => {
      try {
        // Busca clientes primeiro
        const clients = await customInstance<{ items?: Array<{ id: string }>; } | Array<{ id: string }>>({
          url: '/api/v1/clients',
          method: 'GET',
          params: { skip: 0, limit: 100 },
        });

        const clientList = Array.isArray(clients) ? clients : clients?.items ?? [];

        // Busca condomínios de cada cliente
        const allCondominios: Condominio[] = [];
        for (const client of clientList) {
          try {
            const conds = await customInstance<Array<{ id: string; nome?: string; name?: string; tipo?: string; type?: string; condominium_type?: string; status?: string }>>({
              url: `/api/v1/clients/${client.id}/condominiums`,
              method: 'GET',
            }).catch(() => [] as Array<{ id: string; nome?: string; name?: string; tipo?: string; type?: string; condominium_type?: string; status?: string }>);

            if (Array.isArray(conds)) {
              allCondominios.push(
                ...conds.map((c) => ({
                  id: c.id,
                  nome: c.nome || c.name || 'Sem nome',
                  tipo: c.tipo || c.type,
                  status: c.status,
                }))
              );
            }
          } catch {
            // Ignora erro de cliente individual
          }
        }

        setCondominios(allCondominios);

        // Se não tem condomínio selecionado mas tem condomínios, seleciona o primeiro
        if (!condominioId && allCondominios.length > 0) {
          const saved = localStorage.getItem(STORAGE_KEY);
          const first = allCondominios[0];
          const id = saved && allCondominios.some((c) => c.id === saved)
            ? saved
            : first?.id ?? '';
          setCondominioIdState(id);
          localStorage.setItem(STORAGE_KEY, id);
        }
      } catch {
        // API não disponível — mantém lista vazia
      }
    };

    fetchCondominios();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setCondominioId = useCallback((id: string) => {
    setCondominioIdState(id);
    if (id) {
      localStorage.setItem(STORAGE_KEY, id);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const condominioAtual = condominios.find((c) => c.id === condominioId);

  return (
    <CondominioContext.Provider
      value={{
        condominioId,
        setCondominioId,
        condominios,
        isLoading,
        condominioAtual,
      }}
    >
      {children}
    </CondominioContext.Provider>
  );
}

export function useCondominio() {
  const context = useContext(CondominioContext);
  if (!context) {
    // Fallback gracioso — retorna valores padrão se usado fora do provider
    return {
      condominioId: '',
      setCondominioId: () => {},
      condominios: [],
      isLoading: false,
      condominioAtual: undefined,
    } as CondominioContextType;
  }
  return context;
}
