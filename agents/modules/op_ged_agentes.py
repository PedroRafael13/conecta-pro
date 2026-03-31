"""Agentes Operacional e GED."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
from base_agent import BaseAgent


# ─── OPERACIONAL ────────────────────────────────

class AgentePostos(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "postos"
    ENDPOINTS = [
        '/api/v1/operacional/posts/',
        {
            'path': '/api/v1/operacional/posts/invalido-uuid',
            'esperado': 422
        }
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'postos': self.db_query(
                "SELECT COUNT(*) FROM posts "
                "WHERE is_active=true;").strip()
        }


class AgenteEscalas(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "escalas"
    ENDPOINTS = [
        '/api/v1/operacional/scales/',
        '/api/v1/operacional/shifts/',
        '/api/v1/operacional/scales/templates/',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'scales.name vazio '
                         '(3 registros)',
            'corrigido': True,
            'auto_corrigivel': True
        },
        {
            'descricao': 'scale.shifts lazy=noload '
                         '→ total_hours sempre 0',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]

    def corrigir(self):
        # Auto-correção: popular escalas sem nome
        result = self.db_query(
            "SELECT COUNT(*) FROM scales "
            "WHERE name='' OR name IS NULL;")
        if result.strip() not in ['0', '']:
            self.db_query(
                "UPDATE scales SET name = "
                "'Escala ' || LEFT(id::text, 8) "
                "WHERE name='' OR name IS NULL;")
            self.correcoes_aplicadas.append({
                'descricao': 'scales.name populado',
                'auto': True
            })


class AgenteAlocacoes(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "alocacoes"
    ENDPOINTS = [
        '/api/v1/operacional/allocations/',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'alocados': self.db_query(
                "SELECT COUNT(*) FROM allocations "
                "WHERE status='active';").strip()
        }


class AgenteSubstituicoes(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "substituicoes"
    ENDPOINTS = [
        '/api/v1/operacional/substitutions/',
    ]
    CONHECE_BUGS = []


class AgenteOcorrencias(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "ocorrencias"
    ENDPOINTS = [
        '/api/v1/operacional/occurrences/',
    ]
    CONHECE_BUGS = []


class AgenteProcessosDisciplinares(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "processos_disciplinares"
    ENDPOINTS = [
        '/api/v1/operacional/medidas-administrativas',
        '/api/v1/operacional/medidas-administrativas/'
        'templates',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'Tenant ID mismatch — '
                         '11 medidas invisíveis',
            'corrigido': True,
            'auto_corrigivel': False
        },
        {
            'descricao': '/templates capturado '
                         'por /{action_id}',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]


class AgenteRondas(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "rondas"
    ENDPOINTS = [
        '/api/v1/operacional/rondas/',
    ]
    CONHECE_BUGS = []


class AgenteDiaristas(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "diaristas"
    ENDPOINTS = [
        '/api/v1/operacional/diaristas',
    ]
    CONHECE_BUGS = []


class AgenteComunicados(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "comunicados"
    ENDPOINTS = [
        '/api/v1/operacional/comunicados',
        {
            'path': '/api/v1/operacional/'
                    'comunicados/nao-lidos',
            'esperado': 500
        }
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'expires_at → '
                         'data_expiracao sempre NULL',
            'corrigido': True,
            'auto_corrigivel': False
        },
        {
            'descricao': 'Tenant ID mismatch — '
                         '10 comunicados invisíveis',
            'corrigido': True,
            'auto_corrigivel': False
        },
        {
            'descricao': '/comunicados/nao-lidos '
                         '→ 500 (bug no service)',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]

    def auditar(self):
        return {
            'comunicados': self.db_query(
                "SELECT COUNT(*) FROM "
                "communication_announcements;"
            ).strip()
        }


class AgenteCheckInOut(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "checkinout"
    ENDPOINTS = [
        '/api/v1/operacional/shifts/',
    ]
    CONHECE_BUGS = []


class AgenteMonitoramentoCampo(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "monitoramento_campo"
    ENDPOINTS = [
        '/api/v1/operacional/rondas/',
    ]
    CONHECE_BUGS = []


class AgenteKPITendencias(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "kpi_tendencias"
    ENDPOINTS = [
        '/api/v1/operacional/kpi-trends',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'UUID::text cast removido '
                         'em kpi_trends',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]


class AgenteAICommandCenter(BaseAgent):
    MODULO = "operacional"
    SUBMODULO = "ai_command_center"
    ENDPOINTS = [
        '/api/v1/operacional/ai/command-center',
    ]
    CONHECE_BUGS = []


# ─── GED KITS DOCUMENTAIS ───────────────────────

class AgenteDashboardGED(BaseAgent):
    MODULO = "ged"
    SUBMODULO = "dashboard"
    ENDPOINTS = [
        '/api/v1/ged/kits',
        '/api/v1/ged/clients',
        '/api/v1/ged/dashboard',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'kits': self.db_query(
                "SELECT COUNT(*) "
                "FROM ged_document_kits;").strip(),
            'documentos': self.db_query(
                "SELECT COUNT(*) "
                "FROM ged_documents;").strip()
        }


class AgenteClientesCondominios(BaseAgent):
    MODULO = "ged"
    SUBMODULO = "clientes_condominios"
    ENDPOINTS = [
        '/api/v1/ged/clients',
    ]
    CONHECE_BUGS = []


class AgenteKitsDocumentais(BaseAgent):
    MODULO = "ged"
    SUBMODULO = "kits_documentais"
    ENDPOINTS = [
        '/api/v1/ged/kits',
        '/api/v1/ged/kits/summary',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'DocumentTagRepository'
                         '.is_associated ausente',
            'corrigido': True,
            'auto_corrigivel': False
        },
        {
            'descricao': 'ZeroDivisionError '
                         'AI dashboard',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]


class AgenteDocumentosGED(BaseAgent):
    MODULO = "ged"
    SUBMODULO = "documentos"
    ENDPOINTS = [
        '/api/v1/ged/documents',
        '/api/v1/ged/folders',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'Trailing slash 404 '
                         'em rotas GED',
            'corrigido': False,
            'auto_corrigivel': True
        }
    ]


class AgenteCertidoesEmpresa(BaseAgent):
    MODULO = "ged"
    SUBMODULO = "certidoes_empresa"
    ENDPOINTS = [
        '/api/v1/ged/stats',
    ]
    CONHECE_BUGS = []


class AgenteEnviosGED(BaseAgent):
    MODULO = "ged"
    SUBMODULO = "envios"
    ENDPOINTS = [
        '/api/v1/ged/kits',
        {
            'path': '/api/v1/ged/kits/'
                    'inexistente/send',
            'method': 'POST',
            'esperado': 500
        }
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'POST kits/{id}/send '
                         '→ 500 para id inválido '
                         '(falta validação UUID)',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]


class AgenteAssinaturasGED(BaseAgent):
    MODULO = "ged"
    SUBMODULO = "assinaturas"
    ENDPOINTS = [
        '/api/v1/ged/documents',
    ]
    CONHECE_BUGS = []
