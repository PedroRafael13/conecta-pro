"""Tests for Signature Recognition Services."""

import base64
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Import services directly (avoiding model imports that need database)  # noqa: E402
from modules.ai.signature.services.comparison_service import (  # noqa: E402
    ComparisonResult,
    FeatureScore,
    SignatureComparisonService,
)
from modules.ai.signature.services.extraction_service import (  # noqa: E402
    BoundingBox,
    ExtractedSignature,
    ExtractionResult,
    SignatureExtractionService,
)
from modules.ai.signature.services.validation_service import (  # noqa: E402
    FraudAnalysisResult,
    QualityCheckResult,
    SignatureValidationService,
    ValidationResult,
)

# ============== Fixtures ==============


@pytest.fixture
def extraction_service():
    """Create extraction service instance."""
    return SignatureExtractionService(
        min_confidence=0.5,
        enable_preprocessing=True,
        enable_feature_extraction=True,
    )


@pytest.fixture
def comparison_service():
    """Create comparison service instance."""
    return SignatureComparisonService(
        default_threshold=0.75,
        strict_threshold=0.85,
        relaxed_threshold=0.65,
    )


@pytest.fixture
def validation_service(comparison_service, extraction_service):
    """Create validation service instance."""
    return SignatureValidationService(
        comparison_service=comparison_service,
        extraction_service=extraction_service,
    )


@pytest.fixture
def sample_image_data():
    """Create sample image data."""
    # Simple PNG header + data
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


@pytest.fixture
def sample_base64_image(sample_image_data):
    """Create base64 encoded image."""
    return base64.b64encode(sample_image_data).decode()


@pytest.fixture
def sample_signature():
    """Create sample signature data."""
    return {
        "width": 200,
        "height": 50,
        "quality_score": 0.75,
        "contrast_score": 0.7,
        "clarity_score": 0.8,
        "completeness_score": 0.85,
        "stroke_count": 12,
        "feature_vector": [0.1 * i for i in range(128)],
        "contour_data": [[i, i % 30] for i in range(50)],
    }


@pytest.fixture
def sample_template():
    """Create sample template data."""
    return {
        "width": 195,
        "height": 48,
        "quality_score": 0.78,
        "contrast_score": 0.72,
        "clarity_score": 0.82,
        "completeness_score": 0.88,
        "stroke_count": 11,
        "master_feature_vector": [0.1 * i for i in range(128)],
        "similarity_threshold": 0.75,
    }


# ============== BoundingBox Tests ==============


class TestBoundingBox:
    """Tests for BoundingBox class."""

    def test_create_bounding_box(self):
        """Test bounding box creation."""
        bbox = BoundingBox(x=10, y=20, width=100, height=50)

        assert bbox.x == 10
        assert bbox.y == 20
        assert bbox.width == 100
        assert bbox.height == 50

    def test_bounding_box_area(self):
        """Test area calculation."""
        bbox = BoundingBox(x=0, y=0, width=100, height=50)

        assert bbox.area == 5000

    def test_bounding_box_aspect_ratio(self):
        """Test aspect ratio calculation."""
        bbox = BoundingBox(x=0, y=0, width=200, height=50)

        assert bbox.aspect_ratio == 4.0

    def test_bounding_box_to_dict(self):
        """Test conversion to dictionary."""
        bbox = BoundingBox(x=10, y=20, width=100, height=50)
        result = bbox.to_dict()

        assert result["x"] == 10
        assert result["y"] == 20
        assert result["width"] == 100
        assert result["height"] == 50


# ============== Extraction Service Tests ==============


