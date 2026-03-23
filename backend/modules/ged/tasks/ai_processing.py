"""Background task: processamento IA apos upload de documento.

Executa em background (FastAPI BackgroundTasks) apos upload:
1. Extrai texto do arquivo (OCR basico para PDFs/TXT)
2. Classifica tipo e categoria via keywords
3. Extrai palavras-chave para busca fulltext
4. Salva resultados no documento
"""

import logging
from pathlib import Path

from sqlalchemy import select

from core.database import async_session_factory

logger = logging.getLogger(__name__)

# Extensoes que suportam extracao de texto
TEXT_EXTENSIONS = {"txt", "md", "csv", "json", "xml", "html", "htm", "log"}
PDF_EXTENSIONS = {"pdf"}


def _extract_text_from_file(file_path: str, file_extension: str) -> str | None:
    """Extrai texto de um arquivo baseado na extensao."""
    ext = file_extension.lower().lstrip(".")
    path = Path(file_path)

    if not path.exists():
        logger.warning("Arquivo nao encontrado para OCR: %s", file_path)
        return None

    # Arquivos de texto puro
    if ext in TEXT_EXTENSIONS:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            return text[:50000]  # Limitar a 50k chars
        except Exception as e:
            logger.warning("Falha ao ler texto de %s: %s", file_path, e)
            return None

    # PDFs - tentar extrair com pdfplumber ou PyPDF2
    if ext in PDF_EXTENSIONS:
        try:
            import pdfplumber

            with pdfplumber.open(path) as pdf:
                pages_text = []
                for page in pdf.pages[:20]:  # Max 20 paginas
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)
                return "\n".join(pages_text)[:50000] if pages_text else None
        except ImportError:
            try:
                from PyPDF2 import PdfReader

                reader = PdfReader(str(path))
                pages_text = []
                for page in reader.pages[:20]:
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)
                return "\n".join(pages_text)[:50000] if pages_text else None
            except ImportError:
                logger.debug("pdfplumber/PyPDF2 nao instalados, pulando OCR de PDF")
                return None
        except Exception as e:
            logger.warning("Falha ao extrair texto de PDF %s: %s", file_path, e)
            return None

    return None


async def process_document_ai(document_id: str) -> None:
    """Processa documento com IA em background.

    - Extrai texto (OCR)
    - Classifica tipo/categoria
    - Extrai keywords
    - Indexa para busca
    """
    logger.info("IA Background: iniciando processamento do documento %s", document_id)

    async with async_session_factory() as db:
        try:
            # Buscar documento
            from modules.ged.models.document import Document

            result = await db.execute(select(Document).where(Document.id == document_id))
            doc = result.scalars().first()

            if not doc:
                logger.warning("IA Background: documento %s nao encontrado", document_id)
                return

            # 1. Extrair texto
            extracted_text = _extract_text_from_file(doc.file_path, doc.file_extension)

            if extracted_text:
                # Salvar OCR
                doc.set_ocr_result(extracted_text, confidence=0.85)
                logger.info(
                    "IA Background: texto extraido (%d chars) de %s",
                    len(extracted_text),
                    doc.file_name,
                )
            else:
                # Usar titulo + descricao como fallback
                extracted_text = f"{doc.title or ''} {doc.description or ''}"

            # 2. Classificar com IA
            from modules.ged.services.document_ai_service import DocumentAIService

            ai_service = DocumentAIService(db)
            classification = await ai_service.classify_document(
                text=extracted_text,
                file_name=doc.file_name,
            )

            # Salvar classificacao
            doc.set_ai_classification(
                classification=classification,
                confidence=max(
                    classification.get("type_confidence", 0),
                    classification.get("category_confidence", 0),
                ),
            )

            # 3. Extrair e salvar keywords
            keywords = classification.get("keywords", [])
            if keywords:
                doc.mark_as_indexed(keywords[:30])

            await db.commit()

            logger.info(
                "IA Background: documento %s processado — tipo=%s (%.0f%%), categoria=%s (%.0f%%), %d keywords",
                document_id,
                classification.get("suggested_type", "?"),
                classification.get("type_confidence", 0),
                classification.get("suggested_category", "?"),
                classification.get("category_confidence", 0),
                len(keywords),
            )

        except Exception as e:
            logger.error("IA Background: erro ao processar documento %s: %s", document_id, e)
            await db.rollback()
