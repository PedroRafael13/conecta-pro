# GAP Analysis - Testes Unitários

> **Data da análise:** 2026-02-05
> **Projeto:** Conecta Pro Frontend
> **Local:** /opt/conecta-pro/frontend

---

## 📊 Resumo Executivo

| Categoria | Total | Com Teste | SEM Teste | Cobertura |
|-----------|-------|-----------|-----------|-----------|
| Componentes (.tsx) | 164 | 18 | **146** | ~11% |
| Hooks (.ts) | 207 | 9 | **198** | ~4% |
| Utilitários (lib+utils) | 63 | 4 | **59** | ~6% |
| **TOTAL** | **434** | **31** | **403** | **~7%** |

---

## 🧩 Componentes SEM Teste (por módulo)

### UI Components (src/components/ui/)
**Com teste:** 17 | **Sem teste:** 18

#### ❌ SEM Teste (18 componentes):
- [ ] `alert-dialog.tsx` - Modal de confirmação
- [ ] `avatar.tsx` - Componente de avatar do usuário
- [ ] `chart-skeleton.tsx` - Skeleton para gráficos
- [ ] `coming-soon.tsx` - Placeholder de "em breve"
- [ ] `dropdown-menu.tsx` - Menu dropdown
- [ ] `export-button.tsx` - Botão de exportação
- [ ] `form-skeleton.tsx` - Skeleton para formulários
- [ ] `kpi-widget.tsx` - Widget de KPIs
- [ ] `module-card.tsx` - Card de módulos
- [ ] `permission-guard.tsx` - Guarda de permissões
- [ ] `progress.tsx` - Barra de progresso
- [ ] `restore-alert.tsx` - Alerta de restauração
- [ ] `save-indicator.tsx` - Indicador de salvamento
- [ ] `scroll-area.tsx` - Área scrollável
- [ ] `sparkline.tsx` - Mini gráfico sparkline
- [ ] `stepper.tsx` - Stepper/Steps
- [ ] `table-skeleton.tsx` - Skeleton para tabelas
- [ ] `toaster.tsx` - Container de toasts

#### ✅ COM Teste (17 componentes):
- [x] `alert.test.tsx`
- [x] `badge.test.tsx`
- [x] `button.test.tsx`
- [x] `card.test.tsx`
- [x] `dialog.test.tsx`
- [x] `input.test.tsx`
- [x] `label.test.tsx`
- [x] `loading-state.test.tsx`
- [x] `modal.test.tsx`
- [x] `select.test.tsx`
- [x] `separator.test.tsx`
- [x] `switch.test.tsx`
- [x] `table.test.tsx`
- [x] `tabs.test.tsx`
- [x] `textarea.test.tsx`
- [x] `toast.test.tsx`
- [x] `tooltip.test.tsx`

---

### Operacional (src/components/operacional/)
**Total:** 21 | **Sem teste:** 21

- [ ] `allocation-detail-modal.tsx`
- [ ] `allocation-form-modal.tsx`
- [ ] `announcement-detail-modal.tsx`
- [ ] `announcement-form-modal.tsx`
- [ ] `diarist-form-modal.tsx`
- [ ] `disciplinary-detail-modal.tsx`
- [ ] `disciplinary-form-modal.tsx`
- [ ] `disciplinary-signature-modal.tsx`
- [ ] `notification-center.tsx`
- [ ] `occurrence-detail-modal.tsx`
- [ ] `occurrence-form-modal.tsx`
- [ ] `occurrence-resolve-modal.tsx`
- [ ] `patrol-round-detail-modal.tsx`
- [ ] `post-detail-modal.tsx`
- [ ] `post-form-modal.tsx`
- [ ] `scale-editor.tsx`
- [ ] `scale-generate-modal.tsx`
- [ ] `shift-calendar.tsx`
- [ ] `shift-check-modal.tsx`
- [ ] `shift-day-view.tsx`
- [ ] `signature-pad.tsx`

---

### Financeiro (src/components/financeiro/)
**Total:** 17 | **Sem teste:** 17

