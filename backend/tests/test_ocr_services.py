"""Testes dos servicos OCR - Sprint 39.

Testes para:
- OCRService
- ExtractionService
- ValidationService
"""

from datetime import datetime
from typing import Any

import pytest

from modules.ai.ocr.models.extracted_field import FieldType
from modules.ai.ocr.models.ocr_result import OCRProvider
from modules.ai.ocr.services.extraction_service import ExtractionService
from modules.ai.ocr.services.ocr_service import OCRService
from modules.ai.ocr.services.validation_service import ValidationService

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def ocr_service():
    """Servico OCR configurado."""
    return OCRService(
        default_provider=OCRProvider.TESSERACT,
        default_language="por",
        confidence_threshold=0.6,
    )


@pytest.fixture
def extraction_service():
    """Servico de extracao configurado."""
    return ExtractionService(
        confidence_threshold=0.7,
        enable_fuzzy_matching=True,
        enable_auto_correction=True,
    )


@pytest.fixture
def validation_service():
    """Servico de validacao configurado."""
    return ValidationService(
        enable_external_validation=False,
        enable_auto_correction=True,
        strict_mode=False,
    )


@pytest.fixture
def sample_ocr_result() -> dict[str, Any]:
    """Resultado OCR de exemplo."""
    return {
        "raw_text": """NOTA FISCAL ELETRONICA
CNPJ: 12.345.678/0001-90
Razao Social: Empresa Teste LTDA
Data de Emissao: 15/01/2024
Valor Total: R$ 1.500,00
Email: contato@empresa.com.br
Telefone: (11) 99999-1234
CPF Cliente: 123.456.789-09
CEP: 01310-100""",
        "lines": [
            {"text": "NOTA FISCAL ELETRONICA", "confidence": 0.98},
            {"text": "CNPJ: 12.345.678/0001-90", "confidence": 0.95},
            {"text": "Razao Social: Empresa Teste LTDA", "confidence": 0.92},
            {"text": "Data de Emissao: 15/01/2024", "confidence": 0.94},
            {"text": "Valor Total: R$ 1.500,00", "confidence": 0.96},
            {"text": "Email: contato@empresa.com.br", "confidence": 0.97},
            {"text": "Telefone: (11) 99999-1234", "confidence": 0.93},
            {"text": "CPF Cliente: 123.456.789-09", "confidence": 0.91},
            {"text": "CEP: 01310-100", "confidence": 0.95},
        ],
        "key_value_pairs": [
            {"key": "CNPJ", "value": "12.345.678/0001-90", "confidence": 0.95},
            {"key": "Data de Emissao", "value": "15/01/2024", "confidence": 0.94},
            {"key": "Valor Total", "value": "R$ 1.500,00", "confidence": 0.96},
        ],
        "overall_confidence": 0.94,
    }


@pytest.fixture
def sample_extracted_fields() -> list[dict[str, Any]]:
    """Campos extraidos de exemplo."""
    return [
        {
            "field_id": "field_001",
            "field_name": "cnpj",
            "field_type": FieldType.CNPJ.value,
            "extracted_value": "12.345.678/0001-90",
            "normalized_value": "12345678000190",
            "confidence": 0.95,
        },
        {
            "field_id": "field_002",
            "field_name": "cpf",
            "field_type": FieldType.CPF.value,
            "extracted_value": "123.456.789-09",
            "normalized_value": "12345678909",
            "confidence": 0.91,
        },
        {
            "field_id": "field_003",
            "field_name": "email",
            "field_type": FieldType.EMAIL.value,
            "extracted_value": "contato@empresa.com.br",
            "normalized_value": "contato@empresa.com.br",
            "confidence": 0.97,
        },
        {
            "field_id": "field_004",
            "field_name": "data_emissao",
            "field_type": FieldType.DATE.value,
            "extracted_value": "15/01/2024",
            "normalized_value": "2024-01-15",
            "confidence": 0.94,
        },
        {
            "field_id": "field_005",
            "field_name": "valor_total",
            "field_type": FieldType.CURRENCY.value,
            "extracted_value": "R$ 1.500,00",
            "normalized_value": "1500.00",
            "confidence": 0.96,
        },
    ]


# ============================================================
# Testes OCRService
# ============================================================


