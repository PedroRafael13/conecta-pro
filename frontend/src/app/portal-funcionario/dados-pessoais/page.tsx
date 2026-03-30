'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { User, ArrowLeft, ShieldCheck, LogOut, Loader2, AlertCircle, CheckCircle2, Pencil, X, Save, Phone, Mail, MapPin, Heart } from 'lucide-react';

const API_BASE = '/api/v1/people-management/portal';

function getPortalHeaders(): Record<string, string> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface MyData {
  nome: string | null;
  cpf: string | null;
  cargo: string | null;
  data_admissao: string | null;
  telefone: string | null;
  email: string | null;
  endereco: string | null;
  contato_emergencia: string | null;
}

const fmtDate = (d: string | null) => d ? new Date(d).toLocaleDateString('pt-BR') : '—';
const maskCPF = (cpf: string | null) => {
  if (!cpf) return '—';
  const d = cpf.replace(/\D/g, '');
  if (d.length !== 11) return cpf;
  return `***.${d.slice(3, 6)}.${d.slice(6, 9)}-**`;
};

export default function DadosPessoaisPage() {
  const router = useRouter();
  const [employeeName, setEmployeeName] = useState('');
  const [data, setData] = useState<MyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Editable fields
  const [telefone, setTelefone] = useState('');
  const [email, setEmail] = useState('');
  const [endereco, setEndereco] = useState('');
  const [contatoEmergencia, setContatoEmergencia] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('portal_token');
    if (!token) { router.push('/portal-funcionario/login'); return; }
    setEmployeeName(localStorage.getItem('portal_employee_name') || 'Funcionário');
    loadData();
  }, [router]);

  async function loadData() {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/my-data`, { headers: getPortalHeaders() });
      if (res.ok) {
        const d: MyData = await res.json();
        setData(d);
        setTelefone(d.telefone || '');
        setEmail(d.email || '');
        setEndereco(d.endereco || '');
        setContatoEmergencia(d.contato_emergencia || '');
      }
    } catch {
      setError('Erro ao carregar dados.');
    } finally {
      setLoading(false);
    }
  }

  async function saveData() {
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${API_BASE}/my-data`, {
        method: 'PUT',
        headers: getPortalHeaders(),
        body: JSON.stringify({
          telefone: telefone || null,
          email: email || null,
          endereco: endereco || null,
          contato_emergencia: contatoEmergencia || null,
        }),
      });
      if (res.ok) {
        const updated = await res.json();
        setData(updated);
        setEditing(false);
        setSuccess('Dados atualizados com sucesso!');
        setTimeout(() => setSuccess(''), 4000);
      } else {
        const d = await res.json().catch(() => ({}));
        setError(d.detail || 'Erro ao salvar dados.');
      }
    } catch {
      setError('Erro ao salvar dados.');
    } finally {
      setSaving(false);
    }
  }

  const cancelEdit = () => {
    setEditing(false);
    setTelefone(data?.telefone || '');
    setEmail(data?.email || '');
    setEndereco(data?.endereco || '');
    setContatoEmergencia(data?.contato_emergencia || '');
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
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Link href="/portal-funcionario/dashboard" className="text-gray-500 hover:text-gray-700">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <User className="w-5 h-5 text-teal-600" /> Meus Dados
            </h2>
          </div>
          {!editing && data && (
            <button
              onClick={() => setEditing(true)}
              className="flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-800 font-medium transition"
            >
              <Pencil className="w-4 h-4" /> Editar
            </button>
          )}
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
        ) : !data ? (
          <div className="bg-white rounded-xl shadow-sm p-8 text-center text-gray-400">
            <User className="w-10 h-10 mx-auto mb-2 opacity-30" />
            <p className="text-sm">Dados não disponíveis.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Dados fixos */}
            <div className="bg-white rounded-xl shadow-sm p-5">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Informações Profissionais</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Nome</p>
                    <p className="text-sm font-medium text-gray-900">{data.nome || '—'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gray-50 rounded-lg flex items-center justify-center flex-shrink-0">
                    <ShieldCheck className="w-4 h-4 text-gray-500" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">CPF</p>
                    <p className="text-sm font-medium text-gray-900">{maskCPF(data.cpf)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-purple-50 rounded-lg flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Cargo</p>
                    <p className="text-sm font-medium text-gray-900">{data.cargo || '—'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-green-50 rounded-lg flex items-center justify-center flex-shrink-0">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Data de Admissão</p>
                    <p className="text-sm font-medium text-gray-900">{fmtDate(data.data_admissao)}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Dados editáveis */}
            <div className="bg-white rounded-xl shadow-sm p-5">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Contato e Endereço</h3>
              {editing ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1.5 flex items-center gap-1.5">
                      <Phone className="w-3.5 h-3.5" /> Telefone
                    </label>
                    <input
                      type="tel"
                      value={telefone}
                      onChange={e => setTelefone(e.target.value)}
                      placeholder="(92) 99999-9999"
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-[#0A2540] focus:border-transparent outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1.5 flex items-center gap-1.5">
                      <Mail className="w-3.5 h-3.5" /> E-mail pessoal
                    </label>
                    <input
                      type="email"
                      value={email}
                      onChange={e => setEmail(e.target.value)}
                      placeholder="seu@email.com"
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-[#0A2540] focus:border-transparent outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1.5 flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5" /> Endereço
                    </label>
                    <textarea
                      value={endereco}
                      onChange={e => setEndereco(e.target.value)}
                      placeholder="Rua, número, bairro, cidade, CEP"
                      rows={2}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-[#0A2540] focus:border-transparent outline-none resize-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1.5 flex items-center gap-1.5">
                      <Heart className="w-3.5 h-3.5" /> Contato de emergência
                    </label>
                    <input
                      type="text"
                      value={contatoEmergencia}
                      onChange={e => setContatoEmergencia(e.target.value)}
                      placeholder="Nome e telefone"
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-[#0A2540] focus:border-transparent outline-none"
                    />
                  </div>
                  <div className="flex gap-3 pt-2">
                    <button
                      onClick={saveData}
                      disabled={saving}
                      className="flex-1 flex items-center justify-center gap-2 bg-[#0A2540] hover:bg-[#1E3A5F] text-white py-3 rounded-xl font-semibold text-sm transition disabled:opacity-50"
                    >
                      {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                      Salvar
                    </button>
                    <button
                      onClick={cancelEdit}
                      disabled={saving}
                      className="flex-1 flex items-center justify-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 py-3 rounded-xl font-semibold text-sm transition"
                    >
                      <X className="w-4 h-4" /> Cancelar
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {[
                    { icon: Phone, label: 'Telefone', value: data.telefone, color: 'bg-blue-50 text-blue-600' },
                    { icon: Mail, label: 'E-mail', value: data.email, color: 'bg-green-50 text-green-600' },
                    { icon: MapPin, label: 'Endereço', value: data.endereco, color: 'bg-orange-50 text-orange-600' },
                    { icon: Heart, label: 'Contato de emergência', value: data.contato_emergencia, color: 'bg-red-50 text-red-500' },
                  ].map(({ icon: Icon, label, value, color }) => (
                    <div key={label} className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${color}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">{label}</p>
                        <p className={`text-sm font-medium ${value ? 'text-gray-900' : 'text-gray-400 italic'}`}>
                          {value || 'Não informado'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
