// Hook para Equipment - Facilities Module
// Conecta PRO

import { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type {
  Equipment,
  EquipmentFilter,
  EquipmentStats,
  EquipmentLifecycleEvent,
  CreateEquipmentDTO,
  UpdateEquipmentDTO,
  EquipmentStatus
} from '../types/equipment.types';

// Mock data para desenvolvimento
const mockEquipments: Equipment[] = [
  {
    id: '1',
    codigo: 'EQP-001',
    nome: 'Ar Condicionado Split 36.000 BTUs',
    tipo: 'HVAC',
    fabricante: 'Carrier',
    modelo: 'XPower Inverter',
    numero_serie: 'CAR-2024-001234',
    rfid_tag: 'RFID-AC-001',
    qr_code: 'QR-EQP-001',
    localizacao: 'Bloco A - Sala de Servidores',
    status: 'operacional',
    data_aquisicao: '2023-06-15',
    garantia_ate: '2026-06-15',
    ultima_manutencao: '2024-01-10',
    proxima_manutencao: '2024-04-10',
    valor_aquisicao: 8500,
    vida_util_anos: 10,
    depreciacao_anual: 850,
    created_at: '2023-06-15T10:00:00Z',
    updated_at: '2024-01-10T14:30:00Z'
  },
  {
    id: '2',
    codigo: 'EQP-002',
    nome: 'Gerador Diesel 150 kVA',
    tipo: 'Energia',
    fabricante: 'Cummins',
    modelo: 'C150D5',
    numero_serie: 'CUM-2022-005678',
    rfid_tag: 'RFID-GEN-001',
    qr_code: 'QR-EQP-002',
    localizacao: 'Subsolo - Casa de Maquinas',
    status: 'manutencao',
    data_aquisicao: '2022-03-20',
    garantia_ate: '2025-03-20',
    ultima_manutencao: '2024-01-12',
    proxima_manutencao: '2024-01-15',
    valor_aquisicao: 125000,
    vida_util_anos: 15,
    depreciacao_anual: 8333.33,
    created_at: '2022-03-20T09:00:00Z',
    updated_at: '2024-01-12T08:00:00Z'
  },
  {
    id: '3',
    codigo: 'EQP-003',
    nome: 'Elevador Social 01',
    tipo: 'Transporte Vertical',
    fabricante: 'ThyssenKrupp',
    modelo: 'Synergy 300',
    numero_serie: 'TK-2020-112233',
    rfid_tag: 'RFID-ELV-001',
    qr_code: 'QR-EQP-003',
    localizacao: 'Torre A - Hall Principal',
    status: 'operacional',
    data_aquisicao: '2020-01-10',
    garantia_ate: '2025-01-10',
    ultima_manutencao: '2024-01-05',
    proxima_manutencao: '2024-02-05',
    valor_aquisicao: 280000,
    vida_util_anos: 20,
    depreciacao_anual: 14000,
    created_at: '2020-01-10T12:00:00Z',
    updated_at: '2024-01-05T16:00:00Z'
  },
  {
    id: '4',
    codigo: 'EQP-004',
    nome: 'Bomba Pressurizadora 3CV',
    tipo: 'Hidraulica',
    fabricante: 'Schneider',
    modelo: 'BPR-3000',
    numero_serie: 'SCH-2021-445566',
    rfid_tag: 'RFID-BMB-001',
    qr_code: 'QR-EQP-004',
    localizacao: 'Subsolo - Cisterna',
    status: 'operacional',
    data_aquisicao: '2021-08-25',
    garantia_ate: '2024-08-25',
    ultima_manutencao: '2023-12-15',
    proxima_manutencao: '2024-03-15',
    valor_aquisicao: 4500,
    vida_util_anos: 8,
    depreciacao_anual: 562.5,
    created_at: '2021-08-25T11:00:00Z',
    updated_at: '2023-12-15T10:00:00Z'
  },
  {
    id: '5',
    codigo: 'EQP-005',
    nome: 'Portao Automatico Garagem',
    tipo: 'Acesso',
    fabricante: 'PPA',
    modelo: 'Piston Jet Flex',
    numero_serie: 'PPA-2023-778899',
    rfid_tag: 'RFID-PTG-001',
    qr_code: 'QR-EQP-005',
    localizacao: 'Subsolo - Entrada Garagem',
    status: 'inativo',
    data_aquisicao: '2023-02-10',
    garantia_ate: '2025-02-10',
    ultima_manutencao: '2024-01-08',
    proxima_manutencao: undefined,
    valor_aquisicao: 12000,
    vida_util_anos: 10,
    depreciacao_anual: 1200,
    observacoes: 'Aguardando peca de reposicao',
    created_at: '2023-02-10T14:00:00Z',
    updated_at: '2024-01-08T09:00:00Z'
  }
];

const mockLifecycleEvents: EquipmentLifecycleEvent[] = [
  {
    id: 'evt-001',
    equipment_id: '1',
    tipo: 'aquisicao',
    data: '2023-06-15',
    descricao: 'Aquisicao do equipamento via licitacao',
    responsavel: 'Carlos Gestor',
    custo: 8500
  },
  {
    id: 'evt-002',
    equipment_id: '1',
    tipo: 'manutencao',
    data: '2023-12-10',
    descricao: 'Manutencao preventiva - Limpeza de filtros',
    responsavel: 'Joao Tecnico',
    custo: 350
  },
  {
    id: 'evt-003',
    equipment_id: '1',
    tipo: 'manutencao',
    data: '2024-01-10',
    descricao: 'Manutencao preventiva - Verificacao geral',
    responsavel: 'Maria Tecnica',
    custo: 280
  }
];

// API mock functions
const fetchEquipments = async (filters?: EquipmentFilter): Promise<Equipment[]> => {
  await new Promise(resolve => setTimeout(resolve, 500));

  let result = [...mockEquipments];

  if (filters?.search) {
    const search = filters.search.toLowerCase();
    result = result.filter(e =>
      e.nome.toLowerCase().includes(search) ||
      e.codigo.toLowerCase().includes(search) ||
      e.fabricante.toLowerCase().includes(search)
    );
  }

  if (filters?.status?.length) {
    result = result.filter(e => filters.status!.includes(e.status));
  }

  if (filters?.tipo?.length) {
    result = result.filter(e => filters.tipo!.includes(e.tipo));
  }

  if (filters?.localizacao?.length) {
    result = result.filter(e =>
      filters.localizacao!.some(loc => e.localizacao.includes(loc))
    );
  }

  return result;
};

const fetchEquipmentById = async (id: string): Promise<Equipment | null> => {
  await new Promise(resolve => setTimeout(resolve, 300));
  return mockEquipments.find(e => e.id === id) || null;
};

const fetchEquipmentByQRCode = async (qrCode: string): Promise<Equipment | null> => {
  await new Promise(resolve => setTimeout(resolve, 300));
  return mockEquipments.find(e => e.qr_code === qrCode) || null;
};

const fetchEquipmentByRFID = async (rfidTag: string): Promise<Equipment | null> => {
  await new Promise(resolve => setTimeout(resolve, 300));
  return mockEquipments.find(e => e.rfid_tag === rfidTag) || null;
};

const fetchEquipmentStats = async (): Promise<EquipmentStats> => {
  await new Promise(resolve => setTimeout(resolve, 300));

  const today = new Date();
  const thirtyDaysFromNow = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);

  return {
    total: mockEquipments.length,
    operacionais: mockEquipments.filter(e => e.status === 'operacional').length,
    em_manutencao: mockEquipments.filter(e => e.status === 'manutencao').length,
    inativos: mockEquipments.filter(e => e.status === 'inativo').length,
    descartados: mockEquipments.filter(e => e.status === 'descartado').length,
    garantia_vencendo: mockEquipments.filter(e => {
      if (!e.garantia_ate) return false;
      const garantiaDate = new Date(e.garantia_ate);
      return garantiaDate <= thirtyDaysFromNow && garantiaDate >= today;
    }).length,
    manutencao_proxima: mockEquipments.filter(e => {
      if (!e.proxima_manutencao) return false;
      const manutDate = new Date(e.proxima_manutencao);
      return manutDate <= thirtyDaysFromNow;
    }).length,
    valor_total: mockEquipments.reduce((acc, e) => acc + (e.valor_aquisicao || 0), 0)
  };
};

