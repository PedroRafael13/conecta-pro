'use client';

import React, { useState } from 'react';
import { Bot, Check, Copy, Eye, EyeOff, Key, RefreshCw, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

function portalFetch(path: string, options?: RequestInit) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : '';
  return fetch(`${API_BASE}/api/v1/portal${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
}

interface MCPToken {
  mcp_token: string;
  expires_at: string;
  api_url: string;
  instructions: string;
  claude_config: Record<string, unknown>;
}

export default function MCPConfigPage() {
  const [token, setToken] = useState<MCPToken | null>(null);
  const [loading, setLoading] = useState(false);
  const [showToken, setShowToken] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  async function generate() {
    setLoading(true);
    try {
      const res = await portalFetch('/mcp/token', { method: 'POST' });
      if (!res.ok) throw new Error('Falha ao gerar token');
      const data = await res.json();
      setToken(data);
      setShowToken(true);
      toast.success('Token MCP gerado com sucesso!');
    } catch {
      toast.error('Erro ao gerar token MCP');
    } finally {
      setLoading(false);
    }
  }

  async function revoke() {
    if (!confirm('Revogar o token MCP? Ferramentas conectadas perderão acesso.')) return;
    setLoading(true);
    try {
      await portalFetch('/mcp/token', { method: 'DELETE' });
      setToken(null);
      toast.success('Token revogado');
    } catch {
      toast.error('Erro ao revogar token');
    } finally {
      setLoading(false);
    }
  }

  function copy(text: string, key: string) {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(key);
      setTimeout(() => setCopied(null), 2000);
    });
  }

  const configJson = token ? JSON.stringify(token.claude_config, null, 2) : '';

  return (
    <div className="max-w-2xl space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="bg-indigo-600 p-2 rounded-lg">
          <Bot className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Conectar IA via MCP</h1>
          <p className="text-sm text-gray-500">Acesse seus dados no Claude Desktop ou Cursor</p>
        </div>
      </div>

      {/* Explanation */}
      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4">
        <h2 className="text-sm font-semibold text-indigo-800 mb-2">O que é o MCP?</h2>
        <p className="text-sm text-indigo-700">
          O Model Context Protocol (MCP) permite que ferramentas de IA como o Claude Desktop
          acessem diretamente seus kits documentais, chamados e métricas do portal — por linguagem
          natural, sem precisar abrir o sistema.
        </p>
        <p className="text-sm text-indigo-700 mt-2">
          Exemplo: <em>&ldquo;Liste meus kits de 2026&rdquo;</em> ou <em>&ldquo;Abra um chamado sobre o holerite de março&rdquo;</em>
        </p>
      </div>

      {/* Token Section */}
      {!token ? (
        <div className="bg-white rounded-xl border border-gray-200 p-6 text-center">
          <Key className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-600 mb-4">Gere um token de acesso para conectar ferramentas de IA ao seu portal.</p>
          <button
            onClick={generate}
            disabled={loading}
            className="flex items-center gap-2 mx-auto px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Key className="h-4 w-4" />}
            Gerar Token MCP
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
          {/* Token display */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
              Seu Token MCP
            </label>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 font-mono text-sm overflow-hidden">
                {showToken ? token.mcp_token : '•'.repeat(40)}
              </div>
              <button
                onClick={() => setShowToken(!showToken)}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                {showToken ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
              <button
                onClick={() => copy(token.mcp_token, 'token')}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                {copied === 'token' ? <Check className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              Válido até {new Date(token.expires_at).toLocaleDateString('pt-BR')} · Não compartilhe este token
            </p>
          </div>

          {/* Instructions */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Como configurar
            </label>
            <ol className="space-y-1">
              {token.instructions.split('\n').filter(Boolean).map((step, i) => (
                <li key={i} className="flex gap-2 text-sm text-gray-600">
                  <span className="flex-shrink-0 w-5 h-5 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center text-xs font-bold">
                    {i + 1}
                  </span>
                  {step.replace(/^\d+\.\s*/, '')}
                </li>
              ))}
            </ol>
          </div>

          {/* Config JSON */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Configuração Claude Desktop (JSON)
              </label>
              <button
                onClick={() => copy(configJson, 'json')}
                className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800"
              >
                {copied === 'json' ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                Copiar
              </button>
            </div>
            <pre className="bg-gray-900 text-green-400 text-xs rounded-lg p-4 overflow-x-auto">
              {configJson}
            </pre>
          </div>

          {/* Actions */}
          <div className="flex justify-between pt-2">
            <button
              onClick={generate}
              disabled={loading}
              className="flex items-center gap-1.5 text-sm text-indigo-600 hover:text-indigo-800 disabled:opacity-50"
            >
              <RefreshCw className="h-4 w-4" />
              Regenerar token
            </button>
            <button
              onClick={revoke}
              disabled={loading}
              className="flex items-center gap-1.5 text-sm text-red-500 hover:text-red-700 disabled:opacity-50"
            >
              <Trash2 className="h-4 w-4" />
              Revogar acesso
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
