'use client';

import { useState, useEffect } from 'react';
import {
  Search,
  Plus,
  Pencil,
  Trash2,
  X,
  Loader2,
  Building2,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

const API_BASE = '/api/v1/people-management/ged';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface Client {
  id: string;
  name: string;
  type: string;
  cnpj: string | null;
  contact_name: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  portal_access_enabled: boolean;
}

interface ClientForm {
  name: string;
  type: string;
  cnpj: string;
  contact_name: string;
  contact_email: string;
  contact_phone: string;
}

const emptyForm: ClientForm = {
  name: '',
  type: 'empresa',
  cnpj: '',
  contact_name: '',
  contact_email: '',
  contact_phone: '',
};

const typeLabels: Record<string, string> = {
  empresa: 'Empresa',
  condominio: 'Condominio',
  administradora: 'Administradora',
  orgao_publico: 'Orgao Publico',
  pessoa_fisica: 'Pessoa Fisica',
};

const typeBadgeColors: Record<string, string> = {
  empresa: 'bg-blue-100 text-blue-800',
  condominio: 'bg-green-100 text-green-800',
  administradora: 'bg-indigo-100 text-indigo-800',
  orgao_publico: 'bg-purple-100 text-purple-800',
  pessoa_fisica: 'bg-gray-100 text-gray-800',
};

export default function GedClientesPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<ClientForm>(emptyForm);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchClients();
  }, []);

  async function fetchClients() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/clients/`, { headers: getAuthHeaders() });
      if (res.ok) {
        const data = await res.json();
        setClients(Array.isArray(data) ? data : data.items || []);
      }
    } catch {
      // silenced
    } finally {
      setLoading(false);
    }
  }

  function openNew() {
    setEditingId(null);
    setForm(emptyForm);
    setShowModal(true);
  }

  function openEdit(client: Client) {
    setEditingId(client.id);
    setForm({
      name: client.name,
      type: client.type,
      cnpj: client.cnpj || '',
      contact_name: client.contact_name || '',
      contact_email: client.contact_email || '',
      contact_phone: client.contact_phone || '',
    });
    setShowModal(true);
  }

  async function handleSave() {
    setSaving(true);
    try {
      const url = editingId ? `${API_BASE}/clients/${editingId}` : `${API_BASE}/clients/`;
      const method = editingId ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: getAuthHeaders(),
        body: JSON.stringify(form),
      });
      if (res.ok) {
        setShowModal(false);
        fetchClients();
      }
    } catch {
      // silenced
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Tem certeza que deseja excluir este cliente?')) return;
    try {
      const res = await fetch(`${API_BASE}/clients/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        fetchClients();
      }
    } catch {
      // silenced
    }
  }

  async function togglePortal(client: Client) {
    try {
      await fetch(`${API_BASE}/clients/${client.id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ portal_access_enabled: !client.portal_access_enabled }),
      });
      fetchClients();
    } catch {
      // silenced
    }
  }

  const filtered = clients.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      (c.cnpj || '').includes(search)
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-500">Carregando clientes...</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clientes GED</h1>
          <p className="text-gray-500 mt-1">Gerencie os clientes para envio de kits documentais</p>
        </div>
        <button
          onClick={openNew}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Novo Cliente
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar por nome ou CNPJ..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
        />
      </div>

      <Card className="border border-gray-200">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Nome</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Tipo</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">CNPJ</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Contato</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Portal</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Acoes</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-gray-400">
                      <Building2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      Nenhum cliente encontrado
                    </td>
                  </tr>
                ) : (
                  filtered.map((client) => (
                    <tr key={client.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{client.name}</td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${typeBadgeColors[client.type] || 'bg-gray-100 text-gray-800'}`}>
                          {typeLabels[client.type] || client.type}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-600 font-mono text-xs">{client.cnpj || '-'}</td>
                      <td className="py-3 px-4 text-gray-600">
                        <div>
                          <p className="font-medium">{client.contact_name || '-'}</p>
                          {client.contact_email && (
                            <p className="text-xs text-gray-400">{client.contact_email}</p>
                          )}
                          {client.contact_phone && (
                            <p className="text-xs text-gray-400">{client.contact_phone}</p>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <button type="button" onClick={() => togglePortal(client)} title="Alternar acesso portal">
                          {client.portal_access_enabled ? (
                            <CheckCircle className="h-5 w-5 text-green-500" />
                          ) : (
                            <XCircle className="h-5 w-5 text-gray-300" />
                          )}
                        </button>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1">
                          <button type="button" onClick={() => openEdit(client)} className="p-1 rounded hover:bg-gray-100" title="Editar">
                            <Pencil className="h-4 w-4 text-gray-500" />
                          </button>
                          <button type="button" onClick={() => handleDelete(client.id)} className="p-1 rounded hover:bg-red-50" title="Excluir">
                            <Trash2 className="h-4 w-4 text-red-400" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold">
                {editingId ? 'Editar Cliente' : 'Novo Cliente'}
              </h2>
              <button type="button" onClick={() => setShowModal(false)} className="p-1 rounded hover:bg-gray-100">
                <X className="h-5 w-5 text-gray-400" />
              </button>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  placeholder="Nome do cliente"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo *</label>
                  <select
                    value={form.type}
                    onChange={(e) => setForm({ ...form, type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  >
                    <option value="empresa">Empresa</option>
                    <option value="condominio">Condominio</option>
                    <option value="administradora">Administradora</option>
                    <option value="orgao_publico">Orgao Publico</option>
                    <option value="pessoa_fisica">Pessoa Fisica</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">CNPJ</label>
                  <input
                    type="text"
                    value={form.cnpj}
                    onChange={(e) => setForm({ ...form, cnpj: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="00.000.000/0000-00"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Contato</label>
                <input
                  type="text"
                  value={form.contact_name}
                  onChange={(e) => setForm({ ...form, contact_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  placeholder="Nome do contato"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={form.contact_email}
                    onChange={(e) => setForm({ ...form, contact_email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="email@exemplo.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
                  <input
                    type="text"
                    value={form.contact_phone}
                    onChange={(e) => setForm({ ...form, contact_phone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="(92) 99999-0000"
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 p-4 border-t border-gray-200">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleSave}
                disabled={saving || !form.name}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? 'Salvando...' : 'Salvar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
