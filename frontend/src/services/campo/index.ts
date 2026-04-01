/**
 * CAMPO Services - Índice de Exports
 * Módulo completo de Serviço de Campo
 */

// Imports para o objeto agregador
import { ordemServicoService } from './ordemServicoService';
import { visitaService } from './visitaService';
import { checklistService } from './checklistService';
import { roteirizacaoService } from './roteirizacaoService';
import { estoqueService } from './estoqueService';
import { campoServiceMain } from './campoService';
import { monitoringService } from './monitoringService';
import { securityAuditService } from './securityAuditService';

// Ordens de Serviço
export {
  ordemServicoService,
  OrdemServicoService,
} from './ordemServicoService';

// Visitas
export { visitaService, VisitaService } from './visitaService';

// Checklists
export { checklistService, ChecklistService } from './checklistService';

// Roteirização
export {
  roteirizacaoService,
  RoteirizacaoService,
} from './roteirizacaoService';

// Estoque
export { estoqueService, EstoqueService } from './estoqueService';

// Campo Service Principal
export { campoServiceMain, CampoServiceMain } from './campoService';

// Monitoring
export { monitoringService, MonitoringService } from './monitoringService';

// Security Audit
export {
  securityAuditService,
  SecurityAuditService,
} from './securityAuditService';

/**
 * Objeto agregador com todos os services
 */
export const campoServices = {
  ordemServico: ordemServicoService,
  visita: visitaService,
  checklist: checklistService,
  roteirizacao: roteirizacaoService,
  estoque: estoqueService,
  campo: campoServiceMain,
  monitoring: monitoringService,
  securityAudit: securityAuditService,
};
