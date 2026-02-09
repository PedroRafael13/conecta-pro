"""ExtractionService - Servico de extracao de dados estruturados.

Sprint 39 - Document OCR.

Extrai dados estruturados de documentos:
- Campos de formularios
- Dados de notas fiscais
- Informacoes de identificacao
- Tabelas e listas
"""

import logging
import re
import uuid
from typing import Any

from modules.ai.ocr.models.document_template import RuleType
from modules.ai.ocr.models.extracted_field import FieldType

logger = logging.getLogger(__name__)


class ExtractionService:
    """Servico de extracao de dados estruturados."""

    def __init__(
        self,
        confidence_threshold: float = 0.7,
        enable_fuzzy_matching: bool = True,
        enable_auto_correction: bool = True,
    ):
        """Inicializa o servico.

        Args:
            confidence_threshold: Limite de confianca para extracao
            enable_fuzzy_matching: Habilita matching fuzzy
            enable_auto_correction: Habilita correcao automatica
        """
        self.confidence_threshold = confidence_threshold
        self.enable_fuzzy_matching = enable_fuzzy_matching
        self.enable_auto_correction = enable_auto_correction

        # Padroes de extracao por tipo
        self._init_patterns()

    def _init_patterns(self) -> None:
        """Inicializa padroes de extracao."""
        self.patterns = {
            # Identificacao
            FieldType.CPF: [
                r"\b(\d{3}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?\d{2})\b",
            ],
            FieldType.CNPJ: [
                r"\b(\d{2}[.\s]?\d{3}[.\s]?\d{3}[/.\s]?\d{4}[-.\s]?\d{2})\b",
            ],
            FieldType.RG: [
                r"\b(\d{1,2}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?[0-9X])\b",
            ],
            # Contato
            FieldType.EMAIL: [
                r"\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b",
            ],
            FieldType.PHONE: [
                r"\b\(?\d{2}\)?[\s.-]?\d{4,5}[-.\s]?\d{4}\b",
            ],
            FieldType.CEP: [
                r"\b(\d{5}[-.\s]?\d{3})\b",
            ],
            # Financeiro
            FieldType.CURRENCY: [
                r"R\$\s*([\d.,]+)",
                r"([\d.,]+)\s*(?:reais|BRL)",
            ],
            FieldType.BARCODE_BOLETO: [
                r"\b(\d{5}\.\d{5}\s?\d{5}\.\d{6}\s?\d{5}\.\d{6}\s?\d\s?\d{14})\b",
                r"\b(\d{47})\b",
            ],
            # Notas Fiscais
            FieldType.NF_NUMBER: [
                r"(?:N[ºo°]?|Numero)\s*:?\s*(\d{6,9})",
                r"NF[eE]?\s*:?\s*(\d+)",
            ],
            FieldType.NF_SERIE: [
                r"S[ée]rie\s*:?\s*(\d{1,3})",
            ],
            FieldType.NF_KEY: [
                r"\b(\d{44})\b",  # Chave de acesso NFe
            ],
            # Datas
            FieldType.DATE: [
                r"\b(\d{2}[/.-]\d{2}[/.-]\d{2,4})\b",
                r"\b(\d{4}[/.-]\d{2}[/.-]\d{2})\b",
            ],
            FieldType.DATETIME: [
                r"\b(\d{2}[/.-]\d{2}[/.-]\d{4}\s+\d{2}:\d{2}(?::\d{2})?)\b",
            ],
            FieldType.TIME: [
                r"\b(\d{2}:\d{2}(?::\d{2})?)\b",
            ],
            # Numeros
            FieldType.PERCENTAGE: [
                r"(\d+[,.]?\d*)\s*%",
            ],
            FieldType.INTEGER: [
                r"\b(\d+)\b",
            ],
            FieldType.DECIMAL: [
                r"\b(\d+[,.]\d+)\b",
            ],
        }

        # Labels comuns para deteccao key-value
        self.common_labels = {
            FieldType.CPF: ["CPF", "C.P.F.", "CPF/MF"],
            FieldType.CNPJ: ["CNPJ", "C.N.P.J.", "CNPJ/MF"],
            FieldType.EMAIL: ["E-MAIL", "EMAIL", "E-mail", "Correio Eletronico"],
            FieldType.PHONE: ["TELEFONE", "TEL", "FONE", "CELULAR"],
            FieldType.CEP: ["CEP", "C.E.P.", "Codigo Postal"],
            FieldType.DATE: ["DATA", "DT", "Emissao", "Vencimento"],
            FieldType.CURRENCY: ["VALOR", "TOTAL", "PRECO", "R$"],
            FieldType.NF_NUMBER: ["NUMERO", "NF", "NOTA", "N°"],
            FieldType.NAME: ["NOME", "RAZAO SOCIAL", "NOME FANTASIA"],
            FieldType.ADDRESS: ["ENDERECO", "LOGRADOURO", "RUA", "AV", "AVENIDA"],
        }

    def extract_fields(
        self,
        ocr_result: dict[str, Any],
        template: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Extrai campos do resultado OCR.

        Args:
            ocr_result: Resultado do OCR
            template: Template de extracao (opcional)

        Returns:
            Lista de campos extraidos
        """
        fields = []

        # Extrai texto completo
        raw_text = ocr_result.get("raw_text", "")
        lines = ocr_result.get("lines", [])

        # Se tem template, usa extracao guiada
        if template:
            fields = self._extract_with_template(ocr_result, template)
        else:
            # Extracao automatica
            fields = self._extract_automatic(raw_text, lines)

        # Pares chave-valor
        key_value_pairs = ocr_result.get("key_value_pairs", [])
        fields.extend(self._extract_from_key_value(key_value_pairs))

        # Tabelas
        tables = ocr_result.get("tables", [])
        fields.extend(self._extract_from_tables(tables))

        # Deduplica campos
        fields = self._deduplicate_fields(fields)

        return fields

    def _extract_automatic(
        self,
        text: str,
        lines: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Extracao automatica de campos.

        Args:
            text: Texto completo
            lines: Linhas do OCR

        Returns:
            Lista de campos extraidos
        """
        fields = []

        # Aplica todos os padroes conhecidos
        for field_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = match.group(1) if match.groups() else match.group(0)

                    # Normaliza valor
                    normalized = self._normalize_value(value, field_type)

                    # Encontra contexto
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    text[start:end]

                    field = {
                        "field_id": str(uuid.uuid4()),
                        "field_name": self._generate_field_name(field_type, len(fields)),
                        "field_type": field_type.value,
                        "raw_value": match.group(0),
                        "extracted_value": value,
                        "normalized_value": normalized,
                        "confidence": 0.8,
                        "source_text": match.group(0),
                        "context_before": text[start : match.start()],
                        "context_after": text[match.end() : end],
                        "extraction_method": "regex",
                    }

                    fields.append(field)

        return fields

    def _extract_with_template(
        self,
        ocr_result: dict[str, Any],
        template: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Extrai campos usando template.

        Args:
            ocr_result: Resultado OCR
            template: Template de extracao

        Returns:
            Lista de campos extraidos
        """
        fields = []
        text = ocr_result.get("raw_text", "")

        template_fields = template.get("fields", [])
        for template_field in template_fields:
            field_name = template_field.get("name")
            field_type = FieldType(template_field.get("field_type", "text"))
            rules = template_field.get("extraction_rules", [])

            value = None
            confidence = 0.0
            method = None

            # Aplica regras de extracao
            for rule in rules:
                rule_type = RuleType(rule.get("type", "regex"))

                if rule_type == RuleType.REGEX:
                    value, confidence = self._extract_by_regex(
                        text,
                        rule.get("pattern", ""),
                        rule.get("group", 0),
                    )
                    method = "regex"

                elif rule_type == RuleType.KEYWORD:
                    value, confidence = self._extract_by_keyword(
                        text,
                        rule.get("keyword", ""),
                        rule.get("offset_x", 0),
                        rule.get("width", 200),
                    )
                    method = "keyword"

                elif rule_type == RuleType.AFTER_LABEL:
                    value, confidence = self._extract_after_label(
                        text,
                        rule.get("label", ""),
                        rule.get("max_distance", 100),
                    )
                    method = "after_label"

                if value and confidence >= self.confidence_threshold:
                    break

            if value:
                normalized = self._normalize_value(value, field_type)

                field = {
                    "field_id": str(uuid.uuid4()),
                    "field_name": field_name,
                    "field_type": field_type.value,
                    "template_field_id": template_field.get("id"),
                    "raw_value": value,
                    "extracted_value": value,
                    "normalized_value": normalized,
                    "confidence": confidence,
                    "extraction_method": method,
                    "is_required": template_field.get("is_required", False),
                }

                fields.append(field)

        return fields

    def _extract_by_regex(
        self,
        text: str,
        pattern: str,
        group: int = 0,
    ) -> tuple[str | None, float]:
        """Extrai por expressao regular.

        Args:
            text: Texto para busca
            pattern: Padrao regex
            group: Grupo de captura

        Returns:
            Tupla (valor, confianca)
        """
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(group) if group > 0 else match.group(0)
                return value.strip(), 0.85
        except re.error as e:
            logger.warning(f"Regex invalido: {pattern} - {e}")

        return None, 0.0

    def _extract_by_keyword(
        self,
        text: str,
        keyword: str,
        _offset_x: int,
        width: int,
    ) -> tuple[str | None, float]:
        """Extrai valor proximo a keyword.

        Args:
            text: Texto para busca
            keyword: Palavra-chave
            offset_x: Offset horizontal
            width: Largura do campo

        Returns:
            Tupla (valor, confianca)
        """
        # Busca keyword
        pattern = rf"{re.escape(keyword)}\s*:?\s*(\S+.*?)(?:\n|$)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            value = match.group(1).strip()
            return value, 0.8

        return None, 0.0

    def _extract_after_label(
        self,
        text: str,
        label: str,
        max_distance: int,
    ) -> tuple[str | None, float]:
        """Extrai valor apos um label.

        Args:
            text: Texto para busca
            label: Label a procurar
            max_distance: Distancia maxima

        Returns:
            Tupla (valor, confianca)
        """
        pattern = rf"{re.escape(label)}\s*:?\s*(.{{1,{max_distance}}}?)(?:\n|[A-Z]{{2,}})"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            value = match.group(1).strip()
            return value, 0.75

        return None, 0.0

    def _extract_from_key_value(
        self,
        pairs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Extrai campos de pares chave-valor.

        Args:
            pairs: Pares chave-valor do OCR

        Returns:
            Lista de campos
        """
        fields = []

        for pair in pairs:
            key = pair.get("key", "").upper()
            value = pair.get("value", "")
            confidence = pair.get("confidence", 0.7)

            # Detecta tipo pelo label
            field_type = self._detect_type_by_label(key)

            field = {
                "field_id": str(uuid.uuid4()),
                "field_name": self._sanitize_field_name(key),
                "field_label": key,
                "field_type": field_type.value,
                "raw_value": value,
                "extracted_value": value,
                "normalized_value": self._normalize_value(value, field_type),
                "confidence": confidence,
                "extraction_method": "key_value",
            }

            fields.append(field)

        return fields

    def _extract_from_tables(
        self,
        tables: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Extrai campos de tabelas.

        Args:
            tables: Tabelas detectadas

        Returns:
            Lista de campos
        """
        fields = []

        for table_idx, table in enumerate(tables):
            cells = table.get("cells", [])
            table.get("rows", 1)
            table.get("columns", 1)

            # Primeira linha como header
            headers = []
            for cell in cells:
                if cell.get("row", 0) == 0:
                    headers.append(cell.get("text", f"col_{cell.get('col', 0)}"))

            # Demais linhas como dados
            for cell in cells:
                row = cell.get("row", 0)
                col = cell.get("col", 0)

                if row == 0:  # Skip header
                    continue

                header = headers[col] if col < len(headers) else f"col_{col}"

                field = {
                    "field_id": str(uuid.uuid4()),
                    "field_name": f"table_{table_idx}_{header}_row_{row}",
                    "field_label": header,
                    "field_type": FieldType.TEXT.value,
                    "raw_value": cell.get("text", ""),
                    "extracted_value": cell.get("text", ""),
                    "confidence": cell.get("confidence", 0.7),
                    "extraction_method": "table",
                    "is_from_table": True,
                }

                fields.append(field)

        return fields

    def _detect_type_by_label(self, label: str) -> FieldType:
        """Detecta tipo de campo pelo label.

        Args:
            label: Label do campo

        Returns:
            Tipo detectado
        """
        label_upper = label.upper()

        for field_type, labels in self.common_labels.items():
            for known_label in labels:
                if known_label.upper() in label_upper:
                    return field_type

        return FieldType.TEXT

    def _normalize_value(
        self,
        value: str,
        field_type: FieldType,
    ) -> str:
        """Normaliza valor baseado no tipo.

        Args:
            value: Valor a normalizar
            field_type: Tipo do campo

        Returns:
            Valor normalizado
        """
        if not value:
            return ""

        value = value.strip()

        if field_type == FieldType.CPF:
            # Remove pontuacao
            return re.sub(r"[.\-\s]", "", value)

        if field_type == FieldType.CNPJ:
            # Remove pontuacao
            return re.sub(r"[.\-/\s]", "", value)

        if field_type == FieldType.PHONE:
            # Remove pontuacao, mantem numeros
            return re.sub(r"[^\d]", "", value)

        if field_type == FieldType.CEP:
            # Remove hifen
            return re.sub(r"[\-\s]", "", value)

        if field_type == FieldType.CURRENCY:
            # Normaliza para formato numerico
            value = re.sub(r"[R$\s]", "", value)
            value = value.replace(".", "").replace(",", ".")
            return value

        if field_type == FieldType.EMAIL:
            return value.lower()

        if field_type in [FieldType.DATE, FieldType.DATETIME]:
            # Tenta normalizar para formato padrao
            return self._normalize_date(value)

        return value

    def _normalize_date(self, value: str) -> str:
        """Normaliza data para formato padrao.

        Args:
            value: Data a normalizar

        Returns:
            Data normalizada (YYYY-MM-DD)
        """
        # Tenta varios formatos
        date_patterns = [
            (r"(\d{2})/(\d{2})/(\d{4})", r"\3-\2-\1"),  # DD/MM/YYYY -> YYYY-MM-DD
            (r"(\d{2})-(\d{2})-(\d{4})", r"\3-\2-\1"),  # DD-MM-YYYY -> YYYY-MM-DD
            (r"(\d{4})/(\d{2})/(\d{2})", r"\1-\2-\3"),  # YYYY/MM/DD -> YYYY-MM-DD
            (r"(\d{2})/(\d{2})/(\d{2})", r"20\3-\2-\1"),  # DD/MM/YY -> YYYY-MM-DD
        ]

        for pattern, replacement in date_patterns:
            if re.match(pattern, value):
                return re.sub(pattern, replacement, value)

        return value

    def _generate_field_name(
        self,
        field_type: FieldType,
        index: int,
    ) -> str:
        """Gera nome de campo.

        Args:
            field_type: Tipo do campo
            index: Indice do campo

        Returns:
            Nome gerado
        """
        return f"{field_type.value}_{index}"

    def _sanitize_field_name(self, name: str) -> str:
        """Sanitiza nome de campo.

        Args:
            name: Nome a sanitizar

        Returns:
            Nome sanitizado
        """
        # Remove caracteres especiais
        name = re.sub(r"[^\w\s]", "", name)
        # Substitui espacos por underscore
        name = re.sub(r"\s+", "_", name)
        # Lowercase
        name = name.lower()
        # Limita tamanho
        return name[:50]

    def _deduplicate_fields(
        self,
        fields: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Remove campos duplicados.

        Args:
            fields: Lista de campos

        Returns:
            Lista sem duplicatas
        """
        seen = set()
        unique_fields = []

        for field in fields:
            # Chave de deduplicacao
            key = (
                field.get("field_type"),
                field.get("normalized_value"),
            )

            if key not in seen:
                seen.add(key)
                unique_fields.append(field)
            else:
                # Se duplicado, mantem o com maior confianca
                for i, existing in enumerate(unique_fields):
                    existing_key = (
                        existing.get("field_type"),
                        existing.get("normalized_value"),
                    )
                    if existing_key == key:
                        if field.get("confidence", 0) > existing.get("confidence", 0):
                            unique_fields[i] = field
                        break

        return unique_fields
