"""
Modelo de Campo Extraido.

Define estruturas para campos extraidos de documentos,
incluindo tipo, valor, confianca e validacao.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4


class FieldType(str, Enum):
    """Tipos de campos suportados."""

    # Texto
    TEXT = "text"
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    CITY = "city"
    STATE = "state"
    COUNTRY = "country"
    ZIP_CODE = "zip_code"

    # Documentos
    CPF = "cpf"
    CNPJ = "cnpj"
    RG = "rg"
    CNH = "cnh"
    PASSPORT = "passport"
    VOTER_ID = "voter_id"

    # Numeros
    NUMBER = "number"
    INTEGER = "integer"
    DECIMAL = "decimal"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"

    # Datas
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"

    # Financeiros
    BANK_ACCOUNT = "bank_account"
    BANK_AGENCY = "bank_agency"
    BANK_CODE = "bank_code"
    BARCODE = "barcode"
    PIX_KEY = "pix_key"

    # NFe/Boleto
    NFE_NUMBER = "nfe_number"
    NFE_SERIES = "nfe_series"
    NFE_KEY = "nfe_key"
    BOLETO_LINE = "boleto_line"
    BOLETO_BARCODE = "boleto_barcode"

    # Outros
    URL = "url"
    PLATE = "plate"  # Placa de veiculo
    BOOLEAN = "boolean"
    LIST = "list"
    OBJECT = "object"
    UNKNOWN = "unknown"


class FieldConfidence(str, Enum):
    """Niveis de confianca."""

    VERY_HIGH = "very_high"  # >= 95%
    HIGH = "high"  # >= 85%
    MEDIUM = "medium"  # >= 70%
    LOW = "low"  # >= 50%
    VERY_LOW = "very_low"  # < 50%

    @classmethod
    def from_score(cls, score: float) -> "FieldConfidence":
        """Obtem nivel de confianca a partir do score."""
        if score >= 0.95:
            return cls.VERY_HIGH
        if score >= 0.85:
            return cls.HIGH
        if score >= 0.70:
            return cls.MEDIUM
        if score >= 0.50:
            return cls.LOW
        return cls.VERY_LOW


class ExtractionMethod(str, Enum):
    """Metodo de extracao utilizado."""

    REGEX = "regex"
    NLP = "nlp"
    TEMPLATE = "template"
    ML_MODEL = "ml_model"
    RULE_BASED = "rule_based"
    POSITION = "position"
    KEYWORD_ANCHOR = "keyword_anchor"
    TABLE = "table"
    FORM_FIELD = "form_field"
    BARCODE = "barcode"
    QR_CODE = "qr_code"
    MANUAL = "manual"


@dataclass
class FieldLocation:
    """Localizacao do campo no documento."""

    page: int = 1
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    line_number: Optional[int] = None
    word_indices: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "page": self.page,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "line_number": self.line_number,
        }


@dataclass
class FieldValidation:
    """Resultado de validacao do campo."""

    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    formatted_value: Optional[str] = None
    normalized_value: Optional[Any] = None

    def add_error(self, error: str) -> None:
        """Adiciona erro de validacao."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Adiciona aviso de validacao."""
        self.warnings.append(warning)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "formatted_value": self.formatted_value,
            "normalized_value": str(self.normalized_value) if self.normalized_value else None,
        }


