# AUDITORIA DE SERVICES MANUAIS

Data: 2026-01-31 17:38:24

## Estatísticas
- Total de arquivos em src/services: 143
- Total de services (.service.ts): 103
- Total de módulos Orval: 19

## Módulos Orval Disponíveis

- **clients**: 4 arquivos
- **documents.ts**: arquivo único
- **equipment**: 5 arquivos
- **fase5**: 2 arquivos
- **financial**: 3267 arquivos
- **ged**: 389 arquivos
- **government**: 3 arquivos
- **health-occupational**: 2 arquivos
- **integrations**: 4 arquivos
- **mobile**: 2 arquivos
- **notifications**: 5 arquivos
- **operacional**: 15 arquivos
- **recruitment**: 2 arquivos
- **reimbursement**: 112 arquivos
- **scheduler**: 145 arquivos
- **search**: 9 arquivos
- **security-lgpd**: 8 arquivos
- **services**: 2 arquivos
- **workflows**: 2 arquivos

## Mapeamento por Módulo

### Módulo: ai

- **Arquivos totais**: 13
- **Services**: 6
- **Orval**: ❌ Não disponível
- **Arquivos**:
  - useDocumentsAI.ts: 7 exports
  - useOperationalAI.ts: 10 exports
  - useClientsAI.ts: 6 exports
  - useDocumentKitsAI.ts: 6 exports
  - useFinancialAI.ts: 13 exports
  - useBartolo.ts: 10 exports
  - financial.service.ts: 1 exports
  - documents.service.ts: 1 exports
  - document-kits.service.ts: 1 exports
  - bartolo.service.ts: 1 exports
  - clients.service.ts: 1 exports
  - operational.service.ts: 1 exports
  - index.ts: 0
0 exports

### Módulo: analytics

- **Arquivos totais**: 9
- **Services**: 8
- **Orval**: ❌ Não disponível
- **Arquivos**:
  - forecastService.ts: 1 exports
  - churnPredictionService.ts: 1 exports
  - fraudDetectionService.ts: 1 exports
  - modelManagementService.ts: 1 exports
  - executiveDashboardService.ts: 1 exports
  - leadScoringService.ts: 1 exports
  - featureStoreService.ts: 1 exports
  - monitoringService.ts: 1 exports
  - index.ts: 0
0 exports

### Módulo: audit

- **Arquivos totais**: 7
- **Services**: 6
- **Orval**: ❌ Não disponível
- **Arquivos**:
  - auditDashboardService.ts: 1 exports
  - complianceCheckService.ts: 1 exports
  - complianceRuleService.ts: 1 exports
  - accessHistoryService.ts: 1 exports
  - dataRetentionService.ts: 1 exports
  - auditLogService.ts: 1 exports
  - index.ts: 0
0 exports

### Módulo: bidding

- **Arquivos totais**: 6
- **Services**: 5
- **Orval**: ❌ Não disponível
- **Arquivos**:
  - documents.service.ts: 0
0 exports
  - certificates.service.ts: 0
0 exports
  - contracts.service.ts: 0
0 exports
  - proposals.service.ts: 0
0 exports
  - tenders.service.ts: 0
0 exports
  - index.ts: 0
0 exports

### Módulo: campo

- **Arquivos totais**: 11
- **Services**: 9
- **Orval**: ❌ Não disponível
- **Arquivos**:
  - campoService.ts: 2 exports
  - ordemServicoService.ts: 2 exports
  - securityAuditService.ts: 2 exports
  - checklistService.ts: 2 exports
  - roteirizacaoService.ts: 2 exports
  - estoqueService.ts: 2 exports
  - guardianService.ts: 8 exports
  - visitaService.ts: 2 exports
  - types.ts: 0
0 exports
  - monitoringService.ts: 2 exports
  - index.ts: 1 exports

### Módulo: clients

- **Arquivos totais**: 7
- **Services**: 6
- **Orval**: ✅ Disponível
- **Arquivos**:
  - clientAIService.ts: 0
0 exports
  - condominiumService.ts: 0
0 exports
  - unitService.ts: 0
0 exports
  - clientService.ts: 0
0 exports
  - integrationService.ts: 0
0 exports
  - contractService.ts: 0
0 exports
  - index.ts: 0
0 exports

### Módulo: config

- **Arquivos totais**: 7
- **Services**: 0
- **Orval**: ❌ Não disponível
- **Arquivos**:
  - feature-flags.ts: 21 exports
  - tenant-settings.ts: 14 exports
  - tenants.ts: 18 exports
  - system-config.ts: 17 exports
  - dashboards.ts: 16 exports
  - notification-templates.ts: 22 exports
  - index.ts: 0
0 exports

### Módulo: contracts

- **Arquivos totais**: 6
- **Services**: 5
- **Orval**: ❌ Não disponível
- **Arquivos**:
  - contractItemService.ts: 1 exports
  - contractSLAService.ts: 1 exports
  - contractTemplateService.ts: 1 exports
  - contractAddendumService.ts: 1 exports
  - contractService.ts: 1 exports
  - index.ts: 0
0 exports

### Módulo: diarists

- **Arquivos totais**: 4
- **Services**: 3
- **Orval**: ❌ Não disponível
- **Arquivos**:
  - diaristFiscalService.ts: 2 exports
  - diaristNotificationService.ts: 2 exports
  - diaristCoreService.ts: 2 exports
  - index.ts: 0
