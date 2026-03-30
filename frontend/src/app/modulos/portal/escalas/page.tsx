'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  CalendarDays,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  MapPin,
  Clock,
  Sunrise,
  Moon,
  Sun,
  ArrowRight,
} from 'lucide-react'

const API_BASE = '/api/v1/people-management/portal'

function getAuthHeaders() {
  const token =
    typeof window !== 'undefined'
      ? localStorage.getItem('access_token') || localStorage.getItem('token')
      : null
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

interface Shift {
  date?: string
  start_time?: string
  end_time?: string
  workplace?: string
  status?: string
}

interface ScheduleData {
  employee_name?: string
  month?: number
  year?: number
  shifts?: Shift[]
  total_hours?: number
  escala_padrao?: string
  turno_padrao?: string
  carga_horaria_semanal?: number
  jornada_trabalho?: string
  cargo?: string
  posto_atual_nome?: string
}

interface NextShift {
  date?: string
  start_time?: string
  end_time?: string
  workplace?: string
  status?: string
}

const MESES = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
]

function getShiftIcon(start?: string) {
  if (!start) return Sun
  const h = parseInt(start.split(':')[0] ?? '12')
  if (h >= 6 && h < 14) return Sunrise
  if (h >= 14 && h < 22) return Sun
  return Moon
}

function formatTime(t?: string) {
  if (!t) return '—'
  return t.slice(0, 5)
}

