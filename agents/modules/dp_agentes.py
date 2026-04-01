"""
Agentes do Departamento Pessoal, Recursos Humanos e Ponto Eletrônico.
Endpoints validados contra OpenAPI real em 2026-03-31.
Bugs conhecidos das auditorias (skills 01-10) incorporados.
"""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
from base_agent import BaseAgent


# ═══════════════════════════════════════════════════════════
# DEPARTAMENTO PESSOAL — /api/v1/people-management/hr/
# ═══════════════════════════════════════════════════════════

class AgenteColaboradores(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "colaboradores"
    ENDPOINTS = [
        '/api/v1/people-management/hr/employees',
        '/api/v1/people-management/ponto/colaboradores-sem-escala',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'UUID path params str→UUID '
                         '(corrigido em sprint anterior)',
            'corrigido': True,
            'auto_corrigivel': False
        },
        {
            'descricao': 'is_active vs status divergente '
                         '(11 registros detectados)',
            'corrigido': True,
            'auto_corrigivel': True
        }
    ]

    def auditar(self):
        ativos = self.db_query(
            "SELECT COUNT(*) FROM employees "
            "WHERE status='ativo';")
        divergentes = self.db_query(
            "SELECT COUNT(*) FROM employees "
            "WHERE is_active=true "
            "AND status='inativo';")
        total = self.db_query(
            "SELECT COUNT(*) FROM employees;")
        return {
            'total': total.strip(),
            'ativos_status': ativos.strip(),
            'divergentes_is_active': divergentes.strip()
        }

    def corrigir(self):
        divergentes = self.db_query(
            "SELECT COUNT(*) FROM employees "
            "WHERE is_active=true AND status='inativo';")
        if divergentes.strip() not in ['0', '', 'DB_ERROR']:
            self.db_query(
                "UPDATE employees SET is_active=false "
                "WHERE status='inativo' AND is_active=true;")
            self.correcoes_aplicadas.append({
                'descricao': 'is_active sincronizado com status',
                'auto': True
            })


