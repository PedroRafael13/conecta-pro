'use client';

import { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type {
  ServiceOrder,
  ServiceOrderFilters,
  OrderTimelineEvent,
  StatusOrdem
} from '../../types';

// Mock data para desenvolvimento
const mockOrders: ServiceOrder[] = [
  {
    id: '1',
    numero: 'OS-2024-0001',
    cliente: 'Condomínio Solar das Palmeiras',
    endereco: 'Rua das Flores, 123 - Centro',
    tipo: 'instalacao',
    prioridade: 'alta',
    status: 'aberta',
    descricao: 'Instalação de câmeras de segurança no bloco A',
    data_abertura: '2024-01-15T08:00:00Z',
    data_agendamento: '2024-01-16T09:00:00Z',
    sla_horas: 8,
    contato_cliente: 'João Silva',
    telefone_cliente: '(11) 99999-0001',
    equipamentos: ['Câmera IP HD', 'DVR 8 canais', 'Cabo coaxial 100m'],
  },
  {
    id: '2',
    numero: 'OS-2024-0002',
    cliente: 'Edifício Comercial Horizonte',
    endereco: 'Av. Paulista, 1000 - Bela Vista',
    tipo: 'manutencao',
    prioridade: 'normal',
    status: 'em_atendimento',
    tecnico_id: 't1',
    tecnico_nome: 'Carlos Santos',
    descricao: 'Manutenção preventiva do sistema de controle de acesso',
    data_abertura: '2024-01-14T10:30:00Z',
    data_agendamento: '2024-01-15T14:00:00Z',
    sla_horas: 24,
    contato_cliente: 'Maria Oliveira',
    telefone_cliente: '(11) 99999-0002',
  },
  {
    id: '3',
    numero: 'OS-2024-0003',
    cliente: 'Residencial Park Avenue',
    endereco: 'Rua Augusta, 500 - Consolação',
    tipo: 'reparo',
    prioridade: 'urgente',
    status: 'aberta',
    descricao: 'Portão eletrônico não está funcionando - moradores sem acesso',
    data_abertura: '2024-01-15T07:30:00Z',
    sla_horas: 4,
    contato_cliente: 'Pedro Costa',
    telefone_cliente: '(11) 99999-0003',
  },
  {
    id: '4',
    numero: 'OS-2024-0004',
    cliente: 'Shopping Center Norte',
    endereco: 'Av. Brasil, 2000 - Zona Norte',
    tipo: 'inspecao',
    prioridade: 'baixa',
    status: 'concluida',
    tecnico_id: 't2',
    tecnico_nome: 'Ana Paula',
    descricao: 'Inspeção trimestral do sistema de alarme',
    data_abertura: '2024-01-10T09:00:00Z',
    data_agendamento: '2024-01-12T10:00:00Z',
    data_conclusao: '2024-01-12T12:30:00Z',
    sla_horas: 48,
  },
  {
    id: '5',
    numero: 'OS-2024-0005',
    cliente: 'Condomínio Vista Verde',
    endereco: 'Rua Verde, 789 - Jardins',
    tipo: 'instalacao',
    prioridade: 'normal',
    status: 'aberta',
    descricao: 'Instalação de interfones nos apartamentos do bloco C',
    data_abertura: '2024-01-15T11:00:00Z',
    data_agendamento: '2024-01-17T08:00:00Z',
    sla_horas: 24,
    contato_cliente: 'Fernanda Lima',
    telefone_cliente: '(11) 99999-0005',
    equipamentos: ['Interfone digital', 'Central portaria', 'Fonte 12V'],
  },
  {
    id: '6',
    numero: 'OS-2024-0006',
    cliente: 'Torre Empresarial Delta',
    endereco: 'Av. Faria Lima, 3000 - Itaim Bibi',
    tipo: 'reparo',
    prioridade: 'alta',
    status: 'em_atendimento',
    tecnico_id: 't3',
    tecnico_nome: 'Roberto Alves',
    descricao: 'Catraca do estacionamento travada',
    data_abertura: '2024-01-15T06:45:00Z',
    sla_horas: 8,
    contato_cliente: 'Lucas Mendes',
    telefone_cliente: '(11) 99999-0006',
  },
];

const mockTimelineEvents: OrderTimelineEvent[] = [
  {
    id: 'evt1',
    ordem_id: '2',
    tipo: 'abertura',
    descricao: 'Ordem de serviço criada',
    data: '2024-01-14T10:30:00Z',
    usuario: 'Sistema',
  },
  {
    id: 'evt2',
    ordem_id: '2',
    tipo: 'atribuicao',
    descricao: 'Técnico Carlos Santos atribuído',
    data: '2024-01-14T11:00:00Z',
    usuario: 'Admin',
  },
  {
    id: 'evt3',
    ordem_id: '2',
    tipo: 'deslocamento',
    descricao: 'Técnico iniciou deslocamento',
    data: '2024-01-15T13:30:00Z',
    usuario: 'Carlos Santos',
  },
  {
    id: 'evt4',
    ordem_id: '2',
    tipo: 'chegada',
    descricao: 'Técnico chegou ao local',
    data: '2024-01-15T14:15:00Z',
    usuario: 'Carlos Santos',
  },
  {
    id: 'evt5',
    ordem_id: '2',
    tipo: 'inicio_atendimento',
    descricao: 'Atendimento iniciado',
    data: '2024-01-15T14:20:00Z',
    usuario: 'Carlos Santos',
  },
];

// Simular delay de API
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// API Mock functions
const fetchOrders = async (filters?: ServiceOrderFilters): Promise<ServiceOrder[]> => {
  await delay(500);

  let orders = [...mockOrders];

  if (filters) {
    if (filters.status?.length) {
      orders = orders.filter(o => filters.status!.includes(o.status));
    }
    if (filters.tipo?.length) {
      orders = orders.filter(o => filters.tipo!.includes(o.tipo));
    }
    if (filters.prioridade?.length) {
      orders = orders.filter(o => filters.prioridade!.includes(o.prioridade));
    }
    if (filters.tecnico_id) {
      orders = orders.filter(o => o.tecnico_id === filters.tecnico_id);
    }
    if (filters.search) {
      const search = filters.search.toLowerCase();
      orders = orders.filter(o =>
        o.numero.toLowerCase().includes(search) ||
        o.cliente.toLowerCase().includes(search) ||
        o.descricao.toLowerCase().includes(search)
      );
    }
  }

  return orders;
};

const fetchOrderById = async (id: string): Promise<ServiceOrder | null> => {
  await delay(300);
  return mockOrders.find(o => o.id === id) || null;
};

const fetchOrderTimeline = async (orderId: string): Promise<OrderTimelineEvent[]> => {
  await delay(300);
  return mockTimelineEvents.filter(e => e.ordem_id === orderId);
};

const createOrder = async (order: Partial<ServiceOrder>): Promise<ServiceOrder> => {
  await delay(500);
  const newOrder: ServiceOrder = {
    id: String(mockOrders.length + 1),
    numero: `OS-2024-${String(mockOrders.length + 1).padStart(4, '0')}`,
    cliente: order.cliente || '',
    endereco: order.endereco || '',
    tipo: order.tipo || 'manutencao',
    prioridade: order.prioridade || 'normal',
    status: 'aberta',
    descricao: order.descricao || '',
    data_abertura: new Date().toISOString(),
    sla_horas: order.sla_horas || 24,
    ...order,
  };
  mockOrders.push(newOrder);
  return newOrder;
};

const updateOrder = async (id: string, data: Partial<ServiceOrder>): Promise<ServiceOrder> => {
  await delay(500);
  const index = mockOrders.findIndex(o => o.id === id);
  if (index === -1) throw new Error('Ordem não encontrada');
  mockOrders[index] = { ...mockOrders[index], ...data };
  return mockOrders[index];
};

const updateOrderStatus = async (id: string, status: StatusOrdem): Promise<ServiceOrder> => {
  return updateOrder(id, {
    status,
    ...(status === 'concluida' ? { data_conclusao: new Date().toISOString() } : {})
  });
};

const assignTechnician = async (orderId: string, technicianId: string, technicianName: string): Promise<ServiceOrder> => {
  return updateOrder(orderId, {
    tecnico_id: technicianId,
    tecnico_nome: technicianName
  });
};

// Hook principal
export function useServiceOrders(initialFilters?: ServiceOrderFilters) {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<ServiceOrderFilters>(initialFilters || {});

  // Query para listar ordens
  const ordersQuery = useQuery({
    queryKey: ['service-orders', filters],
    queryFn: () => fetchOrders(filters),
    staleTime: 30000,
  });

  // Mutation para criar ordem
  const createMutation = useMutation({
    mutationFn: createOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['service-orders'] });
    },
  });

  // Mutation para atualizar ordem
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ServiceOrder> }) => updateOrder(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['service-orders'] });
    },
  });

  // Mutation para atualizar status
  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: StatusOrdem }) => updateOrderStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['service-orders'] });
    },
  });

  // Mutation para atribuir técnico
  const assignMutation = useMutation({
    mutationFn: ({ orderId, technicianId, technicianName }: {
      orderId: string;
      technicianId: string;
      technicianName: string
    }) => assignTechnician(orderId, technicianId, technicianName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['service-orders'] });
    },
  });

  // Estatísticas computadas
  const stats = useMemo(() => {
    const orders = ordersQuery.data || [];
    return {
      total: orders.length,
      abertas: orders.filter(o => o.status === 'aberta').length,
      emAtendimento: orders.filter(o => o.status === 'em_atendimento').length,
      concluidas: orders.filter(o => o.status === 'concluida').length,
      canceladas: orders.filter(o => o.status === 'cancelada').length,
      urgentes: orders.filter(o => o.prioridade === 'urgente' && o.status !== 'concluida').length,
    };
  }, [ordersQuery.data]);

  // Função para atualizar filtros
  const updateFilters = useCallback((newFilters: Partial<ServiceOrderFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  // Função para limpar filtros
  const clearFilters = useCallback(() => {
    setFilters({});
  }, []);

  return {
    // Data
    orders: ordersQuery.data || [],
    stats,
    filters,

    // Loading states
    isLoading: ordersQuery.isLoading,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,

    // Error states
    error: ordersQuery.error,

    // Actions
    createOrder: createMutation.mutateAsync,
    updateOrder: (id: string, data: Partial<ServiceOrder>) => updateMutation.mutateAsync({ id, data }),
    updateStatus: (id: string, status: StatusOrdem) => statusMutation.mutateAsync({ id, status }),
    assignTechnician: (orderId: string, technicianId: string, technicianName: string) =>
      assignMutation.mutateAsync({ orderId, technicianId, technicianName }),

    // Filter actions
    updateFilters,
    clearFilters,
    setFilters,

    // Refetch
    refetch: ordersQuery.refetch,
  };
}

// Hook para ordem individual
export function useServiceOrder(id: string) {

  const orderQuery = useQuery({
    queryKey: ['service-order', id],
    queryFn: () => fetchOrderById(id),
    enabled: !!id,
  });

  const timelineQuery = useQuery({
    queryKey: ['service-order-timeline', id],
    queryFn: () => fetchOrderTimeline(id),
    enabled: !!id,
  });

  return {
    order: orderQuery.data,
    timeline: timelineQuery.data || [],
    isLoading: orderQuery.isLoading,
    isLoadingTimeline: timelineQuery.isLoading,
    error: orderQuery.error,
    refetch: () => {
      orderQuery.refetch();
      timelineQuery.refetch();
    },
  };
}

export default useServiceOrders;