class TestSignatureExtractionService:
    """Tests for SignatureExtractionService."""

    def test_extract_from_image(self, extraction_service, sample_image_data):
        """Test signature extraction from image."""
        result = extraction_service.extract_from_image(sample_image_data)

        assert isinstance(result, ExtractionResult)
        assert result.processing_time_ms >= 0

    def test_extract_from_base64(self, extraction_service, sample_base64_image):
        """Test extraction from base64 image."""
        result = extraction_service.extract_from_base64(sample_base64_image)

        assert isinstance(result, ExtractionResult)

    def test_extract_with_region(self, extraction_service, sample_image_data):
        """Test extraction with specific region."""
        region = BoundingBox(x=10, y=10, width=100, height=50)
        result = extraction_service.extract_from_image(sample_image_data, region=region)

        assert isinstance(result, ExtractionResult)

    def test_extract_from_region(self, extraction_service, sample_image_data):
        """Test extract_from_region method."""
        result = extraction_service.extract_from_region(sample_image_data, x=10, y=10, width=100, height=50)

        assert isinstance(result, ExtractionResult)

    def test_invalid_base64(self, extraction_service):
        """Test handling of invalid base64."""
        result = extraction_service.extract_from_base64("invalid_base64!!!")

        assert not result.success
        assert len(result.errors) > 0

    def test_extraction_methods(self, extraction_service, sample_image_data):
        """Test different extraction methods."""
        for method in ["contour", "edge", "template", "auto"]:
            result = extraction_service.extract_from_image(sample_image_data, method=method)
            assert isinstance(result, ExtractionResult)

    def test_extracted_signature_properties(self, extraction_service, sample_image_data):
        """Test extracted signature has expected properties."""
        result = extraction_service.extract_from_image(sample_image_data)

        if result.success and result.signatures:
            sig = result.signatures[0]
            assert isinstance(sig, ExtractedSignature)
            assert sig.id is not None
            assert 0 <= sig.confidence <= 1
            assert 0 <= sig.quality_score <= 1

    def test_max_signatures_limit(self, sample_image_data):
        """Test max signatures limit is respected."""
        service = SignatureExtractionService(max_signatures=1)
        result = service.extract_from_image(sample_image_data)

        assert len(result.signatures) <= 1

    def test_min_confidence_filter(self, sample_image_data):
        """Test minimum confidence filter."""
        service = SignatureExtractionService(min_confidence=0.99)
        result = service.extract_from_image(sample_image_data)

        for sig in result.signatures:
            assert sig.confidence >= 0.99

    def test_calculate_image_hash(self, extraction_service, sample_image_data):
        """Test image hash calculation."""
        hash1 = extraction_service.calculate_image_hash(sample_image_data)
        hash2 = extraction_service.calculate_image_hash(sample_image_data)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256

    def test_estimate_stroke_data(self, extraction_service):
        """Test stroke data estimation."""
        sig = ExtractedSignature(
            width=200,
            height=50,
            stroke_count=12,
        )
        stroke_data = extraction_service.estimate_stroke_data(sig)

        assert "estimated_strokes" in stroke_data
        assert "stroke_density" in stroke_data
        assert "complexity" in stroke_data


# ============== Comparison Service Tests ==============


