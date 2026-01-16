import { useState, useEffect, useCallback, useMemo } from 'react';
import type {
  Schedule,
  ScheduleFilters,
  ScheduleStats,
  ScheduleFormData,
  BulkScheduleFormData,
  Conflict,
  ScheduleEvent,
  WeekDay,
  CalendarView,
} from '../types/schedules.types';

// Mock Data
const mockSchedules: Schedule[] = [
  {
    id: 's1',
    posto_id: '1',
    posto_nome: 'Shopping Center Norte',
    profissional_id: 'p1',
    profissional_nome: 'João Silva',
    profissional_avatar: undefined,
    profissional_funcao: 'Vigilante',
    data: '2024-06-28',
    turno_id: 't1',
    turno: 'Turno A - Manhã',
    horario_inicio: '06:00',
    horario_fim: '14:00',
    status: 'em_andamento',
    check_in: {
      timestamp: '2024-06-28T05:58:00Z',
      metodo: 'biometria',
      coordenadas: { lat: -23.5505, lng: -46.6333 },
    },
    created_at: '2024-06-20T10:00:00Z',
    updated_at: '2024-06-28T06:00:00Z',
  },
  {
    id: 's2',
    posto_id: '1',
    posto_nome: 'Shopping Center Norte',
    profissional_id: 'p2',
    profissional_nome: 'Maria Santos',
    profissional_funcao: 'Vigilante',
    data: '2024-06-28',
    turno_id: 't2',
    turno: 'Turno B - Tarde',
    horario_inicio: '14:00',
    horario_fim: '22:00',
    status: 'confirmado',
    created_at: '2024-06-20T10:00:00Z',
    updated_at: '2024-06-20T10:00:00Z',
  },
  {
    id: 's3',
    posto_id: '2',
    posto_nome: 'Condomínio Residencial Aurora',
    profissional_id: 'p3',
    profissional_nome: 'Pedro Oliveira',
    profissional_funcao: 'Porteiro',
    data: '2024-06-28',
    turno_id: 't4',
    turno: 'Escala 12x36 - Diurno',
    horario_inicio: '07:00',
    horario_fim: '19:00',
    status: 'em_andamento',
    check_in: {
      timestamp: '2024-06-28T06:55:00Z',
      metodo: 'app',
      coordenadas: { lat: -23.5912, lng: -46.7192 },
    },
    created_at: '2024-06-18T14:00:00Z',
    updated_at: '2024-06-28T07:00:00Z',
  },
  {
    id: 's4',
    posto_id: '3',
    posto_nome: 'Hospital São Lucas',
    profissional_id: 'p4',
    profissional_nome: 'Ana Costa',
    profissional_funcao: 'Vigilante',
    data: '2024-06-28',
    turno_id: 't6',
    turno: 'Plantão 24h',
    horario_inicio: '07:00',
    horario_fim: '07:00',
    status: 'falta',
    observacoes: 'Profissional não compareceu. Substituição acionada.',
    created_at: '2024-06-15T09:00:00Z',
    updated_at: '2024-06-28T08:00:00Z',
  },
  {
    id: 's5',
    posto_id: '1',
    posto_nome: 'Shopping Center Norte',
    profissional_id: 'p5',
    profissional_nome: 'Carlos Mendes',
    profissional_funcao: 'Vigilante',
    data: '2024-06-28',
    turno_id: 't3',
    turno: 'Turno C - Noite',
    horario_inicio: '22:00',
    horario_fim: '06:00',
    status: 'pendente',
    created_at: '2024-06-20T10:00:00Z',
    updated_at: '2024-06-20T10:00:00Z',
  },
  {
    id: 's6',
    posto_id: '2',
    posto_nome: 'Condomínio Residencial Aurora',
    profissional_id: 'p6',
    profissional_nome: 'Fernanda Lima',
    profissional_funcao: 'Porteira',
    data: '2024-06-29',
    turno_id: 't4',
    turno: 'Escala 12x36 - Diurno',
    horario_inicio: '07:00',
    horario_fim: '19:00',
    status: 'confirmado',
    created_at: '2024-06-18T14:00:00Z',
    updated_at: '2024-06-18T14:00:00Z',
  },
  {
    id: 's7',
    posto_id: '1',
    posto_nome: 'Shopping Center Norte',
    profissional_id: 'p1',
    profissional_nome: 'João Silva',
    profissional_funcao: 'Vigilante',
    data: '2024-06-27',
    turno_id: 't1',
    turno: 'Turno A - Manhã',
    horario_inicio: '06:00',
    horario_fim: '14:00',
    status: 'concluido',
    check_in: {
      timestamp: '2024-06-27T05:55:00Z',
      metodo: 'biometria',
    },
    check_out: {
      timestamp: '2024-06-27T14:02:00Z',
      metodo: 'biometria',
    },
    created_at: '2024-06-20T10:00:00Z',
    updated_at: '2024-06-27T14:05:00Z',
  },
];

