"""
Re-exportacao do service de Recrutamento.

Permite acesso ao CandidateService e outros services de recrutamento
a partir do modulo de Recursos Humanos.
"""

try:
    from modules.recruitment.services.candidate_service import CandidateService
except ImportError:
    CandidateService = None  # type: ignore[assignment, misc]

try:
    from modules.recruitment.services.job_position_service import JobPositionService
except ImportError:
    JobPositionService = None  # type: ignore[assignment, misc]

try:
    from modules.recruitment.services.application_service import ApplicationService
except ImportError:
    ApplicationService = None  # type: ignore[assignment, misc]

try:
    from modules.recruitment.services.interview_service import InterviewService
except ImportError:
    InterviewService = None  # type: ignore[assignment, misc]

__all__ = [
    "CandidateService",
    "JobPositionService",
    "ApplicationService",
    "InterviewService",
]