@dataclass
class ExtractedField:
    """
    Representa um campo extraido do documento.

    Attributes:
        id: Identificador unico
        document_id: ID do documento
        field_name: Nome do campo
        field_type: Tipo do campo
        raw_value: Valor bruto extraido
        normalized_value: Valor normalizado
        confidence: Score de confianca (0-1)
        method: Metodo de extracao
        location: Localizacao no documento
        validation: Resultado da validacao
        is_required: Se e obrigatorio
        is_verified: Se foi verificado manualmente
        alternatives: Valores alternativos
        metadata: Metadados adicionais
        created_at: Data de extracao
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    document_id: str = ""
    ocr_result_id: Optional[str] = None
    template_id: Optional[str] = None

    # Identificacao
    field_name: str = ""
    field_label: Optional[str] = None
    field_type: FieldType = FieldType.TEXT
    field_group: Optional[str] = None  # Agrupamento logico

    # Valores
    raw_value: str = ""
    normalized_value: Optional[Any] = None
    display_value: Optional[str] = None
    original_text: Optional[str] = None  # Texto original do OCR

    # Confianca
    confidence: float = 0.0
    confidence_level: FieldConfidence = FieldConfidence.LOW
    method: ExtractionMethod = ExtractionMethod.REGEX

    # Localizacao
    location: Optional[FieldLocation] = None
    anchor_text: Optional[str] = None  # Texto ancora para extracao

    # Validacao
    validation: Optional[FieldValidation] = None
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)

    # Status
    is_required: bool = False
    is_verified: bool = False
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    is_editable: bool = True

    # Alternativas
    alternatives: List[Dict[str, Any]] = field(default_factory=list)

    # Metadados
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Inicializa campos derivados."""
        self.confidence_level = FieldConfidence.from_score(self.confidence)
        if not self.display_value:
            self.display_value = self._format_display_value()

    def _format_display_value(self) -> str:
        """Formata valor para exibicao."""
        if self.normalized_value is None:
            return self.raw_value

        if self.field_type == FieldType.CPF:
            return self._format_cpf(str(self.normalized_value))
        if self.field_type == FieldType.CNPJ:
            return self._format_cnpj(str(self.normalized_value))
        if self.field_type == FieldType.PHONE:
            return self._format_phone(str(self.normalized_value))
        if self.field_type == FieldType.CURRENCY:
            return self._format_currency(self.normalized_value)
        if self.field_type == FieldType.DATE:
            if isinstance(self.normalized_value, (date, datetime)):
                return self.normalized_value.strftime("%d/%m/%Y")

        return str(self.normalized_value)

    @staticmethod
    def _format_cpf(value: str) -> str:
        """Formata CPF."""
        digits = "".join(filter(str.isdigit, value))
        if len(digits) == 11:
            return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
        return value

    @staticmethod
    def _format_cnpj(value: str) -> str:
        """Formata CNPJ."""
        digits = "".join(filter(str.isdigit, value))
        if len(digits) == 14:
            return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
        return value

    @staticmethod
    def _format_phone(value: str) -> str:
        """Formata telefone."""
        digits = "".join(filter(str.isdigit, value))
        if len(digits) == 11:
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        if len(digits) == 10:
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        return value

    @staticmethod
    def _format_currency(value: Union[Decimal, float, int]) -> str:
        """Formata moeda."""
        try:
            amount = Decimal(str(value))
            return f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return str(value)

    def normalize(self) -> Any:
        """Normaliza o valor extraido."""
        if not self.raw_value:
            return None

        normalizers = {
            FieldType.CPF: self._normalize_cpf,
            FieldType.CNPJ: self._normalize_cnpj,
            FieldType.PHONE: self._normalize_phone,
            FieldType.DATE: self._normalize_date,
            FieldType.CURRENCY: self._normalize_currency,
            FieldType.NUMBER: self._normalize_number,
            FieldType.INTEGER: self._normalize_integer,
            FieldType.DECIMAL: self._normalize_decimal,
            FieldType.EMAIL: self._normalize_email,
        }

        normalizer = normalizers.get(self.field_type)
        if normalizer:
            self.normalized_value = normalizer(self.raw_value)
        else:
            self.normalized_value = self.raw_value.strip()

        self.display_value = self._format_display_value()
        return self.normalized_value

    def _normalize_cpf(self, value: str) -> str:
        """Normaliza CPF."""
        return "".join(filter(str.isdigit, value))

    def _normalize_cnpj(self, value: str) -> str:
        """Normaliza CNPJ."""
        return "".join(filter(str.isdigit, value))

    def _normalize_phone(self, value: str) -> str:
        """Normaliza telefone."""
        return "".join(filter(str.isdigit, value))

    def _normalize_date(self, value: str) -> Optional[date]:
        """Normaliza data."""
        import re

        # Padroes de data comuns
        patterns = [
            (r"(\d{2})/(\d{2})/(\d{4})", "%d/%m/%Y"),
            (r"(\d{2})-(\d{2})-(\d{4})", "%d-%m-%Y"),
            (r"(\d{4})-(\d{2})-(\d{2})", "%Y-%m-%d"),
            (r"(\d{2})\.(\d{2})\.(\d{4})", "%d.%m.%Y"),
        ]

        for pattern, fmt in patterns:
            if re.match(pattern, value):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue

        return None

    def _normalize_currency(self, value: str) -> Optional[Decimal]:
        """Normaliza valor monetario."""
        try:
            # Remove simbolos e formata
            clean = value.replace("R$", "").replace("$", "").strip()
            # Trata formato brasileiro (1.234,56)
            if "," in clean and "." in clean:
                clean = clean.replace(".", "").replace(",", ".")
            elif "," in clean:
                clean = clean.replace(",", ".")
            return Decimal(clean)
        except (ValueError, TypeError):
            return None

    def _normalize_number(self, value: str) -> Optional[float]:
        """Normaliza numero."""
        try:
            clean = value.replace(",", ".")
            return float(clean)
        except ValueError:
            return None

    def _normalize_integer(self, value: str) -> Optional[int]:
        """Normaliza inteiro."""
        try:
            return int("".join(filter(str.isdigit, value)))
        except ValueError:
            return None

    def _normalize_decimal(self, value: str) -> Optional[Decimal]:
        """Normaliza decimal."""
        try:
            clean = value.replace(",", ".")
            return Decimal(clean)
        except (ValueError, TypeError):
            return None

    def _normalize_email(self, value: str) -> str:
        """Normaliza email."""
        return value.strip().lower()

    def verify(self, user_id: str, corrected_value: Optional[str] = None) -> None:
        """Marca campo como verificado."""
        self.is_verified = True
        self.verified_by = user_id
        self.verified_at = datetime.utcnow()
        if corrected_value:
            self.raw_value = corrected_value
            self.normalize()
        self.updated_at = datetime.utcnow()

    def add_alternative(
        self, value: str, confidence: float, source: str
    ) -> None:
        """Adiciona valor alternativo."""
        self.alternatives.append(
            {
                "value": value,
                "confidence": confidence,
                "source": source,
            }
        )

    def get_best_value(self) -> str:
        """Obtem melhor valor (verificado ou maior confianca)."""
        if self.is_verified:
            return self.raw_value

        if self.alternatives:
            best = max(self.alternatives, key=lambda x: x["confidence"])
            if best["confidence"] > self.confidence:
                return best["value"]

        return self.raw_value

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "field_name": self.field_name,
            "field_label": self.field_label,
            "field_type": self.field_type.value,
            "field_group": self.field_group,
            "raw_value": self.raw_value,
            "normalized_value": (
                str(self.normalized_value) if self.normalized_value else None
            ),
            "display_value": self.display_value,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level.value,
            "method": self.method.value,
            "location": self.location.to_dict() if self.location else None,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "is_required": self.is_required,
            "is_verified": self.is_verified,
            "alternatives": self.alternatives,
            "created_at": self.created_at.isoformat(),
        }
