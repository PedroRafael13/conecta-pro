"""Signature Recognition Module.

This module provides signature extraction, comparison, and validation
for digital and handwritten signatures.
"""

from modules.ai.signature.models import (
    Signature,
    SignatureTemplate,
    SignatureVerification,
    SignatureRequest,
    SignedDocument,
)
from modules.ai.signature.services import (
    SignatureExtractionService,
    SignatureComparisonService,
    SignatureValidationService,
)
from modules.ai.signature.controllers import signature_router

__all__ = [
    # Models
    "Signature",
    "SignatureTemplate",
    "SignatureVerification",
    "SignatureRequest",
    "SignedDocument",
    # Services
    "SignatureExtractionService",
    "SignatureComparisonService",
    "SignatureValidationService",
    # Controllers
    "signature_router",
]
