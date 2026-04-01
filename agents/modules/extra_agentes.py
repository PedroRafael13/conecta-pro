"""
Agentes extras — Inteligência, Negócios, Saúde Ocupacional,
Portais, Equipamentos e Administrativo.
Endpoints validados contra OpenAPI real em 2026-04-01.
"""
import sys

sys.path.insert(0, "/opt/conecta-pro/agents/core")
from base_agent import BaseAgent  # noqa: E402


# ═══════════════════════════════════════════════════════════
# INTELIGÊNCIA — /api/v1/ai/
# ═══════════════════════════════════════════════════════════


class AgenteAIBartolo(BaseAgent):
    MODULO = "inteligencia"
    SUBMODULO = "bartolo_core"
    ENDPOINTS = [
        "/api/v1/ai/bartolo/health",
        "/api/v1/ai/bartolo/stats",
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            "health": self.db_query(
                "SELECT COUNT(*) FROM ai_conversation_history;"
            ).strip()
        }


class AgenteAIModulos(BaseAgent):
    MODULO = "inteligencia"
    SUBMODULO = "bartolo_modulos"
    ENDPOINTS = [
        "/api/v1/ai/bartolo/modules",
        "/api/v1/ai/bartolo/wizards",
        "/api/v1/ai/bartolo/greeting",
    ]
    CONHECE_BUGS = []


class AgenteAIAprendizado(BaseAgent):
    MODULO = "inteligencia"
    SUBMODULO = "bartolo_learning"
    ENDPOINTS = [
        "/api/v1/ai/bartolo/learning/stats",
        "/api/v1/ai/bartolo/learning/patterns",
    ]
    CONHECE_BUGS = []


# ═══════════════════════════════════════════════════════════
# NEGÓCIOS — /api/v1/crm/ + /api/v1/bidding/
# ═══════════════════════════════════════════════════════════


class AgenteCRMLeads(BaseAgent):
    MODULO = "negocios"
    SUBMODULO = "crm_leads"
    ENDPOINTS = [
        "/api/v1/crm/leads",
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            "leads_abertos": self.db_query(
                "SELECT COUNT(*) FROM crm_leads "
                "WHERE status='aberto';"
            ).strip()
        }


class AgenteCRMOportunidades(BaseAgent):
    MODULO = "negocios"
    SUBMODULO = "crm_oportunidades"
    ENDPOINTS = [
        "/api/v1/crm/opportunities",
        "/api/v1/crm/proposals",
    ]
    CONHECE_BUGS = []


class AgenteCRMContratos(BaseAgent):
    MODULO = "negocios"
    SUBMODULO = "crm_contratos"
    ENDPOINTS = [
        "/api/v1/crm/contracts",
        "/api/v1/crm/commissions",
    ]
    CONHECE_BUGS = []


# ═══════════════════════════════════════════════════════════
# SAÚDE OCUPACIONAL — /api/v1/health-occupational/ + /sst/
# ═══════════════════════════════════════════════════════════


class AgenteSaudeOcupacional(BaseAgent):
    MODULO = "saude_ocupacional"
    SUBMODULO = "health_occupational_status"
    ENDPOINTS = [
        "/api/v1/health-occupational/health",
        "/api/v1/health-occupational/status",
        "/api/v1/health-occupational/info",
    ]
    CONHECE_BUGS = []


class AgentePCMSO(BaseAgent):
    MODULO = "saude_ocupacional"
    SUBMODULO = "pcmso_aso"
    ENDPOINTS = [
        "/api/v1/people-management/sst/aso",
        "/api/v1/people-management/sst/afastamentos",
    ]
    CONHECE_BUGS = []

    def auditar(self):
        asos_vencidos = self.db_query(
            "SELECT COUNT(*) FROM health_asos "
            "WHERE data_vencimento < CURRENT_DATE "
            "AND status='ativo';"
        ).strip()
        afastamentos = self.db_query(
            "SELECT COUNT(*) FROM sst_afastamentos "
            "WHERE status='ativo';"
        ).strip()
        return {
            "asos_vencidos": asos_vencidos,
            "afastamentos_ativos": afastamentos,
        }


