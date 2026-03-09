"""
API v1 - Router principal.
"""

from fastapi import APIRouter

# Bartolo - Assistente Inteligente (Sessao 4)
from modules.ai.bartolo.controllers import bartolo_router

# ===================================================================
# MÓDULO EMPRESAS - Multi-CNPJ (Sprint 67)
# ===================================================================
from modules.empresas.controllers.empresa_controller import router as empresas_router

# ===================================================================
# MÓDULO AI - INTELIGÊNCIA ARTIFICIAL (Sprints 34-55)
# ===================================================================
# Análise de Contratos (Sprint 46)
from modules.ai.contract_analysis.controllers import router as ai_contract_router

# Qualidade de Dados (Sprint 48)
from modules.ai.data_quality.controllers import data_quality_router as ai_data_quality_router

# Assistente de Email (Sprint 54)
from modules.ai.email_assistant.controllers import router as ai_email_router

# Detecção de Fraude (Sprint 47)
from modules.ai.fraud_detection.controllers import router as ai_fraud_router

# Previsão de Inventário (Sprint 45)
from modules.ai.inventory_forecast.controllers import router as ai_forecast_router

# Base de Conhecimento (Sprint 53)
from modules.ai.knowledge_base.controllers import kb_router as ai_kb_router

# Assistente de Reuniões (Sprint 49)
from modules.ai.meeting_assistant.controllers import meeting_assistant_router as ai_meeting_router

# OCR - Leitura de Documentos (Sprint 39)
from modules.ai.ocr.controllers import ocr_router as ai_ocr_router

# Gerador de Relatórios (Sprint 44)
from modules.ai.report_generator.controllers import report_router as ai_report_router

# Análise de Sentimento (Sprint 43)
from modules.ai.sentiment_analysis.controllers import router as ai_sentiment_router

# Reconhecimento de Assinatura (Sprint 40)
from modules.ai.signature.controllers import signature_router as ai_signature_router

# Reconhecimento de Voz (Sprint 52)
from modules.ai.voice_recognition.controllers import voice_router as ai_voice_router

# Otimizador de Workflows (Sprint 55)
from modules.ai.workflow_optimizer.controllers import router as ai_workflow_router

# ===================================================================
# MÓDULO AUDIT - Auditoria e Compliance (Sprint 33)
# ===================================================================
from modules.audit.controllers import router as audit_router

# ===================================================================
# MÓDULO CLIENTS - Cadastro de Clientes/Condomínios (Sprint 30)
# ===================================================================
from modules.clients.controllers import router as client_router

# ===================================================================
# MÓDULO CONFIG - Configurações e Multi-tenant (Sprint 35)
# ===================================================================
from modules.config.controllers import router as config_router
from modules.crm.controllers import (
    commission_router,
    contract_router,
    dashboard_router,
    lead_router,
    opportunity_router,
    proposal_router,
)

# ===================================================================
# MÓDULO DOCUMENT_KITS - Kits Documentais
# ===================================================================
from modules.document_kits.controllers import router as document_kit_router

# ===================================================================
# MÓDULO DOCUMENTS - Document Intelligence (OCR/IA)
# ===================================================================
from modules.documents.controllers import router as documents_router

# ===================================================================
# MÓDULO EQUIPMENT_MANAGEMENT - Gestão de Equipamentos
# ===================================================================
from modules.equipment_management.controllers import (
    comodato_router,
    equipment_router,
    installation_router,
)
from modules.equipment_management.controllers import (
    maintenance_router as equipment_maintenance_router,
)

# ===================================================================
# MÓDULO FINANCIAL - Gestão Financeira Completa
# ===================================================================
from modules.financial.controllers import (
    # Contabilidade
    accounting_router,
    # Fluxo de Caixa / Bancos
    bank_account_router,
    bank_reconciliation_router,
    bank_transaction_router,
    billing_rule_router,
    cashflow_router,
    # Contas a Receber
    customer_router,
    # Fiscal
    fiscal_router,
    # Estoque
    inventory_router,
    payable_router,
    # Compras
    purchase_router,
    receivable_category_router,
    receivable_router,
    # Contas a Pagar
    supplier_router,
    # AI Command Center
    financial_ai_router,
)

