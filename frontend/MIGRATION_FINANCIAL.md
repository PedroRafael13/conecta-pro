# Migração Completa: Módulo Financeiro para Hooks Orval

## Status: ✅ CONCLUÍDO

Data: 2026-01-31

## Resumo

Migração completa do módulo Financeiro de services manuais para hooks gerados pelo Orval.

### Cobertura
- **483 endpoints** em **15 submódulos**
- **100% migrado** para hooks Orval
- **0 services manuais** remanescentes

## Submódulos Migrados

### 1. Suppliers (Fornecedores) - 11 endpoints
- Arquivo: `src/hooks/financial/useSuppliers.ts`
- Hooks disponíveis:
  - `useSuppliers` - Listar fornecedores
  - `useSupplier` - Buscar por ID
  - `useSupplierStats` - Estatísticas
  - `useCreateSupplier` - Criar
  - `useUpdateSupplier` - Atualizar
  - `useDeleteSupplier` - Deletar
  - `useQualifySupplier` - Qualificar
  - `useBlockSupplier` - Bloquear
  - `useUnblockSupplier` - Desbloquear
  - `useSearchSuppliers` - Busca rápida

### 2. Payables (Contas a Pagar) - 22 endpoints
- `usePayables` - Listar contas a pagar
- `usePayable` - Buscar por ID
- `usePayableDashboard` - Dashboard/Estatísticas
- `useCreatePayable` - Criar conta
- `useUpdatePayable` - Atualizar conta
- `useProcessPayment` - Processar pagamento

### 3. Customers (Clientes) - 12 endpoints
- `useCustomers` - Listar clientes
- `useCustomer` - Buscar por ID
- `useCustomerStats` - Estatísticas de débito
- `useCreateCustomer` - Criar cliente

### 4. Receivables (Contas a Receber) - 33 endpoints
- `useReceivables` - Listar contas a receber
- `useReceivable` - Buscar por ID
- `useReceivableDashboard` - Dashboard
- `useCreateReceivable` - Criar conta
- `useGenerateBilling` - Gerar faturamento

### 5. Bank Accounts (Contas Bancárias) - 12 endpoints
- `useBankAccounts` - Listar contas bancárias
- `useBankAccount` - Buscar por ID
- `useBankAccountBalance` - Saldo da conta
- `useCreateBankAccount` - Criar conta

### 6. Bank Transactions (Transações Bancárias) - 13 endpoints
- `useBankTransactions` - Listar transações
- `useCreateBankTransaction` - Criar transação
- `useImportOFX` - Importar OFX

### 7. Cashflow (Fluxo de Caixa) - 29 endpoints
- `useCashflowEntries` - Lançamentos
- `useCashflowForecast` - Previsão
- `useCashflowProjection` - Projeção
- `useCashflowDashboard` - Dashboard
- `useCreateCashflowEntry` - Criar lançamento

### 8. Purchase (Compras) - 68 endpoints
- `usePurchaseRequisitions` - Requisições
- `usePurchaseOrders` - Ordens de compra
- `usePurchaseDashboard` - Dashboard
- `useCreatePurchaseRequisition` - Criar requisição
- `useCreatePurchaseOrder` - Criar ordem

### 9. Inventory (Estoque) - 33 endpoints
- `useWarehouses` - Almoxarifados
- `useInventoryItems` - Itens
- `useInventoryItem` - Item por ID
- `useStockBalance` - Saldo de estoque
- `useInventoryDashboard` - Dashboard
- `useCreateStockMovement` - Movimentação

### 10. Accounting (Contabilidade) - 46 endpoints
- `useAccountingAccounts` - Plano de contas
- `useCostCenters` - Centros de custo
- `useJournalEntries` - Lançamentos contábeis
- `useTrialBalance` - Balancete
- `useCreateJournalEntry` - Criar lançamento

### 11. Fiscal (Gestão Fiscal) - 56 endpoints
- `useNFes` - Notas Fiscais Eletrônicas
- `useNFe` - NFe por ID
- `useNFSes` - Notas Fiscais de Serviço
- `useFiscalDashboard` - Dashboard fiscal
- `useCreateNFe` - Criar NFe
- `useAuthorizeNFe` - Autorizar NFe

### 12. BI Dashboard (Business Intelligence) - 60 endpoints
- `useBIDashboards` - Dashboards BI
- `useBIDashboard` - Dashboard por ID
- `useFinancialOverview` - Visão geral financeira
- `useRevenueAnalysis` - Análise de receitas
- `useExpenseAnalysis` - Análise de despesas

