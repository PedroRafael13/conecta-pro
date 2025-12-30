"""Controllers do módulo GED (Gestão Eletrônica de Documentos)."""

from modules.ged.controllers.folder_controller import router as folder_router
from modules.ged.controllers.document_controller import router as document_router
from modules.ged.controllers.document_version_controller import (
    router as version_router,
)
from modules.ged.controllers.document_share_controller import router as share_router
from modules.ged.controllers.document_tag_controller import router as tag_router
from modules.ged.controllers.document_signature_controller import (
    router as signature_router,
)


__all__ = [
    "folder_router",
    "document_router",
    "version_router",
    "share_router",
    "tag_router",
    "signature_router",
]
