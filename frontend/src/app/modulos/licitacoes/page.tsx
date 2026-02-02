'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTendersDashboard } from '@/hooks/bidding/useTenders';
import { useProposalsDashboard } from '@/hooks/bidding/useProposals';
import { useContractsDashboard } from '@/hooks/bidding/useContracts';
import Link from 'next/link';
import { FileText, FileCheck, FileSignature, Award, AlertCircle } from 'lucide-react';

export default function LicitacoesPage() {
  const { data: tendersData } = useTendersDashboard();
  const { data: proposalsData } = useProposalsDashboard();
  const { data: contractsData } = useContractsDashboard();

  const stats = [
    {
      title: 'Editais Abertos',
      value: tendersData?.total_abertos || 0,
      icon: FileText,
      href: '/modulos/licitacoes/editais',
      color: 'text-blue-600'
    },
    {
      title: 'Propostas em Análise',
      value: proposalsData?.em_andamento || 0,
      icon: FileCheck,
      href: '/modulos/licitacoes/propostas',
      color: 'text-orange-600'
    },
    {
      title: 'Contratos Vigentes',
      value: contractsData?.vigentes || 0,
      icon: FileSignature,
      href: '/modulos/licitacoes/contratos',
      color: 'text-green-600'
    },
    {
      title: 'Certidões Pendentes',
      value: contractsData?.certidoes_pendentes || 0,
      icon: AlertCircle,
      href: '/modulos/licitacoes/certidoes',
      color: 'text-red-600'
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Licitações</h1>
        <p className="text-muted-foreground">
          Gestão de licitações públicas, editais, propostas e contratos
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Link key={stat.title} href={stat.href}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium">
                    {stat.title}
                  </CardTitle>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>

      {/* Quick Access */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Editais Recentes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Últimos editais publicados
            </p>
            <Link
              href="/modulos/licitacoes/editais"
              className="text-sm font-medium text-blue-600 hover:underline"
            >
              Ver todos os editais →
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Minhas Propostas</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Acompanhe suas propostas
            </p>
            <Link
              href="/modulos/licitacoes/propostas"
              className="text-sm font-medium text-blue-600 hover:underline"
            >
              Ver propostas →
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Contratos Ativos</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Gerencie seus contratos
            </p>
            <Link
              href="/modulos/licitacoes/contratos"
              className="text-sm font-medium text-blue-600 hover:underline"
            >
              Ver contratos →
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
