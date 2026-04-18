'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  RefreshCw,
  FileText,
  CheckCircle,
  AlertCircle,
  Clock,
  Download,
} from 'lucide-react';
import type {
  OnvioStats,
  OnvioStatus,
  SyncLog,
  SyncResult,
  DocumentosResponse,
} from './types';
import { ValoresFiscaisCard } from './components/ValoresFiscaisCard';
import { useValoresFiscaisResumo } from '@/hooks/useValoresFiscaisResumo';

const API = '/api/v1/onvio';

function getAuthHeader(): Record<string, string> {
  if (typeof window === 'undefined') return {};
  const token =
    localStorage.getItem('auth_token') ||
    localStorage.getItem('access_token') ||
    localStorage.getItem('token') ||
    '';
  return token ? { Authorization: `Bearer ${token}` } : {};
}

const CATEGORY_LABELS: Record<string, string> = {
  folha_pagamento: '💰 Folha de Pagamento',
  contracheque: '🧾 Contracheques',
  fgts_guia: '🏦 GFD FGTS',
  fgts_consignado: '🏦 FGTS Consignado',
  fgts_relatorio: '📊 Relatório FGTS',
  inss_guia: '💊 INSS',
  dctfweb_declaracao: '📋 DCTFWeb Declaração',
  dctfweb_recibo: '✅ DCTFWeb Recibo',
  dctfweb_extrato: '📄 DCTFWeb Extrato',
  dctfweb_debitos: '📉 DCTFWeb Débitos',
  dctfweb_creditos: '📈 DCTFWeb Créditos',
  admissao: '👤 Admissão',
  rescisao: '🚪 Rescisão',
  ferias: '🏖️ Férias',
  decimo_terceiro: '🎄 13º Salário',
  empresa_docs: '🏢 Empresa',
  outros: '📎 Outros',
};

const STATUS_CLASS: Record<string, string> = {
  success: 'bg-green-100 text-green-800',
  partial: 'bg-yellow-100 text-yellow-800',
  error: 'bg-red-100 text-red-800',
  running: 'bg-blue-100 text-blue-800',
  pending: 'bg-gray-100 text-gray-600',
};

const HIGHLIGHT_CATS = [
  'folha_pagamento',
  'fgts_guia',
  'dctfweb_declaracao',
  'admissao',
] as const;

