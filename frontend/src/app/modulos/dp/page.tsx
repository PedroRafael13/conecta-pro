'use client';

import {
  Users, UserPlus, UserMinus, FileText, Clock, DollarSign,
  Gift, Sun, ShieldCheck, FolderOpen, ArrowRight, CalendarDays,
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function DPDashboardPage() {
  const router = useRouter();

  const statCards = [
    {
      title: 'Colaboradores Ativos',
      value: 44,
      subtitle: '3 admitidos nos ultimos 30 dias',
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Admissoes este Mes',
      value: 2,
      subtitle: '1 pendente de documentacao',
      icon: UserPlus,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Ferias em Andamento',
      value: 3,
      subtitle: '5 programadas para o proximo mes',
      icon: Sun,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
    {
      title: 'Folha Atual (R$)',
      value: '187.450,00',
      subtitle: 'Competencia Mar/2026',
      icon: DollarSign,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
  ];

  const navCards = [
    { title: 'Admissao', description: 'Processos de admissao de colaboradores', icon: UserPlus, href: '/modulos/dp/admissao', color: 'text-green-600', bgColor: 'bg-green-50' },
    { title: 'Rescisao', description: 'Processos de desligamento e rescisao', icon: UserMinus, href: '/modulos/dp/rescisao', color: 'text-red-600', bgColor: 'bg-red-50' },
    { title: 'Contratos', description: 'Contratos de trabalho dos colaboradores', icon: FileText, href: '/modulos/dp/contratos', color: 'text-blue-600', bgColor: 'bg-blue-50' },
    { title: 'Ponto Eletronico', description: 'Registro e controle de ponto', icon: Clock, href: '/modulos/dp/ponto', color: 'text-cyan-600', bgColor: 'bg-cyan-50' },
    { title: 'Folha Salarial', description: 'Folha de pagamento e encargos', icon: DollarSign, href: '/modulos/dp/folha', color: 'text-purple-600', bgColor: 'bg-purple-50' },
    { title: 'Beneficios', description: 'Gestao de beneficios dos colaboradores', icon: Gift, href: '/modulos/dp/beneficios', color: 'text-pink-600', bgColor: 'bg-pink-50' },
    { title: 'Ferias', description: 'Programacao e controle de ferias', icon: Sun, href: '/modulos/dp/ferias', color: 'text-orange-600', bgColor: 'bg-orange-50' },
    { title: 'Licencas', description: 'Licencas e afastamentos', icon: CalendarDays, href: '/modulos/dp/licencas', color: 'text-yellow-600', bgColor: 'bg-yellow-50' },
    { title: 'eSocial', description: 'Eventos e obrigacoes do eSocial', icon: ShieldCheck, href: '/modulos/dp/esocial', color: 'text-indigo-600', bgColor: 'bg-indigo-50' },
    { title: 'Documentos', description: 'Documentos dos colaboradores', icon: FolderOpen, href: '/modulos/dp/documentos', color: 'text-slate-600', bgColor: 'bg-slate-50' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Users className="h-6 w-6" />
          Departamento Pessoal
        </h1>
        <p className="text-muted-foreground">
          Gestao completa de colaboradores, folha, ponto e beneficios
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <Card key={card.title}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{card.title}</p>
                  <p className="text-2xl font-bold">{card.value}</p>
                  <p className="text-xs text-muted-foreground mt-1">{card.subtitle}</p>
                </div>
                <div className={`h-10 w-10 rounded-lg ${card.bgColor} flex items-center justify-center`}>
                  <card.icon className={`h-5 w-5 ${card.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        {navCards.map((card) => (
          <Card
            key={card.title}
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => router.push(card.href)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
              <card.icon className={`h-5 w-5 ${card.color}`} />
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{card.description}</p>
              <div className="flex items-center gap-1 mt-3 text-xs text-primary">
                <span>Acessar</span>
                <ArrowRight className="h-3 w-3" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
