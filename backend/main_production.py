"""
ERP Conecta Mais V2.0 - Producao (Modulos Core)
Versao otimizada que carrega apenas modulos estaveis.
"""

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from core.config import settings
from core.logging import configure_logging, logger
from core.rate_limit import limiter

# =============================================================================
# SENTRY INITIALIZATION
# =============================================================================
if settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

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
else:
    if settings.environment == "production":
        logger.warning(
            "SENTRY_DSN nao configurado — erros de producao nao serao monitorados",
            action="sentry_missing",
        )


# =============================================================================
# SECURITY HEADERS MIDDLEWARE
# =============================================================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if "/api/" in request.url.path:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        return response


# Rate limiter importado de core.rate_limit (usa Redis, headers habilitados)


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


_is_production = settings.environment == "production"

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema ERP completo para gestao empresarial",
    docs_url=None if _is_production else "/docs",
    redoc_url=None if _is_production else "/redoc",
    openapi_url=None if _is_production else "/openapi.json",
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
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=500)
# ProxyHeaders: confia nos headers X-Forwarded-Proto/X-Forwarded-For do nginx
# para que redirects 307 usem https:// em vez de http://
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["127.0.0.1", "::1"])


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
    from sqlalchemy import text

    from core.cache import get_redis
    from core.database.session import async_session_factory

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
        status_code = 200
    elif "unhealthy" in statuses:
        overall = "unhealthy"
        status_code = 503
    else:
        overall = "degraded"
        status_code = 200

    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall,
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "checks": checks,
            "timestamp": time.time(),
        },
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Bem-vindo ao {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
    }


# =============================================================================
# API ROUTER - CARREGAMENTO VIA 9 MÓDULOS ORGANIZADOS
# Reorganização: 35 módulos → 9 módulos (2026-03-11)
# API URLs inalteradas — apenas imports reorganizados
# =============================================================================
from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# Auth - importacao direta (fora dos módulos)
try:
    import importlib.util

    spec = importlib.util.spec_from_file_location("auth", "/app/api/v1/endpoints/auth.py")
    auth_module = importlib.util.module_from_spec(spec)
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


# =============================================================================
# 1. COMERCIAL (crm + clients + bidding + services)
# =============================================================================
try:
    from modules.comercial import (
        bidding_agent_router,
        bidding_contract_router,
        bidding_document_router,
        bidding_erp_router,
        bidding_proposal_router,
        bidding_sync_router,
        bidding_tender_router,
        client_router,
        crm_commission_router,
        crm_contract_router,
        crm_dashboard_router,
        crm_lead_router,
        crm_opportunity_router,
        crm_proposal_router,
        service_router,
    )

    # CRM
    api_router.include_router(crm_lead_router, prefix="/crm", tags=["CRM - Leads"])
    api_router.include_router(crm_opportunity_router, prefix="/crm", tags=["CRM - Oportunidades"])
    api_router.include_router(crm_proposal_router, prefix="/crm", tags=["CRM - Propostas"])
    api_router.include_router(crm_contract_router, prefix="/crm", tags=["CRM - Contratos"])
    api_router.include_router(crm_commission_router, prefix="/crm", tags=["CRM - Comissoes"])
    api_router.include_router(crm_dashboard_router, prefix="/crm", tags=["CRM - Dashboard"])
    # Clients
    api_router.include_router(client_router, tags=["Clients - Cadastro"])
    # Bidding (Licitações — sem certidões, movidas para fiscal_contabil)
    api_router.include_router(bidding_tender_router, prefix="/bidding", tags=["Bidding - Editais"])
    api_router.include_router(bidding_document_router, prefix="/bidding", tags=["Bidding - Documentos"])
    api_router.include_router(bidding_proposal_router, prefix="/bidding", tags=["Bidding - Propostas"])
    api_router.include_router(bidding_contract_router, prefix="/bidding", tags=["Bidding - Contratos"])
    api_router.include_router(bidding_agent_router, prefix="/bidding", tags=["Bidding - AI Agents"])
    api_router.include_router(bidding_sync_router, prefix="/bidding", tags=["Bidding - Sincronizacao"])
    api_router.include_router(bidding_erp_router, prefix="/bidding", tags=["Bidding - Integracao ERP"])
    # Services
    api_router.include_router(service_router, tags=["Services - Servicos"])
    logger.info("Modulo Comercial: OK (CRM + Clients + Bidding + Services)")
except Exception as e:
    logger.warning(f"Modulo Comercial: {e}")


