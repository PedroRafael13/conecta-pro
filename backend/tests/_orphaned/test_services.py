"""
Testes dos Services Document Intelligence.

Testes para DocumentClassifier, DataExtractor, TemplateManager.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.documents.models.document import DocumentType
from modules.documents.models.extracted_field import FieldType
from modules.documents.models.extraction_template import TemplateCategory
from modules.documents.models.ocr_result import (
    OCRBlock,
    OCRLine,
    OCRPage,
    OCRResult,
    OCRWord,
)
from modules.documents.services.data_extractor import (
    DataExtractor,
    ExtractionConfig,
)
from modules.documents.services.document_classifier import (
    ClassificationResult,
    ClassificationRule,
    ClassifierConfig,
    DocumentClassifier,
)
from modules.documents.services.template_manager import TemplateManager


class TestDocumentClassifier:
    """Testes do classificador de documentos."""

    @pytest.fixture
    def classifier(self):
        """Cria instancia do classificador."""
        return DocumentClassifier()

    @pytest.fixture
    def ocr_boleto(self):
        """Cria OCR result de boleto."""
        text = """
        BOLETO BANCÁRIO
        Cedente: Empresa XYZ LTDA
        Sacado: João da Silva
        Valor do Documento: R$ 1.234,56
        Vencimento: 15/06/2025
        Linha Digitável: 23793.38128 60000.000003 00000.000400 1 84340000123456
        Código de Barras
        Pagável em qualquer banco até o vencimento
        Ficha de Compensação
        """
        word = OCRWord(text=text)
        line = OCRLine(words=[word], text=text)
        block = OCRBlock(lines=[line], text=text)
        page = OCRPage(blocks=[block], text=text)
        return OCRResult(pages=[page], full_text=text)

    @pytest.fixture
    def ocr_nfe(self):
        """Cria OCR result de NFe."""
        text = """
        NOTA FISCAL ELETRÔNICA
        DANFE
        Chave de Acesso: 35210312345678000195550010000001231234567890
        Natureza da Operação: Venda
        ICMS: R$ 100,00
        Emitente: Empresa ABC
        CNPJ: 12.345.678/0001-90
        Destinatário: Cliente XYZ
        Valor Total: R$ 1.500,00
        """
        word = OCRWord(text=text)
        line = OCRLine(words=[word], text=text)
        block = OCRBlock(lines=[line], text=text)
        page = OCRPage(blocks=[block], text=text)
        return OCRResult(pages=[page], full_text=text)

    @pytest.mark.asyncio
    async def test_classify_boleto(self, classifier, ocr_boleto):
        """Testa classificacao de boleto."""
        result = await classifier.classify(ocr_boleto)

        assert result.document_type == DocumentType.CND_FEDERAL
        assert result.confidence > 0.5
        assert len(result.matched_keywords) > 0
        assert "boleto" in [k.lower() for k in result.matched_keywords]

    @pytest.mark.asyncio
    async def test_classify_nfe(self, classifier, ocr_nfe):
        """Testa classificacao de NFe."""
        result = await classifier.classify(ocr_nfe)

        assert result.document_type == DocumentType.CND_FEDERAL
        assert result.confidence > 0.5
        assert len(result.matched_keywords) > 0

    @pytest.mark.asyncio
    async def test_classify_desconhecido(self, classifier):
        """Testa documento desconhecido."""
        text = "Texto generico sem palavras chave de documentos"
        word = OCRWord(text=text)
        line = OCRLine(words=[word], text=text)
        block = OCRBlock(lines=[line], text=text)
        page = OCRPage(blocks=[block], text=text)
        ocr = OCRResult(pages=[page], full_text=text)

        result = await classifier.classify(ocr)

        assert result.confidence < 0.5 or result.document_type == DocumentType.CND_FEDERAL

    def test_add_custom_rule(self, classifier):
        """Testa adicao de regra customizada."""
        rule = ClassificationRule(
            document_type=DocumentType.CND_FEDERAL,
            keywords=["palavra_especifica"],
            min_keyword_matches=1,
        )

        classifier.add_rule(rule)

        assert rule in classifier.rules

    def test_explain_classification(self, classifier):
        """Testa explicacao de classificacao."""
        result = ClassificationResult(
            document_type=DocumentType.CND_FEDERAL,
            confidence=0.85,
            matched_keywords=["boleto", "vencimento"],
            matched_patterns=[r"\d{47}"],
        )

        explanation = classifier.explain_classification(result)

        assert explanation["document_type"] == "boleto"
        assert "85" in explanation["confidence"]
        assert len(explanation["reasoning"]["matched_keywords"]) == 2


class TestDataExtractor:
    """Testes do extrator de dados."""

    @pytest.fixture
    def extractor(self):
        """Cria instancia do extrator."""
        return DataExtractor()

    @pytest.fixture
    def ocr_with_cpf(self):
        """OCR com CPF."""
        text = "CPF: 529.982.247-25\nNome: João da Silva"
        return OCRResult(full_text=text, pages=[])

    @pytest.fixture
    def ocr_with_values(self):
        """OCR com varios valores."""
        text = """
        CPF: 529.982.247-25
        CNPJ: 11.222.333/0001-81
        Email: teste@email.com
        Telefone: (11) 99988-7766
        Data: 15/06/2025
        Valor: R$ 1.234,56
        """
        return OCRResult(full_text=text, pages=[])

    @pytest.mark.asyncio
    async def test_extract_cpf(self, extractor, ocr_with_cpf):
        """Testa extracao de CPF."""
        fields = await extractor.extract(
            ocr_with_cpf,
            field_types=[FieldType.CPF],
        )

        cpf_fields = [f for f in fields if f.field_type == FieldType.CPF]
        assert len(cpf_fields) > 0
        assert "529" in cpf_fields[0].raw_value

    @pytest.mark.asyncio
    async def test_extract_multiple_types(self, extractor, ocr_with_values):
        """Testa extracao de multiplos tipos."""
        fields = await extractor.extract(
            ocr_with_values,
            field_types=[
                FieldType.CPF,
                FieldType.CNPJ,
                FieldType.EMAIL,
                FieldType.PHONE,
            ],
        )

        types_found = {f.field_type for f in fields}

        assert FieldType.CPF in types_found
        assert FieldType.CNPJ in types_found
        assert FieldType.EMAIL in types_found
        assert FieldType.PHONE in types_found

    @pytest.mark.asyncio
    async def test_extract_generic(self, extractor, ocr_with_values):
        """Testa extracao generica."""
        fields = await extractor.extract(ocr_with_values)

        assert len(fields) > 0
        # Deve encontrar varios campos automaticamente

    def test_extract_key_value_pairs(self, extractor):
        """Testa extracao de pares chave-valor."""
        text = """
        Nome: João da Silva
        CPF: 529.982.247-25
        Telefone: (11) 99988-7766
        """
        OCRWord(text=text)
        line1 = OCRLine(words=[], text="Nome: João da Silva")
        line2 = OCRLine(words=[], text="CPF: 529.982.247-25")
        block = OCRBlock(lines=[line1, line2])
        page = OCRPage(blocks=[block])
        ocr = OCRResult(pages=[page], full_text=text)

        pairs = extractor.extract_key_value_pairs(ocr)

        keys = [p[0] for p in pairs]
        assert "Nome" in keys or "CPF" in keys


class TestTemplateManager:
    """Testes do gerenciador de templates."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Cria instancia do gerenciador."""
        return TemplateManager(templates_path=str(tmp_path))

    def test_builtin_templates(self, manager):
        """Testa templates builtin."""
        templates = manager.get_builtin_templates()

        assert len(templates) > 0

        # Deve ter template de boleto
        boleto = manager.get_template("builtin_boleto")
        assert boleto is not None
        assert boleto.document_type == "boleto"
        assert boleto.is_official is True

    def test_get_templates_by_type(self, manager):
        """Testa busca por tipo."""
        templates = manager.get_templates_by_type("boleto")

        assert len(templates) > 0
        assert all(t.document_type == "boleto" for t in templates)

    def test_get_templates_by_category(self, manager):
        """Testa busca por categoria."""
        templates = manager.get_templates_by_category(TemplateCategory.TRANSACTIONAL)

        assert len(templates) > 0
        assert all(t.category == TemplateCategory.TRANSACTIONAL for t in templates)

    def test_list_templates(self, manager):
        """Testa listagem de templates."""
        templates = manager.list_templates(include_builtin=True)

        assert len(templates) > 0

    def test_create_template(self, manager):
        """Testa criacao de template."""
        from modules.documents.models.extraction_template import (
            ExtractionTemplate,
            TemplateField,
            TemplateRule,
        )

        template = ExtractionTemplate(
            tenant_id="tenant1",
            name="Meu Template",
            document_type="custom",
            detection_keywords=["meu", "documento"],
        )
        template.add_field(
            TemplateField(
                name="campo1",
                required=True,
                rules=[TemplateRule(pattern=r"\d+")],
            )
        )

        created = manager.create_template(template)

        assert created.id is not None
        assert created.name == "Meu Template"

        # Deve estar salvo
        loaded = manager.get_template(created.id)
        assert loaded is not None

    def test_clone_template(self, manager):
        """Testa clonagem de template."""
        cloned = manager.clone_template("builtin_boleto", "Meu Boleto", "tenant1")

        assert cloned is not None
        assert cloned.name == "Meu Boleto"
        assert cloned.tenant_id == "tenant1"
        assert cloned.is_official is False
        assert cloned.parent_version_id == "builtin_boleto"

    def test_delete_template_builtin_error(self, manager):
        """Testa que nao pode deletar template builtin."""
        with pytest.raises(ValueError):
            manager.delete_template("builtin_boleto")

    def test_export_import_template(self, manager):
        """Testa exportacao e importacao."""
        # Exportar template builtin
        data = manager.export_template("builtin_boleto")
        assert data is not None
        assert data["name"] == "Boleto Bancario"

        # Importar como novo
        imported = manager.import_template(data, "tenant1")
        assert imported.id != "builtin_boleto"
        assert imported.tenant_id == "tenant1"


class TestExtractionConfig:
    """Testes de configuracao de extracao."""

    def test_default_config(self):
        """Testa configuracao padrao."""
        config = ExtractionConfig()

        assert config.min_confidence == 0.5
        assert config.use_fuzzy_matching is True
        assert config.apply_corrections is True

    def test_custom_config(self):
        """Testa configuracao customizada."""
        config = ExtractionConfig(
            min_confidence=0.8,
            use_fuzzy_matching=False,
            max_alternatives=5,
        )

        assert config.min_confidence == 0.8
        assert config.use_fuzzy_matching is False
        assert config.max_alternatives == 5


class TestClassifierConfig:
    """Testes de configuracao do classificador."""

    def test_default_config(self):
        """Testa configuracao padrao."""
        config = ClassifierConfig()

        assert config.min_confidence == 0.5
        assert config.use_ml_model is False
        assert config.fallback_type == DocumentType.CND_FEDERAL
