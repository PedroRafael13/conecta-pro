'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2,
  Play,
  Code,
  Shield,
  Activity,
  Zap,
  RefreshCw,
  ChevronLeft,
} from 'lucide-react';
import { BartoloChatWidget } from '@/components/ai/BartoloChatWidget';
import { toast } from 'sonner';
import Link from 'next/link';

// Types
interface OpenClawReport {
  cycle_id: string;
  overall_status: 'pass' | 'fail' | 'warn' | 'error';
  duration_seconds: number;
  summary: {
    status_counts: {
      pass: number;
      fail: number;
      warn: number;
      skip: number;
      error: number;
    };
  };
  checks: Array<{
    name: string;
    status: string;
    duration_seconds: number;
    message: string;
  }>;
  timestamp: string;
}

interface HistoryItem {
  cycle_id: string;
  overall_status: string;
  duration_seconds: number;
  timestamp: string;
}

interface HistoryResponse {
  reports: HistoryItem[];
  total: number;
}

// API Service
const openclawApi = {
  async getReport(): Promise<OpenClawReport> {
    const res = await fetch('/api/v1/openclaw/report');
    if (!res.ok) throw new Error('Erro ao buscar relatório');
    return res.json();
  },

  async getHistory(): Promise<HistoryResponse> {
    const res = await fetch('/api/v1/openclaw/history?limit=30');
    if (!res.ok) throw new Error('Erro ao buscar histórico');
    return res.json();
  },

  async runCheck(check: string): Promise<OpenClawReport> {
    const res = await fetch('/api/v1/openclaw/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ check }),
    });
    if (!res.ok) throw new Error('Erro ao executar check');
    return res.json();
  },
};

