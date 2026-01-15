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
    api_router.include_router(lead_router)
    api_router.include_router(opportunity_router)
    api_router.include_router(proposal_router)
    api_router.include_router(contract_router)
    api_router.include_router(commission_router)
    api_router.include_router(dashboard_router)
    logger.info("Modulo CRM: OK")
except Exception as e:
    logger.warning(f"Modulo CRM: {e}")

# Operations
try:
    from modules.operacional.controllers import (
        post_router,
        scale_router,
        shift_router,
        allocation_router,
        substitution_router,
        time_bank_router,
    )
    api_router.include_router(post_router, prefix="/operacional/posts", tags=["Operacional - Postos"])
    api_router.include_router(scale_router, prefix="/operacional/scales", tags=["Operacional - Escalas"])
    api_router.include_router(shift_router, prefix="/operacional/shifts", tags=["Operacional - Turnos"])
    api_router.include_router(allocation_router, prefix="/operacional/allocations", tags=["Operacional - Alocacoes"])
    api_router.include_router(substitution_router, prefix="/operacional/substitutions", tags=["Operacional - Substituicoes"])
    api_router.include_router(time_bank_router, prefix="/operacional/time-bank", tags=["Operacional - Banco de Horas"])
    logger.info("Modulo Operations: OK")
except Exception as e:
    logger.warning(f"Modulo Operations: {e}")

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
    api_router.include_router(accounting_router, prefix="/financial/accounting", tags=["Financial - Contabilidade"])
    api_router.include_router(supplier_router, prefix="/financial/suppliers", tags=["Financial - Fornecedores"])
    api_router.include_router(payable_router, prefix="/financial/payables", tags=["Financial - Contas a Pagar"])
    api_router.include_router(customer_router, prefix="/financial/customers", tags=["Financial - Clientes"])
    api_router.include_router(receivable_category_router, prefix="/financial/receivable-categories", tags=["Financial - Categorias"])
    api_router.include_router(receivable_router, prefix="/financial/receivables", tags=["Financial - Contas a Receber"])
    api_router.include_router(billing_rule_router, prefix="/financial/billing-rules", tags=["Financial - Regras de Cobranca"])
    api_router.include_router(bank_account_router, prefix="/financial/bank-accounts", tags=["Financial - Contas Bancarias"])
    api_router.include_router(bank_transaction_router, prefix="/financial/bank-transactions", tags=["Financial - Transacoes"])
    api_router.include_router(bank_reconciliation_router, prefix="/financial/bank-reconciliation", tags=["Financial - Conciliacao"])
    api_router.include_router(cashflow_router, prefix="/financial/cashflow", tags=["Financial - Fluxo de Caixa"])
    api_router.include_router(purchase_router, prefix="/financial/purchases", tags=["Financial - Compras"])
    api_router.include_router(inventory_router, prefix="/financial/inventory", tags=["Financial - Estoque"])
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
    api_router.include_router(folder_router, prefix="/ged/folders", tags=["GED - Pastas"])
    api_router.include_router(document_router, prefix="/ged/documents", tags=["GED - Documentos"])
    api_router.include_router(version_router, prefix="/ged/versions", tags=["GED - Versoes"])
    api_router.include_router(share_router, prefix="/ged/shares", tags=["GED - Compartilhamentos"])
    api_router.include_router(tag_router, prefix="/ged/tags", tags=["GED - Tags"])
    api_router.include_router(signature_router, prefix="/ged/signatures", tags=["GED - Assinaturas"])
    logger.info("Modulo GED: OK")
except Exception as e:
    logger.warning(f"Modulo GED: {e}")

# Clients
try:
    from modules.clients.controllers import router as client_router
    api_router.include_router(client_router, prefix="/clients", tags=["Clients - Cadastro"])
    logger.info("Modulo Clients: OK")
except Exception as e:
    logger.warning(f"Modulo Clients: {e}")

# Audit
try:
    from modules.audit.controllers import router as audit_router
    api_router.include_router(audit_router, prefix="/audit", tags=["Audit - Auditoria"])
    logger.info("Modulo Audit: OK")
except Exception as e:
    logger.warning(f"Modulo Audit: {e}")

# Config
try:
    from modules.config.controllers import router as config_router
    api_router.include_router(config_router, prefix="/config", tags=["Config - Configuracoes"])
    logger.info("Modulo Config: OK")
except Exception as e:
    logger.warning(f"Modulo Config: {e}")

# Reports
try:
    from modules.reports.controllers import router as report_router
    api_router.include_router(report_router, prefix="/reports", tags=["Reports - Relatorios"])
    logger.info("Modulo Reports: OK")
except Exception as e:
    logger.warning(f"Modulo Reports: {e}")

# Services
try:
    from modules.services.controllers import router as service_router
    api_router.include_router(service_router, prefix="/services", tags=["Services - Servicos"])
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
    api_router.include_router(equipment_router, prefix="/equipment", tags=["Equipment"])
    api_router.include_router(installation_router, prefix="/equipment/installations", tags=["Equipment - Instalacoes"])
    api_router.include_router(equipment_maintenance_router, prefix="/equipment/maintenance", tags=["Equipment - Manutencao"])
    api_router.include_router(comodato_router, prefix="/equipment/comodato", tags=["Equipment - Comodato"])
    logger.info("Modulo Equipment: OK")
except Exception as e:
    logger.warning(f"Modulo Equipment: {e}")

# Integrations (Sprint 32: API Gateway + Sprint 33: Conectores Externos)
try:
    from modules.integrations.controllers import integration_router, connector_router
    api_router.include_router(integration_router, prefix="/integrations", tags=["Integrations - API Gateway"])
    api_router.include_router(connector_router, tags=["Integrations - Conectores"])
    logger.info("Modulo Integrations: OK")
except Exception as e:
    logger.warning(f"Modulo Integrations: {e}")

# Diarists
try:
    from modules.operacional.diaristas.controllers import router as diarist_router
    api_router.include_router(diarist_router, prefix="/operacional/diaristas", tags=["Operacional - Diaristas"])
    logger.info("Modulo Diarists: OK")
except Exception as e:
    logger.warning(f"Modulo Diarists: {e}")

# Document Kits
try:
    from modules.document_kits.controllers import router as document_kit_router
    api_router.include_router(document_kit_router, prefix="/document-kits", tags=["Document Kits"])
    logger.info("Modulo Document Kits: OK")
except Exception as e:
    logger.warning(f"Modulo Document Kits: {e}")

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
