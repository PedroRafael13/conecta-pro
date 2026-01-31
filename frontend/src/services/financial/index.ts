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
import supplierService from './supplierService';
import payableService from './payableService';

// Contas a Receber
import customerService from './customerService';
import receivableService from './receivableService';

// Fluxo de Caixa
import bankAccountService from './bankAccountService';
import bankTransactionService from './bankTransactionService';
import cashflowService from './cashflowService';

// Compras e Estoque
import purchaseService from './purchaseService';
import inventoryService from './inventoryService';

// Contabilidade
import accountingService from './accountingService';

// Fiscal
import fiscalService from './fiscalService';

// BI e Analytics
import biDashboardService from './biDashboardService';

// Custeio ABC
import costingService from './costingService';

// Named exports
export {
  supplierService,
  payableService,
  customerService,
  receivableService,
  bankAccountService,
  bankTransactionService,
  cashflowService,
  purchaseService,
  inventoryService,
  accountingService,
  fiscalService,
  biDashboardService,
  costingService,
};

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
