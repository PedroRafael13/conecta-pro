'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Clock,
  AlertTriangle,
  Timer,
  RefreshCw,
  ChevronRight,
  Fingerprint,
  FileText,
  CalendarX,
  Hourglass,
  Lock,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

const summaryCards = [
  { label: 'Batidas Hoje', value: '3 / 4', icon: Fingerprint, color: 'text-blue-600', bg: 'bg-blue-50', detail: 'Falta 1 batida' },
  { label: 'Atrasos no Mes', value: '2', icon: AlertTriangle, color: 'text-amber-600', bg: 'bg-amber-50', detail: 'Total: 47 min' },
  { label: 'Banco de Horas', value: '+12:30', icon: Timer, color: 'text-green-600', bg: 'bg-green-50', detail: 'Saldo positivo' },
  { label: 'Sync eSocial', value: 'OK', icon: RefreshCw, color: 'text-purple-600', bg: 'bg-purple-50', detail: 'Ultimo: hoje 06:00' },
];

const quickLinks = [
  { label: 'Bater Ponto', href: '/modulos/gestao-pessoas/ponto/batida', icon: Fingerprint, color: 'text-blue-600', bg: 'bg-blue-50' },
  { label: 'Espelho de Ponto', href: '/modulos/gestao-pessoas/ponto/espelho', icon: FileText, color: 'text-indigo-600', bg: 'bg-indigo-50' },
  { label: 'Justificativas', href: '/modulos/gestao-pessoas/ponto/justificativas', icon: FileText, color: 'text-amber-600', bg: 'bg-amber-50' },
  { label: 'Atrasos e Faltas', href: '/modulos/gestao-pessoas/ponto/atrasos', icon: CalendarX, color: 'text-red-600', bg: 'bg-red-50' },
  { label: 'Banco de Horas', href: '/modulos/gestao-pessoas/ponto/banco-horas', icon: Hourglass, color: 'text-green-600', bg: 'bg-green-50' },
  { label: 'Fechamento Mensal', href: '/modulos/gestao-pessoas/ponto/fechamento', icon: Lock, color: 'text-gray-600', bg: 'bg-gray-100' },
];

export default function PontoDashboardPage() {
  const router = useRouter();
  const [currentTime] = useState(new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }));

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Clock className="w-6 h-6 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Controle de Ponto</h1>
            <p className="text-gray-500 mt-1">Gestao de jornada, batidas e banco de horas</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold text-gray-900">{currentTime}</p>
          <p className="text-sm text-gray-500">{new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {summaryCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="border border-gray-200">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">{stat.label}</p>
                    <p className="text-2xl font-bold mt-1">{stat.value}</p>
                    <p className="text-xs text-gray-400 mt-1">{stat.detail}</p>
                  </div>
                  <div className={`p-3 rounded-lg ${stat.bg}`}>
                    <Icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {quickLinks.map((link) => {
          const Icon = link.icon;
          return (
            <Card
              key={link.href}
              className="cursor-pointer hover:shadow-lg transition-all duration-200 border border-gray-200 hover:border-gray-300"
              onClick={() => router.push(link.href)}
            >
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${link.bg}`}>
                      <Icon className={`h-5 w-5 ${link.color}`} />
                    </div>
                    <span className="font-medium text-gray-900">{link.label}</span>
                  </div>
                  <ChevronRight className="h-5 w-5 text-gray-400" />
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
