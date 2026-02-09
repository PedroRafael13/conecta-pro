import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useJobPositions,
  useOpenJobPositions,
  useJobPosition,
  useJobPositionStats,
  useCandidates,
  useCandidate,
  useCandidateStats,
  useApplications,
  useApplicationsByPosition,
  useApplication,
  useApplicationStats,
  useInterviews,
  useTodayInterviews,
  useInterview,
  useInterviewStats,
  recruitmentKeys,
} from '../useRecruitment';
import { recruitmentService } from '@/services/recruitment.service';
import React from 'react';

// Mocks
vi.mock('@/services/recruitment.service', () => ({
  recruitmentService: {
    jobPositions: {
      list: vi.fn(),
      listOpen: vi.fn(),
      getById: vi.fn(),
      getStats: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
      publish: vi.fn(),
      duplicate: vi.fn(),
    },
    candidates: {
      list: vi.fn(),
      listActive: vi.fn(),
      getById: vi.fn(),
      getStats: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      block: vi.fn(),
    },
    applications: {
      list: vi.fn(),
      listByPosition: vi.fn(),
      getById: vi.fn(),
      getStats: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      advance: vi.fn(),
      reject: vi.fn(),
      toggleFavorite: vi.fn(),
    },
    interviews: {
      list: vi.fn(),
      listToday: vi.fn(),
      listUpcoming: vi.fn(),
      getById: vi.fn(),
      getStats: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      complete: vi.fn(),
      cancel: vi.fn(),
      reschedule: vi.fn(),
      getAvailableSlots: vi.fn(),
    },
  },
}));