const fetchEquipmentLifecycle = async (equipmentId: string): Promise<EquipmentLifecycleEvent[]> => {
  await new Promise(resolve => setTimeout(resolve, 300));
  return mockLifecycleEvents.filter(e => e.equipment_id === equipmentId);
};

// Mutation functions
const createEquipment = async (data: CreateEquipmentDTO): Promise<Equipment> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  const newEquipment: Equipment = {
    id: `${mockEquipments.length + 1}`,
    ...data,
    qr_code: `QR-EQP-${String(mockEquipments.length + 1).padStart(3, '0')}`,
    status: 'operacional',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };
  mockEquipments.push(newEquipment);
  return newEquipment;
};

const updateEquipment = async (id: string, data: UpdateEquipmentDTO): Promise<Equipment> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  const index = mockEquipments.findIndex(e => e.id === id);
  if (index === -1) throw new Error('Equipamento nao encontrado');

  mockEquipments[index] = {
    ...mockEquipments[index],
    ...data,
    updated_at: new Date().toISOString()
  };
  return mockEquipments[index];
};

const deleteEquipment = async (id: string): Promise<void> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  const index = mockEquipments.findIndex(e => e.id === id);
  if (index === -1) throw new Error('Equipamento nao encontrado');
  mockEquipments.splice(index, 1);
};

