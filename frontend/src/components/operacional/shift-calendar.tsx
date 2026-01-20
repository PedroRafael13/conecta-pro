'use client';

import { useMemo } from 'react';
import { CalendarDays, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { Shift } from '@/types/operacional';

interface ShiftCalendarProps {
  shifts: Shift[];
  selectedDate: Date;
  onSelectDate: (date: Date) => void;
  view: 'month' | 'week';
  onViewChange: (view: 'month' | 'week') => void;
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

export function ShiftCalendar({
  shifts,
  selectedDate,
  onSelectDate,
  view,
  onViewChange,
}: ShiftCalendarProps) {
  const days = useMemo(() => {
    const start = view === 'week' ? startOfWeek(selectedDate) : startOfMonthGrid(selectedDate);
    const totalDays = view === 'week' ? 7 : 42;
    return Array.from({ length: totalDays }, (_, i) => addDays(start, i));
  }, [selectedDate, view]);

  const shiftCount = useMemo(() => {
    const map = new Map<string, number>();
    shifts.forEach((shift) => {
      const key = shift.shift_date;
      map.set(key, (map.get(key) || 0) + 1);
    });
    return map;
  }, [shifts]);

  const headerLabel = useMemo(() => {
    return selectedDate.toLocaleDateString('pt-BR', {
      month: 'long',
      year: 'numeric',
    });
  }, [selectedDate]);

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

      <div className="grid grid-cols-7 gap-2 text-xs text-[hsl(var(--muted-foreground))] mb-2">
        {WEEK_DAYS.map((day) => (
          <div key={day} className="text-center">
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-2">
        {days.map((day) => {
          const key = toLocalDateKey(day);
          const count = shiftCount.get(key) || 0;
          const isSelected = sameDay(day, selectedDate);
          const isCurrentMonth = day.getMonth() === selectedDate.getMonth();

          return (
            <button
              key={key}
              type="button"
              onClick={() => onSelectDate(day)}
              className={`rounded-lg border p-2 text-left transition-colors ${
                isSelected
                  ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/10'
                  : 'border-[hsl(var(--border))] hover:border-[hsl(var(--primary))]'
              } ${isCurrentMonth ? '' : 'opacity-60'}`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {day.getDate()}
                </span>
                {count > 0 && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-blue-500/10 text-blue-500">
                    {count}
                  </span>
                )}
              </div>
              {count > 0 && (
                <p className="mt-1 text-[10px] text-[hsl(var(--muted-foreground))]">
                  {count} turno(s)
                </p>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
