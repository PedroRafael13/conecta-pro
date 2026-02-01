'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import {
  Receipt,
  Search,
  RefreshCw,
  Plus,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  AlertCircle,
  ArrowLeft,
  DollarSign,
  Clock,
  CheckCircle,
} from 'lucide-react';
import { BillingRuleFormModal } from '@/components/financeiro/billing-rule-form-modal';

type BillingRule = {
  id: string;
  name: string;
  type: 'fixed' | 'variable' | 'percentage';
  value: number;
  frequency: 'monthly' | 'quarterly' | 'annual';
  description: string;
  status: 'active' | 'inactive';
  created_at: string;
};

const formatCurrency = (value: number | undefined | null) => {
  if (value == null) return 'R$ 0,00';
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatDate = (date: string | undefined | null) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('pt-BR');
};

const getTypeColor = (type: string) => {
  switch (type) {
    case 'fixed':
      return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
    case 'variable':
      return 'bg-orange-500/10 text-orange-500 border-orange-500/20';
    case 'percentage':
      return 'bg-purple-500/10 text-purple-500 border-purple-500/20';
    default:
      return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
  }
};

const TYPE_LABELS: Record<string, string> = {
  fixed: 'Fixo',
  variable: 'Variavel',
  percentage: 'Percentual',
};

const FREQUENCY_LABELS: Record<string, string> = {
  monthly: 'Mensal',
  quarterly: 'Trimestral',
  annual: 'Anual',
};

export default function FaturamentoPage() {
  const [rules, setRules] = useState<BillingRule[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showFormModal, setShowFormModal] = useState(false);
  const [selectedRule, setSelectedRule] = useState<BillingRule | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleCreate = () => {
    setSelectedRule(null);
    setShowFormModal(true);
  };

  const handleEdit = (rule: BillingRule) => {
    setSelectedRule(rule);
    setShowFormModal(true);
  };

  const handleDelete = (rule: BillingRule) => {
    setRules((prev) => prev.filter((r) => r.id !== rule.id));
  };

  const handleToggleStatus = (rule: BillingRule) => {
    setRules((prev) =>
      prev.map((r) =>
        r.id === rule.id
          ? { ...r, status: r.status === 'active' ? 'inactive' : 'active' }
          : r
      )
    );
  };

  const handleFormSubmit = (data: any) => {
    if (selectedRule) {
      // Edit
      setRules((prev) =>
        prev.map((r) =>
          r.id === selectedRule.id ? { ...r, ...data } : r
        )
      );
    } else {
      // Create
      const newRule: BillingRule = {
        id: crypto.randomUUID(),
        ...data,
        status: 'active',
        created_at: new Date().toISOString(),
      };
      setRules((prev) => [...prev, newRule]);
    }
    setShowFormModal(false);
    setSelectedRule(null);
  };

  const handleRefresh = useCallback(() => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 500);
  }, []);

  const filteredRules = rules.filter((rule) => {
    const matchesSearch =
      !searchTerm ||
      rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rule.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || rule.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const activeRules = rules.filter((r) => r.status === 'active');
  const totalFixedValue = activeRules
    .filter((r) => r.type === 'fixed')
    .reduce((sum, r) => sum + (r.value || 0), 0);

  return (
    <div className="min-h-screen bg-grid">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[hsl(var(--background))]/80 backdrop-blur-xl border-b border-[hsl(var(--border))]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/modulos/financeiro">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Financeiro
                </Button>
              </Link>
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                  <Receipt className="w-5 h-5 text-amber-500" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                    Faturamento
                  </h1>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    Regras de faturamento e cobranca
                  </p>
                </div>
              </div>
            </div>
            <Button variant="primary" size="sm" onClick={handleCreate}>
              <Plus className="w-4 h-4 mr-2" />
              Nova Regra
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <Receipt className="w-5 h-5 text-amber-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {rules.length}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Total Regras</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-green-500">
                  {activeRules.length}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Ativas</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <p className="text-xl font-bold text-blue-500 truncate">
                  {formatCurrency(totalFixedValue)}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Valor Fixo Total</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gray-500/10 flex items-center justify-center">
                <Clock className="w-5 h-5 text-gray-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {rules.filter((r) => r.status === 'inactive').length}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Inativas</p>
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <Input
              type="search"
              placeholder="Buscar por nome ou descricao..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              icon={<Search className="w-4 h-4" />}
            />
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              <SelectItem value="active">Ativo</SelectItem>
              <SelectItem value="inactive">Inativo</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>

        {/* Table */}
        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Valor / Percentual</TableHead>
                <TableHead>Periodicidade</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Acoes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredRules.map((rule) => (
                <TableRow key={rule.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium text-[hsl(var(--foreground))]">{rule.name}</p>
                      {rule.description && (
                        <p className="text-xs text-[hsl(var(--muted-foreground))] truncate max-w-[200px]">
                          {rule.description}
                        </p>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={getTypeColor(rule.type)}>
                      {TYPE_LABELS[rule.type] || rule.type}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-medium">
                    {rule.type === 'percentage'
                      ? `${rule.value}%`
                      : formatCurrency(rule.value)
                    }
                  </TableCell>
                  <TableCell>
                    <span className="text-sm text-[hsl(var(--foreground))]">
                      {FREQUENCY_LABELS[rule.frequency] || rule.frequency}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge
                      className={
                        rule.status === 'active'
                          ? 'bg-green-500/10 text-green-500 border-green-500/20 cursor-pointer'
                          : 'bg-gray-500/10 text-gray-500 border-gray-500/20 cursor-pointer'
                      }
                      onClick={() => handleToggleStatus(rule)}
                    >
                      {rule.status === 'active' ? 'Ativo' : 'Inativo'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleEdit(rule)}>
                          <Edit className="w-4 h-4 mr-2" />
                          Editar
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleToggleStatus(rule)}>
                          <Eye className="w-4 h-4 mr-2" />
                          {rule.status === 'active' ? 'Desativar' : 'Ativar'}
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleDelete(rule)}
                          className="text-red-500 focus:text-red-500"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Excluir
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {filteredRules.length === 0 && (
            <div className="text-center py-12">
              <Receipt className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
              <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                Nenhuma regra de faturamento encontrada
              </h3>
              <p className="text-[hsl(var(--muted-foreground))] mt-1 mb-4">
                {searchTerm ? 'Tente ajustar os filtros de busca' : 'Crie a primeira regra de faturamento'}
              </p>
              {!searchTerm && (
                <Button variant="primary" onClick={handleCreate}>
                  <Plus className="w-4 h-4 mr-2" />
                  Nova Regra
                </Button>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Modals */}
      <BillingRuleFormModal
        isOpen={showFormModal}
        onClose={() => { setShowFormModal(false); setSelectedRule(null); }}
        onSubmit={handleFormSubmit}
        rule={selectedRule}
      />
    </div>
  );
}
