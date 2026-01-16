import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeft,
  ChevronRight,
  Calendar,
  Clock,
  User,
  MapPin,
  Filter,
  Plus,
  LayoutGrid,
  List,
} from 'lucide-react';
import type { Schedule, ScheduleStatus, WeekDay } from '../types/schedules.types';

interface ScheduleCalendarProps {
  schedules: Schedule[];
  onSelectSchedule?: (schedule: Schedule) => void;
  onSelectDate?: (date: Date) => void;
  onCreateSchedule?: (date: Date) => void;
  view?: 'day' | 'week' | 'month';
  onViewChange?: (view: 'day' | 'week' | 'month') => void;
}

const MESES = [
  'Janeiro',
  'Fevereiro',
  'Marco',
  'Abril',
  'Maio',
  'Junho',
  'Julho',
  'Agosto',
  'Setembro',
  'Outubro',
  'Novembro',
  'Dezembro',
];

const DIAS_SEMANA = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab'];

export const ScheduleCalendar: React.FC<ScheduleCalendarProps> = ({
  schedules,
  onSelectSchedule,
  onSelectDate,
  onCreateSchedule,
  view = 'week',
  onViewChange,
}) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [currentView, setCurrentView] = useState<'day' | 'week' | 'month'>(view);

  const handleViewChange = (newView: 'day' | 'week' | 'month') => {
    setCurrentView(newView);
    onViewChange?.(newView);
  };

  const getStatusConfig = (status: ScheduleStatus) => {
    const configs = {
      confirmado: { color: 'bg-green-500', label: 'Confirmado' },
      pendente: { color: 'bg-yellow-500', label: 'Pendente' },
      cancelado: { color: 'bg-red-500', label: 'Cancelado' },
      em_andamento: { color: 'bg-blue-500', label: 'Em Andamento' },
      concluido: { color: 'bg-gray-400', label: 'Concluido' },
      falta: { color: 'bg-red-600', label: 'Falta' },
      substituido: { color: 'bg-purple-500', label: 'Substituido' },
    };
    return configs[status] || configs.pendente;
  };

  // Navegar entre periodos
  const navigatePeriod = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (currentView === 'day') {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 1 : -1));
    } else if (currentView === 'week') {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7));
    } else {
      newDate.setMonth(newDate.getMonth() + (direction === 'next' ? 1 : -1));
    }
    setCurrentDate(newDate);
  };

  const goToToday = () => setCurrentDate(new Date());

  // Gerar dias da semana
  const weekDays = useMemo((): WeekDay[] => {
    const days: WeekDay[] = [];
    const startOfWeek = new Date(currentDate);
    startOfWeek.setDate(currentDate.getDate() - currentDate.getDay());

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let i = 0; i < 7; i++) {
      const date = new Date(startOfWeek);
      date.setDate(startOfWeek.getDate() + i);
      date.setHours(0, 0, 0, 0);

      const dateStr = date.toISOString().split('T')[0];
      const daySchedules = schedules.filter((s) => s.data === dateStr);

      days.push({
        date,
        dayName: DIAS_SEMANA[date.getDay()],
        dayNumber: date.getDate(),
        isToday: date.getTime() === today.getTime(),
        isWeekend: date.getDay() === 0 || date.getDay() === 6,
        schedules: daySchedules,
      });
    }

    return days;
  }, [currentDate, schedules]);

  // Gerar dias do mes
  const monthDays = useMemo(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);

    const days: { date: Date; isCurrentMonth: boolean; schedules: Schedule[] }[] = [];

    // Dias do mes anterior
    const startPadding = firstDay.getDay();
    for (let i = startPadding - 1; i >= 0; i--) {
      const date = new Date(year, month, -i);
      const dateStr = date.toISOString().split('T')[0];
      days.push({
        date,
        isCurrentMonth: false,
        schedules: schedules.filter((s) => s.data === dateStr),
      });
    }

    // Dias do mes atual
    for (let i = 1; i <= lastDay.getDate(); i++) {
      const date = new Date(year, month, i);
      const dateStr = date.toISOString().split('T')[0];
      days.push({
        date,
        isCurrentMonth: true,
        schedules: schedules.filter((s) => s.data === dateStr),
      });
    }

    // Dias do proximo mes
    const endPadding = 42 - days.length;
    for (let i = 1; i <= endPadding; i++) {
      const date = new Date(year, month + 1, i);
      const dateStr = date.toISOString().split('T')[0];
      days.push({
        date,
        isCurrentMonth: false,
        schedules: schedules.filter((s) => s.data === dateStr),
      });
    }

    return days;
  }, [currentDate, schedules]);

  // Titulo do periodo
  const periodTitle = useMemo(() => {
    if (currentView === 'day') {
      return currentDate.toLocaleDateString('pt-BR', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      });
    } else if (currentView === 'week') {
      const start = weekDays[0].date;
      const end = weekDays[6].date;
      if (start.getMonth() === end.getMonth()) {
        return `${start.getDate()} - ${end.getDate()} de ${MESES[start.getMonth()]} ${start.getFullYear()}`;
      }
      return `${start.getDate()} ${MESES[start.getMonth()].slice(0, 3)} - ${end.getDate()} ${MESES[end.getMonth()].slice(0, 3)} ${end.getFullYear()}`;
    }
    return `${MESES[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
  }, [currentView, currentDate, weekDays]);

  // Horarios para visualizacao diaria/semanal
  const hours = Array.from({ length: 24 }, (_, i) => i);

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <button
                onClick={() => navigatePeriod('prev')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-5 h-5 text-gray-600" />
              </button>
              <button
                onClick={() => navigatePeriod('next')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ChevronRight className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            <h2 className="text-lg font-semibold text-gray-900 capitalize">
              {periodTitle}
            </h2>

            <button
              onClick={goToToday}
              className="px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              Hoje
            </button>
          </div>

          <div className="flex items-center gap-3">
            {/* Seletor de Visualizacao */}
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => handleViewChange('day')}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  currentView === 'day'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Calendar className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleViewChange('week')}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  currentView === 'week'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <List className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleViewChange('month')}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  currentView === 'month'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <LayoutGrid className="w-4 h-4" />
              </button>
            </div>

            <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
              <Filter className="w-5 h-5 text-gray-600" />
            </button>

            <button
              onClick={() => onCreateSchedule?.(currentDate)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              <Plus className="w-4 h-4" />
              Nova Escala
            </button>
          </div>
        </div>
      </div>

      {/* Visualizacao Semanal */}
      {currentView === 'week' && (
        <div className="overflow-x-auto">
          <div className="min-w-[800px]">
            {/* Header dos dias */}
            <div className="grid grid-cols-7 border-b border-gray-200">
              {weekDays.map((day) => (
                <div
                  key={day.date.toISOString()}
                  className={`p-3 text-center border-r last:border-r-0 border-gray-200 ${
                    day.isToday ? 'bg-blue-50' : day.isWeekend ? 'bg-gray-50' : ''
                  }`}
                >
                  <p className="text-xs text-gray-500 uppercase">{day.dayName}</p>
                  <p
                    className={`text-lg font-semibold mt-1 ${
                      day.isToday ? 'text-blue-600' : 'text-gray-900'
                    }`}
                  >
                    {day.dayNumber}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {day.schedules.length} escala(s)
                  </p>
                </div>
              ))}
            </div>

            {/* Grid de escalas */}
            <div className="grid grid-cols-7">
              {weekDays.map((day) => (
                <div
                  key={day.date.toISOString()}
                  className={`min-h-[300px] p-2 border-r last:border-r-0 border-gray-200 ${
                    day.isToday ? 'bg-blue-50/30' : day.isWeekend ? 'bg-gray-50/50' : ''
                  }`}
                  onClick={() => onSelectDate?.(day.date)}
                >
                  <div className="space-y-2">
                    <AnimatePresence mode="popLayout">
                      {day.schedules.map((schedule) => {
                        const statusConfig = getStatusConfig(schedule.status);
                        return (
                          <motion.div
                            key={schedule.id}
                            layout
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            onClick={(e) => {
                              e.stopPropagation();
                              onSelectSchedule?.(schedule);
                            }}
                            className="bg-white rounded-lg border border-gray-200 p-2 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <div
                                className={`w-2 h-2 rounded-full ${statusConfig.color}`}
                              />
                              <span className="text-xs font-medium text-gray-900 truncate">
                                {schedule.profissional_nome}
                              </span>
                            </div>
                            <div className="flex items-center gap-1 text-xs text-gray-500">
                              <Clock className="w-3 h-3" />
                              {schedule.horario_inicio} - {schedule.horario_fim}
                            </div>
                            <div className="flex items-center gap-1 text-xs text-gray-400 mt-1 truncate">
                              <MapPin className="w-3 h-3 flex-shrink-0" />
                              <span className="truncate">{schedule.posto_nome}</span>
                            </div>
                          </motion.div>
                        );
                      })}
                    </AnimatePresence>

                    {day.schedules.length === 0 && (
                      <div className="h-full flex items-center justify-center py-8">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onCreateSchedule?.(day.date);
                          }}
                          className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        >
                          <Plus className="w-5 h-5" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Visualizacao Mensal */}
      {currentView === 'month' && (
        <div className="p-4">
          {/* Header dos dias da semana */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {DIAS_SEMANA.map((dia) => (
              <div
                key={dia}
                className="text-center text-xs font-medium text-gray-500 py-2"
              >
                {dia}
              </div>
            ))}
          </div>

          {/* Grid de dias */}
          <div className="grid grid-cols-7 gap-1">
            {monthDays.map((day, index) => {
              const today = new Date();
              today.setHours(0, 0, 0, 0);
              const isToday = day.date.getTime() === today.getTime();

              return (
                <motion.div
                  key={index}
                  whileHover={{ scale: 1.02 }}
                  onClick={() => onSelectDate?.(day.date)}
                  className={`min-h-[100px] p-2 rounded-lg border cursor-pointer transition-colors ${
                    day.isCurrentMonth
                      ? isToday
                        ? 'bg-blue-50 border-blue-200'
                        : 'bg-white border-gray-200 hover:border-blue-300'
                      : 'bg-gray-50 border-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span
                      className={`text-sm font-medium ${
                        day.isCurrentMonth
                          ? isToday
                            ? 'text-blue-600'
                            : 'text-gray-900'
                          : 'text-gray-400'
                      }`}
                    >
                      {day.date.getDate()}
                    </span>
                    {day.schedules.length > 0 && (
                      <span className="text-xs text-gray-400">
                        {day.schedules.length}
                      </span>
                    )}
                  </div>

                  <div className="space-y-1">
                    {day.schedules.slice(0, 3).map((schedule) => {
                      const statusConfig = getStatusConfig(schedule.status);
                      return (
                        <div
                          key={schedule.id}
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectSchedule?.(schedule);
                          }}
                          className={`text-xs px-1.5 py-0.5 rounded ${statusConfig.color} text-white truncate`}
                        >
                          {schedule.profissional_nome.split(' ')[0]}
                        </div>
                      );
                    })}
                    {day.schedules.length > 3 && (
                      <p className="text-xs text-gray-400 text-center">
                        +{day.schedules.length - 3}
                      </p>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {/* Visualizacao Diaria */}
      {currentView === 'day' && (
        <div className="p-4">
          <div className="flex gap-4">
            {/* Coluna de horarios */}
            <div className="w-16 flex-shrink-0">
              {hours.map((hour) => (
                <div
                  key={hour}
                  className="h-16 text-xs text-gray-400 text-right pr-2"
                >
                  {hour.toString().padStart(2, '0')}:00
                </div>
              ))}
            </div>

            {/* Grid de escalas */}
            <div className="flex-1 relative border-l border-gray-200">
              {/* Linhas de hora */}
              {hours.map((hour) => (
                <div
                  key={hour}
                  className="h-16 border-b border-gray-100"
                />
              ))}

              {/* Escalas posicionadas */}
              {schedules
                .filter(
                  (s) => s.data === currentDate.toISOString().split('T')[0]
                )
                .map((schedule) => {
                  const [startHour] = schedule.horario_inicio.split(':').map(Number);
                  const [endHour, endMin] = schedule.horario_fim.split(':').map(Number);
                  const duration = endHour - startHour + endMin / 60;
                  const statusConfig = getStatusConfig(schedule.status);

                  return (
                    <motion.div
                      key={schedule.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      onClick={() => onSelectSchedule?.(schedule)}
                      className={`absolute left-2 right-2 rounded-lg p-3 cursor-pointer ${statusConfig.color} text-white shadow-md`}
                      style={{
                        top: `${startHour * 64}px`,
                        height: `${Math.max(duration * 64 - 4, 48)}px`,
                      }}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <User className="w-4 h-4" />
                        <span className="font-medium text-sm">
                          {schedule.profissional_nome}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 text-xs opacity-90">
                        <Clock className="w-3 h-3" />
                        {schedule.horario_inicio} - {schedule.horario_fim}
                      </div>
                      <div className="flex items-center gap-1 text-xs opacity-90 mt-1">
                        <MapPin className="w-3 h-3" />
                        {schedule.posto_nome}
                      </div>
                    </motion.div>
                  );
                })}
            </div>
          </div>
        </div>
      )}

      {/* Legenda */}
      <div className="px-6 py-3 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center gap-4 text-xs">
          <span className="text-gray-500 font-medium">Status:</span>
          {[
            { status: 'confirmado', color: 'bg-green-500' },
            { status: 'pendente', color: 'bg-yellow-500' },
            { status: 'em_andamento', color: 'bg-blue-500' },
            { status: 'falta', color: 'bg-red-600' },
            { status: 'concluido', color: 'bg-gray-400' },
          ].map((item) => (
            <div key={item.status} className="flex items-center gap-1.5">
              <div className={`w-2.5 h-2.5 rounded-full ${item.color}`} />
              <span className="text-gray-600 capitalize">
                {item.status.replace('_', ' ')}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ScheduleCalendar;
