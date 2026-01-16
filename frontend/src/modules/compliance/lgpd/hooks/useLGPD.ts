import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@core/api';
import type { DataSubject, RightsRequest, LGPDStats } from '../types/lgpd.types';

// Mock data
const mockStats: LGPDStats = {
  totalSubjects: 1250,
  activeConsents: 3480,
  pendingRequests: 8,
  expiringConsents: 45,
  complianceScore: 94,
};

const mockRequests: RightsRequest[] = [
  {
    id: '1',
    subjectId: '1',
    subjectName: 'Maria Silva',
    type: 'acesso',
    status: 'pendente',
    description: 'Solicito acesso a todos os meus dados pessoais',
    createdAt: '2026-01-10T10:00:00Z',
    deadline: '2026-01-25T10:00:00Z',
    attachments: [],
  },
  {
    id: '2',
    subjectId: '2',
    subjectName: 'Joao Santos',
    type: 'exclusao',
    status: 'em_andamento',
    description: 'Solicito a exclusao de todos os meus dados',
    createdAt: '2026-01-08T10:00:00Z',
    deadline: '2026-01-23T10:00:00Z',
    assignedTo: { id: '1', name: 'Ana Costa' },
    attachments: [],
  },
  {
    id: '3',
    subjectId: '3',
    subjectName: 'Pedro Lima',
    type: 'retificacao',
    status: 'concluida',
    description: 'Correcao do endereco cadastrado',
    createdAt: '2026-01-05T10:00:00Z',
    deadline: '2026-01-20T10:00:00Z',
    completedAt: '2026-01-07T15:00:00Z',
    attachments: [],
    response: 'Dados retificados com sucesso',
  },
];

const mockSubjects: DataSubject[] = [
  {
    id: '1',
    name: 'Maria Silva',
    email: 'maria@email.com',
    cpf: '***.***.***-01',
    consents: [],
    requests: [],
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2026-01-10T00:00:00Z',
  },
];

export function useLGPDStats() {
  return useQuery({
    queryKey: ['lgpd', 'stats'],
    queryFn: async () => {
      try {
        return await api.get<LGPDStats>('/security-lgpd/stats');
      } catch {
        return mockStats;
      }
    },
    staleTime: 1000 * 60 * 5,
  });
}

export function useRightsRequests(status?: string) {
  return useQuery({
    queryKey: ['lgpd', 'requests', status],
    queryFn: async () => {
      try {
        return await api.get<RightsRequest[]>('/security-lgpd/requests', { params: { status } });
      } catch {
        if (status) {
          return mockRequests.filter(r => r.status === status);
        }
        return mockRequests;
      }
    },
  });
}

export function useDataSubjects() {
  return useQuery({
    queryKey: ['lgpd', 'subjects'],
    queryFn: async () => {
      try {
        return await api.get<DataSubject[]>('/security-lgpd/subjects');
      } catch {
        return mockSubjects;
      }
    },
  });
}

export function useCreateRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: Omit<RightsRequest, 'id' | 'createdAt' | 'deadline'>) => {
      return await api.post<RightsRequest>('/security-lgpd/requests', request);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lgpd', 'requests'] });
    },
  });
}

export function useUpdateRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<RightsRequest> }) => {
      return await api.patch<RightsRequest>(`/security-lgpd/requests/${id}`, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lgpd', 'requests'] });
    },
  });
}
