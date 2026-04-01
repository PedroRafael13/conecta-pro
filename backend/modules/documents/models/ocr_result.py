"""
Modelo de Resultado de OCR.

Define estruturas para armazenar resultados do processamento OCR,
incluindo texto, linhas, palavras, blocos e coordenadas.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class OCRProvider(StrEnum):
    """Provedores de OCR suportados."""

    TESSERACT = "tesseract"
    GOOGLE_VISION = "google_vision"
    AWS_TEXTRACT = "aws_textract"
    AZURE_COGNITIVE = "azure_cognitive"
    PADDLEOCR = "paddleocr"
    EASYOCR = "easyocr"
    CUSTOM = "custom"


class TextOrientation(StrEnum):
    """Orientacao do texto."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    ROTATED = "rotated"


class BlockType(StrEnum):
    """Tipo de bloco de texto."""

    TEXT = "text"
    TABLE = "table"
    FIGURE = "figure"
    BARCODE = "barcode"
    QR_CODE = "qr_code"
    SIGNATURE = "signature"
    HANDWRITING = "handwriting"
    STAMP = "stamp"
    LOGO = "logo"
    CHECKBOX = "checkbox"
    FORM_FIELD = "form_field"


@dataclass
class BoundingBox:
    """Caixa delimitadora de um elemento."""

    x: int  # Coordenada X do canto superior esquerdo
    y: int  # Coordenada Y do canto superior esquerdo
    width: int
    height: int

    @property
    def x2(self) -> int:
        """Coordenada X do canto inferior direito."""
        return self.x + self.width

    @property
    def y2(self) -> int:
        """Coordenada Y do canto inferior direito."""
        return self.y + self.height

    @property
    def center(self) -> tuple[int, int]:
        """Centro da caixa."""
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def area(self) -> int:
        """Area da caixa."""
        return self.width * self.height

    def contains(self, x: int, y: int) -> bool:
        """Verifica se ponto esta dentro da caixa."""
        return self.x <= x <= self.x2 and self.y <= y <= self.y2

    def overlaps(self, other: "BoundingBox") -> bool:
        """Verifica se sobrepoe com outra caixa."""
        return not (self.x2 < other.x or self.x > other.x2 or self.y2 < other.y or self.y > other.y2)

    def to_dict(self) -> dict[str, int]:
        """Converte para dicionario."""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }


@dataclass
class OCRWord:
    """Representa uma palavra reconhecida."""

    id: str = field(default_factory=lambda: str(uuid4()))
    text: str = ""
    confidence: float = 0.0
    bounding_box: BoundingBox | None = None
    language: str | None = None
    is_numeric: bool = False
    is_currency: bool = False
    is_date: bool = False
    font_size: int | None = None
    is_bold: bool = False
    is_italic: bool = False

    def __post_init__(self) -> None:
        """Detecta tipo de palavra."""
        if self.text:
            # Detectar numerico
            self.is_numeric = self.text.replace(".", "").replace(",", "").isdigit()
            # Detectar moeda
            self.is_currency = any(c in self.text for c in ["R$", "$", "€", "£", "¥"])

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario."""
        return {
            "id": self.id,
            "text": self.text,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
            "is_numeric": self.is_numeric,
            "is_currency": self.is_currency,
        }


@dataclass
class OCRLine:
    """Representa uma linha de texto reconhecida."""

    id: str = field(default_factory=lambda: str(uuid4()))
    text: str = ""
    confidence: float = 0.0
    bounding_box: BoundingBox | None = None
    words: list[OCRWord] = field(default_factory=list)
    line_number: int = 0
    is_header: bool = False
    is_footer: bool = False
    indent_level: int = 0

    @property
    def word_count(self) -> int:
        """Numero de palavras na linha."""
        return len(self.words)

    @property
    def avg_confidence(self) -> float:
        """Confianca media das palavras."""
        if not self.words:
            return self.confidence
        return sum(w.confidence for w in self.words) / len(self.words)

    def get_text(self, separator: str = " ") -> str:
        """Obtem texto da linha."""
        if self.words:
            return separator.join(w.text for w in self.words)
        return self.text

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario."""
        return {
            "id": self.id,
            "text": self.get_text(),
            "confidence": self.confidence,
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
            "words": [w.to_dict() for w in self.words],
            "line_number": self.line_number,
            "word_count": self.word_count,
        }


