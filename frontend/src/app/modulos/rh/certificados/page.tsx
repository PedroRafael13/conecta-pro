'use client';

import { Award, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const certificadosMock = [
  { id: 1, colaborador: 'Joao Silva', curso: 'Vigilancia Patrimonial', numero: 'CERT-2025-001', emissao: '2025-06-15', validade: '2026-06-15', status: 'Valido' },
  { id: 2, colaborador: 'Maria Santos', curso: 'Primeiros Socorros', numero: 'CERT-2025-042', emissao: '2025-04-10', validade: '2026-04-10', status: 'Vencendo' },
  { id: 3, colaborador: 'Carlos Mendes', curso: 'Combate a Incendio', numero: 'CERT-2024-088', emissao: '2024-01-20', validade: '2025-01-20', status: 'Vencido' },
  { id: 4, colaborador: 'Ana Beatriz', curso: 'CFTV e Monitoramento', numero: 'CERT-2025-103', emissao: '2025-09-01', validade: '2026-09-01', status: 'Valido' },
  { id: 5, colaborador: 'Roberto Lima', curso: 'Vigilancia Patrimonial', numero: 'CERT-2025-055', emissao: '2025-03-20', validade: '2026-03-20', status: 'Vencendo' },
  { id: 6, colaborador: 'Patricia Costa', curso: 'Primeiros Socorros', numero: 'CERT-2024-071', emissao: '2024-08-15', validade: '2025-08-15', status: 'Vencido' },
];

const tabs = ['Validos', 'Vencendo', 'Vencidos'] as const;
const tabFilter: Record<string, string> = { 'Validos': 'Valido', 'Vencendo': 'Vencendo', 'Vencidos': 'Vencido' };

const statusCores: Record<string, string> = {
  'Valido': 'text-green-400',
  'Vencendo': 'text-yellow-400',
  'Vencido': 'text-red-400',
};

const StatusIcon = ({ status }: { status: string }) => {
  if (status === 'Valido') return <CheckCircle className="h-4 w-4 text-green-400" />;
  if (status === 'Vencendo') return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
  return <XCircle className="h-4 w-4 text-red-400" />;
};

export default function CertificadosPage() {
  const [activeTab, setActiveTab] = useState<string>('Validos');
  const filtered = certificadosMock.filter(c => c.status === tabFilter[activeTab]);
  const vencendo = certificadosMock.filter(c => c.status === 'Vencendo');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Award className="h-6 w-6" />
          Certificados
        </h1>
        <p className="text-muted-foreground">Controle de certificados dos colaboradores</p>
      </div>

      {vencendo.length > 0 && (
        <Card className="border-yellow-800 bg-yellow-900/10">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-yellow-400">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-medium">{vencendo.length} certificado(s) vencendo nos proximos 30 dias</span>
            </div>
            <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
              {vencendo.map(c => <li key={c.id}>{c.colaborador} - {c.curso} (validade: {c.validade})</li>)}
            </ul>
          </CardContent>
        </Card>
      )}

      <div className="flex gap-2 border-b border-gray-800 pb-0">
        {tabs.map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === tab ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-white'}`}>
            {tab} ({certificadosMock.filter(c => c.status === tabFilter[tab]).length})
          </button>
        ))}
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left p-4 text-muted-foreground font-medium">Colaborador</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Curso</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Numero</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Emissao</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Validade</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr><td colSpan={6} className="p-8 text-center text-muted-foreground">Nenhum certificado nesta categoria</td></tr>
                ) : filtered.map(c => (
                  <tr key={c.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="p-4 font-medium">{c.colaborador}</td>
                    <td className="p-4 text-muted-foreground">{c.curso}</td>
                    <td className="p-4 text-muted-foreground font-mono text-xs">{c.numero}</td>
                    <td className="p-4 text-muted-foreground">{c.emissao}</td>
                    <td className="p-4 text-muted-foreground">{c.validade}</td>
                    <td className="p-4 text-center"><div className="flex items-center justify-center gap-1"><StatusIcon status={c.status} /><span className={statusCores[c.status]}>{c.status}</span></div></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
