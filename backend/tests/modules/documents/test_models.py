"""
Testes dos Modelos Document Intelligence.

Testes para Document, OCRResult, ExtractedField, Template.
"""

from datetime import datetime
from decimal import Decimal

import pytest

from modules.documents.models.document import (
    Document,
    DocumentSource,
    DocumentStatus,
    DocumentType,
    ProcessingStatus,
    ProcessingStep,
)
from modules.documents.models.extracted_field import (
    ExtractedField,
    ExtractionMethod,
    FieldConfidence,
    FieldType,
)
from modules.documents.models.extraction_template import (
    ExtractionTemplate,
    PostProcessor,
    RuleType,
    TemplateCategory,
    TemplateField,
    TemplateRule,
    TemplateStatus,
)
from modules.documents.models.ocr_result import (
    BoundingBox,
    OCRBlock,
    OCRLine,
    OCRPage,
    OCRProvider,
    OCRResult,
    OCRWord,
)


class TestDocument:
    """Testes do modelo Document."""

    def test_criar_documento(self):
        """Testa criacao de documento."""
        doc = Document(
            tenant_id="tenant1",
            name="boleto.pdf",
            document_type=DocumentType.CND_FEDERAL,
        )

        assert doc.id is not None
        assert doc.tenant_id == "tenant1"
        assert doc.name == "boleto.pdf"
        assert doc.document_type == DocumentType.CND_FEDERAL
        assert doc.status == DocumentStatus.VALID
        assert len(doc.processing_steps) == 6  # Etapas padrao

    def test_processing_steps(self):
        """Testa etapas de processamento."""
        doc = Document(name="test.pdf")

        # Iniciar etapa
        assert doc.start_step("upload") is True
        assert doc.current_step == "upload"
        step = doc.get_step("upload")
        assert step.status == ProcessingStatus.IN_PROGRESS
        assert step.started_at is not None

        # Completar etapa
        assert doc.complete_step("upload") is True
        step = doc.get_step("upload")
        assert step.status == ProcessingStatus.COMPLETED
        assert step.completed_at is not None
        assert step.duration_ms is not None

    def test_fail_step(self):
        """Testa falha em etapa."""
        doc = Document(name="test.pdf")
        doc.start_step("ocr")

        doc.fail_step("ocr", "Erro de OCR")

        step = doc.get_step("ocr")
        assert step.status == ProcessingStatus.FAILED
        assert step.error == "Erro de OCR"
        assert doc.status == DocumentStatus.VALID

    def test_mark_for_review(self):
        """Testa marcacao para revisao."""
        doc = Document(name="test.pdf")
        doc.mark_for_review("Baixa confianca")

        assert doc.needs_review is True
        assert doc.review_reason == "Baixa confianca"
        assert doc.status == DocumentStatus.VALID

    def test_complete_review(self):
        """Testa conclusao de revisao."""
        doc = Document(name="test.pdf")
        doc.mark_for_review("Teste")

        doc.complete_review("user123", "Tudo OK")

        assert doc.needs_review is False
        assert doc.reviewed_by == "user123"
        assert doc.reviewed_at is not None
        assert doc.status == DocumentStatus.VALID

    def test_tags(self):
        """Testa gerenciamento de tags."""
        doc = Document(name="test.pdf")

        doc.add_tag("urgente")
        assert "urgente" in doc.tags

        doc.add_tag("urgente")  # Duplicata
        assert doc.tags.count("urgente") == 1

        doc.remove_tag("urgente")
        assert "urgente" not in doc.tags

    def test_to_dict(self):
        """Testa conversao para dicionario."""
        doc = Document(
            name="test.pdf",
            document_type=DocumentType.CND_FEDERAL,
            tenant_id="t1",
        )

        data = doc.to_dict()
        assert data["name"] == "test.pdf"
        assert data["document_type"] == "nfe"
        assert "processing_summary" in data