- [ ] `bank-account-form-modal.tsx`
- [ ] `bank-transaction-detail-modal.tsx`
- [ ] `billing-rule-form-modal.tsx`
- [ ] `cashflow-form-modal.tsx`
- [ ] `customer-form-modal.tsx`
- [ ] `inventory-form-modal.tsx`
- [ ] `journal-entry-form-modal.tsx`
- [ ] `nfe-detail-modal.tsx`
- [ ] `nfe-form-modal.tsx`
- [ ] `payable-detail-modal.tsx`
- [ ] `payable-form-modal.tsx`
- [ ] `purchase-detail-modal.tsx`
- [ ] `purchase-form-modal.tsx`
- [ ] `receivable-detail-modal.tsx`
- [ ] `receivable-form-modal.tsx`
- [ ] `supplier-detail-modal.tsx`
- [ ] `supplier-form-modal.tsx`

---

### Licitações (src/components/licitacoes/)
**Total:** 17 | **Sem teste:** 17

- [ ] `CertificateStatusBadge.tsx`
- [ ] `CertificateTypeIcon.tsx`
- [ ] `CertificateUploadModal.tsx`
- [ ] `ContractAddendumModal.tsx`
- [ ] `ContractFormModal.tsx`
- [ ] `ContractStatusBadge.tsx`
- [ ] `DocumentStatusBadge.tsx`
- [ ] `DocumentUploadModal.tsx`
- [ ] `ModalityBadge.tsx`
- [ ] `ProposalFilters.tsx`
- [ ] `ProposalFormModal.tsx`
- [ ] `ProposalItemsManager.tsx`
- [ ] `ProposalStatusBadge.tsx`
- [ ] `SubmitProposalDialog.tsx`
- [ ] `TenderFilters.tsx`
- [ ] `TenderFormModal.tsx`
- [ ] `TenderStatusBadge.tsx`

---

### CRM (src/components/crm/)
**Total:** 4 | **Sem teste:** 4

- [ ] `cliente-detail-modal.tsx`
- [ ] `cliente-form-modal.tsx`
- [ ] `oportunidade-detail-modal.tsx`
- [ ] `oportunidade-form-modal.tsx`

---

### Segurança/LGPD (src/components/seguranca/)
**Total:** 7 | **Sem teste:** 7

- [ ] `audit-detail-modal.tsx`
- [ ] `consent-detail-modal.tsx`
- [ ] `consent-form-modal.tsx`
- [ ] `erasure-request-modal.tsx`
- [ ] `pia-detail-modal.tsx`
- [ ] `pia-form-modal.tsx`

---

### Configurações (src/components/configuracoes/)
**Total:** 8 | **Sem teste:** 8

- [ ] `config-value-editor.tsx`
- [ ] `feature-flag-detail-modal.tsx`
- [ ] `feature-flag-form-modal.tsx`
- [ ] `system-config-form-modal.tsx`
- [ ] `template-form-modal.tsx`
- [ ] `template-preview-modal.tsx`
- [ ] `tenant-detail-modal.tsx`
- [ ] `tenant-form-modal.tsx`

---

### GED (src/components/ged/)
**Total:** 8 | **Sem teste:** 8

- [ ] `DocumentApprovalDialog.tsx`
- [ ] `DocumentShareDialog.tsx`
- [ ] `DocumentSignatureDialog.tsx`
- [ ] `DocumentTagManager.tsx`
- [ ] `DocumentVersionHistory.tsx`
- [ ] `EditDocumentDialog.tsx`
- [ ] `FolderTree.tsx`
- [ ] `MoveFolderDialog.tsx`

---

### Campo (src/components/campo/)
**Total:** 4 | **Sem teste:** 4

- [ ] `checkin-detail-modal.tsx`
- [ ] `comunicado-detail-modal.tsx`
- [ ] `comunicado-form-modal.tsx`
- [ ] `monitoramento-detail-modal.tsx`

---

### Equipamentos (src/components/equipamentos/)
**Total:** 6 | **Sem teste:** 6

- [ ] `comodato-detail-modal.tsx`
- [ ] `comodato-form-modal.tsx`
- [ ] `equipment-detail-modal.tsx`
- [ ] `equipment-form-modal.tsx`
- [ ] `maintenance-detail-modal.tsx`
- [ ] `maintenance-form-modal.tsx`

