'use client';

import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeft,
  ChevronRight,
  Wrench,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import type { MaintenanceCalendarEvent, MaintenanceType, MaintenancePriority, MaintenanceStatus } from '../types/maintenance.types';

interface MaintenanceCalendarProps {
  events: MaintenanceCalendarEvent[];
  onSelectEvent?: (event: MaintenanceCalendarEvent) => void;
  onDateChange?: (startDate: string, endDate: string) => void;
}

const typeColors: Record<MaintenanceType, string> = {
  preventiva: 'bg-blue-500',
  corretiva: 'bg-orange-500',
  preditiva: 'bg-purple-500'
};

const priorityBorder: Record<MaintenancePriority, string> = {
  urgente: 'border-l-red-500',
  alta: 'border-l-orange-500',
  normal: 'border-l-blue-500',
  baixa: 'border-l-gray-500'
};

const statusOpacity: Record<MaintenanceStatus, string> = {
  agendada: 'opacity-100',
  em_execucao: 'opacity-100',
  concluida: 'opacity-60',
  cancelada: 'opacity-40 line-through',
  atrasada: 'opacity-100'
};

export function MaintenanceCalendar({
  events,
  onSelectEvent,
  onDateChange
}: MaintenanceCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  // Gerar dias do mes
  const calendarDays = useMemo(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);

    const days: Array<{
      date: Date;
      isCurrentMonth: boolean;
      isToday: boolean;
      events: MaintenanceCalendarEvent[];
    }> = [];

    // Dias do mes anterior
    const firstDayOfWeek = firstDay.getDay();
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
      const date = new Date(year, month, -i);
      days.push({
        date,
        isCurrentMonth: false,
        isToday: false,
        events: []
      });
    }

    // Dias do mes atual
    const today = new Date();
    for (let day = 1; day <= lastDay.getDate(); day++) {
      const date = new Date(year, month, day);
      const dateStr = date.toISOString().split('T')[0];
      const dayEvents = events.filter(e => e.date === dateStr);

      days.push({
        date,
        isCurrentMonth: true,
        isToday: date.toDateString() === today.toDateString(),
        events: dayEvents
      });
    }

    // Dias do proximo mes para completar a grid
    const remainingDays = 42 - days.length;
    for (let i = 1; i <= remainingDays; i++) {
      const date = new Date(year, month + 1, i);
      days.push({
        date,
        isCurrentMonth: false,
        isToday: false,
        events: []
      });
    }

    return days;
  }, [currentDate, events]);

  // Eventos do dia selecionado
  const selectedDayEvents = useMemo(() => {
    if (!selectedDate) return [];
    const dateStr = selectedDate.toISOString().split('T')[0];
    return events.filter(e => e.date === dateStr);
  }, [selectedDate, events]);

  const goToPreviousMonth = () => {
    const newDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1);
    setCurrentDate(newDate);
    notifyDateChange(newDate);
  };

  const goToNextMonth = () => {
    const newDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1);
    setCurrentDate(newDate);
    notifyDateChange(newDate);
  };

  const goToToday = () => {
    const today = new Date();
    setCurrentDate(today);
    setSelectedDate(today);
    notifyDateChange(today);
  };

  const notifyDateChange = (date: Date) => {
    if (onDateChange) {
      const startDate = new Date(date.getFullYear(), date.getMonth(), 1).toISOString().split('T')[0];
      const endDate = new Date(date.getFullYear(), date.getMonth() + 1, 0).toISOString().split('T')[0];
      onDateChange(startDate, endDate);
    }
  };

  const formatMonthYear = (date: Date) => {
    return date.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
  };

  const weekDays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab'];

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={goToPreviousMonth}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
            <h2 className="text-lg font-semibold text-gray-900 capitalize min-w-[180px] text-center">
              {formatMonthYear(currentDate)}
            </h2>
            <button
              onClick={goToNextMonth}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
          </div>

          <button
            onClick={goToToday}
            className="px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            Hoje
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="p-4">
        {/* Week days header */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {weekDays.map(day => (
            <div key={day} className="text-center text-xs font-medium text-gray-500 py-2">
              {day}
            </div>
          ))}
        </div>

        {/* Days grid */}
        <div className="grid grid-cols-7 gap-1">
          {calendarDays.map(({ date, isCurrentMonth, isToday, events: dayEvents }, index) => (
            <motion.button
              key={index}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.01 }}
              onClick={() => setSelectedDate(date)}
              className={`
                relative min-h-[80px] p-1 text-left rounded-lg transition-all
                ${isCurrentMonth ? 'bg-white hover:bg-gray-50' : 'bg-gray-50'}
                ${selectedDate?.toDateString() === date.toDateString() ? 'ring-2 ring-blue-500' : ''}
                ${isToday ? 'bg-blue-50' : ''}
              `}
            >
              <span className={`
                text-sm font-medium
                ${isCurrentMonth ? 'text-gray-900' : 'text-gray-400'}
                ${isToday ? 'text-blue-600' : ''}
              `}>
                {date.getDate()}
              </span>

              {/* Events indicators */}
              {dayEvents.length > 0 && (
                <div className="mt-1 space-y-0.5">
                  {dayEvents.slice(0, 3).map((event, i) => (
                    <div
                      key={i}
                      className={`
                        text-xs truncate px-1 py-0.5 rounded
                        ${typeColors[event.tipo]} text-white
                        ${statusOpacity[event.status]}
                      `}
                      title={event.title}
                    >
                      {event.title.split(' - ')[0]}
                    </div>
                  ))}
                  {dayEvents.length > 3 && (
                    <div className="text-xs text-gray-500 px-1">
                      +{dayEvents.length - 3} mais
                    </div>
                  )}
                </div>
              )}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Selected Day Events Panel */}
      <AnimatePresence>
        {selectedDate && selectedDayEvents.length > 0 && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-gray-200 overflow-hidden"
          >
            <div className="p-4 bg-gray-50">
              <h3 className="text-sm font-medium text-gray-900 mb-3">
                {selectedDate.toLocaleDateString('pt-BR', {
                  weekday: 'long',
                  day: 'numeric',
                  month: 'long'
                })}
              </h3>
              <div className="space-y-2">
                {selectedDayEvents.map((event) => (
                  <button
                    key={event.id}
                    onClick={() => onSelectEvent?.(event)}
                    className={`
                      w-full flex items-center justify-between p-3 bg-white rounded-lg border-l-4
                      ${priorityBorder[event.prioridade]} hover:shadow-sm transition-all
                    `}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-2 h-2 rounded-full ${typeColors[event.tipo]}`} />
                      <div className="text-left">
                        <p className="text-sm font-medium text-gray-900">{event.title}</p>
                        <p className="text-xs text-gray-500">{event.equipment_nome}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {event.status === 'concluida' && (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      )}
                      {event.status === 'atrasada' && (
                        <AlertTriangle className="w-4 h-4 text-red-500" />
                      )}
                      {event.status === 'em_execucao' && (
                        <Wrench className="w-4 h-4 text-yellow-500" />
                      )}
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Legend */}
      <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-center space-x-6">
          <div className="flex items-center space-x-1.5">
            <div className="w-3 h-3 rounded bg-blue-500" />
            <span className="text-xs text-gray-600">Preventiva</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <div className="w-3 h-3 rounded bg-orange-500" />
            <span className="text-xs text-gray-600">Corretiva</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <div className="w-3 h-3 rounded bg-purple-500" />
            <span className="text-xs text-gray-600">Preditiva</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Mini calendario para widgets
interface MiniCalendarProps {
  events: MaintenanceCalendarEvent[];
  onSelectDate?: (date: Date) => void;
}

export function MiniCalendar({ events, onSelectDate }: MiniCalendarProps) {
  const today = new Date();
  const weekStart = new Date(today);
  weekStart.setDate(today.getDate() - today.getDay());

  const weekDays = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(weekStart);
    date.setDate(weekStart.getDate() + i);
    return date;
  });

  const getEventCount = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return events.filter(e => e.date === dateStr).length;
  };

  return (
    <div className="flex items-center space-x-2">
      {weekDays.map((date, index) => {
        const count = getEventCount(date);
        const isToday = date.toDateString() === today.toDateString();

        return (
          <button
            key={index}
            onClick={() => onSelectDate?.(date)}
            className={`
              flex flex-col items-center p-2 rounded-lg transition-colors
              ${isToday ? 'bg-blue-100' : 'hover:bg-gray-100'}
            `}
          >
            <span className="text-xs text-gray-500">
              {date.toLocaleDateString('pt-BR', { weekday: 'short' }).slice(0, 3)}
            </span>
            <span className={`text-sm font-medium ${isToday ? 'text-blue-600' : 'text-gray-900'}`}>
              {date.getDate()}
            </span>
            {count > 0 && (
              <span className="mt-1 w-5 h-5 flex items-center justify-center text-xs font-medium bg-blue-500 text-white rounded-full">
                {count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

export default MaintenanceCalendar;