export default function EscalasPortalPage() {
  const now = new Date()
  const [mes, setMes] = useState(now.getMonth() + 1)
  const [ano, setAno] = useState(now.getFullYear())
  const [schedule, setSchedule] = useState<ScheduleData | null>(null)
  const [nextShift, setNextShift] = useState<NextShift | null>(null)
  const [loading, setLoading] = useState(true)

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [schedRes, nextRes] = await Promise.allSettled([
        fetch(`${API_BASE}/my-schedules?month=${mes}&year=${ano}`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE}/my-schedules/next-shift`, { headers: getAuthHeaders() }),
      ])

      if (schedRes.status === 'fulfilled' && schedRes.value.ok) {
        setSchedule(await schedRes.value.json())
      }
      if (nextRes.status === 'fulfilled' && nextRes.value.ok) {
        setNextShift(await nextRes.value.json())
      } else {
        setNextShift(null)
      }
    } catch {
      /* silencioso */
    } finally {
      setLoading(false)
    }
  }, [mes, ano])

  useEffect(() => { loadData() }, [loadData])

  const navMes = (dir: -1 | 1) => {
    let newMes = mes + dir
    let newAno = ano
    if (newMes < 1) { newMes = 12; newAno -= 1 }
    if (newMes > 12) { newMes = 1; newAno += 1 }
    if (newAno < 2020 || newAno > 2030) return
    setMes(newMes)
    setAno(newAno)
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2].map((i) => (
          <div key={i} className="bg-white rounded-xl p-6 shadow-sm animate-pulse">
            <div className="h-5 bg-gray-100 rounded w-1/3 mb-4" />
            <div className="h-32 bg-gray-50 rounded" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <CalendarDays className="w-6 h-6 text-blue-600" />
            Minha Escala
          </h1>
          <button
            onClick={loadData}
            className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <RefreshCw className="w-4 h-4" /> Atualizar
          </button>
        </div>

        {/* Dados da escala */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-blue-50 rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-blue-600">{schedule?.escala_padrao || '—'}</p>
            <p className="text-xs text-blue-500">Escala Padrão</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-purple-600">{schedule?.carga_horaria_semanal ? `${schedule.carga_horaria_semanal}h` : '—'}</p>
            <p className="text-xs text-purple-500">Carga Semanal</p>
          </div>
          <div className="bg-green-50 rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-green-600">{schedule?.total_hours ? `${schedule.total_hours.toFixed(0)}h` : '—'}</p>
            <p className="text-xs text-green-500">Horas no Mês</p>
          </div>
          <div className="bg-amber-50 rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-amber-600">{schedule?.shifts?.length ?? 0}</p>
            <p className="text-xs text-amber-500">Turnos Escalados</p>
          </div>
        </div>

        {/* Posto e cargo */}
        {(schedule?.posto_atual_nome || schedule?.cargo) && (
          <div className="mt-3 flex flex-wrap gap-2">
            {schedule.posto_atual_nome && (
              <span className="flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                <MapPin className="w-3.5 h-3.5" /> {schedule.posto_atual_nome}
              </span>
            )}
            {schedule.cargo && (
              <span className="flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                <Clock className="w-3.5 h-3.5" /> {schedule.cargo}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Próximo turno */}
      {nextShift && (
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl p-5 text-white shadow-sm">
          <p className="text-blue-200 text-sm font-medium mb-1">Próximo Turno</p>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xl font-bold">
                {nextShift.date
                  ? new Date(nextShift.date).toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long' })
                  : '—'}
              </p>
              <p className="text-blue-200 flex items-center gap-1 mt-1">
                <Clock className="w-4 h-4" />
                {formatTime(nextShift.start_time)} → {formatTime(nextShift.end_time)}
              </p>
              {nextShift.workplace && (
                <p className="text-blue-200 flex items-center gap-1 mt-0.5">
                  <MapPin className="w-4 h-4" /> {nextShift.workplace}
                </p>
              )}
            </div>
            <ArrowRight className="w-8 h-8 text-blue-300" />
          </div>
        </div>
      )}

      {/* Grade mensal */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="flex items-center justify-between border-b px-6 py-3">
          <button onClick={() => navMes(-1)} className="p-1.5 rounded-lg hover:bg-gray-100">
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </button>
          <span className="font-semibold text-gray-800">
            {MESES[mes - 1]} {ano}
          </span>
          <button
            onClick={() => navMes(1)}
            disabled={mes === now.getMonth() + 1 && ano === now.getFullYear()}
            className="p-1.5 rounded-lg hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronRight className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        <div className="p-4">
          {!schedule?.shifts || schedule.shifts.length === 0 ? (
            <div className="text-center py-12">
              <CalendarDays className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">Nenhum turno escalado neste mês</p>
              <p className="text-sm text-gray-400 mt-1">
                A escala é gerenciada pelo supervisor — entre em contato para informações.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {schedule.shifts.map((shift, i) => {
                const ShiftIcon = getShiftIcon(shift.start_time)
                const isToday = shift.date === now.toISOString().slice(0, 10)
                return (
                  <div
                    key={i}
                    className={`flex items-center justify-between p-3 rounded-lg border ${
                      isToday
                        ? 'bg-blue-50 border-blue-200'
                        : 'bg-gray-50 border-transparent'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${
                        isToday ? 'bg-blue-100' : 'bg-white shadow-sm'
                      }`}>
                        <ShiftIcon className={`w-4 h-4 ${isToday ? 'text-blue-600' : 'text-gray-500'}`} />
                      </div>
                      <div>
                        <p className={`text-sm font-medium ${isToday ? 'text-blue-800' : 'text-gray-800'}`}>
                          {shift.date
                            ? new Date(shift.date).toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: '2-digit' })
                            : '—'}
                          {isToday && <span className="ml-2 text-xs text-blue-600 font-semibold">HOJE</span>}
                        </p>
                        {shift.workplace && (
                          <p className="text-xs text-gray-500 flex items-center gap-1">
                            <MapPin className="w-3 h-3" /> {shift.workplace}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-700">
                        {formatTime(shift.start_time)} → {formatTime(shift.end_time)}
                      </p>
                      {shift.status && (
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          shift.status === 'concluido'
                            ? 'bg-green-100 text-green-700'
                            : shift.status === 'em_andamento'
                              ? 'bg-blue-100 text-blue-700'
                              : 'bg-gray-100 text-gray-600'
                        }`}>
                          {shift.status.replace('_', ' ')}
                        </span>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