# ===================================================================
# MÓDULO FACILITIES - REMOVIDO (Transferido para PLUS)
# ===================================================================
# ===================================================================
# MÓDULO GED - Gestão Eletrônica de Documentos
# ===================================================================
from modules.ged.controllers import (
    document_router,
    folder_router,
    share_router,
    signature_router,
    stats_router,
    tag_router,
    version_router,
)

# ===================================================================
# HR - RECURSOS HUMANOS
# ===================================================================
# Analytics Dashboard
from modules.hr.analytics_dashboard import router as hr_analytics_router

# Portal do Funcionário
from modules.hr.employee_portal.controllers import router as hr_portal_router
from modules.hr.mobile_time_clock import (
    checkin_router as mobile_checkin_router,
)

# Mobile Time Clock (Ponto Mobile)
from modules.hr.mobile_time_clock import (
    device_router as mobile_device_router,
)
from modules.hr.mobile_time_clock import (
    geofence_router as mobile_geofence_router,
)
from modules.hr.mobile_time_clock import (
    offline_router as mobile_offline_router,
)

# Integração com Folha de Pagamento
from modules.hr.payroll_integration import router as hr_payroll_router

# Integração REP (Registrador Eletrônico de Ponto)
from modules.hr.rep_integration.controllers import router as hr_rep_router

# Ponto Eletrônico / Time Tracking
from modules.hr.time_tracking.controllers import router as hr_time_tracking_router

# ===================================================================
# MÓDULO INTEGRATIONS - API Gateway / Integrações (Sprint 32)
# ===================================================================
from modules.integrations.controllers import router as integration_router

# Communication - Comunicados, Notificacoes, Alertas
from modules.operacional.communication import communication_router

# Férias e Afastamentos
from modules.operacional.vacations import vacation_router
from modules.operacional.controllers import (
    allocation_router,
    employee_router,
    kpi_trends_router,
    post_router,
    reports_router,
    scale_router,
    scale_template_router,
    shift_router,
    substitution_router,
    time_bank_router,
)
from modules.operacional.controllers import (
    dashboard_router as operacional_dashboard_router,
)
from modules.operacional.diaristas.controllers import (
    fiscal_router as diarist_fiscal_router,
)
from modules.operacional.diaristas.controllers import (
    notificacao_router as diarist_notificacao_router,
)

# ===================================================================
# MÓDULO DIARISTS - Gestão de Diaristas
# ===================================================================
from modules.operacional.diaristas.controllers import (
    router as diarist_router,
)

# Disciplinary - Medidas Administrativas
from modules.operacional.disciplinary import router as disciplinary_router

# Inspection Rounds - Rondas de Inspecao
from modules.operacional.inspection_rounds import inspection_round_router

# Occurrence router now comes from occurrences module
from modules.operacional.occurrences import occurrence_router

# ===================================================================
# RECRUITMENT - RECRUTAMENTO E SELEÇÃO
# ===================================================================
from modules.recruitment import router as recruitment_router

# ===================================================================
# MÓDULO OCCURRENCES - REMOVIDO (Transferido para PLUS)
# ===================================================================
# ===================================================================
# MÓDULO REPORTS - Relatórios Gerenciais (Sprint 34)
# ===================================================================
from modules.reports.controllers import router as report_router

# ===================================================================
# MÓDULO SERVICES - Gestão de Serviços (Sprint 31)
# ===================================================================
from modules.services.controllers import router as service_router

from .endpoints.auth import router as auth_router

router = APIRouter(prefix="/api/v1")

# ===================================================================
# HEALTH CHECK - Monitoramento
# ===================================================================
from core.controllers.health_controller import router as health_router  # noqa: E402