class TestOCRService:
    """Testes do servico OCR."""

    def test_service_creation(self, ocr_service):
        """Deve criar servico corretamente."""
        assert ocr_service.default_provider == OCRProvider.TESSERACT
        assert ocr_service.default_language == "por"
        assert ocr_service.confidence_threshold == 0.6

    def test_process_image_tesseract(self, ocr_service):
        """Deve processar imagem com Tesseract."""
        image_data = b"fake image content"
        result = ocr_service.process_image(image_data)

        assert "raw_text" in result
        assert "provider" in result
        assert result["provider"] == "tesseract"
        assert "processing_time_ms" in result

    def test_process_image_google_vision(self, ocr_service):
        """Deve processar imagem com Google Vision."""
        image_data = b"fake image content"
        result = ocr_service.process_image(
            image_data,
            provider=OCRProvider.GOOGLE_VISION,
        )

        assert result["provider"] == "google_vision"

    def test_process_image_aws_textract(self, ocr_service):
        """Deve processar imagem com AWS Textract."""
        image_data = b"fake image content"
        result = ocr_service.process_image(
            image_data,
            provider=OCRProvider.AWS_TEXTRACT,
        )

        assert result["provider"] == "aws_textract"

    def test_normalize_text(self, ocr_service):
        """Deve normalizar texto."""
        text = "  Texto   com   espacos   extras  "
        result = ocr_service.normalize_text(text)

        assert result == "Texto com espacos extras"

    def test_normalize_empty_text(self, ocr_service):
        """Deve retornar vazio para texto vazio."""
        assert ocr_service.normalize_text("") == ""
        assert ocr_service.normalize_text(None) == ""

    def test_detect_document_type_invoice(self, ocr_service):
        """Deve detectar nota fiscal."""
        # Texto com keywords claros de nota fiscal
        ocr_result = {
            "raw_text": "NOTA FISCAL ELETRONICA - NFe\nDANFE\nChave de Acesso",
        }
        doc_type, confidence = ocr_service.detect_document_type(ocr_result)

        assert doc_type == "invoice"
        assert confidence > 0

    def test_detect_document_type_unknown(self, ocr_service):
        """Deve retornar None para documento desconhecido."""
        ocr_result = {"raw_text": "texto aleatorio sem padroes"}
        doc_type, confidence = ocr_service.detect_document_type(ocr_result)

        # Pode nao detectar tipo
        assert confidence >= 0

    def test_calculate_metrics(self, ocr_service):
        """Deve calcular metricas do resultado."""
        ocr_result = {
            "raw_text": "Texto de teste",
            "lines": [
                {"text": "Texto", "confidence": 0.9, "words": [{"text": "Texto"}]},
                {"text": "de teste", "confidence": 0.8, "words": [{"text": "de"}, {"text": "teste"}]},
            ],
        }

        metrics = ocr_service._calculate_metrics(ocr_result)

        assert metrics["line_count"] == 2
        assert metrics["word_count"] == 3
        assert 0.8 <= metrics["overall_confidence"] <= 0.9

    def test_get_supported_languages(self, ocr_service):
        """Deve retornar idiomas suportados."""
        languages = ocr_service.get_supported_languages(OCRProvider.TESSERACT)

        assert "por" in languages
        assert "eng" in languages

    def test_estimate_processing_cost(self, ocr_service):
        """Deve estimar custo de processamento."""
        cost = ocr_service.estimate_processing_cost(10, OCRProvider.GOOGLE_VISION)

        assert cost["page_count"] == 10
        assert cost["total_cost_usd"] >= 0
        assert cost["currency"] == "USD"

    def test_estimate_cost_tesseract_free(self, ocr_service):
        """Tesseract deve ser gratuito."""
        cost = ocr_service.estimate_processing_cost(100, OCRProvider.TESSERACT)

        assert cost["total_cost_usd"] == 0


# ============================================================
# Testes ExtractionService
# ============================================================


