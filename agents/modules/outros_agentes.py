"""Agentes dos módulos restantes — Conecta PRO.

Cobre: Inteligência, Negócios, Saúde Ocupacional,
       Portais, Equipamentos, Administrativo.
"""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
from base_agent import BaseAgent


# ─── INTELIGÊNCIA ───────────────────────────────

class AgenteDashboardsExecutivos(BaseAgent):
    MODULO = "inteligencia"
    SUBMODULO = "dashboards_executivos"
    ENDPOINTS = [
        '/api/v1/analytics/executive/dashboard',
        '/api/v1/analytics/executive/kpis',
        '/api/v1/analytics/executive/alerts',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'executive_dashboard '
                         'sem auth (KPIs expostos)',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]

    def auditar(self):
        return {
            'score_geral': self.db_query(
                "SELECT AVG(score) "
                "FROM module_scores "
                "WHERE created_at > "
                "CURRENT_DATE - INTERVAL '7 days';"
            ).strip()
        }


class AgenteRelatoriosOperacionais(BaseAgent):
    MODULO = "inteligencia"
    SUBMODULO = "relatorios_operacionais"
    ENDPOINTS = [
        '/api/v1/reports/operational',
        '/api/v1/reports/operational/schedule',
    ]
    CONHECE_BUGS = []


class AgenteAnalytics(BaseAgent):
    MODULO = "inteligencia"
    SUBMODULO = "analytics"
    ENDPOINTS = [
        '/api/v1/analytics/financial',
        '/api/v1/analytics/commercial',
        '/api/v1/analytics/predictive',
    ]
    CONHECE_BUGS = []


class AgenteBartolo(BaseAgent):
    MODULO = "inteligencia"
    SUBMODULO = "bartolo_ai"
    ENDPOINTS = [
        '/api/v1/operacional/ai/health',
        '/api/v1/operacional/ai/bartolo/status',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'AI endpoints /operacional/ai/* '
                         'não requerem auth (retornam 200)',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]


class AgenteMonitoramento(BaseAgent):
    MODULO = "inteligencia"
    SUBMODULO = "monitoramento"
    ENDPOINTS = [
        '/api/v1/monitoring/health',
        '/api/v1/monitoring/services',
    ]
    CONHECE_BUGS = []


# ─── NEGÓCIOS — CRM / VENDAS / LICITAÇÕES ───────

