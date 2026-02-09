"""
Document Scanner Service.

Responsavel pelo upload, pre-processamento e gerenciamento
do pipeline de processamento de documentos.
"""

import hashlib
import io
import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, BinaryIO, Optional
from uuid import uuid4

if TYPE_CHECKING:
    from .ocr_engine import OCREngine

from PIL import Image, ImageEnhance, ImageFilter

from ..models.document import (
    Document,
    DocumentSource,
    DocumentStatus,
    ImageMetadata,
)

logger = logging.getLogger(__name__)


@dataclass
class ScanConfig:
    """Configuracao do scanner."""

    # Diretorio de armazenamento
    storage_path: str = "/opt/conecta-pro/data/documents"
    temp_path: str = "/tmp/conecta-documents"  # noqa: S108

    # Limites
    max_file_size_mb: int = 50
    max_pages: int = 100
    allowed_formats: list[str] = field(default_factory=lambda: ["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "gif"])

    # Pre-processamento
    auto_deskew: bool = True
    auto_enhance: bool = True
    auto_denoise: bool = True
    target_dpi: int = 300
    convert_to_grayscale: bool = False

    # Thumbnails
    generate_thumbnail: bool = True
    thumbnail_size: tuple[int, int] = (200, 200)

    # OCR
    auto_ocr: bool = True
    ocr_languages: list[str] = field(default_factory=lambda: ["por", "eng"])


@dataclass
class ScanResult:
    """Resultado do scan de documento."""

    success: bool
    document: Document | None = None
    error: str | None = None
    warnings: list[str] = field(default_factory=list)


class DocumentScanner:
    """
    Scanner de documentos.

    Processa uploads de documentos, realiza pre-processamento
    e coordena o pipeline de OCR e extracao.
    """

    def __init__(
        self,
        config: ScanConfig | None = None,
        ocr_engine: Optional["OCREngine"] = None,
    ):
        """
        Inicializa o scanner.

        Args:
            config: Configuracao do scanner
            ocr_engine: Engine de OCR para processamento
        """
        self.config = config or ScanConfig()
        self.ocr_engine = ocr_engine

        # Criar diretorios
        os.makedirs(self.config.storage_path, exist_ok=True)
        os.makedirs(self.config.temp_path, exist_ok=True)

    async def scan_file(
        self,
        file: BinaryIO,
        filename: str,
        tenant_id: str,
        source: DocumentSource = DocumentSource.UPLOAD,
        metadata: dict[str, Any] | None = None,
    ) -> ScanResult:
        """
        Processa um arquivo de documento.

        Args:
            file: Arquivo binario
            filename: Nome do arquivo
            tenant_id: ID do tenant
            source: Origem do documento
            metadata: Metadados adicionais

        Returns:
            Resultado do scan
        """
        try:
            logger.info(f"Iniciando scan de documento: {filename}")

            # Validar arquivo
            validation = self._validate_file(file, filename)
            if not validation["valid"]:
                return ScanResult(success=False, error=validation["error"])

            # Criar documento
            document = Document(
                id=str(uuid4()),
                tenant_id=tenant_id,
                name=self._sanitize_filename(filename),
                original_name=filename,
                source=source,
                metadata=metadata or {},
            )

            # Iniciar etapa de upload
            document.start_step("upload")

            # Salvar arquivo original
            file_path = await self._save_file(file, document)
            document.file_path = file_path
            document.file_hash = self._calculate_hash(file)
            document.mime_type = validation["mime_type"]
            document.file_size = validation["size"]

            # Extrair metadados da imagem
            document.image_metadata = await self._extract_image_metadata(file_path)

            # Completar upload
            document.complete_step("upload")

            # Pre-processamento
            document.start_step("preprocessing")
            preprocessed_path, warnings = await self._preprocess_document(file_path, document)
            document.preprocessed_path = preprocessed_path

            # Gerar thumbnail
            if self.config.generate_thumbnail:
                document.thumbnail_path = await self._generate_thumbnail(preprocessed_path or file_path, document)

            document.complete_step("preprocessing")

            # OCR automatico
            if self.config.auto_ocr and self.ocr_engine:
                document.start_step("ocr")
                try:
                    ocr_result = await self.ocr_engine.process(preprocessed_path or file_path)
                    document.ocr_result_id = ocr_result.id
                    document.confidence_score = ocr_result.confidence * 100
                    document.complete_step(
                        "ocr",
                        {
                            "confidence": ocr_result.confidence,
                            "pages": len(ocr_result.pages),
                            "words": ocr_result.total_words,
                        },
                    )
                except Exception as e:
                    logger.error(f"Erro no OCR: {e}")
                    document.fail_step("ocr", str(e))
                    warnings.append(f"OCR falhou: {str(e)}")

            # Atualizar status
            if document.status != DocumentStatus.FAILED:
                document.status = DocumentStatus.QUEUED

            logger.info(f"Documento processado: {document.id}")

            return ScanResult(
                success=True,
                document=document,
                warnings=warnings,
            )

        except Exception as e:
            logger.error(f"Erro ao processar documento: {e}")
            return ScanResult(success=False, error=str(e))

    async def scan_batch(
        self,
        files: list[tuple[BinaryIO, str]],
        tenant_id: str,
        source: DocumentSource = DocumentSource.UPLOAD,
    ) -> list[ScanResult]:
        """
        Processa multiplos documentos.

        Args:
            files: Lista de (arquivo, nome)
            tenant_id: ID do tenant
            source: Origem dos documentos

        Returns:
            Lista de resultados
        """
        results = []
        for file, filename in files:
            result = await self.scan_file(file, filename, tenant_id, source)
            results.append(result)
        return results

    async def scan_from_url(
        self,
        url: str,
        tenant_id: str,
        source: DocumentSource = DocumentSource.API,
    ) -> ScanResult:
        """
        Processa documento de URL.

        Args:
            url: URL do documento
            tenant_id: ID do tenant
            source: Origem do documento

        Returns:
            Resultado do scan
        """
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session, session.get(url, timeout=60) as response:
                if response.status != 200:
                    return ScanResult(
                        success=False,
                        error=f"Erro ao baixar: HTTP {response.status}",
                    )

                # Extrair nome do arquivo
                content_disp = response.headers.get("Content-Disposition", "")
                if "filename=" in content_disp:
                    filename = content_disp.split("filename=")[1].strip('"')
                else:
                    filename = url.split("/")[-1].split("?")[0]

                # Baixar conteudo
                content = await response.read()
                file = io.BytesIO(content)

                return await self.scan_file(file, filename, tenant_id, source, {"source_url": url})

        except Exception as e:
            logger.error(f"Erro ao baixar documento: {e}")
            return ScanResult(success=False, error=str(e))

    async def rescan_document(self, document: Document) -> ScanResult:
        """
        Re-processa um documento existente.

        Args:
            document: Documento a reprocessar

        Returns:
            Resultado do rescan
        """
        try:
            if not os.path.exists(document.file_path):
                return ScanResult(
                    success=False,
                    error="Arquivo original nao encontrado",
                )

            # Resetar etapas
            for step in document.processing_steps:
                if step.name != "upload":
                    step.status = "pending"
                    step.started_at = None
                    step.completed_at = None
                    step.duration_ms = None
                    step.error = None

            document.status = DocumentStatus.QUEUED
            document.updated_at = datetime.utcnow()

            # Reprocessar
            document.start_step("preprocessing")
            preprocessed_path, warnings = await self._preprocess_document(document.file_path, document)
            document.preprocessed_path = preprocessed_path
            document.complete_step("preprocessing")

            if self.config.auto_ocr and self.ocr_engine:
                document.start_step("ocr")
                ocr_result = await self.ocr_engine.process(preprocessed_path or document.file_path)
                document.ocr_result_id = ocr_result.id
                document.confidence_score = ocr_result.confidence * 100
                document.complete_step("ocr")

            return ScanResult(success=True, document=document, warnings=warnings)

        except Exception as e:
            logger.error(f"Erro no rescan: {e}")
            return ScanResult(success=False, error=str(e))

    def _validate_file(self, file: BinaryIO, filename: str) -> dict[str, Any]:
        """Valida arquivo de entrada."""
        result = {"valid": True, "error": None}

        # Verificar extensao
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in self.config.allowed_formats:
            result["valid"] = False
            result["error"] = f"Formato nao suportado: {ext}"
            return result

        # Verificar tamanho
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)

        if size > self.config.max_file_size_mb * 1024 * 1024:
            result["valid"] = False
            result["error"] = f"Arquivo excede limite de {self.config.max_file_size_mb}MB"
            return result

        # Detectar MIME type
        mime_types = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "tiff": "image/tiff",
            "bmp": "image/bmp",
            "gif": "image/gif",
        }
        result["mime_type"] = mime_types.get(ext, "application/octet-stream")
        result["size"] = size

        return result

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitiza nome do arquivo."""
        import re

        # Remover caracteres perigosos
        safe = re.sub(r'[<>:"/\\|?*]', "_", filename)
        # Limitar tamanho
        if len(safe) > 200:
            ext = safe.rsplit(".", 1)[-1] if "." in safe else ""
            safe = safe[:196] + "." + ext
        return safe

    async def _save_file(self, file: BinaryIO, document: Document) -> str:
        """Salva arquivo no storage."""
        # Criar estrutura de diretorios
        date_path = datetime.utcnow().strftime("%Y/%m/%d")
        dir_path = os.path.join(
            self.config.storage_path,
            document.tenant_id,
            date_path,
        )
        os.makedirs(dir_path, exist_ok=True)

        # Nome unico
        ext = document.name.rsplit(".", 1)[-1] if "." in document.name else "bin"
        file_path = os.path.join(dir_path, f"{document.id}.{ext}")

        # Salvar
        file.seek(0)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file, f)

        return file_path

    def _calculate_hash(self, file: BinaryIO) -> str:
        """Calcula hash SHA-256 do arquivo."""
        file.seek(0)
        sha256 = hashlib.sha256()
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)
        file.seek(0)
        return sha256.hexdigest()

    async def _extract_image_metadata(self, file_path: str) -> ImageMetadata:
        """Extrai metadados da imagem."""
        try:
            if file_path.lower().endswith(".pdf"):
                return await self._extract_pdf_metadata(file_path)

            with Image.open(file_path) as img:
                return ImageMetadata(
                    width=img.width,
                    height=img.height,
                    format=img.format or "UNKNOWN",
                    size_bytes=os.path.getsize(file_path),
                    dpi=img.info.get("dpi", (72, 72))[0] if img.info.get("dpi") else None,
                    color_mode=img.mode,
                    pages=getattr(img, "n_frames", 1),
                    orientation="PORTRAIT" if img.height > img.width else "LANDSCAPE",
                )
        except Exception as e:
            logger.warning(f"Erro ao extrair metadados: {e}")
            return ImageMetadata(
                width=0,
                height=0,
                format="UNKNOWN",
                size_bytes=os.path.getsize(file_path),
            )

    async def _extract_pdf_metadata(self, file_path: str) -> ImageMetadata:
        """Extrai metadados de PDF."""
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            page = doc[0]
            rect = page.rect

            metadata = ImageMetadata(
                width=int(rect.width),
                height=int(rect.height),
                format="PDF",
                size_bytes=os.path.getsize(file_path),
                pages=len(doc),
                orientation="PORTRAIT" if rect.height > rect.width else "LANDSCAPE",
            )
            doc.close()
            return metadata

        except ImportError:
            logger.warning("PyMuPDF nao instalado, metadados limitados")
            return ImageMetadata(
                width=0,
                height=0,
                format="PDF",
                size_bytes=os.path.getsize(file_path),
            )

    async def _preprocess_document(self, file_path: str, document: Document) -> tuple[str | None, list[str]]:
        """
        Pre-processa documento para OCR.

        Returns:
            Tupla (caminho_preprocessado, warnings)
        """
        warnings = []

        try:
            # PDF - converter para imagens
            if file_path.lower().endswith(".pdf"):
                return await self._preprocess_pdf(file_path, document)

            # Imagem - aplicar melhorias
            with Image.open(file_path) as img:
                processed = img.copy()

                # Converter para RGB se necessario
                if processed.mode in ("RGBA", "P"):
                    processed = processed.convert("RGB")

                # Converter para escala de cinza
                if self.config.convert_to_grayscale and processed.mode != "L":
                    processed = processed.convert("L")

                # Auto-enhance
                if self.config.auto_enhance:
                    processed = self._enhance_image(processed)

                # Auto-denoise
                if self.config.auto_denoise:
                    processed = self._denoise_image(processed)

                # Auto-deskew
                if self.config.auto_deskew:
                    processed, angle = self._deskew_image(processed)
                    if abs(angle) > 0.5:
                        document.image_metadata.is_skewed = True
                        document.image_metadata.skew_angle = angle
                        warnings.append(f"Imagem corrigida: rotacao de {angle:.1f} graus")

                # Salvar preprocessado
                preprocessed_path = file_path.rsplit(".", 1)[0] + "_preprocessed.png"
                processed.save(preprocessed_path, "PNG", optimize=True)

                return preprocessed_path, warnings

        except Exception as e:
            logger.warning(f"Erro no pre-processamento: {e}")
            warnings.append(f"Pre-processamento parcial: {str(e)}")
            return None, warnings

    async def _preprocess_pdf(self, file_path: str, document: Document) -> tuple[str | None, list[str]]:
        """Pre-processa PDF convertendo para imagens."""
        warnings = []

        try:
            import fitz

            doc = fitz.open(file_path)

            if len(doc) > self.config.max_pages:
                warnings.append(f"PDF tem {len(doc)} paginas, processando apenas {self.config.max_pages}")

            # Diretorio para paginas
            pages_dir = file_path.rsplit(".", 1)[0] + "_pages"
            os.makedirs(pages_dir, exist_ok=True)

            for i, page in enumerate(doc):
                if i >= self.config.max_pages:
                    break

                # Renderizar em alta resolucao
                mat = fitz.Matrix(self.config.target_dpi / 72, self.config.target_dpi / 72)
                pix = page.get_pixmap(matrix=mat)

                # Salvar pagina
                page_path = os.path.join(pages_dir, f"page_{i + 1:04d}.png")
                pix.save(page_path)

            doc.close()
            return pages_dir, warnings

        except ImportError:
            warnings.append("PyMuPDF nao instalado, PDF nao processado")
            return None, warnings

    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """Melhora qualidade da imagem."""
        # Aumentar contraste
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.3)

        # Aumentar nitidez
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)

        return image

    def _denoise_image(self, image: Image.Image) -> Image.Image:
        """Remove ruido da imagem."""
        # Aplicar filtro mediano para reduzir ruido
        return image.filter(ImageFilter.MedianFilter(size=3))

    def _deskew_image(self, image: Image.Image) -> tuple[Image.Image, float]:
        """Corrige inclinacao da imagem."""
        try:
            import numpy as np

            # Converter para array numpy
            np.array(image.convert("L"))

            # Detectar angulo usando projecao de perfil
            angles = np.arange(-5, 5.5, 0.5)
            scores = []

            for angle in angles:
                rotated = image.rotate(angle, fillcolor=255)
                arr = np.array(rotated.convert("L"))
                # Score baseado na variancia das projecoes horizontais
                projection = np.sum(arr < 128, axis=1)
                score = np.var(projection)
                scores.append(score)

            best_angle = angles[np.argmax(scores)]

            if abs(best_angle) > 0.5:
                image = image.rotate(best_angle, fillcolor=255, expand=True)

            return image, best_angle

        except Exception:
            return image, 0.0

    async def _generate_thumbnail(self, file_path: str, document: Document) -> str | None:
        """Gera thumbnail do documento."""
        try:
            # Se for diretorio de paginas PDF, usar primeira pagina
            if os.path.isdir(file_path):
                pages = sorted(os.listdir(file_path))
                if pages:
                    file_path = os.path.join(file_path, pages[0])

            with Image.open(file_path) as img:
                # Criar thumbnail
                img.thumbnail(self.config.thumbnail_size, Image.Resampling.LANCZOS)

                # Salvar
                thumb_path = document.file_path.rsplit(".", 1)[0] + "_thumb.png"
                img.save(thumb_path, "PNG")

                return thumb_path

        except Exception as e:
            logger.warning(f"Erro ao gerar thumbnail: {e}")
            return None

    async def get_document_preview(self, document: Document, page: int = 1) -> bytes | None:
        """
        Obtem preview do documento.

        Args:
            document: Documento
            page: Numero da pagina

        Returns:
            Bytes da imagem de preview
        """
        try:
            # Tentar thumbnail primeiro
            if document.thumbnail_path and os.path.exists(document.thumbnail_path):
                with open(document.thumbnail_path, "rb") as f:
                    return f.read()

            # Preprocessed
            if document.preprocessed_path:
                if os.path.isdir(document.preprocessed_path):
                    pages = sorted(os.listdir(document.preprocessed_path))
                    if page <= len(pages):
                        with open(
                            os.path.join(document.preprocessed_path, pages[page - 1]),
                            "rb",
                        ) as f:
                            return f.read()
                elif os.path.exists(document.preprocessed_path):
                    with open(document.preprocessed_path, "rb") as f:
                        return f.read()

            return None

        except Exception as e:
            logger.error(f"Erro ao obter preview: {e}")
            return None

    async def delete_document_files(self, document: Document) -> bool:
        """
        Remove arquivos de um documento.

        Args:
            document: Documento

        Returns:
            True se removido com sucesso
        """
        try:
            files_to_delete = [
                document.file_path,
                document.preprocessed_path,
                document.thumbnail_path,
            ]

            for file_path in files_to_delete:
                if file_path:
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    elif os.path.exists(file_path):
                        os.remove(file_path)

            return True

        except Exception as e:
            logger.error(f"Erro ao deletar arquivos: {e}")
            return False

    def get_storage_stats(self, tenant_id: str) -> dict[str, Any]:
        """
        Obtem estatisticas de armazenamento.

        Args:
            tenant_id: ID do tenant

        Returns:
            Estatisticas de uso
        """
        tenant_path = os.path.join(self.config.storage_path, tenant_id)

        if not os.path.exists(tenant_path):
            return {"total_files": 0, "total_size_mb": 0}

        total_size = 0
        total_files = 0

        for root, _, files in os.walk(tenant_path):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                total_files += 1

        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "storage_path": tenant_path,
        }