class AgenteAdmissao(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "admissao"
    ENDPOINTS = [
        '/api/v1/people-management/hr/admissions',
        '/api/v1/people-management/hr/admissions/stats',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        pendentes = self.db_query(
            "SELECT COUNT(*) FROM hr_admissions "
            "WHERE status='pending';")
        return {'pendentes': pendentes.strip()}


class AgenteRescisao(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "rescisao"
    ENDPOINTS = [
        '/api/v1/people-management/hr/terminations',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'total': self.db_query(
                "SELECT COUNT(*) FROM hr_terminations;").strip()
        }


class AgenteContratos(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "contratos_trabalho"
    ENDPOINTS = [
        '/api/v1/people-management/hr/contracts',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'tipo_contrato NULL em 100% dos '
                         'funcionários (52/52) — bloqueador eSocial',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]

    def auditar(self):
        sem_tipo = self.db_query(
            "SELECT COUNT(*) FROM employees "
            "WHERE tipo_contrato IS NULL "
            "OR tipo_contrato = '';")
        return {
            'sem_tipo_contrato': sem_tipo.strip(),
            'alerta': 'BLOQUEADOR_ESOCIAL' if sem_tipo.strip() not in ['0', ''] else 'OK'
        }


class AgenteFolhaSalarial(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "folha_salarial"
    ENDPOINTS = [
        '/api/v1/people-management/folha/dashboard',
        '/api/v1/people-management/hr/payroll/benefits',
        '/api/v1/people-management/dp/payslips/',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'folha_dashboard handler síncrono '
                         'sem async/db (retorna 403 para não-admin)',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]


class AgentePontoEletronico(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "ponto_eletronico"
    ENDPOINTS = [
        '/api/v1/people-management/ponto/dashboard',
        '/api/v1/people-management/ponto/batidas/me',
        '/api/v1/people-management/ponto/colaboradores-sem-escala',
        '/api/v1/people-management/ponto/relatorio/inconsistencias',
        '/api/v1/people-management/ponto/justificativas/pendentes',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'ponto_dashboard: 10 handlers '
                         'síncronos (corrigido)',
            'corrigido': True,
            'auto_corrigivel': False
        },
        {
            'descricao': '29 inconsistências ativas '
                         'no espelho de ponto',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]

    def auditar(self):
        batidas = self.db_query(
            "SELECT COUNT(*) FROM gp_clock_punches;")
        inconsistencias = self.db_query(
            "SELECT COUNT(*) FROM gp_clock_punches "
            "WHERE inconsistencia = true;")
        return {
            'total_batidas': batidas.strip(),
            'inconsistencias': inconsistencias.strip()
        }


class AgenteBancoHoras(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "banco_horas"
    ENDPOINTS = [
        '/api/v1/operacional/time-bank/',
        '/api/v1/operacional/time-bank/stats',
        '/api/v1/operacional/time-bank/alerts',
        '/api/v1/operacional/time-bank/pending',
        '/api/v1/operacional/time-bank/expiring',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'TimeBankRepository.get_stats() '
                         'exigia employee_id mas controller '
                         'chamava sem args → 500 (corrigido: '
                         'get_global_stats())',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]


class AgenteFeriasDP(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "ferias"
    ENDPOINTS = [
        '/api/v1/people-management/hr/vacations',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        return {
            'pendentes': self.db_query(
                "SELECT COUNT(*) FROM hr_vacations "
                "WHERE status='pending';").strip()
        }


class AgenteBeneficios(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "beneficios"
    ENDPOINTS = [
        '/api/v1/people-management/hr/benefits',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'UUID não serializado em benefits '
                         '(corrigido)',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]


class AgenteLicencas(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "licencas"
    ENDPOINTS = [
        '/api/v1/people-management/hr/leaves',
    ]
    CONHECE_BUGS = []


class AgenteReembolsos(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "reembolsos"
    ENDPOINTS = [
        '/api/v1/people-management/hr/reimbursements/',
    ]
    CONHECE_BUGS = []


class AgenteESocialDP(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "esocial_dp"
    ENDPOINTS = [
        '/api/v1/people-management/hr/esocial/events',
        '/api/v1/government/esocial/eventos',
        '/api/v1/government/esocial/gaps-funcionarios',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'CCT colunas SQL erradas '
                         '(cargo_nome vs nome_cargo) — corrigido',
            'corrigido': True,
            'auto_corrigivel': False
        },
        {
            'descricao': 'tipo_contrato NULL bloqueia '
                         'geração de eventos eSocial',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]

    def auditar(self):
        gaps = self.db_query(
            "SELECT COUNT(*) FROM employees "
            "WHERE tipo_contrato IS NULL;")
        return {
            'funcionarios_sem_tipo_contrato': gaps.strip(),
            'risco_esocial': 'ALTO' if gaps.strip() not in ['0', ''] else 'BAIXO'
        }


class AgenteDocumentosDP(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "documentos_dp"
    ENDPOINTS = [
        '/api/v1/people-management/hr/documents',
    ]
    CONHECE_BUGS = []


class AgenteDisciplina(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "disciplina"
    ENDPOINTS = [
        '/api/v1/people-management/hr/discipline/'
        'medidas-administrativas',
        '/api/v1/people-management/hr/discipline/'
        'medidas-administrativas/estatisticas',
    ]
    CONHECE_BUGS = []


class AgenteCCT(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "cct"
    ENDPOINTS = [
        '/api/v1/people-management/hr/cct/resumo',
        '/api/v1/people-management/hr/cct/cargos',
        '/api/v1/people-management/hr/cct/conformidade',
        '/api/v1/people-management/admin/cct/convencao-vigente',
    ]
    CONHECE_BUGS = [
        {
            'descricao': 'CCT colunas SQL '
                         '(cargo_nome vs nome_cargo) corrigido',
            'corrigido': True,
            'auto_corrigivel': False
        }
    ]

    def auditar(self):
        cargos = self.db_query(
            "SELECT COUNT(*) FROM cct_cargos;")
        return {'cargos_cadastrados': cargos.strip()}


# ═══════════════════════════════════════════════════════════
# RECURSOS HUMANOS — /people-management/human-resources/
# ═══════════════════════════════════════════════════════════

class AgenteCarreira(BaseAgent):
    MODULO = "recursos_humanos"
    SUBMODULO = "carreira"
    ENDPOINTS = [
        '/api/v1/people-management/human-resources/'
        'career/plans',
    ]
    CONHECE_BUGS = []


class AgenteClima(BaseAgent):
    MODULO = "recursos_humanos"
    SUBMODULO = "clima_organizacional"
    ENDPOINTS = [
        '/api/v1/people-management/human-resources/'
        'climate/absenteismo/alertas',
    ]
    CONHECE_BUGS = []


class AgenteTurnover(BaseAgent):
    MODULO = "recursos_humanos"
    SUBMODULO = "turnover"
    ENDPOINTS = [
        '/api/v1/people-management/human-resources/'
        'turnover/dashboard',
        '/api/v1/people-management/human-resources/'
        'turnover/motivos',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        desligados = self.db_query(
            "SELECT COUNT(*) FROM hr_terminations "
            "WHERE created_at >= NOW() - INTERVAL '30 days';")
        return {'desligamentos_30d': desligados.strip()}


class AgenteTimeTracking(BaseAgent):
    MODULO = "recursos_humanos"
    SUBMODULO = "time_tracking"
    ENDPOINTS = [
        '/api/v1/people-management/hr/time-tracking/'
        'time-tracking/justifications/',
        '/api/v1/people-management/hr/time-tracking/'
        'time-tracking/overtime/',
        '/api/v1/people-management/hr/time-tracking/'
        'time-tracking/time-entries/',
        '/api/v1/people-management/hr/time-records',
    ]
    CONHECE_BUGS = []


class AgentePayroll(BaseAgent):
    MODULO = "recursos_humanos"
    SUBMODULO = "payroll_rh"
    ENDPOINTS = [
        '/api/v1/people-management/hr/payroll/benefits',
    ]
    CONHECE_BUGS = []


# ═══════════════════════════════════════════════════════════
# PONTO ELETRÔNICO — Módulo separado (operações + fechamento)
# ═══════════════════════════════════════════════════════════

class AgenteDashboardPonto(BaseAgent):
    MODULO = "ponto_eletronico"
    SUBMODULO = "dashboard"
    ENDPOINTS = [
        '/api/v1/people-management/ponto/dashboard',
        '/api/v1/people-management/ponto/'
        'colaboradores-sem-escala',
    ]
    CONHECE_BUGS = [
        {
            'descricao': '29 inconsistências ativas '
                         'no espelho de ponto',
            'corrigido': False,
            'auto_corrigivel': False
        }
    ]

    def auditar(self):
        inconsistencias = self.db_query(
            "SELECT COUNT(*) FROM gp_clock_punches "
            "WHERE inconsistencia = true;")
        sem_batida_hoje = self.db_query(
            "SELECT COUNT(*) FROM employees "
            "WHERE status='ativo' AND id NOT IN ("
            "  SELECT DISTINCT employee_id "
            "  FROM gp_clock_punches "
            "  WHERE DATE(created_at)=CURRENT_DATE"
            ");")
        return {
            'inconsistencias_ativas': inconsistencias.strip(),
            'sem_batida_hoje': sem_batida_hoje.strip()
        }


class AgenteJustificativas(BaseAgent):
    MODULO = "ponto_eletronico"
    SUBMODULO = "justificativas"
    ENDPOINTS = [
        '/api/v1/people-management/ponto/'
        'justificativas/pendentes',
        '/api/v1/people-management/ponto/'
        'relatorio/inconsistencias',
    ]
    CONHECE_BUGS = []


class AgenteFechamentoMensal(BaseAgent):
    MODULO = "ponto_eletronico"
    SUBMODULO = "fechamento_mensal"
    ENDPOINTS = [
        {
            'path': '/api/v1/people-management/ponto/fechamento',
            'method': 'GET',
            'esperado': 405  # POST-only endpoint
        },
    ]
    CONHECE_BUGS = []


# ═══════════════════════════════════════════════════════════
# SST — Saúde e Segurança do Trabalho
# ═══════════════════════════════════════════════════════════

class AgenteSST(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "sst_saude_seguranca"
    ENDPOINTS = [
        '/api/v1/people-management/sst/aso',
        '/api/v1/people-management/sst/afastamentos',
    ]
    CONHECE_BUGS = []

    def auditar(self):
        asos_vencidos = self.db_query(
            "SELECT COUNT(*) FROM health_asos "
            "WHERE data_vencimento < CURRENT_DATE "
            "AND status='ativo';")
        afastamentos_ativos = self.db_query(
            "SELECT COUNT(*) FROM sst_afastamentos "
            "WHERE status='ativo';")
        return {
            'asos_vencidos': asos_vencidos.strip(),
            'afastamentos_ativos': afastamentos_ativos.strip()
        }


# ═══════════════════════════════════════════════════════════
# OPERATIONS IA — Command Center
# ═══════════════════════════════════════════════════════════

class AgenteCommandCenter(BaseAgent):
    MODULO = "departamento_pessoal"
    SUBMODULO = "command_center_ia"
    ENDPOINTS = [
        '/api/v1/people-management/operations/ai/'
        'command-center',
        '/api/v1/people-management/operations/ai/'
        'absence-risks',
    ]
    CONHECE_BUGS = []
