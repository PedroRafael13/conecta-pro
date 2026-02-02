'use client';

import { Heart, Stethoscope, HardHat, AlertTriangle, FileCheck, ShieldAlert, Package, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
;
import { useRouter } from 'next/navigation';
import { usePCMSOStatistics, useEPIStatistics, usePPRAStatistics } from '@/hooks/health-occupational';

const subPages = [
  {
    title: 'Exames Medicos (PCMSO)',
    description: 'Gestao de exames ocupacionais, ASOs e agendamentos conforme NR-7',
    icon: Stethoscope,
    href: '/modulos/saude-ocupacional/exames',
    color: 'text-blue-600',
    bg: 'bg-blue-50',
  },
  {
    title: 'EPIs (NR-6)',
    description: 'Controle de equipamentos de protecao individual, entregas e estoque',
    icon: HardHat,
    href: '/modulos/saude-ocupacional/epi',
    color: 'text-purple-600',
    bg: 'bg-purple-50',
  },
  {
    title: 'Riscos Ocupacionais (PPRA/PGR)',
    description: 'Mapeamento de riscos, medidas de controle e analise por setor',
    icon: AlertTriangle,
    href: '/modulos/saude-ocupacional/riscos',
    color: 'text-orange-600',
    bg: 'bg-orange-50',
  },
];

export default function SaudeOcupacionalPage() {
  const router = useRouter();
  const { data: pcmsoStats, isLoading: pcmsoLoading } = usePCMSOStatistics();
  const { data: epiStats, isLoading: epiLoading } = useEPIStatistics();
  const { data: ppraStats, isLoading: ppraLoading } = usePPRAStatistics();

  const statsLoading = pcmsoLoading || epiLoading || ppraLoading;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Heart className="h-6 w-6" />
          Saude Ocupacional
        </h1>
        <p className="text-muted-foreground">
          Gestao integrada de saude e seguranca do trabalho - PCMSO, EPIs e PPRA/PGR.
        </p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Exames</CardTitle>
            <Stethoscope className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="h-8 w-16 animate-pulse rounded bg-muted" />
            ) : (
              <div className="text-2xl font-bold">{(pcmsoStats as any)?.total_exames ?? 0}</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">ASOs Vencendo</CardTitle>
            <FileCheck className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="h-8 w-16 animate-pulse rounded bg-muted" />
            ) : (
              <div className="text-2xl font-bold text-yellow-600">
                {(pcmsoStats as any)?.asos_vencendo ?? 0}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">EPIs Entregues</CardTitle>
            <Package className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="h-8 w-16 animate-pulse rounded bg-muted" />
            ) : (
              <div className="text-2xl font-bold text-purple-600">
                {(epiStats as any)?.total_entregas ?? 0}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Riscos Mapeados</CardTitle>
            <ShieldAlert className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="h-8 w-16 animate-pulse rounded bg-muted" />
            ) : (
              <div className="text-2xl font-bold text-red-600">
                {(ppraStats as any)?.total_riscos ?? 0}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Sub-page navigation cards */}
      <div className="grid gap-4 md:grid-cols-3">
        {subPages.map((page) => (
          <Card
            key={page.href}
            className="cursor-pointer transition-all hover:shadow-md hover:border-primary/30"
            onClick={() => router.push(page.href)}
          >
            <CardContent className="flex items-center gap-4 p-6">
              <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-lg ${page.bg}`}>
                <page.icon className={`h-6 w-6 ${page.color}`} />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold">{page.title}</h3>
                <p className="text-sm text-muted-foreground">{page.description}</p>
              </div>
              <ArrowRight className="h-5 w-5 shrink-0 text-muted-foreground" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
