"""Agentes dos módulos restantes — Conecta PRO."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
from base_agent import BaseAgent


# ─── INTELIGÊNCIA ───────────────────────────────

class AgenteDashboardsExecutivos(BaseAgent):
    MODULO = "inteligencia"
    SUBMODULO = "dashboards_executivos"
    ENDPOINTS = [
        '/api/v1/analytics/executive/dashboard',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'executive_dashboard '
                         'sem auth (KPIs expostos)',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]


class AgenteRelatoriosOperacionais(BaseAgent):
    MODULO = "inteligencia"
    SUBMODULO = "relatorios_operacionais"
    ENDPOINTS = [
        '/api/v1/reports/operational',
    ]
    CONHECE_BUGS = []


class AgenteAnalytics(BaseAgent):
    MODULO = "inteligencia"
    SUBMODULO = "analytics"
    ENDPOINTS = [
        '/api/v1/analytics/financial',
        '/api/v1/analytics/commercial',
    ]
    CONHECE_BUGS = []


# ─── NEGÓCIOS — CRM ─────────────────────────────

class AgenteCRM(BaseAgent):
    MODULO = "negocios"
    SUBMODULO = "crm"
    ENDPOINTS = [
        '/api/v1/crm/clients',
        '/api/v1/crm/leads',
        '/api/v1/crm/opportunities',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'clientes': self.db_query(
                "SELECT COUNT(*) FROM clients "
                "WHERE status='active';").strip(),
            'leads': self.db_query(
                "SELECT COUNT(*) "
                "FROM leads;").strip()
        }


class AgenteFunilVendas(BaseAgent):
    MODULO = "negocios"
    SUBMODULO = "funil_vendas"
    ENDPOINTS = [
        '/api/v1/marketing/funnel',
        '/api/v1/marketing/campaigns',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        # MRR real: R$ 272.086,96
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
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'editais': self.db_query(
                "SELECT COUNT(*) "
                "FROM bidding_tenders "
                "WHERE status='active';"
            ).strip()
        }


# ─── SAÚDE OCUPACIONAL ──────────────────────────

class AgenteExamesASOs(BaseAgent):
    MODULO = "saude_ocupacional"
    SUBMODULO = "exames_asos"
    ENDPOINTS = [
        '/api/v1/people-management/sst/asos',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
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
    ]
    CONHECE_BUGS = []


class AgenteRiscos(BaseAgent):
    MODULO = "saude_ocupacional"
    SUBMODULO = "riscos_ppra"
    ENDPOINTS = [
        '/api/v1/people-management/sst/risks',
    ]
    CONHECE_BUGS = []


class AgenteAfastamentos(BaseAgent):
    MODULO = "saude_ocupacional"
    SUBMODULO = "afastamentos"
    ENDPOINTS = [
        '/api/v1/people-management/leaves/'
        'medical',
    ]
    CONHECE_BUGS = []


class AgenteCAT(BaseAgent):
    MODULO = "saude_ocupacional"
    SUBMODULO = "cat"
    ENDPOINTS = [
        '/api/v1/people-management/sst/cat',
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
    ]
    CONHECE_BUGS = []


class AgenteAreaCliente(BaseAgent):
    MODULO = "portais"
    SUBMODULO = "area_cliente"
    ENDPOINTS = [
        '/api/v1/client-portal/dashboard',
        '/api/v1/client-portal/kits',
        '/api/v1/client-portal/tickets',
    ]
    CONHECE_BUGS = []


# ─── EQUIPAMENTOS ───────────────────────────────

class AgentePatrimonio(BaseAgent):
    MODULO = "equipamentos"
    SUBMODULO = "patrimonio"
    ENDPOINTS = [
        '/api/v1/equipment/assets',
    ]
    CONHECE_BUGS = []


class AgenteComodatos(BaseAgent):
    MODULO = "equipamentos"
    SUBMODULO = "comodatos"
    ENDPOINTS = [
        '/api/v1/equipment/loans',
    ]
    CONHECE_BUGS = []


class AgenteManutencoes(BaseAgent):
    MODULO = "equipamentos"
    SUBMODULO = "manutencoes"
    ENDPOINTS = [
        '/api/v1/equipment/maintenance',
    ]
    CONHECE_BUGS = []


# ─── ADMINISTRATIVO ─────────────────────────────

class AgenteIntegracoes(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "integracoes"
    ENDPOINTS = [
        '/api/v1/integrations/status',
        '/api/v1/integrations/connectors',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        # Verificar integrações online
        # 16 online, 1 homologação
        return {}


class AgenteLGPD(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "lgpd"
    ENDPOINTS = [
        '/api/v1/security/lgpd/consent',
        '/api/v1/security/lgpd/pia',
    ]
    CONHECE_BUGS = [
        {
            'descricao': '6 controllers LGPD '
                         'sem auth',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]


class AgenteWorkflows(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "workflows"
    ENDPOINTS = [
        '/api/v1/automation/workflows',
    ]
    CONHECE_BUGS = []


class AgenteConfiguracoes(BaseAgent):
    MODULO = "administrativo"
    SUBMODULO = "configuracoes"
    ENDPOINTS = [
        '/api/v1/config/tenants',
        '/api/v1/config/feature-flags',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'config_controller 47 rotas '
                         'sem auth',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]
