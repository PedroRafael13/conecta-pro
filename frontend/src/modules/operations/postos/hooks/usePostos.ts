import { useState, useEffect, useCallback, useMemo } from 'react';
import type {
  Posto,
  PostoFilters,
  PostoStats,
  PostoFormData,
  Turno,
  TurnoFormData,
} from '../types/postos.types';

// Mock Data
const mockPostos: Posto[] = [
  {
    id: '1',
    nome: 'Shopping Center Norte',
    endereco: 'Av. Paulista, 1000 - Bela Vista, São Paulo/SP',
    cliente: 'Grupo Center Norte',
    cliente_id: 'c1',
    status: 'ativo',
    coordenadas: { lat: -23.5505, lng: -46.6333 },
    contato_responsavel: {
      nome: 'Carlos Silva',
      telefone: '(11) 99999-0001',
      email: 'carlos.silva@centernorte.com.br',
      cargo: 'Gerente de Segurança',
    },
    turnos: [
      {
        id: 't1',
        nome: 'Turno A - Manhã',
        horario_inicio: '06:00',
        horario_fim: '14:00',
        dias_semana: [1, 2, 3, 4, 5],
        profissionais_alocados: 4,
        profissionais_necessarios: 5,
        tipo: 'diurno',
        adicional_noturno: false,
        intervalo_minutos: 60,
      },
      {
        id: 't2',
        nome: 'Turno B - Tarde',
        horario_inicio: '14:00',
        horario_fim: '22:00',
        dias_semana: [1, 2, 3, 4, 5],
        profissionais_alocados: 5,
        profissionais_necessarios: 5,
        tipo: 'diurno',
        adicional_noturno: false,
        intervalo_minutos: 60,
      },
      {
        id: 't3',
        nome: 'Turno C - Noite',
        horario_inicio: '22:00',
        horario_fim: '06:00',
        dias_semana: [0, 1, 2, 3, 4, 5, 6],
        profissionais_alocados: 3,
        profissionais_necessarios: 3,
        tipo: 'noturno',
        adicional_noturno: true,
        intervalo_minutos: 60,
      },
    ],
    requisitos: [
      { id: 'r1', descricao: 'Curso de Vigilante', obrigatorio: true, tipo: 'certificacao' },
      { id: 'r2', descricao: 'CNV Atualizada', obrigatorio: true, tipo: 'certificacao' },
    ],
    equipamentos: [
      { id: 'e1', nome: 'Rádio Comunicador', quantidade: 15, status: 'disponivel' },
      { id: 'e2', nome: 'Colete Balístico', quantidade: 12, status: 'em_uso' },
    ],
    observacoes: 'Posto de alta movimentação. Requer experiência em shoppings.',
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-06-20T14:30:00Z',
  },
  {
    id: '2',
    nome: 'Condomínio Residencial Aurora',
    endereco: 'Rua das Flores, 500 - Morumbi, São Paulo/SP',
    cliente: 'Administradora Aurora',
    cliente_id: 'c2',
    status: 'ativo',
    coordenadas: { lat: -23.5912, lng: -46.7192 },
    contato_responsavel: {
      nome: 'Maria Santos',
      telefone: '(11) 99999-0002',
      email: 'maria.santos@aurora.com.br',
      cargo: 'Síndica',
    },
    turnos: [
      {
        id: 't4',
        nome: 'Escala 12x36 - Diurno',
        horario_inicio: '07:00',
        horario_fim: '19:00',
        dias_semana: [0, 1, 2, 3, 4, 5, 6],
        profissionais_alocados: 2,
        profissionais_necessarios: 2,
        tipo: '12x36',
        adicional_noturno: false,
        intervalo_minutos: 60,
      },
      {
        id: 't5',
        nome: 'Escala 12x36 - Noturno',
        horario_inicio: '19:00',
        horario_fim: '07:00',
        dias_semana: [0, 1, 2, 3, 4, 5, 6],
        profissionais_alocados: 2,
        profissionais_necessarios: 2,
        tipo: '12x36',
        adicional_noturno: true,
        intervalo_minutos: 60,
      },
    ],
    observacoes: 'Condomínio de alto padrão. Foco em atendimento.',
    created_at: '2024-02-10T08:00:00Z',
    updated_at: '2024-05-15T11:00:00Z',
  },
  {
    id: '3',
    nome: 'Hospital São Lucas',
    endereco: 'Av. Brasil, 2500 - Centro, São Paulo/SP',
    cliente: 'Rede São Lucas Saúde',
    cliente_id: 'c3',
    status: 'ativo',
    coordenadas: { lat: -23.5475, lng: -46.6361 },
    contato_responsavel: {
      nome: 'Dr. Roberto Lima',
      telefone: '(11) 99999-0003',
      email: 'roberto.lima@saolucas.com.br',
      cargo: 'Diretor Administrativo',
    },
    turnos: [
      {
        id: 't6',
        nome: 'Plantão 24h',
        horario_inicio: '07:00',
        horario_fim: '07:00',
        dias_semana: [0, 1, 2, 3, 4, 5, 6],
        profissionais_alocados: 6,
        profissionais_necessarios: 8,
        tipo: '24h',
        adicional_noturno: true,
        intervalo_minutos: 120,
      },
    ],
    requisitos: [
      { id: 'r3', descricao: 'Curso de Vigilante', obrigatorio: true, tipo: 'certificacao' },
      { id: 'r4', descricao: 'Experiência em Hospitais', obrigatorio: true, tipo: 'experiencia' },
      { id: 'r5', descricao: 'Primeiros Socorros', obrigatorio: false, tipo: 'certificacao' },
    ],
    observacoes: 'Ambiente hospitalar. Protocolo especial de segurança.',
    created_at: '2024-03-01T09:00:00Z',
    updated_at: '2024-06-25T16:45:00Z',
  },
  {
    id: '4',
    nome: 'Edifício Corporativo Tower',
    endereco: 'Av. Faria Lima, 3500 - Itaim Bibi, São Paulo/SP',
    cliente: 'Tower Administração',
    cliente_id: 'c4',
    status: 'em_implantacao',
    coordenadas: { lat: -23.5686, lng: -46.6912 },
    contato_responsavel: {
      nome: 'Amanda Costa',
      telefone: '(11) 99999-0004',
      email: 'amanda.costa@tower.com.br',
      cargo: 'Facilities Manager',
    },
    turnos: [
      {
        id: 't7',
        nome: 'Comercial',
        horario_inicio: '07:00',
        horario_fim: '19:00',
        dias_semana: [1, 2, 3, 4, 5],
        profissionais_alocados: 0,
        profissionais_necessarios: 4,
        tipo: 'diurno',
        adicional_noturno: false,
        intervalo_minutos: 60,
      },
    ],
    observacoes: 'Novo contrato. Início previsto para próximo mês.',
    created_at: '2024-06-01T10:00:00Z',
    updated_at: '2024-06-28T09:00:00Z',
  },
  {
    id: '5',
    nome: 'Fábrica Industrial ABC',
    endereco: 'Rod. Anchieta, km 45 - São Bernardo/SP',
    cliente: 'Indústrias ABC',
    cliente_id: 'c5',
    status: 'inativo',
    coordenadas: { lat: -23.6914, lng: -46.5646 },
    contato_responsavel: {
      nome: 'José Oliveira',
      telefone: '(11) 99999-0005',
      email: 'jose.oliveira@abc.com.br',
      cargo: 'Gerente de Operações',
    },
    turnos: [],
    observacoes: 'Contrato encerrado em maio/2024.',
    created_at: '2023-06-15T08:00:00Z',
    updated_at: '2024-05-31T18:00:00Z',
  },
];

