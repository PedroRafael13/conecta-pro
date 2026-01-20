'use client';

import { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { Shift } from '@/types/operacional';
import { AlertCircle } from 'lucide-react';

interface ShiftCheckModalProps {
  isOpen: boolean;
  onClose: () => void;
  shift: Shift | null;
  mode: 'check-in' | 'check-out' | 'missed';
  onConfirm: (payload: { datetime?: string; breakMinutes?: number; reason?: string; notes?: string }) => void;
  isLoading?: boolean;
  error?: string | null;
}

const TIMEZONE = 'America/Manaus';

const buildDefaultDatetime = () => {
  const now = new Date();
  const formatter = new Intl.DateTimeFormat('sv-SE', {
    timeZone: TIMEZONE,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
  const parts = formatter.formatToParts(now);
  const get = (type: string) => parts.find((part) => part.type === type)?.value || '';
  return `${get('year')}-${get('month')}-${get('day')}T${get('hour')}:${get('minute')}`;
};

export function ShiftCheckModal({
  isOpen,
  onClose,
  shift,
  mode,
  onConfirm,
  isLoading = false,
  error,
}: ShiftCheckModalProps) {
  const [dateTime, setDateTime] = useState(buildDefaultDatetime());
  const [breakMinutes, setBreakMinutes] = useState(0);
  const [reason, setReason] = useState('');
  const [notes, setNotes] = useState('');

  const titleMap = {
    'check-in': 'Registrar Check-in',
    'check-out': 'Registrar Check-out',
    missed: 'Registrar Falta',
  };
  const isMissingDatetime = (mode === 'check-in' || mode === 'check-out') && !dateTime;
  const isMissingReason = mode === 'missed' && reason.trim().length === 0;
  const isConfirmDisabled = isLoading || isMissingDatetime || isMissingReason;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={titleMap[mode]}
      description={shift ? `Turno ${shift.shift_date}` : undefined}
      size="sm"
    >
      <div className="space-y-4">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-500 text-sm flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}

        {(mode === 'check-in' || mode === 'check-out') && (
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Data e hora *
            </label>
            <Input
              type="datetime-local"
              value={dateTime}
              onChange={(e) => setDateTime(e.target.value)}
            />
          </div>
        )}

        {mode === 'check-out' && (
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Intervalo (min)
            </label>
            <Input
              type="number"
              min={0}
              value={breakMinutes}
              onChange={(e) => setBreakMinutes(Number(e.target.value) || 0)}
            />
          </div>
        )}

        {mode === 'missed' && (
          <div>
            <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
              Motivo *
            </label>
            <Input
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Ex: falta justificada"
            />
          </div>
        )}

        <div>
          <label className="block text-sm text-[hsl(var(--muted-foreground))] mb-1">
            Observacoes
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm resize-none"
          />
        </div>
      </div>

      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isLoading}>
          Cancelar
        </Button>
        <Button
          variant="primary"
          onClick={() =>
            onConfirm({
              datetime: dateTime,
              breakMinutes,
              reason: reason.trim(),
              notes,
            })
          }
          disabled={isConfirmDisabled}
        >
          {isLoading ? 'Salvando...' : 'Confirmar'}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
