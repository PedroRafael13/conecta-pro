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
