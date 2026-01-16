import { useState, useEffect, useCallback, useMemo } from 'react';
import type {
  Substitution,
  SubstitutionFilters,
  SubstitutionStats,
  SubstitutionFormData,
  ApprovalAction,
  AvailableSubstitute,
  WorkflowStep,
} from '../types/substitutions.types';

// Mock Data
const mockSubstitutions: Substitution[] = [
  {
    id: 'sub1',
    solicitante_id: 'p4',
    solicitante_nome: 'Ana Costa',
    solicitante_funcao: 'Vigilante',
    substituto_id: undefined,
    substituto_nome: undefined,
    posto_id: '3',
    posto_nome: 'Hospital São Lucas',
    schedule_id: 's4',
    data: '2024-06-28',
    turno: 'Plantão 24h',
    horario_inicio: '07:00',
    horario_fim: '07:00',
    motivo: 'atestado_medico',
    motivo_descricao: 'Atestado médico de 3 dias',
    status: 'aguardando_substituto',
    aprovador_id: 'adm1',
    aprovador_nome: 'Supervisor Carlos',
    aprovado_em: '2024-06-27T16:00:00Z',
    urgente: true,
    documentos: [
      {
        id: 'd1',
        nome: 'atestado_ana_costa.pdf',
        tipo: 'atestado',
        url: '/docs/atestado_ana_costa.pdf',
        tamanho: 245000,
        uploaded_at: '2024-06-27T14:00:00Z',
      },
    ],
    historico: [
      {
        id: 'h1',
        acao: 'criacao',
        descricao: 'Solicitação criada',
        usuario_id: 'p4',
        usuario_nome: 'Ana Costa',
        timestamp: '2024-06-27T14:00:00Z',
      },
      {
        id: 'h2',
        acao: 'aprovacao',
        descricao: 'Solicitação aprovada',
        usuario_id: 'adm1',
        usuario_nome: 'Supervisor Carlos',
        timestamp: '2024-06-27T16:00:00Z',
      },
    ],
    created_at: '2024-06-27T14:00:00Z',
    updated_at: '2024-06-27T16:00:00Z',
  },
  {
    id: 'sub2',
    solicitante_id: 'p2',
    solicitante_nome: 'Maria Santos',
    solicitante_funcao: 'Vigilante',
    substituto_id: 'p7',
    substituto_nome: 'Ricardo Alves',
    substituto_funcao: 'Vigilante',
    posto_id: '1',
    posto_nome: 'Shopping Center Norte',
    schedule_id: 's10',
    data: '2024-06-30',
    turno: 'Turno B - Tarde',
    horario_inicio: '14:00',
    horario_fim: '22:00',
    motivo: 'troca_turno',
    motivo_descricao: 'Troca acordada com Ricardo',
    status: 'substituto_confirmado',
    aprovador_id: 'adm1',
    aprovador_nome: 'Supervisor Carlos',
    aprovado_em: '2024-06-26T10:00:00Z',
    urgente: false,
    historico: [
      {
        id: 'h3',
        acao: 'criacao',
        descricao: 'Solicitação criada',
        usuario_id: 'p2',
        usuario_nome: 'Maria Santos',
        timestamp: '2024-06-25T18:00:00Z',
      },
      {
        id: 'h4',
        acao: 'aprovacao',
        descricao: 'Solicitação aprovada',
        usuario_id: 'adm1',
        usuario_nome: 'Supervisor Carlos',
        timestamp: '2024-06-26T10:00:00Z',
      },
      {
        id: 'h5',
        acao: 'substituto_confirmado',
        descricao: 'Ricardo Alves confirmou a substituição',
        usuario_id: 'p7',
        usuario_nome: 'Ricardo Alves',
        timestamp: '2024-06-26T11:00:00Z',
      },
    ],
    created_at: '2024-06-25T18:00:00Z',
    updated_at: '2024-06-26T11:00:00Z',
  },
  {
    id: 'sub3',
    solicitante_id: 'p5',
    solicitante_nome: 'Carlos Mendes',
    solicitante_funcao: 'Vigilante',
    posto_id: '1',
    posto_nome: 'Shopping Center Norte',
    schedule_id: 's5',
    data: '2024-06-28',
    turno: 'Turno C - Noite',
    horario_inicio: '22:00',
    horario_fim: '06:00',
    motivo: 'emergencia_pessoal',
    motivo_descricao: 'Problema familiar urgente',
    status: 'pendente',
    urgente: true,
    historico: [
      {
        id: 'h6',
        acao: 'criacao',
        descricao: 'Solicitação criada',
        usuario_id: 'p5',
        usuario_nome: 'Carlos Mendes',
        timestamp: '2024-06-28T15:00:00Z',
      },
    ],
    created_at: '2024-06-28T15:00:00Z',
    updated_at: '2024-06-28T15:00:00Z',
  },
  {
    id: 'sub4',
    solicitante_id: 'p3',
    solicitante_nome: 'Pedro Oliveira',
    solicitante_funcao: 'Porteiro',
    substituto_id: 'p8',
    substituto_nome: 'Lucia Ferreira',
    substituto_funcao: 'Porteira',
    posto_id: '2',
    posto_nome: 'Condomínio Residencial Aurora',
    schedule_id: 's11',
    data: '2024-06-25',
    turno: 'Escala 12x36 - Diurno',
    horario_inicio: '07:00',
    horario_fim: '19:00',
    motivo: 'folga_compensatoria',
    status: 'concluida',
    aprovador_id: 'adm1',
    aprovador_nome: 'Supervisor Carlos',
    aprovado_em: '2024-06-24T09:00:00Z',
    urgente: false,
    historico: [
      {
        id: 'h7',
        acao: 'criacao',
        descricao: 'Solicitação criada',
        usuario_id: 'p3',
        usuario_nome: 'Pedro Oliveira',
        timestamp: '2024-06-23T10:00:00Z',
      },
      {
        id: 'h8',
        acao: 'aprovacao',
        descricao: 'Solicitação aprovada',
        usuario_id: 'adm1',
        usuario_nome: 'Supervisor Carlos',
        timestamp: '2024-06-24T09:00:00Z',
      },
      {
        id: 'h9',
        acao: 'conclusao',
        descricao: 'Substituição realizada com sucesso',
        usuario_id: 'sistema',
        usuario_nome: 'Sistema',
        timestamp: '2024-06-25T19:00:00Z',
      },
    ],
    created_at: '2024-06-23T10:00:00Z',
    updated_at: '2024-06-25T19:00:00Z',
  },
  {
    id: 'sub5',
    solicitante_id: 'p9',
    solicitante_nome: 'Fernando Gomes',
    solicitante_funcao: 'Vigilante',
    posto_id: '3',
    posto_nome: 'Hospital São Lucas',
    schedule_id: 's12',
    data: '2024-06-27',
    turno: 'Plantão 24h',
    horario_inicio: '07:00',
    horario_fim: '07:00',
    motivo: 'problema_transporte',
    motivo_descricao: 'Carro quebrou, sem condições de ir',
    status: 'rejeitada',
    aprovador_id: 'adm1',
    aprovador_nome: 'Supervisor Carlos',
    rejeitado_em: '2024-06-26T20:00:00Z',
    motivo_rejeicao: 'Solicitação fora do prazo mínimo de 24h',
    urgente: false,
    historico: [
      {
        id: 'h10',
        acao: 'criacao',
        descricao: 'Solicitação criada',
        usuario_id: 'p9',
        usuario_nome: 'Fernando Gomes',
        timestamp: '2024-06-26T18:00:00Z',
      },
      {
        id: 'h11',
        acao: 'rejeicao',
        descricao: 'Solicitação rejeitada: fora do prazo',
        usuario_id: 'adm1',
        usuario_nome: 'Supervisor Carlos',
        timestamp: '2024-06-26T20:00:00Z',
      },
    ],
    created_at: '2024-06-26T18:00:00Z',
    updated_at: '2024-06-26T20:00:00Z',
  },
];

