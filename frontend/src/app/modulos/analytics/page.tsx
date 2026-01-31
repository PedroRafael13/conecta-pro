'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  BarChart3,
  PieChart as PieChartIcon,
  TrendingUp,
  Users,
  MapPin,
  Calendar,
  Activity,
  ArrowLeft,
  RefreshCw,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  Legend,
  PieLabelRenderProps,
} from 'recharts';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { useAnalyticsData } from '@/hooks/useAnalyticsData';
import { KPIWidget, KPIWidgetSkeleton } from '@/components/ui/kpi-widget';

const COLORS = ['#06b6d4', '#8b5cf6', '#22c55e', '#f59e0b', '#ef4444', '#ec4899', '#3b82f6', '#14b8a6'];

export default function AnalyticsPage() {
  const router = useRouter();
  const { user, isLoading: authLoading, isAuthenticated } = useAuth();
  const { data, isLoading, error, refresh } = useAnalyticsData();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))]">
        <div className="animate-pulse-slow text-[hsl(var(--primary))]">
          <BarChart3 className="w-12 h-12" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-grid">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[hsl(var(--background))]/80 backdrop-blur-xl border-b border-[hsl(var(--border))]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/dashboard">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Voltar
                </Button>
              </Link>
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-violet-500" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                    Analytics
                  </h1>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    Visao geral e metricas do sistema
                  </p>
                </div>
              </div>
            </div>
            <Button variant="outline" size="sm" onClick={refresh} disabled={isLoading}>
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Atualizar
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p className="text-sm text-red-500">{error}</p>
          </div>
        )}

        {/* KPIs Summary */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-4">
            Resumo Geral
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
            {isLoading ? (
              <>
                <KPIWidgetSkeleton />
                <KPIWidgetSkeleton />
                <KPIWidgetSkeleton />
                <KPIWidgetSkeleton />
                <KPIWidgetSkeleton />
                <KPIWidgetSkeleton />
              </>
            ) : (
              <>
                <KPIWidget
                  title="Colaboradores"
                  value={data?.summary.totalEmployees || 0}
                  icon={Users}
                  iconColor="text-purple-500"
                  iconBgColor="bg-purple-500/10"
                  onClick={() => router.push('/modulos/operacional/colaboradores')}
                />
                <KPIWidget
                  title="Postos"
                  value={data?.summary.totalPosts || 0}
                  icon={MapPin}
                  iconColor="text-cyan-500"
                  iconBgColor="bg-cyan-500/10"
                  onClick={() => router.push('/modulos/operacional/postos')}
                />
                <KPIWidget
                  title="Escalas"
                  value={data?.summary.totalScales || 0}
                  icon={Calendar}
                  iconColor="text-blue-500"
                  iconBgColor="bg-blue-500/10"
                  onClick={() => router.push('/modulos/operacional/escalas')}
                />
                <KPIWidget
                  title="Alocacoes Ativas"
                  value={data?.summary.activeAllocations || 0}
                  icon={Users}
                  iconColor="text-green-500"
                  iconBgColor="bg-green-500/10"
                  onClick={() => router.push('/modulos/operacional/alocacoes')}
                />
                <KPIWidget
                  title="Cobertura"
                  value={`${data?.summary.coverageRate || 0}%`}
                  icon={Activity}
                  iconColor={
                    (data?.summary.coverageRate || 0) >= 80
                      ? 'text-green-500'
                      : 'text-yellow-500'
                  }
                  iconBgColor={
                    (data?.summary.coverageRate || 0) >= 80
                      ? 'bg-green-500/10'
                      : 'bg-yellow-500/10'
                  }
                />
                <KPIWidget
                  title="Turnos"
                  value={data?.summary.totalOccurrences || 0}
                  icon={TrendingUp}
                  iconColor="text-orange-500"
                  iconBgColor="bg-orange-500/10"
                />
              </>
            )}
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Colaboradores por Departamento */}
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-purple-500" />
              <h3 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                Colaboradores por Departamento
              </h3>
            </div>
            <div className="h-[300px]">
              {isLoading ? (
                <div className="h-full flex items-center justify-center">
                  <div className="animate-pulse text-[hsl(var(--muted-foreground))]">
                    Carregando...
                  </div>
                </div>
              ) : data?.employeesByDepartment && data.employeesByDepartment.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.employeesByDepartment} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                    <YAxis
                      dataKey="departamento"
                      type="category"
                      width={120}
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={11}
                      tickFormatter={(value) => value.length > 15 ? value.slice(0, 15) + '...' : value}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                    />
                    <Bar dataKey="total" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-[hsl(var(--muted-foreground))]">
                  Sem dados disponiveis
                </div>
              )}
            </div>
          </div>

          {/* Postos por Tipo */}
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <PieChartIcon className="w-5 h-5 text-cyan-500" />
              <h3 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                Postos por Tipo
              </h3>
            </div>
            <div className="h-[300px]">
              {isLoading ? (
                <div className="h-full flex items-center justify-center">
                  <div className="animate-pulse text-[hsl(var(--muted-foreground))]">
                    Carregando...
                  </div>
                </div>
              ) : data?.postsByType && data.postsByType.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.postsByType}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(props: PieLabelRenderProps) => {
                        const name = props.name ?? '';
                        const percent = props.percent ?? 0;
                        return `${name} (${(percent * 100).toFixed(0)}%)`;
                      }}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="total"
                      nameKey="type"
                    >
                      {data.postsByType.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-[hsl(var(--muted-foreground))]">
                  Sem dados disponiveis
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Tendencia Mensal */}
        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-green-500" />
            <h3 className="text-lg font-semibold text-[hsl(var(--foreground))]">
              Tendencia Mensal
            </h3>
          </div>
          <div className="h-[350px]">
            {isLoading ? (
              <div className="h-full flex items-center justify-center">
                <div className="animate-pulse text-[hsl(var(--muted-foreground))]">
                  Carregando...
                </div>
              </div>
            ) : data?.monthlyTrends && data.monthlyTrends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.monthlyTrends}>
                  <defs>
                    <linearGradient id="colorEscalas" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorColaboradores" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorOcorrencias" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="escalas"
                    name="Escalas"
                    stroke="#3b82f6"
                    fillOpacity={1}
                    fill="url(#colorEscalas)"
                  />
                  <Area
                    type="monotone"
                    dataKey="colaboradores"
                    name="Colaboradores"
                    stroke="#8b5cf6"
                    fillOpacity={1}
                    fill="url(#colorColaboradores)"
                  />
                  <Area
                    type="monotone"
                    dataKey="ocorrencias"
                    name="Ocorrencias"
                    stroke="#ef4444"
                    fillOpacity={1}
                    fill="url(#colorOcorrencias)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-[hsl(var(--muted-foreground))]">
                Sem dados disponiveis
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