class TestOCRResult:
    """Testes do modelo OCRResult."""

    def test_criar_ocr_result(self):
        """Testa criacao de resultado OCR."""
        result = OCRResult(
            document_id="doc1",
            provider=OCRProvider.TESSERACT,
            full_text="Texto de teste",
            confidence=0.95,
        )

        assert result.id is not None
        assert result.document_id == "doc1"
        assert result.provider == OCRProvider.TESSERACT
        assert result.confidence == 0.95

    def test_bounding_box(self):
        """Testa bounding box."""
        bbox = BoundingBox(x=10, y=20, width=100, height=50)

        assert bbox.x2 == 110
        assert bbox.y2 == 70
        assert bbox.center == (60, 45)
        assert bbox.area == 5000

        # Contains
        assert bbox.contains(50, 40) is True
        assert bbox.contains(0, 0) is False

    def test_ocr_word(self):
        """Testa palavra OCR."""
        word = OCRWord(text="R$100,00", confidence=0.9)

        assert word.text == "R$100,00"
        assert word.is_currency is True

        word2 = OCRWord(text="12345", confidence=0.95)
        assert word2.is_numeric is True

    def test_ocr_line(self):
        """Testa linha OCR."""
        words = [
            OCRWord(text="Valor:", confidence=0.9),
            OCRWord(text="R$100,00", confidence=0.85),
        ]
        line = OCRLine(words=words, line_number=1)

        assert line.word_count == 2
        assert line.get_text() == "Valor: R$100,00"
        assert line.avg_confidence == 0.875

    def test_ocr_page(self):
        """Testa pagina OCR."""
        line = OCRLine(text="Teste")
        block = OCRBlock(lines=[line])
        page = OCRPage(page_number=1, blocks=[block], width=800, height=600)

        assert page.block_count == 1
        assert page.line_count == 1
        assert page.get_text() == "Teste"

    def test_search_text(self):
        """Testa busca de texto."""
        word = OCRWord(text="boleto")
        line = OCRLine(words=[word])
        block = OCRBlock(lines=[line])
        page = OCRPage(blocks=[block])
        result = OCRResult(pages=[page])

        found = result.search_text("boleto")
        assert len(found) == 1
        assert found[0].text == "boleto"


class TestExtractedField:
    """Testes do modelo ExtractedField."""

    def test_criar_campo(self):
        """Testa criacao de campo extraido."""
        field = ExtractedField(
            document_id="doc1",
            field_name="cpf",
            field_type=FieldType.CPF,
            raw_value="529.982.247-25",
            confidence=0.95,
        )

        assert field.field_name == "cpf"
        assert field.field_type == FieldType.CPF
        assert field.confidence_level == FieldConfidence.VERY_HIGH

    def test_normalize_cpf(self):
        """Testa normalizacao de CPF."""
        field = ExtractedField(
            field_name="cpf",
            field_type=FieldType.CPF,
            raw_value="529.982.247-25",
        )

        normalized = field.normalize()
        assert normalized == "52998224725"
        assert field.display_value == "529.982.247-25"

    def test_normalize_cnpj(self):
        """Testa normalizacao de CNPJ."""
        field = ExtractedField(
            field_name="cnpj",
            field_type=FieldType.CNPJ,
            raw_value="11.222.333/0001-81",
        )

        normalized = field.normalize()
        assert normalized == "11222333000181"
        assert "/" in field.display_value

    def test_normalize_currency(self):
        """Testa normalizacao de moeda."""
        field = ExtractedField(
            field_name="valor",
            field_type=FieldType.CURRENCY,
            raw_value="R$ 1.234,56",
        )

        normalized = field.normalize()
        assert normalized == Decimal("1234.56")

    def test_normalize_date(self):
        """Testa normalizacao de data."""
        field = ExtractedField(
            field_name="data",
            field_type=FieldType.DATE,
            raw_value="15/06/2025",
        )

        normalized = field.normalize()
        assert normalized.day == 15
        assert normalized.month == 6
        assert normalized.year == 2025

    def test_verify_field(self):
        """Testa verificacao manual de campo."""
        field = ExtractedField(
            field_name="nome",
            field_type=FieldType.TEXT,
            raw_value="Jao",
        )

        field.verify("user123", "Joao")

        assert field.is_verified is True
        assert field.verified_by == "user123"
        assert field.raw_value == "Joao"

    def test_alternatives(self):
        """Testa valores alternativos."""
        field = ExtractedField(
            field_name="nome",
            field_type=FieldType.TEXT,
            raw_value="Nome",
            confidence=0.7,
        )

        field.add_alternative("Nome Alternativo", 0.9, "ml_model")

        best = field.get_best_value()
        assert best == "Nome Alternativo"


