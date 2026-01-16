import React from 'react';
import {
  Calendar,
  Clock,
  Users,
  AlertTriangle,
  Plus,
} from 'lucide-react';
import { ScheduleCalendar, ConflictList, useSchedules } from '@/modules/operations';

export function SchedulingPage() {
  const { schedules, conflicts } = useSchedules();
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Calendar className="h-7 w-7 text-conecta-escuro" />
            Escalas e Agendamentos
          </h1>
          <p className="text-gray-600 mt-1">
            Gerenciamento de escalas, turnos e agendamentos
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
          <Plus className="h-4 w-4" />
          Nova Escala
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Calendar className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Escalas Ativas</p>
              <p className="text-xl font-bold text-gray-900">45</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Users className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Colaboradores</p>
              <p className="text-xl font-bold text-gray-900">128</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Clock className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Turnos Hoje</p>
              <p className="text-xl font-bold text-gray-900">32</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Conflitos</p>
              <p className="text-xl font-bold text-gray-900">3</p>
            </div>
          </div>
        </div>
      </div>

      {/* Calendar */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <ScheduleCalendar schedules={schedules} />
      </div>

      {/* Conflicts */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-yellow-600" />
          Conflitos Pendentes
        </h2>
        <ConflictList conflicts={conflicts} />
      </div>
    </div>
  );
}

export default SchedulingPage;
