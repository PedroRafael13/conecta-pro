# AUDITORIA COMPLETA: SERVICES MANUAIS VS HOOKS ORVAL

**Data:** 2026-01-31
**Projeto:** Conecta Plus - Frontend Next.js 16
**Objetivo:** Mapear todos os services manuais, identificar equivalentes Orval e priorizar migração

---

## 📊 ESTATÍSTICAS GERAIS

| Métrica | Quantidade |
|---------|-----------|
| **Arquivos totais em src/services** | 143 |
| **Services (.service.ts)** | 103 |
| **Módulos Orval disponíveis** | 19 |
| **Imports totais de services** | 127 |
| **Módulos com Orval** | 11 ✅ |
| **Módulos sem Orval** | 13 ❌ |

---

## 🎯 MÓDULOS ORVAL DISPONÍVEIS

### Prontos para uso (hooks gerados):

| Módulo | Arquivos | Status |
|--------|----------|--------|
| **clients** | 4 arquivos | ✅ Implementado |
| **equipment** | 5 arquivos | ✅ Implementado |
| **financial** | 3267 arquivos | ✅ Implementado |
| **ged** | 389 arquivos | ✅ Implementado |
| **government** | 3 arquivos | ✅ Implementado |
| **integrations** | 4 arquivos | ✅ Implementado |
| **mobile** | 2 arquivos | ✅ Implementado |
| **notifications** | 5 arquivos | ✅ Implementado |
| **reimbursement** | 112 arquivos | ✅ Implementado |
| **scheduler** | 145 arquivos | ✅ Implementado |
| **search** | 9 arquivos | ✅ Implementado |
| **security-lgpd** | 8 arquivos | ✅ Implementado |
| **workflows** | 2 arquivos | ✅ Implementado |

### Módulos especiais:

| Módulo | Tipo | Observação |
|--------|------|------------|
| **documents.ts** | Arquivo único | Schema de documentos |
| **fase5** | 2 arquivos | Módulo de migração |
| **health-occupational** | 2 arquivos | Saúde ocupacional |
| **operacional** | 15 arquivos | Operacional geral |
| **recruitment** | 2 arquivos | Recrutamento |
| **services** | 2 arquivos | Meta-services |

---

## 📋 MAPEAMENTO DETALHADO POR MÓDULO

### ✅ **CLIENTS** (Orval Disponível)

**Status:** Migrado para Orval
**Services manuais:** 6 arquivos
**Uso:** Baixo (0 imports diretos)

| Arquivo | Funções | Status |
|---------|---------|--------|
| `clientService.ts` | 0 exports | ✅ DEPRECATED - Re-exporta hooks Orval |
| `condominiumService.ts` | 0 exports | ⚠️ Vazio |
| `unitService.ts` | 0 exports | ⚠️ Vazio |
| `clientAIService.ts` | 0 exports | ⚠️ Vazio |
| `integrationService.ts` | 0 exports | ⚠️ Vazio |
| `contractService.ts` | 0 exports | ⚠️ Vazio |

**Ação:** 🗑️ **DELETAR** - Services vazios ou migrados

---

### ✅ **DOCUMENTS** (Orval Disponível)

**Status:** Parcialmente migrado
**Services manuais:** 5 arquivos
**Uso:** Médio (4 imports)

| Arquivo | Funções | Status | Uso |
|---------|---------|--------|-----|
| `upload.ts` | 2 exports | 🔄 Service ativo | 1 import |
| `processing.ts` | 5 exports | 🔄 Service ativo | 1 import |
| `metadata.ts` | 5 exports | 🔄 Service ativo | 1 import |
| `templates.ts` | 4 exports | 🔄 Service ativo | 1 import |

**Ação:** 🔄 **MIGRAR** - Verificar hooks Orval em `src/types/generated/documents.ts`

---

### ✅ **EQUIPMENT** (Orval Disponível)

**Status:** Services ativos
**Services manuais:** 4 arquivos
**Uso:** Baixo (4 imports)

| Arquivo | Funções | Status | Uso |
|---------|---------|--------|-----|
| `equipmentService.ts` | 1 export | 🔄 Service ativo | 1 import |
| `maintenanceService.ts` | 1 export | 🔄 Service ativo | 1 import |
| `installationService.ts` | 1 export | 🔄 Service ativo | 1 import |
| `comodatoService.ts` | 1 export | 🔄 Service ativo | 1 import |

**Ação:** 🔄 **MIGRAR** - Hooks Orval em `src/types/generated/equipment/`

---

### ✅ **GOVERNMENT** (Orval Disponível)

