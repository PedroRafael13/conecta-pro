# Hooks Financeiros - Guia de Uso

## Importação

```typescript
// Importação consolidada (recomendado)
import {
  usePayables,
  useCreatePayable,
  useSuppliers,
  // ... outros hooks
} from '@/hooks/financial';

// Importação específica
import { useSuppliers } from '@/hooks/financial/useSuppliers';

// Importação direta do Orval (avançado)
import {
  useListAccountsApiV1FinancialPayablesPayablesGet
} from '@/types/generated/financial/financial-payables/financial-payables';
```

## Hooks Disponíveis

### 📦 Suppliers (Fornecedores)
- `useSuppliers(params?)` - Listar fornecedores
- `useSupplier(id, enabled?)` - Buscar fornecedor por ID
- `useSupplierStats(condominioId)` - Estatísticas de fornecedores
- `useSearchSuppliers(query, enabled?)` - Busca rápida
- `useCreateSupplier()` - Criar fornecedor
- `useUpdateSupplier()` - Atualizar fornecedor
- `useDeleteSupplier()` - Deletar fornecedor
- `useQualifySupplier()` - Qualificar fornecedor
- `useBlockSupplier()` - Bloquear fornecedor
- `useUnblockSupplier()` - Desbloquear fornecedor

### 💰 Payables (Contas a Pagar)
- `usePayables(params?)` - Listar contas a pagar
- `usePayable(id, enabled?)` - Buscar conta por ID
- `usePayableDashboard(condominioId)` - Dashboard/Estatísticas
- `useCreatePayable()` - Criar conta a pagar
- `useUpdatePayable()` - Atualizar conta
- `useProcessPayment()` - Processar pagamento

### 👥 Customers (Clientes)
- `useCustomers(params?)` - Listar clientes
- `useCustomer(id, enabled?)` - Buscar cliente por ID
- `useCustomerStats(customerId)` - Estatísticas de débito
- `useCreateCustomer()` - Criar cliente

### 💵 Receivables (Contas a Receber)
- `useReceivables(params?)` - Listar contas a receber
- `useReceivable(id, enabled?)` - Buscar conta por ID
- `useReceivableDashboard(condominioId)` - Dashboard
- `useCreateReceivable()` - Criar conta a receber
- `useGenerateBilling()` - Gerar faturamento

### 🏦 Bank Accounts (Contas Bancárias)
- `useBankAccounts(params?)` - Listar contas bancárias
- `useBankAccount(id, enabled?)` - Buscar conta por ID
- `useBankAccountBalance(id, enabled?)` - Saldo da conta
- `useCreateBankAccount()` - Criar conta bancária

### 💳 Bank Transactions (Transações Bancárias)
- `useBankTransactions(params?)` - Listar transações
- `useCreateBankTransaction()` - Criar transação
- `useImportOFX()` - Importar arquivo OFX

### 💸 Cashflow (Fluxo de Caixa)
- `useCashflowEntries(params?)` - Lançamentos
- `useCashflowForecast(params)` - Previsão
- `useCashflowProjection(params)` - Projeção
- `useCashflowDashboard(params)` - Dashboard
- `useCreateCashflowEntry()` - Criar lançamento

### 🛒 Purchase (Compras)
- `usePurchaseRequisitions(params?)` - Requisições de compra
- `usePurchaseOrders(params?)` - Ordens de compra
- `usePurchaseDashboard(params)` - Dashboard de compras
- `useCreatePurchaseRequisition()` - Criar requisição
- `useCreatePurchaseOrder()` - Criar ordem

### 📦 Inventory (Estoque)
- `useWarehouses(params?)` - Almoxarifados
- `useInventoryItems(params?)` - Itens de estoque
- `useInventoryItem(id, enabled?)` - Item por ID
- `useStockBalance(params)` - Saldo de estoque
- `useInventoryDashboard(params)` - Dashboard
- `useCreateStockMovement()` - Criar movimentação