@dataclass
class OCRBlock:
    """Representa um bloco de texto (paragrafo, tabela, etc)."""

    id: str = field(default_factory=lambda: str(uuid4()))
    block_type: BlockType = BlockType.TEXT
    text: str = ""
    confidence: float = 0.0
    bounding_box: BoundingBox | None = None
    lines: list[OCRLine] = field(default_factory=list)
    page_number: int = 1
    block_number: int = 0

    # Para tabelas
    rows: int | None = None
    columns: int | None = None
    cells: list[list[str]] | None = None

    # Para codigos
    barcode_type: str | None = None  # CODE128, EAN13, QR, etc
    barcode_value: str | None = None

    @property
    def line_count(self) -> int:
        """Numero de linhas no bloco."""
        return len(self.lines)

    def get_text(self, separator: str = "\n") -> str:
        """Obtem texto do bloco."""
        if self.lines:
            return separator.join(line.get_text() for line in self.lines)
        return self.text

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario."""
        result = {
            "id": self.id,
            "block_type": self.block_type.value,
            "text": self.get_text(),
            "confidence": self.confidence,
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
            "lines": [line.to_dict() for line in self.lines],
            "page_number": self.page_number,
            "block_number": self.block_number,
        }

        if self.block_type == BlockType.TABLE:
            result["rows"] = self.rows
            result["columns"] = self.columns
            result["cells"] = self.cells

        if self.block_type in [BlockType.BARCODE, BlockType.QR_CODE]:
            result["barcode_type"] = self.barcode_type
            result["barcode_value"] = self.barcode_value

        return result


@dataclass
class OCRPage:
    """Representa uma pagina do documento."""

    page_number: int = 1
    width: int = 0
    height: int = 0
    blocks: list[OCRBlock] = field(default_factory=list)
    text: str = ""
    confidence: float = 0.0
    orientation: float | None = None  # Angulo de rotacao
    language: str | None = None

    @property
    def block_count(self) -> int:
        """Numero de blocos na pagina."""
        return len(self.blocks)

    @property
    def line_count(self) -> int:
        """Numero total de linhas."""
        return sum(len(block.lines) for block in self.blocks)

    def get_text(self) -> str:
        """Obtem texto completo da pagina."""
        if self.blocks:
            return "\n\n".join(block.get_text() for block in self.blocks)
        return self.text

    def get_tables(self) -> list[OCRBlock]:
        """Obtem blocos de tabela."""
        return [b for b in self.blocks if b.block_type == BlockType.TABLE]

    def get_barcodes(self) -> list[OCRBlock]:
        """Obtem blocos de codigo de barras."""
        return [b for b in self.blocks if b.block_type in [BlockType.BARCODE, BlockType.QR_CODE]]

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario."""
        return {
            "page_number": self.page_number,
            "width": self.width,
            "height": self.height,
            "blocks": [b.to_dict() for b in self.blocks],
            "text": self.get_text(),
            "confidence": self.confidence,
            "block_count": self.block_count,
            "line_count": self.line_count,
        }


