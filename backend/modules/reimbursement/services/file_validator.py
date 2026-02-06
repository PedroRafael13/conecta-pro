"""
Serviço para validação de arquivos de anexo.

Implementa validações de tamanho, tipo e conteúdo de arquivos.
"""

from typing import Optional
from fastapi import HTTPException, status, UploadFile


class FileValidationError(Exception):
    """Erro de validação de arquivo."""
    pass


class FileValidator:
    """
    Validador de arquivos para anexos de reembolso.

    Valida tamanho máximo, tipos MIME permitidos e integridade básica.
    """

    # Tamanho máximo padrão: 10MB
    DEFAULT_MAX_SIZE = 10 * 1024 * 1024

    # Tipos MIME permitidos por padrão
    DEFAULT_ALLOWED_TYPES = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ]

    def __init__(
        self,
        max_size: int = DEFAULT_MAX_SIZE,
        allowed_types: Optional[list[str]] = None,
    ):
        """
        Inicializa o validador.

        Args:
            max_size: Tamanho máximo permitido em bytes (padrão: 10MB)
            allowed_types: Lista de tipos MIME permitidos (padrão: imagens, PDFs, docs)
        """
        self.max_size = max_size
        self.allowed_types = allowed_types or self.DEFAULT_ALLOWED_TYPES

    async def validate_size(self, content: bytes) -> None:
        """
        Valida tamanho do arquivo.

        Args:
            content: Conteúdo do arquivo em bytes

        Raises:
            HTTPException: Se arquivo exceder tamanho máximo
        """
        file_size = len(content)
        if file_size > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            current_mb = file_size / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Arquivo muito grande ({current_mb:.2f}MB). Máximo permitido: {max_mb:.0f}MB",
            )

    def validate_type(self, content_type: Optional[str]) -> None:
        """
        Valida tipo MIME do arquivo.

        Args:
            content_type: Tipo MIME do arquivo

        Raises:
            HTTPException: Se tipo não for permitido
        """
        if not content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de arquivo não identificado",
            )

        if content_type not in self.allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo não permitido: {content_type}. "
                       f"Tipos aceitos: imagens (JPEG, PNG, GIF, WebP), PDF, Word, Excel",
            )

    async def validate_file(self, file: UploadFile) -> bytes:
        """
        Valida arquivo completo (tamanho e tipo).

        Args:
            file: Arquivo enviado via FastAPI

        Returns:
            Conteúdo do arquivo em bytes

        Raises:
            HTTPException: Se validação falhar
        """
        # Ler conteúdo
        content = await file.read()

        # Validar tamanho
        await self.validate_size(content)

        # Validar tipo
        self.validate_type(file.content_type)

        # Voltar ao início do arquivo para reutilização
        await file.seek(0)

        return content

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Extrai extensão do arquivo.

        Args:
            filename: Nome do arquivo

        Returns:
            Extensão do arquivo (com ponto). Ex: ".pdf", ".jpg"
        """
        if "." in filename:
            return filename[filename.rfind("."):].lower()
        return ""

    @staticmethod
    def is_image(content_type: Optional[str]) -> bool:
        """
        Verifica se arquivo é uma imagem.

        Args:
            content_type: Tipo MIME do arquivo

        Returns:
            True se for imagem
        """
        if not content_type:
            return False
        return content_type.startswith("image/")

    @staticmethod
    def is_pdf(content_type: Optional[str]) -> bool:
        """
        Verifica se arquivo é um PDF.

        Args:
            content_type: Tipo MIME do arquivo

        Returns:
            True se for PDF
        """
        return content_type == "application/pdf"
