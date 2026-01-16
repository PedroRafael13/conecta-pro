# GAPS - Frontend vs Backend - Conecta PRO

**Data:** 2026-01-16
**Objetivo:** Frontend deve espelhar 100% das funcionalidades do backend

---

## RESUMO EXECUTIVO

| Categoria | Backend Controllers | Frontend Pages | Cobertura | GAP |
|-----------|-------------------|----------------|-----------|-----|
| AI/ML | 17 controllers | 6 pages | 35% | 11 faltando |
| Financial | 16 controllers | 12 pages | 75% | 4 faltando |
| GED | 6 controllers | 1 page | 17% | 5 faltando |
| HR | 22 controllers | 11 pages | 50% | 11 faltando |
| Notifications | 5 controllers | 1 page | 20% | 4 faltando |
| Security/LGPD | 7 controllers | 1 page | 14% | 6 faltando |
| Recruitment | 4 controllers | 1 page | 25% | 3 faltando |
| Campo | 13 controllers | 8 pages | 62% | 5 faltando |
| Bidding | 5 controllers | 4 pages | 80% | 1 faltando |
| Operations | 8 controllers | 7 pages | 88% | 1 faltando |
| Analytics | 2 controllers | 2 pages | 100% | 0 faltando |
| Config | 1 controller | 1 page | 100% | 0 faltando |
| Mobile | 1 controller | 0 pages | 0% | 1 faltando |
| Monitoring | 2 controllers | 1 page | 50% | 1 faltando |
| Scheduler | 1 controller | 1 page | 100% | 0 faltando |

**TOTAL: 53 páginas/funcionalidades faltando**

---

## DETALHAMENTO POR MÓDULO

### 1. MÓDULO AI (Inteligência Artificial) - 11 FALTANDO

**Existente no Frontend:**
- [x] AIHubPage.tsx - Hub central de IA
- [x] AIAnalyticsPage.tsx - Analytics IA
- [x] AIDocumentAnalysisPage.tsx - Análise de documentos
- [x] AIFraudDetectionPage.tsx - Detecção de fraude
- [x] AIPredictionsPage.tsx - Previsões
- [x] AISentimentPage.tsx - Análise de sentimento

**FALTANDO CRIAR:**

| # | Página | Backend Controller | Funcionalidades |
|---|--------|-------------------|-----------------|
| 1 | **BartoloPage.tsx** | bartolo_controller.py | Assistente IA conversacional, análise comportamental |
| 2 | **ContractAnalysisPage.tsx** | contract_controller.py | Análise de contratos com IA, extração de cláusulas |
| 3 | **ChatPage.tsx** | chat_controller.py | Chat inteligente, histórico de conversas |
| 4 | **DataQualityPage.tsx** | data_quality_controller.py | Qualidade de dados, validações, limpeza |
| 5 | **EmailAssistantPage.tsx** | email_controller.py | Assistente de email, respostas automáticas |
| 6 | **InventoryForecastPage.tsx** | forecast_controller.py | Previsão de estoque, demanda |
| 7 | **KnowledgeBasePage.tsx** | kb_controller.py | Base de conhecimento, FAQ inteligente |
| 8 | **MeetingAssistantPage.tsx** | meeting_assistant_controller.py | Resumos de reunião, atas automáticas |
| 9 | **OCRPage.tsx** | ocr_controller.py | OCR de documentos, extração de dados |
| 10 | **VoiceRecognitionPage.tsx** | voice_controller.py | Reconhecimento de voz, transcrição |
| 11 | **WorkflowOptimizerPage.tsx** | workflow_controller.py | Otimização de processos com IA |

---

### 2. MÓDULO FINANCIAL - 4 FALTANDO

**Existente no Frontend:**
- [x] FinancialDashboardPage.tsx
- [x] CashflowPage.tsx
- [x] ReceivablesPage.tsx
- [x] PayablesPage.tsx
- [x] BankingPage.tsx
- [x] BankReconciliationPage.tsx
- [x] AccountingPage.tsx
- [x] FiscalPage.tsx
- [x] InventoryPage.tsx
- [x] ProcurementPage.tsx
- [x] SuppliersPage.tsx
- [x] BillingRulesPage.tsx

**FALTANDO CRIAR:**

| # | Página | Backend Controller | Funcionalidades |
|---|--------|-------------------|-----------------|
| 1 | **BIDashboardPage.tsx** | bi_controller.py | BI completo, widgets, KPIs configuráveis |
| 2 | **CostingPage.tsx** | costing_controller.py | Custeio ABC, alocação de custos |
| 3 | **CustomersPage.tsx** | customer_controller.py | Clientes financeiro, crédito, histórico |
| 4 | **ReceivableCategoriesPage.tsx** | receivable_category_controller.py | Categorias de recebíveis |

