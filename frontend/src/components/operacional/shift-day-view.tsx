'use client';

import { Clock, User, MapPin, AlertCircle, CheckCircle, Ban } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { Shift, ShiftStatus } from '@/types/operacional';
import { SHIFT_STATUS_LABELS } from '@/types/operacional';

interface ShiftDayViewProps {
  shifts: Shift[];
  getEmployeeLabel: (employeeId: string | null) => string;
  getPostLabel: (postId: string) => string;
  onCheckIn: (shift: Shift) => void;
  onCheckOut: (shift: Shift) => void;
  onMarkMissed: (shift: Shift) => void;
}

const getStatusBadge = (status: ShiftStatus) => {
  const base = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium';
  switch (status) {
    case 'completed':
      return `${base} bg-green-500/10 text-green-500`;
    case 'in_progress':
      return `${base} bg-blue-500/10 text-blue-500`;
    case 'missed':
      return `${base} bg-red-500/10 text-red-500`;
    case 'cancelled':
      return `${base} bg-gray-500/10 text-gray-500`;
    case 'partial':
      return `${base} bg-orange-500/10 text-orange-500`;
    case 'off_day':
      return `${base} bg-slate-500/10 text-slate-500`;
    default:
      return `${base} bg-yellow-500/10 text-yellow-500`;
  }
};

const formatTime = (value?: string | null) => {
  if (!value) return '-';
  const timePart = value.includes('T') ? (value.split('T')[1] ?? value) : value;
  const clean = timePart.split(/[Z+-]/)[0] ?? timePart;
  const [hours, minutes] = clean.split(':');
  if (!hours || !minutes) return value;
  return `${hours}:${minutes}`;
};

export function ShiftDayView({
  shifts,
  getEmployeeLabel,
  getPostLabel,
  onCheckIn,
  onCheckOut,
  onMarkMissed,
}: ShiftDayViewProps) {
  if (shifts.length === 0) {
    return (
      <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-6 text-center">
        <Clock className="w-10 h-10 text-[hsl(var(--muted-foreground))] mx-auto mb-3" />
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Nenhum turno encontrado para este dia
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {shifts.map((shift) => (
        <div
          key={shift.id}
          className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4"
        >
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className={getStatusBadge(shift.status)}>
                  {SHIFT_STATUS_LABELS[shift.status] || shift.status}
                </span>
                {shift.is_off_day && (
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">Folga</span>
                )}
              </div>
              <div className="flex items-center gap-2 text-sm text-[hsl(var(--foreground))]">
                <Clock className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                {formatTime(shift.planned_start_time)} - {formatTime(shift.planned_end_time)}
              </div>
              <div className="flex items-center gap-2 text-xs text-[hsl(var(--muted-foreground))] mt-1">
                <User className="w-3.5 h-3.5" />
                {getEmployeeLabel(shift.employee_id)}
              </div>
              <div className="flex items-center gap-2 text-xs text-[hsl(var(--muted-foreground))] mt-1">
                <MapPin className="w-3.5 h-3.5" />
                {getPostLabel(shift.post_id)}
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onCheckIn(shift)}
                disabled={shift.status !== 'scheduled'}
              >
                <CheckCircle className="w-3.5 h-3.5 mr-1" />
                Check-in
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onCheckOut(shift)}
                disabled={shift.status !== 'in_progress'}
              >
                <Clock className="w-3.5 h-3.5 mr-1" />
                Check-out
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="text-red-500 hover:text-red-600"
                onClick={() => onMarkMissed(shift)}
                disabled={shift.status === 'completed' || shift.status === 'missed'}
              >
                <Ban className="w-3.5 h-3.5 mr-1" />
                Falta
              </Button>
            </div>
          </div>
          {shift.actual_start_time && (
            <div className="mt-3 text-xs text-[hsl(var(--muted-foreground))] flex items-center gap-2">
              <AlertCircle className="w-3.5 h-3.5" />
              Inicio real: {formatTime(shift.actual_start_time)}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