function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_CLASS[status] ?? STATUS_CLASS.pending}`}
    >
      {status}
    </span>
  );
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: { ...getAuthHeader(), ...(init?.headers ?? {}) },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

export default function OnvioSyncPage() {
  const qc = useQueryClient();
  const [catFiltro, setCatFiltro] = useState<string>('');

  const { data: stats } = useQuery<OnvioStats>({
    queryKey: ['onvio-stats'],
    queryFn: () => apiFetch<OnvioStats>(`${API}/stats`),
    staleTime: 30_000,
  });

  const { data: sessao } = useQuery<OnvioStatus>({
    queryKey: ['onvio-status'],
    queryFn: () => apiFetch<OnvioStatus>(`${API}/status`),
    staleTime: 60_000,
    refetchInterval: 60_000,
  });

  const { data: historico } = useQuery<SyncLog[]>({
    queryKey: ['onvio-historico'],
    queryFn: () => apiFetch<SyncLog[]>(`${API}/historico?limit=10`),
    staleTime: 30_000,
  });

  const { data: docs } = useQuery<DocumentosResponse>({
    queryKey: ['onvio-docs', catFiltro],
    queryFn: () =>
      apiFetch<DocumentosResponse>(
        `${API}/documentos?limit=100${catFiltro ? `&categoria=${catFiltro}` : ''}`,
      ),
    staleTime: 60_000,
  });

  const {
    data: valoresFiscais,
    isLoading: valoresLoading,
    isError: valoresError,
    refetch: valoresRefetch,
  } = useValoresFiscaisResumo();

  const syncMutation = useMutation<SyncResult>({
    mutationFn: () =>
      apiFetch<SyncResult>(`${API}/sync`, { method: 'POST' }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['onvio-stats'] });
      qc.invalidateQueries({ queryKey: ['onvio-historico'] });
      qc.invalidateQueries({ queryKey: ['onvio-docs'] });
      qc.invalidateQueries({ queryKey: ['onvio-status'] });
    },
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            GEDEON — Onvio Sync
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Documentos da Portte Contábil sincronizados automaticamente
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div
            className={`flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-full ${
              sessao?.sessao_valida
                ? 'bg-green-50 text-green-700'
                : 'bg-red-50 text-red-700'
            }`}
          >
            {sessao?.sessao_valida ? (
              <CheckCircle size={14} />
            ) : (
              <AlertCircle size={14} />
            )}
            {sessao?.sessao_valida ? 'Conectado' : 'Sessão expirada'}
          </div>
          <button
            onClick={() => syncMutation.mutate()}
            disabled={syncMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium transition-colors"
          >
            <RefreshCw
              size={16}
              className={syncMutation.isPending ? 'animate-spin' : ''}
            />
            {syncMutation.isPending ? 'Sincronizando...' : 'Sincronizar Agora'}
          </button>
        </div>
      </div>

      {/* Card de valores fiscais */}
      <ValoresFiscaisCard
        data={valoresFiscais}
        isLoading={valoresLoading}
        isError={valoresError}
        onRetry={() => valoresRefetch()}
      />

      {/* Cards de stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-100 dark:border-gray-700">
          <p className="text-xs text-gray-500 uppercase tracking-wide">
            Total Documentos
          </p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
            {stats?.total ?? '—'}
          </p>
        </div>
        {HIGHLIGHT_CATS.map((cat) => (
          <div
            key={cat}
            className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-100 dark:border-gray-700"
          >
            <p className="text-xs text-gray-500 uppercase tracking-wide truncate">
              {CATEGORY_LABELS[cat]?.replace(/^[^\s]+ /, '')}
            </p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
              {stats?.por_categoria?.[cat] ?? 0}
            </p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Histórico de syncs */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <div className="p-4 border-b border-gray-100 dark:border-gray-700">
            <h2 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <Clock size={16} />
              Histórico de Syncs
            </h2>
          </div>
          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {(historico ?? []).map((log) => (
              <div
                key={log.id}
                className="p-3 flex items-center justify-between"
              >
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {log.mes_ref}
                  </p>
                  <p className="text-xs text-gray-400">
                    {new Date(log.created_at).toLocaleString('pt-BR')}
                    {log.duracao_s != null &&
                      ` · ${log.duracao_s.toFixed(1)}s`}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-green-600">+{log.novos}</span>
                  {log.erros > 0 && (
                    <span className="text-xs text-red-500">
                      {log.erros} erros
                    </span>
                  )}
                  <StatusBadge status={log.status} />
                </div>
              </div>
            ))}
            {!historico?.length && (
              <p className="p-4 text-sm text-gray-400 text-center">
                Nenhum sync realizado ainda
              </p>
            )}
          </div>
        </div>

        {/* Documentos por categoria */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
            <h2 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <FileText size={16} />
              Por Categoria
            </h2>
            <select
              value={catFiltro}
              onChange={(e) => setCatFiltro(e.target.value)}
              className="text-xs border rounded px-2 py-1 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="">Todas</option>
              {Object.entries(CATEGORY_LABELS).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
          </div>
          <div className="max-h-80 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-700">
            {(docs?.documentos ?? []).map((d) => (
              <div
                key={d.id}
                className="p-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-gray-900 dark:text-white truncate">
                    {d.nome}
                  </p>
                  <p className="text-xs text-gray-400">
                    {d.mes_ref ?? '—'} ·{' '}
                    {CATEGORY_LABELS[d.categoria] ?? d.categoria}
                  </p>
                </div>
                <Download
                  size={14}
                  className="text-gray-300 flex-shrink-0 ml-2"
                />
              </div>
            ))}
            {!docs?.documentos?.length && (
              <p className="p-4 text-sm text-gray-400 text-center">
                Sem documentos importados ainda
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Banner pós-sync */}
      {syncMutation.data && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4">
          <p className="text-sm font-medium text-green-800">
            ✅ Sync concluído —{' '}
            {syncMutation.data.resultado?.novos ?? 0} novos documentos
            importados
          </p>
        </div>
      )}
      {syncMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <p className="text-sm font-medium text-red-800">
            ❌ Falha no sync — verifique a conexão com o Onvio
          </p>
        </div>
      )}
    </div>
  );
}
