'use client';

import { useState, useMemo } from 'react';
import { Receipt, ArrowLeft, Inbox, Plus, X, Save, Search, Filter, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const statusConfig: Record<string, { label: string; className: string }> = {
  pending: { label: 'Pendente', className: 'bg-yellow-500 text-white' },
  approved: { label: 'Aprovado', className: 'bg-green-500 text-white' },
  rejected: { label: 'Rejeitado', className: 'bg-red-500 text-white' },
};

const categoryOptions = [
  { value: 'transporte', label: 'Transporte' },
  { value: 'alimentacao', label: 'Alimentação' },
  { value: 'hospedagem', label: 'Hospedagem' },
  { value: 'material', label: 'Material de Trabalho' },
  { value: 'outros', label: 'Outros' },
];

const fmt = (v: number) =>
  `R$ ${(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

interface Reembolso {
  id: string;
  employee_name: string;
  category: string;
  description: string;
  amount: number;
  date: string;
  status: 'pending' | 'approved' | 'rejected';
}

export default function ReembolsosPage() {
  const router = useRouter();
  const [reembolsos] = useState<Reembolso[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filtroStatus, setFiltroStatus] = useState('todos');
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    employee_name: '',
    category: 'transporte',
    description: '',
    amount: '',
    date: new Date().toISOString().split('T')[0] ?? '',
  });

  const filteredData = useMemo(() => {
    let items = [...reembolsos];
    if (filtroStatus !== 'todos') {
      items = items.filter(r => r.status === filtroStatus);
    }
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      items = items.filter(r =>
        r.employee_name.toLowerCase().includes(term) ||
        r.description.toLowerCase().includes(term) ||
        r.category.toLowerCase().includes(term)
      );
    }
    return items;
  }, [reembolsos, filtroStatus, searchTerm]);

  const handleCreate = async () => {
    if (!formData.employee_name || !formData.amount || !formData.date) {
      toast.error('Preencha todos os campos obrigatórios', { duration: 4000 });
      return;
    }
    setSaving(true);
    // API não implementada — exibe aviso informativo
    setTimeout(() => {
      setSaving(false);
      setShowForm(false);
      toast.info('Funcionalidade em implementação. O endpoint de reembolsos será integrado em breve.', { duration: 5000 });
    }, 800);
  };

  return (
    <div className="space-y-6 pb-28">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <Button type="button" variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Receipt className="h-6 w-6" />
              Reembolsos
            </h1>
            <p className="text-muted-foreground">Gerencie solicitações de reembolso dos colaboradores</p>
          </div>
        </div>
        <div className="flex gap-2 flex-shrink-0">
          <Button type="button" variant="outline" size="sm" onClick={() => setFiltroStatus('todos')}>
            <Filter className="h-4 w-4 mr-1" /> Todos
          </Button>
          <Button type="button" size="sm" onClick={() => setShowForm(true)}>
            <Plus className="h-4 w-4 mr-1" /> Novo Reembolso
          </Button>
        </div>
      </div>

      {/* Status filter badges */}
      <div className="flex gap-2 flex-wrap">
        {Object.entries(statusConfig).map(([key, val]) => (
          <Badge
            key={key}
            className={`cursor-pointer ${filtroStatus === key ? val.className : 'bg-muted text-muted-foreground'}`}
            onClick={() => setFiltroStatus(filtroStatus === key ? 'todos' : key)}
          >
            {val.label}
          </Badge>
        ))}
      </div>

      {/* Formulário de novo reembolso */}
      {showForm && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Novo Reembolso</CardTitle>
              <Button type="button" variant="ghost" size="sm" onClick={() => setShowForm(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Colaborador *</label>
                <input
                  type="text"
                  value={formData.employee_name}
                  onChange={e => setFormData(p => ({ ...p, employee_name: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-md text-sm"
                  placeholder="Nome do colaborador"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Categoria</label>
                <select
                  value={formData.category}
                  onChange={e => setFormData(p => ({ ...p, category: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-md text-sm"
                >
                  {categoryOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Valor (R$) *</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.amount}
                  onChange={e => setFormData(p => ({ ...p, amount: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-md text-sm"
                  placeholder="0,00"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Data *</label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={e => setFormData(p => ({ ...p, date: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-md text-sm"
                />
              </div>
              <div className="md:col-span-2">
                <label className="text-sm font-medium mb-1 block">Descrição</label>
                <textarea
                  value={formData.description}
                  onChange={e => setFormData(p => ({ ...p, description: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-md text-sm"
                  rows={2}
                  placeholder="Descreva a despesa..."
                />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button type="button" size="sm" disabled={saving} onClick={handleCreate}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Save className="h-4 w-4 mr-1" />}
                {saving ? 'Enviando...' : 'Solicitar Reembolso'}
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={() => setShowForm(false)}>
                Cancelar
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabela */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Solicitações de Reembolso</CardTitle>
            <div className="relative w-64">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                placeholder="Buscar por colaborador..."
                className="w-full pl-9 pr-3 py-2 border rounded-md text-sm"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredData.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p className="font-medium">Nenhum reembolso encontrado</p>
              <p className="text-sm mt-1">
                {searchTerm
                  ? 'Tente outra busca.'
                  : 'As solicitações de reembolso aparecerão aqui quando registradas.'}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Colaborador</TableHead>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Descrição</TableHead>
                  <TableHead>Valor</TableHead>
                  <TableHead>Data</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredData.map(r => (
                  <TableRow key={r.id}>
                    <TableCell className="font-medium">{r.employee_name}</TableCell>
                    <TableCell>{categoryOptions.find(c => c.value === r.category)?.label ?? r.category}</TableCell>
                    <TableCell className="max-w-xs truncate">{r.description}</TableCell>
                    <TableCell>{fmt(r.amount)}</TableCell>
                    <TableCell>{r.date}</TableCell>
                    <TableCell>
                      <Badge className={statusConfig[r.status]?.className ?? ''}>
                        {statusConfig[r.status]?.label ?? r.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