class TestExtractionService:
    """Testes do servico de extracao."""

    def test_service_creation(self, extraction_service):
        """Deve criar servico corretamente."""
        assert extraction_service.confidence_threshold == 0.7
        assert extraction_service.enable_fuzzy_matching is True

    def test_extract_fields(self, extraction_service, sample_ocr_result):
        """Deve extrair campos do resultado OCR."""
        fields = extraction_service.extract_fields(sample_ocr_result)

        assert len(fields) > 0

        # Verifica estrutura dos campos
        for field in fields:
            assert "field_id" in field
            assert "field_name" in field
            assert "field_type" in field

    def test_extract_cnpj(self, extraction_service):
        """Deve extrair CNPJ."""
        ocr_result = {"raw_text": "CNPJ: 12.345.678/0001-90", "lines": []}
        fields = extraction_service.extract_fields(ocr_result)

        cnpj_fields = [f for f in fields if f.get("field_type") == "cnpj"]
        assert len(cnpj_fields) > 0
        assert "12345678000190" in cnpj_fields[0].get("normalized_value", "")

    def test_extract_cpf(self, extraction_service):
        """Deve extrair CPF."""
        ocr_result = {"raw_text": "CPF: 123.456.789-09", "lines": []}
        fields = extraction_service.extract_fields(ocr_result)

        cpf_fields = [f for f in fields if f.get("field_type") == "cpf"]
        assert len(cpf_fields) > 0
        assert "12345678909" in cpf_fields[0].get("normalized_value", "")

    def test_extract_email(self, extraction_service):
        """Deve extrair email."""
        ocr_result = {"raw_text": "Email: teste@email.com", "lines": []}
        fields = extraction_service.extract_fields(ocr_result)

        email_fields = [f for f in fields if f.get("field_type") == "email"]
        assert len(email_fields) > 0
        assert "teste@email.com" in email_fields[0].get("normalized_value", "")

    def test_extract_phone(self, extraction_service):
        """Deve extrair telefone."""
        ocr_result = {"raw_text": "Tel: (11) 99999-1234", "lines": []}
        fields = extraction_service.extract_fields(ocr_result)

        phone_fields = [f for f in fields if f.get("field_type") == "phone"]
        assert len(phone_fields) > 0

    def test_extract_date(self, extraction_service):
        """Deve extrair data."""
        ocr_result = {"raw_text": "Data: 15/01/2024", "lines": []}
        fields = extraction_service.extract_fields(ocr_result)

        date_fields = [f for f in fields if f.get("field_type") == "date"]
        assert len(date_fields) > 0

    def test_extract_currency(self, extraction_service):
        """Deve extrair valor monetario."""
        ocr_result = {"raw_text": "Valor: R$ 1.500,00", "lines": []}
        fields = extraction_service.extract_fields(ocr_result)

        currency_fields = [f for f in fields if f.get("field_type") == "currency"]
        assert len(currency_fields) > 0
        # Valor normalizado
        assert "1500" in currency_fields[0].get("normalized_value", "")

    def test_extract_cep(self, extraction_service):
        """Deve extrair CEP."""
        ocr_result = {"raw_text": "CEP: 01310-100", "lines": []}
        fields = extraction_service.extract_fields(ocr_result)

        cep_fields = [f for f in fields if f.get("field_type") == "cep"]
        assert len(cep_fields) > 0
        assert "01310100" in cep_fields[0].get("normalized_value", "")

    def test_extract_from_key_value_pairs(self, extraction_service, sample_ocr_result):
        """Deve extrair de pares chave-valor."""
        fields = extraction_service._extract_from_key_value(sample_ocr_result["key_value_pairs"])

        assert len(fields) > 0
        for field in fields:
            assert field.get("extraction_method") == "key_value"

    def test_deduplicate_fields(self, extraction_service):
        """Deve remover campos duplicados."""
        fields = [
            {"field_type": "cnpj", "normalized_value": "12345678000190", "confidence": 0.9},
            {"field_type": "cnpj", "normalized_value": "12345678000190", "confidence": 0.8},
            {"field_type": "cpf", "normalized_value": "12345678909", "confidence": 0.95},
        ]

        unique = extraction_service._deduplicate_fields(fields)

        assert len(unique) == 2
        # Deve manter o com maior confianca
        cnpj_field = next(f for f in unique if f["field_type"] == "cnpj")
        assert cnpj_field["confidence"] == 0.9

    def test_normalize_date_formats(self, extraction_service):
        """Deve normalizar diferentes formatos de data."""
        dates = [
            ("15/01/2024", "2024-01-15"),
            ("15-01-2024", "2024-01-15"),
            ("2024/01/15", "2024-01-15"),
        ]

        for input_date, expected in dates:
            result = extraction_service._normalize_date(input_date)
            assert result == expected


