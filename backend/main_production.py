"""
ERP Conecta Mais V2.0 - Producao (Modulos Core)
Versao otimizada que carrega apenas modulos estaveis.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

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

# GED
try:
    from modules.ged.controllers import (
        folder_router,
        document_router,
        version_router,
        share_router,
        tag_router,
        signature_router,
    )
    # Routers já têm seu próprio prefix
    api_router.include_router(folder_router, prefix="/ged", tags=["GED - Pastas"])
    api_router.include_router(document_router, prefix="/ged", tags=["GED - Documentos"])
    api_router.include_router(version_router, prefix="/ged", tags=["GED - Versoes"])
    api_router.include_router(share_router, prefix="/ged", tags=["GED - Compartilhamentos"])
    api_router.include_router(tag_router, prefix="/ged", tags=["GED - Tags"])
    api_router.include_router(signature_router, prefix="/ged", tags=["GED - Assinaturas"])
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
    from modules.operacional.diaristas.controllers import router as diarist_router
    # Router já tem prefix="/diarists"
    api_router.include_router(diarist_router, prefix="/operacional", tags=["Operacional - Diaristas"])
    logger.info("Modulo Diarists: OK")
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

# SEARCH - Busca Global
try:
    from modules.search import search_router
    api_router.include_router(search_router, tags=["Search - Busca Global"])
    logger.info("Modulo Search: OK")
except Exception as e:
    logger.warning(f"Modulo Search: {e}")


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