---

### Fiscal (src/components/fiscal/)
**Total:** 7 | **Sem teste:** 7

- [ ] `certidao-detail-modal.tsx`
- [ ] `dctfweb-detail-modal.tsx`
- [ ] `esocial-detail-modal.tsx`
- [ ] `nfse-detail-modal.tsx`
- [ ] `nfse-form-modal.tsx`
- [ ] `reinf-detail-modal.tsx`
- [ ] `sped-detail-modal.tsx`

---

### Serviços (src/components/servicos/)
**Total:** 6 | **Sem teste:** 6

- [ ] `agendamento-detail-modal.tsx`
- [ ] `agendamento-form-modal.tsx`
- [ ] `contrato-detail-modal.tsx`
- [ ] `contrato-form-modal.tsx`
- [ ] `ordem-detail-modal.tsx`
- [ ] `ordem-form-modal.tsx`

---

### Reembolso (src/components/reembolso/)
**Total:** 4 | **Sem teste:** 4

- [ ] `attachment-upload.tsx`
- [ ] `reimbursement-approval-modal.tsx`
- [ ] `reimbursement-detail-modal.tsx`
- [ ] `reimbursement-form-modal.tsx`

---

### Integrações (src/components/integracoes/)
**Total:** 5 | **Sem teste:** 5

- [ ] `api-key-form-modal.tsx`
- [ ] `connector-detail-modal.tsx`
- [ ] `log-detail-modal.tsx`
- [ ] `webhook-detail-modal.tsx`
- [ ] `webhook-form-modal.tsx`

---

### AI (src/components/ai/)
**Total:** 2 | **Sem teste:** 2

- [ ] `ActionConfirmationModal.tsx`
- [ ] `BartoloChatWidget.tsx`

---

### Lazy Loading (src/components/lazy/)
**Total:** 2 | **Sem teste:** 2

- [ ] `LazyDialog.tsx`
- [ ] `LazyDropdown.tsx`

---

### Root Components (src/components/)
**Total:** 11 | **Sem teste:** 11

- [ ] `BartoloChat.tsx`
- [ ] `BartoloClientWrapper.tsx`
- [ ] `CommandPalette.tsx`
- [ ] `GlobalSearch.tsx`
- [ ] `HelpOverlay.tsx`
- [ ] `NotificationBell.tsx`
- [ ] `ProductivityProvider.tsx`
- [ ] `QuickActions.tsx`
- [ ] `ResponsiveTable.tsx`
- [ ] `SearchTrigger.tsx`
- [ ] `ThemeToggle.tsx`

---

### Providers (src/components/providers/)
**Total:** 1 | **Sem teste:** 1

- [ ] `draft-cleanup-provider.tsx`

---

## 🔗 Hooks SEM Teste

### Hooks Core (src/hooks/)
**Com teste:** 7 | **Sem teste:** Vários

#### ✅ COM Teste:
- [x] `useAuth.test.ts`
- [x] `useDebounce.test.ts`
- [x] `useFetch.test.ts`
- [x] `useForm.test.ts`
- [x] `useLocalStorage.test.ts`
- [x] `usePagination.test.ts`
- [x] `usePermission.test.ts`

#### ❌ SEM Teste - Auth/Permission:
- [ ] `useAuth.ts`
- [ ] `usePermission.ts`

#### ❌ SEM Teste - Data/Fetch:
- [ ] `useAllocations.ts`
- [ ] `useAnalyticsData.ts`
- [ ] `useAnnouncements.ts`
- [ ] `useAutoSave.ts`
- [ ] `useDashboard.ts`
- [ ] `useDebounce.ts`
- [ ] `useDisciplinary.ts`
- [ ] `useEmployees.ts`
- [ ] `useFetch.ts`
- [ ] `useForm.ts`
- [ ] `useKPITrends.ts`
- [ ] `useKeyboardShortcuts.ts`
- [ ] `useLeads.ts`
- [ ] `useLocalStorage.ts`
- [ ] `useNotifications.ts`
- [ ] `useOccurrences.ts`
- [ ] `usePagination.ts`
- [ ] `usePatrolRounds.ts`
- [ ] `usePosts.ts`
- [ ] `useReimbursement.ts`
- [ ] `useRecruitment.ts`
- [ ] `useScaleTemplates.ts`
- [ ] `useScales.ts`
- [ ] `useShifts.ts`

