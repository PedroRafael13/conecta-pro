"""SST Tasks — Celery tasks para automacao SST."""

from .afastamento_tasks import verificar_afastamentos_vencidos, verificar_inss_pendente

__all__ = ["verificar_afastamentos_vencidos", "verificar_inss_pendente"]
