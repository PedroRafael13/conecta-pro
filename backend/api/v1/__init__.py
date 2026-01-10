"""
API v1 - Router principal.
"""

from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from modules.crm.controllers import (
    commission_router,
    contract_router,
    dashboard_router,
    lead_router,
    opportunity_router,
    proposal_router,
)

from modules.operations.controllers import (
    allocation_router,
    post_router,
    scale_router,
    shift_router,
    substitution_router,
    time_bank_router,
)

# ===================================================================
# MÓDULO FINANCIAL - Gestão Financeira Completa
# ===================================================================
from modules.financial.controllers import (
    # Contabilidade
    accounting_router,
    # Contas a Pagar
    supplier_router,
    payable_router,
    # Contas a Receber
    customer_router,
    receivable_category_router,
    receivable_router,
    billing_rule_router,
    # Fluxo de Caixa / Bancos
    bank_account_router,
    bank_transaction_router,
    bank_reconciliation_router,
    cashflow_router,
    # Compras
    purchase_router,
    # Estoque
    inventory_router,
    # Fiscal
    fiscal_router,
)


# ===================================================================
# MÓDULO AI - INTELIGÊNCIA ARTIFICIAL (Sprints 34-55)
# ===================================================================
# Chatbot IA (Sprint 38)
from modules.ai.chatbot.controllers import router as ai_chatbot_router
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
# HR - RECURSOS HUMANOS
# ===================================================================
# Analytics Dashboard
from modules.hr.analytics_dashboard import router as hr_analytics_router
# Portal do Funcionário
from modules.hr.employee_portal.controllers import router as hr_portal_router
# Mobile Time Clock (Ponto Mobile)
from modules.hr.mobile_time_clock import (
    device_router as mobile_device_router,
    checkin_router as mobile_checkin_router,
    geofence_router as mobile_geofence_router,
    offline_router as mobile_offline_router,
)
# Integração com Folha de Pagamento
from modules.hr.payroll_integration import router as hr_payroll_router
# Integração REP (Registrador Eletrônico de Ponto)
from modules.hr.rep_integration.controllers import router as hr_rep_router
# Ponto Eletrônico / Time Tracking
from modules.hr.time_tracking.controllers import router as hr_time_tracking_router

# ===================================================================
# RECRUITMENT - RECRUTAMENTO E SELEÇÃO
# ===================================================================
from modules.recruitment import router as recruitment_router

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

# ===================================================================
# MÓDULO DIARISTS - Gestão de Diaristas
# ===================================================================
from modules.diarists.controllers import router as diarist_router

# ===================================================================
# MÓDULO DOCUMENT_KITS - Kits Documentais
# ===================================================================
from modules.document_kits.controllers import router as document_kit_router

# ===================================================================
# MÓDULO EQUIPMENT_MANAGEMENT - Gestão de Equipamentos
# ===================================================================
# TODO: Módulo equipment_management não implementado ainda
# from modules.equipment_management.controllers import (
#     equipment_router,
#     installation_router,
#     maintenance_router as equipment_maintenance_router,
#     comodato_router,
# )

# ===================================================================
# MÓDULO FACILITIES - Gestão de Facilities
# ===================================================================
from modules.facilities.controllers import (
    area_router,
    maintenance_router as facilities_maintenance_router,
    inspection_router,
    checklist_router,
    service_request_router,
)

# ===================================================================
# MÓDULO GED - Gestão Eletrônica de Documentos
# ===================================================================
from modules.ged.controllers import (
    folder_router,
    document_router,
    version_router,
    share_router,
    tag_router,
    signature_router,
)

# ===================================================================
# MÓDULO INTEGRATIONS - API Gateway / Integrações (Sprint 32)
# ===================================================================
from modules.integrations.controllers import router as integration_router

# ===================================================================
# MÓDULO OCCURRENCES - Gestão de Ocorrências
# ===================================================================
from modules.occurrences.controllers import (
    occurrence_router as occurrences_router,
    category_router as occurrence_category_router,
    comment_router as occurrence_comment_router,
    attachment_router as occurrence_attachment_router,
)

# ===================================================================
# MÓDULO REPORTS - Relatórios Gerenciais (Sprint 34)
# ===================================================================
from modules.reports.controllers import router as report_router

# ===================================================================
# MÓDULO SERVICES - Gestão de Serviços (Sprint 31)
# ===================================================================
from modules.services.controllers import router as service_router

router = APIRouter(prefix="/api/v1")

# ===================================================================
# ROUTERS EXISTENTES
# ===================================================================
router.include_router(auth_router)
router.include_router(lead_router)
router.include_router(opportunity_router)
router.include_router(proposal_router)
router.include_router(commission_router)
router.include_router(dashboard_router)
router.include_router(contract_router)

# ===================================================================
# OPERATIONS - POSTOS E ESCALAS
# ===================================================================
router.include_router(post_router, prefix="/operations/posts", tags=["Operations - Postos"])
router.include_router(scale_router, prefix="/operations/scales", tags=["Operations - Escalas"])
router.include_router(shift_router, prefix="/operations/shifts", tags=["Operations - Turnos"])
router.include_router(allocation_router, prefix="/operations/allocations", tags=["Operations - Alocações"])
router.include_router(substitution_router, prefix="/operations/substitutions", tags=["Operations - Substituições"])
router.include_router(time_bank_router, prefix="/operations/time-bank", tags=["Operations - Banco de Horas"])

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
router.include_router(receivable_category_router, prefix="/financial/receivable-categories", tags=["Financial - Categorias Recebíveis"])
router.include_router(receivable_router, prefix="/financial/receivables", tags=["Financial - Contas a Receber"])
router.include_router(billing_rule_router, prefix="/financial/billing-rules", tags=["Financial - Regras de Cobrança"])

