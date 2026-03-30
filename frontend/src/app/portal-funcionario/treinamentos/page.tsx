'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { GraduationCap, ArrowLeft, ShieldCheck, LogOut, Loader2, AlertCircle, Award, BookOpen } from 'lucide-react';

const API_BASE = '/api/v1/people-management/portal';

function getPortalHeaders(): Record<string, string> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface Enrollment {
  id: string | null;
  training_title: string | null;
  course_name: string | null;
  status: string | null;
  enrolled_at: string | null;
}

interface Certificate {
  id: string | null;
  certificate_number: string | null;
  course_name: string | null;
  issued_at: string | null;
  expires_at: string | null;
  status: string | null;
}

const statusColors: Record<string, string> = {
  concluido: 'bg-green-100 text-green-700',
  em_andamento: 'bg-blue-100 text-blue-700',
  pendente: 'bg-yellow-100 text-yellow-700',
  cancelado: 'bg-gray-100 text-gray-500',
  valido: 'bg-green-100 text-green-700',
  expirado: 'bg-red-100 text-red-600',
};

const fmtDate = (d: string | null) => d ? new Date(d).toLocaleDateString('pt-BR') : '—';

export default function TreinamentosPage() {
  const router = useRouter();
  const [employeeName, setEmployeeName] = useState('');
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState<'matriculas' | 'certificados'>('matriculas');

  useEffect(() => {
    const token = localStorage.getItem('portal_token');
    if (!token) { router.push('/portal-funcionario/login'); return; }
    setEmployeeName(localStorage.getItem('portal_employee_name') || 'Funcionário');

    async function load() {
      setLoading(true);
      setError('');
      try {
        const [enrRes, certRes] = await Promise.all([
          fetch(`${API_BASE}/my-trainings/enrollments`, { headers: getPortalHeaders() }),
          fetch(`${API_BASE}/my-trainings/certificates`, { headers: getPortalHeaders() }),
        ]);
        if (enrRes.ok) {
          const data = await enrRes.json();
          setEnrollments(Array.isArray(data) ? data : (data.items || []));
        }
        if (certRes.ok) {
          const data = await certRes.json();
          setCertificates(Array.isArray(data) ? data : (data.items || []));
        }
      } catch {
        setError('Erro ao carregar treinamentos.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [router]);

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
            <GraduationCap className="w-5 h-5 text-orange-600" /> Treinamentos
          </h2>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4 flex items-center gap-2 text-red-700 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setTab('matriculas')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition ${tab === 'matriculas' ? 'bg-[#0A2540] text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}
          >
            <BookOpen className="w-4 h-4" /> Matrículas ({enrollments.length})
          </button>
          <button
            onClick={() => setTab('certificados')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition ${tab === 'certificados' ? 'bg-[#0A2540] text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}
          >
            <Award className="w-4 h-4" /> Certificados ({certificates.length})
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : tab === 'matriculas' ? (
          enrollments.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-8 text-center text-gray-400">
              <BookOpen className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p className="text-sm">Nenhuma matrícula encontrada.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {enrollments.map((e, i) => (
                <div key={e.id || i} className="bg-white rounded-xl shadow-sm p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-gray-900">{e.training_title || e.course_name || 'Treinamento'}</p>
                      {e.course_name && e.training_title !== e.course_name && (
                        <p className="text-xs text-gray-500 mt-0.5">{e.course_name}</p>
                      )}
                      <p className="text-xs text-gray-400 mt-1">Matriculado em {fmtDate(e.enrolled_at)}</p>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full font-medium flex-shrink-0 ${statusColors[e.status || ''] || 'bg-gray-100 text-gray-600'}`}>
                      {e.status || 'pendente'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )
        ) : (
          certificates.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-8 text-center text-gray-400">
              <Award className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p className="text-sm">Nenhum certificado encontrado.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {certificates.map((c, i) => (
                <div key={c.id || i} className="bg-white rounded-xl shadow-sm p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-gray-900">{c.course_name || 'Curso'}</p>
                      {c.certificate_number && (
                        <p className="text-xs text-gray-500 mt-0.5">Nº {c.certificate_number}</p>
                      )}
                      <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                        <span>Emitido: {fmtDate(c.issued_at)}</span>
                        {c.expires_at && <span>Expira: {fmtDate(c.expires_at)}</span>}
                      </div>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full font-medium flex-shrink-0 ${statusColors[c.status || ''] || 'bg-gray-100 text-gray-600'}`}>
                      {c.status || 'válido'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )
        )}
      </main>
    </div>
  );
}