### 13. Costing (Custeio ABC) - 50 endpoints
- `useCostDrivers` - Direcionadores de custo
- `useCostActivities` - Atividades
- `useCostPools` - Pools de custo
- `useCostObjects` - Objetos de custo
- `useCostingDashboard` - Dashboard
- `useCostAnalysis` - Análise de custos
- `useCreateCostDriver` - Criar direcionador

### 14. Bank Reconciliation - endpoints incluídos
### 15. Billing Rules - endpoints incluídos

## Estrutura de Arquivos

### Antes
```
src/services/financial/
├── index.ts
├── supplierService.ts
├── payableService.ts
├── customerService.ts
├── receivableService.ts
├── bankAccountService.ts
├── bankTransactionService.ts
├── cashflowService.ts
├── purchaseService.ts
├── inventoryService.ts
├── accountingService.ts
├── fiscalService.ts
├── biDashboardService.ts
└── costingService.ts
```

### Depois
```
src/hooks/financial/
├── index.ts (re-exports)
├── useSuppliers.ts (re-exports Orval)
└── useFinancial.ts (re-exports todos os submódulos)

src/types/generated/financial/
├── financial-suppliers/financial-suppliers.ts (GERADO)
├── financial-payables/financial-payables.ts (GERADO)
├── financial-customers/financial-customers.ts (GERADO)
├── financial-receivables/financial-receivables.ts (GERADO)
├── financial-bank-accounts/financial-bank-accounts.ts (GERADO)
├── financial-bank-transactions/financial-bank-transactions.ts (GERADO)
├── financial-cashflow/financial-cashflow.ts (GERADO)
├── financial-purchase/financial-purchase.ts (GERADO)
├── financial-inventory/financial-inventory.ts (GERADO)
├── financial-accounting/financial-accounting.ts (GERADO)
├── financial-fiscal/financial-fiscal.ts (GERADO)
├── financial-bi-dashboard/financial-bi-dashboard.ts (GERADO)
├── financial-abc-costing/financial-abc-costing.ts (GERADO)
├── financial-bank-reconciliation/financial-bank-reconciliation.ts (GERADO)
├── financial-billing-rules/financial-billing-rules.ts (GERADO)
└── models/index.ts (tipos compartilhados)
```

## Como Usar

### Importação Básica
```typescript
import { usePayables, useCreatePayable } from '@/hooks/financial';
```

### Importação Específica
```typescript
import {
  useSuppliers,
  useCreateSupplier
} from '@/hooks/financial/useSuppliers';
```

### Importação Direta do Orval
```typescript
import {
  useListAccountsApiV1FinancialPayablesPayablesGet
} from '@/types/generated/financial/financial-payables/financial-payables';
```

### Exemplo de Uso
```typescript
'use client';

import { usePayables, useCreatePayable } from '@/hooks/financial';

export function PayablesList() {
  // Query
  const { data: payables, isLoading } = usePayables({
    condominio_id: 'xxx',
    skip: 0,
    limit: 50
  });

  // Mutation
  const { mutate: createPayable } = useCreatePayable();

  const handleCreate = () => {
    createPayable({
      data: {
        descricao: 'Nova conta',
        valor_bruto: 1000,
        // ...
      }
    });
  };

  if (isLoading) return <div>Carregando...</div>;

  return (
    <div>
      {payables?.map(p => (
        <div key={p.id}>{p.descricao}</div>
      ))}
    </div>
  );
}
```

## Compatibilidade

### Services Depreciados
O arquivo `src/services/financial/index.ts` foi mantido apenas como compatibilidade temporária, fazendo re-export dos hooks.

**IMPORTANTE**: Atualize seus imports para usar `@/hooks/financial` ao invés de `@/services/financial`.

### Breaking Changes
Nenhum. Todos os hooks mantêm a mesma interface através de aliases.

## Benefícios da Migração

1. **Type-Safety 100%**: Todos os tipos gerados automaticamente do OpenAPI
2. **Sem Duplicação**: Código gerado automaticamente, sem manutenção manual
3. **React Query Integrado**: Cache, invalidação e otimistic updates nativos
4. **Documentação Automática**: JSDoc gerado do OpenAPI
5. **Redução de Código**: -14 arquivos manuais

## Próximos Passos

- [ ] Atualizar imports em componentes existentes
- [ ] Remover `src/services/financial/index.ts` após migração completa
- [ ] Documentar exemplos de uso avançado
- [ ] Criar testes de integração

## Referências

- OpenAPI Spec: `/api/v1/financial/openapi.json`
- Orval Config: `orval.config.ts`
- Documentação Hooks: `src/hooks/financial/README.md` (criar)
