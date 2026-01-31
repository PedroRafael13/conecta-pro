"""
ERP Conecta Mais V2.0 - Producao (Modulos Core)
Versao otimizada que carrega apenas modulos estaveis.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.config import settings
from core.logging import configure_logging, logger

# =============================================================================
# SENTRY INITIALIZATION
# =============================================================================
if settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        release=f"conecta-pro@{settings.app_version}",
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
        ],
        send_default_pii=False,
        attach_stacktrace=True,
    )
    logger.info("Sentry: inicializado")


# =============================================================================
# SECURITY HEADERS MIDDLEWARE
# =============================================================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if "/api/" in request.url.path:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        return response


# =============================================================================
# RATE LIMITER
# =============================================================================
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    from core.cache import close_redis, get_redis
    from core.database import close_db

    configure_logging()
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    logger.info(f"Ambiente: {settings.environment}")

    try:
        await get_redis()
        logger.info("Redis: conectado")
    except Exception as e:
        logger.warning(f"Redis: falha na conexao ({e})")

    yield

    logger.info("Encerrando aplicacao...")
    await close_redis()
    await close_db()
    logger.info("Conexoes fechadas")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema ERP completo para gestao empresarial",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# =============================================================================
# MIDDLEWARES
# =============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=500)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/health/detailed", tags=["Health"])
async def health_check_detailed():
    """
    Health check detalhado para UptimeRobot e monitoramento.
    Verifica: Database, Redis, Celery.
    Retorna: healthy, degraded ou unhealthy.
    """
    from core.cache import get_redis
    from core.database.session import async_session_factory
    from sqlalchemy import text

    checks = {
        "database": {"status": "unknown", "latency_ms": None, "error": None},
        "redis": {"status": "unknown", "latency_ms": None, "error": None},
        "celery": {"status": "unknown", "latency_ms": None, "error": None},
    }

    # Check Database
    try:
        start = time.time()
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        latency = (time.time() - start) * 1000
        checks["database"] = {"status": "healthy", "latency_ms": round(latency, 2), "error": None}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "latency_ms": None, "error": str(e)[:200]}

    # Check Redis
    try:
        start = time.time()
        redis = await get_redis()
        if redis:
            await redis.ping()
            latency = (time.time() - start) * 1000
            checks["redis"] = {"status": "healthy", "latency_ms": round(latency, 2), "error": None}
        else:
            checks["redis"] = {"status": "degraded", "latency_ms": None, "error": "Redis not configured"}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "latency_ms": None, "error": str(e)[:200]}

    # Check Celery (via Redis broker)
    try:
        start = time.time()
        import redis as redis_sync
        celery_redis = redis_sync.from_url(settings.redis_url.replace("/1", "/0"))
        celery_redis.ping()
        latency = (time.time() - start) * 1000
        checks["celery"] = {"status": "healthy", "latency_ms": round(latency, 2), "error": None}
        celery_redis.close()
    except Exception as e:
        checks["celery"] = {"status": "degraded", "latency_ms": None, "error": str(e)[:200]}

    # Determine overall status
    statuses = [c["status"] for c in checks.values()]
    if all(s == "healthy" for s in statuses):
        overall = "healthy"
    elif "unhealthy" in statuses:
        overall = "unhealthy"
    else:
        overall = "degraded"

    return {
        "status": overall,
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": checks,
        "timestamp": time.time(),
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Bem-vindo ao {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
    }


# =============================================================================
# API ROUTER - CARREGAMENTO SEGURO
# =============================================================================
from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")


# Funcao helper para importar modulos com seguranca
def safe_import(module_path: str, router_name: str = "router"):
    """Importa um modulo de forma segura, retornando None se falhar."""
    try:
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, router_name, None)
    except Exception as e:
        logger.warning(f"Modulo {module_path} nao carregado: {e}")
        return None


# =============================================================================
# MODULOS CORE (Alta prioridade)
# =============================================================================

# Auth - importacao direta sem passar pelo api/v1/__init__.py
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("auth", "/app/api/v1/endpoints/auth.py")
    auth_module = importlib.util.module_from_spec(spec)
    # Executar o modulo manualmente
    spec.loader.exec_module(auth_module)
    auth_router = auth_module.router
    api_router.include_router(auth_router)
    logger.info("Modulo Auth: OK")
except Exception as e:
    logger.warning(f"Modulo Auth: {e}")

# Users - gerenciamento de usuarios (admin)
try:
    spec = importlib.util.spec_from_file_location("users", "/app/api/v1/endpoints/users.py")
    users_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(users_module)
    users_router = users_module.router
    api_router.include_router(users_router)
    logger.info("Modulo Users: OK")
except Exception as e:
    logger.warning(f"Modulo Users: {e}")

# CRM
try:
    from modules.crm.controllers import (
        lead_router,
        opportunity_router,
        proposal_router,
        contract_router,
        commission_router,
        dashboard_router,
    )
    api_router.include_router(lead_router, prefix="/crm", tags=["CRM - Leads"])
    api_router.include_router(opportunity_router, prefix="/crm", tags=["CRM - Oportunidades"])
    api_router.include_router(proposal_router, prefix="/crm", tags=["CRM - Propostas"])
    api_router.include_router(contract_router, prefix="/crm", tags=["CRM - Contratos"])
    api_router.include_router(commission_router, prefix="/crm", tags=["CRM - Comissoes"])
    api_router.include_router(dashboard_router, prefix="/crm", tags=["CRM - Dashboard"])
    logger.info("Modulo CRM: OK")
except Exception as e:
    logger.warning(f"Modulo CRM: {e}")

# Operations
try:
    from modules.operacional.controllers import (
        post_router,
        scale_router,
        scale_template_router,
        shift_router,
        allocation_router,
        employee_router,
        substitution_router,
        time_bank_router,
        reports_router,
        kpi_trends_router,
    )
    # Routers já têm seu próprio prefix (/posts, /scales, etc)
    api_router.include_router(post_router, prefix="/operacional", tags=["Operacional - Postos"])
    api_router.include_router(scale_router, prefix="/operacional", tags=["Operacional - Escalas"])
    api_router.include_router(scale_template_router, prefix="/operacional", tags=["Operacional - Templates de Escalas"])
    api_router.include_router(shift_router, prefix="/operacional", tags=["Operacional - Turnos"])
    api_router.include_router(allocation_router, prefix="/operacional", tags=["Operacional - Alocacoes"])
    api_router.include_router(employee_router, prefix="/operacional", tags=["Operacional - Funcionarios"])
    api_router.include_router(substitution_router, prefix="/operacional", tags=["Operacional - Substituicoes"])
    api_router.include_router(time_bank_router, prefix="/operacional", tags=["Operacional - Banco de Horas"])
    api_router.include_router(reports_router, prefix="/operacional", tags=["Operacional - Relatorios"])
    api_router.include_router(kpi_trends_router, prefix="/operacional", tags=["Operacional - KPI Trends"])
    logger.info("Modulo Operations: OK")
except Exception as e:
    logger.warning(f"Modulo Operations: {e}")

# Operations - Occurrences (Ocorrencias Disciplinares)
try:
    from modules.operacional.occurrences import occurrence_router
    api_router.include_router(occurrence_router, prefix="/operacional", tags=["Operacional - Ocorrencias"])
    logger.info("Modulo Operations Occurrences: OK")
except Exception as e:
    logger.warning(f"Modulo Operations Occurrences: {e}")

# Financial (sem costing que tem dependencias)
try:
    from modules.financial.controllers import (
        accounting_router,
        supplier_router,
        payable_router,
        customer_router,
        receivable_category_router,
        receivable_router,
        billing_rule_router,
        bank_account_router,
        bank_transaction_router,
        bank_reconciliation_router,
        cashflow_router,
        purchase_router,
        inventory_router,
    )
    # Todos os routers já têm seu próprio prefix, então usamos apenas /financial
    api_router.include_router(accounting_router, prefix="/financial", tags=["Financial - Contabilidade"])
    api_router.include_router(supplier_router, prefix="/financial", tags=["Financial - Fornecedores"])
    api_router.include_router(payable_router, prefix="/financial", tags=["Financial - Contas a Pagar"])
    api_router.include_router(customer_router, prefix="/financial", tags=["Financial - Clientes"])
    api_router.include_router(receivable_category_router, prefix="/financial", tags=["Financial - Categorias"])
    api_router.include_router(receivable_router, prefix="/financial", tags=["Financial - Contas a Receber"])
    api_router.include_router(billing_rule_router, prefix="/financial", tags=["Financial - Regras de Cobranca"])
    api_router.include_router(bank_account_router, prefix="/financial", tags=["Financial - Contas Bancarias"])
    api_router.include_router(bank_transaction_router, prefix="/financial", tags=["Financial - Transacoes"])
    api_router.include_router(bank_reconciliation_router, prefix="/financial", tags=["Financial - Conciliacao"])
    api_router.include_router(cashflow_router, prefix="/financial", tags=["Financial - Fluxo de Caixa"])
    api_router.include_router(purchase_router, prefix="/financial", tags=["Financial - Compras"])
    api_router.include_router(inventory_router, prefix="/financial", tags=["Financial - Estoque"])
    logger.info("Modulo Financial: OK")
except Exception as e:
    logger.warning(f"Modulo Financial: {e}")

# Financial - BI Dashboard (60 endpoints - Sprint 30)
try:
    from modules.financial.bi_dashboard.controllers import router as bi_dashboard_router
    api_router.include_router(bi_dashboard_router, prefix="/financial", tags=["Financial - BI Dashboard"])
    logger.info("Modulo Financial BI Dashboard: OK")
except Exception as e:
    logger.warning(f"Modulo Financial BI Dashboard: {e}")

# Analytics - Executive Dashboard (7 endpoints - FASE 3)
try:
    from modules.analytics.controllers import executive_dashboard_router
    api_router.include_router(executive_dashboard_router, prefix="/analytics", tags=["Analytics - Executive Dashboard"])
    logger.info("Modulo Analytics Executive Dashboard: OK")
except Exception as e:
    logger.warning(f"Modulo Analytics Executive Dashboard: {e}")

# Analytics - Predictive Analytics (25 endpoints - Sprint 04)
try:
    from modules.analytics.controllers import analytics_router
    api_router.include_router(analytics_router, tags=["Analytics - Predictive"])
    logger.info("Modulo Analytics Predictive: OK")
except Exception as e:
    logger.warning(f"Modulo Analytics Predictive: {e}")

# GED
try:
    from modules.ged.controllers import (
        folder_router,
        document_router,
        version_router,
        share_router,
        tag_router,
        signature_router,
        stats_router,
    )
    # Routers já têm seu próprio prefix
    api_router.include_router(folder_router, prefix="/ged", tags=["GED - Pastas"])
    api_router.include_router(document_router, prefix="/ged", tags=["GED - Documentos"])
    api_router.include_router(version_router, prefix="/ged", tags=["GED - Versoes"])
    api_router.include_router(share_router, prefix="/ged", tags=["GED - Compartilhamentos"])
    api_router.include_router(tag_router, prefix="/ged", tags=["GED - Tags"])
    api_router.include_router(signature_router, prefix="/ged", tags=["GED - Assinaturas"])
    api_router.include_router(stats_router, prefix="/ged", tags=["GED - Estatísticas"])
    logger.info("Modulo GED: OK")
except Exception as e:
    logger.warning(f"Modulo GED: {e}")

# Clients
try:
    from modules.clients.controllers import router as client_router
    # Router já tem prefix="/clients"
    api_router.include_router(client_router, tags=["Clients - Cadastro"])
    logger.info("Modulo Clients: OK")
except Exception as e:
    logger.warning(f"Modulo Clients: {e}")

# Audit
try:
    from modules.audit.controllers import router as audit_router
    # Router já tem prefix="/audit"
    api_router.include_router(audit_router, tags=["Audit - Auditoria"])
    logger.info("Modulo Audit: OK")
except Exception as e:
    logger.warning(f"Modulo Audit: {e}")

# Config
try:
    from modules.config.controllers import router as config_router
    # Router já tem prefix="/config"
    api_router.include_router(config_router, tags=["Config - Configuracoes"])
    logger.info("Modulo Config: OK")
except Exception as e:
    logger.warning(f"Modulo Config: {e}")

# Reports
try:
    from modules.reports.controllers import router as report_router
    # Router já tem prefix="/reports"
    api_router.include_router(report_router, tags=["Reports - Relatorios"])
    logger.info("Modulo Reports: OK")
except Exception as e:
    logger.warning(f"Modulo Reports: {e}")

# Services
try:
    from modules.services.controllers import router as service_router
    # Router já tem prefix="/services"
    api_router.include_router(service_router, tags=["Services - Servicos"])
    logger.info("Modulo Services: OK")
except Exception as e:
    logger.warning(f"Modulo Services: {e}")

# Occurrences - REMOVIDO (Transferido para PLUS)
# Facilities - REMOVIDO (Transferido para PLUS)

# Equipment Management
try:
    from modules.equipment_management.controllers import (
        equipment_router,
        installation_router,
        maintenance_router as equipment_maintenance_router,
        comodato_router,
    )
    # Routers já têm prefixes próprios (/equipment, /installations, /maintenances, /comodatos)
    api_router.include_router(equipment_router, tags=["Equipment"])
    api_router.include_router(installation_router, tags=["Equipment - Instalacoes"])
    api_router.include_router(equipment_maintenance_router, tags=["Equipment - Manutencao"])
    api_router.include_router(comodato_router, tags=["Equipment - Comodato"])
    logger.info("Modulo Equipment: OK")
except Exception as e:
    logger.warning(f"Modulo Equipment: {e}")

# Integrations (Sprint 32: API Gateway + Sprint 33: Conectores Externos + Sólides)
try:
    from modules.integrations.controllers import integration_router, connector_router, solides_router
    api_router.include_router(integration_router, prefix="/integrations", tags=["Integrations - API Gateway"])
    api_router.include_router(connector_router, tags=["Integrations - Conectores"])
    api_router.include_router(solides_router, prefix="/integrations", tags=["Integrations - Sólides RH/DP"])
    logger.info("Modulo Integrations: OK")
except Exception as e:
    logger.warning(f"Modulo Integrations: {e}")

# Diarists
try:
    from modules.operacional.diaristas.controllers import router as diarist_router, fiscal_router as diarist_fiscal_router
    # Adicionado prefix /diaristas
    api_router.include_router(diarist_router, prefix="/operacional/diaristas", tags=["Operacional - Diaristas"])
    api_router.include_router(diarist_fiscal_router, prefix="/operacional/diaristas/fiscal", tags=["Operacional - Diaristas Fiscal"])
    logger.info("Modulo Diarists: OK")
    logger.info("Modulo Diarists Fiscal: OK")
except Exception as e:
    logger.warning(f"Modulo Diarists: {e}")

# Document Kits
try:
    from modules.document_kits.controllers import router as document_kit_router
    # Router já tem prefix="/document-kits"
    api_router.include_router(document_kit_router, tags=["Document Kits"])
    logger.info("Modulo Document Kits: OK")
except Exception as e:
    logger.warning(f"Modulo Document Kits: {e}")

# Document Kits - Operational Integration
try:
    from modules.document_kits.controllers.operational_controller import router as operational_router
    # Router já tem prefix="/document-kits-operational"
    api_router.include_router(operational_router)
    logger.info("Modulo Document Kits Operational: OK")
except Exception as e:
    logger.warning(f"Modulo Document Kits Operational: {e}")

# Government Integrations
try:
    from modules.government_integrations import government_integrations_router
    api_router.include_router(government_integrations_router, tags=["Government"])
    logger.info("Modulo Government: OK")
except Exception as e:
    logger.warning(f"Modulo Government: {e}")

# Monitoring
try:
    from modules.monitoring import router as monitoring_router
    api_router.include_router(monitoring_router, tags=["Monitoring"])
    logger.info("Modulo Monitoring: OK")
except Exception as e:
    logger.warning(f"Modulo Monitoring: {e}")

# Automation/Workflows
try:
    from modules.automation.workflow.controllers import router as workflow_router
    api_router.include_router(workflow_router, prefix="/workflows", tags=["Workflows"])
    logger.info("Modulo Workflows: OK")
except Exception as e:
    logger.warning(f"Modulo Workflows: {e}")

# CAMPO - Servico de Campo (OS, Visitas, Checklists)
try:
    from modules.campo import (
        ordem_servico_router,
        visita_router,
        checklist_router,
    )
    api_router.include_router(ordem_servico_router, prefix="/campo/os", tags=["Campo - Ordens de Servico"])
    api_router.include_router(visita_router, prefix="/campo/visitas", tags=["Campo - Visitas"])
    api_router.include_router(checklist_router, prefix="/campo/checklists", tags=["Campo - Checklists"])
    logger.info("Modulo Campo (OS/Visitas/Checklists): OK")
except Exception as e:
    logger.warning(f"Modulo Campo: {e}")

# REEMBOLSO - Reembolso de Despesas
try:
    from modules.reimbursement import reimbursement_router
    api_router.include_router(reimbursement_router, prefix="/reimbursements", tags=["Reimbursement - Reembolsos"])
    logger.info("Modulo Reimbursement: OK")
except Exception as e:
    logger.warning(f"Modulo Reimbursement: {e}")

# DISCIPLINARY - Medidas Administrativas (Advertencias, Suspensoes, Demissoes)
try:
    from modules.operacional.disciplinary import router as disciplinary_router
    api_router.include_router(disciplinary_router, prefix="/operacional", tags=["Operacional - Medidas Administrativas"])
    logger.info("Modulo Disciplinary: OK")
except Exception as e:
    logger.warning(f"Modulo Disciplinary: {e}")

# INSPECTION ROUNDS - Rondas de Inspecao
try:
    from modules.operacional.inspection_rounds import inspection_round_router
    api_router.include_router(inspection_round_router, prefix="/operacional/rondas", tags=["Operacional - Rondas de Inspecao"])
    logger.info("Modulo Inspection Rounds: OK")
except Exception as e:
    logger.warning(f"Modulo Inspection Rounds: {e}")

# COMMUNICATION - Comunicados, Notificacoes, Alertas
try:
    from modules.operacional.communication import communication_router
    api_router.include_router(communication_router, prefix="/operacional", tags=["Operacional - Comunicacao"])
    logger.info("Modulo Communication: OK")
except Exception as e:
    logger.warning(f"Modulo Communication: {e}")

# SEARCH - Busca Global
try:
    from modules.search import search_router
    api_router.include_router(search_router, tags=["Search - Busca Global"])
    logger.info("Modulo Search: OK")
except Exception as e:
    logger.warning(f"Modulo Search: {e}")

# BARTOLO - Assistente Inteligente IA
try:
    from modules.ai.bartolo.controllers import bartolo_router
    api_router.include_router(bartolo_router, prefix="/ai", tags=["AI - Bartolo Assistente"])
    logger.info("Modulo Bartolo: OK")
except Exception as e:
    logger.warning(f"Modulo Bartolo: {e}")

# RECRUITMENT - Recrutamento e Selecao
try:
    from modules.recruitment import router as recruitment_router
    api_router.include_router(recruitment_router, tags=["Recruitment - Recrutamento e Selecao"])
    logger.info("Modulo Recruitment: OK")
except Exception as e:
    logger.warning(f"Modulo Recruitment: {e}")

# NOTIFICATIONS - Notification Hub (Sprint 36, 37, 03)
try:
    from modules.notifications.controllers import router as notification_router
    from modules.notifications.controllers import intelligent_router as intelligent_notification_router
    from modules.notifications.push.controllers import router as push_notification_router

    api_router.include_router(notification_router, prefix="/notifications", tags=["Notifications - Hub"])
    api_router.include_router(intelligent_notification_router, prefix="/notifications/intelligent", tags=["Notifications - Intelligent"])
    api_router.include_router(push_notification_router, prefix="/notifications/push", tags=["Notifications - Push"])
    logger.info("Modulo Notifications: OK")
except Exception as e:
    logger.warning(f"Modulo Notifications: {e}")

# MOBILE - APIs Mobile Nativas (Sincronizacao Offline, Push Notifications)
try:
    from modules.mobile import mobile_router
    api_router.include_router(mobile_router, tags=["Mobile - API Nativa"])
    logger.info("Modulo Mobile: OK")
except Exception as e:
    logger.warning(f"Modulo Mobile: {e}")

# BIDDING - Licitacoes Publicas (Lei 14.133/2021, PNCP)
try:
    from modules.bidding import (
        tender_router,
        document_router as bidding_document_router,
        proposal_router as bidding_proposal_router,
        contract_router as bidding_contract_router,
        certificate_router,
    )
    api_router.include_router(tender_router, prefix="/bidding", tags=["Bidding - Editais"])
    api_router.include_router(bidding_document_router, prefix="/bidding", tags=["Bidding - Documentos"])
    api_router.include_router(bidding_proposal_router, prefix="/bidding", tags=["Bidding - Propostas"])
    api_router.include_router(bidding_contract_router, prefix="/bidding", tags=["Bidding - Contratos"])
    api_router.include_router(certificate_router, prefix="/bidding", tags=["Bidding - Certidoes"])
    logger.info("Modulo Bidding: OK")
except Exception as e:
    logger.warning(f"Modulo Bidding: {e}")


# Incluir router principal
app.include_router(api_router)

logger.info("=== API CONECTA PRO INICIADA ===")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_production:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