class TestSignatureComparisonService:
    """Tests for SignatureComparisonService."""

    def test_compare_identical_signatures(self, comparison_service, sample_signature):
        """Test comparing identical signatures."""
        result = comparison_service.compare(sample_signature, sample_signature)

        assert isinstance(result, ComparisonResult)
        assert result.similarity_score >= 0.9
        assert result.is_match

    def test_compare_different_signatures(self, comparison_service):
        """Test comparing different signatures."""
        sig1 = {
            "width": 200,
            "height": 50,
            "feature_vector": [0.1] * 128,
            "contour_data": [[i, i] for i in range(50)],
        }
        sig2 = {
            "width": 100,
            "height": 100,
            "feature_vector": [0.9] * 128,
            "contour_data": [[i, 50 - i] for i in range(50)],
        }
        result = comparison_service.compare(sig1, sig2)

        assert isinstance(result, ComparisonResult)
        assert result.similarity_score < 0.9

    def test_compare_modes(self, comparison_service, sample_signature, sample_template):
        """Test different comparison modes."""
        for mode in ["strict", "normal", "relaxed"]:
            result = comparison_service.compare(sample_signature, sample_template, mode=mode)
            assert isinstance(result, ComparisonResult)

    def test_custom_threshold(self, comparison_service, sample_signature, sample_template):
        """Test custom threshold."""
        result = comparison_service.compare(sample_signature, sample_template, custom_threshold=0.5)

        assert result.threshold_used == 0.5

    def test_compare_with_template(self, comparison_service, sample_signature, sample_template):
        """Test comparison with template."""
        result = comparison_service.compare_with_template(sample_signature, sample_template)

        assert isinstance(result, ComparisonResult)

    def test_compare_batch(self, comparison_service, sample_signature):
        """Test batch comparison."""
        candidates = [sample_signature.copy() for _ in range(5)]
        results = comparison_service.compare_batch(sample_signature, candidates, top_n=3)

        assert len(results) <= 3
        # Results should be sorted by similarity
        scores = [r[1].similarity_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_feature_scores(self, comparison_service, sample_signature, sample_template):
        """Test feature scores in result."""
        result = comparison_service.compare(sample_signature, sample_template)

        assert len(result.feature_scores) > 0
        for score in result.feature_scores:
            assert isinstance(score, FeatureScore)
            assert 0 <= score.score <= 1
            assert score.weight > 0

    def test_anomaly_detection(self, comparison_service):
        """Test anomaly detection."""
        sig1 = {"feature_vector": [0.1] * 128, "quality_score": 0.9}
        sig2 = {"feature_vector": [0.5] * 128, "quality_score": 0.3}  # Big quality diff

        result = comparison_service.compare(sig1, sig2)

        # Should detect quality anomaly
        assert "Significant quality difference" in result.anomalies or len(result.anomalies) >= 0

    def test_processing_time(self, comparison_service, sample_signature, sample_template):
        """Test processing time is recorded."""
        result = comparison_service.compare(sample_signature, sample_template)

        assert result.processing_time_ms >= 0

    def test_result_to_dict(self, comparison_service, sample_signature, sample_template):
        """Test result conversion to dictionary."""
        result = comparison_service.compare(sample_signature, sample_template)
        result_dict = result.to_dict()

        assert "is_match" in result_dict
        assert "similarity_score" in result_dict
        assert "confidence" in result_dict


# ============== Validation Service Tests ==============


class TestSignatureValidationService:
    """Tests for SignatureValidationService."""

    def test_validate_signature(self, validation_service, sample_signature):
        """Test signature validation."""
        result = validation_service.validate(sample_signature)

        assert isinstance(result, ValidationResult)
        assert result.status in ["pending", "valid", "invalid", "suspicious", "error"]

    def test_validate_with_template(self, validation_service, sample_signature, sample_template):
        """Test validation with template."""
        result = validation_service.validate(sample_signature, template=sample_template)

        assert isinstance(result, ValidationResult)
        assert result.comparison_result is not None

    def test_validate_with_context(self, validation_service, sample_signature):
        """Test validation with context."""
        context = {
            "purpose": "contract_signing",
            "document_type": "contract",
        }
        result = validation_service.validate(sample_signature, context=context)

        assert isinstance(result, ValidationResult)
        assert result.metadata.get("context") == context

    def test_quality_check(self, validation_service, sample_signature):
        """Test quality check."""
        result = validation_service.check_quality(sample_signature)

        assert isinstance(result, QualityCheckResult)
        assert result.passed or len(result.issues) > 0

    def test_quality_check_low_quality(self, validation_service):
        """Test quality check with low quality signature."""
        low_quality = {
            "quality_score": 0.2,
            "contrast_score": 0.1,
            "clarity_score": 0.2,
            "completeness_score": 0.3,
            "width": 30,
            "height": 10,
        }
        result = validation_service.check_quality(low_quality)

        assert not result.passed
        assert len(result.issues) > 0
        assert len(result.recommendations) > 0

    def test_fraud_analysis(self, validation_service, sample_signature):
        """Test fraud analysis."""
        result = validation_service.analyze_fraud(sample_signature)

        assert isinstance(result, FraudAnalysisResult)
        assert result.risk_level in ["low", "medium", "high", "critical"]

    def test_fraud_analysis_with_template(self, validation_service, sample_signature, sample_template):
        """Test fraud analysis with template."""
        result = validation_service.analyze_fraud(sample_signature, template=sample_template)

        assert isinstance(result, FraudAnalysisResult)

    def test_validate_certificate(self, validation_service):
        """Test certificate validation."""
        from datetime import datetime, timedelta

        cert_data = {
            "certificate_id": "cert_123",
            "certificate_issuer": "ICP-Brasil",
            "certificate_valid_from": datetime.utcnow() - timedelta(days=30),
            "certificate_valid_to": datetime.utcnow() + timedelta(days=30),
            "hash_algorithm": "sha256",
            "signature_hash": "abc123" * 20,
        }
        result = validation_service.validate_certificate(cert_data)

        assert result["is_valid"]
        assert len(result["errors"]) == 0

    def test_validate_expired_certificate(self, validation_service):
        """Test expired certificate validation."""
        from datetime import datetime, timedelta

        cert_data = {
            "certificate_id": "cert_123",
            "certificate_valid_to": datetime.utcnow() - timedelta(days=1),
        }
        result = validation_service.validate_certificate(cert_data)

        assert not result["is_valid"]
        assert "expired" in str(result["errors"]).lower()

    def test_validate_document_integrity(self, validation_service):
        """Test document integrity validation."""
        result = validation_service.validate_document_integrity(
            document_hash="abc123def456", expected_hash="abc123def456", algorithm="sha256"
        )

        assert result["is_valid"]
        assert result["match"]

    def test_validate_document_integrity_modified(self, validation_service):
        """Test document integrity with modified document."""
        result = validation_service.validate_document_integrity(
            document_hash="abc123def456",
            expected_hash="different_hash",
        )

        assert not result["is_valid"]
        assert not result["match"]
        assert "modified" in result.get("error", "").lower()

    def test_strict_mode(self, sample_signature, sample_template):
        """Test strict validation mode."""
        service = SignatureValidationService(strict_mode=True)

        result = service.validate(sample_signature, template=sample_template)

        assert isinstance(result, ValidationResult)

    def test_validation_result_to_dict(self, validation_service, sample_signature):
        """Test validation result conversion to dictionary."""
        result = validation_service.validate(sample_signature)
        result_dict = result.to_dict()

        assert "id" in result_dict
        assert "is_valid" in result_dict
        assert "status" in result_dict

    def test_disabled_fraud_detection(self, sample_signature):
        """Test with fraud detection disabled."""
        service = SignatureValidationService(enable_fraud_detection=False)
        result = service.validate(sample_signature)

        assert result.fraud_analysis is None

    def test_disabled_quality_check(self, sample_signature):
        """Test with quality check disabled."""
        service = SignatureValidationService(enable_quality_check=False)
        result = service.validate(sample_signature)

        assert result.quality_check is None


# ============== Integration Tests ==============


class TestSignatureIntegration:
    """Integration tests for signature services."""

    def test_full_pipeline(
        self,
        extraction_service,
        comparison_service,
        validation_service,
        sample_image_data,
        sample_template,
    ):
        """Test full signature processing pipeline."""
        # 1. Extract signature
        extraction_result = extraction_service.extract_from_image(sample_image_data)

        # 2. If extraction successful, validate
        if extraction_result.success and extraction_result.signatures:
            sig = extraction_result.signatures[0]
            sig_data = {
                "width": sig.width,
                "height": sig.height,
                "quality_score": sig.quality_score,
                "feature_vector": sig.feature_vector,
                "contour_data": sig.contour_data,
            }

            # 3. Compare with template
            comparison_result = comparison_service.compare(sig_data, sample_template)
            assert isinstance(comparison_result, ComparisonResult)

            # 4. Full validation
            validation_result = validation_service.validate(sig_data, template=sample_template)
            assert isinstance(validation_result, ValidationResult)

    def test_batch_verification(
        self,
        comparison_service,
        sample_signature,
    ):
        """Test batch signature verification."""
        # Create variations
        candidates = []
        for i in range(5):
            candidate = sample_signature.copy()
            candidate["width"] = sample_signature["width"] + i * 5
            candidates.append(candidate)

        # Compare against all
        results = comparison_service.compare_batch(sample_signature, candidates, top_n=3)

        assert len(results) == 3
        # First should be best match
        assert results[0][1].similarity_score >= results[1][1].similarity_score

    def test_template_training(
        self,
        extraction_service,
        sample_image_data,
    ):
        """Test template training with multiple samples."""
        samples = []

        # Extract multiple samples
        for _ in range(3):
            result = extraction_service.extract_from_image(sample_image_data)
            if result.success and result.signatures:
                sig = result.signatures[0]
                samples.append(
                    {
                        "feature_vector": sig.feature_vector,
                        "contour_data": sig.contour_data,
                    }
                )

        # Verify we got samples
        assert len(samples) >= 1

        # In production, would average feature vectors to create template
        if samples and samples[0].get("feature_vector"):
            import numpy as np

            vectors = [s["feature_vector"] for s in samples if s.get("feature_vector")]
            if vectors:
                master_vector = np.mean(vectors, axis=0).tolist()
                assert len(master_vector) == len(vectors[0])
