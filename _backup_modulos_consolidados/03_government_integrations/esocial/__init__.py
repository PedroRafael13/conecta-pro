"""
Package: esocial
Description: Modulo de integracao com eSocial
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: Decreto 8.373/2014 - eSocial
"""

from .esocial_transmitter import (
    ESocialTransmitter,
    ESocialEvent,
    EventType,
    TransmissionStatus,
    Environment,
    ESocialError,
    ValidationError,
    TransmissionError,
    CertificateInfo,
    XMLBuilder,
    ESocialEventModel,
    get_esocial_transmitter,
    init_esocial_transmitter,
)

__all__ = [
    "ESocialTransmitter",
    "ESocialEvent",
    "EventType",
    "TransmissionStatus",
    "Environment",
    "ESocialError",
    "ValidationError",
    "TransmissionError",
    "CertificateInfo",
    "XMLBuilder",
    "ESocialEventModel",
    "get_esocial_transmitter",
    "init_esocial_transmitter",
]

__version__ = "1.0.0"
