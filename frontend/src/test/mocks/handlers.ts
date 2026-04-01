/**
 * MSW Handlers para mock de APIs
 * Exporta todos os handlers de cada módulo
 */

import { licitacoesHandlers } from './handlers/licitacoes';
import { authHandlers } from './handlers/auth';
import { clientesHandlers } from './handlers/clientes';
import { crmHandlers } from './handlers/crm';
import { operacionalHandlers } from './handlers/operacional';
import { financialHandlers } from './handlers/financial';

// Exporta todos os handlers combinados
export const handlers = [
  ...licitacoesHandlers,
  ...authHandlers,
  ...clientesHandlers,
  ...crmHandlers,
  ...operacionalHandlers,
  ...financialHandlers,
];

// Re-exporta handlers individuais para uso específico
export {
  licitacoesHandlers,
  authHandlers,
  clientesHandlers,
  crmHandlers,
  operacionalHandlers,
  financialHandlers,
};
