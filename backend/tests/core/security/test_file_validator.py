"""Testes para o validador de arquivos."""

import io
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.security.file_validator import FileValidationError, FileValidator


def make_upload_file(content: bytes, content_type: str, filename: str = "test.pdf"):
    """Cria um mock de UploadFile."""
    file = AsyncMock()
    file.read = AsyncMock(return_value=content)
    file.seek = AsyncMock()
    file.content_type = content_type
    file.filename = filename
    return file


class TestFileValidator:
    """Testes para FileValidator."""

    def setup_method(self):
        self.validator = FileValidator(
            max_size_mb=10,
            allowed_types=["application/pdf", "image/jpeg", "image/png"],
        )

    @pytest.mark.asyncio
    async def test_arquivo_valido_pdf(self):
        """PDF válido com magic number correto deve ser aceito."""
        content = b"%PDF-1.4 fake pdf content" + b"\x00" * 100
        file = make_upload_file(content, "application/pdf", "doc.pdf")

        result = await self.validator.validate_file(file)
        assert result == content

    @pytest.mark.asyncio
    async def test_arquivo_valido_jpeg(self):
        """JPEG válido com magic number correto deve ser aceito."""
        content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        file = make_upload_file(content, "image/jpeg", "photo.jpg")

        result = await self.validator.validate_file(file)
        assert result == content

    @pytest.mark.asyncio
    async def test_arquivo_valido_png(self):
        """PNG válido com magic number correto deve ser aceito."""
        content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        file = make_upload_file(content, "image/png", "image.png")

        result = await self.validator.validate_file(file)
        assert result == content

    @pytest.mark.asyncio
    async def test_tipo_nao_permitido(self):
        """Tipo MIME não na whitelist deve ser rejeitado."""
        content = b"fake executable content"
        file = make_upload_file(content, "application/x-executable", "malware.exe")

        with pytest.raises(Exception) as exc_info:
            await self.validator.validate_file(file)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_arquivo_sem_tipo(self):
        """Arquivo sem content_type deve ser rejeitado."""
        content = b"some content"
        file = make_upload_file(content, None, "unknown")
        file.content_type = None

        with pytest.raises(Exception) as exc_info:
            await self.validator.validate_file(file)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_arquivo_muito_grande(self):
        """Arquivo acima do limite de tamanho deve ser rejeitado."""
        content = b"\xff\xd8\xff" + b"\x00" * (11 * 1024 * 1024)  # 11MB > 10MB limit
        file = make_upload_file(content, "image/jpeg", "huge.jpg")

        with pytest.raises(Exception) as exc_info:
            await self.validator.validate_file(file)
        assert exc_info.value.status_code == 400
        assert "grande" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_magic_number_mismatch(self):
        """Arquivo com magic number que não corresponde ao tipo deve ser rejeitado."""
        # Declara PDF mas conteúdo começa com JPEG magic
        content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        file = make_upload_file(content, "application/pdf", "fake.pdf")

        with pytest.raises(Exception) as exc_info:
            await self.validator.validate_file(file)
        assert exc_info.value.status_code == 400
        assert "não corresponde" in exc_info.value.detail

    def test_magic_number_valido(self):
        """Validação de magic number com bytes corretos."""
        assert self.validator.validate_magic_number(b"%PDF-1.4", "application/pdf") is True
        assert self.validator.validate_magic_number(b"\xff\xd8\xff", "image/jpeg") is True
        assert self.validator.validate_magic_number(b"\x89PNG", "image/png") is True

    def test_magic_number_invalido(self):
        """Validação de magic number com bytes incorretos."""
        assert self.validator.validate_magic_number(b"NOT_PDF", "application/pdf") is False
        assert self.validator.validate_magic_number(b"NOT_JPEG", "image/jpeg") is False

    def test_magic_number_tipo_desconhecido(self):
        """Tipo sem magic number definido deve retornar True (permitir)."""
        assert self.validator.validate_magic_number(b"anything", "text/plain") is True

    def test_is_image(self):
        """Verificação de tipo imagem."""
        assert FileValidator.is_image("image/jpeg") is True
        assert FileValidator.is_image("image/png") is True
        assert FileValidator.is_image("application/pdf") is False
        assert FileValidator.is_image(None) is False

    def test_is_pdf(self):
        """Verificação de tipo PDF."""
        assert FileValidator.is_pdf("application/pdf") is True
        assert FileValidator.is_pdf("image/jpeg") is False

    def test_get_file_extension(self):
        """Extração de extensão de arquivo."""
        assert FileValidator.get_file_extension("doc.pdf") == ".pdf"
        assert FileValidator.get_file_extension("photo.JPG") == ".jpg"
        assert FileValidator.get_file_extension("noext") == ""
        assert FileValidator.get_file_extension("multi.dots.txt") == ".txt"
