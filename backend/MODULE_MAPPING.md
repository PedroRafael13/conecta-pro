# Mapeamento de Modulos — Reorganizacao Backend

> Conecta PRO — 2026-03-11
> 35 modulos legados → 9 modulos agregadores

## Grafo de Dependencias

```
COMERCIAL ──┬── crm (leads, oportunidades, propostas, contratos, comissoes)
            ├── clients (clientes, condominios, unidades)
            ├── bidding (licitacoes, editais, certidoes)
            └── services (catalogo de servicos, OS, SLA)

OPERACOES ──┬── operacional (postos, escalas, turnos, alocacoes, banco de horas)
            │   ├── .ai (otimizadores, preditivos)
            │   ├── .communication (comunicados, alertas)
            │   ├── .diaristas (gestao de diaristas)
            │   ├── .disciplinary (medidas administrativas)
            │   ├── .inspection_rounds (rondas)
            │   ├── .occurrences (ocorrencias)
            │   ├── .reports (relatorios operacionais)
            │   ├── .vacations (ferias)
            │   └── .websockets (tempo real)
            └── campo (ordens de servico, visitas, checklists)

PESSOAS ────┬── recruitment (vagas, candidatos, entrevistas)
            ├── retention (onboarding, perfil, clima, turnover)
            ├── reimbursement (reembolso de despesas)
            └── ged (documentos, pastas, versoes, assinaturas)

FINANCEIRO ─┬── financial (contabilidade, contas a pagar/receber, fluxo de caixa)
            │   ├── .bi_dashboard (KPIs, widgets)
            │   └── .costing (custeio ABC)
            └── (todos os 16 routers vem do modulo financial)

FISCAL ─────┬── empresas (multi-CNPJ, migrador, obrigacoes, Dominio)
CONTABIL    ├── fiscal (NFS-e multi-empresa)
            └── government_integrations (Receita Federal, eSocial, SEFAZ)

INTELIGENCIA┬── ai.bartolo (assistente IA)
            ├── analytics (dashboard executivo, analytics)
            ├── monitoring (early warning system)
            └── reports (relatorios gerenciais)

GESTAO ─────┬── audit (auditoria, compliance)
            ├── automation.workflow (workflows)
            ├── config (configuracoes, tenants, feature flags)
            ├── integrations (API gateway, webhooks, banking, conectores)
            ├── mobile (API mobile)
            └── notifications (hub de notificacoes, push, compliance)

TECNICO ────┬── equipment_management (equipamentos, instalacoes, manutencao)
            └── document_kits (kits documentais)

CADASTROS ──── (reservado para consolidacao futura de dados mestres)
```

## Tabela de Routers por Agregador