@dataclass
class OCRResult:
    """
    Resultado completo do processamento OCR.

    Attributes:
        id: Identificador unico
        document_id: ID do documento
        provider: Provedor de OCR usado
        pages: Paginas processadas
        full_text: Texto completo extraido
        confidence: Confianca media
        language: Idioma detectado
        processing_time_ms: Tempo de processamento
        metadata: Metadados adicionais
        created_at: Data de criacao
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    document_id: str = ""
    provider: OCRProvider = OCRProvider.TESSERACT
    provider_version: str | None = None

    # Resultados
    pages: list[OCRPage] = field(default_factory=list)
    full_text: str = ""
    confidence: float = 0.0

    # Deteccao de idioma
    language: str = "pt"
    language_confidence: float = 0.0
    detected_languages: list[str] = field(default_factory=list)

    # Estatisticas
    total_blocks: int = 0
    total_lines: int = 0
    total_words: int = 0
    total_characters: int = 0

    # Elementos especiais encontrados
    tables_found: int = 0
    barcodes_found: int = 0
    signatures_found: int = 0
    handwriting_found: int = 0

    # Performance
    processing_time_ms: int = 0
    preprocessing_time_ms: int = 0

    # Raw response do provider
    raw_response: dict[str, Any] | None = None

    # Metadados
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Calcula estatisticas."""
        self._calculate_stats()

    def _calculate_stats(self) -> None:
        """Calcula estatisticas do resultado."""
        self.total_blocks = sum(p.block_count for p in self.pages)
        self.total_lines = sum(p.line_count for p in self.pages)

        # Contar palavras e caracteres
        self.total_words = 0
        self.total_characters = 0
        for page in self.pages:
            for block in page.blocks:
                for line in block.lines:
                    self.total_words += len(line.words)
                    self.total_characters += sum(len(w.text) for w in line.words)

        # Contar elementos especiais
        for page in self.pages:
            for block in page.blocks:
                if block.block_type == BlockType.TABLE:
                    self.tables_found += 1
                elif block.block_type in [BlockType.BARCODE, BlockType.QR_CODE]:
                    self.barcodes_found += 1
                elif block.block_type == BlockType.SIGNATURE:
                    self.signatures_found += 1
                elif block.block_type == BlockType.HANDWRITING:
                    self.handwriting_found += 1

    def get_full_text(self) -> str:
        """Obtem texto completo do documento."""
        if self.full_text:
            return self.full_text
        return "\n\n".join(page.get_text() for page in self.pages)

    def get_page(self, page_number: int) -> OCRPage | None:
        """Obtem pagina por numero."""
        for page in self.pages:
            if page.page_number == page_number:
                return page
        return None

    def search_text(self, query: str, case_sensitive: bool = False) -> list[OCRWord]:
        """Busca texto no documento."""
        results = []
        search_query = query if case_sensitive else query.lower()

        for page in self.pages:
            for block in page.blocks:
                for line in block.lines:
                    for word in line.words:
                        word_text = word.text if case_sensitive else word.text.lower()
                        if search_query in word_text:
                            results.append(word)

        return results

    def get_lines_containing(self, text: str) -> list[OCRLine]:
        """Obtem linhas contendo texto."""
        results = []
        search_text = text.lower()

        for page in self.pages:
            for block in page.blocks:
                for line in block.lines:
                    if search_text in line.get_text().lower():
                        results.append(line)

        return results

    def get_text_near(self, x: int, y: int, radius: int = 50) -> list[tuple[OCRWord, int]]:
        """Obtem palavras proximas a uma coordenada."""
        results = []

        for page in self.pages:
            for block in page.blocks:
                for line in block.lines:
                    for word in line.words:
                        if word.bounding_box:
                            center = word.bounding_box.center
                            distance = ((center[0] - x) ** 2 + (center[1] - y) ** 2) ** 0.5
                            if distance <= radius:
                                results.append((word, int(distance)))

        return sorted(results, key=lambda x: x[1])

    def get_all_tables(self) -> list[OCRBlock]:
        """Obtem todas as tabelas do documento."""
        tables = []
        for page in self.pages:
            tables.extend(page.get_tables())
        return tables

    def get_all_barcodes(self) -> list[dict[str, Any]]:
        """Obtem todos os codigos de barra."""
        barcodes = []
        for page in self.pages:
            for block in page.get_barcodes():
                barcodes.append(
                    {
                        "type": block.barcode_type,
                        "value": block.barcode_value,
                        "page": page.page_number,
                    }
                )
        return barcodes

    def get_statistics(self) -> dict[str, Any]:
        """Obtem estatisticas do OCR."""
        return {
            "provider": self.provider.value,
            "pages": len(self.pages),
            "blocks": self.total_blocks,
            "lines": self.total_lines,
            "words": self.total_words,
            "characters": self.total_characters,
            "confidence": self.confidence,
            "language": self.language,
            "tables_found": self.tables_found,
            "barcodes_found": self.barcodes_found,
            "processing_time_ms": self.processing_time_ms,
        }

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "provider": self.provider.value,
            "pages": [p.to_dict() for p in self.pages],
            "full_text": self.get_full_text(),
            "statistics": self.get_statistics(),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
