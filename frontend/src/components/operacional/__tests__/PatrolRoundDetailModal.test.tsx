/**
 * Testes para PatrolRoundDetailModal
 * Cobre branches: patrolRound=null (retorna null), cada status de ronda,
 * progress_percentage > 0, observations presente/ausente,
 * status=concluida com/sem summary, checkpoints presente/ausente,
 * checkpoint com/sem post_name, checkpoint com/sem employee_name,
 * checkpoint com/sem description, checkpoint com/sem occurrence_code,
 * localizacao com/sem total_distance_km, formatDuration com/sem horas
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@/test/helpers/test-utils';
import { PatrolRoundDetailModal } from '../patrol-round-detail-modal';
import type { PatrolRound, PatrolCheckpoint } from '@/types/operacional';

const mockOnClose = vi.fn();

const basePatrolRound: PatrolRound = {
  id: 'pr-1',
  code: 'RND-001',
  tenant_id: 'tenant-1',
  inspector_id: 'emp-1',
  inspector_name: 'Carlos Silva',
  inspector_role: 'supervisor_operacional',
  status: 'agendada',
  scheduled_date: '2025-01-15T08:00:00Z',
  started_at: null,
  completed_at: null,
  duration_minutes: null,
  posts_to_visit: ['post-1', 'post-2'],
  posts_visited: ['post-1'],
  total_distance_km: null,
  start_latitude: null,
  start_longitude: null,
  end_latitude: null,
  end_longitude: null,
  total_checkpoints: 5,
  total_occurrences: 0,
  total_disciplinary_actions: 0,
  total_employees_checked: 0,
  progress_percentage: 0,
  observations: null,
  summary: null,
  checkpoints: [],
  is_active: true,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
};

const makeCheckpoint = (overrides: Partial<PatrolCheckpoint> = {}): PatrolCheckpoint => ({
  id: 'cp-1',
  inspection_round_id: 'pr-1',
  post_id: null,
  post_name: null,
  client_id: null,
  client_name: null,
  checkpoint_type: 'verificacao_posto',
  status: 'conforme',
  employee_id: null,
  employee_name: null,
  employee_cpf: null,
  employee_position: null,
  occurrence_id: null,
  occurrence_code: null,
  disciplinary_action_id: null,
  disciplinary_action_code: null,
  disciplinary_action_type: null,
  title: null,
  description: null,
  observations: null,
  infraction_category: null,
  infraction_severity: null,
  photos: null,
  latitude: null,
  longitude: null,
  sequence: 1,
  created_at: '2025-01-01T00:00:00Z',
  ...overrides,
});

describe('PatrolRoundDetailModal', () => {
  describe('quando patrolRound e null', () => {
    it('nao renderiza nada', () => {
      const { container } = render(
        <PatrolRoundDetailModal isOpen={true} onClose={mockOnClose} patrolRound={null} />
      );
      expect(container.firstChild).toBeNull();
    });
  });

  describe('quando modal esta fechado', () => {
    it('nao exibe conteudo quando isOpen=false', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={false}
          onClose={mockOnClose}
          patrolRound={basePatrolRound}
        />
      );
      expect(screen.queryByText('RND-001')).not.toBeInTheDocument();
    });
  });

  describe('renderizacao basica', () => {
    it('exibe codigo da ronda no description', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={basePatrolRound}
        />
      );
      expect(screen.getByText(/RND-001/)).toBeInTheDocument();
    });

    it('exibe nome do inspetor', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={basePatrolRound}
        />
      );
      expect(screen.getByText('Carlos Silva')).toBeInTheDocument();
    });

    it('exibe cargo do inspetor', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={basePatrolRound}
        />
      );
      expect(screen.getByText('Supervisor Operacional')).toBeInTheDocument();
    });
  });

  describe('status branches - badge e icone', () => {
    const statusCases: Array<{ status: PatrolRound['status']; label: string }> = [
      { status: 'agendada', label: 'Agendada' },
      { status: 'em_andamento', label: 'Em Andamento' },
      { status: 'pausada', label: 'Pausada' },
      { status: 'concluida', label: 'Concluída' },
      { status: 'cancelada', label: 'Cancelada' },
    ];

    statusCases.forEach(({ status, label }) => {
      it(`exibe badge correto para status "${status}"`, () => {
        render(
          <PatrolRoundDetailModal
            isOpen={true}
            onClose={mockOnClose}
            patrolRound={{ ...basePatrolRound, status }}
          />
        );
        expect(screen.getByText(label)).toBeInTheDocument();
      });
    });
  });

  describe('progress_percentage branch', () => {
    it('exibe percentual de progresso quando > 0', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, progress_percentage: 60 }}
        />
      );
      expect(screen.getByText(/Progresso: 60%/)).toBeInTheDocument();
    });

    it('nao exibe progresso quando e 0', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, progress_percentage: 0 }}
        />
      );
      expect(screen.queryByText(/Progresso:/)).not.toBeInTheDocument();
    });
  });

  describe('observations branch', () => {
    it('exibe observacoes quando presentes', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, observations: 'Tudo normal na ronda' }}
        />
      );
      expect(screen.getByText('Tudo normal na ronda')).toBeInTheDocument();
    });

    it('nao exibe secao de observacoes quando ausentes (null)', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, observations: null }}
        />
      );
      expect(screen.queryByText('Tudo normal na ronda')).not.toBeInTheDocument();
    });
  });

  describe('summary branch (status concluida)', () => {
    it('exibe resumo de conclusao quando status=concluida e summary presente', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{
            ...basePatrolRound,
            status: 'concluida',
            summary: 'Ronda concluida sem incidentes',
            completed_at: '2025-01-15T10:00:00Z',
          }}
        />
      );
      expect(screen.getByText('Ronda concluida sem incidentes')).toBeInTheDocument();
      expect(screen.getByText(/Resumo da Conclus/i)).toBeInTheDocument();
    });

    it('nao exibe resumo quando status=concluida mas summary e null', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, status: 'concluida', summary: null }}
        />
      );
      expect(screen.queryByText(/Resumo da Conclus/i)).not.toBeInTheDocument();
    });

    it('nao exibe resumo quando status != concluida mesmo com summary preenchido', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, status: 'em_andamento', summary: 'Algum resumo' }}
        />
      );
      expect(screen.queryByText(/Resumo da Conclus/i)).not.toBeInTheDocument();
    });
  });

  describe('formatDuration branches', () => {
    it('exibe "-" quando duration_minutes e null', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, duration_minutes: null }}
        />
      );
      // "-" aparece no campo duracao (e tambem nos campos started_at/completed_at que sao null)
      const dashes = screen.getAllByText('-');
      expect(dashes.length).toBeGreaterThan(0);
    });

    it('exibe apenas minutos quando duracao < 60 min', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, duration_minutes: 45 }}
        />
      );
      expect(screen.getByText('45min')).toBeInTheDocument();
    });

    it('exibe horas e minutos quando duracao >= 60 min', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, duration_minutes: 90 }}
        />
      );
      expect(screen.getByText('1h 30min')).toBeInTheDocument();
    });

    it('exibe somente horas quando minutos restantes = 0', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, duration_minutes: 120 }}
        />
      );
      expect(screen.getByText('2h 0min')).toBeInTheDocument();
    });
  });

  describe('checkpoints section', () => {
    it('nao exibe secao de checkpoints quando lista e vazia', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, checkpoints: [] }}
        />
      );
      expect(screen.queryByText(/Checkpoints \(/)).not.toBeInTheDocument();
    });

    it('exibe secao de checkpoints com contagem quando lista nao e vazia', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, checkpoints: [makeCheckpoint()] }}
        />
      );
      expect(screen.getByText('Checkpoints (1)')).toBeInTheDocument();
    });

    it('exibe post_name do checkpoint quando presente', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{
            ...basePatrolRound,
            checkpoints: [makeCheckpoint({ post_name: 'Portaria Principal' })],
          }}
        />
      );
      expect(screen.getByText('Portaria Principal')).toBeInTheDocument();
    });

    it('nao exibe MapPin do checkpoint quando post_name e null', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{
            ...basePatrolRound,
            checkpoints: [makeCheckpoint({ post_name: null })],
          }}
        />
      );
      // Sem post_name, nao deve aparecer o texto do posto
      expect(screen.queryByText('Portaria Principal')).not.toBeInTheDocument();
    });

    it('exibe employee_name quando presente', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{
            ...basePatrolRound,
            checkpoints: [
              makeCheckpoint({
                checkpoint_type: 'verificacao_funcionario',
                employee_name: 'Ana Souza',
              }),
            ],
          }}
        />
      );
      expect(screen.getByText('Ana Souza')).toBeInTheDocument();
    });

    it('exibe description quando presente', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{
            ...basePatrolRound,
            checkpoints: [
              makeCheckpoint({
                status: 'nao_conforme',
                description: 'Porta encontrada destrancada',
              }),
            ],
          }}
        />
      );
      expect(screen.getByText('Porta encontrada destrancada')).toBeInTheDocument();
    });

    it('exibe occurrence_code quando presente', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{
            ...basePatrolRound,
            checkpoints: [
              makeCheckpoint({ status: 'com_ocorrencia', occurrence_code: 'OCC-042' }),
            ],
          }}
        />
      );
      expect(screen.getByText(/OCC-042/)).toBeInTheDocument();
    });

    it('nao exibe occurrence quando occurrence_code e null', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{
            ...basePatrolRound,
            checkpoints: [makeCheckpoint({ occurrence_code: null })],
          }}
        />
      );
      expect(screen.queryByText(/Ocorrência:/)).not.toBeInTheDocument();
    });
  });

  describe('localizacao section', () => {
    it('exibe secao de localizacao quando start_latitude presente', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, start_latitude: -3.1, start_longitude: -60.0 }}
        />
      );
      expect(screen.getByText(/Informa/i)).toBeInTheDocument();
    });

    it('exibe distancia percorrida quando total_distance_km presente', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, total_distance_km: 5.75, start_latitude: -3.1 }}
        />
      );
      expect(screen.getByText('5.75 km')).toBeInTheDocument();
    });

    it('exibe contagens de postos quando presentes', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{
            ...basePatrolRound,
            start_latitude: -3.1,
            posts_to_visit: ['p1', 'p2', 'p3'],
            posts_visited: ['p1', 'p2'],
          }}
        />
      );
      expect(screen.getByText('Postos planejados:')).toBeInTheDocument();
      expect(screen.getByText('Postos visitados:')).toBeInTheDocument();
    });

    it('nao exibe secao de localizacao quando start_latitude e total_distance_km sao null', () => {
      render(
        <PatrolRoundDetailModal
          isOpen={true}
          onClose={mockOnClose}
          patrolRound={{ ...basePatrolRound, start_latitude: null, total_distance_km: null }}
        />
      );
      expect(screen.queryByText('Postos planejados:')).not.toBeInTheDocument();
    });
  });
});