router.include_router(health_router)

# ===================================================================
# ROUTERS EXISTENTES
# ===================================================================
router.include_router(auth_router)

# ===================================================================
# CRM - GESTÃO COMERCIAL
# ===================================================================
router.include_router(lead_router, prefix="/crm", tags=["CRM - Leads"])
router.include_router(opportunity_router, prefix="/crm", tags=["CRM - Oportunidades"])
router.include_router(proposal_router, prefix="/crm", tags=["CRM - Propostas"])
router.include_router(commission_router, prefix="/crm", tags=["CRM - Comissões"])
router.include_router(dashboard_router, prefix="/crm", tags=["CRM - Dashboard"])
router.include_router(contract_router, prefix="/crm", tags=["CRM - Contratos"])

# ===================================================================
# OPERACIONAL - POSTOS, ESCALAS E GESTÃO DE PESSOAL
# ===================================================================
router.include_router(post_router, prefix="/operacional/postos", tags=["Operacional - Postos"])
router.include_router(scale_router, prefix="/operacional/escalas", tags=["Operacional - Escalas"])
router.include_router(
    scale_template_router, prefix="/operacional/scales/templates", tags=["Operacional - Templates de Escalas"]
)
router.include_router(shift_router, prefix="/operacional/turnos", tags=["Operacional - Turnos"])
router.include_router(allocation_router, prefix="/operacional/alocacoes", tags=["Operacional - Alocações"])
router.include_router(employee_router, prefix="/operacional", tags=["Operacional - Funcionarios"])
router.include_router(occurrence_router, prefix="/operacional", tags=["Operacional - Ocorrências"])
router.include_router(substitution_router, prefix="/operacional/substituicoes", tags=["Operacional - Substituições"])
router.include_router(time_bank_router, prefix="/operacional/banco-horas", tags=["Operacional - Banco de Horas"])
router.include_router(reports_router, prefix="/operacional", tags=["Operacional - Relatorios"])
router.include_router(operacional_dashboard_router, prefix="/operacional", tags=["Operacional - Dashboard"])
router.include_router(kpi_trends_router, prefix="/operacional", tags=["Operacional - KPI Trends"])
router.include_router(disciplinary_router, prefix="/operacional", tags=["Operacional - Medidas Administrativas"])
router.include_router(communication_router, prefix="/operacional", tags=["Operacional - Comunicacao"])
router.include_router(inspection_round_router, prefix="/operacional/rondas", tags=["Operacional - Rondas de Inspecao"])
router.include_router(vacation_router, prefix="/operacional", tags=["Operacional - Férias e Afastamentos"])

# ===================================================================
# FINANCIAL - GESTÃO FINANCEIRA COMPLETA
# ===================================================================
# Contabilidade
router.include_router(accounting_router, prefix="/financial/accounting", tags=["Financial - Contabilidade"])

# Contas a Pagar
router.include_router(supplier_router, prefix="/financial/suppliers", tags=["Financial - Fornecedores"])
router.include_router(payable_router, prefix="/financial/payables", tags=["Financial - Contas a Pagar"])

# Contas a Receber
router.include_router(customer_router, prefix="/financial/customers", tags=["Financial - Clientes"])
router.include_router(
    receivable_category_router, prefix="/financial/receivable-categories", tags=["Financial - Categorias Recebíveis"]
)
router.include_router(receivable_router, prefix="/financial/receivables", tags=["Financial - Contas a Receber"])
router.include_router(billing_rule_router, prefix="/financial/billing-rules", tags=["Financial - Regras de Cobrança"])

# Fluxo de Caixa / Bancos
router.include_router(bank_account_router, prefix="/financial/bank-accounts", tags=["Financial - Contas Bancárias"])
router.include_router(
    bank_transaction_router, prefix="/financial/bank-transactions", tags=["Financial - Transações Bancárias"]
)
router.include_router(
    bank_reconciliation_router, prefix="/financial/bank-reconciliation", tags=["Financial - Conciliação Bancária"]
)
router.include_router(cashflow_router, prefix="/financial/cashflow", tags=["Financial - Fluxo de Caixa"])