**Status:** Services implementados
**Services manuais:** 8 arquivos
**Uso:** Baixo (8 imports)

| Arquivo | Funções | Status | Uso |
|---------|---------|--------|-----|
| `esocial.service.ts` | 8 exports | 🔄 Service ativo | 1 import |
| `sped.service.ts` | 0 exports | ⚠️ Vazio | 1 import |
| `nfse.service.ts` | 0 exports | ⚠️ Vazio | 1 import |
| `sefaz.service.ts` | 0 exports | ⚠️ Vazio | 1 import |
| `receita-federal.service.ts` | 0 exports | ⚠️ Vazio | 1 import |
| `fgts-simples.service.ts` | 0 exports | ⚠️ Vazio | 1 import |
| `govbr-ecac.service.ts` | 0 exports | ⚠️ Vazio | 1 import |
| `sync-certificates.service.ts` | 0 exports | ⚠️ Vazio | 1 import |

**Ação:**
- 🔄 **MIGRAR** `esocial.service.ts` para hooks Orval
- 🗑️ **DELETAR** services vazios

---

### ✅ **MOBILE** (Orval Disponível)

**Status:** Services ativos
**Services manuais:** 4 arquivos
**Uso:** Baixo (4 imports)

| Arquivo | Funções | Status | Uso |
|---------|---------|--------|-----|
| `mobileService.ts` | 1 export | 🔄 Service ativo | 1 import |
| `deviceService.ts` | 3 exports | 🔄 Service ativo | 1 import |
| `syncService.ts` | 2 exports | 🔄 Service ativo | 1 import |
| `pushNotificationService.ts` | 0 exports | ⚠️ Vazio | 1 import |

**Ação:** 🔄 **MIGRAR** para `src/types/generated/mobile/`

---

### ✅ **NOTIFICATIONS** (Orval Disponível)

**Status:** Services ativos
**Services manuais:** 5 arquivos
**Uso:** Médio (5 imports)

| Arquivo | Funções | Status | Uso |
|---------|---------|--------|-----|
| `notification.service.ts` | 2 exports | 🔄 Service ativo | Hooks |
| `preference.service.ts` | 2 exports | 🔄 Service ativo | Hooks |
| `intelligent.service.ts` | 2 exports | 🔄 Service ativo | Hooks |
| `template.service.ts` | 2 exports | 🔄 Service ativo | Hooks |
| `push.service.ts` | 2 exports | 🔄 Service ativo | Hooks |

**Ação:** 🔄 **MIGRAR ALTA PRIORIDADE** - Usado em hooks custom

---

### ✅ **REIMBURSEMENT** (Orval Disponível)

**Status:** Services ativos
**Services manuais:** 5 arquivos
**Uso:** Médio (5 imports)

| Arquivo | Funções | Status | Uso |
|---------|---------|--------|-----|
| `reimbursementRequestService.ts` | 1 export | 🔄 Service ativo | Hooks |
| `reimbursementApprovalService.ts` | 1 export | 🔄 Service ativo | Hooks |
| `reimbursementItemService.ts` | 1 export | 🔄 Service ativo | Hooks |
| `reimbursementPaymentService.ts` | 1 export | 🔄 Service ativo | Hooks |
| `reimbursementAttachmentService.ts` | 1 export | 🔄 Service ativo | Hooks |

**Ação:** 🔄 **MIGRAR** - 112 hooks Orval disponíveis

---

### ✅ **SCHEDULER** (Orval Disponível)

**Status:** Services ativos
**Services manuais:** 6 arquivos
**Uso:** Baixo (6 imports)

| Arquivo | Funções | Status | Uso |
|---------|---------|--------|-----|
| `tasks.service.ts` | 10 exports | 🔄 Service ativo | 1 import |
| `queue.service.ts` | 4 exports | 🔄 Service ativo | 1 import |
| `locks.service.ts` | 4 exports | 🔄 Service ativo | 1 import |
| `executions.service.ts` | 4 exports | 🔄 Service ativo | 1 import |
| `workers.service.ts` | 3 exports | 🔄 Service ativo | 1 import |
| `operations.service.ts` | 1 export | 🔄 Service ativo | 1 import |

**Ação:** 🔄 **MIGRAR** - 145 hooks Orval disponíveis

---

### ✅ **SEARCH** (Orval Disponível)

**Status:** Service ativo
**Services manuais:** 1 arquivo
**Uso:** Baixo (1 import)

| Arquivo | Funções | Status | Uso |
|---------|---------|--------|-----|
| `searchService.ts` | 1 export | 🔄 Service ativo | 1 import |

**Ação:** 🔄 **MIGRAR** - 9 hooks Orval disponíveis

