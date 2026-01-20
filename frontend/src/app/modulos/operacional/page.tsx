'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Shield,
  MapPin,
  Calendar,
  Users,
  Clock,
  ChevronRight,
  ArrowLeft,
  Search,
  Plus,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/useAuth';
import { usePostStats } from '@/hooks/usePosts';
import { useScales } from '@/hooks/useScales';
import { useTodayShifts } from '@/hooks/useShifts';

// Sub-módulos do Operacional
const subModules = [
  {
    id: 'postos',
    title: 'Postos de Trabalho',
    description: 'Gerenciar postos, locais e requisitos de trabalho',
    icon: MapPin,
    href: '/modulos/operacional/postos',
    color: 'cyan',
    stats: { label: 'postos ativos', key: 'total' },
  },
  {
    id: 'escalas',
    title: 'Escalas',
    description: 'Criar e gerenciar escalas mensais de trabalho',
    icon: Calendar,
    href: '/modulos/operacional/escalas',
    color: 'blue',
    stats: { label: 'escalas', key: 'scales' },
  },
  {
    id: 'alocacoes',
    title: 'Alocações',
    description: 'Alocar funcionários nos postos de trabalho',
    icon: Users,
    href: '/modulos/operacional/alocacoes',
    color: 'green',
    stats: { label: 'alocados', key: 'total_allocated' },
  },
  {
    id: 'turnos',
    title: 'Turnos',
    description: 'Visualizar e gerenciar turnos diários',
    icon: Clock,
    href: '/modulos/operacional/turnos',
    color: 'orange',
    stats: { label: 'turnos hoje', key: 'shifts' },
  },
];

export default function OperacionalPage() {
  const router = useRouter();
  const { user, isLoading: authLoading, isAuthenticated } = useAuth();
  const { stats, isLoading: statsLoading } = usePostStats();
  const { total: scalesTotal, isLoading: scalesLoading } = useScales(1, 1);
  const { shifts: todayShifts, isLoading: shiftsLoading } = useTodayShifts();

  const moduleStats = {
    postos: stats?.total,
    escalas: scalesLoading ? null : scalesTotal,
    alocacoes: stats?.total_allocated,
    turnos: shiftsLoading ? null : todayShifts.length,
  } as const;

  // Redirecionar se não autenticado
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  if (authLoading || statsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))]">
        <div className="animate-pulse-slow text-[hsl(var(--primary))]">
          <Shield className="w-12 h-12" />
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
                <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-green-500" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                    Operacional
                  </h1>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    Gestao de postos, escalas e alocacoes
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                <MapPin className="w-5 h-5 text-cyan-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {stats?.total || 0}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Postos</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {stats?.filled || 0}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Preenchidos</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center">
                <AlertCircle className="w-5 h-5 text-orange-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {stats?.with_vacancy || 0}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Com vagas</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Users className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {stats?.total_allocated || 0}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Alocados</p>
              </div>
            </div>
          </div>
        </div>

        {/* Sub-modules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {subModules.map((module) => {
            const Icon = module.icon;
            const isDisabled = false;

            return (
              <Link
                key={module.id}
                href={isDisabled ? '#' : module.href}
                className={isDisabled ? 'cursor-not-allowed' : ''}
              >
                <div
                  className={`
                    group relative bg-[hsl(var(--card))] border border-[hsl(var(--border))]
                    rounded-xl p-6 transition-all duration-200
                    ${isDisabled ? 'opacity-60' : 'hover:border-[hsl(var(--primary))] hover:shadow-lg'}
                  `}
                >
                  <div className="flex items-start gap-4">
                    <div
                      className={`
                        w-12 h-12 rounded-xl flex items-center justify-center
                        ${module.color === 'cyan' ? 'bg-cyan-500/10' : ''}
                        ${module.color === 'blue' ? 'bg-blue-500/10' : ''}
                        ${module.color === 'green' ? 'bg-green-500/10' : ''}
                        ${module.color === 'orange' ? 'bg-orange-500/10' : ''}
                      `}
                    >
                      <Icon
                        className={`
                          w-6 h-6
                          ${module.color === 'cyan' ? 'text-cyan-500' : ''}
                          ${module.color === 'blue' ? 'text-blue-500' : ''}
                          ${module.color === 'green' ? 'text-green-500' : ''}
                          ${module.color === 'orange' ? 'text-orange-500' : ''}
                        `}
                      />
                    </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-1">
                      {module.title}
                    </h3>
                    <p className="text-sm text-[hsl(var(--muted-foreground))]">
                      {module.description}
                    </p>
                    {module.stats && (
                      <p className="text-xs text-[hsl(var(--muted-foreground))] mt-3">
                        {module.stats.label}:{' '}
                        <span className="text-[hsl(var(--foreground))] font-semibold">
                          {moduleStats[module.id as keyof typeof moduleStats] ?? '...'}
                        </span>
                      </p>
                    )}
                  </div>
                    <ChevronRight
                      className={`
                        w-5 h-5 text-[hsl(var(--muted-foreground))]
                        transition-transform group-hover:translate-x-1
                        ${isDisabled ? 'hidden' : ''}
                      `}
                    />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>

        {/* Quick Stats by Type */}
        {stats && Object.keys(stats.by_type).length > 0 && (
          <div className="mt-8">
            <h2 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-4">
              Postos por Tipo
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {Object.entries(stats.by_type).map(([type, count]) => (
                <div
                  key={type}
                  className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-3 text-center"
                >
                  <p className="text-xl font-bold text-[hsl(var(--foreground))]">{count}</p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))] capitalize">
                    {type.replace(/_/g, ' ')}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