class AgenteCRM(BaseAgent):
    MODULO = "negocios"
    SUBMODULO = "crm"
    ENDPOINTS = [
        '/api/v1/crm/clients',
        '/api/v1/crm/leads',
        '/api/v1/crm/opportunities',
        '/api/v1/crm/activities',
    ]
    CONHECE_BUGS = [
        {
            'descricao': '/api/v1/clients/ retorna '
                         'vazio (bug módulo Comercial — '
                         'usar /financial/clients)',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]

    def auditar(self):
        return {
            'clientes_ativos': self.db_query(
                "SELECT COUNT(*) FROM clients "
                "WHERE status='active';"
            ).strip(),
            'leads_abertos': self.db_query(
                "SELECT COUNT(*) FROM leads "
                "WHERE status NOT IN "
                "('won','lost');"
            ).strip()
        }


class AgenteFunilVendas(BaseAgent):
    MODULO = "negocios"
    SUBMODULO = "funil_vendas"
    ENDPOINTS = [
        '/api/v1/marketing/funnel',
        '/api/v1/marketing/campaigns',
        '/api/v1/marketing/pipeline',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        # MRR real: R$ 272.086,96 (11 contratos)
        mrr = self.db_query(
            "SELECT SUM(monthly_value) "
            "FROM contracts "
            "WHERE status='active';"
        ).strip()
        return {'mrr': mrr}


class AgenteLicitacoes(BaseAgent):
    MODULO = "negocios"
    SUBMODULO = "licitacoes"
    ENDPOINTS = [
        '/api/v1/bidding/tenders',
        '/api/v1/bidding/proposals',
        '/api/v1/bidding/opportunities',
        '/api/v1/bidding/ai/analyze',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'editais_ativos': self.db_query(
                "SELECT COUNT(*) "
                "FROM bidding_tenders "
                "WHERE status='active';"
            ).strip(),
            'propostas_abertas': self.db_query(
                "SELECT COUNT(*) "
                "FROM bidding_proposals "
                "WHERE status='draft';"
            ).strip()
        }


class AgenteServicos(BaseAgent):
    MODULO = "negocios"
    SUBMODULO = "servicos"
    ENDPOINTS = [
        '/api/v1/services',
        '/api/v1/services/pricing',
        '/api/v1/services/packages',
    ]
    CONHECE_BUGS = []


# ─── SAÚDE OCUPACIONAL ──────────────────────────

class AgenteExamesASOs(BaseAgent):
    MODULO = "saude_ocupacional"
    SUBMODULO = "exames_asos"
    ENDPOINTS = [
        '/api/v1/people-management/sst/asos',
        '/api/v1/people-management/sst/asos/pending',
        '/api/v1/people-management/sst/asos/expired',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'asos_vencidos': self.db_query(
                "SELECT COUNT(*) FROM employee_asos "
                "WHERE validity_date < CURRENT_DATE "
                "AND status='active';"
            ).strip(),
            'afastados': self.db_query(
                "SELECT COUNT(*) FROM employees "
                "WHERE status='afastado';"
            ).strip()
        }


class AgenteEPIs(BaseAgent):
    MODULO = "saude_ocupacional"
    SUBMODULO = "epis"
    ENDPOINTS = [
        '/api/v1/people-management/sst/epis',
        '/api/v1/people-management/sst/epis/stock',
        '/api/v1/people-management/sst/epis/deliveries',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        # 220 EPIs cadastrados (sessão 26)
        return {
            'epis_cadastrados': self.db_query(
                "SELECT COUNT(*) FROM epis;"
            ).strip(),
            'epis_estoque_baixo': self.db_query(
                "SELECT COUNT(*) FROM epis "
                "WHERE quantity <= min_quantity;"
            ).strip()
        }


class AgenteRiscos(BaseAgent):
    MODULO = "saude_ocupacional"
    SUBMODULO = "riscos_ppra"
    ENDPOINTS = [
        '/api/v1/people-management/sst/risks',
        '/api/v1/people-management/sst/ppra',
        '/api/v1/people-management/sst/pcmso',
    ]
    CONHECE_BUGS = []


class AgenteAfastamentos(BaseAgent):
    MODULO = "saude_ocupacional"
    SUBMODULO = "afastamentos"
    ENDPOINTS = [
        '/api/v1/people-management/leaves/medical',
        '/api/v1/people-management/leaves/accident',
        '/api/v1/people-management/leaves/maternity',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'afastamentos_ativos': self.db_query(
                "SELECT COUNT(*) "
                "FROM employee_leaves "
                "WHERE end_date IS NULL "
                "OR end_date > CURRENT_DATE;"
            ).strip()
        }


class AgenteCAT(BaseAgent):
    MODULO = "saude_ocupacional"
    SUBMODULO = "cat"
    ENDPOINTS = [
        '/api/v1/people-management/sst/cat',
        '/api/v1/people-management/sst/cat/pending',
    ]
    CONHECE_BUGS = []


class AgenteNRs(BaseAgent):
    MODULO = "saude_ocupacional"
    SUBMODULO = "normas_regulamentadoras"
    ENDPOINTS = [
        '/api/v1/people-management/sst/nr1',
        '/api/v1/people-management/sst/compliance',
    ]
    CONHECE_BUGS = []


# ─── PORTAIS ────────────────────────────────────

class AgentePortalFuncionario(BaseAgent):
    MODULO = "portais"
    SUBMODULO = "portal_funcionario"
    ENDPOINTS = [
        '/api/v1/employee-portal/dashboard',
        '/api/v1/employee-portal/payslips',
        '/api/v1/employee-portal/vacations',
        '/api/v1/employee-portal/documents',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'funcionarios_com_acesso': self.db_query(
                "SELECT COUNT(*) FROM employees "
                "WHERE status='active' "
                "AND portal_access=true;"
            ).strip()
        }


class AgenteAreaCliente(BaseAgent):
    MODULO = "portais"
    SUBMODULO = "area_cliente"
    ENDPOINTS = [
        '/api/v1/client-portal/dashboard',
        '/api/v1/client-portal/kits',
        '/api/v1/client-portal/tickets',
        '/api/v1/client-portal/reports',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'clientes_com_portal': self.db_query(
                "SELECT COUNT(*) FROM clients "
                "WHERE portal_enabled=true;"
            ).strip()
        }


class AgenteMobile(BaseAgent):
    MODULO = "portais"
    SUBMODULO = "mobile_api"
    ENDPOINTS = [
        '/api/v1/mobile/auth',
        '/api/v1/mobile/dashboard',
        '/api/v1/mobile/notifications',
    ]
    CONHECE_BUGS = []


# ─── EQUIPAMENTOS ───────────────────────────────

class AgentePatrimonio(BaseAgent):
    MODULO = "equipamentos"
    SUBMODULO = "patrimonio"
    ENDPOINTS = [
        '/api/v1/equipment/assets',
        '/api/v1/equipment/assets/categories',
        '/api/v1/equipment/assets/depreciation',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'total_ativos': self.db_query(
                "SELECT COUNT(*) FROM equipment_assets "
                "WHERE status='active';"
            ).strip()
        }


class AgenteComodatos(BaseAgent):
    MODULO = "equipamentos"
    SUBMODULO = "comodatos"
    ENDPOINTS = [
        '/api/v1/equipment/loans',
        '/api/v1/equipment/loans/active',
        '/api/v1/equipment/loans/overdue',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'comodatos_ativos': self.db_query(
                "SELECT COUNT(*) "
                "FROM equipment_loans "
                "WHERE return_date IS NULL;"
            ).strip()
        }


class AgenteManutencoes(BaseAgent):
    MODULO = "equipamentos"
    SUBMODULO = "manutencoes"
    ENDPOINTS = [
        '/api/v1/equipment/maintenance',
        '/api/v1/equipment/maintenance/scheduled',
        '/api/v1/equipment/maintenance/pending',
    ]
    CONHECE_BUGS = []


class AgenteDocumentKits(BaseAgent):
    MODULO = "equipamentos"
    SUBMODULO = "document_kits"
    ENDPOINTS = [
        '/api/v1/technical/document-kits',
        '/api/v1/technical/document-kits/templates',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'kits_ativos': self.db_query(
                "SELECT COUNT(*) FROM document_kits "
                "WHERE status='active';"
            ).strip()
        }


# ─── ADMINISTRATIVO ─────────────────────────────

class AgenteIntegracoes(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "integracoes"
    ENDPOINTS = [
        '/api/v1/integrations/status',
        '/api/v1/integrations/connectors',
        '/api/v1/integrations/webhooks',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        # Gov Integrações: 16/17 online (sessão 29)
        return {
            'integracoes_online': self.db_query(
                "SELECT COUNT(*) "
                "FROM integration_connectors "
                "WHERE status='active';"
            ).strip()
        }


class AgenteLGPD(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "lgpd"
    ENDPOINTS = [
        '/api/v1/security/lgpd/consent',
        '/api/v1/security/lgpd/pia',
        '/api/v1/security/lgpd/requests',
    ]
    CONHECE_BUGS = [
        {
            'descricao': '6 controllers LGPD '
                         'sem auth (auditoria skill06)',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]


class AgenteWorkflows(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "workflows"
    ENDPOINTS = [
        '/api/v1/automation/workflows',
        '/api/v1/automation/workflows/active',
        '/api/v1/automation/triggers',
    ]
    CONHECE_BUGS = []


class AgenteConfiguracoes(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "configuracoes"
    ENDPOINTS = [
        '/api/v1/config/tenants',
        '/api/v1/config/feature-flags',
        '/api/v1/config/system',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'config_controller 47 rotas '
                         'sem auth (auditoria skill06)',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]


class AgenteAuditoria(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "auditoria"
    ENDPOINTS = [
        '/api/v1/audit/logs',
        '/api/v1/audit/events',
        '/api/v1/audit/compliance',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'eventos_hoje': self.db_query(
                "SELECT COUNT(*) FROM audit_logs "
                "WHERE created_at::date = "
                "CURRENT_DATE;"
            ).strip()
        }


class AgenteNotificacoes(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "notificacoes"
    ENDPOINTS = [
        '/api/v1/notifications',
        '/api/v1/notifications/unread',
        '/api/v1/notifications/settings',
    ]
    CONHECE_BUGS = []
