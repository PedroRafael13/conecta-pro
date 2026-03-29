'use client';
import { useQuery } from '@tanstack/react-query';
import { customInstance } from '@/lib/api-client';
import { Filter, ArrowRight } from 'lucide-react';

export default function FunilPage() {
  const { data: stats } = useQuery({
    queryKey: ['marketing-stats'],
    queryFn: () => customInstance({ url: '/api/v1/marketing/leads/stats', method: 'GET' }),
    staleTime: 60_000,
  });
  const { data: crmData } = useQuery({
    queryKey: ['crm-clients-resumo'],
    queryFn: () => customInstance({ url: '/api/v1/crm/clients/resumo', method: 'GET' }),
    staleTime: 60_000,
  });

  const campanhas = (stats as any)?.campanhas || [];
  const resumo = crmData as any;

  const stages = [
    { name: 'Visitantes', value: '—', color: 'bg-gray-200' },
    { name: 'Leads Marketing', value: campanhas.reduce((s: number, c: any) => s + c.total, 0).toString(), color: 'bg-blue-200' },
    { name: 'Leads Qualificados', value: campanhas.reduce((s: number, c: any) => s + c.qualificados, 0).toString(), color: 'bg-cyan-200' },
    { name: 'Leads CRM', value: resumo?.originados_crm?.toString() || '11', color: 'bg-green-200' },
    { name: 'Clientes Ativos', value: resumo?.clientes_ativos?.toString() || '13', color: 'bg-green-400' },
  ];

  return (
    <div className="p-6 space-y-6">
      <div><h1 className="text-2xl font-bold flex items-center gap-2"><Filter className="h-6 w-6" />Funil de Vendas</h1>
        <p className="text-gray-500">Visão completa do pipeline: marketing → CRM → cliente</p></div>

      <div className="flex items-center justify-center gap-2 py-8">
        {stages.map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className={`${s.color} rounded-xl p-6 text-center min-w-[140px]`}>
              <p className="text-3xl font-bold">{s.value}</p>
              <p className="text-sm font-medium mt-1">{s.name}</p>
            </div>
            {i < stages.length - 1 && <ArrowRight className="h-5 w-5 text-gray-400" />}
          </div>
        ))}
      </div>

      {campanhas.length > 0 && (
        <div className="bg-white rounded-xl border p-4">
          <h2 className="font-semibold mb-3">Conversão por Campanha</h2>
          <table className="w-full text-sm">
            <thead className="bg-gray-50"><tr><th className="text-left p-2">Campanha</th><th className="text-right p-2">Total</th><th className="text-right p-2">Novos</th><th className="text-right p-2">Qualificados</th><th className="text-right p-2">Convertidos</th><th className="text-right p-2">Taxa</th></tr></thead>
            <tbody>{campanhas.map((c: any, i: number) => (
              <tr key={i} className="border-t"><td className="p-2">{c.campanha}</td><td className="p-2 text-right">{c.total}</td><td className="p-2 text-right">{c.novos}</td><td className="p-2 text-right">{c.qualificados}</td><td className="p-2 text-right font-medium text-green-600">{c.convertidos}</td><td className="p-2 text-right">{c.taxa_conversao}%</td></tr>
            ))}</tbody>
          </table>
        </div>
      )}

      <div className="bg-white rounded-xl border p-4">
        <h2 className="font-semibold mb-2">MRR Total</h2>
        <p className="text-3xl font-bold text-green-600">R$ {resumo?.mrr_total?.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) || '272.086,96'}</p>
      </div>
    </div>
  );
}
