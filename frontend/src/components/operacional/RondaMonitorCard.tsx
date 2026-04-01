'use client';

import { Shield, AlertCircle, Play, Pause, Clock, MapPin } from 'lucide-react';

interface RondaMonitorCardProps {
  round: {
    id: string;
    code: string;
    inspector_name: string;
    inspector_role: string;
    status: 'em_andamento' | 'pausada' | string;
    progress_percentage: number;
    total_checkpoints: number;
    total_occurrences: number;
    started_at: string | null;
    scheduled_date: string | null;
    duration_minutes: number | null;
  };
  onClick: () => void;
}

function computeElapsed(started_at: string | null): string | null {
  if (!started_at) return null;
  const diffMs = Date.now() - new Date(started_at).getTime();
  if (diffMs < 0) return null;
  const totalMinutes = Math.floor(diffMs / 60_000);
  const hours = Math.floor(totalMinutes / 60);
  const mins = totalMinutes % 60;
  if (hours > 0) return `${hours}h ${mins}min`;
  return `${mins}min`;
}

function getProgressColor(pct: number): string {
  if (pct >= 80) return 'bg-green-500';
  if (pct >= 50) return 'bg-orange-500';
  return 'bg-red-500';
}

export function RondaMonitorCard({ round, onClick }: RondaMonitorCardProps) {
  const isActive = round.status === 'em_andamento';
  const elapsed = computeElapsed(round.started_at);
  const progressColor = getProgressColor(round.progress_percentage);

  const borderExtra = isActive ? 'border-green-500/30' : '';

  return (
    <div
      className={`bg-[hsl(var(--card))] border border-[hsl(var(--border))] ${borderExtra} rounded-xl p-4 cursor-pointer hover:border-[hsl(var(--primary))]/50 transition-all`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onClick(); }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-mono font-semibold text-[hsl(var(--foreground))]">
          {round.code}
        </span>
        <div className="flex items-center gap-1.5">
          {isActive ? (
            <>
              <span className="inline-block w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="inline-flex items-center gap-1 text-xs font-medium text-green-500">
                <Play className="w-3 h-3" />
                Em Andamento
              </span>
            </>
          ) : (
            <>
              <span className="inline-block w-2 h-2 rounded-full bg-yellow-500" />
              <span className="inline-flex items-center gap-1 text-xs font-medium text-yellow-500">
                <Pause className="w-3 h-3" />
                Pausada
              </span>
            </>
          )}
        </div>
      </div>

      {/* Inspector */}
      <div className="mb-3">
        <p className="text-sm font-medium text-[hsl(var(--foreground))]">
          {round.inspector_name}
        </p>
        <p className="text-xs text-[hsl(var(--muted-foreground))]">
          {round.inspector_role}
        </p>
      </div>

      {/* Progress bar */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-[hsl(var(--muted-foreground))]">Progresso</span>
          <span className="text-xs font-semibold text-[hsl(var(--foreground))]">
            {round.progress_percentage}%
          </span>
        </div>
        <div className="w-full h-2 rounded-full bg-[hsl(var(--muted))]">
          <div
            className={`h-2 rounded-full transition-all ${progressColor}`}
            style={{ width: `${Math.min(100, Math.max(0, round.progress_percentage))}%` }}
          />
        </div>
      </div>

      {/* Stats row */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1 text-xs text-[hsl(var(--muted-foreground))]">
          <Shield className="w-3.5 h-3.5" />
          <span>{round.total_checkpoints} checkpoints</span>
        </div>
        <div className="flex items-center gap-1 text-xs text-[hsl(var(--muted-foreground))]">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>{round.total_occurrences} ocorrências</span>
        </div>
      </div>

      {/* Time elapsed */}
      {elapsed && (
        <div className="flex items-center gap-1 mt-2 text-xs text-[hsl(var(--muted-foreground))]">
          <Clock className="w-3.5 h-3.5" />
          <span>Há {elapsed}</span>
        </div>
      )}
    </div>
  );
}