---

### 3. MÓDULO GED - 5 FALTANDO

**Existente no Frontend:**
- [x] GEDPage.tsx - Página principal (básica)

**FALTANDO CRIAR:**

| # | Página | Backend Controller | Funcionalidades |
|---|--------|-------------------|-----------------|
| 1 | **FoldersPage.tsx** | folder_controller.py | Gestão de pastas, hierarquia, permissões |
| 2 | **DocumentVersionsPage.tsx** | document_version_controller.py | Versionamento, histórico, comparação |
| 3 | **DocumentSignaturesPage.tsx** | document_signature_controller.py | Assinaturas digitais, validação |
| 4 | **DocumentSharePage.tsx** | document_share_controller.py | Compartilhamento, permissões, links |
| 5 | **DocumentTagsPage.tsx** | document_tag_controller.py | Tags, categorização, busca |

**OU expandir GEDPage.tsx com abas para todas funcionalidades**

---

### 4. MÓDULO HR (Recursos Humanos) - 11 FALTANDO

**Existente no Frontend:**
- [x] HRDashboardPage.tsx
- [x] EmployeesPage.tsx
- [x] TimeTrackingPage.tsx
- [x] PayrollPage.tsx
- [x] RecruitmentPage.tsx
- [x] REPIntegrationPage.tsx
- [x] MobileTimeClockPage.tsx
- [x] EmployeePortalPage.tsx (hr-portal)
- [x] DocumentsPage.tsx (hr-portal)
- [x] PayslipsPage.tsx (hr-portal)
- [x] VacationPage.tsx (hr-portal)

**FALTANDO CRIAR:**

| # | Página | Backend Controller | Funcionalidades |
|---|--------|-------------------|-----------------|
| 1 | **HRAnalyticsDashboardPage.tsx** | dashboard_controller.py | Dashboard analytics RH |
| 2 | **HRKPIsPage.tsx** | kpi_controller.py | KPIs de RH, metas |
| 3 | **HRReportsPage.tsx** | report_controller.py | Relatórios de RH |
| 4 | **PayrollEventsPage.tsx** | payroll_event_controller.py | Eventos da folha |
| 5 | **PayrollExportPage.tsx** | payroll_export_controller.py | Exportação folha |
| 6 | **PayrollPeriodsPage.tsx** | payroll_period_controller.py | Períodos de folha |
| 7 | **GeofencePage.tsx** | geofence_controller.py | Cercas geográficas |
| 8 | **OfflineSyncPage.tsx** | offline_controller.py | Sincronização offline |
| 9 | **TimeJustificationsPage.tsx** | justification_controller.py | Justificativas de ponto |
| 10 | **OvertimePage.tsx** | overtime_controller.py | Horas extras |
| 11 | **TimeSheetsPage.tsx** | time_sheet_controller.py | Folhas de ponto |

---

### 5. MÓDULO NOTIFICATIONS - 4 FALTANDO

**Existente no Frontend:**
- [x] NotificationsPage.tsx - Página básica

**FALTANDO CRIAR:**

| # | Página | Backend Controller | Funcionalidades |
|---|--------|-------------------|-----------------|
| 1 | **NotificationTemplatesPage.tsx** | notification_controller.py | Templates de notificação |
| 2 | **NotificationChannelsPage.tsx** | notification_controller.py | Canais (email, SMS, WhatsApp, push) |
| 3 | **PushNotificationsPage.tsx** | push_controller.py | Push notifications config |
| 4 | **AntiProcrastinationPage.tsx** | checklist_controller.py, escalation_controller.py | Sistema anti-procrastinação |

---

### 6. MÓDULO SECURITY/LGPD - 6 FALTANDO

**Existente no Frontend:**
- [x] LGPDPage.tsx (compliance/) - Página básica

**FALTANDO CRIAR:**

| # | Página | Backend Controller | Funcionalidades |
|---|--------|-------------------|-----------------|
| 1 | **AuditLogsPage.tsx** | audit_controller.py | Logs de auditoria, eventos |
| 2 | **ConsentManagementPage.tsx** | consent_controller.py | Gestão de consentimentos LGPD |
| 3 | **DataEncryptionPage.tsx** | encryption_controller.py | Criptografia, chaves |
| 4 | **DataMaskingPage.tsx** | masking_controller.py | Mascaramento de dados |
| 5 | **DataErasurePage.tsx** | erasure_controller.py | Exclusão de dados (direito ao esquecimento) |
| 6 | **PIAPage.tsx** | pia_controller.py | Privacy Impact Assessment |

