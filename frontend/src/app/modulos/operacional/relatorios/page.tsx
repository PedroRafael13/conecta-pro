'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  AlertCircle,
  ArrowLeft,
  BarChart3,
  Filter,
  RefreshCw,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/useAuth';
import { useEmployees } from '@/hooks/useEmployees';
import { usePosts } from '@/hooks/usePosts';
import { reportsService } from '@/lib/services/reports';
import { getErrorMessage } from '@/lib/api';
import type {
  CoverageReportResponse,
  CostsReportResponse,
  Employee,
  HoursReportResponse,
  Post,
} from '@/types/operacional';

const TIMEZONE = 'America/Manaus';

const formatDateInput = (value: Date) => {
  return new Intl.DateTimeFormat('en-CA', { timeZone: TIMEZONE }).format(value);
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

const formatPercent = (value: number) => `${value.toFixed(1)}%`;

export default function RelatoriosPage() {
  const router = useRouter();
  const { isLoading: authLoading, isAuthenticated } = useAuth();
  const { posts } = usePosts({ initialPageSize: 200 });
  const { employees } = useEmployees({ initialPageSize: 200 });

  const now = useMemo(() => new Date(), []);
  const [startDate, setStartDate] = useState(
    formatDateInput(new Date(now.getFullYear(), now.getMonth(), 1))
  );
  const [endDate, setEndDate] = useState(formatDateInput(now));
  const [postId, setPostId] = useState<string>('');
  const [employeeId, setEmployeeId] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);

  const [coverageReport, setCoverageReport] = useState<CoverageReportResponse | null>(null);
  const [hoursReport, setHoursReport] = useState<HoursReportResponse | null>(null);
  const [costsReport, setCostsReport] = useState<CostsReportResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  const postMap = useMemo(() => {
    return posts.reduce<Record<string, Post>>((acc, post) => {
      acc[post.id] = post;
      return acc;
    }, {});
  }, [posts]);

  const employeeMap = useMemo(() => {
    return employees.reduce<Record<string, Employee>>((acc, employee) => {
      acc[employee.id] = employee;
      return acc;
    }, {});
  }, [employees]);

  const getEmployeeLabel = (id: string) => {
    const employee = employeeMap[id];
    return employee?.full_name || employee?.name || employee?.email || employee?.registration || id;
  };

  const fetchReports = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [coverage, hours, costs] = await Promise.all([
        reportsService.getCoverage({
          start_date: startDate,
          end_date: endDate,
          post_id: postId || undefined,
        }),
        reportsService.getHours({
          start_date: startDate,
          end_date: endDate,
          employee_id: employeeId || undefined,
        }),
        reportsService.getCosts({
          start_date: startDate,
          end_date: endDate,
          post_id: postId || undefined,
        }),
      ]);

      setCoverageReport(coverage);
      setHoursReport(hours);
      setCostsReport(costs);
    } catch (err) {
      setError(getErrorMessage(err));
      setCoverageReport(null);
      setHoursReport(null);
      setCostsReport(null);
    } finally {
      setIsLoading(false);
    }
  }, [startDate, endDate, postId, employeeId]);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

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
      <header className="sticky top-0 z-50 bg-[hsl(var(--background))]/80 backdrop-blur-xl border-b border-[hsl(var(--border))]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/modulos/operacional">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Operacional
                </Button>
              </Link>
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-emerald-500" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                    Relatórios
                  </h1>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    Cobertura, horas e custos operacionais
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className={showFilters ? 'border-[hsl(var(--primary))]' : ''}
              >
                <Filter className="w-4 h-4 mr-2" />
                Filtros
              </Button>
              <Button variant="outline" onClick={fetchReports} disabled={isLoading}>
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {showFilters && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="text-sm text-[hsl(var(--muted-foreground))] mb-1 block">
                  Posto
                </label>
                <select
                  className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm"
                  value={postId}
                  onChange={(e) => setPostId(e.target.value)}
                >
                  <option value="">Todos</option>
                  {posts.map((post) => (
                    <option key={post.id} value={post.id}>
                      {post.name} ({post.code})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm text-[hsl(var(--muted-foreground))] mb-1 block">
                  Funcionario
                </label>
                <select
                  className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                >
                  <option value="">Todos</option>
                  {employees.map((employee) => (
                    <option key={employee.id} value={employee.id}>
                      {getEmployeeLabel(employee.id)}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm text-[hsl(var(--muted-foreground))] mb-1 block">
                  Inicio
                </label>
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm text-[hsl(var(--muted-foreground))] mb-1 block">
                  Fim
                </label>
                <Input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <p className="text-red-500">{error}</p>
            <Button variant="outline" size="sm" onClick={fetchReports} className="ml-auto">
              Tentar novamente
            </Button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <p className="text-xs text-[hsl(var(--muted-foreground))]">Cobertura</p>
            <p className="text-2xl font-semibold text-[hsl(var(--foreground))]">
              {coverageReport ? formatPercent(coverageReport.coverage_rate) : '--'}
            </p>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
              {coverageReport
                ? `${coverageReport.active_allocations}/${coverageReport.total_allocations} alocacoes ativas`
                : 'Sem dados'}
            </p>
          </div>
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <p className="text-xs text-[hsl(var(--muted-foreground))]">Horas trabalhadas</p>
            <p className="text-2xl font-semibold text-[hsl(var(--foreground))]">
              {hoursReport ? hoursReport.total_hours.toFixed(1) : '--'}
            </p>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
              {hoursReport ? `${hoursReport.total_overtime.toFixed(1)}h extras` : 'Sem dados'}
            </p>
          </div>
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <p className="text-xs text-[hsl(var(--muted-foreground))]">Custo estimado</p>
            <p className="text-2xl font-semibold text-[hsl(var(--foreground))]">
              {costsReport ? formatCurrency(costsReport.total_cost) : '--'}
            </p>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
              {costsReport ? `${costsReport.total_posts} postos` : 'Sem dados'}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <h2 className="text-sm font-semibold text-[hsl(var(--foreground))] mb-3">
              Cobertura por posto
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-[hsl(var(--muted-foreground))]">
                    <th className="pb-2">Posto</th>
                    <th className="pb-2">Alocacoes</th>
                    <th className="pb-2">Cobertura</th>
                  </tr>
                </thead>
                <tbody>
                  {coverageReport?.items.map((item) => (
                    <tr key={item.post_id} className="border-t border-[hsl(var(--border))]">
                      <td className="py-2">{postMap[item.post_id]?.name || item.post_name}</td>
                      <td className="py-2">
                        {item.active_allocations}/{item.total_allocations}
                      </td>
                      <td className="py-2">{formatPercent(item.coverage_rate)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!coverageReport?.items.length && (
                <p className="text-xs text-[hsl(var(--muted-foreground))] py-4">
                  Nenhum dado de cobertura encontrado.
                </p>
              )}
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <h2 className="text-sm font-semibold text-[hsl(var(--foreground))] mb-3">
              Horas por funcionario
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-[hsl(var(--muted-foreground))]">
                    <th className="pb-2">Funcionario</th>
                    <th className="pb-2">Turnos</th>
                    <th className="pb-2">Horas</th>
                  </tr>
                </thead>
                <tbody>
                  {hoursReport?.items.map((item) => (
                    <tr key={item.employee_id} className="border-t border-[hsl(var(--border))]">
                      <td className="py-2">{getEmployeeLabel(item.employee_id)}</td>
                      <td className="py-2">{item.total_shifts}</td>
                      <td className="py-2">{item.total_hours.toFixed(1)}h</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!hoursReport?.items.length && (
                <p className="text-xs text-[hsl(var(--muted-foreground))] py-4">
                  Nenhum dado de horas encontrado.
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
          <h2 className="text-sm font-semibold text-[hsl(var(--foreground))] mb-3">
            Custos estimados por posto
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-[hsl(var(--muted-foreground))]">
                  <th className="pb-2">Posto</th>
                  <th className="pb-2">Turnos</th>
                  <th className="pb-2">Custo</th>
                </tr>
              </thead>
              <tbody>
                {costsReport?.items.map((item) => (
                  <tr key={item.post_id} className="border-t border-[hsl(var(--border))]">
                    <td className="py-2">{postMap[item.post_id]?.name || item.post_name}</td>
                    <td className="py-2">{item.total_shifts}</td>
                    <td className="py-2">{formatCurrency(item.total_cost)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!costsReport?.items.length && (
              <p className="text-xs text-[hsl(var(--muted-foreground))] py-4">
                Nenhum dado de custos encontrado.
              </p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