# =============================================================================
# 2. OPERAÇÕES (operacional + campo)
# =============================================================================
try:
    from modules.operacoes import (
        allocation_router,
        announcement_router,
        banco_horas_alias,
        checklist_router,
        communication_router,
        diarist_fiscal_router,
        diarist_router,
        disciplinary_router,
        employee_router,
        ferias_alias,
        inspection_round_router,
        kpi_trends_router,
        notification_router,
        occurrence_router,
        ocorrencias_alias,
        operacional_ai_router,
        operacional_dashboard_router,
        operacional_ws_router,
        ordem_servico_router,
        post_router,
        reports_router,
        scale_router,
        scale_template_router,
        scale_templates_alias,
        shift_router,
        substitution_router,
        time_bank_router,
        vacation_router,
        visita_router,
    )

    # Core
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
    api_router.include_router(occurrence_router, prefix="/operacional", tags=["Operacional - Ocorrencias"])
    # Diaristas
    api_router.include_router(diarist_router, prefix="/operacional/diaristas", tags=["Operacional - Diaristas"])
    api_router.include_router(
        diarist_fiscal_router, prefix="/operacional/diaristas/fiscal", tags=["Operacional - Diaristas Fiscal"]
    )
    # Disciplinary
    api_router.include_router(
        disciplinary_router, prefix="/operacional", tags=["Operacional - Medidas Administrativas"]
    )
    # Inspection Rounds
    api_router.include_router(
        inspection_round_router, prefix="/operacional/rondas", tags=["Operacional - Rondas de Inspecao"]
    )
    # Communication
    api_router.include_router(communication_router, prefix="/operacional", tags=["Operacional - Comunicacao"])
    # Vacations
    api_router.include_router(vacation_router, prefix="/operacional", tags=["Operacional - Férias"])
    # AI
    api_router.include_router(operacional_ai_router, prefix="/operacional", tags=["Operacional - AI"])
    # WebSocket
    api_router.include_router(operacional_ws_router, prefix="/operacional", tags=["Operacional - WebSocket"])
    # Campo
    api_router.include_router(ordem_servico_router, prefix="/campo/os", tags=["Campo - Ordens de Servico"])
    api_router.include_router(visita_router, prefix="/campo/visitas", tags=["Campo - Visitas"])
    api_router.include_router(checklist_router, prefix="/campo/checklists", tags=["Campo - Checklists"])
    # --- Dashboard operacional ---
    api_router.include_router(operacional_dashboard_router, prefix="/operacional", tags=["Operacional - Dashboard"])
    # --- Aliases PT-BR (frontend compatibility — redirects) ---
    api_router.include_router(banco_horas_alias, prefix="/operacional", tags=["Operacional - Banco Horas (alias)"])
    api_router.include_router(ocorrencias_alias, prefix="/operacional", tags=["Operacional - Ocorrencias (alias)"])
    api_router.include_router(ferias_alias, prefix="/operacional", tags=["Operacional - Ferias (alias)"])
    api_router.include_router(
        scale_templates_alias, prefix="/operacional", tags=["Operacional - Scale Templates (alias)"]
    )
    # --- Comunicados e Notificações (direto, sem /comunicacao/) ---
    api_router.include_router(announcement_router, prefix="/operacional", tags=["Operacional - Comunicados"])
    api_router.include_router(notification_router, prefix="/operacional", tags=["Operacional - Notificacoes"])
    logger.info("Modulo Operacoes: OK (Operacional + Campo)")
except Exception as e:
    logger.warning(f"Modulo Operacoes: {e}")


# =============================================================================
# 3. TÉCNICO (equipment + document_kits)
# =============================================================================
try:
    from modules.tecnico import (
        comodato_router,
        document_kit_router,
        equipment_maintenance_router,
        equipment_router,
        installation_router,
    )

    api_router.include_router(equipment_router, tags=["Equipment"])
    api_router.include_router(installation_router, tags=["Equipment - Instalacoes"])
    api_router.include_router(equipment_maintenance_router, tags=["Equipment - Manutencao"])
    api_router.include_router(comodato_router, tags=["Equipment - Comodato"])
    api_router.include_router(document_kit_router, tags=["Document Kits"])
    logger.info("Modulo Tecnico: OK (Equipment + Document Kits)")
except Exception as e:
    logger.warning(f"Modulo Tecnico: {e}")

# Document Kits - Operational Integration (carregamento separado por dependência apscheduler)
try:
    from modules.document_kits.controllers.operational_controller import router as operational_router

    api_router.include_router(operational_router)
    logger.info("Modulo Document Kits Operational: OK")
except Exception as e:
    logger.warning(f"Modulo Document Kits Operational: {e}")