# Compras
router.include_router(purchase_router, prefix="/financial/purchases", tags=["Financial - Compras"])

# Estoque
router.include_router(inventory_router, prefix="/financial/inventory", tags=["Financial - Estoque"])

# Fiscal
router.include_router(fiscal_router, prefix="/financial/fiscal", tags=["Financial - Fiscal/Tributário"])

# AI Command Center
router.include_router(financial_ai_router, prefix="/financial", tags=["Financial AI"])

# ===================================================================
# HR - RECURSOS HUMANOS
# ===================================================================
# Analytics Dashboard (KPIs, Reports, Dashboards)
router.include_router(hr_analytics_router, prefix="/hr", tags=["HR - Analytics"])

# Portal do Funcionário (Holerites, Férias, Documentos, Preferências)
router.include_router(hr_portal_router, prefix="/hr", tags=["HR - Portal"])

# Mobile Time Clock - Ponto Mobile
router.include_router(mobile_device_router, prefix="/hr/mobile", tags=["HR - Mobile Devices"])
router.include_router(mobile_checkin_router, prefix="/hr/mobile", tags=["HR - Mobile Check-in"])
router.include_router(mobile_geofence_router, prefix="/hr/mobile", tags=["HR - Geofencing"])
router.include_router(mobile_offline_router, prefix="/hr/mobile", tags=["HR - Offline Sync"])

# Integração Folha de Pagamento (Períodos, Eventos, Export, eSocial)
router.include_router(hr_payroll_router, prefix="/hr", tags=["HR - Payroll"])

# Integração REP (Dispositivos, Sync, Eventos, AFD, Webhooks)
router.include_router(hr_rep_router, prefix="/hr", tags=["HR - REP"])

# Ponto Eletrônico (Marcações, Folha Ponto, Horas Extras, Justificativas)
router.include_router(hr_time_tracking_router, prefix="/hr", tags=["HR - Time Tracking"])

# ===================================================================
# RECRUITMENT - RECRUTAMENTO E SELEÇÃO
# ===================================================================
# Vagas, Candidatos, Candidaturas, Entrevistas
router.include_router(recruitment_router, prefix="", tags=["Recruitment"])

# ===================================================================
# AUDIT - AUDITORIA E COMPLIANCE
# ===================================================================
router.include_router(audit_router, prefix="/audit", tags=["Audit - Auditoria e Compliance"])

# ===================================================================
# CLIENTS - CLIENTES/CONDOMÍNIOS
# ===================================================================
router.include_router(client_router, prefix="/clients", tags=["Clients - Cadastro"])

# ===================================================================
# CONFIG - CONFIGURAÇÕES E MULTI-TENANT
# ===================================================================
router.include_router(config_router, prefix="/config", tags=["Config - Configurações"])

# ===================================================================
# OPERACIONAL - DIARISTAS (Submódulo)
# ===================================================================
router.include_router(diarist_router, prefix="/operacional/diaristas", tags=["Operacional - Diaristas"])
router.include_router(
    diarist_notificacao_router,
    prefix="/operacional/diaristas/notificacoes",
    tags=["Operacional - Diaristas Notificações"],
)
router.include_router(
    diarist_fiscal_router, prefix="/operacional/diaristas/fiscal", tags=["Operacional - Diaristas Fiscal"]
)

# ===================================================================
# DOCUMENT KITS - KITS DOCUMENTAIS
# ===================================================================
router.include_router(document_kit_router, prefix="/document-kits", tags=["Document Kits - Kits Documentais"])

# ===================================================================
# DOCUMENTS - DOCUMENT INTELLIGENCE (OCR/IA)
# ===================================================================
router.include_router(documents_router, prefix="", tags=["Documents - Document Intelligence"])

