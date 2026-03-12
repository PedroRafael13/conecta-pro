'use client';

import { BarChart3, Users, TrendingDown, Clock, Smile } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const kpis = [
  { title: 'Headcount', value: 44, subtitle: '+3 este mes', icon: Users, color: 'text-blue-600', bgColor: 'bg-blue-50' },
  { title: 'Turnover Rate', value: '4.2%', subtitle: 'Meta: < 5%', icon: TrendingDown, color: 'text-green-600', bgColor: 'bg-green-50' },
  { title: 'Tempo Medio Contratacao', value: '18 dias', subtitle: 'Meta: 15 dias', icon: Clock, color: 'text-orange-600', bgColor: 'bg-orange-50' },
  { title: 'Satisfacao', value: '78%', subtitle: 'Pesquisa Q1 2026', icon: Smile, color: 'text-purple-600', bgColor: 'bg-purple-50' },
];

const charts = [
  { title: 'Headcount por Departamento', desc: 'Distribuicao de colaboradores por area' },
  { title: 'Turnover Mensal', desc: 'Evolucao do turnover nos ultimos 12 meses' },
  { title: 'Treinamentos por Categoria', desc: 'Horas de treinamento por tipo de curso' },
];

export default function DashboardRHPage() {
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
        {charts.map((chart) => (
          <Card key={chart.title}>
            <CardHeader>
              <CardTitle className="text-sm font-medium">{chart.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-48 bg-gray-800/50 rounded-lg flex items-center justify-center border border-gray-700 border-dashed">
                <div className="text-center">
                  <BarChart3 className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">{chart.desc}</p>
                  <p className="text-xs text-muted-foreground mt-1">Grafico em desenvolvimento</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
