'use client';

import { Calendar, Plus, Edit2, Trash2, User, Clock, AlertCircle, ChevronLeft, ChevronRight } from 'lucide-react';
import { useState, useMemo, useCallback } from 'react';
;
import { Button } from '@/components/ui/button';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Input } from '@/components/ui/input';
import { useShiftOperations } from '@/hooks/useShifts';
import type {
  Shift,
  ShiftCreate,
  ShiftUpdate,
  ShiftStatus,
  Employee,
  Scale,
} from '@/types/operacional';
import { SHIFT_STATUS_LABELS } from '@/types/operacional';

interface ScaleEditorProps {
  scale: Scale;
  shifts: Shift[];
  employees: Employee[];
  onRefresh: () => void;
}

interface ShiftEditData {
  shift?: Shift;
  date: string;
  employeeId: string | null;
}

const WEEK_DAYS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab'];

export function ScaleEditor({ scale, shifts, employees, onRefresh }: ScaleEditorProps) {
  const { createShift, updateShift, deleteShift, isLoading } = useShiftOperations();

  // Modal states
  const [showEditModal, setShowEditModal] = useState(false);
  const [editData, setEditData] = useState<ShiftEditData | null>(null);
  const [formData, setFormData] = useState({
    planned_start_time: '07:00',
    planned_end_time: '19:00',
    planned_break_minutes: 60,
    is_off_day: false,
    notes: '',
  });

  // Gerar dias do mês
  const monthDays = useMemo(() => {
    const year = scale.year;
    const month = scale.month - 1;
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const days: Date[] = [];

    for (let d = 1; d <= lastDay.getDate(); d++) {
      days.push(new Date(year, month, d));
    }

    return days;
  }, [scale.month, scale.year]);

  // Mapear turnos por funcionário e data
  const shiftsMap = useMemo(() => {
    const map = new Map<string, Shift>();
    shifts.forEach((shift) => {
      const key = `${shift.employee_id}_${shift.shift_date}`;
      map.set(key, shift);
    });
    return map;
  }, [shifts]);

  // Funcionários únicos com turnos na escala
  const scaleEmployees = useMemo(() => {
    const employeeIds = new Set(shifts.map((s) => s.employee_id).filter(Boolean));
    return employees.filter((emp) => employeeIds.has(emp.id));
  }, [shifts, employees]);

  // Função para obter turno
  const getShift = (employeeId: string, date: Date): Shift | undefined => {
    const dateStr = date.toISOString().split('T')[0];
    return shiftsMap.get(`${employeeId}_${dateStr}`);
  };

  // Função para formatar data
  const formatDate = (date: Date): string => {
    return date.toISOString().split('T')[0];
  };

  // Função para obter cor do status
  const getStatusColor = (status: ShiftStatus): string => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 border-green-500/50 text-green-700 dark:text-green-300';
      case 'scheduled':
        return 'bg-blue-500/20 border-blue-500/50 text-blue-700 dark:text-blue-300';
      case 'in_progress':
        return 'bg-cyan-500/20 border-cyan-500/50 text-cyan-700 dark:text-cyan-300';
      case 'missed':
        return 'bg-red-500/20 border-red-500/50 text-red-700 dark:text-red-300';
      case 'off_day':
        return 'bg-gray-500/20 border-gray-500/50 text-gray-700 dark:text-gray-300';
      case 'substituted':
        return 'bg-orange-500/20 border-orange-500/50 text-orange-700 dark:text-orange-300';
      case 'cancelled':
        return 'bg-red-300/20 border-red-300/50 text-red-600 dark:text-red-400';
      default:
        return 'bg-gray-400/20 border-gray-400/50 text-gray-600 dark:text-gray-400';
    }
  };

  // Abrir modal para criar/editar turno
  const handleCellClick = (employeeId: string, date: Date) => {
    const shift = getShift(employeeId, date);
    const dateStr = formatDate(date);

    if (shift) {
      // Editar turno existente
      setEditData({ shift, date: dateStr, employeeId });
      setFormData({
        planned_start_time: shift.planned_start_time.substring(0, 5),
        planned_end_time: shift.planned_end_time.substring(0, 5),
        planned_break_minutes: shift.planned_break_minutes,
        is_off_day: shift.is_off_day,
        notes: shift.notes || '',
      });
    } else {
      // Criar novo turno
      setEditData({ date: dateStr, employeeId });
      setFormData({
        planned_start_time: '07:00',
        planned_end_time: '19:00',
        planned_break_minutes: 60,
        is_off_day: false,
        notes: '',
      });
    }
    setShowEditModal(true);
  };

  // Salvar turno
  const handleSave = async () => {
    if (!editData) return;

    const baseData = {
      planned_start_time: `${formData.planned_start_time}:00`,
      planned_end_time: `${formData.planned_end_time}:00`,
      planned_break_minutes: formData.planned_break_minutes,
      is_off_day: formData.is_off_day,
      notes: formData.notes || null,
    };

    if (editData.shift) {
      // Atualizar turno existente
      const updated = await updateShift(editData.shift.id, baseData);
      if (updated) {
        setShowEditModal(false);
        onRefresh();
      }
    } else {
      // Criar novo turno
      const createData: ShiftCreate = {
        ...baseData,
        scale_id: scale.id,
        post_id: scale.post_id,
        employee_id: editData.employeeId || null,
        shift_date: editData.date,
      };
      const created = await createShift(createData);
      if (created) {
        setShowEditModal(false);
        onRefresh();
      }
    }
  };

  // Deletar turno
  const handleDelete = async () => {
    if (!editData?.shift) return;
    const success = await deleteShift(editData.shift.id);
    if (success) {
      setShowEditModal(false);
      onRefresh();
    }
  };

  // Obter nome do funcionário
  const getEmployeeName = (empId: string): string => {
    const emp = employees.find((e) => e.id === empId);
    return emp?.full_name || emp?.name || emp?.email || 'Sem nome';
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-[hsl(var(--primary))]" />
          <h2 className="text-lg font-semibold text-[hsl(var(--foreground))]">
            Editor de Turnos - {scale.month}/{scale.year}
          </h2>
        </div>
        <div className="text-sm text-[hsl(var(--muted-foreground))]">
          {shifts.length} turnos • {scaleEmployees.length} funcionários
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-2 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded border bg-blue-500/20 border-blue-500/50" />
          <span className="text-[hsl(var(--muted-foreground))]">Agendado</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded border bg-green-500/20 border-green-500/50" />
          <span className="text-[hsl(var(--muted-foreground))]">Concluído</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded border bg-red-500/20 border-red-500/50" />
          <span className="text-[hsl(var(--muted-foreground))]">Falta</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded border bg-gray-500/20 border-gray-500/50" />
          <span className="text-[hsl(var(--muted-foreground))]">Folga</span>
        </div>
      </div>

      {/* Grid Container */}
      <div className="overflow-x-auto border border-[hsl(var(--border))] rounded-lg">
        <div className="min-w-max">
          {/* Header com dias */}
          <div className="grid grid-cols-[200px_repeat(auto-fit,minmax(60px,1fr))] bg-[hsl(var(--muted))]/30 border-b border-[hsl(var(--border))]">
            <div className="p-2 font-medium text-sm sticky left-0 bg-[hsl(var(--muted))]/30 border-r border-[hsl(var(--border))]">
              Funcionário
            </div>
            {monthDays.map((day) => (
              <div
                key={day.toISOString()}
                className="p-2 text-center text-xs border-r border-[hsl(var(--border))] last:border-r-0"
              >
                <div className="font-medium">{day.getDate()}</div>
                <div className="text-[hsl(var(--muted-foreground))]">
                  {WEEK_DAYS[day.getDay()]}
                </div>
              </div>
            ))}
          </div>

          {/* Linhas de funcionários */}
          {scaleEmployees.length === 0 ? (
            <div className="p-8 text-center text-[hsl(var(--muted-foreground))]">
              <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>Nenhum funcionário alocado nesta escala</p>
            </div>
          ) : (
            scaleEmployees.map((employee) => (
              <div
                key={employee.id}
                className="grid grid-cols-[200px_repeat(auto-fit,minmax(60px,1fr))] border-b border-[hsl(var(--border))] last:border-b-0"
              >
                {/* Nome do funcionário */}
                <div className="p-2 sticky left-0 bg-[hsl(var(--card))] border-r border-[hsl(var(--border))] flex items-center gap-2">
                  <User className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                  <span className="text-sm truncate">{getEmployeeName(employee.id)}</span>
                </div>

                {/* Células de turnos */}
                {monthDays.map((day) => {
                  const shift = getShift(employee.id, day);
                  const isWeekend = day.getDay() === 0 || day.getDay() === 6;

                  return (
                    <button
                      key={`${employee.id}_${day.toISOString()}`}
                      onClick={() => handleCellClick(employee.id, day)}
                      className={`
                        p-1 text-xs border-r border-[hsl(var(--border))] last:border-r-0
                        hover:bg-[hsl(var(--muted))]/50 transition-colors
                        ${isWeekend ? 'bg-[hsl(var(--muted))]/20' : ''}
                        ${shift ? getStatusColor(shift.status) : ''}
                      `}
                    >
                      {shift ? (
                        <div className="flex flex-col items-center justify-center min-h-[40px]">
                          <Clock className="w-3 h-3 mb-0.5" />
                          <span className="font-medium">
                            {shift.planned_start_time.substring(0, 5)}
                          </span>
                          {shift.is_off_day && <span className="text-[10px]">Folga</span>}
                        </div>
                      ) : (
                        <div className="flex items-center justify-center min-h-[40px] opacity-30 hover:opacity-100">
                          <Plus className="w-3 h-3" />
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Edit Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        title={editData?.shift ? 'Editar Turno' : 'Criar Turno'}
        size="md"
      >
        <div className="space-y-4">
          {/* Info */}
          <div className="bg-[hsl(var(--muted))]/30 rounded-lg p-3 text-sm">
            <div className="font-medium mb-1">
              {editData && getEmployeeName(editData.employeeId || '')}
            </div>
            <div className="text-[hsl(var(--muted-foreground))]">
              Data: {editData?.date ? new Date(editData.date + 'T12:00:00').toLocaleDateString('pt-BR') : ''}
            </div>
          </div>

          {/* Form */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Início
              </label>
              <Input
                type="time"
                value={formData.planned_start_time}
                onChange={(e) => setFormData({ ...formData, planned_start_time: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Fim
              </label>
              <Input
                type="time"
                value={formData.planned_end_time}
                onChange={(e) => setFormData({ ...formData, planned_end_time: e.target.value })}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Intervalo (minutos)
            </label>
            <Input
              type="number"
              min="0"
              max="120"
              value={formData.planned_break_minutes}
              onChange={(e) => setFormData({ ...formData, planned_break_minutes: Number(e.target.value) })}
            />
          </div>

          <div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={formData.is_off_day}
                onChange={(e) => setFormData({ ...formData, is_off_day: e.target.checked })}
                className="rounded border-[hsl(var(--border))]"
              />
              <span>Marcar como folga</span>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Observações
            </label>
            <textarea
              className="w-full min-h-[80px] px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm resize-none"
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="Observações sobre o turno..."
            />
          </div>
        </div>

        <ModalFooter>
          <div className="flex items-center justify-between w-full">
            <div>
              {editData?.shift && (
                <Button
                  variant="ghost"
                  className="text-red-500 hover:text-red-600"
                  onClick={handleDelete}
                  disabled={isLoading}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Excluir
                </Button>
              )}
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setShowEditModal(false)} disabled={isLoading}>
                Cancelar
              </Button>
              <Button onClick={handleSave} disabled={isLoading}>
                {isLoading ? 'Salvando...' : 'Salvar'}
              </Button>
            </div>
          </div>
        </ModalFooter>
      </Modal>
    </div>
  );
}