const mockAvailableSubstitutes: AvailableSubstitute[] = [
  {
    id: 'p7',
    nome: 'Ricardo Alves',
    funcao: 'Vigilante',
    telefone: '(11) 99999-1001',
    email: 'ricardo.alves@email.com',
    disponibilidade: 'disponivel',
    horas_trabalhadas_semana: 32,
    distancia_posto: 5.2,
    avaliacao: 4.8,
    total_substituicoes: 15,
    ultima_substituicao: '2024-06-20',
  },
  {
    id: 'p8',
    nome: 'Lucia Ferreira',
    funcao: 'Porteira',
    telefone: '(11) 99999-1002',
    email: 'lucia.ferreira@email.com',
    disponibilidade: 'disponivel',
    horas_trabalhadas_semana: 36,
    distancia_posto: 8.1,
    avaliacao: 4.5,
    total_substituicoes: 8,
    ultima_substituicao: '2024-06-25',
  },
  {
    id: 'p10',
    nome: 'Roberto Santos',
    funcao: 'Vigilante',
    telefone: '(11) 99999-1003',
    email: 'roberto.santos@email.com',
    disponibilidade: 'parcial',
    horas_trabalhadas_semana: 40,
    distancia_posto: 12.5,
    avaliacao: 4.2,
    total_substituicoes: 22,
    ultima_substituicao: '2024-06-26',
  },
  {
    id: 'p11',
    nome: 'Patricia Lima',
    funcao: 'Vigilante',
    telefone: '(11) 99999-1004',
    email: 'patricia.lima@email.com',
    disponibilidade: 'indisponivel',
    horas_trabalhadas_semana: 44,
    avaliacao: 4.9,
    total_substituicoes: 30,
    ultima_substituicao: '2024-06-27',
  },
];

