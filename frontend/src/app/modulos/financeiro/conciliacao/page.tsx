'use client';

import { CheckCircle2, Search, RefreshCw, Plus, Landmark, Upload, Eye, MoreHorizontal, AlertCircle, ArrowLeft, Edit, Trash2 } from 'lucide-react';
import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
;
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  useBankAccounts,
  useCreateBankAccount,
  useBankTransactions,
  useImportOFX,
} from '@/hooks/financial/useFinancial';
import { BankAccountFormModal } from '@/components/financeiro/bank-account-form-modal';
import { BankTransactionDetailModal } from '@/components/financeiro/bank-transaction-detail-modal';
import { cn, formatCurrency, formatDate } from '@/lib/utils';

type TabType = 'accounts' | 'transactions' | 'reconciliation';

export default function ConciliacaoPage() {
  const [activeTab, setActiveTab] = useState<TabType>('accounts');
  const [search, setSearch] = useState('');
  const [showAccountModal, setShowAccountModal] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<any>(null);
  const [showTransactionDetail, setShowTransactionDetail] = useState(false);

  // Hooks de dados
  const {
    data: accountsData,
    isLoading: loadingAccounts,
    isError: accountsError,
    error: accountsErr,
    refetch: refetchAccounts,
  } = useBankAccounts();

  const {
    data: transactionsData,
    isLoading: loadingTransactions,
    isError: transactionsError,
    error: transactionsErr,
    refetch: refetchTransactions,
  } = useBankTransactions();

  const createBankAccount = useCreateBankAccount();
  const importOFX = useImportOFX();

  const accounts = accountsData?.data || accountsData?.items || [];
  const transactions = transactionsData?.data || transactionsData?.items || [];

  const isLoading = activeTab === 'accounts' ? loadingAccounts : loadingTransactions;
  const isError = activeTab === 'accounts' ? accountsError : transactionsError;
  const error = activeTab === 'accounts' ? accountsErr : transactionsErr;

  const handleCreateAccount = async (data: any) => {
    try {
      await createBankAccount.mutateAsync({ data });
      setShowAccountModal(false);
      // refetch() removido - mutation já invalida queries automaticamente
    } catch (err) {
      console.error('Erro ao criar conta bancaria:', err);
      throw err;
    }
  };

  const handleImportOFX = async () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.ofx,.OFX';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;

      try {
        const formData = new FormData();
        formData.append('file', file);
        await importOFX.mutateAsync({ data: formData as any });
        // refetch() removido - mutation já invalida queries automaticamente
      } catch (err) {
        console.error('Erro ao importar OFX:', err);
      }
    };
    input.click();
  };

  const handleViewTransaction = (transaction: any) => {
    setSelectedTransaction(transaction);
    setShowTransactionDetail(true);
  };

  const getTransactionTypeColor = (type: string) => {
    switch (type) {
      case 'credit':
        return 'bg-green-500/10 text-green-500 border-green-500/30';
      case 'debit':
        return 'bg-red-500/10 text-red-500 border-red-500/30';
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/30';
    }
  };

  const getMatchStatusColor = (status: string) => {
    switch (status) {
      case 'matched':
        return 'bg-green-500/10 text-green-500 border-green-500/30';
      case 'unmatched':
      case 'pending':
        return 'bg-orange-500/10 text-orange-500 border-orange-500/30';
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/30';
    }
  };

  const getMatchStatusLabel = (status: string) => {
    switch (status) {
      case 'matched':
        return 'Conciliado';
      case 'unmatched':
        return 'Pendente';
      case 'pending':
        return 'Pendente';
      default:
        return status;
    }
  };

  // Filter by search
  const filteredAccounts = search
    ? accounts.filter((acc: any) =>
        acc.name?.toLowerCase().includes(search.toLowerCase()) ||
        acc.bank_name?.toLowerCase().includes(search.toLowerCase())
      )
    : accounts;

  const filteredTransactions = search
    ? transactions.filter((tx: any) =>
        tx.description?.toLowerCase().includes(search.toLowerCase())
      )
    : transactions;

  const refetch = () => {
    refetchAccounts();
    refetchTransactions();
  };

  const tabs: { key: TabType; label: string }[] = [
    { key: 'accounts', label: 'Contas Bancarias' },
    { key: 'transactions', label: 'Transacoes' },
    { key: 'reconciliation', label: 'Conciliacao' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link href="/modulos/financeiro">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Financeiro
            </Button>
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                Conciliacao Bancaria
              </h1>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                Gerencie contas, transacoes e conciliacao
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={refetch}
            disabled={isLoading}
          >
            <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
          </Button>
          {activeTab === 'accounts' && (
            <Button variant="primary" size="sm" onClick={() => setShowAccountModal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Nova Conta
            </Button>
          )}
          {activeTab === 'transactions' && (
            <Button
              variant="primary"
              size="sm"
              onClick={handleImportOFX}
              disabled={importOFX.isPending}
            >
              <Upload className="w-4 h-4 mr-2" />
              Importar OFX
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {tabs.map((tab) => (
          <Button
            key={tab.key}
            variant="ghost"
            size="sm"
            className={cn(
              'rounded-lg px-4 py-2',
              activeTab === tab.key
                ? 'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]'
                : 'bg-[hsl(var(--secondary))] text-[hsl(var(--secondary-foreground))]'
            )}
            onClick={() => { setActiveTab(tab.key); setSearch(''); }}
          >
            {tab.label}
          </Button>
        ))}
      </div>

      {/* Search */}
      <div className="flex-1">
        <Input
          type="search"
          placeholder={
            activeTab === 'accounts'
              ? 'Buscar contas...'
              : activeTab === 'transactions'
              ? 'Buscar transacoes...'
              : 'Buscar conciliacoes...'
          }
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          icon={<Search className="w-4 h-4" />}
        />
      </div>

      {/* Error */}
      {isError && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-[hsl(var(--destructive))]/10 border border-[hsl(var(--destructive))]/30">
          <AlertCircle className="w-5 h-5 text-[hsl(var(--destructive))]" />
          <div>
            <p className="font-medium text-[hsl(var(--destructive))]">Erro ao carregar dados</p>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              {(error as Error)?.message || 'Tente novamente em alguns instantes'}
            </p>
          </div>
          <Button variant="secondary" size="sm" onClick={refetch} className="ml-auto">
            Tentar novamente
          </Button>
        </div>
      )}

      {/* Tab 1: Contas Bancarias */}
      {activeTab === 'accounts' && (
        <Card>
          <CardContent className="p-0">
            {loadingAccounts ? (
              <div className="divide-y divide-[hsl(var(--border))]">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="p-4 flex items-center gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="h-4 w-48 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                      <div className="h-3 w-32 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[hsl(var(--border))]">
                      <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                        Nome
                      </th>
                      <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))] hidden md:table-cell">
                        Banco
                      </th>
                      <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))] hidden lg:table-cell">
                        Agencia
                      </th>
                      <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))] hidden lg:table-cell">
                        Conta
                      </th>
                      <th className="text-right p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                        Saldo
                      </th>
                      <th className="w-12 p-4"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[hsl(var(--border))]">
                    {filteredAccounts.map((account: any) => (
                      <tr
                        key={account.id}
                        className="hover:bg-[hsl(var(--secondary))]/50 transition-colors"
                      >
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
                              <Landmark className="w-5 h-5 text-emerald-500" />
                            </div>
                            <div>
                              <p className="font-medium text-[hsl(var(--foreground))]">
                                {account.name}
                              </p>
                              <p className="text-xs text-[hsl(var(--muted-foreground))] md:hidden">
                                {account.bank_name}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="p-4 hidden md:table-cell">
                          <span className="text-sm text-[hsl(var(--foreground))]">
                            {account.bank_name || '-'}
                          </span>
                        </td>
                        <td className="p-4 hidden lg:table-cell">
                          <span className="text-sm text-[hsl(var(--muted-foreground))]">
                            {account.agency || '-'}
                          </span>
                        </td>
                        <td className="p-4 hidden lg:table-cell">
                          <span className="text-sm text-[hsl(var(--muted-foreground))]">
                            {account.account_number || '-'}
                          </span>
                        </td>
                        <td className="p-4 text-right">
                          <span className="font-mono text-sm font-medium text-[hsl(var(--foreground))]">
                            {formatCurrency(account.balance || 0)}
                          </span>
                        </td>
                        <td className="p-4">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <MoreHorizontal className="w-4 h-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem>
                                <Eye className="w-4 h-4 mr-2" />
                                Visualizar
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Edit className="w-4 h-4 mr-2" />
                                Editar
                              </DropdownMenuItem>
                              <DropdownMenuItem className="text-red-500">
                                <Trash2 className="w-4 h-4 mr-2" />
                                Excluir
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Empty state */}
            {!loadingAccounts && filteredAccounts.length === 0 && (
              <div className="text-center py-12">
                <Landmark className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
                <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                  Nenhuma conta bancaria encontrada
                </h3>
                <p className="text-[hsl(var(--muted-foreground))] mt-1">
                  {search
                    ? 'Tente ajustar a busca'
                    : 'Cadastre sua primeira conta bancaria'}
                </p>
                {!search && (
                  <Button className="mt-4" onClick={() => setShowAccountModal(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Nova Conta
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Tab 2: Transacoes */}
      {activeTab === 'transactions' && (
        <Card>
          <CardContent className="p-0">
            {loadingTransactions ? (
              <div className="divide-y divide-[hsl(var(--border))]">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="p-4 flex items-center gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="h-4 w-48 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                      <div className="h-3 w-32 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[hsl(var(--border))]">
                      <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                        Data
                      </th>
                      <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                        Descricao
                      </th>
                      <th className="text-right p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                        Valor
                      </th>
                      <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                        Tipo
                      </th>
                      <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))] hidden md:table-cell">
                        Status
                      </th>
                      <th className="w-12 p-4"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[hsl(var(--border))]">
                    {filteredTransactions.map((tx: any) => (
                      <tr
                        key={tx.id}
                        className="hover:bg-[hsl(var(--secondary))]/50 transition-colors cursor-pointer"
                        onClick={() => handleViewTransaction(tx)}
                      >
                        <td className="p-4">
                          <span className="text-sm text-[hsl(var(--foreground))]">
                            {tx.date ? formatDate(tx.date) : '-'}
                          </span>
                        </td>
                        <td className="p-4">
                          <p className="font-medium text-[hsl(var(--foreground))]">
                            {tx.description || '-'}
                          </p>
                        </td>
                        <td className="p-4 text-right">
                          <span
                            className={cn(
                              'font-mono text-sm font-medium',
                              tx.transaction_type === 'credit' ? 'text-green-500' : 'text-red-500'
                            )}
                          >
                            {tx.transaction_type === 'credit' ? '+' : '-'}
                            {formatCurrency(Math.abs(tx.amount || 0))}
                          </span>
                        </td>
                        <td className="p-4">
                          <span
                            className={cn(
                              'inline-flex px-2 py-1 text-xs font-medium rounded-full border',
                              getTransactionTypeColor(tx.transaction_type)
                            )}
                          >
                            {tx.transaction_type === 'credit' ? 'Credito' : 'Debito'}
                          </span>
                        </td>
                        <td className="p-4 hidden md:table-cell">
                          <span
                            className={cn(
                              'inline-flex px-2 py-1 text-xs font-medium rounded-full border',
                              getMatchStatusColor(tx.match_status || 'unmatched')
                            )}
                          >
                            {getMatchStatusLabel(tx.match_status || 'unmatched')}
                          </span>
                        </td>
                        <td className="p-4" onClick={(e) => e.stopPropagation()}>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <MoreHorizontal className="w-4 h-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem onClick={() => handleViewTransaction(tx)}>
                                <Eye className="w-4 h-4 mr-2" />
                                Detalhes
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Empty state */}
            {!loadingTransactions && filteredTransactions.length === 0 && (
              <div className="text-center py-12">
                <CheckCircle2 className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
                <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                  Nenhuma transacao encontrada
                </h3>
                <p className="text-[hsl(var(--muted-foreground))] mt-1">
                  {search
                    ? 'Tente ajustar a busca'
                    : 'Importe um arquivo OFX para comecar'}
                </p>
                {!search && (
                  <Button className="mt-4" onClick={handleImportOFX}>
                    <Upload className="w-4 h-4 mr-2" />
                    Importar OFX
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Tab 3: Conciliacao */}
      {activeTab === 'reconciliation' && (
        <Card>
          <CardContent className="p-0">
            {loadingTransactions ? (
              <div className="divide-y divide-[hsl(var(--border))]">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="p-4 flex items-center gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="h-4 w-48 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                      <div className="h-3 w-32 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[hsl(var(--border))]">
                      <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                        Transacao Bancaria
                      </th>
                      <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))] hidden md:table-cell">
                        Lancamento Vinculado
                      </th>
                      <th className="text-right p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                        Valor
                      </th>
                      <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                        Status
                      </th>
                      <th className="w-12 p-4"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[hsl(var(--border))]">
                    {filteredTransactions.map((tx: any) => (
                      <tr
                        key={tx.id}
                        className="hover:bg-[hsl(var(--secondary))]/50 transition-colors"
                      >
                        <td className="p-4">
                          <div>
                            <p className="font-medium text-[hsl(var(--foreground))]">
                              {tx.description || '-'}
                            </p>
                            <p className="text-xs text-[hsl(var(--muted-foreground))]">
                              {tx.date ? formatDate(tx.date) : '-'}
                            </p>
                          </div>
                        </td>
                        <td className="p-4 hidden md:table-cell">
                          <span className="text-sm text-[hsl(var(--muted-foreground))]">
                            {tx.matched_entry_description || 'Nenhum lancamento vinculado'}
                          </span>
                        </td>
                        <td className="p-4 text-right">
                          <span className="font-mono text-sm font-medium text-[hsl(var(--foreground))]">
                            {formatCurrency(Math.abs(tx.amount || 0))}
                          </span>
                        </td>
                        <td className="p-4">
                          <span
                            className={cn(
                              'inline-flex px-2 py-1 text-xs font-medium rounded-full border',
                              getMatchStatusColor(tx.match_status || 'pending')
                            )}
                          >
                            {getMatchStatusLabel(tx.match_status || 'pending')}
                          </span>
                        </td>
                        <td className="p-4">
                          {(tx.match_status !== 'matched') && (
                            <Button variant="outline" size="sm">
                              Conciliar
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Empty state */}
            {!loadingTransactions && filteredTransactions.length === 0 && (
              <div className="text-center py-12">
                <CheckCircle2 className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
                <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                  Nenhuma transacao para conciliar
                </h3>
                <p className="text-[hsl(var(--muted-foreground))] mt-1">
                  Importe transacoes bancarias para iniciar a conciliacao
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Modals */}
      <BankAccountFormModal
        isOpen={showAccountModal}
        onClose={() => setShowAccountModal(false)}
        onSubmit={handleCreateAccount}
        isLoading={createBankAccount.isPending}
      />

      <BankTransactionDetailModal
        isOpen={showTransactionDetail}
        onClose={() => {
          setShowTransactionDetail(false);
          setSelectedTransaction(null);
        }}
        transaction={selectedTransaction}
      />
    </div>
  );
}