---

### 7. MÓDULO RECRUITMENT - 3 FALTANDO

**Existente no Frontend:**
- [x] RecruitmentPage.tsx (dentro de hr/)

**FALTANDO CRIAR:**

| # | Página | Backend Controller | Funcionalidades |
|---|--------|-------------------|-----------------|
| 1 | **CandidatesPage.tsx** | candidate_controller.py | Gestão de candidatos, perfis |
| 2 | **JobPositionsPage.tsx** | job_position_controller.py | Vagas abertas, requisitos |
| 3 | **InterviewsPage.tsx** | interview_controller.py | Agendamento de entrevistas |
| 4 | **ApplicationsPage.tsx** | application_controller.py | Candidaturas, status |

---

### 8. MÓDULO CAMPO - 5 FALTANDO

**Existente no Frontend:**
- [x] CampoDashboardPage.tsx
- [x] ServiceOrdersPage.tsx
- [x] OccurrencesPage.tsx
- [x] VisitsPage.tsx
- [x] AccessLogPage.tsx
- [x] EquipmentStatusPage.tsx
- [x] ChecklistPage.tsx
- [x] RoutesPage.tsx

**FALTANDO CRIAR:**

| # | Página | Backend Controller | Funcionalidades |
|---|--------|-------------------|-----------------|
| 1 | **FieldInventoryPage.tsx** | estoque_controller.py | Estoque em campo (já em extras/) |
| 2 | **GuardianSyncPage.tsx** | guardian_sync_controller.py | Sincronização com sistemas de vigilância |
| 3 | **SecurityAuditPage.tsx** | security_audit_controller.py | Auditoria de segurança |
| 4 | **SSHGatewayPage.tsx** | ssh_gateway_controller.py | Gateway SSH para equipamentos |
| 5 | **FieldMonitoringPage.tsx** | monitoring_controller.py | Monitoramento de campo específico |

---

### 9. MÓDULO BIDDING - 1 FALTANDO

**Existente no Frontend:**
- [x] BiddingDashboardPage.tsx
- [x] BiddingsPage.tsx (editais)
- [x] BidProposalsPage.tsx
- [x] BidDocumentsPage.tsx

**FALTANDO CRIAR:**

| # | Página | Backend Controller | Funcionalidades |
|---|--------|-------------------|-----------------|
| 1 | **BidContractsPage.tsx** | contract_controller.py | Contratos de licitação |
| 2 | **BidCertificatesPage.tsx** | certificate_controller.py | Certificados e qualificações |

---

### 10. MÓDULO OPERATIONS - 1 FALTANDO

**Existente no Frontend:**
- [x] ShiftsPage.tsx
- [x] AllocationsPage.tsx
- [x] SubstitutionsPage.tsx
- [x] TimeBankPage.tsx
- [x] PostsPage.tsx
- [x] ScalesPage.tsx
- [x] DailyWorkersPage.tsx

**FALTANDO CRIAR:**

| # | Página | Backend Controller | Funcionalidades |
|---|--------|-------------------|-----------------|
| 1 | **OperationsDashboardPage.tsx** | dashboard_controller.py | Dashboard operacional |

---

### 11. MÓDULO MOBILE - 1 FALTANDO

**Existente no Frontend:**
- [ ] Nenhum

**FALTANDO CRIAR:**

| # | Página | Backend Controller | Funcionalidades |
|---|--------|-------------------|-----------------|
| 1 | **MobileConfigPage.tsx** | mobile_controller.py | Configurações do app mobile |

---

### 12. MÓDULO MONITORING - 1 FALTANDO

**Existente no Frontend:**
- [x] MonitoringPage.tsx (em extras/)

**FALTANDO CRIAR:**

| # | Página | Backend Controller | Funcionalidades |
|---|--------|-------------------|-----------------|
| 1 | **RealtimeMonitoringPage.tsx** | realtime_controller.py | Monitoramento em tempo real |

---

### 13. MÓDULOS COM COBERTURA COMPLETA (OK)

