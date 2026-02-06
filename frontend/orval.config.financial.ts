/**
 * Configuração Orval - Módulo FINANCIAL
 *
 * Estratégia HÍBRIDA:
 * - Gera APENAS tipos TypeScript a partir do OpenAPI
 * - Services e hooks serão implementados manualmente
 * - Mantém padrão do projeto mas garante tipos sincronizados
 *
 * Cobertura: 483 endpoints de Gestão Financeira Completa
 * - Contas a Pagar: Suppliers (11) + Payables (22)
 * - Contas a Receber: Customers (12) + Receivables (33) + Categories (9) + Billing Rules (12)
 * - Fluxo de Caixa: Bank Accounts (12) + Transactions (13) + Reconciliation (13) + Cashflow (29)
 * - Compras: Purchase (68 endpoints)
 * - Estoque: Inventory (33 endpoints)
 * - Contabilidade: Accounting (46 endpoints)
 * - Fiscal: NFe/NFSe/SPED (56 endpoints)
 * - BI Dashboard: KPIs e Analytics (60 endpoints)
 * - ABC Costing: Custeio por Atividade (50 endpoints)
 *
 * Uso:
 *   npm run orval:financial
 */

import { defineConfig } from 'orval';

export default defineConfig({
  financial: {
    input: {
      target: './openapi/openapi-financial.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/financial',
      schemas: './src/types/generated/financial/models',
      client: 'react-query',
      mock: false,
      clean: true,
      prettier: true,
      override: {
        mutator: {
          path: './src/lib/api-client.ts',
          name: 'customInstance',
        },
        query: {
          useQuery: true,
          useMutation: true,
          signal: true,
        },
      },
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write',
    },
  },
});