// Hook principal
export function useEquipment(filters?: EquipmentFilter) {
  const queryClient = useQueryClient();

  // Query para lista de equipamentos
  const {
    data: equipments = [],
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['equipments', filters],
    queryFn: () => fetchEquipments(filters),
    staleTime: 30000
  });

  // Query para estatisticas
  const { data: stats } = useQuery({
    queryKey: ['equipment-stats'],
    queryFn: fetchEquipmentStats,
    staleTime: 60000
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: createEquipment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipments'] });
      queryClient.invalidateQueries({ queryKey: ['equipment-stats'] });
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateEquipmentDTO }) =>
      updateEquipment(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipments'] });
      queryClient.invalidateQueries({ queryKey: ['equipment-stats'] });
    }
  });

  const deleteMutation = useMutation({
    mutationFn: deleteEquipment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipments'] });
      queryClient.invalidateQueries({ queryKey: ['equipment-stats'] });
    }
  });

  // Estatisticas derivadas
  const statusCounts = useMemo(() => {
    const counts: Record<EquipmentStatus, number> = {
      operacional: 0,
      manutencao: 0,
      inativo: 0,
      descartado: 0
    };
    equipments.forEach(e => {
      counts[e.status]++;
    });
    return counts;
  }, [equipments]);

  // Equipamentos por tipo
  const equipmentsByType = useMemo(() => {
    const byType: Record<string, Equipment[]> = {};
    equipments.forEach(e => {
      if (!byType[e.tipo]) byType[e.tipo] = [];
      byType[e.tipo].push(e);
    });
    return byType;
  }, [equipments]);

  return {
    // Data
    equipments,
    stats,
    statusCounts,
    equipmentsByType,

    // Loading states
    isLoading,
    isError,
    error,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,

    // Actions
    refetch,
    create: createMutation.mutateAsync,
    update: updateMutation.mutateAsync,
    delete: deleteMutation.mutateAsync
  };
}

// Hook para equipamento individual
export function useEquipmentDetails(id: string) {
  const { data: equipment, isLoading, isError } = useQuery({
    queryKey: ['equipment', id],
    queryFn: () => fetchEquipmentById(id),
    enabled: !!id
  });

  const { data: lifecycle = [] } = useQuery({
    queryKey: ['equipment-lifecycle', id],
    queryFn: () => fetchEquipmentLifecycle(id),
    enabled: !!id
  });

  return {
    equipment,
    lifecycle,
    isLoading,
    isError
  };
}

// Hook para busca por QR Code
export function useEquipmentByQRCode() {
  const [qrCode, setQRCode] = useState<string | null>(null);

  const { data: equipment, isLoading, isError } = useQuery({
    queryKey: ['equipment-qr', qrCode],
    queryFn: () => fetchEquipmentByQRCode(qrCode!),
    enabled: !!qrCode
  });

  const scanQRCode = useCallback((code: string) => {
    setQRCode(code);
  }, []);

  const clearScan = useCallback(() => {
    setQRCode(null);
  }, []);

  return {
    equipment,
    isLoading,
    isError,
    scanQRCode,
    clearScan,
    scannedCode: qrCode
  };
}

// Hook para busca por RFID
export function useEquipmentByRFID() {
  const [rfidTag, setRFIDTag] = useState<string | null>(null);

  const { data: equipment, isLoading, isError } = useQuery({
    queryKey: ['equipment-rfid', rfidTag],
    queryFn: () => fetchEquipmentByRFID(rfidTag!),
    enabled: !!rfidTag
  });

  const scanRFID = useCallback((tag: string) => {
    setRFIDTag(tag);
  }, []);

  const clearScan = useCallback(() => {
    setRFIDTag(null);
  }, []);

  return {
    equipment,
    isLoading,
    isError,
    scanRFID,
    clearScan,
    scannedTag: rfidTag
  };
}

export default useEquipment;
