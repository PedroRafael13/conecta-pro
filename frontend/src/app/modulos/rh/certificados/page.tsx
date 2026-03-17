'use client';

import { useState, useEffect } from 'react';
import { Award, AlertTriangle, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

const API_BASE = '/api/v1/people-management/human-resources';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

const tabs = ['Validos', 'Vencendo', 'Vencidos'] as const;
const tabFilter: Record<string, string[]> = {
  'Validos': ['valid', 'Valido'],
  'Vencendo': ['expiring', 'Vencendo'],
  'Vencidos': ['expired', 'Vencido'],
};

const statusCores: Record<string, string> = {
  'valid': 'text-green-400', 'Valido': 'text-green-400',
  'expiring': 'text-yellow-400', 'Vencendo': 'text-yellow-400',
  'expired': 'text-red-400', 'Vencido': 'text-red-400',
};

const statusLabels: Record<string, string> = {
  valid: 'Valido', expiring: 'Vencendo', expired: 'Vencido',
};

const StatusIcon = ({ status }: { status: string }) => {
  if (status === 'valid' || status === 'Valido') return <CheckCircle className="h-4 w-4 text-green-400" />;
  if (status === 'expiring' || status === 'Vencendo') return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
  return <XCircle className="h-4 w-4 text-red-400" />;
};

export default function CertificadosPage() {
  const [activeTab, setActiveTab] = useState<string>('Validos');
  const [certificados, setCertificados] = useState<any[]>([]);
  const [expiring, setExpiring] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [enrRes, expRes] = await Promise.all([
          fetch(`${API_BASE}/training/enrollments?limit=100`, { headers: getAuthHeaders() }),
          fetch(`${API_BASE}/training/certificates/expiring`, { headers: getAuthHeaders() }),
        ]);
        if (enrRes.ok) {
          const data = await enrRes.json();
          // Filter enrollments that have certificates
          const items = (data.items || data || []).filter((e: any) => e.certificate_number || e.certificate_id);
          setCertificados(items);
        }
        if (expRes.ok) {
          const data = await expRes.json();
          setExpiring(data.items || data || []);
        }
      } catch { setCertificados([]); } finally { setLoading(false); }
    }
    load();
  }, []);

  const filtered = certificados.filter(c => tabFilter[activeTab]?.includes(c.status));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Award className="h-6 w-6" />
          Certificados
        </h1>
        <p className="text-muted-foreground">Controle de certificados dos colaboradores</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : (
        <>
          {expiring.length > 0 && (
            <Card className="border-yellow-800 bg-yellow-900/10">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-yellow-400">
                  <AlertTriangle className="h-5 w-5" />
                  <span className="font-medium">{expiring.length} certificado(s) vencendo nos proximos 30 dias</span>
                </div>
                <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                  {expiring.map((c, i) => <li key={i}>{c.employee_name || c.colaborador} - {c.course_name || c.curso} (validade: {c.expires_at || c.validade})</li>)}
                </ul>
              </CardContent>
            </Card>
          )}

          <div className="flex gap-2 border-b border-gray-800 pb-0">
            {tabs.map(tab => (
              <button key={tab} onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === tab ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-white'}`}>
                {tab} ({certificados.filter(c => tabFilter[tab]?.includes(c.status)).length})
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
                    ) : filtered.map((c, i) => {
                      const label = statusLabels[c.status] || c.status;
                      return (
                        <tr key={c.id || i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                          <td className="p-4 font-medium">{c.employee_name || c.colaborador}</td>
                          <td className="p-4 text-muted-foreground">{c.course_name || c.curso}</td>
                          <td className="p-4 text-muted-foreground font-mono text-xs">{c.certificate_number || c.numero}</td>
                          <td className="p-4 text-muted-foreground">{c.issued_at || c.emissao}</td>
                          <td className="p-4 text-muted-foreground">{c.expires_at || c.validade}</td>
                          <td className="p-4 text-center"><div className="flex items-center justify-center gap-1"><StatusIcon status={c.status} /><span className={statusCores[c.status] || 'text-gray-400'}>{label}</span></div></td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