---

### Hooks Operacionais (src/hooks/operacional/)
**Com teste:** 2 | **Sem teste:** 14

#### ✅ COM Teste:
- [x] `useOccurrences.test.tsx`
- [x] `usePosts.test.tsx`

#### ❌ SEM Teste (14 hooks):
- [ ] `useAllocations.ts`
- [ ] `useDiarists.ts`
- [ ] `useDisciplinary.ts`
- [ ] `useEmployees.ts`
- [ ] `useKPITrends.ts`
- [ ] `usePatrolRounds.ts`
- [ ] `usePosts.ts`
- [ ] `useReports.ts`
- [ ] `useScaleTemplates.ts`
- [ ] `useScales.ts`
- [ ] `useShifts.ts`
- [ ] `useSubstitutions.ts`
- [ ] `useTimeBank.ts`

---

### Hooks Saúde Ocupacional (src/hooks/health-occupational/)
**Total:** 4 | **Sem teste:** 4

- [ ] `useEPI.ts`
- [ ] `usePCMSO.ts`
- [ ] `usePPRA.ts`

---

### Hooks GED (src/hooks/ged/)
**Total:** 3 | **Sem teste:** 3

- [ ] `useGedDocuments.ts`
- [ ] `useGedFolders.ts`

---

### Hooks Documentos (src/hooks/documents/)
**Total:** 5 | **Sem teste:** 5

- [ ] `useMetadata.ts`
- [ ] `useProcessing.ts`
- [ ] `useTemplates.ts`
- [ ] `useUpload.ts`

---

### Hooks Financeiro (src/hooks/financial/)
**Total:** 3 | **Sem teste:** 3

- [ ] `useFinancial.ts`
- [ ] `useSuppliers.ts`

---

### Hooks Segurança/LGPD (src/hooks/security-lgpd/)
**Total:** 8 | **Sem teste:** 8

- [ ] `useAudit.ts`
- [ ] `useConsent.ts`
- [ ] `useEncryption.ts`
- [ ] `useErasure.ts`
- [ ] `useMasking.ts`
- [ ] `usePIA.ts`
- [ ] `useStatus.ts`

---

### Hooks Auditoria (src/hooks/audit/)
**Total:** 6 | **Sem teste:** 6

- [ ] `useAccessHistory.ts`
- [ ] `useAuditDashboard.ts`
- [ ] `useAuditLogs.ts`
- [ ] `useComplianceChecks.ts`
- [ ] `useComplianceRules.ts`
- [ ] `useDataRetention.ts`

---

### Hooks Analytics (src/hooks/analytics/)
**Total:** 9 | **Sem teste:** 9

- [ ] `useChurnPrediction.ts`
- [ ] `useExecutiveDashboard.ts`
- [ ] `useFeatureStore.ts`
- [ ] `useFraudDetection.ts`
- [ ] `useForecast.ts`
- [ ] `useLeadScoring.ts`
- [ ] `useModelManagement.ts`
- [ ] `useMonitoring.ts`

---

### Hooks Equipamentos (src/hooks/equipment/)
**Total:** 5 | **Sem teste:** 5

- [ ] `useComodato.ts`
- [ ] `useEquipment.ts`
- [ ] `useInstallation.ts`
- [ ] `useMaintenance.ts`

---

### Hooks Campo (src/hooks/campo/)
**Total:** 8 | **Sem teste:** 8

- [ ] `useCampo.ts`
- [ ] `useChecklist.ts`
- [ ] `useEstoque.ts`
- [ ] `useGuardian.ts`
- [ ] `useOrdemServico.ts`
- [ ] `useRoteirizacao.ts`
- [ ] `useVisita.ts`

---

### Hooks Diaristas (src/hooks/diarists/)
**Total:** 9 | **Sem teste:** 9

