"""
OCR Engine Service.

Motor de OCR multi-provider com suporte a Tesseract,
Google Vision, AWS Textract, e outros.
"""

import asyncio
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

from ..models.ocr_result import (
    BlockType,
    BoundingBox,
    OCRBlock,
    OCRLine,
    OCRPage,
    OCRProvider,
    OCRResult,
    OCRWord,
)

logger = logging.getLogger(__name__)


class OCRLanguage(str, Enum):
    """Idiomas suportados para OCR."""

    PORTUGUESE = "por"
    ENGLISH = "eng"
    SPANISH = "spa"
    FRENCH = "fra"
    GERMAN = "deu"
    ITALIAN = "ita"


@dataclass
class OCRConfig:
    """Configuracao do OCR Engine."""

    # Provider primario
    primary_provider: OCRProvider = OCRProvider.TESSERACT

    # Fallback providers
    fallback_providers: List[OCRProvider] = field(default_factory=list)

    # Idiomas
    languages: List[str] = field(default_factory=lambda: ["por", "eng"])

    # Qualidade
    min_confidence: float = 0.6
    use_spell_check: bool = True
    detect_orientation: bool = True

    # Performance
    timeout_seconds: int = 120
    max_concurrent: int = 4
    enable_gpu: bool = False

    # Tesseract
    tesseract_path: Optional[str] = None
    tesseract_config: str = "--oem 3 --psm 3"

    # Cloud providers
    google_credentials_path: Optional[str] = None
    aws_region: str = "us-east-1"
    azure_endpoint: Optional[str] = None
    azure_key: Optional[str] = None

    # Pos-processamento
    merge_lines: bool = True
    detect_tables: bool = True
    detect_barcodes: bool = True


class BaseOCRProvider(ABC):
    """Interface base para providers de OCR."""

    @abstractmethod
    async def process(
        self, image_path: str, languages: List[str]
    ) -> OCRResult:
        """Processa imagem e retorna resultado OCR."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se provider esta disponivel."""
        pass


