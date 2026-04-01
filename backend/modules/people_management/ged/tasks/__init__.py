"""
Celery tasks do modulo GED.

Tasks assincroas para montagem automatica de kits e sincronizacao de CNDs.
"""

from modules.people_management.ged.tasks.auto_collect_task import ged_auto_collect_documents
from modules.people_management.ged.tasks.cnd_sync_task import ged_sync_cnds

__all__ = [
    "ged_auto_collect_documents",
    "ged_sync_cnds",
]