const mockConflicts: Conflict[] = [
  {
    id: 'c1',
    tipo: 'sobreposicao',
    severidade: 'alta',
    descricao: 'João Silva está escalado em dois postos no mesmo horário',
    schedules: ['s1', 's8'],
    profissional_id: 'p1',
    profissional_nome: 'João Silva',
    data: '2024-06-30',
    sugestao_resolucao: 'Remover uma das escalas ou alocar outro profissional',
    resolvido: false,
  },
  {
    id: 'c2',
    tipo: 'descanso_minimo',
    severidade: 'media',
    descricao: 'Maria Santos não terá 11h de descanso entre turnos',
    schedules: ['s2', 's9'],
    profissional_id: 'p2',
    profissional_nome: 'Maria Santos',
    data: '2024-06-29',
    sugestao_resolucao: 'Ajustar horário de início do próximo turno',
    resolvido: false,
  },
  {
    id: 'c3',
    tipo: 'limite_horas_semanais',
    severidade: 'baixa',
    descricao: 'Carlos Mendes atingirá 48h semanais',
    schedules: ['s5'],
    profissional_id: 'p5',
    profissional_nome: 'Carlos Mendes',
    data: '2024-06-28',
    sugestao_resolucao: 'Verificar banco de horas ou compensação',
    resolvido: false,
  },
];