export default function OpenClawPage() {
  const queryClient = useQueryClient();

  // Queries
  const {
    data: report,
    isLoading: reportLoading,
    refetch: refetchReport,
  } = useQuery({
    queryKey: ['openclaw', 'report'],
    queryFn: openclawApi.getReport,
  });

  const { data: history } = useQuery({
    queryKey: ['openclaw', 'history'],
    queryFn: openclawApi.getHistory,
  });

  // Mutation para executar checks
  const runCheckMutation = useMutation({
    mutationFn: (check: string) => openclawApi.runCheck(check),
    onSuccess: () => {
      toast.success('Check executado com sucesso');
      queryClient.invalidateQueries({ queryKey: ['openclaw', 'report'] });
      queryClient.invalidateQueries({ queryKey: ['openclaw', 'history'] });
    },
    onError: (error: Error) => {
      toast.error('Erro ao executar check', {
        description: error.message,
      });
    },
  });

  // Status badge
  const getStatusBadge = (status: string) => {
    const variants: Record<string, { bg: string; text: string }> = {
      pass: { bg: 'bg-green-500/10', text: 'text-green-500' },
      fail: { bg: 'bg-red-500/10', text: 'text-red-500' },
      warn: { bg: 'bg-yellow-500/10', text: 'text-yellow-500' },
      error: { bg: 'bg-red-800/10', text: 'text-red-800' },
    };

    const icons: Record<string, JSX.Element> = {
      pass: <CheckCircle className="w-4 h-4" />,
      fail: <XCircle className="w-4 h-4" />,
      warn: <AlertTriangle className="w-4 h-4" />,
      error: <XCircle className="w-4 h-4" />,
    };

    const variant = variants[status] || { bg: 'bg-gray-500/10', text: 'text-gray-500' };
    const icon = icons[status];

    return (
      <span
        className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${variant.bg} ${variant.text}`}
      >
        {icon}
        <span>{status.toUpperCase()}</span>
      </span>
    );
  };

  // Quick actions
  const quickActions = [
    { label: 'Testes', check: 'tests', icon: CheckCircle },
    { label: 'Lint', check: 'lint', icon: Code },
    { label: 'Security', check: 'security', icon: Shield },
    { label: 'Coverage', check: 'coverage', icon: Activity },
    { label: 'Health', check: 'health', icon: Activity },
    { label: 'Ciclo Completo', check: 'full', icon: Zap },
  ];

  // Trend data
  const trendData = history?.reports.slice(0, 30).reverse().map((item) => ({
    cycle: item.cycle_id.split('_')[1]?.substring(0, 8) || '',
    pass: item.overall_status === 'pass' ? 1 : 0,
    fail: item.overall_status === 'fail' ? 1 : 0,
    warn: item.overall_status === 'warn' ? 1 : 0,
  }));

  if (reportLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-[hsl(var(--primary))]" />
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
              <Link href="/modulos">
                <Button variant="ghost" size="sm">
                  <ChevronLeft className="w-4 h-4 mr-2" />
                  Módulos
                </Button>
              </Link>
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                    OpenClaw - Agente de Qualidade
                  </h1>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    Monitoramento contínuo de qualidade, segurança e performance
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={() => refetchReport()} disabled={reportLoading}>
                <RefreshCw className={`w-4 h-4 mr-2 ${reportLoading ? 'animate-spin' : ''}`} />
                Atualizar
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Status Card */}
        {report && (
          <Card>
            <CardHeader>
              <CardTitle>Status Geral</CardTitle>
              <CardDescription>Último ciclo: {report.cycle_id}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  {getStatusBadge(report.overall_status)}
                  <p className="text-sm text-muted-foreground">
                    Duração: {report.duration_seconds.toFixed(1)}s
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(report.timestamp).toLocaleString('pt-BR')}
                  </p>
                </div>
                <div className="grid grid-cols-5 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {report.summary.status_counts.pass}
                    </div>
                    <div className="text-xs text-muted-foreground">Pass</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {report.summary.status_counts.fail}
                    </div>
                    <div className="text-xs text-muted-foreground">Fail</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-600">
                      {report.summary.status_counts.warn}
                    </div>
                    <div className="text-xs text-muted-foreground">Warn</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-600">
                      {report.summary.status_counts.skip}
                    </div>
                    <div className="text-xs text-muted-foreground">Skip</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-800">
                      {report.summary.status_counts.error}
                    </div>
                    <div className="text-xs text-muted-foreground">Error</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Ações Rápidas</CardTitle>
            <CardDescription>Execute checks individuais ou ciclo completo</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {quickActions.map((action) => {
                const Icon = action.icon;
                return (
                  <Button
                    key={action.check}
                    variant="outline"
                    className="h-20 flex flex-col items-center justify-center gap-2"
                    onClick={() => runCheckMutation.mutate(action.check)}
                    disabled={runCheckMutation.isPending}
                  >
                    {runCheckMutation.isPending ? (
                      <Loader2 className="w-6 h-6 animate-spin" />
                    ) : (
                      <Icon className="w-6 h-6" />
                    )}
                    <span className="text-sm">{action.label}</span>
                  </Button>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Last Report Table */}
        {report && report.checks && report.checks.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Último Relatório</CardTitle>
              <CardDescription>Detalhes do último ciclo executado</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Check</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Duração</TableHead>
                      <TableHead>Mensagem</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {report.checks.map((check, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-medium">{check.name}</TableCell>
                        <TableCell>{getStatusBadge(check.status)}</TableCell>
                        <TableCell>{check.duration_seconds.toFixed(1)}s</TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {check.message || '-'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Trend Chart */}
        {trendData && trendData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Tendência (Últimos 30 Ciclos)</CardTitle>
              <CardDescription>Histórico de execuções do OpenClaw</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="cycle" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="pass"
                    stroke="#22c55e"
                    name="Pass"
                    strokeWidth={2}
                  />
                  <Line
                    type="monotone"
                    dataKey="fail"
                    stroke="#ef4444"
                    name="Fail"
                    strokeWidth={2}
                  />
                  <Line
                    type="monotone"
                    dataKey="warn"
                    stroke="#eab308"
                    name="Warn"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* History Table */}
        {history && history.reports && history.reports.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Histórico de Ciclos</CardTitle>
              <CardDescription>Últimas 10 execuções do OpenClaw</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Ciclo</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Duração</TableHead>
                      <TableHead>Data/Hora</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {history.reports.slice(0, 10).map((item) => (
                      <TableRow key={item.cycle_id}>
                        <TableCell className="font-mono text-sm">
                          {item.cycle_id}
                        </TableCell>
                        <TableCell>{getStatusBadge(item.overall_status)}</TableCell>
                        <TableCell>{item.duration_seconds.toFixed(1)}s</TableCell>
                        <TableCell>
                          {new Date(item.timestamp).toLocaleString('pt-BR')}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Empty state quando não há dados */}
        {!report && !reportLoading && (
          <Card>
            <CardContent className="text-center py-12">
              <AlertTriangle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground">
                Nenhum relatório disponível
              </h3>
              <p className="text-muted-foreground mt-1">
                Execute um check para gerar o primeiro relatório
              </p>
            </CardContent>
          </Card>
        )}
      </main>

      {/* Bartolo Chat Widget */}
      <BartoloChatWidget module="openclaw" initialOpen={false} />
    </div>
  );
}
