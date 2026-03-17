'use client';

import React, { useEffect, useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Send, Loader2 } from 'lucide-react';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || '') + '/api/v1/portal';

function getPortalHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface KitOption {
  id: number;
  mes_referencia: string;
}

const priorityOptions = [
  { value: 'BAIXA', label: 'Baixa' },
  { value: 'NORMAL', label: 'Normal' },
  { value: 'ALTA', label: 'Alta' },
  { value: 'URGENTE', label: 'Urgente' },
];

export default function NovoChamadoPage() {
  const router = useRouter();
  const [assunto, setAssunto] = useState('');
  const [kitId, setKitId] = useState('');
  const [prioridade, setPrioridade] = useState('NORMAL');
  const [descricao, setDescricao] = useState('');
  const [kits, setKits] = useState<KitOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchKits() {
      try {
        const res = await fetch(`${API_BASE}/kits`, { headers: getPortalHeaders() });
        if (res.ok) {
          const data = await res.json();
          const items: KitOption[] = Array.isArray(data) ? data : data.items || [];
          setKits(items);
        }
      } catch {
        // silently handle
      }
    }
    fetchKits();
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');

    if (!assunto.trim()) {
      setError('Informe o assunto do chamado.');
      return;
    }
    if (!descricao.trim()) {
      setError('Descreva o motivo do chamado.');
      return;
    }

    setLoading(true);
    try {
      const body: Record<string, unknown> = {
        assunto: assunto.trim(),
        prioridade,
        descricao: descricao.trim(),
      };
      if (kitId) body.kit_id = Number(kitId);

      const res = await fetch(`${API_BASE}/tickets`, {
        method: 'POST',
        headers: getPortalHeaders(),
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.detail || 'Erro ao criar chamado.');
      }

      router.push('/area-cliente/chamados');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Erro ao enviar chamado. Tente novamente.';
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Back */}
      <Link
        href="/area-cliente/chamados"
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-indigo-600 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Voltar para Chamados
      </Link>

      <div>
        <h1 className="text-2xl font-bold text-gray-900">Novo Chamado</h1>
        <p className="text-gray-500 text-sm mt-1">
          Preencha os dados abaixo para abrir uma solicitação.
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-5">
        {/* Subject */}
        <div>
          <label htmlFor="assunto" className="block text-sm font-medium text-gray-700 mb-1">
            Assunto *
          </label>
          <input
            id="assunto"
            type="text"
            value={assunto}
            onChange={(e) => setAssunto(e.target.value)}
            placeholder="Resumo da sua solicitação"
            required
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-gray-900 placeholder-gray-400"
          />
        </div>

        {/* Kit selector */}
        <div>
          <label htmlFor="kit" className="block text-sm font-medium text-gray-700 mb-1">
            Kit Relacionado <span className="text-gray-400">(opcional)</span>
          </label>
          <select
            id="kit"
            value={kitId}
            onChange={(e) => setKitId(e.target.value)}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-gray-900 bg-white"
          >
            <option value="">Nenhum kit selecionado</option>
            {kits.map((kit) => (
              <option key={kit.id} value={kit.id}>
                Kit {kit.mes_referencia}
              </option>
            ))}
          </select>
        </div>

        {/* Priority */}
        <div>
          <label htmlFor="prioridade" className="block text-sm font-medium text-gray-700 mb-1">
            Prioridade
          </label>
          <select
            id="prioridade"
            value={prioridade}
            onChange={(e) => setPrioridade(e.target.value)}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-gray-900 bg-white"
          >
            {priorityOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Description */}
        <div>
          <label htmlFor="descricao" className="block text-sm font-medium text-gray-700 mb-1">
            Descrição *
          </label>
          <textarea
            id="descricao"
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
            placeholder="Descreva com detalhes o motivo do seu chamado..."
            rows={5}
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none text-gray-900 placeholder-gray-400"
          />
        </div>

        {/* Submit */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Enviando...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                Enviar Chamado
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