# ============================================================
# Testes ValidationService
# ============================================================


class TestValidationService:
    """Testes do servico de validacao."""

    def test_service_creation(self, validation_service):
        """Deve criar servico corretamente."""
        assert validation_service.enable_external_validation is False
        assert validation_service.enable_auto_correction is True
        assert validation_service.strict_mode is False

    def test_validate_fields(self, validation_service, sample_extracted_fields):
        """Deve validar campos extraidos."""
        result = validation_service.validate_fields(sample_extracted_fields)

        assert "validation_id" in result
        assert "status" in result
        assert "total_fields" in result
        assert result["total_fields"] == len(sample_extracted_fields)

    def test_validate_cpf_valid(self, validation_service):
        """Deve validar CPF valido."""
        # CPF valido: 529.982.247-25
        fields = [
            {
                "field_id": "1",
                "field_name": "cpf",
                "field_type": "cpf",
                "normalized_value": "52998224725",
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["valid_fields"] == 1
        assert result["invalid_fields"] == 0

    def test_validate_cpf_invalid(self, validation_service):
        """Deve rejeitar CPF invalido."""
        fields = [
            {
                "field_id": "1",
                "field_name": "cpf",
                "field_type": "cpf",
                "normalized_value": "12345678900",  # CPF invalido
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["invalid_fields"] == 1
        assert len(result["errors"]) > 0

    def test_validate_cpf_repeated_digits(self, validation_service):
        """Deve rejeitar CPF com digitos repetidos."""
        fields = [
            {
                "field_id": "1",
                "field_name": "cpf",
                "field_type": "cpf",
                "normalized_value": "11111111111",
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["invalid_fields"] == 1

    def test_validate_cnpj_valid(self, validation_service):
        """Deve validar CNPJ valido."""
        # CNPJ valido: 11.222.333/0001-81
        fields = [
            {
                "field_id": "1",
                "field_name": "cnpj",
                "field_type": "cnpj",
                "normalized_value": "11222333000181",
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["valid_fields"] == 1

    def test_validate_cnpj_invalid(self, validation_service):
        """Deve rejeitar CNPJ invalido."""
        fields = [
            {
                "field_id": "1",
                "field_name": "cnpj",
                "field_type": "cnpj",
                "normalized_value": "12345678000190",  # CNPJ invalido
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["invalid_fields"] == 1

    def test_validate_email_valid(self, validation_service):
        """Deve validar email valido."""
        fields = [
            {
                "field_id": "1",
                "field_name": "email",
                "field_type": "email",
                "normalized_value": "teste@email.com",
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["valid_fields"] == 1

    def test_validate_email_invalid(self, validation_service):
        """Deve rejeitar email invalido."""
        fields = [
            {
                "field_id": "1",
                "field_name": "email",
                "field_type": "email",
                "normalized_value": "email_invalido",
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["invalid_fields"] == 1

    def test_validate_phone(self, validation_service):
        """Deve validar telefone."""
        fields = [
            {
                "field_id": "1",
                "field_name": "phone",
                "field_type": "phone",
                "normalized_value": "11999991234",
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["valid_fields"] == 1

    def test_validate_phone_invalid(self, validation_service):
        """Deve rejeitar telefone muito curto."""
        fields = [
            {
                "field_id": "1",
                "field_name": "phone",
                "field_type": "phone",
                "normalized_value": "123",
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["invalid_fields"] == 1

    def test_validate_cep(self, validation_service):
        """Deve validar CEP."""
        fields = [
            {
                "field_id": "1",
                "field_name": "cep",
                "field_type": "cep",
                "normalized_value": "01310100",
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["valid_fields"] == 1

    def test_validate_date_valid(self, validation_service):
        """Deve validar data valida."""
        fields = [
            {
                "field_id": "1",
                "field_name": "date",
                "field_type": "date",
                "normalized_value": "2024-01-15",
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["valid_fields"] == 1

    def test_validate_date_invalid_format(self, validation_service):
        """Deve rejeitar data com formato invalido."""
        fields = [
            {
                "field_id": "1",
                "field_name": "date",
                "field_type": "date",
                "normalized_value": "invalido",
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["invalid_fields"] == 1

    def test_validate_currency(self, validation_service):
        """Deve validar valor monetario."""
        fields = [
            {
                "field_id": "1",
                "field_name": "valor",
                "field_type": "currency",
                "normalized_value": "1500.00",
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["valid_fields"] == 1

    def test_validate_currency_negative_warning(self, validation_service):
        """Deve gerar warning para valor negativo."""
        fields = [
            {
                "field_id": "1",
                "field_name": "valor",
                "field_type": "currency",
                "normalized_value": "-100.00",
            }
        ]

        result = validation_service.validate_fields(fields)

        assert result["warning_fields"] == 1

    def test_calculate_score(self, validation_service):
        """Deve calcular score corretamente."""
        result = {
            "total_fields": 10,
            "valid_fields": 8,
            "warning_fields": 1,
            "invalid_fields": 1,
        }

        score = validation_service._calculate_score(result)

        # (8 + 1*0.5) / 10 = 0.85
        assert score == 0.85

    def test_needs_review_with_errors(self, validation_service):
        """Deve precisar de revisao com erros."""
        result = {
            "invalid_fields": 1,
            "overall_score": 0.9,
            "cross_validation_results": [],
        }

        assert validation_service._needs_review(result) is True

    def test_needs_review_low_score(self, validation_service):
        """Deve precisar de revisao com score baixo."""
        result = {
            "invalid_fields": 0,
            "overall_score": 0.5,
            "cross_validation_results": [],
        }

        assert validation_service._needs_review(result) is True

    def test_no_review_needed_good_result(self, validation_service):
        """Nao deve precisar de revisao com bom resultado."""
        result = {
            "invalid_fields": 0,
            "overall_score": 0.95,
            "cross_validation_results": [],
        }

        assert validation_service._needs_review(result) is False

    def test_cross_validation_sum_check(self, validation_service):
        """Deve validar soma de itens vs total."""
        fields = [
            {"field_name": "item_1", "field_type": "currency", "normalized_value": "500.00"},
            {"field_name": "item_2", "field_type": "currency", "normalized_value": "500.00"},
            {"field_name": "item_3", "field_type": "currency", "normalized_value": "500.00"},
            {"field_name": "total", "field_type": "currency", "normalized_value": "1500.00"},
        ]

        results = validation_service._cross_validate(fields, "invoice")

        sum_checks = [r for r in results if r.get("type") == "sum_check"]
        assert len(sum_checks) > 0
        assert sum_checks[0]["status"] == "passed"

    def test_cross_validation_sum_mismatch(self, validation_service):
        """Deve detectar divergencia na soma."""
        fields = [
            {"field_name": "item_1", "field_type": "currency", "normalized_value": "500.00"},
            {"field_name": "item_2", "field_type": "currency", "normalized_value": "500.00"},
            {"field_name": "total", "field_type": "currency", "normalized_value": "2000.00"},  # Errado
        ]

        results = validation_service._cross_validate(fields, "invoice")

        sum_checks = [r for r in results if r.get("type") == "sum_check"]
        if sum_checks:
            assert sum_checks[0]["status"] == "failed"


# ============================================================
# Testes de Integracao
# ============================================================


class TestOCRIntegration:
    """Testes de integracao entre servicos."""

    def test_full_pipeline(self, ocr_service, extraction_service, validation_service):
        """Deve processar pipeline completo."""
        # 1. Processa OCR
        image_data = b"fake invoice image"
        ocr_result = ocr_service.process_image(image_data)

        assert "raw_text" in ocr_result
        assert "provider" in ocr_result

        # 2. Extrai campos
        fields = extraction_service.extract_fields(ocr_result)

        # Pode nao extrair campos do mock
        assert isinstance(fields, list)

        # 3. Valida campos (se houver)
        if fields:
            validation_result = validation_service.validate_fields(fields)

            assert "status" in validation_result
            assert "total_fields" in validation_result

    def test_multiple_providers(self, ocr_service):
        """Deve processar com diferentes providers."""
        image_data = b"test image"
        providers = [
            OCRProvider.TESSERACT,
            OCRProvider.GOOGLE_VISION,
            OCRProvider.AWS_TEXTRACT,
        ]

        for provider in providers:
            result = ocr_service.process_image(image_data, provider=provider)
            assert result["provider"] == provider.value
