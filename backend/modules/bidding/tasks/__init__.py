"""
Tasks Celery do modulo Bidding (Licitacoes).
=============================================

Re-exporta todas as tasks dos sub-modulos para manter compatibilidade
com imports existentes (celery_app.py include="modules.bidding.tasks").
"""

from modules.bidding.tasks.dispute_tasks import *  # noqa: F401, F403
from modules.bidding.tasks.notification_tasks import *  # noqa: F401, F403
from modules.bidding.tasks.sync_tasks import *  # noqa: F401, F403
