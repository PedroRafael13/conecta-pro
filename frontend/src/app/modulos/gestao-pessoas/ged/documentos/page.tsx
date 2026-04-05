'use client';

import { useState, useEffect } from 'react';
import {
  Search,
  Loader2,
  FileText,
  CheckCircle,
  XCircle,
  Filter,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

const API_BASE = '/api/v1/ged';

function showToast(msg: string, type: 'success' | 'error' = 'success') {
  const el = document.createElement('div');
  el.className = `fixed top-4 right-4 z-[9999] px-4 py-3 rounded-lg shadow-lg text-sm font-medium text-white transition-opacity ${type === 'error' ? 'bg-red-500' : 'bg-emerald-500'}`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 3000);
}

function getAuthHeaders() {
  let token: string | null = null;
  try {
    token = localStorage.getItem('access_token') || localStorage.getItem('token');
  } catch {
    token = null;
  }
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface DocumentResult {
  id: string;
  name?: string;
  title?: string;
  document_type: string;
  kit_name?: string;
  kit_id?: string;
  employee_name?: string;
  signed?: boolean;
  status?: string;
  created_at: string;
  origin?: string;
  category?: string;
}

// typeOptions carregados dinamicamente de /ged/config/document-types

const originOptions = [
  { value: '', label: 'Todas as Origens' },
  { value: 'dp', label: 'Depto Pessoal' },
  { value: 'rh', label: 'Recursos Humanos' },
  { value: 'fiscal', label: 'Fiscal' },
  { value: 'contabil', label: 'Contabil' },
  { value: 'financeiro', label: 'Financeiro' },
  { value: 'operacional', label: 'Operacional' },
];

const signedOptions = [
  { value: '', label: 'Todos' },
  { value: 'true', label: 'Assinados' },
  { value: 'false', label: 'Nao Assinados' },
];

interface TypeOption {
  value: string;
  label: string;
}

interface ClientOption {
  id: string;
  name: string;
}

export default function DocumentosSearchPage() {
  const [query, setQuery] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterOrigin, setFilterOrigin] = useState('');
  const [filterSigned, setFilterSigned] = useState('');
  const [filterClient, setFilterClient] = useState('');
  const [results, setResults] = useState<DocumentResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [typeOptions, setTypeOptions] = useState<TypeOption[]>([{ value: '', label: 'Todos os Tipos' }]);
  const [clientOptions, setClientOptions] = useState<ClientOption[]>([]);

  useEffect(() => {
    fetch(`${API_BASE}/config/document-types`, { headers: getAuthHeaders() })
      .then((r) => r.json())
      .then((d) => {
        const lista: TypeOption[] = (d.tipos || d.data || (Array.isArray(d) ? d : [])).map(
          (t: { name?: string; category?: string }) => ({
            value: (t.name || '').toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, ''),
            label: t.name || '',
          }),
        );
        setTypeOptions([{ value: '', label: 'Todos os Tipos' }, ...lista]);
      })
      .catch(() => {});

    fetch(`${API_BASE}/clients/`, { headers: getAuthHeaders() })
      .then((r) => r.json())
      .then((d) => {
        const lista: ClientOption[] = (Array.isArray(d) ? d : d.items || d.clientes || []).map(
          (c: { id: string; name: string }) => ({ id: c.id, name: c.name }),
        );
        setClientOptions(lista);
      })
      .catch(() => {});
  }, []);

  async function handleSearch() {
    setLoading(true);
    setSearched(true);
    try {
      const params = new URLSearchParams();
      if (query) params.append('q', query);
      if (filterType) params.append('type', filterType);
      if (filterOrigin) params.append('origin', filterOrigin);
      if (filterSigned) params.append('signed', filterSigned);
      if (filterClient) params.append('client_id', filterClient);
      const res = await fetch(`${API_BASE}/documents/search?${params.toString()}`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        setResults(Array.isArray(data) ? data : data.items || []);
      }
    } catch (err) {
      console.error('Erro ao buscar documentos:', err);
      showToast('Erro ao buscar documentos. Tente novamente.', 'error');
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter') handleSearch();
  }

  function formatDate(dateStr: string) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR');
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Busca de Documentos</h1>
        <p className="text-gray-500 mt-1">Pesquise documentos em todos os kits</p>
      </div>

      <Card className="border border-gray-200">
        <CardContent className="p-4 space-y-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por nome do documento, funcionario..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Buscar'}
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={filterClient}
              onChange={(e) => setFilterClient(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value="">Todos os Clientes</option>
              {clientOptions.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              {typeOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
            <select
              value={filterOrigin}
              onChange={(e) => setFilterOrigin(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              {originOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
            <select
              value={filterSigned}
              onChange={(e) => setFilterSigned(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              {signedOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-500">Buscando documentos...</span>
        </div>
      ) : (
        <Card className="border border-gray-200">
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 bg-gray-50">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Nome</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Tipo</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Kit</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Funcionario</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Assinado</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Data</th>
                  </tr>
                </thead>
                <tbody>
                  {!searched ? (
                    <tr>
                      <td colSpan={6} className="py-12 text-center text-gray-400">
                        <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        Utilize os filtros acima para buscar documentos
                      </td>
                    </tr>
                  ) : results.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-12 text-center text-gray-400">
                        <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        Nenhum documento encontrado
                      </td>
                    </tr>
                  ) : (
                    results.map((doc) => (
                      <tr key={doc.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 font-medium">{doc.title || doc.name || '—'}</td>
                        <td className="py-3 px-4">
                          <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-700">
                            {doc.document_type || '—'}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-gray-600">{doc.kit_name || doc.category || '—'}</td>
                        <td className="py-3 px-4 text-gray-600">{doc.employee_name || '—'}</td>
                        <td className="py-3 px-4">
                          {doc.signed || doc.status === 'assinado' ? (
                            <CheckCircle className="h-5 w-5 text-green-500" />
                          ) : (
                            <XCircle className="h-5 w-5 text-red-400" />
                          )}
                        </td>
                        <td className="py-3 px-4 text-gray-600">{formatDate(doc.created_at)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