# ===================================================================
# EQUIPMENT MANAGEMENT - GESTÃO DE EQUIPAMENTOS
# ===================================================================
router.include_router(equipment_router, prefix="/equipment", tags=["Equipment - Equipamentos"])
router.include_router(installation_router, prefix="/equipment/installations", tags=["Equipment - Instalações"])
router.include_router(equipment_maintenance_router, prefix="/equipment/maintenance", tags=["Equipment - Manutenção"])
router.include_router(comodato_router, prefix="/equipment/comodato", tags=["Equipment - Comodato"])

# ===================================================================
# FACILITIES - REMOVIDO (Transferido para PLUS)
# ===================================================================

# ===================================================================
# GED - GESTÃO ELETRÔNICA DE DOCUMENTOS
# ===================================================================
router.include_router(folder_router, prefix="/ged/folders", tags=["GED - Pastas"])
router.include_router(document_router, prefix="/ged/documents", tags=["GED - Documentos"])
router.include_router(version_router, prefix="/ged/versions", tags=["GED - Versões"])
router.include_router(share_router, prefix="/ged/shares", tags=["GED - Compartilhamentos"])
router.include_router(tag_router, prefix="/ged/tags", tags=["GED - Tags"])
router.include_router(signature_router, prefix="/ged/signatures", tags=["GED - Assinaturas"])
router.include_router(stats_router, prefix="/ged", tags=["GED - Estatísticas"])

# ===================================================================
# INTEGRATIONS - API GATEWAY E INTEGRAÇÕES
# ===================================================================
router.include_router(integration_router, prefix="/integrations", tags=["Integrations - API Gateway"])

# ===================================================================
# OCCURRENCES - REMOVIDO (Transferido para PLUS)
# ===================================================================

# ===================================================================
# REPORTS - RELATÓRIOS GERENCIAIS
# ===================================================================
router.include_router(report_router, prefix="/reports", tags=["Reports - Relatórios Gerenciais"])

# ===================================================================
# SERVICES - GESTÃO DE SERVIÇOS
# ===================================================================
router.include_router(service_router, prefix="/services", tags=["Services - Gestão de Serviços"])

# ===================================================================
# AI - INTELIGÊNCIA ARTIFICIAL
# ===================================================================
# Análise de Contratos
router.include_router(ai_contract_router, prefix="/ai/contracts", tags=["AI - Análise de Contratos"])
# Qualidade de Dados
router.include_router(ai_data_quality_router, prefix="/ai/data-quality", tags=["AI - Qualidade de Dados"])
# Assistente de Email
router.include_router(ai_email_router, prefix="/ai/email", tags=["AI - Assistente de Email"])
# Detecção de Fraude
router.include_router(ai_fraud_router, prefix="/ai/fraud", tags=["AI - Detecção de Fraude"])
# Previsão de Inventário
router.include_router(ai_forecast_router, prefix="/ai/forecast", tags=["AI - Previsão de Inventário"])
# Base de Conhecimento
router.include_router(ai_kb_router, prefix="/ai/knowledge-base", tags=["AI - Base de Conhecimento"])
# Assistente de Reuniões
router.include_router(ai_meeting_router, prefix="/ai/meetings", tags=["AI - Assistente de Reuniões"])
# OCR - Leitura de Documentos
router.include_router(ai_ocr_router, prefix="/ai/ocr", tags=["AI - OCR"])
# Gerador de Relatórios IA
router.include_router(ai_report_router, prefix="/ai/reports", tags=["AI - Gerador de Relatórios"])
# Análise de Sentimento
router.include_router(ai_sentiment_router, prefix="/ai/sentiment", tags=["AI - Análise de Sentimento"])
# Reconhecimento de Assinatura
router.include_router(ai_signature_router, prefix="/ai/signatures", tags=["AI - Reconhecimento de Assinatura"])
# Reconhecimento de Voz
router.include_router(ai_voice_router, prefix="/ai/voice", tags=["AI - Reconhecimento de Voz"])
# Otimizador de Workflows
router.include_router(ai_workflow_router, prefix="/ai/workflows", tags=["AI - Otimizador de Workflows"])
# Bartolo - Assistente Inteligente
router.include_router(bartolo_router, prefix="/ai", tags=["AI - Bartolo Assistente"])