---

### ✅ **SECURITY-LGPD** (Orval Disponível)

**Status:** Services ativos
**Services manuais:** 7 arquivos
**Uso:** **ALTO** (20 imports) 🔥

| Arquivo | Funções | Status | Uso |
|---------|---------|--------|-----|
| `encryptionService.ts` | 1 export | 🔄 Service ativo | Muito usado |
| `maskingService.ts` | 1 export | 🔄 Service ativo | Muito usado |
| `consentService.ts` | 1 export | 🔄 Service ativo | Muito usado |
| `auditService.ts` | 1 export | 🔄 Service ativo | Muito usado |
| `erasureService.ts` | 1 export | 🔄 Service ativo | Muito usado |
| `statusService.ts` | 1 export | 🔄 Service ativo | Muito usado |
| `piaService.ts` | 1 export | 🔄 Service ativo | Muito usado |

**Ação:** 🔥 **MIGRAR URGENTE** - Módulo crítico e muito usado

---

### ✅ **WORKFLOWS** (Orval Disponível)

**Status:** Services ativos
**Services manuais:** 2 arquivos
**Uso:** Baixo (3 imports)

| Arquivo | Funções | Status | Uso |
|---------|---------|--------|-----|
| `workflowService.ts` | 1 export | 🔄 Service ativo | 1 import |
| `executionService.ts` | 1 export | 🔄 Service ativo | 1 import |

**Ação:** 🔄 **MIGRAR** - 2 hooks Orval disponíveis

---

### ❌ **AI** (Orval NÃO Disponível)

**Status:** Services + Hooks custom
**Services manuais:** 13 arquivos (6 services + 7 hooks)
**Uso:** Baixo (2 imports)

| Arquivo | Tipo | Funções | Observação |
|---------|------|---------|------------|
| `bartolo.service.ts` | Service | 1 export | API Bartolo (IA) |
| `clients.service.ts` | Service | 1 export | IA para clientes |
| `documents.service.ts` | Service | 1 export | IA para documentos |
| `document-kits.service.ts` | Service | 1 export | IA para kits |
| `financial.service.ts` | Service | 1 export | IA financeiro |
| `operational.service.ts` | Service | 1 export | IA operacional |
| `useBartolo.ts` | Hook | 10 exports | Hook custom |
| `useClientsAI.ts` | Hook | 6 exports | Hook custom |
| `useDocumentsAI.ts` | Hook | 7 exports | Hook custom |
| `useDocumentKitsAI.ts` | Hook | 6 exports | Hook custom |
| `useFinancialAI.ts` | Hook | 13 exports | Hook custom |
| `useOperationalAI.ts` | Hook | 10 exports | Hook custom |

**Ação:** 🔧 **MANTER** - Módulo de IA sem spec OpenAPI no backend

---

### ❌ **ANALYTICS** (Orval NÃO Disponível)

**Status:** Services de Analytics/ML
**Services manuais:** 8 arquivos
**Uso:** Médio (8 imports)

| Arquivo | Funções | Observação |
|---------|---------|------------|
| `churnPredictionService.ts` | 1 export | Usa hooks gerados em `/api/generated/analytics/` |
| `executiveDashboardService.ts` | 1 export | Dashboard executivo |
| `featureStoreService.ts` | 1 export | Feature store ML |
| `forecastService.ts` | 1 export | Previsões |
| `fraudDetectionService.ts` | 1 export | Detecção fraude |
| `leadScoringService.ts` | 1 export | Scoring de leads |
| `modelManagementService.ts` | 1 export | Gestão modelos ML |
| `monitoringService.ts` | 1 export | Monitoramento |

**Ação:** 🔍 **VERIFICAR** - Já usa hooks em `@/api/generated/analytics/`

---

### ❌ **AUDIT** (Orval NÃO Disponível)

**Status:** Services de auditoria
**Services manuais:** 6 arquivos
**Uso:** Médio (via hooks)

| Arquivo | Funções | Observação |
|---------|---------|------------|
| `auditLogService.ts` | 1 export | Logs de auditoria |
| `auditDashboardService.ts` | 1 export | Dashboard |
| `accessHistoryService.ts` | 1 export | Histórico de acesso |
| `complianceCheckService.ts` | 1 export | Verificações compliance |
| `complianceRuleService.ts` | 1 export | Regras compliance |
| `dataRetentionService.ts` | 1 export | Retenção de dados |

**Ação:** 🔧 **MANTER OU GERAR SPEC** - Considerar criar spec OpenAPI

---

### ❌ **BIDDING** (Orval NÃO Disponível)

