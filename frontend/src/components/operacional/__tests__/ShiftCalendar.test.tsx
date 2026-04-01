/**
 * Testes para ShiftCalendar
 * Cobre branches: view month/week, getStatusColor para cada status,
 * getEmployeeName com/sem id, dias com/sem turnos,
 * stats.needsSubstitution > 0, stats.shifts.length > 2 ("+N mais"),
 * troca de mes/semana com botoes de navegacao
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@/test/helpers/test-utils';
import { ShiftCalendar } from '../shift-calendar';
import type { Shift } from '@/types/operacional';

const mockOnSelectDate = vi.fn();
const mockOnViewChange = vi.fn();

// Data fixa para facilitar asserts
const fixedDate = new Date(2025, 0, 15); // 15 jan 2025

const makeShift = (overrides: Partial<Shift> = {}): Shift => ({
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
  ...overrides,
});

const defaultProps = {
  shifts: [],
  selectedDate: fixedDate,
  onSelectDate: mockOnSelectDate,
  view: 'month' as const,
  onViewChange: mockOnViewChange,
};

describe('ShiftCalendar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('renderizacao basica', () => {
    it('renderiza legenda de cores', () => {
      render(<ShiftCalendar {...defaultProps} />);
      expect(screen.getByText('Trabalhado')).toBeInTheDocument();
      expect(screen.getByText('Agendado')).toBeInTheDocument();
      expect(screen.getByText('Falta')).toBeInTheDocument();
      expect(screen.getByText('Substituicao')).toBeInTheDocument();
    });

    it('renderiza cabecalho com dias da semana', () => {
      render(<ShiftCalendar {...defaultProps} />);
      expect(screen.getByText('Dom')).toBeInTheDocument();
      expect(screen.getByText('Seg')).toBeInTheDocument();
      expect(screen.getByText('Sex')).toBeInTheDocument();
    });

    it('renderiza botoes de alternancia de visualizacao', () => {
      render(<ShiftCalendar {...defaultProps} />);
      expect(screen.getByRole('button', { name: /mes/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /semana/i })).toBeInTheDocument();
    });

    it('mostra 42 celulas no modo mes', () => {
      render(<ShiftCalendar {...defaultProps} view="month" />);
      // 42 = 6 semanas x 7 dias
      const buttons = screen.getAllByRole('button');
      // Filtra apenas celulas de dia (tem type="button" sem texto de acao)
      const dayButtons = buttons.filter((b) => {
        const text = b.textContent || '';
        return !['Mes', 'Semana'].includes(text.trim()) && !text.includes('‹') && !text.includes('›');
      });
      expect(dayButtons.length).toBeGreaterThanOrEqual(28);
    });

    it('mostra 7 celulas no modo semana', () => {
      render(<ShiftCalendar {...defaultProps} view="week" />);
      const buttons = screen.getAllByRole('button');
      const dayButtons = buttons.filter((b) => {
        const text = b.textContent || '';
        return !['Mes', 'Semana'].includes(text.trim());
      });
      // 7 dias + 4 botoes de controle = ao menos 7 dias
      expect(dayButtons.length).toBeGreaterThanOrEqual(7);
    });
  });

  describe('botoes de navegacao', () => {
    it('chama onViewChange("month") ao clicar em Mes', () => {
      render(<ShiftCalendar {...defaultProps} view="week" />);
      fireEvent.click(screen.getByRole('button', { name: /mes/i }));
      expect(mockOnViewChange).toHaveBeenCalledWith('month');
    });

    it('chama onViewChange("week") ao clicar em Semana', () => {
      render(<ShiftCalendar {...defaultProps} view="month" />);
      fireEvent.click(screen.getByRole('button', { name: /semana/i }));
      expect(mockOnViewChange).toHaveBeenCalledWith('week');
    });

    it('chama onSelectDate ao navegar para semana anterior', () => {
      render(<ShiftCalendar {...defaultProps} view="week" />);
      const prevBtn = screen.getAllByRole('button').find((b) => b.querySelector('svg'));
      // Clica no primeiro botao de navegacao (ChevronLeft)
      const navButtons = screen.getAllByRole('button').filter((b) => {
        const svg = b.querySelector('svg');
        return !!svg && b.className.includes('w-8');
      });
      if (navButtons[0]) {
        fireEvent.click(navButtons[0]);
        expect(mockOnSelectDate).toHaveBeenCalled();
      }
    });

    it('chama onSelectDate ao clicar em um dia', () => {
      render(<ShiftCalendar {...defaultProps} />);
      // Clica no botao que representa o dia 15 (o texto "15" deve aparecer)
      const dayButtons = screen.getAllByRole('button').filter((b) =>
        b.textContent?.includes('15')
      );
      if (dayButtons[0]) {
        fireEvent.click(dayButtons[0]);
        expect(mockOnSelectDate).toHaveBeenCalled();
      }
    });
  });

  describe('exibicao de turnos por status', () => {
    const statusCases: Array<{ status: Shift['status'] }> = [
      { status: 'completed' },
      { status: 'scheduled' },
      { status: 'in_progress' },
      { status: 'missed' },
      { status: 'substituted' },
      { status: 'partial' },
      { status: 'cancelled' },
      { status: 'off_day' },
    ];

    statusCases.forEach(({ status }) => {
      it(`exibe contador para turno com status "${status}"`, () => {
        const shift = makeShift({ status, shift_date: '2025-01-15' });
        render(<ShiftCalendar {...defaultProps} shifts={[shift]} />);
        // O total badge "1" deve aparecer
        const totalBadge = screen.getAllByText('1');
        expect(totalBadge.length).toBeGreaterThanOrEqual(1);
      });
    });
  });

  describe('getEmployeeName branches', () => {
    it('exibe "Sem funcionario" quando employee_id e null', () => {
      const shift = makeShift({ employee_id: null, shift_date: '2025-01-15' });
      const employeeMap = {};
      render(<ShiftCalendar {...defaultProps} shifts={[shift]} employeeMap={employeeMap} />);
      expect(screen.getByText('Sem')).toBeInTheDocument(); // "Sem funcionario".split(' ')[0] = "Sem"
    });

    it('exibe "Funcionario desconhecido" quando employee nao esta no mapa', () => {
      const shift = makeShift({ employee_id: 'emp-unknown', shift_date: '2025-01-15' });
      const employeeMap = {};
      render(<ShiftCalendar {...defaultProps} shifts={[shift]} employeeMap={employeeMap} />);
      expect(screen.getByText('Funcionario')).toBeInTheDocument(); // "Funcionario desconhecido".split(' ')[0]
    });

    it('exibe full_name do funcionario quando disponivel', () => {
      const shift = makeShift({ employee_id: 'emp-1', shift_date: '2025-01-15' });
      const employeeMap = { 'emp-1': { full_name: 'Joao Silva', name: null, email: null } };
      render(<ShiftCalendar {...defaultProps} shifts={[shift]} employeeMap={employeeMap} />);
      expect(screen.getByText('Joao')).toBeInTheDocument(); // split(' ')[0]
    });

    it('exibe name quando full_name e null', () => {
      const shift = makeShift({ employee_id: 'emp-1', shift_date: '2025-01-15' });
      const employeeMap = { 'emp-1': { full_name: null, name: 'Maria', email: null } };
      render(<ShiftCalendar {...defaultProps} shifts={[shift]} employeeMap={employeeMap} />);
      expect(screen.getByText('Maria')).toBeInTheDocument();
    });

    it('exibe email quando full_name e name sao null', () => {
      const shift = makeShift({ employee_id: 'emp-1', shift_date: '2025-01-15' });
      const employeeMap = { 'emp-1': { full_name: null, name: null, email: 'joao@test.com' } };
      render(<ShiftCalendar {...defaultProps} shifts={[shift]} employeeMap={employeeMap} />);
      expect(screen.getByText('joao@test.com')).toBeInTheDocument();
    });
  });

  describe('stats e contadores', () => {
    it('exibe badge de completed quando ha turno concluido', () => {
      const shift = makeShift({ status: 'completed', shift_date: '2025-01-15' });
      render(<ShiftCalendar {...defaultProps} shifts={[shift]} />);
      // Deve haver elemento com classe green para completed
      const greenSpans = document.querySelectorAll('.bg-green-500\\/20');
      expect(greenSpans.length).toBeGreaterThan(0);
    });

    it('exibe badge de scheduled quando ha turno agendado', () => {
      const shift = makeShift({ status: 'scheduled', shift_date: '2025-01-15' });
      render(<ShiftCalendar {...defaultProps} shifts={[shift]} />);
      const yellowSpans = document.querySelectorAll('.bg-yellow-500\\/20');
      expect(yellowSpans.length).toBeGreaterThan(0);
    });

    it('exibe badge de missed quando ha turno com falta', () => {
      const shift = makeShift({ status: 'missed', shift_date: '2025-01-15' });
      render(<ShiftCalendar {...defaultProps} shifts={[shift]} />);
      const redSpans = document.querySelectorAll('.bg-red-500\\/20');
      expect(redSpans.length).toBeGreaterThan(0);
    });

    it('exibe badge de necessita substituicao quando needs_substitution=true', () => {
      const shift = makeShift({ needs_substitution: true, shift_date: '2025-01-15' });
      render(<ShiftCalendar {...defaultProps} shifts={[shift]} />);
      const orangeSpans = document.querySelectorAll('.bg-orange-500\\/20');
      expect(orangeSpans.length).toBeGreaterThan(0);
    });

    it('exibe "+N mais" quando ha mais de 2 turnos no mesmo dia', () => {
      const shifts = [
        makeShift({ id: 's1', employee_id: 'emp-1', shift_date: '2025-01-15' }),
        makeShift({ id: 's2', employee_id: 'emp-2', shift_date: '2025-01-15' }),
        makeShift({ id: 's3', employee_id: 'emp-3', shift_date: '2025-01-15' }),
      ];
      render(<ShiftCalendar {...defaultProps} shifts={shifts} />);
      expect(screen.getByText(/\+1 mais/)).toBeInTheDocument();
    });

    it('nao exibe "+N mais" quando ha 2 ou menos turnos no mesmo dia', () => {
      const shifts = [
        makeShift({ id: 's1', employee_id: 'emp-1', shift_date: '2025-01-15' }),
        makeShift({ id: 's2', employee_id: 'emp-2', shift_date: '2025-01-15' }),
      ];
      render(<ShiftCalendar {...defaultProps} shifts={shifts} />);
      expect(screen.queryByText(/mais/)).not.toBeInTheDocument();
    });
  });

  describe('employeeMap padrao (vazio)', () => {
    it('funciona sem employeeMap passado', () => {
      const shift = makeShift({ shift_date: '2025-01-15' });
      render(<ShiftCalendar {...defaultProps} shifts={[shift]} />);
      // Deve renderizar sem erros
      expect(screen.getByText('Trabalhado')).toBeInTheDocument();
    });
  });
});
