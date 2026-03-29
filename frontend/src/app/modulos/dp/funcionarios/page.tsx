'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Users, ArrowLeft, Search, Loader2, AlertTriangle, CheckCircle2, Edit, Save, X,
  ChevronLeft, ChevronRight, User, FileText, MapPin, Building2, CreditCard, Shield,
} from 'lucide-react';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const API_BASE = '/api/v1/people-management/hr';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? (localStorage.getItem('access_token') || localStorage.getItem('token')) : null;
  return { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) };
}

// Campos obrigatórios para eSocial S-2200
const ESOCIAL_FIELDS = [
  'nome', 'cpf', 'data_nascimento', 'sexo', 'estado_civil', 'nome_mae',
  'rg', 'pis', 'ctps_numero', 'nacionalidade', 'naturalidade',
  'cep', 'logradouro', 'cidade', 'uf',
] as const;

function calcCompleteness(emp: Record<string, unknown>): { percent: number; missing: string[] } {
  const missing: string[] = [];
  for (const f of ESOCIAL_FIELDS) {
    if (!emp[f] || String(emp[f]).trim() === '') missing.push(f);
  }
  const percent = Math.round(((ESOCIAL_FIELDS.length - missing.length) / ESOCIAL_FIELDS.length) * 100);
  return { percent, missing };
}

const FIELD_LABELS: Record<string, string> = {
  nome: 'Nome', cpf: 'CPF', data_nascimento: 'Data de Nascimento', sexo: 'Sexo',
  estado_civil: 'Estado Civil', nome_mae: 'Nome da Mãe', nome_pai: 'Nome do Pai',
  rg: 'RG', rg_orgao: 'Órgão Emissor RG', rg_uf: 'UF RG', pis: 'PIS/PASEP',
  ctps_numero: 'CTPS Número', ctps_serie: 'CTPS Série', ctps_uf: 'CTPS UF', ctps_data_emissao: 'CTPS Data Emissão',
  nacionalidade: 'Nacionalidade', naturalidade: 'Naturalidade',
  email: 'Email', telefone: 'Telefone', celular: 'Celular',
  contato_emergencia: 'Contato Emergência', telefone_emergencia: 'Tel. Emergência',
  cep: 'CEP', logradouro: 'Logradouro', numero: 'Número', complemento: 'Complemento',
  bairro: 'Bairro', cidade: 'Cidade', uf: 'UF',
  cargo: 'Cargo', departamento: 'Departamento', salario_base: 'Salário Base',
  tipo_contrato: 'Tipo Contrato', regime_trabalho: 'Regime', data_admissao: 'Data Admissão',
  banco: 'Banco', agencia: 'Agência', conta: 'Conta', tipo_conta: 'Tipo Conta', pix: 'Chave PIX',
  titulo_eleitor: 'Título Eleitor', certificado_reservista: 'Cert. Reservista',
  cnh_numero: 'CNH', cnh_categoria: 'Categoria CNH', cnh_validade: 'Validade CNH',
  curso_vigilante: 'Curso Vigilante', curso_vigilante_validade: 'Validade Curso',
  cnv: 'CNV', cnv_validade: 'Validade CNV',
  observacoes: 'Observações',
};

const PAGE_SIZE = 15;

type Tab = 'pessoal' | 'documentos' | 'endereco' | 'profissional' | 'bancario' | 'vigilancia';

