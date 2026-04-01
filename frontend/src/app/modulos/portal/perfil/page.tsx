'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  User,
  Briefcase,
  Calendar,
  MapPin,
  Phone,
  Mail,
  Clock,
  FileText,
  RefreshCw,
  Shield,
  Building2,
  ChevronRight,
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

interface PerfilData {
  employee_id?: string
  nome?: string
  cargo?: string
  data_admissao?: string
  escala?: string
  turno?: string
  posto?: string
  departamento?: string
  email?: string
  telefone?: string
  status?: string
  matricula?: string
}

interface ContratoData {
  employee_id?: string
  tipo_contrato?: string
  regime_trabalho?: string
  carga_horaria_semanal?: number
  jornada?: string
  data_admissao?: string
  posto_trabalho?: string
  cliente?: string
  salario_base?: number
  salario_conforme_cct?: boolean
  piso_cct_cargo?: number
  cct_vigente?: string
}

export default function PerfilPortalPage() {
  const [perfil, setPerfil] = useState<PerfilData | null>(null)
  const [contrato, setContrato] = useState<ContratoData | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'perfil' | 'contrato'>('perfil')

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [perfilRes, contratoRes] = await Promise.allSettled([
        fetch(`${API_BASE}/perfil`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE}/contrato`, { headers: getAuthHeaders() }),
      ])

      if (perfilRes.status === 'fulfilled' && perfilRes.value.ok) {
        setPerfil(await perfilRes.value.json())
      }
      if (contratoRes.status === 'fulfilled' && contratoRes.value.ok) {
        setContrato(await contratoRes.value.json())
      }
    } catch {
      /* silencioso */
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2].map((i) => (
          <div key={i} className="bg-white rounded-xl p-6 shadow-sm animate-pulse">
            <div className="h-5 bg-gray-100 rounded w-1/4 mb-4" />
            <div className="grid grid-cols-2 gap-3">
              {[1, 2, 3, 4].map((j) => (
                <div key={j} className="h-14 bg-gray-50 rounded" />
              ))}
            </div>
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
            <User className="w-6 h-6 text-blue-600" />
            Meu Perfil
          </h1>
          <button
            onClick={loadData}
            className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <RefreshCw className="w-4 h-4" /> Atualizar
          </button>
        </div>

        {/* Avatar e nome */}
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-2xl font-bold">
            {(perfil?.nome ?? 'F').charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{perfil?.nome || '—'}</h2>
            <p className="text-sm text-gray-500">{perfil?.cargo || '—'}</p>
            <span className={`inline-flex items-center gap-1 mt-1 px-2 py-0.5 rounded-full text-xs font-medium ${
              perfil?.status === 'ativo'
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-600'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${perfil?.status === 'ativo' ? 'bg-green-500' : 'bg-gray-400'}`} />
              {perfil?.status || 'ativo'}
            </span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="flex border-b px-4 pt-3">
          {([
            { key: 'perfil', label: 'Dados Pessoais', icon: User },
            { key: 'contrato', label: 'Dados Contratuais', icon: FileText },
          ] as const).map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {/* Tab: Perfil */}
          {activeTab === 'perfil' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InfoCard icon={User} label="Nome completo" value={perfil?.nome} />
              <InfoCard icon={Briefcase} label="Cargo" value={perfil?.cargo} />
              <InfoCard icon={Calendar} label="Data de admissão" value={formatDate(perfil?.data_admissao)} />
              <InfoCard icon={Building2} label="Departamento" value={perfil?.departamento} />
              <InfoCard icon={MapPin} label="Posto atual" value={perfil?.posto} />
              <InfoCard icon={Clock} label="Escala" value={perfil?.escala} />
              <InfoCard icon={Clock} label="Turno padrão" value={perfil?.turno} />
              <InfoCard icon={FileText} label="Matrícula" value={perfil?.matricula} />
              <InfoCard icon={Mail} label="E-mail" value={perfil?.email} />
              <InfoCard icon={Phone} label="Telefone" value={perfil?.telefone} />
            </div>
          )}

          {/* Tab: Contrato */}
          {activeTab === 'contrato' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <InfoCard icon={FileText} label="Tipo de contrato" value={contrato?.tipo_contrato} />
                <InfoCard icon={Briefcase} label="Regime de trabalho" value={contrato?.regime_trabalho} />
                <InfoCard icon={Clock} label="Carga horária semanal" value={contrato?.carga_horaria_semanal ? `${contrato.carga_horaria_semanal}h` : undefined} />
                <InfoCard icon={Clock} label="Jornada" value={contrato?.jornada} />
                <InfoCard icon={Calendar} label="Data de admissão" value={formatDate(contrato?.data_admissao)} />
                <InfoCard icon={MapPin} label="Posto de trabalho" value={contrato?.posto_trabalho} />
                <InfoCard icon={Building2} label="Cliente" value={contrato?.cliente} />
              </div>

              {/* CCT e Salário */}
              {contrato?.cct_vigente && (
                <div className="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-100">
                  <div className="flex items-center gap-2 mb-3">
                    <Shield className="w-5 h-5 text-blue-600" />
                    <span className="font-semibold text-blue-800">Convenção Coletiva de Trabalho</span>
                  </div>
                  <p className="text-sm text-blue-700 font-medium mb-3">{contrato.cct_vigente}</p>

                  {contrato.salario_base !== undefined && (
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="bg-white rounded-lg p-3">
                        <p className="text-gray-500 text-xs">Salário Base</p>
                        <p className="font-bold text-gray-900 text-lg">
                          {formatCurrency(contrato.salario_base)}
                        </p>
                      </div>
                      <div className="bg-white rounded-lg p-3">
                        <p className="text-gray-500 text-xs">Piso CCT (cargo)</p>
                        <p className="font-bold text-gray-900 text-lg">
                          {formatCurrency(contrato.piso_cct_cargo || 0)}
                        </p>
                      </div>
                    </div>
                  )}

                  {contrato.salario_conforme_cct !== undefined && (
                    <div className={`mt-3 flex items-center gap-2 text-sm px-3 py-2 rounded-lg ${
                      contrato.salario_conforme_cct
                        ? 'bg-green-50 text-green-700'
                        : 'bg-red-50 text-red-700'
                    }`}>
                      <Shield className="w-4 h-4" />
                      {contrato.salario_conforme_cct
                        ? 'Salário conforme o piso CCT'
                        : 'Salário abaixo do piso CCT — reportar ao DP'}
                    </div>
                  )}
                </div>
              )}

              <div className="flex items-center gap-2 text-xs text-gray-500 mt-2">
                <ChevronRight className="w-3 h-3" />
                Para informações detalhadas sobre a CCT, acesse{' '}
                <a href="/modulos/portal/cct" className="text-blue-600 hover:underline font-medium">
                  Direitos CCT
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function InfoCard({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType
  label: string
  value?: string | number | null
}) {
  return (
    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
      <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center shadow-sm flex-shrink-0">
        <Icon className="w-4 h-4 text-blue-500" />
      </div>
      <div className="min-w-0">
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-sm font-medium text-gray-900 truncate">{value || '—'}</p>
      </div>
    </div>
  )
}

function formatDate(dateStr?: string | null): string | undefined {
  if (!dateStr || dateStr === 'None' || dateStr === 'null') return undefined
  try {
    return new Date(dateStr).toLocaleDateString('pt-BR')
  } catch {
    return dateStr
  }
}

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}
