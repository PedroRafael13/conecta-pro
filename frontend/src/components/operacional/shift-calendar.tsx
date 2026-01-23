'use client';

import { useMemo, useState } from 'react';
import { CalendarDays, ChevronLeft, ChevronRight, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { Shift } from '@/types/operacional';

interface ShiftCalendarProps {
  shifts: Shift[];
  selectedDate: Date;
  onSelectDate: (date: Date) => void;
  view: 'month' | 'week';
  onViewChange: (view: 'month' | 'week') => void;
  employeeMap?: Record<string, { full_name?: string | null; name?: string | null; email?: string | null }>;
}

const WEEK_DAYS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab'];
const TIMEZONE = 'America/Manaus';

const startOfWeek = (date: Date) => {
  const d = new Date(date);
  d.setDate(d.getDate() - d.getDay());
  d.setHours(0, 0, 0, 0);
  return d;
};

const startOfMonthGrid = (date: Date) => {
  const first = new Date(date.getFullYear(), date.getMonth(), 1);
  return startOfWeek(first);
};

const addDays = (date: Date, days: number) => {
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return d;
};

const toLocalDateKey = (date: Date) => {
  return new Intl.DateTimeFormat('en-CA', { timeZone: TIMEZONE }).format(date);
};

const sameDay = (a: Date, b: Date) =>
  a.getFullYear() === b.getFullYear() &&
  a.getMonth() === b.getMonth() &&
  a.getDate() === b.getDate();

// Funcao para determinar cor do status
const getStatusColor = (status: Shift['status']) => {
  switch (status) {
    case 'completed':
      return 'bg-green-500/20 border-green-500/30 text-green-600 dark:text-green-400';
    case 'scheduled':
    case 'in_progress':
      return 'bg-yellow-500/20 border-yellow-500/30 text-yellow-600 dark:text-yellow-400';
    case 'missed':
      return 'bg-red-500/20 border-red-500/30 text-red-600 dark:text-red-400';
    case 'substituted':
    case 'partial':
      return 'bg-orange-500/20 border-orange-500/30 text-orange-600 dark:text-orange-400';
    case 'cancelled':
    case 'off_day':
      return 'bg-gray-500/20 border-gray-500/30 text-gray-600 dark:text-gray-400';
    default:
      return 'bg-blue-500/20 border-blue-500/30 text-blue-600 dark:text-blue-400';
  }
};

// Interface para estatisticas do dia
interface DayStats {
  total: number;
  completed: number;
  scheduled: number;
  missed: number;
  needsSubstitution: number;
  shifts: Shift[];
}

export function ShiftCalendar({
  shifts,
  selectedDate,
  onSelectDate,
  view,
  onViewChange,
  employeeMap = {},
}: ShiftCalendarProps) {
  const [hoveredDay, setHoveredDay] = useState<string | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

  const days = useMemo(() => {
    const start = view === 'week' ? startOfWeek(selectedDate) : startOfMonthGrid(selectedDate);
    const totalDays = view === 'week' ? 7 : 42;
    return Array.from({ length: totalDays }, (_, i) => addDays(start, i));
  }, [selectedDate, view]);

  // Mapa com estatisticas por dia
  const dayStatsMap = useMemo(() => {
    const map = new Map<string, DayStats>();
    shifts.forEach((shift) => {
      const key = shift.shift_date;
      const stats = map.get(key) || {
        total: 0,
        completed: 0,
        scheduled: 0,
        missed: 0,
        needsSubstitution: 0,
        shifts: [],
      };

      stats.total++;
      stats.shifts.push(shift);

      if (shift.status === 'completed') stats.completed++;
      if (shift.status === 'scheduled' || shift.status === 'in_progress') stats.scheduled++;
      if (shift.status === 'missed') stats.missed++;
      if (shift.needs_substitution) stats.needsSubstitution++;

      map.set(key, stats);
    });
    return map;
  }, [shifts]);

  const headerLabel = useMemo(() => {
    return selectedDate.toLocaleDateString('pt-BR', {
      month: 'long',
      year: 'numeric',
    });
  }, [selectedDate]);

  const getEmployeeName = (employeeId: string | null) => {
    if (!employeeId) return 'Sem funcionario';
    const employee = employeeMap[employeeId];
    if (!employee) return 'Funcionario desconhecido';
    return employee.full_name || employee.name || employee.email || employeeId;
  };

  const handleMouseEnter = (event: React.MouseEvent, key: string) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltipPosition({ x: rect.left, y: rect.bottom + 5 });
    setHoveredDay(key);
  };

  return (
    <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2 text-[hsl(var(--foreground))]">
          <CalendarDays className="w-4 h-4" />
          <span className="font-medium capitalize">{headerLabel}</span>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={view === 'month' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => onViewChange('month')}
          >
            Mes
          </Button>
          <Button
            variant={view === 'week' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => onViewChange('week')}
          >
            Semana
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="w-8 px-0"
            onClick={() => onSelectDate(addDays(selectedDate, view === 'week' ? -7 : -30))}
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="w-8 px-0"
            onClick={() => onSelectDate(addDays(selectedDate, view === 'week' ? 7 : 30))}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Legenda de cores */}
      <div className="mb-4 flex flex-wrap gap-3 text-[10px] p-2 bg-[hsl(var(--background))] rounded-lg">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-green-500/30 border border-green-500/50"></div>
          <span className="text-[hsl(var(--muted-foreground))]">Trabalhado</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-yellow-500/30 border border-yellow-500/50"></div>
          <span className="text-[hsl(var(--muted-foreground))]">Agendado</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-red-500/30 border border-red-500/50"></div>
          <span className="text-[hsl(var(--muted-foreground))]">Falta</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-orange-500/30 border border-orange-500/50"></div>
          <span className="text-[hsl(var(--muted-foreground))]">Substituicao</span>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-2 text-xs text-[hsl(var(--muted-foreground))] mb-2">
        {WEEK_DAYS.map((day) => (
          <div key={day} className="text-center">
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-2 relative">
        {days.map((day) => {
          const key = toLocalDateKey(day);
          const stats = dayStatsMap.get(key);
          const isSelected = sameDay(day, selectedDate);
          const isCurrentMonth = day.getMonth() === selectedDate.getMonth();
          const isHovered = hoveredDay === key;

          return (
            <button
              key={key}
              type="button"
              onClick={() => onSelectDate(day)}
              onMouseEnter={(e) => stats && handleMouseEnter(e, key)}
              onMouseLeave={() => setHoveredDay(null)}
              className={`rounded-lg border p-2 text-left transition-colors min-h-[80px] ${
                isSelected
                  ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/10'
                  : 'border-[hsl(var(--border))] hover:border-[hsl(var(--primary))]'
              } ${isCurrentMonth ? '' : 'opacity-60'}`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-[hsl(var(--foreground))]">
                  {day.getDate()}
                </span>
                {stats && stats.total > 0 && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-blue-500/10 text-blue-500 font-medium">
                    {stats.total}
                  </span>
                )}
              </div>

              {stats && stats.total > 0 && (
                <div className="space-y-1">
                  {/* Contadores de status */}
                  <div className="flex flex-wrap gap-1 text-[9px]">
                    {stats.completed > 0 && (
                      <span className="px-1 py-0.5 rounded bg-green-500/20 text-green-600 dark:text-green-400">
                        {stats.completed}
                      </span>
                    )}
                    {stats.scheduled > 0 && (
                      <span className="px-1 py-0.5 rounded bg-yellow-500/20 text-yellow-600 dark:text-yellow-400">
                        {stats.scheduled}
                      </span>
                    )}
                    {stats.missed > 0 && (
                      <span className="px-1 py-0.5 rounded bg-red-500/20 text-red-600 dark:text-red-400">
                        {stats.missed}
                      </span>
                    )}
                    {stats.needsSubstitution > 0 && (
                      <span className="px-1 py-0.5 rounded bg-orange-500/20 text-orange-600 dark:text-orange-400">
                        {stats.needsSubstitution}
                      </span>
                    )}
                  </div>

                  {/* Preview dos primeiros turnos */}
                  <div className="space-y-0.5">
                    {stats.shifts.slice(0, 2).map((shift) => (
                      <div
                        key={shift.id}
                        className={`text-[9px] px-1 py-0.5 rounded border truncate ${getStatusColor(
                          shift.status
                        )}`}
                        title={getEmployeeName(shift.employee_id)}
                      >
                        {getEmployeeName(shift.employee_id).split(' ')[0]}
                      </div>
                    ))}
                    {stats.shifts.length > 2 && (
                      <div className="text-[9px] text-[hsl(var(--muted-foreground))] px-1">
                        +{stats.shifts.length - 2} mais
                      </div>
                    )}
                  </div>
                </div>
              )}
            </button>
          );
        })}

        {/* Tooltip com detalhes */}
        {hoveredDay && dayStatsMap.get(hoveredDay) && (
          <div
            className="fixed z-50 bg-[hsl(var(--popover))] border border-[hsl(var(--border))] rounded-lg p-3 shadow-lg max-w-xs"
            style={{
              left: `${tooltipPosition.x}px`,
              top: `${tooltipPosition.y}px`,
            }}
          >
            <div className="space-y-2">
              <div className="flex items-center gap-2 pb-2 border-b border-[hsl(var(--border))]">
                <Info className="w-4 h-4 text-[hsl(var(--primary))]" />
                <span className="font-semibold text-sm text-[hsl(var(--foreground))]">
                  Detalhes do dia
                </span>
              </div>

              {(() => {
                const stats = dayStatsMap.get(hoveredDay)!;
                return (
                  <>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="text-[hsl(var(--muted-foreground))]">Total:</span>
                        <span className="ml-1 font-medium">{stats.total}</span>
                      </div>
                      <div>
                        <span className="text-green-600 dark:text-green-400">Trabalhados:</span>
                        <span className="ml-1 font-medium">{stats.completed}</span>
                      </div>
                      <div>
                        <span className="text-yellow-600 dark:text-yellow-400">Agendados:</span>
                        <span className="ml-1 font-medium">{stats.scheduled}</span>
                      </div>
                      <div>
                        <span className="text-red-600 dark:text-red-400">Faltas:</span>
                        <span className="ml-1 font-medium">{stats.missed}</span>
                      </div>
                      {stats.needsSubstitution > 0 && (
                        <div className="col-span-2">
                          <span className="text-orange-600 dark:text-orange-400">
                            Precisam substituicao:
                          </span>
                          <span className="ml-1 font-medium">{stats.needsSubstitution}</span>
                        </div>
                      )}
                    </div>

                    <div className="pt-2 border-t border-[hsl(var(--border))]">
                      <div className="text-xs font-medium text-[hsl(var(--muted-foreground))] mb-1">
                        Funcionarios:
                      </div>
                      <div className="space-y-1 max-h-32 overflow-y-auto">
                        {stats.shifts.map((shift) => (
                          <div
                            key={shift.id}
                            className={`text-[10px] px-2 py-1 rounded border ${getStatusColor(
                              shift.status
                            )}`}
                          >
                            <div className="font-medium">{getEmployeeName(shift.employee_id)}</div>
                            <div className="text-[9px] opacity-70">
                              {shift.planned_start_time.substring(0, 5)} -{' '}
                              {shift.planned_end_time.substring(0, 5)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                );
              })()}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
