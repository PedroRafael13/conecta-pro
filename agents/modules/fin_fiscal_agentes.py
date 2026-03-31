"""Agentes Financeiro e Fiscal & Contábil."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
from base_agent import BaseAgent


# ─── FINANCEIRO ─────────────────────────────────

class AgenteDashboardFinanceiro(BaseAgent):
    MODULO = "financeiro"
    SUBMODULO = "dashboard"
    ENDPOINTS = [
        '/api/v1/financial/bi/dashboard',
        '/api/v1/financial/bi/revenue',
        '/api/v1/financial/bi/cashflow',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'BI Dashboard Session→'
                         'AsyncSession (0/11 endpoints)',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]

    def auditar(self):
        return {
            'receita': self.db_query(
                "SELECT SUM(gross_value) "
                "FROM receivable_accounts "
                "WHERE status='paga';").strip(),
            'inadimplencia': self.db_query(
                "SELECT SUM(gross_value) "
                "FROM receivable_accounts "
                "WHERE status='pendente' "
                "AND due_date < CURRENT_DATE;"
            ).strip()
        }


class AgenteContratos(BaseAgent):
    MODULO = "financeiro"
    SUBMODULO = "contratos"
    ENDPOINTS = [
        '/api/v1/financial/contracts',
    ]
    CONHECE_BUGS = []


class AgenteContasPagar(BaseAgent):
    MODULO = "financeiro"
    SUBMODULO = "contas_pagar"
    ENDPOINTS = [
        '/api/v1/financial/payables',
        '/api/v1/financial/payables/upcoming',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'condominio_id sem '
                         'fallback JWT → 422',
            'corrigido': True,
            'auto_corrigivel': False
        },
        {
            'descricao': 'N+1 em bulk_payment',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]

    def auditar(self):
        return {
            'total': self.db_query(
                "SELECT COUNT(*), SUM(gross_value) "
                "FROM payable_accounts;").strip()
        }


class AgenteContasReceber(BaseAgent):
    MODULO = "financeiro"
    SUBMODULO = "contas_receber"
    ENDPOINTS = [
        '/api/v1/financial/receivables',
        '/api/v1/financial/receivables/upcoming',
        '/api/v1/financial/receivables/'
        'installments/pending',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'grace_days coluna '
                         'inexistente no banco',
            'corrigido': True,
            'auto_corrigivel': False
        },
        {
            'descricao': '/installments/pending '
                         'capturado por /{id}',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]

    def auditar(self):
        return {
            'total': self.db_query(
                "SELECT COUNT(*), SUM(gross_value) "
                "FROM receivable_accounts;").strip()
        }


class AgenteFluxoCaixa(BaseAgent):
    MODULO = "financeiro"
    SUBMODULO = "fluxo_caixa"
    ENDPOINTS = [
        '/api/v1/financial/cashflow/dashboard',
        '/api/v1/financial/cashflow/forecast',
    ]
    CONHECE_BUGS = []


class AgenteConciliacaoBancaria(BaseAgent):
    MODULO = "financeiro"
    SUBMODULO = "conciliacao_bancaria"
    ENDPOINTS = [
        '/api/v1/financial/bank-transactions',
        '/api/v1/financial/bank-reconciliations',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'list_with_filters '
                         'ausente no BankTransaction',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]

    def auditar(self):
        return {
            'transacoes': self.db_query(
                "SELECT COUNT(*) "
                "FROM bank_transactions;").strip()
        }


class AgenteBoletos(BaseAgent):
    MODULO = "financeiro"
    SUBMODULO = "boletos_cobr"
    ENDPOINTS = [
        '/api/v1/financial/boletos',
        '/api/v1/financial/cobrancas',
    ]
    CONHECE_BUGS = []


class AgenteFornecedores(BaseAgent):
    MODULO = "financeiro"
    SUBMODULO = "fornecedores"
    ENDPOINTS = [
        '/api/v1/financial/suppliers',
    ]
    CONHECE_BUGS = []


class AgenteContabilidade(BaseAgent):
    MODULO = "financeiro"
    SUBMODULO = "contabilidade"
    ENDPOINTS = [
        '/api/v1/financial/accounting/cost-centers',
        '/api/v1/financial/accounting/periods',
        '/api/v1/financial/accounting/'
        'trial-balances',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'current_user["key"] '
                         '→ current_user.key '
                         '(72 ocorrências)',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]


class AgenteFaturamento(BaseAgent):
    MODULO = "financeiro"
    SUBMODULO = "faturamento"
    ENDPOINTS = [
        '/api/v1/financial/billing',
    ]
    CONHECE_BUGS = []


class AgentePrecificacao(BaseAgent):
    MODULO = "financeiro"
    SUBMODULO = "precificacao"
    ENDPOINTS = [
        '/api/v1/financial/pricing',
    ]
    CONHECE_BUGS = []


class AgenteRelatoriosFinanceiros(BaseAgent):
    MODULO = "financeiro"
    SUBMODULO = "relatorios_fin"
    ENDPOINTS = [
        '/api/v1/financial/reports',
    ]
    CONHECE_BUGS = []


# ─── FISCAL & CONTÁBIL ───────────────────────────

class AgenteNFe(BaseAgent):
    MODULO = "fiscal_contabil"
    SUBMODULO = "nfe"
    ENDPOINTS = [
        '/api/v1/government/sefaz/nfe/list',
    ]
    CONHECE_BUGS = []


class AgenteNFSe(BaseAgent):
    MODULO = "fiscal_contabil"
    SUBMODULO = "nfse"
    ENDPOINTS = [
        '/api/v1/government/nfse/list',
        '/api/v1/government/nfse-manaus/list',
    ]
    CONHECE_BUGS = []


class AgenteCertidoes(BaseAgent):
    MODULO = "fiscal_contabil"
    SUBMODULO = "certidoes"
    ENDPOINTS = [
        '/api/v1/government/certificates',
        '/api/v1/government/ecac/certidoes',
    ]
    CONHECE_BUGS = []


class AgenteESocialFiscal(BaseAgent):
    MODULO = "fiscal_contabil"
    SUBMODULO = "esocial_fiscal"
    ENDPOINTS = [
        '/api/v1/government/esocial/status',
        {
            'path': '/api/v1/government/'
                    'esocial/eventos',
            'esperado': 200
        }
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'esocial/eventos '
                         'sem auth (dados fiscais)',
            'corrigido': True,
            'auto_corrigivel': False
        },
        {
            'descricao': 'get_db_sync ImportError',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]


class AgenteSPED(BaseAgent):
    MODULO = "fiscal_contabil"
    SUBMODULO = "sped"
    ENDPOINTS = [
        '/api/v1/government/sped-fiscal/status',
        '/api/v1/government/sped-contabil/status',
    ]
    CONHECE_BUGS = []


class AgenteDCTFWeb(BaseAgent):
    MODULO = "fiscal_contabil"
    SUBMODULO = "dctfweb"
    ENDPOINTS = [
        '/api/v1/government/dctfweb/status',
    ]
    CONHECE_BUGS = []


class AgenteEFDReinf(BaseAgent):
    MODULO = "fiscal_contabil"
    SUBMODULO = "efd_reinf"
    ENDPOINTS = [
        '/api/v1/government/reinf/status',
        '/api/v1/government/reinf/r1000',
    ]
    CONHECE_BUGS = []