- [ ] `useAssignments.ts`
- [ ] `useDiaristAI.ts`
- [ ] `useDiarists.ts`
- [ ] `useEvaluations.ts`
- [ ] `useFiscal.ts`
- [ ] `useNotifications.ts`
- [ ] `usePayments.ts`
- [ ] `useSchedules.ts`
- [ ] `useStatistics.ts`

---

### Hooks Clientes (src/hooks/clients/)
**Total:** 7 | **Sem teste:** 7

- [ ] `useClientAI.ts`
- [ ] `useClients.ts`
- [ ] `useCondominiums.ts`
- [ ] `useContracts.ts`
- [ ] `useIntegrations.ts`
- [ ] `useUnits.ts`

---

### Hooks Kits de Documentos (src/hooks/document-kits/)
**Total:** 5 | **Sem teste:** 5

- [ ] `useDocumentKitAI.ts`
- [ ] `useDocumentKitAssignments.ts`
- [ ] `useDocumentKitItems.ts`
- [ ] `useDocumentKitOperational.ts`
- [ ] `useDocumentKits.ts`

---

### Hooks Reembolso (src/hooks/reimbursement/)
**Total:** 6 | **Sem teste:** 6

- [ ] `useReimbursementApprovals.ts`
- [ ] `useReimbursementAttachments.ts`
- [ ] `useReimbursementItems.ts`
- [ ] `useReimbursementPayments.ts`
- [ ] `useReimbursementRequests.ts`

---

### Hooks Mobile (src/hooks/mobile/)
**Total:** 5 | **Sem teste:** 5

- [ ] `useDevice.ts`
- [ ] `useMobile.ts`
- [ ] `usePushNotifications.ts`
- [ ] `useSync.ts`

---

### Hooks Contratos (src/hooks/contracts/)
**Total:** 6 | **Sem teste:** 6

- [ ] `useContractAddendums.ts`
- [ ] `useContractItems.ts`
- [ ] `useContractSLA.ts`
- [ ] `useContractTemplates.ts`
- [ ] `useContracts.ts`

---

### Hooks Integrações (src/hooks/integrations/)
**Total:** 12 | **Sem teste:** 12

- [ ] `useAPIEndpoints.ts`
- [ ] `useAPIKeys.ts`
- [ ] `useConnectors.ts`
- [ ] `useIntegrationAccounts.ts`
- [ ] `useIntegrationDashboard.ts`
- [ ] `useIntegrationLogs.ts`
- [ ] `useSolides.ts`
- [ ] `useSyncQueue.ts`
- [ ] `useSyncRuns.ts`
- [ ] `useWebhooks.ts`

---

### Hooks CRM (src/hooks/crm/)
**Total:** 2 | **Sem teste:** 2

- [ ] `useCRM.ts`

---

### Hooks Governo (src/hooks/government/)
**Total:** 9 | **Sem teste:** 9

- [ ] `useESocial.ts`
- [ ] `useFGTSSimples.ts`
- [ ] `useGovBrECAC.ts`
- [ ] `useNFSe.ts`
- [ ] `useReceitaFederal.ts`
- [ ] `useSEFAZ.ts`
- [ ] `useSPED.ts`
- [ ] `useSyncMonitoring.ts`

---

### Hooks Configurações (src/hooks/useConfig/)
**Total:** 7 | **Sem teste:** 7

- [ ] `useDashboards.ts`
- [ ] `useFeatureFlags.ts`
- [ ] `useNotificationTemplates.ts`
- [ ] `useSystemConfig.ts`
- [ ] `useTenantSettings.ts`
- [ ] `useTenants.ts`

---

### Hooks Notificações (src/hooks/notifications/)
**Total:** 7 | **Sem teste:** 7

- [ ] `useIntelligentNotifications.ts`
- [ ] `useNotificationWebSocket.ts`
- [ ] `useNotifications.ts`
- [ ] `usePreferences.ts`
- [ ] `usePush.ts`
- [ ] `useTemplates.ts`

---

### Hooks Busca (src/hooks/search/)
**Total:** 2 | **Sem teste:** 2

- [ ] `useGlobalSearch.ts`

---

### Hooks AI (src/hooks/ai/)
**Total:** 2 | **Sem teste:** 2

- [ ] `useBartolo.ts`

