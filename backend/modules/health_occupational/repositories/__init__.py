"""Repositories do modulo de Saude Ocupacional."""

from modules.health_occupational.repositories.epi_repository import EPIRepository
from modules.health_occupational.repositories.pcmso_repository import PCMSORepository
from modules.health_occupational.repositories.ppra_repository import PPRARepository

__all__ = [
    "PCMSORepository",
    "PPRARepository",
    "EPIRepository",
]