# ===================================================================
# MONITORING - EARLY WARNING SYSTEM (Fase 0)
# ===================================================================
from modules.monitoring import router as monitoring_router  # noqa: E402

router.include_router(monitoring_router, tags=["Monitoring - Early Warning System"])

# ===================================================================
# AUTOMATION - WORKFLOW ENGINE (Sprint 33)
# ===================================================================
from modules.automation.workflow.controllers import router as workflow_router  # noqa: E402

router.include_router(workflow_router, prefix="/workflows", tags=["Automation - Workflows"])

# ===================================================================
# FASE 5 - GRAND FINALE (CCT + Email Intelligence + MCP)
# ===================================================================
from modules.fase5.controllers import fase5_router  # noqa: E402

router.include_router(fase5_router, tags=["Fase 5 - Grand Finale"])

# ===================================================================
# FASE 3 - SECURITY LGPD (Seguranca e Compliance LGPD)
# ===================================================================
from modules.security_lgpd import security_lgpd_router  # noqa: E402

router.include_router(security_lgpd_router, prefix="/security")

# ===================================================================
# FASE 3 - HEALTH OCCUPATIONAL (Saude Ocupacional NR-4/6/7/9)
# ===================================================================
from modules.health_occupational import health_occupational_router  # noqa: E402

router.include_router(health_occupational_router, tags=["Health - Saude Ocupacional"])

# ===================================================================
# FASE 3 - GOVERNMENT INTEGRATIONS (eSocial, SEFAZ, FGTS/INSS)
# ===================================================================
from modules.government_integrations import government_integrations_router  # noqa: E402

router.include_router(government_integrations_router, tags=["Government - Integracoes Governamentais"])

# ===================================================================
# BIDDING - MÓDULO DE LICITAÇÕES PÚBLICAS
# ===================================================================
from modules.bidding import (  # noqa: E402
    certificate_router,
    tender_router,
)
from modules.bidding import (  # noqa: E402
    contract_router as bidding_contract_router,
)
from modules.bidding import (  # noqa: E402
    document_router as bidding_document_router,
)
from modules.bidding import (  # noqa: E402
    proposal_router as bidding_proposal_router,
)

router.include_router(tender_router, prefix="/bidding", tags=["Bidding - Editais"])
router.include_router(bidding_document_router, prefix="/bidding", tags=["Bidding - Documentos"])
router.include_router(bidding_proposal_router, prefix="/bidding", tags=["Bidding - Propostas"])
router.include_router(bidding_contract_router, prefix="/bidding", tags=["Bidding - Contratos"])
router.include_router(certificate_router, prefix="/bidding", tags=["Bidding - Certidoes"])

# ===================================================================
# CAMPO - SERVIÇO DE CAMPO (Equipes Externas, Visitas, OS)
# ===================================================================
from modules.campo import (  # noqa: E402
    access_log_router as campo_access_router,
)
from modules.campo import (  # noqa: E402
    campo_service_router,
    checklist_router,
    estoque_router,
    # Novos routers CAMPO v3.0
    ordem_servico_router,
    roteirizacao_router,
    visita_router,
)
from modules.campo import (  # noqa: E402
    equipment_status_router as campo_equipment_router,
)
from modules.campo import (  # noqa: E402
    occurrence_router as campo_occurrence_router,
)

