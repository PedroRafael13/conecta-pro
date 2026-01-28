/**
 * Financial Services Index
 *
 * Exportação centralizada de todos os services do módulo FINANCIAL.
 * Cobertura: 483 endpoints em 15 submódulos.
 *
 * Submódulos:
 * - Suppliers (11 endpoints)
 * - Payables (22 endpoints)
 * - Customers (12 endpoints)
 * - Receivables (33 endpoints)
 * - Bank Accounts (12 endpoints)
 * - Bank Transactions (13 endpoints)
 * - Cashflow (29 endpoints)
 * - Purchase (68 endpoints)
 * - Inventory (33 endpoints)
 * - Accounting (46 endpoints)
 * - Fiscal (56 endpoints)
 * - BI Dashboard (60 endpoints)
 * - ABC Costing (50 endpoints)
 */

// Contas a Pagar
export { default as supplierService } from './supplierService';
export { default as payableService } from './payableService';

// Contas a Receber
export { default as customerService } from './customerService';
export { default as receivableService } from './receivableService';

// Fluxo de Caixa
export { default as bankAccountService } from './bankAccountService';
export { default as bankTransactionService } from './bankTransactionService';
export { default as cashflowService } from './cashflowService';

// Compras e Estoque
export { default as purchaseService } from './purchaseService';
export { default as inventoryService } from './inventoryService';

// Contabilidade
export { default as accountingService } from './accountingService';

// Fiscal
export { default as fiscalService } from './fiscalService';

// BI e Analytics
export { default as biDashboardService } from './biDashboardService';

// Custeio ABC
export { default as costingService } from './costingService';

// Export consolidado
export default {
  // Contas a Pagar
  supplier: supplierService,
  payable: payableService,

  // Contas a Receber
  customer: customerService,
  receivable: receivableService,

  // Fluxo de Caixa
  bankAccount: bankAccountService,
  bankTransaction: bankTransactionService,
  cashflow: cashflowService,

  // Compras e Estoque
  purchase: purchaseService,
  inventory: inventoryService,

  // Contabilidade
  accounting: accountingService,

  // Fiscal
  fiscal: fiscalService,

  // BI e Analytics
  biDashboard: biDashboardService,

  // Custeio ABC
  costing: costingService,
};