# Fluxo de Caixa / Bancos
router.include_router(bank_account_router, prefix="/financial/bank-accounts", tags=["Financial - Contas Bancárias"])
router.include_router(bank_transaction_router, prefix="/financial/bank-transactions", tags=["Financial - Transações Bancárias"])
router.include_router(bank_reconciliation_router, prefix="/financial/bank-reconciliation", tags=["Financial - Conciliação Bancária"])
router.include_router(cashflow_router, prefix="/financial/cashflow", tags=["Financial - Fluxo de Caixa"])

# Compras
router.include_router(purchase_router, prefix="/financial/purchases", tags=["Financial - Compras"])

# Estoque
router.include_router(inventory_router, prefix="/financial/inventory", tags=["Financial - Estoque"])

# Fiscal
router.include_router(fiscal_router, prefix="/financial/fiscal", tags=["Financial - Fiscal/Tributário"])


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
# DIARISTS - GESTÃO DE DIARISTAS
# ===================================================================
router.include_router(diarist_router, prefix="/diarists", tags=["Diarists - Gestão de Diaristas"])

# ===================================================================
# DOCUMENT KITS - KITS DOCUMENTAIS
# ===================================================================
router.include_router(document_kit_router, prefix="/document-kits", tags=["Document Kits - Kits Documentais"])

# ===================================================================
# EQUIPMENT MANAGEMENT - GESTÃO DE EQUIPAMENTOS
# ===================================================================
# TODO: Módulo equipment_management não implementado ainda
# router.include_router(equipment_router, prefix="/equipment", tags=["Equipment - Equipamentos"])
# router.include_router(installation_router, prefix="/equipment/installations", tags=["Equipment - Instalações"])
# router.include_router(equipment_maintenance_router, prefix="/equipment/maintenance", tags=["Equipment - Manutenção"])
# router.include_router(comodato_router, prefix="/equipment/comodato", tags=["Equipment - Comodato"])

# ===================================================================
# FACILITIES - GESTÃO DE FACILITIES
# ===================================================================
router.include_router(area_router, prefix="/facilities/areas", tags=["Facilities - Áreas"])
router.include_router(facilities_maintenance_router, prefix="/facilities/maintenance", tags=["Facilities - Manutenção"])
router.include_router(inspection_router, prefix="/facilities/inspections", tags=["Facilities - Inspeções"])
router.include_router(checklist_router, prefix="/facilities/checklists", tags=["Facilities - Checklists"])
router.include_router(service_request_router, prefix="/facilities/service-requests", tags=["Facilities - Solicitações de Serviço"])

# ===================================================================
# GED - GESTÃO ELETRÔNICA DE DOCUMENTOS
# ===================================================================
router.include_router(folder_router, prefix="/ged/folders", tags=["GED - Pastas"])
router.include_router(document_router, prefix="/ged/documents", tags=["GED - Documentos"])
router.include_router(version_router, prefix="/ged/versions", tags=["GED - Versões"])
router.include_router(share_router, prefix="/ged/shares", tags=["GED - Compartilhamentos"])
router.include_router(tag_router, prefix="/ged/tags", tags=["GED - Tags"])
router.include_router(signature_router, prefix="/ged/signatures", tags=["GED - Assinaturas"])

# ===================================================================
# INTEGRATIONS - API GATEWAY E INTEGRAÇÕES
# ===================================================================
router.include_router(integration_router, prefix="/integrations", tags=["Integrations - API Gateway"])

# ===================================================================
# OCCURRENCES - GESTÃO DE OCORRÊNCIAS
# ===================================================================
router.include_router(occurrences_router, prefix="/occurrences", tags=["Occurrences - Ocorrências"])
router.include_router(occurrence_category_router, prefix="/occurrences/categories", tags=["Occurrences - Categorias"])
router.include_router(occurrence_comment_router, prefix="/occurrences/comments", tags=["Occurrences - Comentários"])
router.include_router(occurrence_attachment_router, prefix="/occurrences/attachments", tags=["Occurrences - Anexos"])

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
# Chatbot IA
router.include_router(ai_chatbot_router, prefix="/ai/chatbot", tags=["AI - Chatbot"])
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

# ===================================================================
# MONITORING - EARLY WARNING SYSTEM (Fase 0)
# ===================================================================
from modules.monitoring import router as monitoring_router
router.include_router(monitoring_router, tags=["Monitoring - Early Warning System"])

# ===================================================================
# AUTOMATION - WORKFLOW ENGINE (Sprint 33)
# ===================================================================
from modules.automation.workflow.controllers import router as workflow_router
router.include_router(workflow_router, prefix="/workflows", tags=["Automation - Workflows"])

# ===================================================================
# FASE 5 - GRAND FINALE (CCT + Email Intelligence + MCP)
# ===================================================================
from modules.fase5.controllers import fase5_router
router.include_router(fase5_router, tags=["Fase 5 - Grand Finale"])