"""
Module: health_occupational
Description: API para Saude Ocupacional (NR-4, NR-6, NR-7, NR-9)
Author: Conecta PRO Team
Date: 2026-01-11
Version: 2.0.0
Quality Score Target: 99+/100
Compliance: NRs do Ministerio do Trabalho

Este modulo implementa a gestao de saude ocupacional seguindo as Normas
Regulamentadoras do Ministerio do Trabalho:

- NR-4: SESMT - Servicos Especializados em Engenharia de Seguranca
- NR-6: EPI - Equipamento de Protecao Individual
- NR-7: PCMSO - Programa de Controle Medico de Saude Ocupacional
- NR-9: PPRA/PGR - Programa de Prevencao de Riscos Ambientais

Estrutura Modular:
- models/: Modelos SQLAlchemy
- schemas/: Schemas Pydantic para validacao
- controllers/: Endpoints REST FastAPI
- services/: Logica de negocio
- repositories/: Camada de acesso a dados
"""

from fastapi import APIRouter

# Importar routers dos controllers
from modules.health_occupational.controllers import (
    pcmso_router,
    ppra_router,
    epi_router,
    health_router,
)

# Importar models para registro no SQLAlchemy
from modules.health_occupational.models import (
    # PCMSO
    MedicalExam,
    ASO,
    ComplementaryExam,
    ExamType,
    ExamStatus,
    FitnessResult,
    # PPRA
    RiskMapping,
    OccupationalRisk,
    ControlMeasure,
    RiskCategory,
    RiskLevel,
    RiskAgent,
    # EPI
    EPI,
    EPIDelivery,
    EPIInventory,
    EPICategory,
    EPIStatus,
    DeliveryReason,
)

# Importar services
from modules.health_occupational.services import (
    PCMSOService,
    PPRAService,
    EPIService,
)

# Importar repositories
from modules.health_occupational.repositories import (
    PCMSORepository,
    PPRARepository,
    EPIRepository,
)

# Criar router principal do modulo
router = APIRouter(prefix="/health-occupational", tags=["Health - Saude Ocupacional"])

# Incluir sub-routers
router.include_router(pcmso_router)
router.include_router(ppra_router)
router.include_router(epi_router)
router.include_router(health_router)

# Manter compatibilidade com versao anterior
health_occupational_router = router

__all__ = [
    # Router principal
    "router",
    "health_occupational_router",
    # Sub-routers
    "pcmso_router",
    "ppra_router",
    "epi_router",
    "health_router",
    # Models PCMSO
    "MedicalExam",
    "ASO",
    "ComplementaryExam",
    "ExamType",
    "ExamStatus",
    "FitnessResult",
    # Models PPRA
    "RiskMapping",
    "OccupationalRisk",
    "ControlMeasure",
    "RiskCategory",
    "RiskLevel",
    "RiskAgent",
    # Models EPI
    "EPI",
    "EPIDelivery",
    "EPIInventory",
    "EPICategory",
    "EPIStatus",
    "DeliveryReason",
    # Services
    "PCMSOService",
    "PPRAService",
    "EPIService",
    # Repositories
    "PCMSORepository",
    "PPRARepository",
    "EPIRepository",
]

__version__ = "2.0.0"
__author__ = "Conecta PRO Team"
