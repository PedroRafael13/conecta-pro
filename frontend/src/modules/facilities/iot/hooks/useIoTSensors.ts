// Hook para IoT Sensors - Facilities Module
// Conecta PRO

import { useState, useMemo, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type {
  Sensor,
  SensorReading,
  SensorReadingAggregated,
  Alert,
  SensorThreshold,
  SensorFilter,
  SensorStats,
  SensorType,
  SensorStatus
} from '../types/iot.types';

// Mock data para desenvolvimento
const mockSensors: Sensor[] = [
  {
    id: 'SENS-001',
    nome: 'Sala de Servidores - Temperatura',
    tipo: 'temperatura',
    localizacao: 'Bloco A - 2o Andar - Sala TI',
    status: 'online',
    valor_atual: 18.5,
    unidade: 'C',
    limite_min: 16,
    limite_max: 24,
    ultima_leitura: new Date().toISOString(),
    bateria_nivel: 95,
    firmware_versao: '2.1.4',
    modelo: 'TempSense Pro',
    fabricante: 'IoTech',
    intervalo_leitura: 60
  },
  {
    id: 'SENS-002',
    nome: 'Sala de Servidores - Umidade',
    tipo: 'umidade',
    localizacao: 'Bloco A - 2o Andar - Sala TI',
    status: 'alerta',
    valor_atual: 68,
    unidade: '%',
    limite_min: 40,
    limite_max: 60,
    ultima_leitura: new Date().toISOString(),
    bateria_nivel: 87,
    firmware_versao: '2.1.4',
    modelo: 'HumSense Pro',
    fabricante: 'IoTech',
    intervalo_leitura: 60
  },
  {
    id: 'SENS-003',
    nome: 'Medidor Principal - Energia',
    tipo: 'energia',
    localizacao: 'Subsolo - Subestacao',
    status: 'online',
    valor_atual: 125.6,
    unidade: 'kW',
    limite_min: 0,
    limite_max: 200,
    ultima_leitura: new Date().toISOString(),
    bateria_nivel: undefined,
    firmware_versao: '3.0.1',
    modelo: 'PowerMeter X500',
    fabricante: 'EnergyTech',
    intervalo_leitura: 15
  },
  {
    id: 'SENS-004',
    nome: 'Hall Principal - Movimento',
    tipo: 'movimento',
    localizacao: 'Bloco A - Terreo - Hall',
    status: 'online',
    valor_atual: 12,
    unidade: 'pessoas',
    limite_min: 0,
    limite_max: 100,
    ultima_leitura: new Date().toISOString(),
    bateria_nivel: 72,
    firmware_versao: '1.8.2',
    modelo: 'MotionTrack 200',
    fabricante: 'SecureTech',
    intervalo_leitura: 30
  },
  {
    id: 'SENS-005',
    nome: 'Cisterna - Pressao',
    tipo: 'pressao',
    localizacao: 'Subsolo - Casa de Bombas',
    status: 'offline',
    valor_atual: 0,
    unidade: 'bar',
    limite_min: 2,
    limite_max: 6,
    ultima_leitura: new Date(Date.now() - 3600000).toISOString(),
    bateria_nivel: 15,
    firmware_versao: '1.5.0',
    modelo: 'PressureSense 100',
    fabricante: 'HydroTech',
    intervalo_leitura: 60
  },
  {
    id: 'SENS-006',
    nome: 'Escritorio Central - CO2',
    tipo: 'co2',
    localizacao: 'Bloco B - 3o Andar - Escritorio',
    status: 'online',
    valor_atual: 650,
    unidade: 'ppm',
    limite_min: 400,
    limite_max: 1000,
    ultima_leitura: new Date().toISOString(),
    bateria_nivel: 88,
    firmware_versao: '2.0.3',
    modelo: 'AirQuality Pro',
    fabricante: 'EnviroTech',
    intervalo_leitura: 120
  }
];

const mockAlerts: Alert[] = [
  {
    id: 'ALT-001',
    sensor_id: 'SENS-002',
    sensor_nome: 'Sala de Servidores - Umidade',
    tipo: 'limite_excedido',
    mensagem: 'Umidade acima do limite maximo (68% > 60%)',
    severidade: 'alta',
    valor_detectado: 68,
    limite_violado: 60,
    created_at: new Date(Date.now() - 1800000).toISOString(),
    acknowledged: false,
    resolved: false
  },
  {
    id: 'ALT-002',
    sensor_id: 'SENS-005',
    sensor_nome: 'Cisterna - Pressao',
    tipo: 'offline',
    mensagem: 'Sensor offline ha mais de 1 hora',
    severidade: 'critica',
    created_at: new Date(Date.now() - 3600000).toISOString(),
    acknowledged: false,
    resolved: false
  },
  {
    id: 'ALT-003',
    sensor_id: 'SENS-005',
    sensor_nome: 'Cisterna - Pressao',
    tipo: 'bateria_baixa',
    mensagem: 'Nivel de bateria critico (15%)',
    severidade: 'media',
    created_at: new Date(Date.now() - 7200000).toISOString(),
    acknowledged: true,
    acknowledged_at: new Date(Date.now() - 6000000).toISOString(),
    acknowledged_by: 'admin@conectapro.com.br',
    resolved: false
  }
];

// Gerar readings historicos
const generateReadings = (sensorId: string, hours: number = 24): SensorReading[] => {
  const readings: SensorReading[] = [];
  const now = Date.now();
  const sensor = mockSensors.find(s => s.id === sensorId);
  if (!sensor) return [];

  for (let i = hours * 60; i >= 0; i -= 5) {
    const timestamp = new Date(now - i * 60000);
    const baseValue = sensor.valor_atual;
    const variation = (Math.random() - 0.5) * 10;

    readings.push({
      sensor_id: sensorId,
      timestamp: timestamp.toISOString(),
      valor: Number((baseValue + variation).toFixed(2))
    });
  }

  return readings;
};

// API mock functions
const fetchSensors = async (filters?: SensorFilter): Promise<Sensor[]> => {
  await new Promise(resolve => setTimeout(resolve, 400));

  let result = [...mockSensors];

  if (filters?.search) {
    const search = filters.search.toLowerCase();
    result = result.filter(s =>
      s.nome.toLowerCase().includes(search) ||
      s.localizacao.toLowerCase().includes(search)
    );
  }

  if (filters?.tipo?.length) {
    result = result.filter(s => filters.tipo!.includes(s.tipo));
  }

  if (filters?.status?.length) {
    result = result.filter(s => filters.status!.includes(s.status));
  }

  if (filters?.com_alerta) {
    result = result.filter(s => s.status === 'alerta');
  }

  if (filters?.bateria_baixa) {
    result = result.filter(s => s.bateria_nivel !== undefined && s.bateria_nivel < 20);
  }

  return result;
};

const fetchSensorById = async (id: string): Promise<Sensor | null> => {
  await new Promise(resolve => setTimeout(resolve, 200));
  return mockSensors.find(s => s.id === id) || null;
};

const fetchSensorStats = async (): Promise<SensorStats> => {
  await new Promise(resolve => setTimeout(resolve, 200));

  return {
    total: mockSensors.length,
    online: mockSensors.filter(s => s.status === 'online').length,
    offline: mockSensors.filter(s => s.status === 'offline').length,
    em_alerta: mockSensors.filter(s => s.status === 'alerta').length,
    alertas_ativos: mockAlerts.filter(a => !a.resolved).length,
    alertas_criticos: mockAlerts.filter(a => !a.resolved && a.severidade === 'critica').length,
    leituras_24h: mockSensors.length * 288
  };
};

const fetchAlerts = async (onlyActive: boolean = true): Promise<Alert[]> => {
  await new Promise(resolve => setTimeout(resolve, 300));

  if (onlyActive) {
    return mockAlerts.filter(a => !a.resolved);
  }
  return [...mockAlerts];
};

const fetchSensorReadings = async (
  sensorId: string,
  hours: number = 24
): Promise<SensorReading[]> => {
  await new Promise(resolve => setTimeout(resolve, 400));
  return generateReadings(sensorId, hours);
};

const fetchSensorReadingsAggregated = async (
  sensorId: string,
  periodo: 'hora' | 'dia' | 'semana' = 'hora',
  quantidade: number = 24
): Promise<SensorReadingAggregated[]> => {
  await new Promise(resolve => setTimeout(resolve, 400));

  const readings = generateReadings(sensorId, quantidade);
  const aggregated: SensorReadingAggregated[] = [];
  const chunkSize = periodo === 'hora' ? 12 : periodo === 'dia' ? 288 : 2016;

  for (let i = 0; i < readings.length; i += chunkSize) {
    const chunk = readings.slice(i, i + chunkSize);
    if (chunk.length === 0) continue;

    const valores = chunk.map(r => r.valor);
    aggregated.push({
      periodo: chunk[0].timestamp,
      media: Number((valores.reduce((a, b) => a + b, 0) / valores.length).toFixed(2)),
      minimo: Math.min(...valores),
      maximo: Math.max(...valores),
      contagem: valores.length
    });
  }

  return aggregated;
};

// Mutations
const acknowledgeAlert = async (alertId: string): Promise<Alert> => {
  await new Promise(resolve => setTimeout(resolve, 300));

  const index = mockAlerts.findIndex(a => a.id === alertId);
  if (index === -1) throw new Error('Alerta nao encontrado');

  mockAlerts[index] = {
    ...mockAlerts[index],
    acknowledged: true,
    acknowledged_at: new Date().toISOString(),
    acknowledged_by: 'admin@conectapro.com.br'
  };

  return mockAlerts[index];
};

const resolveAlert = async (alertId: string): Promise<Alert> => {
  await new Promise(resolve => setTimeout(resolve, 300));

  const index = mockAlerts.findIndex(a => a.id === alertId);
  if (index === -1) throw new Error('Alerta nao encontrado');

  mockAlerts[index] = {
    ...mockAlerts[index],
    resolved: true,
    resolved_at: new Date().toISOString()
  };

  // Update sensor status if needed
  const sensor = mockSensors.find(s => s.id === mockAlerts[index].sensor_id);
  if (sensor && sensor.status === 'alerta') {
    sensor.status = 'online';
  }

  return mockAlerts[index];
};

const updateSensorThreshold = async (threshold: SensorThreshold): Promise<Sensor> => {
  await new Promise(resolve => setTimeout(resolve, 300));

  const index = mockSensors.findIndex(s => s.id === threshold.sensor_id);
  if (index === -1) throw new Error('Sensor nao encontrado');

  mockSensors[index] = {
    ...mockSensors[index],
    limite_min: threshold.limite_min,
    limite_max: threshold.limite_max
  };

  return mockSensors[index];
};

// Hook principal
export function useIoTSensors(filters?: SensorFilter) {
  const queryClient = useQueryClient();

  // Query para lista de sensores
  const {
    data: sensors = [],
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['sensors', filters],
    queryFn: () => fetchSensors(filters),
    staleTime: 10000,
    refetchInterval: 30000 // Atualiza a cada 30s
  });

  // Query para estatisticas
  const { data: stats } = useQuery({
    queryKey: ['sensor-stats'],
    queryFn: fetchSensorStats,
    staleTime: 10000,
    refetchInterval: 30000
  });

  // Query para alertas ativos
  const { data: alerts = [] } = useQuery({
    queryKey: ['sensor-alerts', true],
    queryFn: () => fetchAlerts(true),
    staleTime: 5000,
    refetchInterval: 15000 // Alertas atualizam mais rapido
  });

  // Mutations
  const acknowledgeMutation = useMutation({
    mutationFn: acknowledgeAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sensor-alerts'] });
    }
  });

  const resolveMutation = useMutation({
    mutationFn: resolveAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sensors'] });
      queryClient.invalidateQueries({ queryKey: ['sensor-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['sensor-stats'] });
    }
  });

  const thresholdMutation = useMutation({
    mutationFn: updateSensorThreshold,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sensors'] });
    }
  });

  // Sensores por tipo
  const sensorsByType = useMemo(() => {
    const byType: Record<SensorType, Sensor[]> = {
      temperatura: [],
      umidade: [],
      pressao: [],
      movimento: [],
      energia: [],
      luminosidade: [],
      co2: [],
      ruido: []
    };
    sensors.forEach(s => {
      if (byType[s.tipo]) byType[s.tipo].push(s);
    });
    return byType;
  }, [sensors]);

  // Sensores por status
  const sensorsByStatus = useMemo(() => {
    const byStatus: Record<SensorStatus, Sensor[]> = {
      online: [],
      offline: [],
      alerta: []
    };
    sensors.forEach(s => {
      byStatus[s.status].push(s);
    });
    return byStatus;
  }, [sensors]);

  // Alertas criticos
  const criticalAlerts = useMemo(() =>
    alerts.filter(a => a.severidade === 'critica'),
    [alerts]
  );

  return {
    // Data
    sensors,
    stats,
    alerts,
    criticalAlerts,
    sensorsByType,
    sensorsByStatus,

    // Loading states
    isLoading,
    isError,
    error,

    // Actions
    refetch,
    acknowledgeAlert: acknowledgeMutation.mutateAsync,
    resolveAlert: resolveMutation.mutateAsync,
    updateThreshold: thresholdMutation.mutateAsync
  };
}

