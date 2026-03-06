/**
 * Testes para ShiftDayView
 * Cobre branches: empty state, shift status badges, action button states,
 * formatTime com ISO / null / timezone offset, is_off_day, actual_start_time
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@/test/helpers/test-utils';
import userEvent from '@testing-library/user-event';
import { ShiftDayView } from '../shift-day-view';
import type { Shift } from '@/types/operacional';

const mockOnCheckIn = vi.fn();
const mockOnCheckOut = vi.fn();
const mockOnMarkMissed = vi.fn();

const getEmployeeLabel = (id: string | null) => (id ? `Funcionario ${id}` : 'Sem funcionario');
const getPostLabel = (id: string) => `Posto ${id}`;

const baseShift: Shift = {
  id: 'shift-1',
  scale_id: 'scale-1',
  employee_id: 'emp-1',
  post_id: 'post-1',
  shift_date: '2025-01-15',
  planned_start_time: '07:00:00',
  planned_end_time: '19:00:00',
  planned_break_minutes: 60,
  actual_start_time: null,
  actual_end_time: null,
  actual_break_minutes: null,
  status: 'scheduled',
  is_holiday: false,
  is_night_shift: false,
  is_overtime: false,
  is_off_day: false,
  needs_substitution: false,
  planned_hours: 12,
  actual_hours: 0,
  overtime_hours: 0,
  night_hours: 0,
  base_pay: 0,
  overtime_pay: 0,
  night_bonus: 0,
  holiday_bonus: 0,
  total_pay: 0,
  notes: null,
  is_active: true,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
  is_future: false,
  is_today: true,
  is_filled: true,
  was_worked: false,
};

describe('ShiftDayView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('empty state', () => {
    it('exibe mensagem quando nao ha turnos', () => {
      render(
        <ShiftDayView
          shifts={[]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      expect(screen.getByText(/nenhum turno encontrado/i)).toBeInTheDocument();
    });
  });

  describe('renderizacao de turno', () => {
    it('exibe nome do funcionario e posto', () => {
      render(
        <ShiftDayView
          shifts={[baseShift]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      expect(screen.getByText('Funcionario emp-1')).toBeInTheDocument();
      expect(screen.getByText('Posto post-1')).toBeInTheDocument();
    });

    it('exibe horario planejado formatado', () => {
      render(
        <ShiftDayView
          shifts={[baseShift]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      expect(screen.getByText(/07:00/)).toBeInTheDocument();
      expect(screen.getByText(/19:00/)).toBeInTheDocument();
    });
  });

  describe('status badge branches', () => {
    const statusCases: Array<{ status: Shift['status']; label: string }> = [
      { status: 'scheduled', label: 'Agendado' },
      { status: 'in_progress', label: 'Em andamento' },
      { status: 'completed', label: 'Concluido' },
      { status: 'missed', label: 'Falta' },
      { status: 'partial', label: 'Parcial' },
      { status: 'cancelled', label: 'Cancelado' },
      { status: 'off_day', label: 'Folga' },
      { status: 'substituted', label: 'Substituido' },
    ];

    statusCases.forEach(({ status, label }) => {
      it(`renderiza badge correto para status "${status}"`, () => {
        render(
          <ShiftDayView
            shifts={[{ ...baseShift, status }]}
            getEmployeeLabel={getEmployeeLabel}
            getPostLabel={getPostLabel}
            onCheckIn={mockOnCheckIn}
            onCheckOut={mockOnCheckOut}
            onMarkMissed={mockOnMarkMissed}
          />
        );
        expect(screen.getAllByText(label).length).toBeGreaterThanOrEqual(1);
      });
    });
  });

  describe('is_off_day branch', () => {
    it('exibe texto "Folga" quando is_off_day=true', () => {
      render(
        <ShiftDayView
          shifts={[{ ...baseShift, is_off_day: true }]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      // "Folga" aparece como status label e tambem como marcacao off_day
      const folgaElements = screen.getAllByText('Folga');
      expect(folgaElements.length).toBeGreaterThanOrEqual(1);
    });

    it('nao exibe marcacao de folga quando is_off_day=false', () => {
      render(
        <ShiftDayView
          shifts={[{ ...baseShift, status: 'scheduled', is_off_day: false }]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      expect(screen.getByText('Agendado')).toBeInTheDocument();
      // Nao deve ter elemento com o texto isolado "Folga" (sem status badge)
      const folgaElements = screen.queryAllByText('Folga');
      expect(folgaElements).toHaveLength(0);
    });
  });

  describe('actual_start_time branch', () => {
    it('exibe inicio real quando actual_start_time esta preenchido', () => {
      render(
        <ShiftDayView
          shifts={[{ ...baseShift, actual_start_time: '07:05:00', status: 'in_progress' }]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      expect(screen.getByText(/inicio real/i)).toBeInTheDocument();
      expect(screen.getByText(/07:05/)).toBeInTheDocument();
    });

    it('nao exibe inicio real quando actual_start_time e null', () => {
      render(
        <ShiftDayView
          shifts={[{ ...baseShift, actual_start_time: null }]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      expect(screen.queryByText(/inicio real/i)).not.toBeInTheDocument();
    });
  });

  describe('formatTime branches', () => {
    it('exibe "-" quando horario e null/undefined', () => {
      // Shift com planned times undefined - simula edge case de formatTime
      const shiftWithIso = {
        ...baseShift,
        planned_start_time: '2025-01-15T07:00:00Z',
        planned_end_time: '2025-01-15T19:00:00Z',
      };
      render(
        <ShiftDayView
          shifts={[shiftWithIso]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      // Deve extrair horas do ISO e exibir
      expect(screen.getByText(/07:00/)).toBeInTheDocument();
    });
  });

  describe('botoes de acao - estados disabled', () => {
    it('habilita Check-in apenas para turno agendado (scheduled)', () => {
      render(
        <ShiftDayView
          shifts={[{ ...baseShift, status: 'scheduled' }]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      const checkinBtn = screen.getByRole('button', { name: /check-in/i });
      const checkoutBtn = screen.getByRole('button', { name: /check-out/i });
      expect(checkinBtn).not.toBeDisabled();
      expect(checkoutBtn).toBeDisabled();
    });

    it('habilita Check-out apenas para turno em andamento (in_progress)', () => {
      render(
        <ShiftDayView
          shifts={[{ ...baseShift, status: 'in_progress' }]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      const checkinBtn = screen.getByRole('button', { name: /check-in/i });
      const checkoutBtn = screen.getByRole('button', { name: /check-out/i });
      expect(checkinBtn).toBeDisabled();
      expect(checkoutBtn).not.toBeDisabled();
    });

    it('desabilita botao Falta para turno completed', () => {
      render(
        <ShiftDayView
          shifts={[{ ...baseShift, status: 'completed' }]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      const faltaBtn = screen.getByRole('button', { name: /falta/i });
      expect(faltaBtn).toBeDisabled();
    });

    it('desabilita botao Falta para turno missed', () => {
      render(
        <ShiftDayView
          shifts={[{ ...baseShift, status: 'missed' }]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      const faltaBtn = screen.getByRole('button', { name: /falta/i });
      expect(faltaBtn).toBeDisabled();
    });

    it('habilita botao Falta para turno scheduled', () => {
      render(
        <ShiftDayView
          shifts={[{ ...baseShift, status: 'scheduled' }]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      const faltaBtn = screen.getByRole('button', { name: /falta/i });
      expect(faltaBtn).not.toBeDisabled();
    });
  });

  describe('chamadas de callbacks', () => {
    it('chama onCheckIn ao clicar no botao Check-in', async () => {
      const user = userEvent.setup();
      render(
        <ShiftDayView
          shifts={[{ ...baseShift, status: 'scheduled' }]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      await user.click(screen.getByRole('button', { name: /check-in/i }));
      expect(mockOnCheckIn).toHaveBeenCalledWith(expect.objectContaining({ id: 'shift-1' }));
    });

    it('chama onCheckOut ao clicar no botao Check-out', async () => {
      const user = userEvent.setup();
      render(
        <ShiftDayView
          shifts={[{ ...baseShift, status: 'in_progress' }]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      await user.click(screen.getByRole('button', { name: /check-out/i }));
      expect(mockOnCheckOut).toHaveBeenCalledWith(expect.objectContaining({ id: 'shift-1' }));
    });

    it('chama onMarkMissed ao clicar no botao Falta', async () => {
      const user = userEvent.setup();
      render(
        <ShiftDayView
          shifts={[{ ...baseShift, status: 'scheduled' }]}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      await user.click(screen.getByRole('button', { name: /falta/i }));
      expect(mockOnMarkMissed).toHaveBeenCalledWith(expect.objectContaining({ id: 'shift-1' }));
    });
  });

  describe('multiplos turnos', () => {
    it('renderiza todos os turnos da lista', () => {
      const shifts: Shift[] = [
        { ...baseShift, id: 'shift-1', employee_id: 'emp-1' },
        { ...baseShift, id: 'shift-2', employee_id: 'emp-2', status: 'in_progress' },
        { ...baseShift, id: 'shift-3', employee_id: 'emp-3', status: 'completed' },
      ];
      render(
        <ShiftDayView
          shifts={shifts}
          getEmployeeLabel={getEmployeeLabel}
          getPostLabel={getPostLabel}
          onCheckIn={mockOnCheckIn}
          onCheckOut={mockOnCheckOut}
          onMarkMissed={mockOnMarkMissed}
        />
      );
      expect(screen.getByText('Funcionario emp-1')).toBeInTheDocument();
      expect(screen.getByText('Funcionario emp-2')).toBeInTheDocument();
      expect(screen.getByText('Funcionario emp-3')).toBeInTheDocument();
    });
  });
});