# =============================================================================
# 4. PESSOAS (recruitment + retention + reimbursement + ged)
# =============================================================================
try:
    from modules.pessoas import (
        climate_router,
        ged_document_router,
        ged_folder_router,
        ged_share_router,
        ged_signature_router,
        ged_stats_router,
        ged_tag_router,
        ged_version_router,
        onboarding_router,
        profile_router,
        recruitment_router,
        reimbursement_router,
        turnover_router,
    )

    # Recruitment
    api_router.include_router(recruitment_router, tags=["Recruitment - Recrutamento e Selecao"])
    # Retention
    api_router.include_router(onboarding_router, tags=["Retention - Onboarding"])
    api_router.include_router(profile_router, tags=["Retention - Operational Profile"])
    api_router.include_router(climate_router, tags=["Retention - Climate Survey"])
    api_router.include_router(turnover_router, tags=["Retention - Turnover Prediction"])
    # Reimbursement
    api_router.include_router(reimbursement_router, prefix="/reimbursements", tags=["Reimbursement - Reembolsos"])
    # GED
    api_router.include_router(ged_folder_router, prefix="/ged", tags=["GED - Pastas"])
    api_router.include_router(ged_document_router, prefix="/ged", tags=["GED - Documentos"])
    api_router.include_router(ged_version_router, prefix="/ged", tags=["GED - Versoes"])
    api_router.include_router(ged_share_router, prefix="/ged", tags=["GED - Compartilhamentos"])
    api_router.include_router(ged_tag_router, prefix="/ged", tags=["GED - Tags"])
    api_router.include_router(ged_signature_router, prefix="/ged", tags=["GED - Assinaturas"])
    api_router.include_router(ged_stats_router, prefix="/ged", tags=["GED - Estatísticas"])
    try:
        from modules.ged.controllers.ged_integration_controller import router as ged_integration_router

        api_router.include_router(ged_integration_router, prefix="/ged", tags=["GED - Integracao"])
    except ImportError:
        logger.warning("Modulo GED Integration: falha ao importar (ImportError)")
    logger.info("Modulo Pessoas: OK (Recruitment + Retention + Reimbursement + GED + Integracao)")
except Exception as e:
    logger.warning(f"Modulo Pessoas: {e}")


# =============================================================================
# 5. FINANCEIRO (financial completo)
# =============================================================================
try:
    from modules.financeiro import (
        accounting_router,
        bank_account_router,
        bank_reconciliation_router,
        bank_transaction_router,
        bi_dashboard_router,
        billing_rule_router,
        cashflow_router,
        customer_router,
        financial_ai_router,
        fiscal_router,
        inventory_router,
        payable_router,
        purchase_router,
        receivable_category_router,
        receivable_router,
        relatorios_router,
        supplier_router,
    )

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
    api_router.include_router(fiscal_router, prefix="/financial", tags=["Financial - Fiscal/Tributário"])
    api_router.include_router(financial_ai_router, prefix="/financial", tags=["Financial AI"])
    api_router.include_router(relatorios_router, prefix="/financial", tags=["Financial - Relatórios"])
    api_router.include_router(bi_dashboard_router, prefix="/financial", tags=["Financial - BI Dashboard"])
    logger.info("Modulo Financeiro: OK (17 routers)")
except Exception as e:
    logger.warning(f"Modulo Financeiro: {e}")


# =============================================================================
# 6. FISCAL/CONTÁBIL (empresas + fiscal + government)
# =============================================================================
try:
    from modules.fiscal_contabil import (
        bidding_certificate_router,
        bookkeeper_router,
        dominio_router,
        empresas_dashboard_router,
        empresas_router,
        government_integrations_router,
        migrador_router,
        nfse_multi_router,
        obrigacoes_router,
        statements_router,
    )

    # Empresas Multi-CNPJ
    api_router.include_router(empresas_router, tags=["Empresas - Multi-CNPJ"])
    api_router.include_router(migrador_router, prefix="/empresas", tags=["Migrador de Contratos"])
    api_router.include_router(obrigacoes_router, prefix="/empresas", tags=["Obrigações Multi-Empresa"])
    api_router.include_router(empresas_dashboard_router, prefix="/empresas", tags=["Dashboard Multi-Empresa"])
    api_router.include_router(dominio_router, tags=["Domínio TOTVS"])
    api_router.include_router(bookkeeper_router, tags=["Escrituração Contábil"])
    api_router.include_router(statements_router, tags=["Demonstrativos Financeiros"])
    # Fiscal
    api_router.include_router(nfse_multi_router, prefix="/fiscal", tags=["Fiscal - NFS-e Multi-Empresa"])
    # Government
    api_router.include_router(government_integrations_router, tags=["Government"])
    # Certidões (CNDs) — movido de comercial/bidding
    api_router.include_router(bidding_certificate_router, prefix="/bidding", tags=["Certidões - CNDs"])
    logger.info("Modulo Fiscal/Contabil: OK (Empresas + Fiscal + Government + Certidoes)")