---

### Hooks Workflows (src/hooks/workflows/)
**Total:** 3 | **Sem teste:** 3

- [ ] `useExecutions.ts`
- [ ] `useWorkflows.ts`

---

### Hooks Licitações (src/hooks/bidding/)
**Total:** 6 | **Sem teste:** 6

- [ ] `useCertificates.ts`
- [ ] `useContracts.ts`
- [ ] `useDocuments.ts`
- [ ] `useProposals.ts`
- [ ] `useTenders.ts`

---

### Hooks Recrutamento (src/hooks/recruitment/)
**Total:** 5 | **Sem teste:** 5

- [ ] `useApplications.ts`
- [ ] `useCandidates.ts`
- [ ] `useInterviews.ts`
- [ ] `useJobPositions.ts`

---

### Hooks Scheduler (src/hooks/scheduler/)
**Total:** 6 | **Sem teste:** 6

- [ ] `useExecutions.ts`
- [ ] `useLocks.ts`
- [ ] `useOperations.ts`
- [ ] `useQueue.ts`
- [ ] `useTasks.ts`
- [ ] `useWorkers.ts`

---

### Hooks RH (src/hooks/hr/)
**Total:** 7 | **Sem teste:** 7

- [ ] `useAnalyticsDashboard.ts`
- [ ] `useEmployeePortal.ts`
- [ ] `useMobileTimeClock.ts`
- [ ] `usePayrollIntegration.ts`
- [ ] `useREPIntegration.ts`
- [ ] `useTimeTracking.ts`

---

### Hooks Fase 5 (src/hooks/fase5/)
**Total:** 5 | **Sem teste:** 5

- [ ] `useCCT.ts`
- [ ] `useEmailIntelligence.ts`
- [ ] `useQuality.ts`
- [ ] `useStatus.ts`

---

## 🛠️ Utilitários SEM Teste

### src/utils/ (2 arquivos)
**Com teste:** 2 | **Sem teste:** 0

#### ✅ COM Teste:
- [x] `export.test.ts`
- [x] `file-helpers.test.ts`

---

### src/lib/ (61 arquivos)
**Com teste:** 2 | **Sem teste:** 59

#### ✅ COM Teste:
- [x] `formatters.test.ts`
- [x] `utils.test.ts`

#### ❌ SEM Teste - Core:
- [ ] `api.ts`
- [ ] `api-client.ts`
- [ ] `axios-instance.ts`
- [ ] `utils.ts`
- [ ] `websocket.ts`

#### ❌ SEM Teste - API Client (src/lib/api/):
- [ ] `client.ts`
- [ ] `hooks/services/useSLA.ts`
- [ ] `hooks/services/useServiceAI.ts`
- [ ] `hooks/services/useServiceCatalog.ts`
- [ ] `hooks/services/useServiceExecution.ts`
- [ ] `hooks/services/useServiceOrder.ts`
- [ ] `hooks/services/useServiceReport.ts`
- [ ] `security-lgpd/hooks/useAudit.ts`
- [ ] `security-lgpd/hooks/useConsent.ts`
- [ ] `security-lgpd/hooks/useEncryption.ts`
- [ ] `security-lgpd/hooks/useErasure.ts`
- [ ] `security-lgpd/hooks/useMasking.ts`
- [ ] `security-lgpd/hooks/usePIA.ts`
- [ ] `security-lgpd/services/auditService.ts`
- [ ] `security-lgpd/services/consentService.ts`
- [ ] `security-lgpd/services/encryptionService.ts`
- [ ] `security-lgpd/services/erasureService.ts`
- [ ] `security-lgpd/services/maskingService.ts`
- [ ] `security-lgpd/services/piaService.ts`
- [ ] `security-lgpd/services/statusService.ts`
- [ ] `services/integrations/apiEndpointService.ts`
- [ ] `services/integrations/apiKeyService.ts`
- [ ] `services/integrations/bankingService.ts`
- [ ] `services/integrations/connectorService.ts`
- [ ] `services/integrations/emailService.ts`
- [ ] `services/integrations/integrationAccountService.ts`
- [ ] `services/integrations/integrationLogService.ts`
- [ ] `services/integrations/solidesService.ts`
- [ ] `services/integrations/syncQueueService.ts`
- [ ] `services/integrations/syncRunService.ts`
- [ ] `services/integrations/webhookService.ts`
- [ ] `services/integrations/whatsappService.ts`
- [ ] `services/services/serviceAIService.ts`
- [ ] `services/services/serviceCatalogService.ts`
- [ ] `services/services/serviceExecutionService.ts`
- [ ] `services/services/serviceOrderService.ts`
- [ ] `services/services/serviceReportService.ts`
- [ ] `services/services/slaService.ts`

