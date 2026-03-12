"""
Serviço de Documentos — Departamento Pessoal.

Re-exporta funcionalidades do módulo GED (Gestão Eletrônica de Documentos).
"""

import logging

logger = logging.getLogger(__name__)

# Re-export do serviço existente
try:
    from modules.ged.services.document_service import DocumentService
except ImportError:
    try:
        from modules.ged.services import DocumentService
    except ImportError:
        logger.info("Módulo GED não disponível para re-export")

        class DocumentService:  # type: ignore[no-redef]
            """Stub para quando o módulo GED não está disponível."""

            def __init__(self, db=None):
                self.db = db

            async def list_documents(self, **kwargs):
                """Lista documentos (stub)."""
                return {"items": [], "total": 0, "message": "Módulo GED não disponível"}

            async def get_document(self, document_id, **kwargs):
                """Busca documento por ID (stub)."""
                return None


__all__ = ["DocumentService"]
