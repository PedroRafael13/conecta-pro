"""Celery Tasks - Módulo Financeiro.

Sync automático: bank_transactions → cashflow_entries
Executado a cada hora via Celery Beat.
"""

import logging

from celery_app import app

logger = logging.getLogger(__name__)


@app.task(
    name="financial.sync_cashflow_entries",
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
def sync_cashflow_entries_task(self):
    """Sincroniza bank_transactions pendentes → cashflow_entries.

    Executado a cada hora via Celery Beat.
    Idempotente: ON CONFLICT (bank_transaction_id) DO NOTHING.
    """
    try:
        from modules.financial.services.auto_sync_service import run_full_sync

        result = run_full_sync(limit=500)
        logger.info(
            "[Financial Task] sync_cashflow: pending=%s synced=%s errors=%s",
            result["pending"],
            result["synced"],
            result["errors"],
        )
        return result
    except Exception as exc:
        logger.error("[Financial Task] sync_cashflow error: %s", exc)
        raise self.retry(exc=exc)


# ═══════════════════════════════════════
# GEDEON LAYER 2 — Execução automática dos agentes financeiros
# ═══════════════════════════════════════


def _run_async(coro):
    """Helper para rodar corrotinas async nas tasks Celery."""
    import asyncio
    import os

    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://")

    async def _inner():
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            return await coro(session)

    return asyncio.run(_inner())


@app.task(name="gedeon.risk_monitor", bind=True, max_retries=3)
def gedeon_risk_monitor_task(self):
    """RiskMonitorAgent — executa a cada 5 minutos."""

    def run(session):
        from modules.financial.agents.gedeon_financial_orchestrator import GedeonFinancialOrchestrator

        orch = GedeonFinancialOrchestrator(db=session)
        return orch.run_risk_monitor()

    try:
        return _run_async(run)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@app.task(name="gedeon.daily_all", bind=True, max_retries=1)
def gedeon_daily_all_task(self):
    """Pipeline diário — todos os agentes (07:00)."""

    def run(session):
        from modules.financial.agents.gedeon_financial_orchestrator import GedeonFinancialOrchestrator

        orch = GedeonFinancialOrchestrator(db=session)
        return orch.run_all_daily()

    try:
        return _run_async(run)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@app.task(name="gedeon.cashflow_predictor", bind=True, max_retries=2)
def gedeon_cashflow_predictor_task(self):
    """CashflowPredictorAgent — diariamente às 07:00."""

    def run(session):
        from modules.financial.agents.gedeon_financial_orchestrator import GedeonFinancialOrchestrator

        orch = GedeonFinancialOrchestrator(db=session)
        return orch.run_cashflow_predictor()

    try:
        return _run_async(run)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@app.task(name="gedeon.collection_negotiator", bind=True, max_retries=2)
def gedeon_collection_negotiator_task(self):
    """CollectionNegotiatorAgent — diariamente às 09:00."""

    def run(session):
        from modules.financial.agents.gedeon_financial_orchestrator import GedeonFinancialOrchestrator

        orch = GedeonFinancialOrchestrator(db=session)
        return orch.run_collection_negotiator()

    try:
        return _run_async(run)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)