class TestExtractionTemplate:
    """Testes do modelo ExtractionTemplate."""

    def test_criar_template(self):
        """Testa criacao de template."""
        template = ExtractionTemplate(
            name="Template Boleto",
            document_type="boleto",
            category=TemplateCategory.TRANSACTIONAL,
        )

        assert template.id is not None
        assert template.name == "Template Boleto"
        assert template.status == TemplateStatus.DRAFT

    def test_add_field(self):
        """Testa adicao de campo."""
        template = ExtractionTemplate(name="Test")

        field = TemplateField(
            name="valor",
            field_type="currency",
            required=True,
        )

        template.add_field(field)

        assert len(template.fields) == 1
        assert template.fields[0].order == 0

    def test_get_field(self):
        """Testa obtencao de campo."""
        template = ExtractionTemplate(name="Test")
        template.add_field(TemplateField(name="cpf"))
        template.add_field(TemplateField(name="nome"))

        field = template.get_field("cpf")
        assert field is not None
        assert field.name == "cpf"

        assert template.get_field("inexistente") is None

    def test_required_fields(self):
        """Testa campos obrigatorios."""
        template = ExtractionTemplate(name="Test")
        template.add_field(TemplateField(name="cpf", required=True))
        template.add_field(TemplateField(name="nome", required=False))

        required = template.get_required_fields()
        assert len(required) == 1
        assert required[0].name == "cpf"

    def test_validate_template(self):
        """Testa validacao de template."""
        template = ExtractionTemplate()  # Sem nome/tipo

        errors = template.validate()
        assert len(errors) > 0
        assert any("Nome" in e for e in errors)

    def test_clone_template(self):
        """Testa clonagem de template."""
        original = ExtractionTemplate(
            name="Original",
            document_type="boleto",
        )
        original.add_field(TemplateField(name="valor"))

        cloned = original.clone("Copia")

        assert cloned.id != original.id
        assert cloned.name == "Copia"
        assert cloned.parent_version_id == original.id
        assert cloned.status == TemplateStatus.DRAFT
        assert len(cloned.fields) == 1

    def test_activate_template(self):
        """Testa ativacao de template."""
        template = ExtractionTemplate(name="Test", document_type="test")
        template.add_field(TemplateField(name="campo", rules=[TemplateRule()]))
        template.detection_keywords = ["teste"]

        template.activate()

        assert template.status == TemplateStatus.ACTIVE
        assert template.published_at is not None

    def test_template_statistics(self):
        """Testa estatisticas de template."""
        template = ExtractionTemplate(name="Test")

        template.update_statistics(True, 0.95, 100)
        template.update_statistics(True, 0.90, 120)
        template.update_statistics(False, 0.60, 80)

        assert template.usage_count == 3
        assert template.success_count == 2
        assert template.success_rate == 2 / 3


class TestTemplateRule:
    """Testes de regras de template."""

    def test_regex_rule(self):
        """Testa regra regex."""
        rule = TemplateRule(
            rule_type=RuleType.THRESHOLD,
            pattern=r"\d{11}",
        )

        compiled = rule.compile_pattern()
        assert compiled is not None
        assert compiled.match("12345678901")

    def test_post_processors(self):
        """Testa pos-processadores."""
        rule = TemplateRule(
            post_processors=[
                PostProcessor.STRIP,
                PostProcessor.UPPERCASE,
                PostProcessor.REMOVE_SPACES,
            ]
        )

        result = rule.apply_post_processors("  hello world  ")
        assert result == "HELLOWORLD"

    def test_digits_only(self):
        """Testa extrator de digitos."""
        rule = TemplateRule(post_processors=[PostProcessor.DIGITS_ONLY])

        result = rule.apply_post_processors("529.982.247-25")
        assert result == "52998224725"

    def test_validate_value(self):
        """Testa validacao de valor."""
        rule = TemplateRule(
            min_length=3,
            max_length=10,
            validation_regex=r"^[A-Z]+$",
        )

        assert rule.validate_value("ABC") is True
        assert rule.validate_value("AB") is False  # Muito curto
        assert rule.validate_value("ABCDEFGHIJK") is False  # Muito longo
        assert rule.validate_value("abc") is False  # Minusculo