- [x] **Analytics** - AnalyticsPage.tsx cobre todos endpoints
- [x] **Config** - SettingsPage.tsx cobre configurações
- [x] **Scheduler** - SchedulerPage.tsx em extras/
- [x] **Clients** - ClientsPage.tsx + ClientDetailPage.tsx
- [x] **CRM** - Todas as 5 páginas existentes
- [x] **Services** - ServicesPage.tsx
- [x] **Equipment** - Todas as 4 páginas existentes
- [x] **Integrations** - Todas as 4 páginas existentes

---

## LISTA CONSOLIDADA DE PÁGINAS A CRIAR

### PRIORIDADE CRÍTICA (Core Business)

1. **BartoloPage.tsx** - Assistente IA principal
2. **BIDashboardPage.tsx** - BI financeiro
3. **CostingPage.tsx** - Custeio
4. **FoldersPage.tsx** - Pastas GED
5. **DocumentVersionsPage.tsx** - Versionamento
6. **DocumentSignaturesPage.tsx** - Assinaturas digitais
7. **AuditLogsPage.tsx** - Auditoria LGPD
8. **ConsentManagementPage.tsx** - Consentimentos LGPD

### PRIORIDADE ALTA (Operacional)

9. **CandidatesPage.tsx** - Candidatos
10. **JobPositionsPage.tsx** - Vagas
11. **InterviewsPage.tsx** - Entrevistas
12. **HRAnalyticsDashboardPage.tsx** - Analytics RH
13. **PayrollEventsPage.tsx** - Eventos folha
14. **TimeJustificationsPage.tsx** - Justificativas
15. **OvertimePage.tsx** - Horas extras
16. **NotificationTemplatesPage.tsx** - Templates
17. **NotificationChannelsPage.tsx** - Canais

### PRIORIDADE MÉDIA (Compliance)

18. **DataEncryptionPage.tsx** - Criptografia
19. **DataMaskingPage.tsx** - Mascaramento
20. **DataErasurePage.tsx** - Exclusão dados
21. **PIAPage.tsx** - Privacy Impact
22. **GuardianSyncPage.tsx** - Sync vigilância
23. **SecurityAuditPage.tsx** - Auditoria segurança

### PRIORIDADE NORMAL (Extras)

24. **ChatPage.tsx** - Chat IA
25. **EmailAssistantPage.tsx** - Assistente email
26. **KnowledgeBasePage.tsx** - Base conhecimento
27. **MeetingAssistantPage.tsx** - Reuniões
28. **OCRPage.tsx** - OCR
29. **VoiceRecognitionPage.tsx** - Voz
30. **WorkflowOptimizerPage.tsx** - Otimização
31. **ContractAnalysisPage.tsx** - Análise contratos
32. **DataQualityPage.tsx** - Qualidade dados
33. **InventoryForecastPage.tsx** - Previsão estoque

### COMPLEMENTARES

34. **DocumentSharePage.tsx**
35. **DocumentTagsPage.tsx**
36. **CustomersPage.tsx**
37. **ReceivableCategoriesPage.tsx**
38. **HRKPIsPage.tsx**
39. **HRReportsPage.tsx**
40. **PayrollExportPage.tsx**
41. **PayrollPeriodsPage.tsx**
42. **GeofencePage.tsx**
43. **OfflineSyncPage.tsx**
44. **TimeSheetsPage.tsx**
45. **PushNotificationsPage.tsx**
46. **AntiProcrastinationPage.tsx**
47. **ApplicationsPage.tsx**
48. **SSHGatewayPage.tsx**
49. **FieldMonitoringPage.tsx**
50. **BidContractsPage.tsx**
51. **BidCertificatesPage.tsx**
52. **OperationsDashboardPage.tsx**
53. **MobileConfigPage.tsx**
54. **RealtimeMonitoringPage.tsx**

---

## ESTATÍSTICAS FINAIS

| Métrica | Valor |
|---------|-------|
| **Backend Controllers** | ~147 |
| **Frontend Pages Existentes** | 88 |
| **Frontend Pages Faltando** | 54 |
| **Cobertura Atual** | 62% |
| **Meta** | 100% |

---

## RECOMENDAÇÃO

**Estratégia sugerida:**

1. **Sprint 1 (Crítico):** Páginas 1-8 (Core Business)
2. **Sprint 2 (Operacional):** Páginas 9-17 (RH e Recrutamento)
3. **Sprint 3 (Compliance):** Páginas 18-23 (LGPD e Segurança)
4. **Sprint 4 (IA):** Páginas 24-33 (Recursos de IA)
5. **Sprint 5 (Finalização):** Páginas 34-54 (Complementares)

---

*Gerado em: 2026-01-16*
*Por: Claude Opus 4.5*
