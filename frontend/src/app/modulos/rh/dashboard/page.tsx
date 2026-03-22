'use client';

import { useState, useEffect } from 'react';
import { BarChart3, Users, TrendingDown, Clock, Smile, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

const API_HR = '/api/v1/people-management/hr';
const API_RH = '/api/v1/people-management/human-resources';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface HeadcountItem { cargo: string; total: number }
interface AdmissaoItem { mes: string; total: number }
interface TurnoItem { name: string; value: number }

const COLORS = ['#1E3A5F', '#FF6B35', '#2563eb', '#f97316', '#10b981', '#8b5cf6'];

export default function DashboardRHPage() {
  const [stats, setStats] = useState({ headcount: 0, turnoverRate: '-', avgHireTime: '-', satisfaction: '-%' });
  const [headcountData, setHeadcountData] = useState<HeadcountItem[]>([]);
  const [admissaoData, setAdmissaoData] = useState<AdmissaoItem[]>([]);
  const [turnoData, setTurnoData] = useState<TurnoItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const headers = getAuthHeaders();
        const [empRes, turnoverRes, climaRes] = await Promise.all([
          fetch(`${API_HR}/employees?limit=200`, { headers }),
          fetch(`${API_RH}/turnover/dashboard`, { headers }).catch(() => null),
          fetch(`${API_RH}/climate?limit=1`, { headers }).catch(() => null),
        ]);

        let headcount = 0;
        const cargoCounts: Record<string, number> = {};
        const admissoesPorMes: Record<string, number> = {};

        if (empRes.ok) {
          const d = await empRes.json();
          const items = d.items || d || [];
          headcount = d.total || items.length;

          for (const emp of items) {
            const cargo = (emp.cargo || 'Outros')
              .replace('Agente de ', 'Ag. ')
              .replace('Lider de ', 'Lider ');
            cargoCounts[cargo] = (cargoCounts[cargo] || 0) + 1;

            if (emp.data_admissao) {
              const mes = emp.data_admissao.substring(0, 7);
              admissoesPorMes[mes] = (admissoesPorMes[mes] || 0) + 1;
            }
          }

          setHeadcountData(
            Object.entries(cargoCounts)
              .map(([cargo, total]) => ({ cargo, total }))
              .sort((a, b) => b.total - a.total)
          );

          const meses = Object.entries(admissoesPorMes)
            .sort(([a], [b]) => a.localeCompare(b))
            .slice(-6);
          setAdmissaoData(meses.map(([mes, total]) => ({
            mes: mes.replace(/^\d{4}-/, ''),
            total,
          })));

          const funcDistr: TurnoItem[] = Object.entries(cargoCounts)
            .map(([name, value]) => ({ name, value }))
            .sort((a, b) => b.value - a.value);
          setTurnoData(funcDistr);
        }

        let turnoverRate = '-';
        let avgHireTime = '-';
        if (turnoverRes?.ok) {
          const td = await turnoverRes.json();
          if (td.turnover_rate !== undefined) turnoverRate = `${td.turnover_rate}%`;
          if (td.avg_hire_time !== undefined) avgHireTime = `${td.avg_hire_time} dias`;
        }

        let satisfaction = '-%';
        if (climaRes?.ok) {
          const d = await climaRes.json();
          const items = d.items || d || [];
          if (items.length > 0) {
            satisfaction = `${items[0].score || items[0].overall_score || 0}%`;
          }
        }

        setStats({ headcount, turnoverRate, avgHireTime, satisfaction });
      } catch { /* fallback */ } finally { setLoading(false); }
    }
    load();
  }, []);

  const kpis = [
    { title: 'Headcount', value: loading ? '...' : stats.headcount, subtitle: 'Total ativo', icon: Users, color: 'text-blue-600', bgColor: 'bg-blue-50' },
    { title: 'Turnover Rate', value: loading ? '...' : stats.turnoverRate, subtitle: 'Meta: < 5%', icon: TrendingDown, color: 'text-green-600', bgColor: 'bg-green-50' },
    { title: 'Tempo Medio Contratacao', value: loading ? '...' : stats.avgHireTime, subtitle: 'Meta: 15 dias', icon: Clock, color: 'text-orange-600', bgColor: 'bg-orange-50' },
    { title: 'Satisfacao', value: loading ? '...' : stats.satisfaction, subtitle: 'Pesquisa de clima', icon: Smile, color: 'text-purple-600', bgColor: 'bg-purple-50' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <BarChart3 className="h-6 w-6" />
          Dashboard de RH
        </h1>
        <p className="text-muted-foreground">Indicadores e metricas de Recursos Humanos</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {kpis.map((kpi) => (
          <Card key={kpi.title}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{kpi.title}</p>
                  <p className="text-2xl font-bold">{kpi.value}</p>
                  <p className="text-xs text-muted-foreground mt-1">{kpi.subtitle}</p>
                </div>
                <div className={`h-10 w-10 rounded-lg ${kpi.bgColor} flex items-center justify-center`}>
                  <kpi.icon className={`h-5 w-5 ${kpi.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Headcount por Cargo</CardTitle>
          </CardHeader>
          <CardContent>
            {headcountData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={headcountData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="cargo" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }} />
                  <Bar dataKey="total" fill="#1E3A5F" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-48 flex items-center justify-center text-muted-foreground">
                {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : 'Sem dados'}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Admissoes Ultimos Meses</CardTitle>
          </CardHeader>
          <CardContent>
            {admissaoData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={admissaoData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="mes" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }} />
                  <Line type="monotone" dataKey="total" stroke="#FF6B35" strokeWidth={2} dot={{ fill: '#FF6B35', r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-48 flex items-center justify-center text-muted-foreground">
                {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : 'Sem dados de admissao'}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Distribuicao por Funcao</CardTitle>
          </CardHeader>
          <CardContent>
            {turnoData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={turnoData} cx="50%" cy="50%" outerRadius={70} dataKey="value" label={(props: any) => `${props.name} ${((props.percent ?? 0) * 100).toFixed(0)}%`}>
                    {turnoData.map((_, idx) => (
                      <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-48 flex items-center justify-center text-muted-foreground">
                {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : 'Sem dados'}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
