"""Services do modulo de Ocorrencias."""

from .occurrence_service import (
    OccurrenceService,
    OccurrenceServiceError,
    OccurrenceNotFoundError,
    OccurrenceValidationError,
)
from .occurrence_ai_analyzer import (
    OccurrenceAIAnalyzer,
    ClassificationResult,
    PatternAnalysis,
)

__all__ = [
    # Service
    "OccurrenceService",
    # Exceptions
    "OccurrenceServiceError",
    "OccurrenceNotFoundError",
    "OccurrenceValidationError",
    # AI Analyzer
    "OccurrenceAIAnalyzer",
    "ClassificationResult",
    "PatternAnalysis",
]
