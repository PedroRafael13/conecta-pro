'use client';

import { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type {
  Technician,
  TechnicianFilters,
  Route,
  StatusTecnico
} from '../../types';

// Mock data para desenvolvimento
const mockTechnicians: Technician[] = [
  {
    id: 't1',
    nome: 'Carlos Santos',
    avatar: undefined,
    status: 'ocupado',
    especialidades: ['Câmeras', 'Alarmes', 'Controle de Acesso'],
    localizacao: { lat: -23.5505, lng: -46.6333, endereco: 'Av. Paulista, 1000' },
    ordens_hoje: 3,
    rating: 4.8,
    telefone: '(11) 99999-1001',
    email: 'carlos.santos@conectapro.com',
    veiculo: 'Fiat Fiorino',
    placa_veiculo: 'ABC-1234',
  },
  {
    id: 't2',
    nome: 'Ana Paula Oliveira',
    avatar: undefined,
    status: 'disponivel',
    especialidades: ['Interfones', 'Portões Eletrônicos'],
    localizacao: { lat: -23.5630, lng: -46.6543, endereco: 'Rua Augusta, 500' },
    ordens_hoje: 2,
    rating: 4.9,
    telefone: '(11) 99999-1002',
    email: 'ana.oliveira@conectapro.com',
    veiculo: 'Renault Kangoo',
    placa_veiculo: 'DEF-5678',
  },
  {
    id: 't3',
    nome: 'Roberto Alves',
    avatar: undefined,
    status: 'em_deslocamento',
    especialidades: ['Catracas', 'Cancelas', 'Automação'],
    localizacao: { lat: -23.5870, lng: -46.6820, endereco: 'Av. Faria Lima, 2500' },
    ordens_hoje: 4,
    rating: 4.7,
    telefone: '(11) 99999-1003',
    email: 'roberto.alves@conectapro.com',
    veiculo: 'Fiat Strada',
    placa_veiculo: 'GHI-9012',
  },
  {
    id: 't4',
    nome: 'Fernanda Lima',
    avatar: undefined,
    status: 'disponivel',
    especialidades: ['Câmeras', 'CFTV', 'Redes'],
    localizacao: { lat: -23.5320, lng: -46.6200, endereco: 'Rua Verde, 789' },
    ordens_hoje: 1,
    rating: 4.6,
    telefone: '(11) 99999-1004',
    email: 'fernanda.lima@conectapro.com',
    veiculo: 'VW Saveiro',
    placa_veiculo: 'JKL-3456',
  },
  {
    id: 't5',
    nome: 'Marcos Souza',
    avatar: undefined,
    status: 'offline',
    especialidades: ['Alarmes', 'Sensores', 'Cerca Elétrica'],
    localizacao: undefined,
    ordens_hoje: 0,
    rating: 4.5,
    telefone: '(11) 99999-1005',
    email: 'marcos.souza@conectapro.com',
    veiculo: 'Fiat Mobi',
    placa_veiculo: 'MNO-7890',
  },
  {
    id: 't6',
    nome: 'Juliana Costa',
    avatar: undefined,
    status: 'disponivel',
    especialidades: ['Controle de Acesso', 'Biometria', 'Tags RFID'],
    localizacao: { lat: -23.5450, lng: -46.6400, endereco: 'Rua Oscar Freire, 200' },
    ordens_hoje: 2,
    rating: 4.8,
    telefone: '(11) 99999-1006',
    email: 'juliana.costa@conectapro.com',
    veiculo: 'Renault Duster',
    placa_veiculo: 'PQR-1234',
  },
];

const mockRoutes: Route[] = [
  {
    id: 'r1',
    tecnico_id: 't1',
    tecnico_nome: 'Carlos Santos',
    ordens: ['2', '6'],
    distancia_total_km: 15.3,
    tempo_estimado_min: 45,
    otimizada: true,
    data_criacao: '2024-01-15T08:00:00Z',
  },
  {
    id: 'r2',
    tecnico_id: 't3',
    tecnico_nome: 'Roberto Alves',
    ordens: ['3', '1', '5'],
    distancia_total_km: 28.7,
    tempo_estimado_min: 85,
    otimizada: false,
    data_criacao: '2024-01-15T08:30:00Z',
  },
];

// Simular delay de API
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// API Mock functions
const fetchTechnicians = async (filters?: TechnicianFilters): Promise<Technician[]> => {
  await delay(500);

  let technicians = [...mockTechnicians];

  if (filters) {
    if (filters.status?.length) {
      technicians = technicians.filter(t => filters.status!.includes(t.status));
    }
    if (filters.especialidade) {
      technicians = technicians.filter(t =>
        t.especialidades.some(e => e.toLowerCase().includes(filters.especialidade!.toLowerCase()))
      );
    }
    if (filters.search) {
      const search = filters.search.toLowerCase();
      technicians = technicians.filter(t =>
        t.nome.toLowerCase().includes(search) ||
        t.especialidades.some(e => e.toLowerCase().includes(search))
      );
    }
  }

  return technicians;
};

const fetchTechnicianById = async (id: string): Promise<Technician | null> => {
  await delay(300);
  return mockTechnicians.find(t => t.id === id) || null;
};

const updateTechnicianStatus = async (id: string, status: StatusTecnico): Promise<Technician> => {
  await delay(300);
  const index = mockTechnicians.findIndex(t => t.id === id);
  if (index === -1) throw new Error('Técnico não encontrado');
  mockTechnicians[index] = { ...mockTechnicians[index], status };
  return mockTechnicians[index];
};

const updateTechnicianLocation = async (
  id: string,
  location: { lat: number; lng: number; endereco?: string }
): Promise<Technician> => {
  await delay(300);
  const index = mockTechnicians.findIndex(t => t.id === id);
  if (index === -1) throw new Error('Técnico não encontrado');
  mockTechnicians[index] = {
    ...mockTechnicians[index],
    localizacao: { ...location, ultima_atualizacao: new Date().toISOString() }
  };
  return mockTechnicians[index];
};

const fetchRoutes = async (technicianId?: string): Promise<Route[]> => {
  await delay(400);
  if (technicianId) {
    return mockRoutes.filter(r => r.tecnico_id === technicianId);
  }
  return mockRoutes;
};

const fetchRouteById = async (id: string): Promise<Route | null> => {
  await delay(300);
  return mockRoutes.find(r => r.id === id) || null;
};

const optimizeRoute = async (routeId: string): Promise<Route> => {
  await delay(1000); // Simula processamento de otimização
  const index = mockRoutes.findIndex(r => r.id === routeId);
  if (index === -1) throw new Error('Rota não encontrada');

  // Simula redução de 20% na distância e tempo após otimização
  const route = mockRoutes[index];
  mockRoutes[index] = {
    ...route,
    distancia_total_km: route.distancia_total_km * 0.8,
    tempo_estimado_min: Math.round(route.tempo_estimado_min * 0.8),
    otimizada: true,
    data_atualizacao: new Date().toISOString(),
  };

  return mockRoutes[index];
};

const reorderRoute = async (routeId: string, newOrder: string[]): Promise<Route> => {
  await delay(500);
  const index = mockRoutes.findIndex(r => r.id === routeId);
  if (index === -1) throw new Error('Rota não encontrada');

  mockRoutes[index] = {
    ...mockRoutes[index],
    ordens: newOrder,
    otimizada: false,
    data_atualizacao: new Date().toISOString(),
  };

  return mockRoutes[index];
};

const createRoute = async (technicianId: string, orderIds: string[]): Promise<Route> => {
  await delay(500);

  const technician = mockTechnicians.find(t => t.id === technicianId);
  const newRoute: Route = {
    id: `r${mockRoutes.length + 1}`,
    tecnico_id: technicianId,
    tecnico_nome: technician?.nome,
    ordens: orderIds,
    distancia_total_km: orderIds.length * 8.5, // Estimativa fictícia
    tempo_estimado_min: orderIds.length * 25,
    otimizada: false,
    data_criacao: new Date().toISOString(),
  };

  mockRoutes.push(newRoute);
  return newRoute;
};

// Hook principal para técnicos
export function useTechnicians(initialFilters?: TechnicianFilters) {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<TechnicianFilters>(initialFilters || {});

  // Query para listar técnicos
  const techniciansQuery = useQuery({
    queryKey: ['technicians', filters],
    queryFn: () => fetchTechnicians(filters),
    staleTime: 30000,
    refetchInterval: 60000, // Atualiza a cada minuto
  });

  // Mutation para atualizar status
  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: StatusTecnico }) =>
      updateTechnicianStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['technicians'] });
    },
  });

  // Mutation para atualizar localização
  const locationMutation = useMutation({
    mutationFn: ({ id, location }: {
      id: string;
      location: { lat: number; lng: number; endereco?: string }
    }) => updateTechnicianLocation(id, location),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['technicians'] });
    },
  });

  // Estatísticas computadas
  const stats = useMemo(() => {
    const technicians = techniciansQuery.data || [];
    return {
      total: technicians.length,
      disponiveis: technicians.filter(t => t.status === 'disponivel').length,
      ocupados: technicians.filter(t => t.status === 'ocupado').length,
      emDeslocamento: technicians.filter(t => t.status === 'em_deslocamento').length,
      offline: technicians.filter(t => t.status === 'offline').length,
      ratingMedio: technicians.length > 0
        ? technicians.reduce((acc, t) => acc + t.rating, 0) / technicians.length
        : 0,
    };
  }, [techniciansQuery.data]);

  // Função para atualizar filtros
  const updateFilters = useCallback((newFilters: Partial<TechnicianFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  // Função para limpar filtros
  const clearFilters = useCallback(() => {
    setFilters({});
  }, []);

  return {
    // Data
    technicians: techniciansQuery.data || [],
    stats,
    filters,

    // Loading states
    isLoading: techniciansQuery.isLoading,
    isUpdating: statusMutation.isPending || locationMutation.isPending,

    // Error states
    error: techniciansQuery.error,

    // Actions
    updateStatus: (id: string, status: StatusTecnico) => statusMutation.mutateAsync({ id, status }),
    updateLocation: (id: string, location: { lat: number; lng: number; endereco?: string }) =>
      locationMutation.mutateAsync({ id, location }),

    // Filter actions
    updateFilters,
    clearFilters,
    setFilters,

    // Refetch
    refetch: techniciansQuery.refetch,
  };
}

// Hook para técnico individual
export function useTechnician(id: string) {
  const technicianQuery = useQuery({
    queryKey: ['technician', id],
    queryFn: () => fetchTechnicianById(id),
    enabled: !!id,
    refetchInterval: 30000,
  });

  return {
    technician: technicianQuery.data,
    isLoading: technicianQuery.isLoading,
    error: technicianQuery.error,
    refetch: technicianQuery.refetch,
  };
}

// Hook para rotas
export function useRoutes(technicianId?: string) {
  const queryClient = useQueryClient();

  const routesQuery = useQuery({
    queryKey: ['routes', technicianId],
    queryFn: () => fetchRoutes(technicianId),
    staleTime: 30000,
  });

  // Mutation para otimizar rota
  const optimizeMutation = useMutation({
    mutationFn: optimizeRoute,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routes'] });
    },
  });

  // Mutation para reordenar rota
  const reorderMutation = useMutation({
    mutationFn: ({ routeId, newOrder }: { routeId: string; newOrder: string[] }) =>
      reorderRoute(routeId, newOrder),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routes'] });
    },
  });

  // Mutation para criar rota
  const createMutation = useMutation({
    mutationFn: ({ technicianId, orderIds }: { technicianId: string; orderIds: string[] }) =>
      createRoute(technicianId, orderIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routes'] });
    },
  });

  return {
    routes: routesQuery.data || [],
    isLoading: routesQuery.isLoading,
    isOptimizing: optimizeMutation.isPending,
    isReordering: reorderMutation.isPending,
    isCreating: createMutation.isPending,
    error: routesQuery.error,

    // Actions
    optimizeRoute: optimizeMutation.mutateAsync,
    reorderRoute: (routeId: string, newOrder: string[]) =>
      reorderMutation.mutateAsync({ routeId, newOrder }),
    createRoute: (technicianId: string, orderIds: string[]) =>
      createMutation.mutateAsync({ technicianId, orderIds }),

    refetch: routesQuery.refetch,
  };
}

// Hook para rota individual
export function useRoute(id: string) {
  const routeQuery = useQuery({
    queryKey: ['route', id],
    queryFn: () => fetchRouteById(id),
    enabled: !!id,
  });

  return {
    route: routeQuery.data,
    isLoading: routeQuery.isLoading,
    error: routeQuery.error,
    refetch: routeQuery.refetch,
  };
}

export default useTechnicians;
