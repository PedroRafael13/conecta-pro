"""Controllers do módulo Recruitment."""

from .application_controller import router as application_router
from .candidate_controller import router as candidate_router
from .interview_controller import router as interview_router
from .job_position_controller import router as job_position_router

__all__ = [
    "job_position_router",
    "candidate_router",
    "application_router",
    "interview_router",
]
