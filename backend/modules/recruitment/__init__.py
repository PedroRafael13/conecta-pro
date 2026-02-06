"""
Módulo de Recrutamento e Seleção.

Este módulo gerencia todo o processo de recrutamento:
- Vagas de emprego (JobPosition)
- Candidatos (Candidate)
- Candidaturas (Application)
- Entrevistas (Interview)
- Habilidades (CandidateSkill)
- Experiências (CandidateExperience)
- Formação (CandidateEducation)

Features:
- Matching de candidatos com vagas usando IA
- Score de compatibilidade
- Parsing de currículo
- Workflow de candidatura
- Agendamento de entrevistas
- Geração de perguntas para entrevista
"""

from fastapi import APIRouter

from .controllers import (
    job_position_router,
    candidate_router,
    application_router,
    interview_router,
)

# Router principal do módulo
router = APIRouter(prefix="/recruitment", tags=["Recruitment"])

# Inclui sub-routers
router.include_router(job_position_router)
router.include_router(candidate_router)
router.include_router(application_router)
router.include_router(interview_router)

__all__ = [
    "router",
]