| Agregador       | Router no Agregador                  | Modulo Legado         | Router Original           |
|-----------------|--------------------------------------|-----------------------|---------------------------|
| comercial       | crm_lead_router                      | crm                   | lead_router               |
| comercial       | crm_opportunity_router               | crm                   | opportunity_router        |
| comercial       | crm_proposal_router                  | crm                   | proposal_router           |
| comercial       | crm_contract_router                  | crm                   | contract_router           |
| comercial       | crm_commission_router                | crm                   | commission_router         |
| comercial       | crm_dashboard_router                 | crm                   | dashboard_router          |
| comercial       | client_router                        | clients               | router                    |
| comercial       | bidding_tender_router                | bidding               | tender_router             |
| comercial       | bidding_document_router              | bidding               | document_router           |
| comercial       | bidding_proposal_router              | bidding               | proposal_router           |
| comercial       | bidding_contract_router              | bidding               | contract_router           |
| comercial       | bidding_certificate_router           | bidding               | certificate_router        |
| comercial       | service_router                       | services              | router                    |
| operacoes       | post_router                          | operacional           | post_router               |
| operacoes       | scale_router                         | operacional           | scale_router              |
| operacoes       | scale_template_router                | operacional           | scale_template_router     |
| operacoes       | shift_router                         | operacional           | shift_router              |
| operacoes       | allocation_router                    | operacional           | allocation_router         |
| operacoes       | employee_router                      | operacional           | employee_router           |
| operacoes       | substitution_router                  | operacional           | substitution_router       |
| operacoes       | time_bank_router                     | operacional           | time_bank_router          |
| operacoes       | reports_router                       | operacional           | dashboard_router          |
| operacoes       | kpi_trends_router                    | operacional           | (KPI trends)              |
| operacoes       | occurrence_router                    | operacional.occurrences| occurrence_router         |
| operacoes       | diarist_router                       | operacional.diaristas | diarist_router            |
| operacoes       | diarist_fiscal_router                | operacional.diaristas | fiscal_router             |
| operacoes       | disciplinary_router                  | operacional.disciplinary| disciplinary_router      |
| operacoes       | inspection_round_router              | operacional.inspection_rounds| inspection_round_router|
| operacoes       | communication_router                 | operacional.communication| communication_router    |
| operacoes       | vacation_router                      | operacional.vacations | vacation_router           |
| operacoes       | operacional_ai_router                | operacional.ai        | ai_router                 |
| operacoes       | operacional_ws_router                | operacional.websockets| websocket_router          |
| operacoes       | ordem_servico_router                 | campo                 | ordem_servico_router      |
| operacoes       | visita_router                        | campo                 | visita_router             |
| operacoes       | checklist_router                     | campo                 | checklist_router          |
| pessoas         | recruitment_router                   | recruitment           | router                    |
| pessoas         | onboarding_router                    | retention             | onboarding_router         |
| pessoas         | profile_router                       | retention             | profile_router            |
| pessoas         | climate_router                       | retention             | climate_router            |
| pessoas         | turnover_router                      | retention             | turnover_router           |
| pessoas         | reimbursement_router                 | reimbursement         | reimbursement_router      |
| pessoas         | ged_folder_router                    | ged                   | folder_router             |
| pessoas         | ged_document_router                  | ged                   | document_router           |
| pessoas         | ged_version_router                   | ged                   | version_router            |
| pessoas         | ged_share_router                     | ged                   | share_router              |
| pessoas         | ged_tag_router                       | ged                   | tag_router                |
| pessoas         | ged_signature_router                 | ged                   | signature_router          |
| pessoas         | ged_stats_router                     | ged                   | stats_router              |
| financeiro      | accounting_router                    | financial             | accounting_router         |
| financeiro      | supplier_router                      | financial             | supplier_router           |
| financeiro      | payable_router                       | financial             | payable_router            |
| financeiro      | customer_router                      | financial             | customer_router           |
| financeiro      | receivable_category_router           | financial             | receivable_category_router|
| financeiro      | receivable_router                    | financial             | receivable_router         |
| financeiro      | billing_rule_router                  | financial             | billing_rule_router       |
| financeiro      | bank_account_router                  | financial             | bank_account_router       |
| financeiro      | bank_transaction_router              | financial             | bank_transaction_router   |
| financeiro      | bank_reconciliation_router           | financial             | bank_reconciliation_router|
| financeiro      | cashflow_router                      | financial             | cashflow_router           |
| financeiro      | purchase_router                      | financial             | purchase_router           |
| financeiro      | inventory_router                     | financial             | inventory_router          |
| financeiro      | fiscal_router                        | financial             | fiscal_router             |
| financeiro      | financial_ai_router                  | financial             | financial_ai_router       |
| financeiro      | relatorios_router                    | financial             | relatorios_router         |
| financeiro      | bi_dashboard_router                  | financial.bi_dashboard| router                    |
| fiscal_contabil | empresas_router                      | empresas              | empresa_router            |
| fiscal_contabil | migrador_router                      | empresas              | migrador_router           |
| fiscal_contabil | obrigacoes_router                    | empresas              | obligations_router        |
| fiscal_contabil | empresas_dashboard_router            | empresas              | dashboard_router          |
| fiscal_contabil | dominio_router                       | empresas              | dominio_router            |
| fiscal_contabil | bookkeeper_router                    | empresas              | bookkeeper_router         |
| fiscal_contabil | statements_router                    | empresas              | statements_router         |
| fiscal_contabil | nfse_multi_router                    | fiscal                | nfse_multi_router         |
| fiscal_contabil | government_integrations_router       | government_integrations| government_integrations_router|
| inteligencia    | bartolo_router                       | ai.bartolo            | bartolo_router            |
| inteligencia    | executive_dashboard_router           | analytics             | executive_dashboard_router|
| inteligencia    | analytics_router                     | analytics             | analytics_router          |
| inteligencia    | report_router                        | reports               | router                    |
| inteligencia    | monitoring_router                    | monitoring            | router                    |
| gestao          | config_router                        | config                | router                    |
| gestao          | audit_router                         | audit                 | router                    |
| gestao          | notification_router                  | notifications         | router                    |
| gestao          | notification_compliance_router       | notifications         | compliance_router         |
| gestao          | intelligent_notification_router      | notifications         | intelligent_router        |
| gestao          | push_notification_router             | notifications.push    | router                    |
| gestao          | mobile_router                        | mobile                | mobile_router             |
| gestao          | workflow_router                      | automation.workflow    | router                    |
| gestao          | integration_router                   | integrations          | integration_router        |
| gestao          | connector_router                     | integrations          | connector_router          |
| gestao          | solides_router                       | integrations          | solides_router            |
| gestao          | banking_router                       | integrations          | banking_router            |
| tecnico         | equipment_router                     | equipment_management  | equipment_router          |
| tecnico         | installation_router                  | equipment_management  | installation_router       |
| tecnico         | equipment_maintenance_router         | equipment_management  | maintenance_router        |
| tecnico         | comodato_router                      | equipment_management  | comodato_router           |
| tecnico         | document_kit_router                  | document_kits         | router                    |

## Modulos NAO cobertos pelos agregadores (DEV-ONLY)

Estes modulos sao registrados diretamente no `api/v1/__init__.py`:

| Modulo                | Motivo                                      |
|-----------------------|---------------------------------------------|
| hr                    | Sub-routers de RH (sem __init__.py)         |
| ai (sub-modules)      | AI feature_store, model_manager, etc.       |
| documents             | Document Intelligence                       |
| security_lgpd         | Seguranca e LGPD                            |
| health_occupational   | Saude Ocupacional (NRs)                     |
| fase5                 | DEPRECATED - AI Orchestration experimental  |
| campo (legacy)        | Access log, equipment status, SSH gateway   |
| scheduler             | Task scheduler                              |
| core                  | Core system module                          |

## Modulos Removidos

| Modulo   | Motivo                                | Data       |
|----------|---------------------------------------|------------|
| search   | Funcionalidade nao utilizada          | 2026-03-11 |
