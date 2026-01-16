// Hook para Maintenance - Facilities Module
// Conecta PRO

import { useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type {
  MaintenanceOrder,
  MaintenanceFilter,
  MaintenanceStats,
  MaintenanceCalendarEvent,
  PredictiveAlert,
  Technician,
  CreateMaintenanceOrderDTO,
  UpdateMaintenanceOrderDTO,
  MaintenanceStatus,
  MaintenanceType,
  MaintenanceChecklistItem
} from '../types/maintenance.types';

// Mock data para desenvolvimento
const mockMaintenanceOrders: MaintenanceOrder[] = [
  {
    id: 'MNT-001',
    numero: 'OS-2024-0001',
    equipment_id: '1',
    equipment_nome: 'Ar Condicionado Split 36.000 BTUs',
    equipment_codigo: 'EQP-001',
    equipment_localizacao: 'Bloco A - Sala de Servidores',
    tipo: 'preventiva',
    prioridade: 'normal',
    status: 'agendada',
    descricao: 'Limpeza de filtros e verificacao do sistema de refrigeracao',
    tecnico_responsavel: 'Joao Silva',
    tecnico_id: 'TEC-001',
    data_agendada: '2024-04-10',
    tempo_estimado_horas: 2,
    custo_estimado: 350,
    checklist: [
      { id: '1', descricao: 'Desligar equipamento', concluido: false },
      { id: '2', descricao: 'Remover filtros', concluido: false },
      { id: '3', descricao: 'Limpar filtros com agua', concluido: false },
      { id: '4', descricao: 'Verificar gas refrigerante', concluido: false },
      { id: '5', descricao: 'Testar funcionamento', concluido: false }
    ],
    created_at: '2024-01-15T10:00:00Z',
    created_by: 'admin@conectapro.com.br'
  },
  {
    id: 'MNT-002',
    numero: 'OS-2024-0002',
    equipment_id: '2',
    equipment_nome: 'Gerador Diesel 150 kVA',
    equipment_codigo: 'EQP-002',
    equipment_localizacao: 'Subsolo - Casa de Maquinas',
    tipo: 'corretiva',
    prioridade: 'urgente',
    status: 'em_execucao',
    descricao: 'Reparo no sistema de injecao de combustivel - Vazamento detectado',
    tecnico_responsavel: 'Maria Santos',
    tecnico_id: 'TEC-002',
    data_agendada: '2024-01-12',
    data_inicio: '2024-01-12T08:30:00Z',
    tempo_estimado_horas: 6,
    custo_estimado: 2500,
    pecas_utilizadas: [
      { id: '1', nome: 'Bomba injetora', codigo: 'BI-150', quantidade: 1, valor_unitario: 1200, valor_total: 1200 },
      { id: '2', nome: 'Mangueira combustivel', codigo: 'MC-08', quantidade: 2, valor_unitario: 85, valor_total: 170 }
    ],
    observacoes: 'Peca principal ja foi substituida, aguardando teste de pressao',
    created_at: '2024-01-12T07:00:00Z',
    created_by: 'supervisor@conectapro.com.br'
  },
  {
    id: 'MNT-003',
    numero: 'OS-2024-0003',
    equipment_id: '3',
    equipment_nome: 'Elevador Social 01',
    equipment_codigo: 'EQP-003',
    equipment_localizacao: 'Torre A - Hall Principal',
    tipo: 'preventiva',
    prioridade: 'alta',
    status: 'concluida',
    descricao: 'Manutencao mensal preventiva - Lubrificacao e ajustes',
    tecnico_responsavel: 'Carlos Oliveira',
    tecnico_id: 'TEC-003',
    data_agendada: '2024-01-05',
    data_inicio: '2024-01-05T09:00:00Z',
    data_conclusao: '2024-01-05T14:30:00Z',
    tempo_estimado_horas: 4,
    tempo_real_horas: 5.5,
    custo_estimado: 800,
    custo_real: 850,
    checklist: [
      { id: '1', descricao: 'Verificar cabos de tracao', concluido: true },
      { id: '2', descricao: 'Lubrificar guias', concluido: true },
      { id: '3', descricao: 'Testar sistema de freio', concluido: true },
      { id: '4', descricao: 'Verificar nivelamento', concluido: true },
      { id: '5', descricao: 'Testar interfone', concluido: true }
    ],
    observacoes: 'Detectado desgaste nos rolamentos - agendar troca em 30 dias',
    created_at: '2024-01-02T11:00:00Z',
    created_by: 'gestor@conectapro.com.br'
  },
  {
    id: 'MNT-004',
    numero: 'OS-2024-0004',
    equipment_id: '4',
    equipment_nome: 'Bomba Pressurizadora 3CV',
    equipment_codigo: 'EQP-004',
    equipment_localizacao: 'Subsolo - Cisterna',
    tipo: 'preditiva',
    prioridade: 'normal',
    status: 'agendada',
    descricao: 'Substituicao preventiva de rolamentos baseado em analise de vibracao',
    tecnico_responsavel: 'Ana Costa',
    tecnico_id: 'TEC-004',
    data_agendada: '2024-01-20',
    tempo_estimado_horas: 3,
    custo_estimado: 650,
    created_at: '2024-01-10T14:00:00Z',
    created_by: 'ia@conectapro.com.br'
  }
];

const mockPredictiveAlerts: PredictiveAlert[] = [
  {
    id: 'PRED-001',
    equipment_id: '4',
    equipment_nome: 'Bomba Pressurizadora 3CV',
    equipment_codigo: 'EQP-004',
    probabilidade_falha: 78,
    dias_estimados: 15,
    recomendacao: 'Substituir rolamentos antes que ocorra falha catastrofica. Analise de vibracao indica desgaste avancado.',
    baseado_em: ['Analise de vibracao', 'Historico de manutencao', 'Idade do componente', 'Horas de operacao'],
    severidade: 'alta',
    modelo_ia: 'Predictive Maintenance v2.1',
    confianca: 85,
    created_at: '2024-01-10T12:00:00Z',
    acknowledged: true,
    ordem_criada: true,
    ordem_id: 'MNT-004'
  },
  {
    id: 'PRED-002',
    equipment_id: '1',
    equipment_nome: 'Ar Condicionado Split 36.000 BTUs',
    equipment_codigo: 'EQP-001',
    probabilidade_falha: 45,
    dias_estimados: 45,
    recomendacao: 'Verificar compressor - Consumo de energia 12% acima do esperado nas ultimas 2 semanas.',
    baseado_em: ['Consumo de energia', 'Temperatura de operacao', 'Ciclos de acionamento'],
    severidade: 'media',
    modelo_ia: 'Predictive Maintenance v2.1',
    confianca: 72,
    created_at: '2024-01-11T09:30:00Z',
    acknowledged: false,
    ordem_criada: false
  }
];

const mockTechnicians: Technician[] = [
  { id: 'TEC-001', nome: 'Joao Silva', email: 'joao@tecnico.com', telefone: '11999001001', especialidades: ['HVAC', 'Refrigeracao'], disponivel: true, ordens_ativas: 1 },
  { id: 'TEC-002', nome: 'Maria Santos', email: 'maria@tecnico.com', telefone: '11999002002', especialidades: ['Geradores', 'Eletrica'], disponivel: false, ordens_ativas: 2 },
  { id: 'TEC-003', nome: 'Carlos Oliveira', email: 'carlos@tecnico.com', telefone: '11999003003', especialidades: ['Elevadores', 'Mecanica'], disponivel: true, ordens_ativas: 0 },
  { id: 'TEC-004', nome: 'Ana Costa', email: 'ana@tecnico.com', telefone: '11999004004', especialidades: ['Hidraulica', 'Bombas'], disponivel: true, ordens_ativas: 1 }
];

// API mock functions
const fetchMaintenanceOrders = async (filters?: MaintenanceFilter): Promise<MaintenanceOrder[]> => {
  await new Promise(resolve => setTimeout(resolve, 400));

  let result = [...mockMaintenanceOrders];

  if (filters?.search) {
    const search = filters.search.toLowerCase();
    result = result.filter(m =>
      m.numero.toLowerCase().includes(search) ||
      m.equipment_nome.toLowerCase().includes(search) ||
      m.descricao.toLowerCase().includes(search)
    );
  }

  if (filters?.status?.length) {
    result = result.filter(m => filters.status!.includes(m.status));
  }

  if (filters?.tipo?.length) {
    result = result.filter(m => filters.tipo!.includes(m.tipo));
  }

  if (filters?.prioridade?.length) {
    result = result.filter(m => filters.prioridade!.includes(m.prioridade));
  }

  if (filters?.tecnico_id) {
    result = result.filter(m => m.tecnico_id === filters.tecnico_id);
  }

  if (filters?.equipment_id) {
    result = result.filter(m => m.equipment_id === filters.equipment_id);
  }

  if (filters?.atrasadas) {
    const today = new Date();
    result = result.filter(m => {
      if (m.status === 'concluida' || m.status === 'cancelada') return false;
      return new Date(m.data_agendada) < today;
    });
  }

  return result;
};

const fetchMaintenanceOrderById = async (id: string): Promise<MaintenanceOrder | null> => {
  await new Promise(resolve => setTimeout(resolve, 200));
  return mockMaintenanceOrders.find(m => m.id === id) || null;
};

const fetchMaintenanceStats = async (): Promise<MaintenanceStats> => {
  await new Promise(resolve => setTimeout(resolve, 200));

  const today = new Date();
  const orders = mockMaintenanceOrders;

  const concluidas = orders.filter(m => m.status === 'concluida');
  const tempoTotal = concluidas.reduce((acc, m) => acc + (m.tempo_real_horas || 0), 0);

  return {
    total: orders.length,
    agendadas: orders.filter(m => m.status === 'agendada').length,
    em_execucao: orders.filter(m => m.status === 'em_execucao').length,
    concluidas: concluidas.length,
    atrasadas: orders.filter(m => {
      if (m.status === 'concluida' || m.status === 'cancelada') return false;
      return new Date(m.data_agendada) < today;
    }).length,
    canceladas: orders.filter(m => m.status === 'cancelada').length,
    preventivas: orders.filter(m => m.tipo === 'preventiva').length,
    corretivas: orders.filter(m => m.tipo === 'corretiva').length,
    preditivas: orders.filter(m => m.tipo === 'preditiva').length,
    custo_total_mes: orders.reduce((acc, m) => acc + (m.custo_real || m.custo_estimado || 0), 0),
    tempo_medio_resolucao: concluidas.length > 0 ? tempoTotal / concluidas.length : 0,
    taxa_cumprimento: orders.length > 0 ? (concluidas.length / orders.length) * 100 : 0
  };
};

const fetchCalendarEvents = async (
  startDate: string,
  endDate: string
): Promise<MaintenanceCalendarEvent[]> => {
  await new Promise(resolve => setTimeout(resolve, 300));

  return mockMaintenanceOrders
    .filter(m => {
      const date = new Date(m.data_agendada);
      return date >= new Date(startDate) && date <= new Date(endDate);
    })
    .map(m => ({
      id: m.id,
      title: `${m.numero} - ${m.equipment_nome}`,
      date: m.data_agendada,
      tipo: m.tipo,
      prioridade: m.prioridade,
      status: m.status,
      equipment_nome: m.equipment_nome
    }));
};

const fetchPredictiveAlerts = async (): Promise<PredictiveAlert[]> => {
  await new Promise(resolve => setTimeout(resolve, 300));
  return [...mockPredictiveAlerts];
};

const fetchTechnicians = async (): Promise<Technician[]> => {
  await new Promise(resolve => setTimeout(resolve, 200));
  return [...mockTechnicians];
};

// Mutations
const createMaintenanceOrder = async (data: CreateMaintenanceOrderDTO): Promise<MaintenanceOrder> => {
  await new Promise(resolve => setTimeout(resolve, 500));

  // Converter checklist de string[] para MaintenanceChecklistItem[]
  const checklistItems = data.checklist?.map((item, index) => ({
    id: String(index + 1),
    descricao: item,
    concluido: false
  }));

  const newOrder: MaintenanceOrder = {
    id: `MNT-${String(mockMaintenanceOrders.length + 1).padStart(3, '0')}`,
    numero: `OS-2024-${String(mockMaintenanceOrders.length + 1).padStart(4, '0')}`,
    equipment_id: data.equipment_id,
    tipo: data.tipo,
    prioridade: data.prioridade,
    descricao: data.descricao,
    data_agendada: data.data_agendada,
    tecnico_id: data.tecnico_id,
    tempo_estimado_horas: data.tempo_estimado_horas,
    custo_estimado: data.custo_estimado,
    checklist: checklistItems,
    equipment_nome: 'Equipamento ' + data.equipment_id,
    status: 'agendada',
    created_at: new Date().toISOString(),
    created_by: 'admin@conectapro.com.br'
  };

  mockMaintenanceOrders.push(newOrder);
  return newOrder;
};

const updateMaintenanceOrder = async (
  id: string,
  data: UpdateMaintenanceOrderDTO
): Promise<MaintenanceOrder> => {
  await new Promise(resolve => setTimeout(resolve, 500));

  const index = mockMaintenanceOrders.findIndex(m => m.id === id);
  if (index === -1) throw new Error('Ordem de manutencao nao encontrada');

  // Converter checklist se fornecido
  const checklistItems = data.checklist?.map((item, idx) =>
    typeof item === 'string'
      ? { id: String(idx + 1), descricao: item, concluido: false }
      : item
  );

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { checklist: _checklist, ...restData } = data;

  mockMaintenanceOrders[index] = {
    ...mockMaintenanceOrders[index],
    ...restData,
    ...(checklistItems && { checklist: checklistItems as MaintenanceChecklistItem[] }),
    updated_at: new Date().toISOString()
  };

  return mockMaintenanceOrders[index];
};

const startMaintenanceOrder = async (id: string): Promise<MaintenanceOrder> => {
  return updateMaintenanceOrder(id, {
    status: 'em_execucao',
    data_inicio: new Date().toISOString()
  });
};

const completeMaintenanceOrder = async (
  id: string,
  data: { custo_real?: number; tempo_real_horas?: number; observacoes?: string }
): Promise<MaintenanceOrder> => {
  return updateMaintenanceOrder(id, {
    status: 'concluida',
    data_conclusao: new Date().toISOString(),
    ...data
  });
};

const cancelMaintenanceOrder = async (id: string, motivo: string): Promise<MaintenanceOrder> => {
  return updateMaintenanceOrder(id, {
    status: 'cancelada',
    observacoes: motivo
  });
};

const acknowledgePredictiveAlert = async (alertId: string): Promise<PredictiveAlert> => {
  await new Promise(resolve => setTimeout(resolve, 300));

  const index = mockPredictiveAlerts.findIndex(a => a.id === alertId);
  if (index === -1) throw new Error('Alerta nao encontrado');

  mockPredictiveAlerts[index] = {
    ...mockPredictiveAlerts[index],
    acknowledged: true
  };

  return mockPredictiveAlerts[index];
};

const createOrderFromPredictiveAlert = async (alertId: string): Promise<MaintenanceOrder> => {
  await new Promise(resolve => setTimeout(resolve, 500));

  const alert = mockPredictiveAlerts.find(a => a.id === alertId);
  if (!alert) throw new Error('Alerta nao encontrado');

  const newOrder = await createMaintenanceOrder({
    equipment_id: alert.equipment_id,
    tipo: 'preditiva',
    prioridade: alert.severidade === 'critica' ? 'urgente' : alert.severidade === 'alta' ? 'alta' : 'normal',
    descricao: alert.recomendacao,
    data_agendada: new Date(Date.now() + alert.dias_estimados * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  });

  // Update alert
  const alertIndex = mockPredictiveAlerts.findIndex(a => a.id === alertId);
  mockPredictiveAlerts[alertIndex] = {
    ...mockPredictiveAlerts[alertIndex],
    ordem_criada: true,
    ordem_id: newOrder.id
  };

  return newOrder;
};

// Hook principal
export function useMaintenance(filters?: MaintenanceFilter) {
  const queryClient = useQueryClient();

  // Query para lista de ordens
  const {
    data: orders = [],
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['maintenance-orders', filters],
    queryFn: () => fetchMaintenanceOrders(filters),
    staleTime: 30000
  });

  // Query para estatisticas
  const { data: stats } = useQuery({
    queryKey: ['maintenance-stats'],
    queryFn: fetchMaintenanceStats,
    staleTime: 60000
  });

  // Query para alertas preditivos
  const { data: predictiveAlerts = [] } = useQuery({
    queryKey: ['predictive-alerts'],
    queryFn: fetchPredictiveAlerts,
    staleTime: 60000
  });

  // Query para tecnicos
  const { data: technicians = [] } = useQuery({
    queryKey: ['technicians'],
    queryFn: fetchTechnicians,
    staleTime: 300000
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: createMaintenanceOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance-orders'] });
      queryClient.invalidateQueries({ queryKey: ['maintenance-stats'] });
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateMaintenanceOrderDTO }) =>
      updateMaintenanceOrder(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance-orders'] });
      queryClient.invalidateQueries({ queryKey: ['maintenance-stats'] });
    }
  });

  const startMutation = useMutation({
    mutationFn: startMaintenanceOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance-orders'] });
      queryClient.invalidateQueries({ queryKey: ['maintenance-stats'] });
    }
  });

  const completeMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: { custo_real?: number; tempo_real_horas?: number; observacoes?: string } }) =>
      completeMaintenanceOrder(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance-orders'] });
      queryClient.invalidateQueries({ queryKey: ['maintenance-stats'] });
    }
  });

  const cancelMutation = useMutation({
    mutationFn: ({ id, motivo }: { id: string; motivo: string }) =>
      cancelMaintenanceOrder(id, motivo),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance-orders'] });
      queryClient.invalidateQueries({ queryKey: ['maintenance-stats'] });
    }
  });

  const acknowledgePredictiveMutation = useMutation({
    mutationFn: acknowledgePredictiveAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictive-alerts'] });
    }
  });

  const createFromAlertMutation = useMutation({
    mutationFn: createOrderFromPredictiveAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance-orders'] });
      queryClient.invalidateQueries({ queryKey: ['predictive-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['maintenance-stats'] });
    }
  });

  // Ordens por status
  const ordersByStatus = useMemo(() => {
    const byStatus: Record<MaintenanceStatus, MaintenanceOrder[]> = {
      agendada: [],
      em_execucao: [],
      concluida: [],
      cancelada: [],
      atrasada: []
    };
    orders.forEach(o => {
      byStatus[o.status].push(o);
    });
    return byStatus;
  }, [orders]);

  // Ordens por tipo
  const ordersByType = useMemo(() => {
    const byType: Record<MaintenanceType, MaintenanceOrder[]> = {
      preventiva: [],
      corretiva: [],
      preditiva: []
    };
    orders.forEach(o => {
      byType[o.tipo].push(o);
    });
    return byType;
  }, [orders]);

  // Alertas nao reconhecidos
  const unacknowledgedAlerts = useMemo(() =>
    predictiveAlerts.filter(a => !a.acknowledged),
    [predictiveAlerts]
  );

  return {
    // Data
    orders,
    stats,
    predictiveAlerts,
    unacknowledgedAlerts,
    technicians,
    ordersByStatus,
    ordersByType,

    // Loading states
    isLoading,
    isError,
    error,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,

    // Actions
    refetch,
    create: createMutation.mutateAsync,
    update: updateMutation.mutateAsync,
    start: startMutation.mutateAsync,
    complete: completeMutation.mutateAsync,
    cancel: cancelMutation.mutateAsync,
    acknowledgePredictive: acknowledgePredictiveMutation.mutateAsync,
    createFromAlert: createFromAlertMutation.mutateAsync
  };
}

// Hook para ordem individual
export function useMaintenanceOrder(id: string) {
  const { data: order, isLoading, isError } = useQuery({
    queryKey: ['maintenance-order', id],
    queryFn: () => fetchMaintenanceOrderById(id),
    enabled: !!id
  });

  return {
    order,
    isLoading,
    isError
  };
}

// Hook para calendario
export function useMaintenanceCalendar(startDate: string, endDate: string) {
  const { data: events = [], isLoading } = useQuery({
    queryKey: ['maintenance-calendar', startDate, endDate],
    queryFn: () => fetchCalendarEvents(startDate, endDate),
    enabled: !!startDate && !!endDate
  });

  // Agrupar por data
  const eventsByDate = useMemo(() => {
    const byDate: Record<string, MaintenanceCalendarEvent[]> = {};
    events.forEach(e => {
      if (!byDate[e.date]) byDate[e.date] = [];
      byDate[e.date].push(e);
    });
    return byDate;
  }, [events]);

  return {
    events,
    eventsByDate,
    isLoading
  };
}

export default useMaintenance;