0 exports

### Módulo: document-kits

- **Arquivos totais**: 7
- **Services**: 6
- **Orval**: ❌ Não disponível
- **Arquivos**:
  - documentKitItemService.ts: 1 exports
  - documentKitService.ts: 1 exports
  - documentKitItemStatusService.ts: 1 exports
  - documentKitAssignmentService.ts: 1 exports
  - documentKitOperationalService.ts: 1 exports
  - documentKitAIService.ts: 1 exports
  - index.ts: 0
0 exports

### Módulo: documents

- **Arquivos totais**: 5
- **Services**: 0
- **Orval**: ✅ Disponível
- **Arquivos**:
  - processing.ts: 5 exports
  - metadata.ts: 5 exports
  - templates.ts: 4 exports
  - upload.ts: 2 exports
  - index.ts: 0
0 exports

### Módulo: equipment

- **Arquivos totais**: 5
- **Services**: 4
- **Orval**: ✅ Disponível
- **Arquivos**:
  - comodatoService.ts: 1 exports
  - installationService.ts: 1 exports
  - maintenanceService.ts: 1 exports
  - equipmentService.ts: 1 exports
  - index.ts: 0
0 exports

### Módulo: financial

- **Arquivos totais**: 1
- **Services**: 0
- **Orval**: ✅ Disponível
- **Arquivos**:
  - index.ts: 0
0 exports

### Módulo: government

- **Arquivos totais**: 9
- **Services**: 8
- **Orval**: ✅ Disponível
- **Arquivos**:
  - fgts-simples.service.ts: 0
0 exports
  - receita-federal.service.ts: 0
0 exports
  - nfse.service.ts: 0
0 exports
  - sefaz.service.ts: 0
0 exports
  - govbr-ecac.service.ts: 0
0 exports
  - esocial.service.ts: 0
0 exports
  - sped.service.ts: 0
0 exports
  - sync-certificates.service.ts: 0
0 exports
  - index.ts: 0
0 exports

### Módulo: hr

- **Arquivos totais**: 7
- **Services**: 6
- **Orval**: ❌ Não disponível
- **Arquivos**:
  - repIntegrationService.ts: 1 exports
  - timeTrackingService.ts: 1 exports
  - payrollIntegrationService.ts: 1 exports
  - mobileTimeClockService.ts: 1 exports
  - employeePortalService.ts: 1 exports
  - index.ts: 0
0 exports
  - analyticsDashboardService.ts: 1 exports

### Módulo: mobile

- **Arquivos totais**: 5
- **Services**: 4
- **Orval**: ✅ Disponível
- **Arquivos**:
  - mobileService.ts: 1 exports
  - deviceService.ts: 3 exports
  - syncService.ts: 2 exports
  - pushNotificationService.ts: 0
0 exports
  - index.ts: 0
0 exports

### Módulo: notifications

- **Arquivos totais**: 6
- **Services**: 5
- **Orval**: ✅ Disponível
- **Arquivos**:
  - preference.service.ts: 2 exports
  - intelligent.service.ts: 2 exports
  - template.service.ts: 2 exports
  - push.service.ts: 2 exports
  - index.ts: 0
0 exports
  - notification.service.ts: 2 exports

### Módulo: reimbursement

- **Arquivos totais**: 6
- **Services**: 5
- **Orval**: ✅ Disponível
- **Arquivos**:
  - reimbursementItemService.ts: 1 exports
  - reimbursementPaymentService.ts: 1 exports
  - reimbursementRequestService.ts: 1 exports
  - reimbursementApprovalService.ts: 1 exports
  - reimbursementAttachmentService.ts: 1 exports
  - index.ts: 0
0 exports

### Módulo: scheduler

- **Arquivos totais**: 7
- **Services**: 6
- **Orval**: ✅ Disponível
- **Arquivos**:
  - queue.service.ts: 4 exports
  - locks.service.ts: 4 exports
  - executions.service.ts: 4 exports
  - workers.service.ts: 3 exports
  - tasks.service.ts: 10 exports
  - index.ts: 0
0 exports
  - operations.service.ts: 1 exports

### Módulo: search

- **Arquivos totais**: 2
- **Services**: 1
- **Orval**: ✅ Disponível
- **Arquivos**:
  - searchService.ts: 1 exports
  - index.ts: 0
0 exports

### Módulo: security-lgpd

- **Arquivos totais**: 8
- **Services**: 7
- **Orval**: ✅ Disponível
- **Arquivos**:
  - maskingService.ts: 1 exports
  - consentService.ts: 1 exports
  - auditService.ts: 1 exports
  - encryptionService.ts: 1 exports
  - statusService.ts: 1 exports
  - erasureService.ts: 1 exports
  - index.ts: 0
0 exports
  - piaService.ts: 1 exports

### Módulo: workflows

- **Arquivos totais**: 3
- **Services**: 2
- **Orval**: ✅ Disponível
- **Arquivos**:
  - executionService.ts: 1 exports
  - index.ts: 0
0 exports
  - workflowService.ts: 1 exports

## Análise de Uso

Buscando imports de services no código...

- **ai/bartolo.service**: 1 imports

## Análise Completa