### 📊 Accounting (Contabilidade)
- `useAccountingAccounts(params?)` - Plano de contas
- `useCostCenters(params?)` - Centros de custo
- `useJournalEntries(params?)` - Lançamentos contábeis
- `useTrialBalance(params)` - Balancete
- `useCreateJournalEntry()` - Criar lançamento

### 🧾 Fiscal (Gestão Fiscal)
- `useNFes(params?)` - Notas Fiscais Eletrônicas
- `useNFe(id, enabled?)` - NFe por ID
- `useNFSes(params?)` - Notas Fiscais de Serviço
- `useFiscalDashboard(params)` - Dashboard fiscal
- `useCreateNFe()` - Criar NFe
- `useAuthorizeNFe()` - Autorizar NFe

### 📈 BI Dashboard (Business Intelligence)
- `useBIDashboards(params?)` - Dashboards BI
- `useBIDashboard(id, enabled?)` - Dashboard por ID
- `useFinancialOverview(params)` - Visão geral financeira
- `useRevenueAnalysis(params)` - Análise de receitas
- `useExpenseAnalysis(params)` - Análise de despesas

### 📉 Costing (Custeio ABC)
- `useCostDrivers(params?)` - Direcionadores de custo
- `useCostActivities(params?)` - Atividades
- `useCostPools(params?)` - Pools de custo
- `useCostObjects(params?)` - Objetos de custo
- `useCostingDashboard(params)` - Dashboard de custeio
- `useCostAnalysis(params)` - Análise de custos
- `useCreateCostDriver()` - Criar direcionador

## Exemplos de Uso

### Query Básica
```typescript
function PayablesList() {
  const { data, isLoading, error } = usePayables({
    condominio_id: 'xxx',
    skip: 0,
    limit: 50
  });

  if (isLoading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error.message}</div>;

  return (
    <div>
      {data?.map(payable => (
        <div key={payable.id}>{payable.descricao}</div>
      ))}
    </div>
  );
}
```

### Mutation
```typescript
function CreatePayableForm() {
  const { mutate, isPending } = useCreatePayable();

  const handleSubmit = (values) => {
    mutate(
      { data: values },
      {
        onSuccess: (data) => {
          console.log('Conta criada:', data);
        },
        onError: (error) => {
          console.error('Erro:', error);
        }
      }
    );
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* ... campos do formulário */}
      <button type="submit" disabled={isPending}>
        {isPending ? 'Criando...' : 'Criar Conta'}
      </button>
    </form>
  );
}
```

### Query com Enabled
```typescript
function SupplierDetails({ supplierId }) {
  const { data } = useSupplier(
    supplierId,
    !!supplierId // só busca se supplierId existir
  );

  if (!supplierId) return null;
  if (!data) return <div>Carregando...</div>;

  return <div>{data.nome}</div>;
}
```

### Invalidação Manual de Cache
```typescript
import { useQueryClient } from '@tanstack/react-query';

function SomeComponent() {
  const queryClient = useQueryClient();

  const handleRefresh = () => {
    // Invalidar lista de contas a pagar
    queryClient.invalidateQueries({
      queryKey: ['listAccountsApiV1FinancialPayablesPayablesGet']
    });
  };

  return <button onClick={handleRefresh}>Atualizar</button>;
}
```

## Tipos

Todos os tipos estão disponíveis em:
```typescript
import type {
  PayableAccountCreate,
  PayableAccountResponse,
  SupplierCreate,
  // ... etc
} from '@/types/generated/financial/models';
```

## Query Keys

Para invalidação de cache e outras operações avançadas:
```typescript
import {
  payableKeys,
  supplierKeys,
  customerKeys,
  // ... etc
} from '@/hooks/financial';

// Usar em invalidações
queryClient.invalidateQueries({ queryKey: payableKeys });
```

## Documentação Adicional

- [Migração Completa](../../../MIGRATION_FINANCIAL.md)
- [React Query Docs](https://tanstack.com/query/latest/docs/react/overview)
- [Orval Docs](https://orval.dev/)
