"""
Validador de arquivos para upload seguro.

Implementa validações de:
- Tamanho máximo
- Tipos MIME permitidos (whitelist)
- Magic numbers (file signatures) para verificação real do tipo
"""

import logging

from fastapi import HTTPException, UploadFile, status

logger = logging.getLogger(__name__)


class FileValidationError(Exception):
    """Erro de validação de arquivo."""


# Magic numbers (file signatures) por tipo MIME
MAGIC_NUMBERS: dict[str, list[bytes]] = {
    "application/pdf": [b"%PDF"],
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG"],
    "image/gif": [b"GIF87a", b"GIF89a"],
    "image/webp": [b"RIFF"],  # RIFF....WEBP
    "image/tiff": [b"II\x2a\x00", b"MM\x00\x2a"],
    "image/bmp": [b"BM"],
    # Office docs (ZIP-based)
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [b"PK\x03\x04"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [b"PK\x03\x04"],
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": [b"PK\x03\x04"],
    # Legacy Office
    "application/msword": [b"\xd0\xcf\x11\xe0"],
    "application/vnd.ms-excel": [b"\xd0\xcf\x11\xe0"],
}


class FileValidator:
    """
    Validador de arquivos com verificação de magic numbers.

    Uso:
        validator = FileValidator(max_size_mb=50, allowed_types=[...])
        content = await validator.validate_file(file)
    """

    def __init__(
        self,
        max_size_mb: int = 10,
        allowed_types: list[str] | None = None,
    ):
        self.max_size = max_size_mb * 1024 * 1024
        self.allowed_types = allowed_types or list(MAGIC_NUMBERS.keys())

    def validate_magic_number(self, content: bytes, content_type: str) -> bool:
        """
        Verifica se os bytes iniciais do arquivo correspondem ao tipo declarado.

        Args:
            content: Conteúdo do arquivo em bytes
            content_type: Tipo MIME declarado

        Returns:
            True se magic number corresponde ou tipo não tem magic number definido
        """
        signatures = MAGIC_NUMBERS.get(content_type)
        if not signatures:
            return True  # Tipo sem magic number conhecido

        return any(content[: len(sig)] == sig for sig in signatures)

    def validate_type(self, content_type: str | None) -> None:
        """Valida se tipo MIME está na whitelist."""
        if not content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de arquivo não identificado",
            )
        if content_type not in self.allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo não permitido: {content_type}",
            )

    async def validate_size(self, content: bytes) -> None:
        """Valida se o tamanho do arquivo está dentro do limite."""
        if len(content) > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            current_mb = len(content) / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Arquivo muito grande ({current_mb:.2f}MB). Máximo: {max_mb:.0f}MB",
            )

    async def validate_file(self, file: UploadFile) -> bytes:
        """
        Valida arquivo completo: tamanho, tipo MIME e magic number.

        Args:
            file: Arquivo enviado via FastAPI

        Returns:
            Conteúdo do arquivo em bytes

        Raises:
            HTTPException: Se qualquer validação falhar
        """
        content = await file.read()

        await self.validate_size(content)
        self.validate_type(file.content_type)

        if not self.validate_magic_number(content, file.content_type or ""):
            logger.warning(
                "Magic number mismatch: arquivo=%s, tipo_declarado=%s",
                file.filename,
                file.content_type,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conteúdo do arquivo não corresponde ao tipo declarado",
            )

        await file.seek(0)
        return content

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Extrai extensão do arquivo."""
        if "." in filename:
            return filename[filename.rfind(".") :].lower()
        return ""

    @staticmethod
    def is_image(content_type: str | None) -> bool:
        """Verifica se arquivo é uma imagem."""
        return bool(content_type and content_type.startswith("image/"))

    @staticmethod
    def is_pdf(content_type: str | None) -> bool:
        """Verifica se arquivo é um PDF."""
        return content_type == "application/pdf"


# Instâncias pré-configuradas por módulo

# GED: PDFs, imagens, Office docs - max 50MB
GED_ALLOWED_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/tiff",
    "image/bmp",
    "application/msword",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
]
ged_file_validator = FileValidator(max_size_mb=50, allowed_types=GED_ALLOWED_TYPES)

# OCR: PDFs e imagens - max 20MB
OCR_ALLOWED_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "image/bmp",
]
ocr_file_validator = FileValidator(max_size_mb=20, allowed_types=OCR_ALLOWED_TYPES)
