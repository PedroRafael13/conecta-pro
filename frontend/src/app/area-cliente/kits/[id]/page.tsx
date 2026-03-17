'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft, Download, FileText, User, Building2, Loader2, ShieldCheck, PenLine,
} from 'lucide-react';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || '') + '/api/v1/portal';

function getPortalHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface KitDetail {
  id: number;
  mes_referencia: string;
  status: string;
  percentual_conclusao: number;
}

interface KitDocument {
  id: number;
  nome: string;
  tipo: string;
  categoria: 'funcionario' | 'empresa';
  funcionario_nome?: string;
  assinado: boolean;
  url_download?: string;
}

const statusLabels: Record<string, string> = {
  em_montagem: 'Em Montagem',
  completo: 'Completo',
  enviado: 'Enviado',
  conferido: 'Conferido',
  aprovado: 'Aprovado',
};

const statusColors: Record<string, string> = {
  em_montagem: 'bg-yellow-100 text-yellow-800',
  completo: 'bg-blue-100 text-blue-800',
  enviado: 'bg-green-100 text-green-800',
  conferido: 'bg-purple-100 text-purple-800',
  aprovado: 'bg-emerald-100 text-emerald-800',
};

export default function KitDetailPage() {
  const params = useParams();
  const kitId = params.id as string;
  const [kit, setKit] = useState<KitDetail | null>(null);
  const [documents, setDocuments] = useState<KitDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [approving, setApproving] = useState(false);
  const [downloadingZip, setDownloadingZip] = useState(false);

  useEffect(() => {
    async function fetchKit() {
      try {
        const [kitRes, docsRes] = await Promise.all([
          fetch(`${API_BASE}/kits/${kitId}`, { headers: getPortalHeaders() }),
          fetch(`${API_BASE}/kits/${kitId}/documents`, { headers: getPortalHeaders() }),
        ]);
        if (kitRes.ok) setKit(await kitRes.json());
        if (docsRes.ok) {
          const d = await docsRes.json();
          setDocuments(Array.isArray(d) ? d : d.items || []);
        }
      } catch {
        // silently handle
      } finally {
        setLoading(false);
      }
    }
    fetchKit();
  }, [kitId]);

  async function handleApprove() {
    if (!confirm('Deseja aprovar este kit? Esta ação não pode ser desfeita.')) return;
    setApproving(true);
    try {
      const res = await fetch(`${API_BASE}/kits/${kitId}/approve`, {
        method: 'POST',
        headers: getPortalHeaders(),
      });
      if (res.ok) {
        setKit((prev) => (prev ? { ...prev, status: 'aprovado' } : prev));
      }
    } catch {
      // silently handle
    } finally {
      setApproving(false);
    }
  }

  async function handleDownloadZip() {
    setDownloadingZip(true);
    try {
      const token = localStorage.getItem('portal_token');
      const res = await fetch(`${API_BASE}/kits/${kitId}/download`, {
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `kit-${kit?.mes_referencia || kitId}.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch {
      // silently handle
    } finally {
      setDownloadingZip(false);
    }
  }

  function handleDownloadDoc(doc: KitDocument) {
    if (doc.url_download) {
      window.open(doc.url_download, '_blank');
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (!kit) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-500">Kit não encontrado.</p>
        <Link href="/area-cliente/kits" className="text-indigo-600 hover:underline text-sm mt-2 inline-block">
          Voltar para Meus Kits
        </Link>
      </div>
    );
  }

  const employeeDocs = documents.filter((d) => d.categoria === 'funcionario');
  const companyDocs = documents.filter((d) => d.categoria === 'empresa');
  const canApprove = ['enviado', 'conferido'].includes(kit.status);

  // Group employee docs by employee name
  const groupedByEmployee: Record<string, KitDocument[]> = {};
  employeeDocs.forEach((doc) => {
    const name = doc.funcionario_nome || 'Sem Nome';
    if (!groupedByEmployee[name]) groupedByEmployee[name] = [];
    groupedByEmployee[name].push(doc);
  });

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        href="/area-cliente/kits"
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-indigo-600 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Voltar para Meus Kits
      </Link>

      {/* Kit Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Kit {kit.mes_referencia}</h1>
            <span
              className={`inline-block mt-2 text-xs font-medium px-3 py-1 rounded-full ${
                statusColors[kit.status] || 'bg-gray-100 text-gray-600'
              }`}
            >
              {statusLabels[kit.status] || kit.status}
            </span>
          </div>
          <div className="w-48">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Conclusão</span>
              <span className="font-medium">{kit.percentual_conclusao}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-indigo-600 h-2.5 rounded-full transition-all"
                style={{ width: `${kit.percentual_conclusao}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Documents by Employee */}
      {Object.keys(groupedByEmployee).length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center gap-2">
            <User className="h-5 w-5 text-indigo-600" />
            <h2 className="text-lg font-semibold text-gray-900">Documentos por Funcionário</h2>
          </div>
          <div className="divide-y divide-gray-100">
            {Object.entries(groupedByEmployee).map(([name, docs]) => (
              <div key={name} className="px-6 py-4">
                <p className="text-sm font-medium text-gray-700 mb-3">{name}</p>
                <div className="space-y-2 pl-4">
                  {docs.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between py-1.5">
                      <div className="flex items-center gap-3">
                        <FileText className="h-4 w-4 text-gray-400" />
                        <span className="text-sm text-gray-700">{doc.nome}</span>
                        <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">
                          {doc.tipo}
                        </span>
                        {doc.assinado ? (
                          <span title="Assinado"><PenLine className="h-4 w-4 text-green-500" /></span>
                        ) : null}
                      </div>
                      <button
                        onClick={() => handleDownloadDoc(doc)}
                        className="text-indigo-600 hover:text-indigo-800 p-1"
                        title="Baixar"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Company Documents */}
      {companyDocs.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center gap-2">
            <Building2 className="h-5 w-5 text-indigo-600" />
            <h2 className="text-lg font-semibold text-gray-900">Documentos da Empresa</h2>
          </div>
          <div className="divide-y divide-gray-100">
            {companyDocs.map((doc) => (
              <div key={doc.id} className="px-6 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-700">{doc.nome}</span>
                  <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">
                    {doc.tipo}
                  </span>
                  {doc.assinado && <span title="Assinado"><PenLine className="h-4 w-4 text-green-500" /></span>}
                </div>
                <button
                  onClick={() => handleDownloadDoc(doc)}
                  className="text-indigo-600 hover:text-indigo-800 p-1"
                  title="Baixar"
                >
                  <Download className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No documents */}
      {documents.length === 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Nenhum documento disponível neste kit.</p>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={handleDownloadZip}
          disabled={downloadingZip || documents.length === 0}
          className="flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {downloadingZip ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Download className="h-4 w-4" />
          )}
          Baixar Kit Completo (ZIP)
        </button>
        {canApprove && (
          <button
            onClick={handleApprove}
            disabled={approving}
            className="flex items-center gap-2 bg-emerald-600 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {approving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <ShieldCheck className="h-4 w-4" />
            )}
            Aprovar Kit
          </button>
        )}
      </div>
    </div>
  );
}