export const useSubstitutions = (filters?: SubstitutionFilters) => {
  const [substitutions, setSubstitutions] = useState<Substitution[]>([]);
  const [availableSubstitutes, setAvailableSubstitutes] = useState<AvailableSubstitute[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSubstitutions = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      await new Promise((resolve) => setTimeout(resolve, 500));

      let filteredSubstitutions = [...mockSubstitutions];

      if (filters?.status?.length) {
        filteredSubstitutions = filteredSubstitutions.filter((s) =>
          filters.status!.includes(s.status)
        );
      }

      if (filters?.motivo?.length) {
        filteredSubstitutions = filteredSubstitutions.filter((s) =>
          filters.motivo!.includes(s.motivo)
        );
      }

      if (filters?.posto_id) {
        filteredSubstitutions = filteredSubstitutions.filter(
          (s) => s.posto_id === filters.posto_id
        );
      }

      if (filters?.solicitante_id) {
        filteredSubstitutions = filteredSubstitutions.filter(
          (s) => s.solicitante_id === filters.solicitante_id
        );
      }

      if (filters?.urgente !== undefined) {
        filteredSubstitutions = filteredSubstitutions.filter(
          (s) => s.urgente === filters.urgente
        );
      }

      if (filters?.data_inicio) {
        filteredSubstitutions = filteredSubstitutions.filter(
          (s) => s.data >= filters.data_inicio!
        );
      }

      if (filters?.data_fim) {
        filteredSubstitutions = filteredSubstitutions.filter(
          (s) => s.data <= filters.data_fim!
        );
      }

      setSubstitutions(filteredSubstitutions);
      setAvailableSubstitutes(mockAvailableSubstitutes);
    } catch (err) {
      setError('Erro ao carregar substituições');
      console.error('Erro ao carregar substituições:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadSubstitutions();
  }, [loadSubstitutions]);

  const stats = useMemo<SubstitutionStats>(() => {
    const pendentes = substitutions.filter((s) => s.status === 'pendente');
    const aprovadas = substitutions.filter(
      (s) => s.status === 'aprovada' || s.status === 'aguardando_substituto'
    );
    const rejeitadas = substitutions.filter((s) => s.status === 'rejeitada');
    const aguardando = substitutions.filter(
      (s) => s.status === 'aguardando_substituto'
    );
    const concluidas = substitutions.filter((s) => s.status === 'concluida');

    const total = substitutions.length;
    const taxaAprovacao =
      total > 0
        ? ((aprovadas.length + concluidas.length) / total) * 100
        : 0;

    // Calcular motivos frequentes
    const motivosCount: Record<string, number> = {};
    substitutions.forEach((s) => {
      motivosCount[s.motivo] = (motivosCount[s.motivo] || 0) + 1;
    });

    const motivosFrequentes = Object.entries(motivosCount)
      .map(([motivo, quantidade]) => ({
        motivo: motivo as SubstitutionFormData['motivo'],
        quantidade,
        percentual: total > 0 ? (quantidade / total) * 100 : 0,
      }))
      .sort((a, b) => b.quantidade - a.quantidade)
      .slice(0, 5);

    return {
      total_solicitacoes: total,
      pendentes: pendentes.length,
      aprovadas: aprovadas.length,
      rejeitadas: rejeitadas.length,
      aguardando_substituto: aguardando.length,
      concluidas: concluidas.length,
      taxa_aprovacao: taxaAprovacao,
      tempo_medio_aprovacao: 4.5, // Mock: 4.5 horas em média
      motivos_frequentes: motivosFrequentes,
    };
  }, [substitutions]);

  const getWorkflowSteps = useCallback((substitution: Substitution): WorkflowStep[] => {
    const steps: WorkflowStep[] = [
      {
        id: 'step1',
        ordem: 1,
        titulo: 'Solicitação Criada',
        descricao: 'Profissional solicitou substituição',
        status: 'concluido',
        responsavel: substitution.solicitante_nome,
        data_conclusao: substitution.created_at,
        icone: 'FileText',
      },
      {
        id: 'step2',
        ordem: 2,
        titulo: 'Análise do Supervisor',
        descricao: 'Aguardando aprovação',
        status:
          substitution.status === 'pendente'
            ? 'atual'
            : substitution.status === 'rejeitada'
            ? 'concluido'
            : 'concluido',
        responsavel: substitution.aprovador_nome,
        data_conclusao: substitution.aprovado_em || substitution.rejeitado_em,
        icone: 'UserCheck',
      },
      {
        id: 'step3',
        ordem: 3,
        titulo: 'Busca de Substituto',
        descricao: 'Localizando profissional disponível',
        status:
          substitution.status === 'pendente' || substitution.status === 'rejeitada'
            ? 'pendente'
            : substitution.status === 'aguardando_substituto'
            ? 'atual'
            : 'concluido',
        icone: 'Search',
      },
      {
        id: 'step4',
        ordem: 4,
        titulo: 'Confirmação do Substituto',
        descricao: 'Substituto aceita a escala',
        status:
          ['pendente', 'rejeitada', 'aguardando_substituto'].includes(substitution.status)
            ? 'pendente'
            : substitution.status === 'substituto_confirmado'
            ? 'atual'
            : 'concluido',
        responsavel: substitution.substituto_nome,
        icone: 'CheckCircle',
      },
      {
        id: 'step5',
        ordem: 5,
        titulo: 'Substituição Concluída',
        descricao: 'Turno realizado com sucesso',
        status: substitution.status === 'concluida' ? 'concluido' : 'pendente',
        icone: 'Flag',
      },
    ];

    // Marcar como pulado se rejeitada
    if (substitution.status === 'rejeitada') {
      steps.slice(2).forEach((step) => {
        step.status = 'pulado';
      });
    }

    return steps;
  }, []);

  const createSubstitution = async (
    data: SubstitutionFormData
  ): Promise<Substitution> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      const novaSubstituicao: Substitution = {
        id: `sub${Date.now()}`,
        solicitante_id: 'current_user', // Seria o usuário logado
        solicitante_nome: 'Usuário Atual',
        solicitante_funcao: 'Vigilante',
        substituto_id: data.substituto_id,
        posto_id: 'p1', // Seria extraído do schedule
        posto_nome: 'Posto',
        schedule_id: data.schedule_id,
        data: new Date().toISOString().split('T')[0],
        turno: 'Turno',
        horario_inicio: '08:00',
        horario_fim: '16:00',
        motivo: data.motivo,
        motivo_descricao: data.motivo_descricao,
        status: 'pendente',
        urgente: data.urgente,
        historico: [
          {
            id: `h${Date.now()}`,
            acao: 'criacao',
            descricao: 'Solicitação criada',
            usuario_id: 'current_user',
            usuario_nome: 'Usuário Atual',
            timestamp: new Date().toISOString(),
          },
        ],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setSubstitutions((prev) => [novaSubstituicao, ...prev]);
      return novaSubstituicao;
    } catch (err) {
      console.error('Erro ao criar substituição:', err);
      throw err;
    }
  };

  const processApproval = async (action: ApprovalAction): Promise<Substitution> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      let updatedSubstitution: Substitution | undefined;

      setSubstitutions((prev) =>
        prev.map((sub) => {
          if (sub.id === action.substitution_id) {
            const newHistoryItem = {
              id: `h${Date.now()}`,
              acao: action.tipo === 'aprovar' ? 'aprovacao' : 'rejeicao',
              descricao:
                action.tipo === 'aprovar'
                  ? 'Solicitação aprovada'
                  : `Solicitação rejeitada: ${action.motivo_rejeicao}`,
              usuario_id: 'current_user',
              usuario_nome: 'Supervisor Atual',
              timestamp: new Date().toISOString(),
            };

            updatedSubstitution = {
              ...sub,
              status:
                action.tipo === 'aprovar' ? 'aguardando_substituto' : 'rejeitada',
              aprovador_id: 'current_user',
              aprovador_nome: 'Supervisor Atual',
              aprovado_em:
                action.tipo === 'aprovar' ? new Date().toISOString() : undefined,
              rejeitado_em:
                action.tipo === 'rejeitar' ? new Date().toISOString() : undefined,
              motivo_rejeicao: action.motivo_rejeicao,
              substituto_id: action.substituto_id,
              historico: [...sub.historico, newHistoryItem],
              updated_at: new Date().toISOString(),
            };

            return updatedSubstitution;
          }
          return sub;
        })
      );

      if (!updatedSubstitution) {
        throw new Error('Substituição não encontrada');
      }

      return updatedSubstitution;
    } catch (err) {
      console.error('Erro ao processar aprovação:', err);
      throw err;
    }
  };

  const assignSubstitute = async (
    substitutionId: string,
    substituteId: string
  ): Promise<Substitution> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      const substitute = availableSubstitutes.find((s) => s.id === substituteId);
      let updatedSubstitution: Substitution | undefined;

      setSubstitutions((prev) =>
        prev.map((sub) => {
          if (sub.id === substitutionId) {
            const newHistoryItem = {
              id: `h${Date.now()}`,
              acao: 'substituto_atribuido',
              descricao: `Substituto atribuído: ${substitute?.nome}`,
              usuario_id: 'current_user',
              usuario_nome: 'Supervisor Atual',
              timestamp: new Date().toISOString(),
            };

            updatedSubstitution = {
              ...sub,
              substituto_id: substituteId,
              substituto_nome: substitute?.nome,
              substituto_funcao: substitute?.funcao,
              status: 'substituto_confirmado',
              historico: [...sub.historico, newHistoryItem],
              updated_at: new Date().toISOString(),
            };

            return updatedSubstitution;
          }
          return sub;
        })
      );

      if (!updatedSubstitution) {
        throw new Error('Substituição não encontrada');
      }

      return updatedSubstitution;
    } catch (err) {
      console.error('Erro ao atribuir substituto:', err);
      throw err;
    }
  };

  const cancelSubstitution = async (id: string): Promise<void> => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 300));

      setSubstitutions((prev) =>
        prev.map((sub) => {
          if (sub.id === id) {
            return {
              ...sub,
              status: 'cancelada',
              updated_at: new Date().toISOString(),
            };
          }
          return sub;
        })
      );
    } catch (err) {
      console.error('Erro ao cancelar substituição:', err);
      throw err;
    }
  };

  const getSubstitutionById = useCallback(
    (id: string): Substitution | undefined => {
      return substitutions.find((s) => s.id === id);
    },
    [substitutions]
  );

  const getReasonLabel = (reason: string): string => {
    const labels: Record<string, string> = {
      atestado_medico: 'Atestado Médico',
      emergencia_pessoal: 'Emergência Pessoal',
      problema_transporte: 'Problema de Transporte',
      ferias: 'Férias',
      licenca: 'Licença',
      folga_compensatoria: 'Folga Compensatória',
      troca_turno: 'Troca de Turno',
      outro: 'Outro',
    };
    return labels[reason] || reason;
  };

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      pendente: 'Pendente',
      aprovada: 'Aprovada',
      rejeitada: 'Rejeitada',
      cancelada: 'Cancelada',
      aguardando_substituto: 'Aguardando Substituto',
      substituto_confirmado: 'Substituto Confirmado',
      concluida: 'Concluída',
    };
    return labels[status] || status;
  };

  return {
    substitutions,
    availableSubstitutes,
    loading,
    error,
    stats,
    loadSubstitutions,
    createSubstitution,
    processApproval,
    assignSubstitute,
    cancelSubstitution,
    getSubstitutionById,
    getWorkflowSteps,
    getReasonLabel,
    getStatusLabel,
  };
};

export default useSubstitutions;
