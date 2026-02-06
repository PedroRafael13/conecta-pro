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
import {
  guardianAccessLogService,
  guardianOccurrenceService,
  guardianEquipmentService,
  guardianSyncService,
} from './guardianService';
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

// Guardian Services
export {
  guardianAccessLogService,
  guardianOccurrenceService,
  guardianEquipmentService,
  guardianSyncService,
  GuardianAccessLogService,
  GuardianOccurrenceService,
  GuardianEquipmentService,
  GuardianSyncService,
} from './guardianService';

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
  guardian: {
    accessLog: guardianAccessLogService,
    occurrence: guardianOccurrenceService,
    equipment: guardianEquipmentService,
    sync: guardianSyncService,
  },
  monitoring: monitoringService,
  securityAudit: securityAuditService,
};
