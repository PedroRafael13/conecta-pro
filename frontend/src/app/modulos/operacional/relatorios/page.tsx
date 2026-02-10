'use client';

import { AlertCircle, ArrowLeft, BarChart3, Filter, RefreshCw, FileSpreadsheet, FileText } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/useAuth';
import { useEmployees } from '@/hooks/operacional/useEmployees';
import { usePosts } from '@/hooks/operacional/usePosts';
import { useCoverageReport, useHoursReport, useCostsReport } from '@/hooks/operacional/useReports';
import type {
  Employee,
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
  const { data: postsData } = usePosts();
  const posts = useMemo(() => postsData?.items ?? [], [postsData?.items]);
  const { data: employeesData } = useEmployees();
  const employees = useMemo(() => employeesData?.items ?? [], [employeesData?.items]);

  const now = useMemo(() => new Date(), []);
  const [startDate, setStartDate] = useState(
    formatDateInput(new Date(now.getFullYear(), now.getMonth(), 1))
  );
  const [endDate, setEndDate] = useState(formatDateInput(now));
  const [postId, setPostId] = useState<string>('');
  const [employeeId, setEmployeeId] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  // Report hooks com params
  const coverageParams = useMemo(() => ({
    start_date: startDate,
    end_date: endDate,
    ...(postId ? { post_id: postId } : {}),
  }), [startDate, endDate, postId]);

  const hoursParams = useMemo(() => ({
    start_date: startDate,
    end_date: endDate,
    ...(employeeId ? { employee_id: employeeId } : {}),
  }), [startDate, endDate, employeeId]);

  const costsParams = useMemo(() => ({
    start_date: startDate,
    end_date: endDate,
    ...(postId ? { post_id: postId } : {}),
  }), [startDate, endDate, postId]);

  const {
    data: coverageReport,
    isLoading: coverageLoading,
    error: coverageError,
    refetch: refetchCoverage,
  } = useCoverageReport(coverageParams);

  const {
    data: hoursReport,
    isLoading: hoursLoading,
    error: hoursError,
    refetch: refetchHours,
  } = useHoursReport(hoursParams);

  const {
    data: costsReport,
    isLoading: costsLoading,
    error: costsError,
    refetch: refetchCosts,
  } = useCostsReport(costsParams);

  const isLoading = coverageLoading || hoursLoading || costsLoading;
  const error = coverageError || hoursError || costsError;

  const fetchReports = useCallback(() => {
    refetchCoverage();
    refetchHours();
    refetchCosts();
  }, [refetchCoverage, refetchHours, refetchCosts]);

  const postMap = useMemo(() => {
    return posts.reduce<Record<string, Post>>((acc, post) => {
      acc[post.id] = post as Post;
      return acc;
    }, {});
  }, [posts]);

  const employeeMap = useMemo(() => {
    return employees.reduce<Record<string, Employee>>((acc, employee) => {
      acc[employee.id] = employee;
      return acc;
    }, {});
  }, [employees]);

  const getEmployeeLabel = useCallback((id: string) => {
    const employee = employeeMap[id];
    return employee?.full_name || employee?.name || employee?.email || employee?.registration || id;
  }, [employeeMap]);

  // Export to CSV/Excel
  const exportToCSV = useCallback(() => {
    if (!coverageReport && !hoursReport && !costsReport) return;

    const lines: string[] = [];

    // Header
    lines.push(`Relatorio Operacional - ${startDate} a ${endDate}`);
    lines.push('');

    // Cobertura
    if (coverageReport) {
      lines.push('COBERTURA POR POSTO');
      lines.push('Posto,Alocacoes Ativas,Total Alocacoes,Taxa Cobertura');
      coverageReport.items.forEach(item => {
        lines.push(`"${postMap[item.post_id]?.name || item.post_name}",${item.active_allocations},${item.total_allocations},${item.coverage_rate.toFixed(1)}%`);
      });
      lines.push('');
    }

    // Horas
    if (hoursReport) {
      lines.push('HORAS POR FUNCIONARIO');
      lines.push('Funcionario,Turnos,Horas,Horas Extras');
      hoursReport.items.forEach(item => {
        lines.push(`"${getEmployeeLabel(item.employee_id)}",${item.total_shifts},${item.total_hours.toFixed(1)},${item.overtime_hours?.toFixed(1) || 0}`);
      });
      lines.push('');
    }

    // Custos
    if (costsReport) {
      lines.push('CUSTOS POR POSTO');
      lines.push('Posto,Turnos,Custo Total');
      costsReport.items.forEach(item => {
        lines.push(`"${postMap[item.post_id]?.name || item.post_name}",${item.total_shifts},${item.total_cost.toFixed(2)}`);
      });
    }

    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `relatorio-operacional-${startDate}-${endDate}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }, [coverageReport, hoursReport, costsReport, startDate, endDate, postMap, getEmployeeLabel]);

  // Export to PDF (simple HTML print)
  const exportToPDF = useCallback(() => {
    const printContent = document.getElementById('report-content');
    if (!printContent) return;

    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Relatorio Operacional - ${startDate} a ${endDate}</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            h1 { font-size: 18px; margin-bottom: 20px; }
            h2 { font-size: 14px; margin-top: 20px; margin-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 12px; }
            th { background-color: #f5f5f5; }
            .summary { display: flex; gap: 20px; margin-bottom: 20px; }
            .summary-card { padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            @media print { body { print-color-adjust: exact; } }
          </style>
        </head>
        <body>
          <h1>Relatorio Operacional</h1>
          <p>Periodo: ${startDate} a ${endDate}</p>
          ${printContent.innerHTML}
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  }, [startDate, endDate]);

  // Calculate max for simple bar visualization
  const maxHours = useMemo(() => {
    if (!hoursReport?.items.length) return 100;
    return Math.max(...hoursReport.items.map(i => i.total_hours));
  }, [hoursReport]);

  const maxCost = useMemo(() => {
    if (!costsReport?.items.length) return 1000;
    return Math.max(...costsReport.items.map(i => i.total_cost));
  }, [costsReport]);

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
              <Button
                variant="outline"
                onClick={exportToCSV}
                disabled={!coverageReport && !hoursReport && !costsReport}
                title="Exportar Excel/CSV"
              >
                <FileSpreadsheet className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                onClick={exportToPDF}
                disabled={!coverageReport && !hoursReport && !costsReport}
                title="Exportar PDF"
              >
                <FileText className="w-4 h-4" />
              </Button>
              <Button variant="outline" onClick={fetchReports} disabled={isLoading}>
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main id="report-content" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
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
            <p className="text-red-500">{(error as any)?.message || 'Erro ao carregar relatórios'}</p>
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
                    <th className="pb-2 w-48">Cobertura</th>
                  </tr>
                </thead>
                <tbody>
                  {coverageReport?.items.map((item) => (
                    <tr key={item.post_id} className="border-t border-[hsl(var(--border))]">
                      <td className="py-2">{postMap[item.post_id]?.name || item.post_name}</td>
                      <td className="py-2">
                        {item.active_allocations}/{item.total_allocations}
                      </td>
                      <td className="py-2">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 bg-[hsl(var(--muted))] rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all ${
                                item.coverage_rate >= 80 ? 'bg-green-500' :
                                item.coverage_rate >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${Math.min(item.coverage_rate, 100)}%` }}
                            />
                          </div>
                          <span className="text-xs w-12 text-right">{formatPercent(item.coverage_rate)}</span>
                        </div>
                      </td>
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
                    <th className="pb-2 w-48">Horas</th>
                  </tr>
                </thead>
                <tbody>
                  {hoursReport?.items.map((item) => (
                    <tr key={item.employee_id} className="border-t border-[hsl(var(--border))]">
                      <td className="py-2">{getEmployeeLabel(item.employee_id)}</td>
                      <td className="py-2">{item.total_shifts}</td>
                      <td className="py-2">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 bg-[hsl(var(--muted))] rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-500 rounded-full transition-all"
                              style={{ width: `${maxHours > 0 ? (item.total_hours / maxHours) * 100 : 0}%` }}
                            />
                          </div>
                          <span className="text-xs w-16 text-right">{item.total_hours.toFixed(1)}h</span>
                        </div>
                      </td>
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
                  <th className="pb-2 w-64">Custo</th>
                </tr>
              </thead>
              <tbody>
                {costsReport?.items.map((item) => (
                  <tr key={item.post_id} className="border-t border-[hsl(var(--border))]">
                    <td className="py-2">{postMap[item.post_id]?.name || item.post_name}</td>
                    <td className="py-2">{item.total_shifts}</td>
                    <td className="py-2">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-[hsl(var(--muted))] rounded-full overflow-hidden">
                          <div
                            className="h-full bg-emerald-500 rounded-full transition-all"
                            style={{ width: `${maxCost > 0 ? (item.total_cost / maxCost) * 100 : 0}%` }}
                          />
                        </div>
                        <span className="text-xs w-24 text-right">{formatCurrency(item.total_cost)}</span>
                      </div>
                    </td>
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