#### ❌ SEM Teste - Services (src/lib/services/):
- [ ] `announcements.ts`
- [ ] `diarist-fiscal.ts`
- [ ] `diarists.ts`
- [ ] `document-kits.ts`
- [ ] `health-occupational/epi.ts`
- [ ] `health-occupational/pcmso.ts`
- [ ] `health-occupational/ppra.ts`
- [ ] `notifications.ts`
- [ ] `scale-templates.ts`
- [ ] `substitutions.ts`
- [ ] `time-bank.ts`
- [ ] `types.ts`

---

## 🎯 Priorização de Testes

### P0 - Críticos (20 itens) - Cobertura Essencial
Devem ser testados primeiro devido à alta reutilização e criticidade.

#### Componentes UI (10):
| # | Componente | Justificativa |
|---|------------|---------------|
| 1 | `button.tsx` | Base de 90% das interações |
| 2 | `input.tsx` | Formulários em toda aplicação |
| 3 | `dialog.tsx` | Modais críticos de confirmação |
| 4 | `table.tsx` | Listagem de dados principal |
| 5 | `select.tsx` | Inputs de seleção ubíquos |
| 6 | `badge.tsx` | Status indicators |
| 7 | `card.tsx` | Containers de conteúdo |
| 8 | `dropdown-menu.tsx` | Ações contextuais |
| 9 | `alert-dialog.tsx` | Confirmações destrutivas |
| 10 | `permission-guard.tsx` | Segurança de acesso |

#### Hooks Core (10):
| # | Hook | Justificativa |
|---|------|---------------|
| 1 | `useAuth.ts` | Autenticação de usuários |
| 2 | `usePermission.ts` | Controle de acesso RBAC |
| 3 | `useFetch.ts` | Todas as requisições HTTP |
| 4 | `useForm.ts` | Todos os formulários |
| 5 | `useLocalStorage.ts` | Persistência local |
| 6 | `useNotifications.ts` | Sistema de notificações |
| 7 | `useDebounce.ts` | Performance de inputs |
| 8 | `usePagination.ts` | Listagens paginadas |
| 9 | `useAutoSave.ts` | Recuperação de dados |
| 10 | `useKeyboardShortcuts.ts` | Acessibilidade |

---

### P1 - Importantes (50 itens) - Módulos Principais

#### Componentes por Módulo (25):
| Módulo | Componentes Prioritários |
|--------|--------------------------|
| **Operacional** | `notification-center`, `shift-calendar`, `occurrence-form-modal` |
| **Financeiro** | `payable-form-modal`, `receivable-form-modal`, `nfe-form-modal` |
| **Licitações** | `TenderFormModal`, `ProposalFormModal`, `ContractFormModal` |
| **CRM** | `cliente-form-modal`, `oportunidade-form-modal` |
| **GED** | `DocumentApprovalDialog`, `FolderTree` |
| **Segurança** | `consent-form-modal`, `audit-detail-modal` |
| **AI** | `BartoloChatWidget`, `ActionConfirmationModal` |
| **Root** | `CommandPalette`, `GlobalSearch`, `NotificationBell` |

#### Hooks por Domínio (25):
| Domínio | Hooks Prioritários |
|---------|-------------------|
| **Operacional** | `useEmployees`, `useScales`, `useShifts` |
| **Financeiro** | `useFinancial`, `useSuppliers` |
| **Clientes** | `useClients`, `useCondominiums` |
| **LGPD** | `useConsent`, `useAudit` |
| **Analytics** | `useExecutiveDashboard`, `useAnalyticsDashboard` |
| **Notificações** | `useNotificationWebSocket`, `usePush` |
| **Mobile** | `useDevice`, `useSync` |
| **Integrações** | `useWebhooks`, `useAPIKeys` |
| **Recrutamento** | `useCandidates`, `useJobPositions` |
| **Diaristas** | `useDiarists`, `useAssignments` |

