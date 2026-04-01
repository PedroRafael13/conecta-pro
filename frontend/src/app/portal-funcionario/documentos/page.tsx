'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { FolderOpen, ArrowLeft, ShieldCheck, LogOut, Loader2, AlertCircle, CheckCircle2, PenLine, FileText, Clock } from 'lucide-react';

const API_BASE = '/api/v1/people-management/portal';

function getPortalHeaders(): Record<string, string> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface Document {
  id: number;
  title: string;
  document_type: string;
  description: string | null;
  is_signed: boolean;
  signed_at: string | null;
  requires_signature: boolean;
  created_at: string | null;
}

const docTypeLabel: Record<string, string> = {
  contract: 'Contrato',
  addendum: 'Aditivo',
  policy: 'Política',
  admission: 'Admissão',
  termination: 'Rescisão',
  other: 'Outro',
};

const fmtDate = (d: string | null) => d ? new Date(d).toLocaleDateString('pt-BR') : '—';

export default function DocumentosPage() {
  const router = useRouter();
  const [employeeName, setEmployeeName] = useState('');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [signingId, setSigningId] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('portal_token');
    if (!token) { router.push('/portal-funcionario/login'); return; }
    setEmployeeName(localStorage.getItem('portal_employee_name') || 'Funcionário');
    loadDocuments();
  }, [router]);

  async function loadDocuments() {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/my-documents`, { headers: getPortalHeaders() });
      if (res.ok) {
        const data = await res.json();
        setDocuments(Array.isArray(data) ? data : (data.documents || []));
      } else {
        setDocuments([]);
      }
    } catch {
      setError('Erro ao carregar documentos.');
    } finally {
      setLoading(false);
    }
  }

  async function signDocument(doc: Document) {
    setSigningId(doc.id);
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${API_BASE}/my-documents/${doc.id}/sign`, {
        method: 'POST',
        headers: getPortalHeaders(),
        body: JSON.stringify({ document_id: doc.id, signature_type: 'digital' }),
      });
      if (res.ok) {
        setSuccess(`Documento "${doc.title}" assinado com sucesso!`);
        await loadDocuments();
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data.detail || 'Erro ao assinar documento.');
      }
    } catch {
      setError('Erro ao assinar documento.');
    } finally {
      setSigningId(null);
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('portal_token');
    localStorage.removeItem('portal_refresh_token');
    localStorage.removeItem('portal_employee_name');
    router.push('/portal-funcionario/login');
  };

  const pendentes = documents.filter(d => d.requires_signature && !d.is_signed);
  const assinados = documents.filter(d => d.is_signed);
  const outros = documents.filter(d => !d.requires_signature && !d.is_signed);

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
            <FolderOpen className="w-5 h-5 text-purple-600" /> Documentos
          </h2>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4 flex items-center gap-2 text-red-700 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
          </div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-4 flex items-center gap-2 text-green-700 text-sm">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" /> {success}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : documents.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-8 text-center text-gray-400">
            <FolderOpen className="w-10 h-10 mx-auto mb-2 opacity-30" />
            <p>Nenhum documento disponível.</p>
          </div>
        ) : (
          <div className="space-y-5">
            {pendentes.length > 0 && (
              <section>
                <h3 className="text-sm font-semibold text-orange-600 uppercase tracking-wide flex items-center gap-2 mb-3">
                  <Clock className="w-4 h-4" /> Pendentes de Assinatura ({pendentes.length})
                </h3>
                <div className="space-y-3">
                  {pendentes.map(doc => (
                    <div key={doc.id} className="bg-white rounded-xl shadow-sm border border-orange-100 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-gray-900 truncate">{doc.title}</p>
                          <p className="text-xs text-gray-500 mt-0.5">{docTypeLabel[doc.document_type] || doc.document_type} · {fmtDate(doc.created_at)}</p>
                          {doc.description && <p className="text-sm text-gray-600 mt-1">{doc.description}</p>}
                        </div>
                        <button
                          onClick={() => signDocument(doc)}
                          disabled={signingId === doc.id}
                          className="flex items-center gap-1.5 bg-[#0A2540] hover:bg-[#1E3A5F] text-white text-sm px-4 py-2 rounded-lg transition disabled:opacity-50 whitespace-nowrap flex-shrink-0"
                        >
                          {signingId === doc.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <PenLine className="w-4 h-4" />}
                          Assinar
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {assinados.length > 0 && (
              <section>
                <h3 className="text-sm font-semibold text-green-600 uppercase tracking-wide flex items-center gap-2 mb-3">
                  <CheckCircle2 className="w-4 h-4" /> Assinados ({assinados.length})
                </h3>
                <div className="space-y-3">
                  {assinados.map(doc => (
                    <div key={doc.id} className="bg-white rounded-xl shadow-sm p-4 flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{doc.title}</p>
                        <p className="text-xs text-gray-500">{docTypeLabel[doc.document_type] || doc.document_type} · Assinado em {fmtDate(doc.signed_at)}</p>
                      </div>
                      <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
                    </div>
                  ))}
                </div>
              </section>
            )}

            {outros.length > 0 && (
              <section>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide flex items-center gap-2 mb-3">
                  <FileText className="w-4 h-4" /> Outros ({outros.length})
                </h3>
                <div className="space-y-3">
                  {outros.map(doc => (
                    <div key={doc.id} className="bg-white rounded-xl shadow-sm p-4">
                      <p className="font-medium text-gray-900">{doc.title}</p>
                      <p className="text-xs text-gray-500">{docTypeLabel[doc.document_type] || doc.document_type} · {fmtDate(doc.created_at)}</p>
                      {doc.description && <p className="text-sm text-gray-600 mt-1">{doc.description}</p>}
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