export const useSchedules = (filters?: ScheduleFilters) => {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [calendarView, setCalendarView] = useState<CalendarView>({
    type: 'week',
    currentDate: new Date(),
    startDate: new Date(),
    endDate: new Date(),
  });

  const loadSchedules = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      await new Promise((resolve) => setTimeout(resolve, 500));

      let filteredSchedules = [...mockSchedules];

      if (filters?.posto_id) {
        filteredSchedules = filteredSchedules.filter(
          (s) => s.posto_id === filters.posto_id
        );
      }

      if (filters?.profissional_id) {
        filteredSchedules = filteredSchedules.filter(
          (s) => s.profissional_id === filters.profissional_id
        );
      }

      if (filters?.status?.length) {
        filteredSchedules = filteredSchedules.filter((s) =>
          filters.status!.includes(s.status)
        );
      }

      if (filters?.data_inicio) {
        filteredSchedules = filteredSchedules.filter(
          (s) => s.data >= filters.data_inicio!
        );
      }

      if (filters?.data_fim) {
        filteredSchedules = filteredSchedules.filter(
          (s) => s.data <= filters.data_fim!
        );
      }

      setSchedules(filteredSchedules);
      setConflicts(mockConflicts.filter((c) => !c.resolvido));
    } catch (err) {
      setError('Erro ao carregar escalas');
      console.error('Erro ao carregar escalas:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadSchedules();
  }, [loadSchedules]);

  const stats = useMemo<ScheduleStats>(() => {
    const confirmadas = schedules.filter((s) => s.status === 'confirmado');
    const pendentes = schedules.filter((s) => s.status === 'pendente');
    const canceladas = schedules.filter((s) => s.status === 'cancelado');
    const faltas = schedules.filter((s) => s.status === 'falta');
    const substituidas = schedules.filter((s) => s.status === 'substituido');
    const comCheckIn = schedules.filter((s) => s.check_in);
    const pontuais = comCheckIn.filter((s) => {
      if (!s.check_in) return false;
      const checkIn = new Date(s.check_in.timestamp);
      const [hora, minuto] = s.horario_inicio.split(':').map(Number);
      const esperado = new Date(checkIn);
      esperado.setHours(hora, minuto, 0, 0);
      return checkIn <= esperado;
    });

    return {
      total_escalas: schedules.length,
      escalas_confirmadas: confirmadas.length,
      escalas_pendentes: pendentes.length,
      escalas_canceladas: canceladas.length,
      faltas: faltas.length,
      substituicoes: substituidas.length,
      conflitos_ativos: conflicts.length,
      taxa_pontualidade:
        comCheckIn.length > 0 ? (pontuais.length / comCheckIn.length) * 100 : 0,
      horas_programadas: schedules.length * 8, // Simplificado
      horas_trabalhadas: schedules.filter(
        (s) => s.status === 'concluido' || s.status === 'em_andamento'
      ).length * 8,
    };
  }, [schedules, conflicts]);

  const events = useMemo<ScheduleEvent[]>(() => {
    return schedules.map((schedule) => {
      const [startHour, startMin] = schedule.horario_inicio.split(':').map(Number);
      const [endHour, endMin] = schedule.horario_fim.split(':').map(Number);

      const start = new Date(schedule.data);
      start.setHours(startHour, startMin, 0, 0);

      const end = new Date(schedule.data);
      end.setHours(endHour, endMin, 0, 0);

      // Se fim é menor que início, é turno que passa da meia-noite
      if (endHour < startHour) {
        end.setDate(end.getDate() + 1);
      }

      const statusColors: Record<string, string> = {
        confirmado: '#22c55e',
        pendente: '#f59e0b',
        cancelado: '#ef4444',
        em_andamento: '#3b82f6',
        concluido: '#6b7280',
        falta: '#dc2626',
        substituido: '#8b5cf6',
      };

      return {
        id: schedule.id,
        title: `${schedule.profissional_nome} - ${schedule.turno}`,
        start,
        end,
        resourceId: schedule.posto_id,
        profissional_id: schedule.profissional_id,
        profissional_nome: schedule.profissional_nome,
        posto_id: schedule.posto_id,
        posto_nome: schedule.posto_nome,
        status: schedule.status,
        color: statusColors[schedule.status] || '#6b7280',
        extendedProps: {
          turno: schedule.turno,
          funcao: schedule.profissional_funcao,
        },
      };
    });
  }, [schedules]);

  const getWeekDays = useCallback((startDate: Date): WeekDay[] => {
    const days: WeekDay[] = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const dayNames = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

    for (let i = 0; i < 7; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      date.setHours(0, 0, 0, 0);

      const dateStr = date.toISOString().split('T')[0];
      const daySchedules = schedules.filter((s) => s.data === dateStr);

      days.push({
        date,
        dayName: dayNames[date.getDay()],
        dayNumber: date.getDate(),
        isToday: date.getTime() === today.getTime(),
        isWeekend: date.getDay() === 0 || date.getDay() === 6,
        schedules: daySchedules,
      });
    }

    return days;
  }, [schedules]);

  const createSchedule = async (data: ScheduleFormData): Promise<Schedule> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      const novaEscala: Schedule = {
        id: `s${Date.now()}`,
        posto_id: data.posto_id,
        posto_nome: 'Posto', // Seria buscado
        profissional_id: data.profissional_id,
        profissional_nome: 'Profissional', // Seria buscado
        profissional_funcao: 'Vigilante',
        data: data.data,
        turno_id: data.turno_id,
        turno: 'Turno', // Seria buscado
        horario_inicio: '08:00',
        horario_fim: '16:00',
        status: 'pendente',
        observacoes: data.observacoes,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setSchedules((prev) => [...prev, novaEscala]);
      return novaEscala;
    } catch (err) {
      console.error('Erro ao criar escala:', err);
      throw err;
    }
  };

  const createBulkSchedules = async (
    data: BulkScheduleFormData
  ): Promise<Schedule[]> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));

      const novasEscalas: Schedule[] = [];
      const startDate = new Date(data.data_inicio);
      const endDate = new Date(data.data_fim);

      for (let d = startDate; d <= endDate; d.setDate(d.getDate() + 1)) {
        if (data.dias_semana.includes(d.getDay())) {
          for (const profissionalId of data.profissionais) {
            const escala: Schedule = {
              id: `s${Date.now()}-${Math.random()}`,
              posto_id: data.posto_id,
              posto_nome: 'Posto',
              profissional_id: profissionalId,
              profissional_nome: 'Profissional',
              profissional_funcao: 'Vigilante',
              data: d.toISOString().split('T')[0],
              turno_id: data.turno_id,
              turno: 'Turno',
              horario_inicio: '08:00',
              horario_fim: '16:00',
              status: 'pendente',
              observacoes: data.observacoes,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            };
            novasEscalas.push(escala);
          }
        }
      }

      setSchedules((prev) => [...prev, ...novasEscalas]);
      return novasEscalas;
    } catch (err) {
      console.error('Erro ao criar escalas em lote:', err);
      throw err;
    }
  };

  const updateSchedule = async (
    id: string,
    data: Partial<ScheduleFormData>
  ): Promise<Schedule> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      let updatedSchedule: Schedule | undefined;

      setSchedules((prev) =>
        prev.map((schedule) => {
          if (schedule.id === id) {
            updatedSchedule = {
              ...schedule,
              ...data,
              updated_at: new Date().toISOString(),
            };
            return updatedSchedule;
          }
          return schedule;
        })
      );

      if (!updatedSchedule) {
        throw new Error('Escala não encontrada');
      }

      return updatedSchedule;
    } catch (err) {
      console.error('Erro ao atualizar escala:', err);
      throw err;
    }
  };

  const deleteSchedule = async (id: string): Promise<void> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));
      setSchedules((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      console.error('Erro ao deletar escala:', err);
      throw err;
    }
  };

  const confirmSchedule = async (id: string): Promise<Schedule> => {
    return updateSchedule(id, { status: 'confirmado' } as Partial<Schedule>);
  };

  const cancelSchedule = async (id: string): Promise<Schedule> => {
    return updateSchedule(id, { status: 'cancelado' } as Partial<Schedule>);
  };

  const resolveConflict = async (conflictId: string): Promise<void> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));
      setConflicts((prev) =>
        prev.map((c) =>
          c.id === conflictId
            ? { ...c, resolvido: true, resolvido_em: new Date().toISOString() }
            : c
        )
      );
    } catch (err) {
      console.error('Erro ao resolver conflito:', err);
      throw err;
    }
  };

  const getScheduleById = useCallback(
    (id: string): Schedule | undefined => {
      return schedules.find((s) => s.id === id);
    },
    [schedules]
  );

  return {
    schedules,
    conflicts,
    loading,
    error,
    stats,
    events,
    calendarView,
    setCalendarView,
    getWeekDays,
    loadSchedules,
    createSchedule,
    createBulkSchedules,
    updateSchedule,
    deleteSchedule,
    confirmSchedule,
    cancelSchedule,
    resolveConflict,
    getScheduleById,
  };
};

export default useSchedules;