**Status:** Services de licitações
**Services manuais:** 5 arquivos
**Uso:** Baixo (0 imports diretos)

| Arquivo | Funções | Observação |
|---------|---------|------------|
| `tenders.service.ts` | 11 exports | Editais (PNCP, Lei 14.133) |
| `proposals.service.ts` | 0 exports | ⚠️ Vazio |
| `documents.service.ts` | 0 exports | ⚠️ Vazio |
| `certificates.service.ts` | 0 exports | ⚠️ Vazio |
| `contracts.service.ts` | 0 exports | ⚠️ Vazio |

**Ação:**
- 🔧 **MANTER** `tenders.service.ts` - Funcional
- 🗑️ **DELETAR** services vazios

---

### ❌ **CAMPO** (Orval NÃO Disponível)

**Status:** Services de campo/operações
**Services manuais:** 9 arquivos + types
**Uso:** Médio (12 imports - 7 services + 5 types)

| Arquivo | Funções | Observação |
|---------|---------|------------|
| `campoService.ts` | 2 exports | Operações de campo |
| `ordemServicoService.ts` | 2 exports | Ordens de serviço |
| `checklistService.ts` | 2 exports | Checklists |
| `visitaService.ts` | 2 exports | Visitas |
| `estoqueService.ts` | 2 exports | Estoque |
| `roteirizacaoService.ts` | 2 exports | Roteirização |
| `monitoringService.ts` | 2 exports | Monitoramento |
| `guardianService.ts` | 8 exports | Guardian (segurança) |
| `securityAuditService.ts` | 2 exports | Auditoria segurança |
| `types.ts` | 0 exports | Tipos TypeScript |

**Ação:** 🔧 **MANTER OU GERAR SPEC** - Módulo funcional e usado

---

### ❌ **CONFIG** (Orval NÃO Disponível)

**Status:** Services de configuração
**Services manuais:** 7 arquivos (não .service.ts)
**Uso:** Desconhecido

| Arquivo | Funções | Observação |
|---------|---------|------------|
| `feature-flags.ts` | 21 exports | Feature flags (usa schemas de `/types/generated/config/`) |
| `tenant-settings.ts` | 14 exports | Configurações tenant |
| `tenants.ts` | 18 exports | Gestão tenants |
| `system-config.ts` | 17 exports | Config sistema |
| `dashboards.ts` | 16 exports | Dashboards |
| `notification-templates.ts` | 22 exports | Templates notificação |

**Ação:** 🔍 **VERIFICAR** - Já usa schemas de `@/types/generated/config/`

---

### ❌ **CONTRACTS** (Orval NÃO Disponível)

**Status:** Services de contratos
**Services manuais:** 5 arquivos
**Uso:** Médio (5 imports)

| Arquivo | Funções | Observação |
|---------|---------|------------|
| `contractService.ts` | 1 export | Contratos |
| `contractTemplateService.ts` | 1 export | Templates |
| `contractItemService.ts` | 1 export | Itens |
| `contractSLAService.ts` | 1 export | SLAs |
| `contractAddendumService.ts` | 1 export | Aditivos |

**Ação:** 🔧 **MANTER OU GERAR SPEC** - Considerar criar spec OpenAPI

---

### ❌ **DIARISTS** (Orval NÃO Disponível)

**Status:** Services de diaristas
**Services manuais:** 3 arquivos
**Uso:** **ALTO** (9 imports) 🔥

| Arquivo | Funções | Observação |
|---------|---------|------------|
| `diaristCoreService.ts` | 2 exports | Core diaristas |
| `diaristFiscalService.ts` | 2 exports | Fiscal |
| `diaristNotificationService.ts` | 2 exports | Notificações |

**Ação:** 🔥 **GERAR SPEC ORVAL** - Muito usado, precisa de padronização

---

### ❌ **DOCUMENT-KITS** (Orval NÃO Disponível)

**Status:** Services de kits documentais
**Services manuais:** 6 arquivos
**Uso:** Baixo (0 imports diretos)

| Arquivo | Funções | Observação |
|---------|---------|------------|
| `documentKitService.ts` | 1 export | Kits |
| `documentKitItemService.ts` | 1 export | Itens |
| `documentKitItemStatusService.ts` | 1 export | Status |
| `documentKitAssignmentService.ts` | 1 export | Atribuições |
| `documentKitOperationalService.ts` | 1 export | Operacional |
| `documentKitAIService.ts` | 1 export | IA |

**Ação:** 🔧 **MANTER OU GERAR SPEC** - Considerar criar spec OpenAPI

---

### ❌ **HR** (Orval NÃO Disponível)

