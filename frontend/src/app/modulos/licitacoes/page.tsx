'use client';

/**
 * Dashboard de Licitações - Conecta PRO
 * Visão geral completa do módulo com KPIs, funil e acesso rápido
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useTendersDashboard, useListarEditaisAbertos } from '@/hooks/bidding/useTenders';
import { useEstatisticasPropostas } from '@/hooks/bidding/useProposals';
import { useContractsDashboard } from '@/hooks/bidding/useContracts';
import Link from 'next/link';
import {
  FileText,
  FileCheck,
  FileSignature,
  AlertCircle,
  Bot,
  TrendingUp,
  DollarSign,
  Shield,
  Calendar,
  ChevronRight,
  Search,
  Award,
  Target,
  ArrowUpRight,
} from 'lucide-react';

export default function LicitacoesPage() {
  const { data: tendersData } = useTendersDashboard();
  const { data: proposalsData } = useEstatisticasPropostas();
  const { data: contractsData } = useContractsDashboard();
  const { data: editaisAbertos } = useListarEditaisAbertos({ size: 5 });

  const stats = [
    {
      title: 'Editais Abertos',
      value: Number(tendersData?.total_abertos) || 0,
      subtitle: `${Number(tendersData?.total) || 0} total`,
      icon: FileText,
      href: '/modulos/licitacoes/editais',
      color: 'text-blue-600',
      bgColor: 'bg-blue-500/10',
    },
    {
      title: 'Propostas',
      value: Number(proposalsData?.total) || 0,
      subtitle: `${Number(proposalsData?.taxa_sucesso) || 0}% taxa sucesso`,
      icon: FileCheck,
      href: '/modulos/licitacoes/propostas',
      color: 'text-orange-600',
      bgColor: 'bg-orange-500/10',
    },
    {
      title: 'Contratos Vigentes',
      value: Number(contractsData?.vigentes) || 0,
      subtitle: contractsData?.valor_total
        ? `R$ ${Number(contractsData.valor_total).toLocaleString('pt-BR', { minimumFractionDigits: 0 })}`
        : 'R$ 0',
      icon: FileSignature,
      href: '/modulos/licitacoes/contratos',
      color: 'text-green-600',
      bgColor: 'bg-green-500/10',
    },
    {
      title: 'Certidoes',
      value: Number(contractsData?.certidoes_pendentes) || 0,
      subtitle: 'pendentes renovacao',
      icon: Shield,
      href: '/modulos/licitacoes/certidoes',
      color: 'text-red-600',
      bgColor: 'bg-red-500/10',
    },
  ];

  // Funil de licitações
  const funnel = [
    { label: 'Oportunidades', value: Number(tendersData?.total) || 0, color: 'bg-blue-500' },
    { label: 'Em Analise', value: Number(tendersData?.em_andamento || tendersData?.em_analise) || 0, color: 'bg-purple-500' },
    { label: 'Participando', value: Number(tendersData?.participando) || 0, color: 'bg-orange-500' },
    { label: 'Propostas', value: Number(proposalsData?.total) || 0, color: 'bg-yellow-500' },
    { label: 'Vencidos', value: Number(proposalsData?.vencedoras) || 0, color: 'bg-green-500' },
  ];

  const maxFunnel = Math.max(...funnel.map((f) => f.value), 1);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Licitacoes</h1>
          <p className="text-muted-foreground">
            Gestao inteligente de licitacoes publicas
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/modulos/licitacoes/ia">
            <Button variant="outline" size="sm">
              <Bot className="w-4 h-4 mr-2" />
              IA Hub
            </Button>
          </Link>
          <Link href="/modulos/licitacoes/editais">
            <Button size="sm">
              <Search className="w-4 h-4 mr-2" />
              Buscar Editais
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Link key={stat.title} href={stat.href}>
              <Card className="hover:shadow-lg transition-all cursor-pointer group">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className={`w-10 h-10 rounded-xl ${stat.bgColor} flex items-center justify-center`}>
                      <Icon className={`w-5 h-5 ${stat.color}`} />
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <div className="mt-4">
                    <p className="text-3xl font-bold">{stat.value}</p>
                    <p className="text-sm text-muted-foreground">{stat.title}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{stat.subtitle}</p>
                  </div>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Funil de Licitações */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-primary" />
              Funil de Licitacoes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {funnel.map((step, idx) => (
                <div key={step.label} className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground w-28 text-right">{step.label}</span>
                  <div className="flex-1 h-8 bg-muted rounded-lg overflow-hidden">
                    <div
                      className={`h-full ${step.color} rounded-lg flex items-center justify-end pr-3 transition-all`}
                      style={{ width: `${Math.max((step.value / maxFunnel) * 100, 5)}%` }}
                    >
                      <span className="text-xs font-bold text-white">{step.value}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Acesso Rápido */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Acesso Rapido</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {[
              { label: 'Novo Edital', href: '/modulos/licitacoes/editais', icon: FileText, color: 'text-blue-600' },
              { label: 'Nova Proposta', href: '/modulos/licitacoes/propostas', icon: FileCheck, color: 'text-orange-600' },
              { label: 'Contratos', href: '/modulos/licitacoes/contratos', icon: FileSignature, color: 'text-green-600' },
              { label: 'Certidoes', href: '/modulos/licitacoes/certidoes', icon: Award, color: 'text-amber-600' },
              { label: 'Documentos', href: '/modulos/licitacoes/documentos', icon: FileText, color: 'text-purple-600' },
              { label: 'IA Hub', href: '/modulos/licitacoes/ia', icon: Bot, color: 'text-cyan-600' },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <Link key={item.label} href={item.href}>
                  <div className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-muted transition-colors cursor-pointer group">
                    <Icon className={`w-4 h-4 ${item.color}`} />
                    <span className="text-sm font-medium flex-1">{item.label}</span>
                    <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100" />
                  </div>
                </Link>
              );
            })}
          </CardContent>
        </Card>
      </div>

      {/* Editais Recentes + Próximos Vencimentos */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Editais Recentes</CardTitle>
            <Link href="/modulos/licitacoes/editais">
              <Button variant="ghost" size="sm">Ver todos</Button>
            </Link>
          </CardHeader>
          <CardContent>
            {editaisAbertos?.items && editaisAbertos.items.length > 0 ? (
              <div className="space-y-3">
                {editaisAbertos.items.slice(0, 5).map((edital: any) => (
                  <Link key={edital.id} href={`/modulos/licitacoes/editais/${edital.id}`}>
                    <div className="flex items-start gap-3 p-2 rounded-lg hover:bg-muted transition-colors cursor-pointer">
                      <div className="w-8 h-8 rounded bg-blue-500/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <FileText className="w-4 h-4 text-blue-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{edital.title || edital.number || 'Edital'}</p>
                        <p className="text-xs text-muted-foreground truncate">
                          {(edital as any).entity || 'Orgao nao informado'}
                        </p>
                      </div>
                      <Badge variant="outline" className="text-xs flex-shrink-0">
                        {edital.status}
                      </Badge>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FileText className="w-10 h-10 text-muted-foreground/30 mx-auto mb-3" />
                <p className="text-sm text-muted-foreground">Nenhum edital cadastrado</p>
                <Link href="/modulos/licitacoes/editais">
                  <Button variant="outline" size="sm" className="mt-3">
                    Cadastrar Edital
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Proximos Vencimentos</CardTitle>
            <Link href="/modulos/licitacoes/certidoes">
              <Button variant="ghost" size="sm">Ver certidoes</Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { nome: 'CND Federal (Receita + PGFN)', orgao: 'Receita Federal', icon: Shield, color: 'text-red-600' },
                { nome: 'CNDT (Trabalhista)', orgao: 'TST', icon: Shield, color: 'text-blue-600' },
                { nome: 'CRF FGTS', orgao: 'Caixa Economica', icon: Shield, color: 'text-orange-600' },
                { nome: 'CND Estadual', orgao: 'SEFAZ-AM', icon: Shield, color: 'text-green-600' },
                { nome: 'CND Municipal', orgao: 'Prefeitura Manaus', icon: Shield, color: 'text-purple-600' },
              ].map((cert) => {
                const Icon = cert.icon;
                return (
                  <div key={cert.nome} className="flex items-center gap-3 p-2 rounded-lg">
                    <Icon className={`w-4 h-4 ${cert.color} flex-shrink-0`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{cert.nome}</p>
                      <p className="text-xs text-muted-foreground">{cert.orgao}</p>
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      Verificar
                    </Badge>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Integration Banner */}
      <Card className="border-primary/20 bg-gradient-to-r from-primary/5 to-transparent">
        <CardContent className="py-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
              <TrendingUp className="w-6 h-6 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold">Integracao ERP Completa</h3>
              <p className="text-sm text-muted-foreground">
                Licitacao → Contrato → Execucao → Medicao → Fatura → NF-e. Diferencial unico no mercado.
              </p>
            </div>
            <Link href="/modulos/licitacoes/ia">
              <Button variant="outline" size="sm">
                <Bot className="w-4 h-4 mr-2" />
                Conhecer IA Hub
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
