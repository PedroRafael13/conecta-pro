'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { FileText, Download, ChevronLeft, ChevronRight, ArrowLeft, ShieldCheck, LogOut, Loader2, AlertCircle } from 'lucide-react';

const API_BASE = '/api/v1/people-management/portal';

function getPortalHeaders(): Record<string, string> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

const MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
const fmt = (v: number) => `R$ ${(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

interface Payslip {
  month: number;
  year: number;
  reference: string;
  gross_salary: number;
  net_salary: number;
  deductions: number;
  status: string;
  items?: Array<{ description: string; type: string; value: number }>;
}

export default function ContracheqquesPage() {
  const router = useRouter();
  const [employeeName, setEmployeeName] = useState('');
  const [year, setYear] = useState(new Date().getFullYear());
  const [payslips, setPayslips] = useState<Payslip[]>([]);
  const [selected, setSelected] = useState<Payslip | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('portal_token');
    if (!token) { router.push('/portal-funcionario/login'); return; }
    setEmployeeName(localStorage.getItem('portal_employee_name') || 'Funcionário');
  }, [router]);

  const loadPayslips = useCallback(async () => {
    setLoading(true);
    setError('');
    setSelected(null);
    try {
      const res = await fetch(`${API_BASE}/my-payslips?year=${year}`, { headers: getPortalHeaders() });
      if (res.ok) {
        const data: Payslip[] = await res.json();
        setPayslips(data);
      } else {
        setPayslips([]);
      }
    } catch {
      setError('Erro ao carregar contracheques.');
    } finally {
      setLoading(false);
    }
  }, [year]);

  useEffect(() => { loadPayslips(); }, [loadPayslips]);

  const loadDetail = async (p: Payslip) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/my-payslips/${p.month}/${p.year}`, { headers: getPortalHeaders() });
      if (res.ok) setSelected(await res.json());
      else setSelected(p);
    } catch { setSelected(p); } finally { setLoading(false); }
  };

  const downloadPdf = async (p: Payslip) => {
    setDownloading(true);
    try {
      const res = await fetch(`${API_BASE}/my-payslips/${p.month}/${p.year}/pdf`, { headers: getPortalHeaders() });
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `contracheque_${String(p.month).padStart(2,'0')}_${p.year}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch { /* ignore */ } finally { setDownloading(false); }
  };

  const handleLogout = () => {
    localStorage.removeItem('portal_token');
    localStorage.removeItem('portal_refresh_token');
    localStorage.removeItem('portal_employee_name');
    router.push('/portal-funcionario/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-[#0A2540] text-white">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-6 h-6 text-blue-300" />
            <div>
              <h1 className="text-base font-bold leading-none">CONECTA PRO</h1>
              <p className="text-xs text-blue-300">Portal do Funcionário</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-blue-200 hidden sm:block">{employeeName}</span>
            <button onClick={handleLogout} className="text-blue-300 hover:text-white" title="Sair">
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-6">
        <div className="flex items-center gap-3 mb-6">
          <Link href="/portal-funcionario/dashboard" className="text-gray-500 hover:text-gray-700">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" /> Contracheques
          </h2>
        </div>

        {/* Seletor de ano */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-4 flex items-center justify-between">
          <button onClick={() => setYear(y => y - 1)} className="p-2 rounded-lg hover:bg-gray-100 transition">
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </button>
          <span className="text-lg font-semibold text-gray-900">{year}</span>
          <button onClick={() => setYear(y => y + 1)} disabled={year >= new Date().getFullYear()} className="p-2 rounded-lg hover:bg-gray-100 transition disabled:opacity-40">
            <ChevronRight className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4 flex items-center gap-2 text-red-700 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : selected ? (
          /* Detalhe do contracheque */
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="p-4 bg-blue-600 text-white flex items-center justify-between">
              <div>
                <p className="text-sm opacity-80">Competência</p>
                <p className="text-lg font-bold">{MESES[(selected.month || 1) - 1]}/{selected.year}</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => downloadPdf(selected)}
                  disabled={downloading}
                  className="flex items-center gap-1.5 bg-white/20 hover:bg-white/30 text-white text-sm px-3 py-2 rounded-lg transition"
                >
                  {downloading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                  PDF
                </button>
                <button onClick={() => setSelected(null)} className="bg-white/20 hover:bg-white/30 text-white text-sm px-3 py-2 rounded-lg transition">
                  Voltar
                </button>
              </div>
            </div>
            <div className="p-4 space-y-3">
              {(selected.items || []).length > 0 ? (
                <>
                  <div className="grid grid-cols-3 text-xs font-semibold text-gray-500 uppercase pb-2 border-b">
                    <span>Descrição</span>
                    <span className="text-center">Tipo</span>
                    <span className="text-right">Valor</span>
                  </div>
                  {selected.items!.map((item, i) => (
                    <div key={i} className="grid grid-cols-3 text-sm py-1.5 border-b border-gray-50">
                      <span className="text-gray-700">{item.description}</span>
                      <span className={`text-center font-medium ${item.type === 'provento' ? 'text-green-600' : 'text-red-500'}`}>
                        {item.type === 'provento' ? 'Provento' : 'Desconto'}
                      </span>
                      <span className="text-right text-gray-900">{fmt(item.value)}</span>
                    </div>
                  ))}
                </>
              ) : (
                <p className="text-gray-400 text-sm text-center py-4">Sem itens detalhados.</p>
              )}
              <div className="mt-4 grid grid-cols-3 gap-3">
                <div className="bg-green-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-500">Bruto</p>
                  <p className="text-sm font-bold text-green-700">{fmt(selected.gross_salary)}</p>
                </div>
                <div className="bg-red-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-500">Descontos</p>
                  <p className="text-sm font-bold text-red-600">{fmt(selected.deductions)}</p>
                </div>
                <div className="bg-blue-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-500">Líquido</p>
                  <p className="text-sm font-bold text-blue-700">{fmt(selected.net_salary)}</p>
                </div>
              </div>
            </div>
          </div>
        ) : payslips.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-8 text-center text-gray-400">
            <FileText className="w-10 h-10 mx-auto mb-2 opacity-30" />
            <p>Nenhum contracheque encontrado para {year}.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {payslips.map((p) => (
              <div key={`${p.month}-${p.year}`} className="bg-white rounded-xl shadow-sm p-4 flex items-center justify-between hover:shadow-md transition cursor-pointer" onClick={() => loadDetail(p)}>
                <div>
                  <p className="font-semibold text-gray-900">{MESES[(p.month || 1) - 1]} / {p.year}</p>
                  <p className="text-sm text-gray-500">Líquido: <span className="font-medium text-blue-700">{fmt(p.net_salary)}</span></p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${p.status === 'pago' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                    {p.status || 'processado'}
                  </span>
                  <button
                    onClick={(e) => { e.stopPropagation(); downloadPdf(p); }}
                    disabled={downloading}
                    className="p-2 hover:bg-gray-100 rounded-lg transition text-gray-400 hover:text-gray-700"
                    title="Baixar PDF"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