except Exception as e:
    logger.warning(f"Modulo Fiscal/Contabil: {e}")


# =============================================================================
# 7. INTELIGÊNCIA (ai/bartolo + analytics + reports + monitoring + search)
# =============================================================================
try:
    from modules.inteligencia import (
        analytics_router,
        bartolo_router,
        executive_dashboard_router,
        monitoring_router,
        report_router,
    )

    api_router.include_router(bartolo_router, prefix="/ai", tags=["AI - Bartolo Assistente"])
    api_router.include_router(executive_dashboard_router, prefix="/analytics", tags=["Analytics - Executive Dashboard"])
    api_router.include_router(analytics_router, tags=["Analytics - Predictive"])
    api_router.include_router(report_router, tags=["Reports - Relatorios"])
    api_router.include_router(monitoring_router, tags=["Monitoring"])
    logger.info("Modulo Inteligencia: OK (AI + Analytics + Reports + Monitoring + Search)")
except Exception as e:
    logger.warning(f"Modulo Inteligencia: {e}")


# =============================================================================
# 8. GESTÃO (config + audit + notifications + mobile + workflows + integrations)
# =============================================================================
try:
    from modules.gestao import (
        audit_router,
        banking_router,
        config_router,
        connector_router,
        integration_router,
        intelligent_notification_router,
        mobile_router,
        notification_router,
        push_notification_router,
        solides_router,
        workflow_router,
    )

    # Config
    api_router.include_router(config_router, tags=["Config - Configuracoes"])
    # Audit
    api_router.include_router(audit_router, tags=["Audit - Auditoria"])
    # Notifications
    api_router.include_router(notification_router, prefix="", tags=["Notifications - Hub"])
    api_router.include_router(
        intelligent_notification_router, prefix="/notifications", tags=["Notifications - Intelligent"]
    )
    api_router.include_router(push_notification_router, prefix="/notifications", tags=["Notifications - Push"])
    # Mobile
    api_router.include_router(mobile_router, tags=["Mobile - API Nativa"])
    # Workflows
    api_router.include_router(workflow_router, prefix="/workflows", tags=["Workflows"])
    # Integrations
    api_router.include_router(integration_router, prefix="/integrations", tags=["Integrations - API Gateway"])
    api_router.include_router(connector_router, tags=["Integrations - Conectores"])
    api_router.include_router(solides_router, prefix="/integrations", tags=["Integrations - Sólides RH/DP"])
    api_router.include_router(banking_router, prefix="/integrations", tags=["Integrations - Banking"])
    logger.info("Modulo Gestao: OK (Config + Audit + Notifications + Mobile + Workflows + Integrations)")
except Exception as e:
    logger.warning(f"Modulo Gestao: {e}")


# 9. CADASTROS - reservado para dados mestres (módulo futuro)
# Importações serão adicionadas conforme refatoração avançar


# =============================================================================
# 10. GESTÃO DE PESSOAS (people_management: DP + RH + Operations + Portal)
# =============================================================================
try:
    from modules.people_management import router as people_management_router

    api_router.include_router(people_management_router)
    logger.info("Modulo People Management: OK (DP + RH + Operations + Portal + GED)")
except Exception as e:
    logger.warning(f"Modulo People Management: {e}")


# =============================================================================
# 11. AREA DO CLIENTE (client_portal: Auth + Kits + Chamados)
# =============================================================================
try:
    from modules.client_portal import router as client_portal_router

    api_router.include_router(client_portal_router)
    logger.info("Modulo Client Portal: OK (Auth + Kits + Tickets)")
except Exception as e:
    logger.warning(f"Modulo Client Portal: {e}")


# =============================================================================
# 12. CCT 2026 — SINDECOMPRESTS/SINDICOND-AM
# =============================================================================
try:
    from modules.cct import router as cct_router

    api_router.include_router(cct_router)
    logger.info("Modulo CCT 2026: OK (Salarios + Beneficios + Jornadas + Compliance + Rescisao + Feriados)")
except Exception as e:
    logger.warning(f"Modulo CCT 2026: {e}")


# Incluir router principal
app.include_router(api_router)

logger.info("=== API CONECTA PRO INICIADA (11 módulos) ===")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_production:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