---

### P2 - Padrão (Restante) - Cobertura Completa

Todos os demais componentes, hooks e utilitários não listados acima.

**Estimativa:**
- Componentes: ~100
- Hooks: ~150
- Utilitários: ~55

---

## 📋 Testes Existentes - Resumo

### Estrutura de Testes Atual:

```
src/
├── api/__tests__/                    (5 testes)
│   ├── api-client.test.ts
│   ├── auth-api.test.ts
│   ├── clientes-api.test.ts
│   ├── crm-api.test.ts
│
├── app/modulos/licitacoes/__tests__/ (7 testes)
│   ├── dashboard.test.tsx
│   ├── certidoes/certidoes-documentos.test.tsx
│   ├── contratos/contratos.test.tsx
│   ├── editais/editais-detail.test.tsx
│   ├── editais/editais-list.test.tsx
│   └── propostas/propostas.test.tsx
│
├── components/__tests__/             (1 teste)
│   └── smoke.test.tsx
│
├── components/ui/__tests__/          (17 testes)
│   ├── alert.test.tsx
│   ├── badge.test.tsx
│   ├── button.test.tsx
│   ├── card.test.tsx
│   ├── dialog.test.tsx
│   ├── input.test.tsx
│   ├── label.test.tsx
│   ├── loading-state.test.tsx
│   ├── modal.test.tsx
│   ├── select.test.tsx
│   ├── separator.test.tsx
│   ├── switch.test.tsx
│   ├── table.test.tsx
│   ├── tabs.test.tsx
│   ├── textarea.test.tsx
│   ├── toast.test.tsx
│   └── tooltip.test.tsx
│
├── hooks/__tests__/                  (7 testes)
│   ├── useAuth.test.ts
│   ├── useDebounce.test.ts
│   ├── useFetch.test.ts
│   ├── useForm.test.ts
│   ├── useLocalStorage.test.ts
│   ├── usePagination.test.ts
│   └── usePermission.test.ts
│
├── hooks/operacional/__tests__/      (2 testes)
│   ├── useOccurrences.test.tsx
│   └── usePosts.test.tsx
│
├── lib/__tests__/                    (2 testes)
│   ├── formatters.test.ts
│   └── utils.test.ts
│
└── utils/__tests__/                  (2 testes)
    ├── export.test.ts
    └── file-helpers.test.ts
```

---

## 📈 Recomendações

### 1. Estratégia de Cobertura
```
Fase 1 (Sprint 1-2):  P0 - 20 itens    → Meta: 15% cobertura
Fase 2 (Sprint 3-5):  P1 - 50 itens    → Meta: 30% cobertura
Fase 3 (Sprint 6-10): P2 - 333 itens   → Meta: 70% cobertura
```

### 2. Ferramentas Recomendadas
- **Jest** - Framework de teste (já em uso)
- **React Testing Library** - Testes de componentes (já em uso)
- **MSW (Mock Service Worker)** - Mock de APIs
- **Cypress Component Testing** - Testes E2E de componentes

### 3. Métricas de Qualidade
- Cobertura mínima: 70% para código novo
- Testes de regressão para bugs críticos
- Snapshot tests para componentes UI estáticos

### 4. Padrões de Teste
```typescript
// Exemplo de estrutura recomendada
describe('Componente', () => {
  describe('Renderização', () => { ... });
  describe('Interações', () => { ... });
  describe('Estados', () => { ... });
  describe('Acessibilidade', () => { ... });
});
```

---

## 🔄 Próximos Passos

1. **Semana 1:** Implementar testes P0 - Componentes UI base
2. **Semana 2:** Implementar testes P0 - Hooks core
3. **Semana 3-4:** Revisar e expandir testes P1
4. **Semana 5+:** Estabelecer ritmo contínuo de testes P2

---

*Relatório gerado automaticamente em 2026-02-05*