# Routers legados
router.include_router(campo_service_router, prefix="/campo", tags=["Campo - Serviços e OS"])
router.include_router(campo_access_router, prefix="/campo/acessos", tags=["Campo - Logs de Acesso"])
router.include_router(campo_occurrence_router, prefix="/campo/ocorrencias", tags=["Campo - Ocorrências"])
router.include_router(campo_equipment_router, prefix="/campo/equipamentos", tags=["Campo - Equipamentos"])
# Novos routers CAMPO v3.0
router.include_router(ordem_servico_router, prefix="/campo/os", tags=["Campo - Ordens de Serviço"])
router.include_router(visita_router, prefix="/campo/visitas", tags=["Campo - Visitas"])
router.include_router(checklist_router, prefix="/campo/checklists", tags=["Campo - Checklists"])
router.include_router(roteirizacao_router, prefix="/campo/rotas", tags=["Campo - Roteirização"])
router.include_router(estoque_router, prefix="/campo/estoque", tags=["Campo - Estoque"])

# ===================================================================
# CENTRAL DE IA - INTELLIGENCE HUB (Nova Funcionalidade)
# ===================================================================
from modules.ai.intelligence_hub.controllers import intelligence_hub_router  # noqa: E402

router.include_router(intelligence_hub_router, prefix="/ai", tags=["Intelligence Hub - Central IA"])

# ===================================================================
# REIMBURSEMENT - MÓDULO DE REEMBOLSO DE DESPESAS
# ===================================================================
from modules.reimbursement import reimbursement_router  # noqa: E402

router.include_router(reimbursement_router, prefix="/reimbursements", tags=["Reimbursement - Reembolsos"])

# ===================================================================
# SEARCH - BUSCA GLOBAL
# ===================================================================
from modules.search import search_router  # noqa: E402

router.include_router(search_router, tags=["Search - Busca Global"])

# ===================================================================
# SCHEDULER - AGENDAMENTO DE TAREFAS (Sprint 35)
# ===================================================================
from modules.scheduler.controllers import router as scheduler_router  # noqa: E402

router.include_router(scheduler_router, prefix="/scheduler", tags=["Scheduler - Agendamento de Tarefas"])

# ===================================================================
# NOTIFICATIONS - NOTIFICATION HUB (Sprint 36, 37, 03)
# ===================================================================
from modules.notifications.controllers import compliance_router as notification_compliance_router  # noqa: E402
from modules.notifications.controllers import intelligent_router as intelligent_notification_router  # noqa: E402
from modules.notifications.controllers import router as notification_router  # noqa: E402
from modules.notifications.push.controllers import router as push_notification_router  # noqa: E402

router.include_router(notification_router, prefix="", tags=["Notifications - Hub"])
router.include_router(intelligent_notification_router, prefix="/notifications", tags=["Notifications - Intelligent"])
router.include_router(notification_compliance_router, prefix="/notifications", tags=["Notifications - LGPD Compliance"])
router.include_router(push_notification_router, prefix="/notifications", tags=["Notifications - Push"])

# ===================================================================
# MOBILE - API MOBILE (Sprint 38)
# ===================================================================
from modules.mobile import mobile_router  # noqa: E402

router.include_router(mobile_router, prefix="/mobile", tags=["Mobile API"])

# ===================================================================
# RETENTION - RETENÇÃO DE TALENTOS (Sprint 39)
# ===================================================================
from modules.retention import (  # noqa: E402
    climate_router,
    onboarding_router,
    profile_router,
    turnover_router,
)

router.include_router(onboarding_router, prefix="/retention/onboarding", tags=["Retention - Onboarding"])
router.include_router(profile_router, prefix="/retention/profile", tags=["Retention - Operational Profile"])
router.include_router(climate_router, prefix="/retention/climate", tags=["Retention - Climate Survey"])
router.include_router(turnover_router, prefix="/retention/turnover", tags=["Retention - Turnover Prediction"])

# ===================================================================
# EMPRESAS - MULTI-CNPJ (Sprint 67)
# ===================================================================
router.include_router(empresas_router, tags=["Empresas - Multi-CNPJ"])
