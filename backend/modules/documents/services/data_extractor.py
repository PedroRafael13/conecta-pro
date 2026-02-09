"""
Data Extractor Service.

Responsavel pela extracao estruturada de dados de documentos
usando templates, regras e padroes configurados.
"""

import logging
import re
import time
from dataclasses import dataclass, field
from re import Pattern
from typing import Any

from ..models.extracted_field import (
    ExtractedField,
    ExtractionMethod,
    FieldLocation,
    FieldType,
)
from ..models.extraction_template import (
    ExtractionTemplate,
    RuleType,
    TemplateField,
    TemplateRule,
)
from ..models.ocr_result import OCRResult

logger = logging.getLogger(__name__)


@dataclass
class ExtractionConfig:
    """Configuracao do extrator."""

    # Limites
    min_confidence: float = 0.5
    max_alternatives: int = 3

    # Comportamento
    use_fuzzy_matching: bool = True
    fuzzy_threshold: float = 0.8
    case_sensitive: bool = False
    normalize_whitespace: bool = True

    # Melhorias
    apply_corrections: bool = True
    infer_missing_fields: bool = True

    # Performance
    timeout_seconds: int = 60


@dataclass
class ExtractionContext:
    """Contexto para extracao."""

    ocr_result: OCRResult
    template: ExtractionTemplate | None = None
    document_type: str | None = None
    extracted_fields: dict[str, ExtractedField] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class DataExtractor:
    """
    Extrator de dados estruturados.

    Extrai campos de documentos usando templates,
    regex, ancoras e heuristicas.
    """

    # Padroes comuns brasileiros
    PATTERNS = {
        "cpf": r"\b\d{3}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?\d{2}\b",
        "cnpj": r"\b\d{2}[.\s]?\d{3}[.\s]?\d{3}[/.\s]?\d{4}[-.\s]?\d{2}\b",
        "cep": r"\b\d{5}[-.\s]?\d{3}\b",
        "phone": r"\b(?:\+55\s?)?(?:\(?\d{2}\)?[-.\s]?)?\d{4,5}[-.\s]?\d{4}\b",
        "email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        "date_br": r"\b\d{2}[/.-]\d{2}[/.-]\d{4}\b",
        "date_iso": r"\b\d{4}[-/]\d{2}[-/]\d{2}\b",
        "currency_br": r"R\$\s*[\d.,]+",
        "currency_generic": r"\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\b",
        "nfe_key": r"\b\d{44}\b",
        "boleto_line": r"\b\d{5}[.\s]?\d{5}[.\s]?\d{5}[.\s]?\d{6}[.\s]?\d{5}[.\s]?\d{6}[.\s]?\d[.\s]?\d{14}\b",
        "plate": r"\b[A-Z]{3}[-\s]?\d[A-Z0-9]\d{2}\b",
        "rg": r"\b\d{1,2}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?[0-9Xx]\b",
        "pis": r"\b\d{3}[.\s]?\d{5}[.\s]?\d{2}[-.\s]?\d\b",
    }

    # Mapeamento de tipo de campo para padrao
    FIELD_PATTERNS = {
        FieldType.CPF: ["cpf"],
        FieldType.CNPJ: ["cnpj"],
        FieldType.ZIP_CODE: ["cep"],
        FieldType.PHONE: ["phone"],
        FieldType.EMAIL: ["email"],
        FieldType.DATE: ["date_br", "date_iso"],
        FieldType.CURRENCY: ["currency_br", "currency_generic"],
        FieldType.NFE_KEY: ["nfe_key"],
        FieldType.BOLETO_LINE: ["boleto_line"],
        FieldType.PLATE: ["plate"],
        FieldType.RG: ["rg"],
    }

    def __init__(self, config: ExtractionConfig | None = None):
        """
        Inicializa extrator.

        Args:
            config: Configuracao do extrator
        """
        self.config = config or ExtractionConfig()
        self._compiled_patterns: dict[str, Pattern] = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compila padroes regex."""
        flags = 0 if self.config.case_sensitive else re.IGNORECASE
        for name, pattern in self.PATTERNS.items():
            self._compiled_patterns[name] = re.compile(pattern, flags)

    async def extract(
        self,
        ocr_result: OCRResult,
        template: ExtractionTemplate | None = None,
        field_types: list[FieldType] | None = None,
    ) -> list[ExtractedField]:
        """
        Extrai dados do resultado OCR.

        Args:
            ocr_result: Resultado do OCR
            template: Template de extracao (opcional)
            field_types: Tipos de campo a extrair (opcional)

        Returns:
            Lista de campos extraidos
        """
        start_time = time.time()
        context = ExtractionContext(ocr_result=ocr_result, template=template)

        extracted_fields = []

        # Extracao por template
        if template:
            template_fields = await self._extract_by_template(context)
            extracted_fields.extend(template_fields)

        # Extracao automatica por tipo
        if field_types:
            auto_fields = await self._extract_by_types(context, field_types)
            extracted_fields.extend(auto_fields)

        # Se nenhum template/tipo, fazer extracao generica
        if not template and not field_types:
            generic_fields = await self._extract_generic(context)
            extracted_fields.extend(generic_fields)

        # Pos-processamento
        for ext_field in extracted_fields:
            ext_field.normalize()

        # Deduplicar
        extracted_fields = self._deduplicate_fields(extracted_fields)

        elapsed = int((time.time() - start_time) * 1000)
        logger.info(f"Extracao concluida: {len(extracted_fields)} campos em {elapsed}ms")

        return extracted_fields

    async def _extract_by_template(self, context: ExtractionContext) -> list[ExtractedField]:
        """Extrai campos usando template."""
        fields = []
        template = context.template

        for template_field in template.fields:
            field = await self._extract_field(context, template_field)
            if field:
                fields.append(field)

        return fields

    async def _extract_field(
        self,
        context: ExtractionContext,
        template_field: TemplateField,
    ) -> ExtractedField | None:
        """Extrai um campo especifico."""
        best_match = None
        best_confidence = 0

        for rule in template_field.rules:
            result = await self._apply_rule(context, rule)
            if result and result[1] > best_confidence:
                best_match = result
                best_confidence = result[1]

        if best_match:
            value, confidence, method, location = best_match

            # Aplicar pos-processadores
            if template_field.primary_rule:
                value = template_field.primary_rule.apply_post_processors(value)

            field = ExtractedField(
                document_id=context.ocr_result.document_id,
                field_name=template_field.name,
                field_label=template_field.label,
                field_type=self._map_field_type(template_field.field_type),
                field_group=template_field.group,
                raw_value=value,
                confidence=confidence,
                method=method,
                location=location,
                is_required=template_field.required,
                template_id=context.template.id if context.template else None,
            )

            return field

        # Campo obrigatorio nao encontrado
        if template_field.required:
            logger.warning(f"Campo obrigatorio nao encontrado: {template_field.name}")
            if template_field.default_value:
                return ExtractedField(
                    document_id=context.ocr_result.document_id,
                    field_name=template_field.name,
                    field_label=template_field.label,
                    field_type=self._map_field_type(template_field.field_type),
                    raw_value=template_field.default_value,
                    confidence=0.0,
                    method=ExtractionMethod.RULE_BASED,
                    is_required=True,
                    validation_errors=["Campo extraido com valor padrao"],
                )

        return None

    async def _apply_rule(
        self,
        context: ExtractionContext,
        rule: TemplateRule,
    ) -> tuple[str, float, ExtractionMethod, FieldLocation | None] | None:
        """Aplica uma regra de extracao."""
        full_text = context.ocr_result.get_full_text()

        if rule.rule_type == RuleType.REGEX:
            return self._apply_regex_rule(context, rule, full_text)

        elif rule.rule_type == RuleType.KEYWORD_ANCHOR:
            return self._apply_anchor_rule(context, rule, full_text)

        elif rule.rule_type == RuleType.AFTER_LABEL:
            return self._apply_after_label_rule(context, rule)

        elif rule.rule_type == RuleType.BETWEEN_LABELS:
            return self._apply_between_labels_rule(context, rule, full_text)

        elif rule.rule_type == RuleType.LINE_MATCH:
            return self._apply_line_match_rule(context, rule)

        elif rule.rule_type == RuleType.POSITION:
            return self._apply_position_rule(context, rule)

        elif rule.rule_type == RuleType.TABLE_CELL:
            return self._apply_table_rule(context, rule)

        return None

    def _apply_regex_rule(
        self,
        context: ExtractionContext,
        rule: TemplateRule,
        text: str,
    ) -> tuple[str, float, ExtractionMethod, FieldLocation | None] | None:
        """Aplica regra regex."""
        if not rule.pattern:
            return None

        try:
            compiled = rule.compile_pattern()
            if not compiled:
                return None

            match = compiled.search(text)
            if match:
                value = match.group(rule.group) if rule.group <= len(match.groups()) else match.group(0)

                # Validar valor
                if rule.min_length and len(value) < rule.min_length:
                    return None
                if rule.max_length and len(value) > rule.max_length:
                    return None

                # Estimar confianca baseada na especificidade do padrao
                confidence = 0.85

                return (value, confidence, ExtractionMethod.REGEX, None)

        except Exception as e:
            logger.warning(f"Erro ao aplicar regex: {e}")

        return None

    def _apply_anchor_rule(
        self,
        context: ExtractionContext,
        rule: TemplateRule,
        text: str,
    ) -> tuple[str, float, ExtractionMethod, FieldLocation | None] | None:
        """Aplica regra de ancora."""
        if not rule.anchor:
            return None

        # Encontrar ancora no texto
        anchor_lower = rule.anchor.lower()
        text_lower = text.lower()

        pos = text_lower.find(anchor_lower)
        if pos == -1:
            return None

        # Extrair texto apos ancora
        if rule.anchor_position == "after":
            start = pos + len(rule.anchor)
            # Pegar ate fim da linha ou proximo campo
            end = text.find("\n", start)
            if end == -1:
                end = min(start + 100, len(text))
            value = text[start:end].strip()

        elif rule.anchor_position == "before":
            end = pos
            start = text.rfind("\n", 0, end)
            if start == -1:
                start = max(0, end - 100)
            value = text[start:end].strip()

        else:
            return None

        # Aplicar padrao adicional se existir
        if rule.pattern and value:
            match = re.search(rule.pattern, value, re.IGNORECASE)
            if match:
                value = match.group(rule.group if rule.group else 0)

        if value:
            return (value, 0.80, ExtractionMethod.KEYWORD_ANCHOR, None)

        return None

    def _apply_after_label_rule(
        self,
        context: ExtractionContext,
        rule: TemplateRule,
    ) -> tuple[str, float, ExtractionMethod, FieldLocation | None] | None:
        """Extrai valor apos um label."""
        if not rule.anchor:
            return None

        # Procurar nas linhas do OCR
        for page in context.ocr_result.pages:
            for block in page.blocks:
                for i, line in enumerate(block.lines):
                    line_text = line.get_text().lower()

                    if rule.anchor.lower() in line_text:
                        # Valor pode estar na mesma linha ou na proxima
                        parts = line_text.split(rule.anchor.lower())
                        if len(parts) > 1 and parts[1].strip():
                            value = parts[1].strip()
                            # Aplicar padrao se existir
                            if rule.pattern:
                                match = re.search(rule.pattern, value, re.IGNORECASE)
                                if match:
                                    value = match.group(0)
                            return (
                                value,
                                0.85,
                                ExtractionMethod.KEYWORD_ANCHOR,
                                FieldLocation(
                                    page=page.page_number,
                                    line_number=line.line_number,
                                ),
                            )

                        # Tentar proxima linha
                        if i + 1 < len(block.lines):
                            next_line = block.lines[i + 1]
                            value = next_line.get_text().strip()
                            if value:
                                return (
                                    value,
                                    0.75,
                                    ExtractionMethod.KEYWORD_ANCHOR,
                                    FieldLocation(
                                        page=page.page_number,
                                        line_number=next_line.line_number,
                                    ),
                                )

        return None

    def _apply_between_labels_rule(
        self,
        context: ExtractionContext,
        rule: TemplateRule,
        text: str,
    ) -> tuple[str, float, ExtractionMethod, FieldLocation | None] | None:
        """Extrai valor entre dois labels."""
        # Usar params para start/end labels
        start_label = rule.anchor
        end_label = rule.params.get("end_label", "")

        if not start_label:
            return None

        text_lower = text.lower()
        start_pos = text_lower.find(start_label.lower())
        if start_pos == -1:
            return None

        start_pos += len(start_label)

        if end_label:
            end_pos = text_lower.find(end_label.lower(), start_pos)
            if end_pos == -1:
                end_pos = text.find("\n", start_pos)
        else:
            end_pos = text.find("\n", start_pos)

        if end_pos == -1:
            end_pos = min(start_pos + 200, len(text))

        value = text[start_pos:end_pos].strip()

        if value:
            return (value, 0.75, ExtractionMethod.KEYWORD_ANCHOR, None)

        return None

    def _apply_line_match_rule(
        self,
        context: ExtractionContext,
        rule: TemplateRule,
    ) -> tuple[str, float, ExtractionMethod, FieldLocation | None] | None:
        """Extrai linha que corresponde a um padrao."""
        if not rule.pattern:
            return None

        compiled = rule.compile_pattern()
        if not compiled:
            return None

        for page in context.ocr_result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = line.get_text()
                    match = compiled.search(line_text)
                    if match:
                        value = match.group(rule.group) if rule.group else match.group(0)
                        return (
                            value,
                            0.80,
                            ExtractionMethod.REGEX,
                            FieldLocation(
                                page=page.page_number,
                                line_number=line.line_number,
                            ),
                        )

        return None

    def _apply_position_rule(
        self,
        context: ExtractionContext,
        rule: TemplateRule,
    ) -> tuple[str, float, ExtractionMethod, FieldLocation | None] | None:
        """Extrai por posicao na pagina."""
        page_num = rule.page or 1

        page = context.ocr_result.get_page(page_num)
        if not page:
            return None

        # Encontrar palavras na regiao
        words_in_region = []
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    if word.bounding_box:
                        bbox = word.bounding_box
                        # Verificar se esta na regiao
                        if (
                            (rule.x_min is None or bbox.x >= rule.x_min)
                            and (rule.x_max is None or bbox.x2 <= rule.x_max)
                            and (rule.y_min is None or bbox.y >= rule.y_min)
                            and (rule.y_max is None or bbox.y2 <= rule.y_max)
                        ):
                            words_in_region.append(word)

        if words_in_region:
            # Ordenar por posicao
            words_in_region.sort(key=lambda w: (w.bounding_box.y, w.bounding_box.x))
            value = " ".join(w.text for w in words_in_region)

            return (
                value,
                0.70,
                ExtractionMethod.POSITION,
                FieldLocation(
                    page=page_num,
                    x=words_in_region[0].bounding_box.x,
                    y=words_in_region[0].bounding_box.y,
                ),
            )

        return None

    def _apply_table_rule(
        self,
        context: ExtractionContext,
        rule: TemplateRule,
    ) -> tuple[str, float, ExtractionMethod, FieldLocation | None] | None:
        """Extrai de celula de tabela."""
        tables = context.ocr_result.get_all_tables()

        for table in tables:
            if table.cells:
                row = rule.row or 0
                col = rule.column or 0

                if row < len(table.cells) and col < len(table.cells[row]):
                    value = table.cells[row][col]
                    if value:
                        return (value, 0.85, ExtractionMethod.TABLE, None)

            # Tentar por header
            if rule.header and table.cells:
                # Primeira linha como header
                headers = table.cells[0] if table.cells else []
                try:
                    col_idx = headers.index(rule.header)
                    row_idx = rule.row or 1
                    if row_idx < len(table.cells):
                        value = table.cells[row_idx][col_idx]
                        if value:
                            return (value, 0.85, ExtractionMethod.TABLE, None)
                except ValueError:
                    pass

        return None

    async def _extract_by_types(
        self,
        context: ExtractionContext,
        field_types: list[FieldType],
    ) -> list[ExtractedField]:
        """Extrai campos por tipo automaticamente."""
        fields = []
        full_text = context.ocr_result.get_full_text()

        for field_type in field_types:
            pattern_names = self.FIELD_PATTERNS.get(field_type, [])

            for pattern_name in pattern_names:
                pattern = self._compiled_patterns.get(pattern_name)
                if not pattern:
                    continue

                matches = pattern.findall(full_text)
                for i, match in enumerate(matches[: self.config.max_alternatives]):
                    field = ExtractedField(
                        document_id=context.ocr_result.document_id,
                        field_name=f"{field_type.value}_{i + 1}",
                        field_type=field_type,
                        raw_value=match if isinstance(match, str) else match[0],
                        confidence=0.80,
                        method=ExtractionMethod.REGEX,
                    )
                    fields.append(field)

        return fields

    async def _extract_generic(
        self,
        context: ExtractionContext,
    ) -> list[ExtractedField]:
        """Extracao generica de campos comuns."""
        fields = []
        full_text = context.ocr_result.get_full_text()

        # Extrair todos os tipos conhecidos
        for pattern_name, pattern in self._compiled_patterns.items():
            matches = pattern.findall(full_text)

            # Mapear para FieldType
            field_type_map = {
                "cpf": FieldType.CPF,
                "cnpj": FieldType.CNPJ,
                "cep": FieldType.ZIP_CODE,
                "phone": FieldType.PHONE,
                "email": FieldType.EMAIL,
                "date_br": FieldType.DATE,
                "date_iso": FieldType.DATE,
                "currency_br": FieldType.CURRENCY,
                "currency_generic": FieldType.CURRENCY,
                "nfe_key": FieldType.NFE_KEY,
                "boleto_line": FieldType.BOLETO_LINE,
                "plate": FieldType.PLATE,
            }

            field_type = field_type_map.get(pattern_name, FieldType.TEXT)

            for i, match in enumerate(matches[: self.config.max_alternatives]):
                value = match if isinstance(match, str) else match[0]

                # Evitar duplicatas
                if any(f.raw_value == value for f in fields):
                    continue

                field = ExtractedField(
                    document_id=context.ocr_result.document_id,
                    field_name=f"{pattern_name}_{i + 1}",
                    field_type=field_type,
                    raw_value=value,
                    confidence=0.75,
                    method=ExtractionMethod.REGEX,
                )
                fields.append(field)

        return fields

    def _map_field_type(self, type_str: str) -> FieldType:
        """Mapeia string de tipo para FieldType."""
        try:
            return FieldType(type_str.lower())
        except ValueError:
            return FieldType.TEXT

    def _deduplicate_fields(self, fields: list[ExtractedField]) -> list[ExtractedField]:
        """Remove campos duplicados mantendo maior confianca."""
        seen = {}
        for dup_field in fields:
            key = (dup_field.field_name, dup_field.raw_value)
            if key not in seen or dup_field.confidence > seen[key].confidence:
                seen[key] = dup_field

        return list(seen.values())

    def extract_key_value_pairs(self, ocr_result: OCRResult) -> list[tuple[str, str, float]]:
        """
        Extrai pares chave-valor do documento.

        Returns:
            Lista de (chave, valor, confianca)
        """
        pairs = []

        # Padroes de separadores
        separators = [":", "=", "-", "–"]

        for page in ocr_result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = line.get_text()

                    for sep in separators:
                        if sep in line_text:
                            parts = line_text.split(sep, 1)
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip()

                                # Validar
                                if len(key) > 2 and len(value) > 0 and len(key) < 50:
                                    pairs.append((key, value, 0.70))
                            break

        return pairs

    def find_field_location(self, ocr_result: OCRResult, value: str) -> FieldLocation | None:
        """Encontra localizacao de um valor no documento."""
        value_lower = value.lower()

        for page in ocr_result.pages:
            for block in page.blocks:
                for line in block.lines:
                    if value_lower in line.get_text().lower():
                        # Encontrar palavra exata
                        for word in line.words:
                            if value_lower in word.text.lower() and word.bounding_box:
                                return FieldLocation(
                                    page=page.page_number,
                                    x=word.bounding_box.x,
                                    y=word.bounding_box.y,
                                    width=word.bounding_box.width,
                                    height=word.bounding_box.height,
                                    line_number=line.line_number,
                                )

        return None
