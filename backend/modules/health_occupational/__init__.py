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
    epi_router,
    health_router,
    pcmso_router,
    ppra_router,
)

# Importar models para registro no SQLAlchemy
from modules.health_occupational.models import (
    ASO,
    # EPI
    EPI,
    ComplementaryExam,
    ControlMeasure,
    DeliveryReason,
    EPICategory,
    EPIDelivery,
    EPIInventory,
    EPIStatus,
    ExamStatus,
    ExamType,
    FitnessResult,
    # PCMSO
    MedicalExam,
    OccupationalRisk,
    RiskAgent,
    RiskCategory,
    RiskLevel,
    # PPRA
    RiskMapping,
)

# Importar repositories
from modules.health_occupational.repositories import (
    EPIRepository,
    PCMSORepository,
    PPRARepository,
)

# Importar services
from modules.health_occupational.services import (
    EPIService,
    PCMSOService,
    PPRAService,
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

# Registrar subscribers de eventos RH na inicialização
try:
    from modules.health_occupational.integrations.hr_events import register_hr_event_subscribers

    register_hr_event_subscribers()
except Exception as _e:
    import logging as _log

    _log.getLogger(__name__).warning("Health Occupational: falha ao registrar subscribers: %s", _e)
