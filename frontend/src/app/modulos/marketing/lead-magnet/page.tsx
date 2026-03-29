'use client';
import { useQuery } from '@tanstack/react-query';
import { customInstance } from '@/lib/api-client';
import { Magnet, Download, Users } from 'lucide-react';

export default function LeadMagnetPage() {
  const { data } = useQuery({
    queryKey: ['marketing-leads'],
    queryFn: () => customInstance({ url: '/api/v1/marketing/leads/', method: 'GET' }),
    staleTime: 30_000,
  });
  const leads = (data as any)?.items || [];

  return (
    <div className="p-6 space-y-6">
      <div><h1 className="text-2xl font-bold flex items-center gap-2"><Magnet className="h-6 w-6" />Lead Magnets</h1>
        <p className="text-gray-500">Iscas digitais para captura de leads qualificados</p></div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border p-4"><div className="text-gray-500 text-sm flex items-center gap-1"><Users className="h-4 w-4" />Total Leads</div><p className="text-2xl font-bold">{leads.length}</p></div>
        <div className="bg-white rounded-xl border p-4"><div className="text-gray-500 text-sm flex items-center gap-1"><Download className="h-4 w-4" />Novos</div><p className="text-2xl font-bold">{leads.filter((l: any) => l.status === 'new').length}</p></div>
        <div className="bg-white rounded-xl border p-4"><div className="text-gray-500 text-sm">Convertidos</div><p className="text-2xl font-bold text-green-600">{leads.filter((l: any) => l.status === 'converted').length}</p></div>
      </div>

      <div className="bg-white rounded-xl border p-6 space-y-4">
        <h2 className="font-semibold text-lg">Ideias de Lead Magnets para Segurança Patrimonial</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { title: 'Checklist de Segurança Condominial', desc: 'PDF com 30 itens essenciais para avaliar a segurança do condomínio' },
            { title: 'Guia de Redução de Custos com Portaria', desc: 'Comparativo portaria presencial vs remota com simulação de economia' },
            { title: 'Template de Proposta de Segurança', desc: 'Modelo editável para síndicos solicitarem orçamentos' },
            { title: 'Calculadora de Custo de Segurança', desc: 'Planilha interativa para estimar investimento mensal' },
          ].map((lm, i) => (
            <div key={i} className="border rounded-lg p-4 hover:border-cyan-300 transition-colors">
              <h3 className="font-medium">{lm.title}</h3>
              <p className="text-sm text-gray-500 mt-1">{lm.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {leads.length > 0 && (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50"><tr><th className="text-left p-3">Lead</th><th className="text-left p-3">Email</th><th className="text-left p-3">Campanha</th><th className="text-left p-3">Status</th></tr></thead>
            <tbody>{leads.map((l: any) => (
              <tr key={l.id} className="border-t hover:bg-gray-50"><td className="p-3 font-medium">{l.name}</td><td className="p-3">{l.email || '—'}</td><td className="p-3">{l.campaign_name || '—'}</td><td className="p-3"><span className={`px-2 py-0.5 rounded text-xs ${l.status === 'converted' ? 'bg-green-100 text-green-700' : 'bg-gray-100'}`}>{l.status}</span></td></tr>
            ))}</tbody>
          </table>
        </div>
      )}
    </div>
  );
}