export default function FuncionariosPage() {
  const router = useRouter();
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [filterComplete, setFilterComplete] = useState<'all' | 'incomplete' | 'complete'>('all');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editData, setEditData] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>('pessoal');

  const loadEmployees = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/employees?page_size=100`, { headers: getAuthHeaders() });
      if (res.ok) {
        const data = await res.json();
        setEmployees(data.items || data || []);
      }
    } catch { /* */ } finally { setLoading(false); }
  }, []);

  useEffect(() => { loadEmployees(); }, [loadEmployees]);

  const enriched = useMemo(() =>
    employees.map(e => ({ ...e, ...calcCompleteness(e) })),
  [employees]);

  const filtered = useMemo(() => {
    let items = enriched;
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      items = items.filter(e => (e.nome || '').toLowerCase().includes(term) || (e.cpf || '').includes(term));
    }
    if (filterComplete === 'incomplete') items = items.filter(e => e.percent < 100);
    if (filterComplete === 'complete') items = items.filter(e => e.percent === 100);
    return items.sort((a, b) => a.percent - b.percent); // Mais incompletos primeiro
  }, [enriched, searchTerm, filterComplete]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paginated = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  const statsComplete = enriched.filter(e => e.percent === 100).length;
  const statsIncomplete = enriched.filter(e => e.percent < 100).length;
  const avgPercent = enriched.length ? Math.round(enriched.reduce((s, e) => s + e.percent, 0) / enriched.length) : 0;

  const startEditing = (emp: any) => {
    setEditingId(emp.id);
    const data: Record<string, string> = {};
    for (const key of Object.keys(FIELD_LABELS)) {
      data[key] = emp[key] != null ? String(emp[key]) : '';
    }
    setEditData(data);
    setActiveTab('pessoal');
  };

  const handleSave = async () => {
    if (!editingId) return;
    setSaving(true);
    try {
      const original = employees.find(e => e.id === editingId) || {};
      const payload: Record<string, unknown> = {};
      for (const [key, val] of Object.entries(editData)) {
        const origVal = original[key] != null ? String(original[key]) : '';
        if (val !== origVal && val !== '') {
          payload[key] = val;
        }
      }
      if (Object.keys(payload).length === 0) {
        toast.info('Nenhuma alteração detectada', { duration: 3000 });
        setSaving(false);
        return;
      }
      const res = await fetch(`${API_BASE}/employees/${editingId}`, {
        method: 'PATCH', headers: getAuthHeaders(), body: JSON.stringify(payload),
      });
      if (res.ok) {
        toast.success('Dados atualizados com sucesso!', { duration: 4000 });
        setEditingId(null);
        await loadEmployees();
      } else {
        const err = await res.json().catch(() => null);
        toast.error(err?.detail || 'Erro ao salvar', { duration: 5000 });
      }
    } catch { toast.error('Erro de conexão', { duration: 5000 }); }
    finally { setSaving(false); }
  };

  const renderField = (key: string, type: string = 'text', options?: string[]) => (
    <div key={key}>
      <label className="text-sm font-medium mb-1 block">
        {FIELD_LABELS[key] || key}
        {ESOCIAL_FIELDS.includes(key as any) && <span className="text-red-500 ml-1">*</span>}
      </label>
      {options ? (
        <select value={editData[key] || ''} onChange={e => setEditData(p => ({ ...p, [key]: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm">
          <option value="">Selecione</option>
          {options.map(o => <option key={o} value={o}>{o}</option>)}
        </select>
      ) : (
        <input type={type} value={editData[key] || ''} onChange={e => setEditData(p => ({ ...p, [key]: e.target.value }))}
          className={`w-full px-3 py-2 border rounded-md text-sm ${ESOCIAL_FIELDS.includes(key as any) && !editData[key] ? 'border-yellow-400 bg-yellow-50' : ''}`} />
      )}
    </div>
  );

  const tabs: { key: Tab; label: string; icon: typeof User }[] = [
    { key: 'pessoal', label: 'Pessoal', icon: User },
    { key: 'documentos', label: 'Documentos', icon: FileText },
    { key: 'endereco', label: 'Endereço', icon: MapPin },
    { key: 'profissional', label: 'Profissional', icon: Building2 },
    { key: 'bancario', label: 'Bancário', icon: CreditCard },
    { key: 'vigilancia', label: 'Vigilância', icon: Shield },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Users className="h-6 w-6" />
              Cadastro de Funcionários
            </h1>
            <p className="text-muted-foreground">Complete os dados para eSocial e obrigações trabalhistas</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">Total</p>
          <p className="text-2xl font-bold">{enriched.length}</p>
        </CardContent></Card>
        <Card className="cursor-pointer hover:shadow-md" onClick={() => setFilterComplete('complete')}>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Cadastro Completo</p>
            <p className="text-2xl font-bold text-green-600">{statsComplete}</p>
          </CardContent>
        </Card>
        <Card className="cursor-pointer hover:shadow-md" onClick={() => setFilterComplete('incomplete')}>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Dados Incompletos</p>
            <p className="text-2xl font-bold text-yellow-600">{statsIncomplete}</p>
          </CardContent>
        </Card>
        <Card><CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">Completude Média</p>
          <p className={`text-2xl font-bold ${avgPercent >= 80 ? 'text-green-600' : avgPercent >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>{avgPercent}%</p>
        </CardContent></Card>
      </div>

      {/* Edit Form */}
      {editingId && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Editar Funcionário — {editData.nome || 'Sem nome'}</CardTitle>
              <Button variant="ghost" size="sm" onClick={() => setEditingId(null)}><X className="h-4 w-4" /></Button>
            </div>
            <div className="flex gap-1 mt-2">
              {tabs.map(t => (
                <Button key={t.key} variant={activeTab === t.key ? 'default' : 'outline'} size="sm"
                  onClick={() => setActiveTab(t.key)} className="text-xs">
                  <t.icon className="h-3.5 w-3.5 mr-1" /> {t.label}
                </Button>
              ))}
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {activeTab === 'pessoal' && (<>
                {renderField('nome')}
                {renderField('cpf')}
                {renderField('data_nascimento', 'date')}
                {renderField('sexo', 'text', ['M', 'F'])}
                {renderField('estado_civil', 'text', ['solteiro', 'casado', 'divorciado', 'viuvo', 'uniao_estavel'])}
                {renderField('nacionalidade', 'text', ['Brasileira', 'Estrangeira'])}
                {renderField('naturalidade')}
                {renderField('nome_mae')}
                {renderField('nome_pai')}
                {renderField('email')}
                {renderField('telefone')}
                {renderField('celular')}
                {renderField('contato_emergencia')}
                {renderField('telefone_emergencia')}
              </>)}
              {activeTab === 'documentos' && (<>
                {renderField('rg')}
                {renderField('rg_orgao')}
                {renderField('rg_uf', 'text', ['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO'])}
                {renderField('pis')}
                {renderField('ctps_numero')}
                {renderField('ctps_serie')}
                {renderField('ctps_uf', 'text', ['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO'])}
                {renderField('ctps_data_emissao', 'date')}
                {renderField('titulo_eleitor')}
                {renderField('certificado_reservista')}
                {renderField('cnh_numero')}
                {renderField('cnh_categoria', 'text', ['A', 'B', 'AB', 'C', 'D', 'E'])}
                {renderField('cnh_validade', 'date')}
              </>)}
              {activeTab === 'endereco' && (<>
                {renderField('cep')}
                {renderField('logradouro')}
                {renderField('numero')}
                {renderField('complemento')}
                {renderField('bairro')}
                {renderField('cidade')}
                {renderField('uf', 'text', ['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO'])}
              </>)}
              {activeTab === 'profissional' && (<>
                {renderField('cargo')}
                {renderField('departamento', 'text', ['Operações', 'Administrativo', 'Comercial', 'Financeiro'])}
                {renderField('salario_base', 'number')}
                {renderField('tipo_contrato', 'text', ['CLT', 'Temporário', 'Experiência'])}
                {renderField('regime_trabalho', 'text', ['CLT', 'Estatutário', 'Temporário'])}
                {renderField('data_admissao', 'date')}
                {renderField('observacoes')}
              </>)}
              {activeTab === 'bancario' && (<>
                {renderField('banco')}
                {renderField('agencia')}
                {renderField('conta')}
                {renderField('tipo_conta', 'text', ['Corrente', 'Poupança', 'Salário'])}
                {renderField('pix')}
              </>)}
              {activeTab === 'vigilancia' && (<>
                {renderField('curso_vigilante')}
                {renderField('curso_vigilante_validade', 'date')}
                {renderField('cnv')}
                {renderField('cnv_validade', 'date')}
              </>)}
            </div>
            <div className="flex gap-2 mt-4">
              <Button size="sm" disabled={saving} onClick={handleSave}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Save className="h-4 w-4 mr-1" />}
                {saving ? 'Salvando...' : 'Salvar Alterações'}
              </Button>
              <Button variant="outline" size="sm" onClick={() => setEditingId(null)}>Cancelar</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Funcionários</CardTitle>
            <div className="flex gap-2 items-center">
              <div className="flex gap-1">
                <Badge className={`cursor-pointer ${filterComplete === 'all' ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-muted text-muted-foreground'}`} onClick={() => { setFilterComplete('all'); setCurrentPage(1); }}>Todos</Badge>
                <Badge className={`cursor-pointer ${filterComplete === 'incomplete' ? 'bg-yellow-500 text-white hover:bg-yellow-600' : 'bg-muted text-muted-foreground'}`} onClick={() => { setFilterComplete('incomplete'); setCurrentPage(1); }}>Incompletos</Badge>
                <Badge className={`cursor-pointer ${filterComplete === 'complete' ? 'bg-green-500 text-white hover:bg-green-600' : 'bg-muted text-muted-foreground'}`} onClick={() => { setFilterComplete('complete'); setCurrentPage(1); }}>Completos</Badge>
              </div>
              <div className="relative w-56">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <input type="text" value={searchTerm} onChange={e => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                  placeholder="Buscar nome ou CPF..." className="w-full pl-9 pr-3 py-2 border rounded-md text-sm" />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Users className="h-12 w-12 mb-3" />
              <p className="font-medium">Nenhum funcionário encontrado</p>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome</TableHead>
                    <TableHead>CPF</TableHead>
                    <TableHead>Cargo</TableHead>
                    <TableHead>Completude eSocial</TableHead>
                    <TableHead>Campos Faltantes</TableHead>
                    <TableHead>Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paginated.map((emp) => (
                    <TableRow key={emp.id} className={emp.percent < 100 ? 'bg-yellow-50/50' : ''}>
                      <TableCell className="font-medium">{emp.nome || '-'}</TableCell>
                      <TableCell className="text-sm">{emp.cpf || '-'}</TableCell>
                      <TableCell className="text-sm">{emp.cargo || '-'}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {emp.percent === 100 ? (
                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                          ) : (
                            <AlertTriangle className="h-4 w-4 text-yellow-500" />
                          )}
                          <div className="w-20 bg-muted rounded-full h-2">
                            <div className={`h-2 rounded-full ${emp.percent === 100 ? 'bg-green-500' : emp.percent >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                              style={{ width: `${emp.percent}%` }} />
                          </div>
                          <span className="text-xs text-muted-foreground">{emp.percent}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {emp.missing.length > 0 ? (
                          <span className="text-xs text-yellow-700">
                            {emp.missing.slice(0, 3).map((f: string) => FIELD_LABELS[f] || f).join(', ')}
                            {emp.missing.length > 3 && ` +${emp.missing.length - 3}`}
                          </span>
                        ) : (
                          <span className="text-xs text-green-600">Completo</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm" onClick={() => startEditing(emp)}>
                          <Edit className="h-3.5 w-3.5 mr-1" /> Editar
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="flex items-center justify-between mt-4 text-sm">
                <span className="text-muted-foreground">{filtered.length} funcionário{filtered.length !== 1 ? 's' : ''} — Página {currentPage}/{totalPages}</span>
                <div className="flex gap-1">
                  <Button variant="outline" size="sm" disabled={currentPage <= 1} onClick={() => setCurrentPage(p => p - 1)}><ChevronLeft className="h-4 w-4" /></Button>
                  <Button variant="outline" size="sm" disabled={currentPage >= totalPages} onClick={() => setCurrentPage(p => p + 1)}><ChevronRight className="h-4 w-4" /></Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
