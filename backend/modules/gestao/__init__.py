"""
Módulo GESTÃO — Agregador
Unifica: config + audit + notifications + mobile + automation (workflows)
         + integrations

Routers re-exportados dos módulos de implementação.
API URLs inalteradas.
Data migração: 2026-03-11
"""

# --- Config ---
# --- Audit ---
from modules.audit.controllers import router as audit_router

# --- Automation/Workflows ---
from modules.automation.workflow.controllers import router as workflow_router
from modules.config.controllers import router as config_router

# --- Integrations ---
from modules.integrations.controllers import (
    banking_router,
    connector_router,
    integration_router,
    solides_router,
)

# --- WhatsApp (Evolution API) ---
try:
    from modules.integrations.connectors.whatsapp.controller import router as whatsapp_router
except Exception:
    whatsapp_router = None

# --- Mobile ---
from modules.mobile import mobile_router

# --- Notifications ---
from modules.notifications.controllers import compliance_router as notification_compliance_router
from modules.notifications.controllers import intelligent_router as intelligent_notification_router
from modules.notifications.controllers import router as notification_router
from modules.notifications.push.controllers import router as push_notification_router

__all__ = [
    # Config
    "config_router",
    # Audit
    "audit_router",
    # Notifications
    "notification_router",
    "notification_compliance_router",
    "intelligent_notification_router",
    "push_notification_router",
    # Mobile
    "mobile_router",
    # Workflows
    "workflow_router",
    # Integrations
    "integration_router",
    "connector_router",
    "solides_router",
    "banking_router",
    "whatsapp_router",
]
