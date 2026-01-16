import React from 'react';
import {
  Users,
  UserPlus,
  Briefcase,
  Heart,
  Clock,
  Calendar,
  TrendingUp,
  Award,
} from 'lucide-react';

export function HRPage() {
  const stats = {
    totalEmployees: 248,
    activeRecruitments: 12,
    vacancies: 8,
    turnoverRate: 4.2,
    avgTenure: 3.5,
    trainingsThisMonth: 15,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Users className="h-7 w-7 text-conecta-escuro" />
            Recursos Humanos
          </h1>
          <p className="text-gray-600 mt-1">
            Gestao de pessoas, recrutamento e desenvolvimento
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
          <UserPlus className="h-4 w-4" />
          Nova Vaga
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-gray-600">Colaboradores</p>
              <p className="text-xl font-bold text-gray-900">{stats.totalEmployees}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Briefcase className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-gray-600">Vagas Abertas</p>
              <p className="text-xl font-bold text-gray-900">{stats.vacancies}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <UserPlus className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-xs text-gray-600">Processos Ativos</p>
              <p className="text-xl font-bold text-gray-900">{stats.activeRecruitments}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <TrendingUp className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-xs text-gray-600">Turnover</p>
              <p className="text-xl font-bold text-gray-900">{stats.turnoverRate}%</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Clock className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-xs text-gray-600">Tempo Medio</p>
              <p className="text-xl font-bold text-gray-900">{stats.avgTenure} anos</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <Award className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-xs text-gray-600">Treinamentos</p>
              <p className="text-xl font-bold text-gray-900">{stats.trainingsThisMonth}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recruitment Pipeline */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Briefcase className="h-5 w-5 text-conecta-escuro" />
            Pipeline de Recrutamento
          </h2>
          <div className="space-y-3">
            {[
              { stage: 'Triagem', count: 45, color: 'bg-blue-500' },
              { stage: 'Entrevista RH', count: 23, color: 'bg-purple-500' },
              { stage: 'Entrevista Tecnica', count: 12, color: 'bg-orange-500' },
              { stage: 'Proposta', count: 5, color: 'bg-green-500' },
            ].map((item) => (
              <div key={item.stage} className="flex items-center gap-3">
                <span className="w-32 text-sm text-gray-600">{item.stage}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-2">
                  <div
                    className={`${item.color} h-2 rounded-full`}
                    style={{ width: `${(item.count / 45) * 100}%` }}
                  />
                </div>
                <span className="w-8 text-sm font-medium text-gray-900">{item.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Health & Wellbeing */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Heart className="h-5 w-5 text-red-500" />
            Saude e Bem-estar
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600">Exames em Dia</p>
              <p className="text-2xl font-bold text-green-600">92%</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">Afastamentos</p>
              <p className="text-2xl font-bold text-blue-600">3</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600">Ferias Pendentes</p>
              <p className="text-2xl font-bold text-purple-600">15</p>
            </div>
            <div className="p-4 bg-orange-50 rounded-lg">
              <p className="text-sm text-gray-600">Atestados (mes)</p>
              <p className="text-2xl font-bold text-orange-600">8</p>
            </div>
          </div>
        </div>
      </div>

      {/* Calendar placeholder */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Calendar className="h-5 w-5 text-conecta-escuro" />
          Calendario de RH
        </h2>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <p className="text-gray-500">Calendario de eventos, ferias e treinamentos</p>
        </div>
      </div>
    </div>
  );
}

export default HRPage;