// Hook para sensor individual com readings
export function useSensorDetails(sensorId: string) {
  const { data: sensor, isLoading: loadingSensor } = useQuery({
    queryKey: ['sensor', sensorId],
    queryFn: () => fetchSensorById(sensorId),
    enabled: !!sensorId,
    staleTime: 10000,
    refetchInterval: 30000
  });

  const { data: readings = [], isLoading: loadingReadings } = useQuery({
    queryKey: ['sensor-readings', sensorId],
    queryFn: () => fetchSensorReadings(sensorId, 24),
    enabled: !!sensorId,
    staleTime: 60000
  });

  return {
    sensor,
    readings,
    isLoading: loadingSensor || loadingReadings
  };
}

// Hook para grafico de readings
export function useSensorChart(
  sensorId: string,
  periodo: 'hora' | 'dia' | 'semana' = 'hora',
  quantidade: number = 24
) {
  const { data: readings = [], isLoading } = useQuery({
    queryKey: ['sensor-readings-aggregated', sensorId, periodo, quantidade],
    queryFn: () => fetchSensorReadingsAggregated(sensorId, periodo, quantidade),
    enabled: !!sensorId,
    staleTime: 60000
  });

  const chartData = useMemo(() => {
    return readings.map(r => ({
      time: new Date(r.periodo).toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
      }),
      valor: r.media,
      min: r.minimo,
      max: r.maximo
    }));
  }, [readings]);

  return {
    readings,
    chartData,
    isLoading
  };
}

// Hook para simular real-time updates
export function useRealtimeSensor(sensorId: string, intervalMs: number = 5000) {
  const [currentValue, setCurrentValue] = useState<number | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    const sensor = mockSensors.find(s => s.id === sensorId);
    if (!sensor) return;

    const updateValue = () => {
      const variation = (Math.random() - 0.5) * 2;
      const newValue = sensor.valor_atual + variation;
      setCurrentValue(Number(newValue.toFixed(2)));
      setLastUpdate(new Date());
    };

    updateValue();
    const interval = setInterval(updateValue, intervalMs);

    return () => clearInterval(interval);
  }, [sensorId, intervalMs]);

  return {
    currentValue,
    lastUpdate
  };
}

export default useIoTSensors;