class TesseractProvider(BaseOCRProvider):
    """Provider Tesseract OCR."""

    def __init__(self, config: OCRConfig):
        self.config = config
        self._tesseract_cmd = config.tesseract_path or "tesseract"

    def is_available(self) -> bool:
        """Verifica se Tesseract esta instalado."""
        import shutil

        return shutil.which(self._tesseract_cmd) is not None

    async def process(
        self, image_path: str, languages: List[str]
    ) -> OCRResult:
        """Processa imagem com Tesseract."""
        try:
            import pytesseract

            if self.config.tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_path

            start_time = time.time()

            # Abrir imagem
            image = Image.open(image_path)

            # Detectar orientacao
            if self.config.detect_orientation:
                try:
                    osd = pytesseract.image_to_osd(image, output_type=pytesseract.Output.DICT)
                    if osd.get("rotate"):
                        image = image.rotate(-osd["rotate"], expand=True)
                except Exception:
                    pass

            # Configurar idiomas
            lang_str = "+".join(languages)

            # OCR com dados detalhados
            data = pytesseract.image_to_data(
                image,
                lang=lang_str,
                config=self.config.tesseract_config,
                output_type=pytesseract.Output.DICT,
            )

            # Construir resultado
            pages = self._build_pages(data, image.width, image.height)

            # Texto completo
            full_text = pytesseract.image_to_string(
                image, lang=lang_str, config=self.config.tesseract_config
            )

            # Calcular confianca media
            confidences = [c for c in data["conf"] if c > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            processing_time = int((time.time() - start_time) * 1000)

            return OCRResult(
                provider=OCRProvider.TESSERACT,
                pages=pages,
                full_text=full_text.strip(),
                confidence=avg_confidence / 100,
                language=languages[0] if languages else "por",
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Erro Tesseract: {e}")
            raise

    def _build_pages(
        self, data: Dict, width: int, height: int
    ) -> List[OCRPage]:
        """Constroi paginas a partir dos dados Tesseract."""
        pages: Dict[int, OCRPage] = {}
        blocks: Dict[Tuple[int, int], OCRBlock] = {}
        lines: Dict[Tuple[int, int, int], OCRLine] = {}

        for i in range(len(data["text"])):
            text = data["text"][i].strip()
            conf = data["conf"][i]
            page_num = data["page_num"][i]
            block_num = data["block_num"][i]
            line_num = data["line_num"][i]

            # Criar pagina se necessario
            if page_num not in pages:
                pages[page_num] = OCRPage(
                    page_number=page_num,
                    width=width,
                    height=height,
                )

            # Pular palavras vazias ou com confianca muito baixa
            if not text or conf < 0:
                continue

            # Criar bloco se necessario
            block_key = (page_num, block_num)
            if block_key not in blocks:
                blocks[block_key] = OCRBlock(
                    block_type=BlockType.TEXT,
                    page_number=page_num,
                    block_number=block_num,
                )

            # Criar linha se necessario
            line_key = (page_num, block_num, line_num)
            if line_key not in lines:
                lines[line_key] = OCRLine(line_number=line_num)

            # Criar palavra
            word = OCRWord(
                text=text,
                confidence=conf / 100,
                bounding_box=BoundingBox(
                    x=data["left"][i],
                    y=data["top"][i],
                    width=data["width"][i],
                    height=data["height"][i],
                ),
            )

            lines[line_key].words.append(word)

        # Montar hierarquia
        for line_key, line in lines.items():
            page_num, block_num, _ = line_key
            line.text = " ".join(w.text for w in line.words)
            line.confidence = (
                sum(w.confidence for w in line.words) / len(line.words)
                if line.words
                else 0
            )
            blocks[(page_num, block_num)].lines.append(line)

        for block_key, block in blocks.items():
            page_num, _ = block_key
            block.text = "\n".join(line.text for line in block.lines)
            block.confidence = (
                sum(line.confidence for line in block.lines) / len(block.lines)
                if block.lines
                else 0
            )
            pages[page_num].blocks.append(block)

        # Calcular confianca das paginas
        for page in pages.values():
            if page.blocks:
                page.confidence = sum(b.confidence for b in page.blocks) / len(
                    page.blocks
                )

        return list(pages.values())


class EasyOCRProvider(BaseOCRProvider):
    """Provider EasyOCR."""

    def __init__(self, config: OCRConfig):
        self.config = config
        self._reader = None

    def is_available(self) -> bool:
        """Verifica se EasyOCR esta disponivel."""
        try:
            import easyocr

            return True
        except ImportError:
            return False

    def _get_reader(self, languages: List[str]):
        """Obtem reader EasyOCR."""
        import easyocr

        # Mapear codigos de idioma
        lang_map = {
            "por": "pt",
            "eng": "en",
            "spa": "es",
            "fra": "fr",
            "deu": "de",
            "ita": "it",
        }
        langs = [lang_map.get(l, l) for l in languages]

        return easyocr.Reader(langs, gpu=self.config.enable_gpu)

    async def process(
        self, image_path: str, languages: List[str]
    ) -> OCRResult:
        """Processa imagem com EasyOCR."""
        try:
            start_time = time.time()

            reader = self._get_reader(languages)
            results = reader.readtext(image_path)

            # Construir pagina
            image = Image.open(image_path)
            page = OCRPage(
                page_number=1,
                width=image.width,
                height=image.height,
            )

            # Processar resultados
            current_block = OCRBlock(block_type=BlockType.TEXT, page_number=1)
            current_line = OCRLine(line_number=1)
            last_y = None

            for bbox, text, conf in results:
                # Calcular bounding box
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)

                word = OCRWord(
                    text=text,
                    confidence=conf,
                    bounding_box=BoundingBox(
                        x=int(x_min),
                        y=int(y_min),
                        width=int(x_max - x_min),
                        height=int(y_max - y_min),
                    ),
                )

                # Detectar nova linha
                if last_y is not None and abs(y_min - last_y) > 20:
                    if current_line.words:
                        current_line.text = " ".join(w.text for w in current_line.words)
                        current_block.lines.append(current_line)
                    current_line = OCRLine(line_number=len(current_block.lines) + 1)

                current_line.words.append(word)
                last_y = y_min

            # Adicionar ultima linha
            if current_line.words:
                current_line.text = " ".join(w.text for w in current_line.words)
                current_block.lines.append(current_line)

            if current_block.lines:
                current_block.text = "\n".join(l.text for l in current_block.lines)
                page.blocks.append(current_block)

            # Calcular metricas
            all_words = [w for b in page.blocks for l in b.lines for w in l.words]
            avg_confidence = (
                sum(w.confidence for w in all_words) / len(all_words)
                if all_words
                else 0
            )

            full_text = "\n".join(b.text for b in page.blocks)
            processing_time = int((time.time() - start_time) * 1000)

            return OCRResult(
                provider=OCRProvider.EASYOCR,
                pages=[page],
                full_text=full_text,
                confidence=avg_confidence,
                language=languages[0] if languages else "por",
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Erro EasyOCR: {e}")
            raise


class GoogleVisionProvider(BaseOCRProvider):
    """Provider Google Cloud Vision."""

    def __init__(self, config: OCRConfig):
        self.config = config

    def is_available(self) -> bool:
        """Verifica se Google Vision esta configurado."""
        if self.config.google_credentials_path:
            return os.path.exists(self.config.google_credentials_path)
        return os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") is not None

    async def process(
        self, image_path: str, languages: List[str]
    ) -> OCRResult:
        """Processa imagem com Google Vision."""
        try:
            from google.cloud import vision

            start_time = time.time()

            if self.config.google_credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                    self.config.google_credentials_path
                )

            client = vision.ImageAnnotatorClient()

            with open(image_path, "rb") as f:
                content = f.read()

            image = vision.Image(content=content)

            # Configurar hints de idioma
            lang_hints = []
            for lang in languages:
                if lang == "por":
                    lang_hints.append("pt")
                elif lang == "eng":
                    lang_hints.append("en")
                else:
                    lang_hints.append(lang[:2])

            context = vision.ImageContext(language_hints=lang_hints)

            # Fazer OCR
            response = client.document_text_detection(
                image=image, image_context=context
            )

            # Processar resposta
            pages = self._parse_response(response)

            full_text = response.full_text_annotation.text if response.full_text_annotation else ""
            processing_time = int((time.time() - start_time) * 1000)

            # Calcular confianca
            all_confidences = []
            for page in pages:
                for block in page.blocks:
                    for line in block.lines:
                        for word in line.words:
                            all_confidences.append(word.confidence)

            avg_confidence = (
                sum(all_confidences) / len(all_confidences) if all_confidences else 0
            )

            return OCRResult(
                provider=OCRProvider.GOOGLE_VISION,
                pages=pages,
                full_text=full_text,
                confidence=avg_confidence,
                language=languages[0] if languages else "por",
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Erro Google Vision: {e}")
            raise

    def _parse_response(self, response) -> List[OCRPage]:
        """Parseia resposta do Google Vision."""
        pages = []

        if not response.full_text_annotation:
            return pages

        for page_idx, gv_page in enumerate(response.full_text_annotation.pages):
            page = OCRPage(
                page_number=page_idx + 1,
                width=gv_page.width,
                height=gv_page.height,
            )

            for block_idx, gv_block in enumerate(gv_page.blocks):
                block = OCRBlock(
                    block_type=BlockType.TEXT,
                    page_number=page_idx + 1,
                    block_number=block_idx,
                )

                for para in gv_block.paragraphs:
                    line = OCRLine(line_number=len(block.lines) + 1)

                    for word in para.words:
                        text = "".join(s.text for s in word.symbols)
                        confidence = word.confidence

                        # Bounding box
                        vertices = word.bounding_box.vertices
                        bbox = BoundingBox(
                            x=vertices[0].x,
                            y=vertices[0].y,
                            width=vertices[2].x - vertices[0].x,
                            height=vertices[2].y - vertices[0].y,
                        )

                        ocr_word = OCRWord(
                            text=text,
                            confidence=confidence,
                            bounding_box=bbox,
                        )
                        line.words.append(ocr_word)

                    line.text = " ".join(w.text for w in line.words)
                    line.confidence = (
                        sum(w.confidence for w in line.words) / len(line.words)
                        if line.words
                        else 0
                    )
                    block.lines.append(line)

                block.text = "\n".join(l.text for l in block.lines)
                page.blocks.append(block)

            pages.append(page)

        return pages


class OCREngine:
    """
    Motor de OCR multi-provider.

    Gerencia multiplos providers de OCR com fallback automatico
    e otimizacoes para diferentes tipos de documento.
    """

    PROVIDERS = {
        OCRProvider.TESSERACT: TesseractProvider,
        OCRProvider.EASYOCR: EasyOCRProvider,
        OCRProvider.GOOGLE_VISION: GoogleVisionProvider,
    }

    def __init__(self, config: Optional[OCRConfig] = None):
        """
        Inicializa OCR Engine.

        Args:
            config: Configuracao do engine
        """
        self.config = config or OCRConfig()
        self._providers: Dict[OCRProvider, BaseOCRProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Inicializa providers disponiveis."""
        # Provider primario
        if self.config.primary_provider in self.PROVIDERS:
            provider_class = self.PROVIDERS[self.config.primary_provider]
            provider = provider_class(self.config)
            if provider.is_available():
                self._providers[self.config.primary_provider] = provider
            else:
                logger.warning(
                    f"Provider primario {self.config.primary_provider} nao disponivel"
                )

        # Fallback providers
        for provider_name in self.config.fallback_providers:
            if provider_name in self.PROVIDERS:
                provider_class = self.PROVIDERS[provider_name]
                provider = provider_class(self.config)
                if provider.is_available():
                    self._providers[provider_name] = provider

    async def process(
        self,
        image_path: str,
        languages: Optional[List[str]] = None,
        provider: Optional[OCRProvider] = None,
    ) -> OCRResult:
        """
        Processa documento com OCR.

        Args:
            image_path: Caminho da imagem ou diretorio de paginas
            languages: Idiomas para OCR
            provider: Provider especifico (opcional)

        Returns:
            Resultado do OCR
        """
        languages = languages or self.config.languages

        # Se for diretorio, processar multiplas paginas
        if os.path.isdir(image_path):
            return await self._process_pages(image_path, languages, provider)

        # Processar imagem unica
        return await self._process_single(image_path, languages, provider)

    async def _process_single(
        self,
        image_path: str,
        languages: List[str],
        provider: Optional[OCRProvider] = None,
    ) -> OCRResult:
        """Processa uma unica imagem."""
        # Determinar provider
        providers_to_try = []

        if provider and provider in self._providers:
            providers_to_try.append(provider)
        else:
            if self.config.primary_provider in self._providers:
                providers_to_try.append(self.config.primary_provider)
            providers_to_try.extend(
                p for p in self.config.fallback_providers if p in self._providers
            )

        if not providers_to_try:
            raise RuntimeError("Nenhum provider de OCR disponivel")

        # Tentar cada provider
        last_error = None
        for prov in providers_to_try:
            try:
                logger.info(f"Processando com {prov.value}: {image_path}")
                result = await self._providers[prov].process(image_path, languages)

                # Pos-processamento
                if self.config.detect_tables:
                    result = self._detect_tables(result)

                if self.config.detect_barcodes:
                    result = await self._detect_barcodes(result, image_path)

                return result

            except Exception as e:
                logger.warning(f"Falha com {prov.value}: {e}")
                last_error = e

        raise RuntimeError(f"Todos os providers falharam: {last_error}")

    async def _process_pages(
        self,
        pages_dir: str,
        languages: List[str],
        provider: Optional[OCRProvider] = None,
    ) -> OCRResult:
        """Processa multiplas paginas."""
        pages = sorted(os.listdir(pages_dir))
        all_pages: List[OCRPage] = []
        all_text = []
        total_confidence = 0
        total_time = 0

        # Processar em paralelo (limitado)
        semaphore = asyncio.Semaphore(self.config.max_concurrent)

        async def process_page(page_file: str, page_num: int):
            async with semaphore:
                page_path = os.path.join(pages_dir, page_file)
                result = await self._process_single(page_path, languages, provider)
                if result.pages:
                    result.pages[0].page_number = page_num
                    return result
                return None

        tasks = [
            process_page(page_file, i + 1) for i, page_file in enumerate(pages)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Erro ao processar pagina: {result}")
                continue
            if result:
                all_pages.extend(result.pages)
                all_text.append(result.full_text)
                total_confidence += result.confidence
                total_time += result.processing_time_ms

        return OCRResult(
            provider=provider or self.config.primary_provider,
            pages=all_pages,
            full_text="\n\n".join(all_text),
            confidence=total_confidence / len(results) if results else 0,
            language=languages[0] if languages else "por",
            processing_time_ms=total_time,
        )

    def _detect_tables(self, result: OCRResult) -> OCRResult:
        """Detecta tabelas no resultado OCR."""
        for page in result.pages:
            # Heuristica simples: detectar padroes de alinhamento
            lines_by_y = {}
            for block in page.blocks:
                for line in block.lines:
                    if line.bounding_box:
                        y = line.bounding_box.y
                        # Agrupar linhas proximas
                        key = y // 20 * 20
                        if key not in lines_by_y:
                            lines_by_y[key] = []
                        lines_by_y[key].append(line)

            # Detectar linhas com multiplas colunas
            for y_pos, lines in lines_by_y.items():
                if len(lines) > 2:
                    # Possivel linha de tabela
                    for line in lines:
                        if len(line.words) >= 3:
                            # Marcar como possivel tabela
                            pass

        return result

    async def _detect_barcodes(
        self, result: OCRResult, image_path: str
    ) -> OCRResult:
        """Detecta codigos de barra na imagem."""
        try:
            from pyzbar import pyzbar

            image = Image.open(image_path)
            barcodes = pyzbar.decode(image)

            for barcode in barcodes:
                # Criar bloco para barcode
                x, y, w, h = barcode.rect
                block = OCRBlock(
                    block_type=BlockType.BARCODE
                    if barcode.type != "QRCODE"
                    else BlockType.QR_CODE,
                    bounding_box=BoundingBox(x=x, y=y, width=w, height=h),
                    barcode_type=barcode.type,
                    barcode_value=barcode.data.decode("utf-8"),
                    page_number=1,
                )

                if result.pages:
                    result.pages[0].blocks.append(block)
                    result.barcodes_found += 1

        except ImportError:
            logger.debug("pyzbar nao instalado, deteccao de barcode desativada")
        except Exception as e:
            logger.warning(f"Erro ao detectar barcodes: {e}")

        return result

    def get_available_providers(self) -> List[OCRProvider]:
        """Retorna lista de providers disponiveis."""
        return list(self._providers.keys())

    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna informacoes sobre providers."""
        return {
            "primary": self.config.primary_provider.value,
            "available": [p.value for p in self._providers.keys()],
            "languages": self.config.languages,
            "config": {
                "min_confidence": self.config.min_confidence,
                "detect_tables": self.config.detect_tables,
                "detect_barcodes": self.config.detect_barcodes,
            },
        }
