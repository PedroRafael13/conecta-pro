"""Service para OccurrenceAttachment."""

import logging
import os
import uuid as uuid_module
from typing import Optional
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from modules.occurrences.models.attachment import AttachmentType
from modules.occurrences.repositories.attachment_repository import AttachmentRepository
from modules.occurrences.repositories.occurrence_repository import OccurrenceRepository
from modules.occurrences.schemas.attachment import (
    AttachmentCreate,
    AttachmentListResponse,
    AttachmentResponse,
)

logger = logging.getLogger(__name__)

# Configuracoes de upload
UPLOAD_DIR = "/opt/erp-conecta-mais/uploads/occurrences"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
    "video": [".mp4", ".avi", ".mov", ".wmv", ".webm"],
    "audio": [".mp3", ".wav", ".ogg", ".m4a"],
    "document": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv"],
    "spreadsheet": [".xls", ".xlsx", ".csv", ".ods"],
    "presentation": [".ppt", ".pptx", ".odp"],
    "archive": [".zip", ".rar", ".7z", ".tar", ".gz"],
}


class AttachmentService:
    """Service para operacoes de OccurrenceAttachment."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = AttachmentRepository(session)
        self.occurrence_repository = OccurrenceRepository(session)

    def _get_file_type(self, filename: str) -> AttachmentType:
        """Determina o tipo do arquivo pela extensao."""
        ext = os.path.splitext(filename)[1].lower()

        for file_type, extensions in ALLOWED_EXTENSIONS.items():
            if ext in extensions:
                return AttachmentType(file_type)

        return AttachmentType.OTHER

    def _validate_file(self, filename: str, file_size: int) -> None:
        """Valida arquivo para upload."""
        # Verifica tamanho
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"Arquivo muito grande. Maximo: {MAX_FILE_SIZE / 1024 / 1024}MB")

        # Verifica extensao
        ext = os.path.splitext(filename)[1].lower()
        all_extensions = []
        for extensions in ALLOWED_EXTENSIONS.values():
            all_extensions.extend(extensions)

        if ext not in all_extensions:
            raise ValueError(f"Tipo de arquivo nao permitido: {ext}")

    async def create(self, data: AttachmentCreate) -> AttachmentResponse:
        """Cria um novo anexo."""
        # Verificar se ocorrencia existe
        occurrence = await self.occurrence_repository.get_by_id(data.occurrence_id)
        if not occurrence:
            raise ValueError(f"Ocorrencia {data.occurrence_id} nao encontrada")

        attachment = await self.repository.create(data)
        await self.session.commit()
        await self.session.refresh(attachment)
        return AttachmentResponse.model_validate(attachment)

    async def upload_file(
        self,
        occurrence_id: UUID,
        file: UploadFile,
        uploaded_by_id: str,
        uploaded_by_name: str,
        description: Optional[str] = None,
        is_public: bool = True,
    ) -> AttachmentResponse:
        """Faz upload de arquivo e cria anexo."""
        # Verificar se ocorrencia existe
        occurrence = await self.occurrence_repository.get_by_id(occurrence_id)
        if not occurrence:
            raise ValueError(f"Ocorrencia {occurrence_id} nao encontrada")

        # Ler conteudo do arquivo
        content = await file.read()
        file_size = len(content)

        # Validar arquivo
        self._validate_file(file.filename, file_size)

        # Gerar nome unico
        ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid_module.uuid4()}{ext}"

        # Criar diretorio se nao existir
        occurrence_dir = os.path.join(UPLOAD_DIR, str(occurrence_id))
        os.makedirs(occurrence_dir, exist_ok=True)

        # Salvar arquivo
        file_path = os.path.join(occurrence_dir, unique_filename)
        with open(file_path, "wb") as f:
            f.write(content)

        # Determinar tipo
        file_type = self._get_file_type(file.filename)

        # Criar anexo
        data = AttachmentCreate(
            occurrence_id=occurrence_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_url=f"/uploads/occurrences/{occurrence_id}/{unique_filename}",
            file_type=file_type,
            mime_type=file.content_type,
            file_size=file_size,
            uploaded_by_id=uploaded_by_id,
            uploaded_by_name=uploaded_by_name,
            description=description,
            is_public=is_public,
        )

        return await self.create(data)

    async def get_by_id(self, attachment_id: str | UUID) -> Optional[AttachmentResponse]:
        """Busca anexo por ID."""
        attachment = await self.repository.get_by_id(attachment_id)
        if not attachment:
            return None
        return AttachmentResponse.model_validate(attachment)

    async def delete(self, attachment_id: str | UUID) -> bool:
        """Deleta um anexo."""
        # Buscar anexo
        attachment = await self.repository.get_by_id(attachment_id)
        if not attachment:
            return False

        # Deletar arquivo fisico se existir
        if attachment.file_path and os.path.exists(attachment.file_path):
            try:
                os.remove(attachment.file_path)
            except OSError as e:
                logger.warning(f"Erro ao deletar arquivo fisico: {e}")

        # Deletar registro
        result = await self.repository.delete(attachment_id)
        if result:
            await self.session.commit()
        return result

    async def list_by_occurrence(
        self,
        occurrence_id: str | UUID,
        attachment_type: Optional[AttachmentType] = None,
        is_public: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> AttachmentListResponse:
        """Lista anexos de uma ocorrencia."""
        skip = (page - 1) * page_size
        attachments, total = await self.repository.list_by_occurrence(
            occurrence_id, attachment_type, is_public, skip, page_size
        )

        items = [AttachmentResponse.model_validate(a) for a in attachments]
        return AttachmentListResponse(items=items, total=total, page=page, page_size=page_size)

    async def list_images(self, occurrence_id: str | UUID) -> list[AttachmentResponse]:
        """Lista imagens de uma ocorrencia."""
        attachments = await self.repository.list_images(occurrence_id)
        return [AttachmentResponse.model_validate(a) for a in attachments]

    async def list_documents(self, occurrence_id: str | UUID) -> list[AttachmentResponse]:
        """Lista documentos de uma ocorrencia."""
        attachments = await self.repository.list_documents(occurrence_id)
        return [AttachmentResponse.model_validate(a) for a in attachments]

    async def list_media(self, occurrence_id: str | UUID) -> list[AttachmentResponse]:
        """Lista videos e audios de uma ocorrencia."""
        attachments = await self.repository.list_media(occurrence_id)
        return [AttachmentResponse.model_validate(a) for a in attachments]

    async def get_stats_by_type(self, occurrence_id: str | UUID) -> dict:
        """Retorna estatisticas de anexos por tipo."""
        return await self.repository.get_stats_by_type(occurrence_id)

    async def toggle_public(self, attachment_id: str | UUID) -> Optional[AttachmentResponse]:
        """Alterna visibilidade publica do anexo."""
        attachment = await self.repository.get_by_id(attachment_id)
        if not attachment:
            return None

        attachment.is_public = not attachment.is_public
        await self.session.commit()
        return AttachmentResponse.model_validate(attachment)