export const usePostos = (filters?: PostoFilters) => {
  const [postos, setPostos] = useState<Posto[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPostos = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Simula delay de API
      await new Promise((resolve) => setTimeout(resolve, 500));

      let filteredPostos = [...mockPostos];

      if (filters?.status?.length) {
        filteredPostos = filteredPostos.filter((p) =>
          filters.status!.includes(p.status)
        );
      }

      if (filters?.cliente_id) {
        filteredPostos = filteredPostos.filter(
          (p) => p.cliente_id === filters.cliente_id
        );
      }

      if (filters?.search) {
        const search = filters.search.toLowerCase();
        filteredPostos = filteredPostos.filter(
          (p) =>
            p.nome.toLowerCase().includes(search) ||
            p.endereco.toLowerCase().includes(search) ||
            p.cliente.toLowerCase().includes(search)
        );
      }

      if (filters?.com_vagas) {
        filteredPostos = filteredPostos.filter((p) =>
          p.turnos.some((t) => t.profissionais_alocados < t.profissionais_necessarios)
        );
      }

      setPostos(filteredPostos);
    } catch (err) {
      setError('Erro ao carregar postos');
      console.error('Erro ao carregar postos:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadPostos();
  }, [loadPostos]);

  const stats = useMemo<PostoStats>(() => {
    const ativos = postos.filter((p) => p.status === 'ativo');
    const inativos = postos.filter((p) => p.status === 'inativo');
    const todosTurnos = postos.flatMap((p) => p.turnos);
    const alocados = todosTurnos.reduce((acc, t) => acc + t.profissionais_alocados, 0);
    const necessarios = todosTurnos.reduce(
      (acc, t) => acc + t.profissionais_necessarios,
      0
    );

    return {
      total_postos: postos.length,
      postos_ativos: ativos.length,
      postos_inativos: inativos.length,
      total_turnos: todosTurnos.length,
      profissionais_alocados: alocados,
      profissionais_necessarios: necessarios,
      taxa_ocupacao: necessarios > 0 ? (alocados / necessarios) * 100 : 0,
    };
  }, [postos]);

  const createPosto = async (data: PostoFormData): Promise<Posto> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      const novoPosto: Posto = {
        ...data,
        id: `p${Date.now()}`,
        cliente: 'Novo Cliente', // Seria buscado pelo cliente_id
        turnos: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setPostos((prev) => [novoPosto, ...prev]);
      return novoPosto;
    } catch (err) {
      console.error('Erro ao criar posto:', err);
      throw err;
    }
  };

  const updatePosto = async (id: string, data: Partial<PostoFormData>): Promise<Posto> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      let updatedPosto: Posto | undefined;

      setPostos((prev) =>
        prev.map((posto) => {
          if (posto.id === id) {
            updatedPosto = {
              ...posto,
              ...data,
              updated_at: new Date().toISOString(),
            };
            return updatedPosto;
          }
          return posto;
        })
      );

      if (!updatedPosto) {
        throw new Error('Posto não encontrado');
      }

      return updatedPosto;
    } catch (err) {
      console.error('Erro ao atualizar posto:', err);
      throw err;
    }
  };

  const deletePosto = async (id: string): Promise<void> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));
      setPostos((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      console.error('Erro ao deletar posto:', err);
      throw err;
    }
  };

  const addTurno = async (postoId: string, data: TurnoFormData): Promise<Turno> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      const novoTurno: Turno = {
        ...data,
        id: `t${Date.now()}`,
        profissionais_alocados: 0,
      };

      setPostos((prev) =>
        prev.map((posto) => {
          if (posto.id === postoId) {
            return {
              ...posto,
              turnos: [...posto.turnos, novoTurno],
              updated_at: new Date().toISOString(),
            };
          }
          return posto;
        })
      );

      return novoTurno;
    } catch (err) {
      console.error('Erro ao adicionar turno:', err);
      throw err;
    }
  };

  const updateTurno = async (
    postoId: string,
    turnoId: string,
    data: Partial<TurnoFormData>
  ): Promise<Turno> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      let updatedTurno: Turno | undefined;

      setPostos((prev) =>
        prev.map((posto) => {
          if (posto.id === postoId) {
            return {
              ...posto,
              turnos: posto.turnos.map((turno) => {
                if (turno.id === turnoId) {
                  updatedTurno = { ...turno, ...data };
                  return updatedTurno;
                }
                return turno;
              }),
              updated_at: new Date().toISOString(),
            };
          }
          return posto;
        })
      );

      if (!updatedTurno) {
        throw new Error('Turno não encontrado');
      }

      return updatedTurno;
    } catch (err) {
      console.error('Erro ao atualizar turno:', err);
      throw err;
    }
  };

  const deleteTurno = async (postoId: string, turnoId: string): Promise<void> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      setPostos((prev) =>
        prev.map((posto) => {
          if (posto.id === postoId) {
            return {
              ...posto,
              turnos: posto.turnos.filter((t) => t.id !== turnoId),
              updated_at: new Date().toISOString(),
            };
          }
          return posto;
        })
      );
    } catch (err) {
      console.error('Erro ao deletar turno:', err);
      throw err;
    }
  };

  const getPostoById = useCallback(
    (id: string): Posto | undefined => {
      return postos.find((p) => p.id === id);
    },
    [postos]
  );

  return {
    postos,
    loading,
    error,
    stats,
    loadPostos,
    createPosto,
    updatePosto,
    deletePosto,
    addTurno,
    updateTurno,
    deleteTurno,
    getPostoById,
  };
};

export default usePostos;