# ═══════════════════════════════════════════════════════════
# PORTAIS — /api/v1/clients/ + /government/ + /cct/
# ═══════════════════════════════════════════════════════════


class AgentePortalClientes(BaseAgent):
    MODULO = "portais"
    SUBMODULO = "portal_clientes"
    ENDPOINTS = [
        "/api/v1/clients",
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            "clientes": self.db_query(
                "SELECT COUNT(*) FROM clients;"
            ).strip()
        }


class AgenteGovESocial(BaseAgent):
    MODULO = "portais"
    SUBMODULO = "governo_esocial"
    ENDPOINTS = [
        "/api/v1/government/esocial/eventos",
        "/api/v1/government/esocial/gaps-funcionarios",
    ]
    CONHECE_BUGS = []


class AgenteCCTPortal(BaseAgent):
    MODULO = "portais"
    SUBMODULO = "cct_portal"
    ENDPOINTS = [
        "/api/v1/people-management/hr/cct/resumo",
        "/api/v1/people-management/hr/cct/conformidade",
        "/api/v1/people-management/hr/cct/cargos",
        "/api/v1/people-management/admin/cct/convencao-vigente",
    ]
    CONHECE_BUGS = []


# ═══════════════════════════════════════════════════════════
# EQUIPAMENTOS — /api/v1/equipment/
# ═══════════════════════════════════════════════════════════


class AgenteEquipamentos(BaseAgent):
    MODULO = "equipamentos"
    SUBMODULO = "equipment_inventory"
    ENDPOINTS = [
        {
            "path": "/api/v1/equipment/stats",
            "esperado": 500,  # bug conhecido — DB model divergência
        },
        {
            "path": "/api/v1/equipment/in-stock",
            "esperado": 500,  # bug conhecido
        },
    ]
    CONHECE_BUGS = [
        {
            "descricao": "GET /equipment/stats retorna 500 — "
            "divergência model/DB no módulo equipment_management",
            "corrigido": False,
            "auto_corrigivel": False,
        }
    ]


class AgenteEquipamentosManutencao(BaseAgent):
    MODULO = "equipamentos"
    SUBMODULO = "equipment_manutencao"
    ENDPOINTS = [
        {
            "path": "/api/v1/equipment/needing-maintenance",
            "esperado": 500,  # bug conhecido
        },
    ]
    CONHECE_BUGS = [
        {
            "descricao": "Endpoints de manutenção retornam 500 — "
            "model divergência equipment_management",
            "corrigido": False,
            "auto_corrigivel": False,
        }
    ]


# ═══════════════════════════════════════════════════════════
# ADMINISTRATIVO — /api/v1/reimbursements/ + notifications
# ═══════════════════════════════════════════════════════════


class AgenteReembolsos(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "reembolsos_admin"
    ENDPOINTS = [
        "/api/v1/reimbursements/",
        "/api/v1/reimbursements/stats",
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            "pendentes": self.db_query(
                "SELECT COUNT(*) FROM reimbursements "
                "WHERE status='pending';"
            ).strip()
        }


class AgenteNotificacoesAdmin(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "notificacoes"
    ENDPOINTS = [
        "/api/v1/notifications/push",
        "/api/v1/notifications/push/subscriptions",
    ]
    CONHECE_BUGS = [
        {
            "descricao": "Notificações push — endpoint requires "
            "specific permissions além de admin",
            "corrigido": False,
            "auto_corrigivel": False,
        }
    ]


class AgenteCCTAdmin(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "cct_admin"
    ENDPOINTS = [
        "/api/v1/people-management/hr/cct/resumo",
        "/api/v1/people-management/hr/cct/cargos",
    ]
    CONHECE_BUGS = []