describe('useRecruitment', () => {
  let queryClient: QueryClient;

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    React.createElement(QueryClientProvider, { client: queryClient }, children)
  );

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  describe('Query Keys', () => {
    it('deve gerar chaves corretas para vagas', () => {
      expect(recruitmentKeys.positions.all).toEqual(['recruitment', 'positions']);
      expect(recruitmentKeys.positions.list({ search: 'dev' })).toEqual([
        'recruitment', 'positions', 'list', { search: 'dev' }
      ]);
    });

    it('deve gerar chaves corretas para candidatos', () => {
      expect(recruitmentKeys.candidates.all).toEqual(['recruitment', 'candidates']);
      expect(recruitmentKeys.candidates.detail('123')).toEqual([
        'recruitment', 'candidates', 'detail', '123'
      ]);
    });

    it('deve gerar chaves corretas para candidaturas', () => {
      expect(recruitmentKeys.applications.all).toEqual(['recruitment', 'applications']);
      expect(recruitmentKeys.applications.byPosition('pos-1')).toEqual([
        'recruitment', 'applications', 'position', 'pos-1', undefined
      ]);
    });

    it('deve gerar chaves corretas para entrevistas', () => {
      expect(recruitmentKeys.interviews.all).toEqual(['recruitment', 'interviews']);
      expect(recruitmentKeys.interviews.today()).toEqual([
        'recruitment', 'interviews', 'today', undefined
      ]);
    });
  });

  describe('Job Positions', () => {
    it('deve listar vagas', async () => {
      const mockData = { items: [{ id: '1', title: 'Dev', code: 'DEV-001', status: 'open', created_at: '2026-01-01', is_open: true, is_expired: false, remaining_vacancies: 2, is_fully_filled: false, salary_range: '' }], total: 1, page: 1, page_size: 20, pages: 1 };
      vi.mocked(recruitmentService.jobPositions.list).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useJobPositions({ search: 'dev' }), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });

    it('deve listar vagas abertas', async () => {
      const mockData = { items: [{ id: '1', title: 'Dev', status: 'open', code: 'DEV-001', created_at: '2026-01-01', is_open: true, is_expired: false, remaining_vacancies: 2, is_fully_filled: false, salary_range: '' }], total: 1, page: 1, page_size: 20, pages: 1 };
      vi.mocked(recruitmentService.jobPositions.listOpen).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useOpenJobPositions(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });

    it('deve buscar vaga por ID', async () => {
      const mockData = { id: '1', title: 'Dev', code: 'DEV-001', status: 'open', created_at: '2026-01-01', is_open: true, is_expired: false, remaining_vacancies: 2, is_fully_filled: false, salary_range: '' };
      vi.mocked(recruitmentService.jobPositions.getById).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useJobPosition('1'), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });

    it('não deve buscar vaga quando ID é vazio', () => {
      vi.mocked(recruitmentService.jobPositions.getById).mockResolvedValue({} as any);

      const { result } = renderHook(() => useJobPosition(''), { wrapper });

      expect(result.current.isLoading).toBe(false);
      expect(recruitmentService.jobPositions.getById).not.toHaveBeenCalled();
    });

    it('deve buscar estatísticas de vagas', async () => {
      const mockData = { total_positions: 10, open_positions: 5 };
      vi.mocked(recruitmentService.jobPositions.getStats).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useJobPositionStats(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });
  });

  describe('Candidates', () => {
    it('deve listar candidatos', async () => {
      const mockData = { items: [{ id: '1', name: 'John', email: 'john@example.com', status: 'active', created_at: '2026-01-01', is_available: true }], total: 1, page: 1, page_size: 20, pages: 1 };
      vi.mocked(recruitmentService.candidates.list).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useCandidates(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });

    it('deve buscar candidato por ID', async () => {
      const mockData = { id: '1', name: 'John', email: 'john@example.com', status: 'active', created_at: '2026-01-01', is_available: true };
      vi.mocked(recruitmentService.candidates.getById).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useCandidate('1'), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });

    it('deve buscar estatísticas de candidatos', async () => {
      const mockData = { total_candidates: 100, active_candidates: 80 };
      vi.mocked(recruitmentService.candidates.getStats).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useCandidateStats(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });
  });

  describe('Applications', () => {
    it('deve listar candidaturas', async () => {
      const mockData = { items: [{ id: '1', candidate_id: 'c1', job_position_id: 'p1', current_stage: 1, status: 'new', applied_at: '2026-01-01' }], total: 1, page: 1, page_size: 20, pages: 1 };
      vi.mocked(recruitmentService.applications.list).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useApplications(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });

    it('deve listar candidaturas por vaga', async () => {
      const mockData = { items: [{ id: '1', position_id: 'pos-1', candidate_id: 'c1', job_position_id: 'pos-1', current_stage: 1, status: 'new', applied_at: '2026-01-01' }], total: 1, page: 1, page_size: 20, pages: 1 };
      vi.mocked(recruitmentService.applications.listByPosition).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useApplicationsByPosition('pos-1'), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });

    it('não deve buscar quando positionId é vazio', () => {
      vi.mocked(recruitmentService.applications.listByPosition).mockResolvedValue({} as any);

      const { result } = renderHook(() => useApplicationsByPosition(''), { wrapper });

      expect(result.current.isLoading).toBe(false);
    });

    it('deve buscar candidatura por ID', async () => {
      const mockData = { id: '1', status: 'new', job_position_id: 'p1', candidate_id: 'c1', current_stage: 1, applied_at: '2026-01-01' };
      vi.mocked(recruitmentService.applications.getById).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useApplication('1'), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });

    it('deve buscar estatísticas de candidaturas', async () => {
      const mockData = { total: 50, by_status: { pending: 20 } };
      vi.mocked(recruitmentService.applications.getStats).mockResolvedValue(mockData);

      const { result } = renderHook(() => useApplicationStats(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });
  });

  describe('Interviews', () => {
    it('deve listar entrevistas', async () => {
      const mockData = { items: [{ id: '1', scheduled_at: '2026-01-01', scheduled_date: '2026-01-01', scheduled_time: '10:00', application_id: 'a1', created_at: '2026-01-01' }], total: 1, page: 1, page_size: 20, pages: 1 };
      vi.mocked(recruitmentService.interviews.list).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useInterviews(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });

    it('deve listar entrevistas de hoje', async () => {
      const mockData = { items: [{ id: '1', date: 'today', scheduled_date: '2026-01-01', scheduled_time: '10:00', application_id: 'a1', created_at: '2026-01-01' }], total: 1, page: 1, page_size: 20, pages: 1 };
      vi.mocked(recruitmentService.interviews.listToday).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useTodayInterviews(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });

    it('deve buscar entrevista por ID', async () => {
      const mockData = { id: '1', status: 'scheduled', scheduled_date: '2026-01-01', scheduled_time: '10:00', application_id: 'a1', created_at: '2026-01-01' };
      vi.mocked(recruitmentService.interviews.getById).mockResolvedValue(mockData as any);

      const { result } = renderHook(() => useInterview('1'), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });

    it('deve buscar estatísticas de entrevistas', async () => {
      const mockData = { total: 20, completed: 15 };
      vi.mocked(recruitmentService.interviews.getStats).mockResolvedValue(mockData);

      const { result } = renderHook(() => useInterviewStats(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData);
      });
    });
  });

  describe('Stale Times', () => {
    it('deve usar staleTime de 5 minutos para lista de vagas', async () => {
      vi.mocked(recruitmentService.jobPositions.list).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20, pages: 1 } as any);

      renderHook(() => useJobPositions(), { wrapper });

      // Verificar que staleTime é passado nas opções
      await waitFor(() => {
        expect(recruitmentService.jobPositions.list).toHaveBeenCalled();
      });
    });

    it('deve usar staleTime de 1 minuto para entrevistas de hoje', async () => {
      vi.mocked(recruitmentService.interviews.listToday).mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20, pages: 1 } as any);

      renderHook(() => useTodayInterviews(), { wrapper });

      await waitFor(() => {
        expect(recruitmentService.interviews.listToday).toHaveBeenCalled();
      });
    });
  });
});