**Status:** Services de RH
**Services manuais:** 6 arquivos
**Uso:** Médio (6 imports)

| Arquivo | Funções | Observação |
|---------|---------|------------|
| `timeTrackingService.ts` | 1 export | Ponto eletrônico |
| `payrollIntegrationService.ts` | 1 export | Folha pagamento |
| `repIntegrationService.ts` | 1 export | REP |
| `mobileTimeClockService.ts` | 1 export | Ponto mobile |
| `employeePortalService.ts` | 1 export | Portal colaborador |
| `analyticsDashboardService.ts` | 1 export | Analytics RH |

**Ação:** 🔧 **MANTER OU GERAR SPEC** - Considerar criar spec OpenAPI

---

### ⚠️ **RECRUITMENT** (Service único)

**Status:** Service de recrutamento
**Arquivo:** `recruitment.service.ts`
**Uso:** Baixo (1 import)

**Ação:** 🔍 **VERIFICAR** - Verificar se existe em `@/types/generated/recruitment/`

---

## 🎯 PLANO DE MIGRAÇÃO PRIORIZADO

### 🔥 **ALTA PRIORIDADE** (Migrar Primeiro)

| Módulo | Motivo | Hooks Orval | Impacto |
|--------|--------|-------------|---------|
| **security-lgpd** | 20 imports, crítico LGPD | 8 arquivos | 🔥🔥🔥 |
| **notifications** | 5 imports, usado em hooks | 5 arquivos | 🔥🔥 |
| **reimbursement** | 5 imports, 112 hooks | 112 arquivos | 🔥🔥 |

### 🔄 **MÉDIA PRIORIDADE**

| Módulo | Motivo | Hooks Orval | Impacto |
|--------|--------|-------------|---------|
| **scheduler** | 6 imports, 145 hooks | 145 arquivos | 🔄🔄 |
| **documents** | 4 imports, parcial | 1 arquivo | 🔄🔄 |
| **equipment** | 4 imports | 5 arquivos | 🔄 |
| **mobile** | 4 imports | 2 arquivos | 🔄 |
| **workflows** | 3 imports | 2 arquivos | 🔄 |

### 🔧 **BAIXA PRIORIDADE OU MANTER**

| Módulo | Ação | Motivo |
|--------|------|--------|
| **ai** | MANTER | Módulo IA sem spec OpenAPI |
| **analytics** | VERIFICAR | Já usa hooks de `/api/generated/analytics/` |
| **config** | VERIFICAR | Já usa schemas de `/types/generated/config/` |
| **campo** | MANTER | 12 imports, sem spec |
| **diarists** | GERAR SPEC | 9 imports, precisa padronizar |
| **hr** | MANTER | 6 imports, sem spec |
| **contracts** | MANTER | 5 imports, sem spec |
| **audit** | MANTER | Sem spec OpenAPI |
| **document-kits** | MANTER | 0 imports diretos |
| **bidding** | MANTER tenders | Funcional, deletar vazios |

### 🗑️ **DELETAR**

| Módulo | Arquivos | Motivo |
|--------|----------|--------|
| **clients** | 6 arquivos | Todos vazios ou migrados |
| **government** | 7 arquivos | Vazios (manter esocial) |
| **bidding** | 4 arquivos | Vazios (manter tenders) |

---

## 📝 RESUMO EXECUTIVO

### Status Atual:

- **143 arquivos** em `src/services`
- **103 services** (.service.ts)
- **19 módulos Orval** disponíveis
- **127 imports** de services no código

### Problemas Identificados:

1. **Duplicação**: Services manuais coexistem com hooks Orval
2. **Inconsistência**: Alguns migrados, outros não
3. **Services vazios**: ~15 arquivos sem código útil
4. **Fragmentação**: Hooks em `/types/generated/` e `/api/generated/`

### Recomendações:

1. **Migrar urgente**: security-lgpd, notifications, reimbursement
2. **Deletar vazios**: clients/*, government/*, bidding/* (exceto tenders, esocial)
3. **Gerar specs**: diarists, contracts, hr, campo
4. **Manter**: ai, analytics (já usa hooks gerados), config
5. **Padronizar**: Consolidar todos hooks Orval em `/types/generated/`

### Próximos Passos:

1. ✅ Migrar módulos de alta prioridade
2. 🗑️ Deletar services vazios/obsoletos
3. 🔍 Verificar uso real de analytics e config
4. 🔧 Gerar specs OpenAPI para módulos críticos sem Orval
5. 📚 Documentar padrão de uso de hooks Orval

---

**Gerado em:** 2026-01-31
**Ferramenta:** Claude Code - Auditoria Automatizada
