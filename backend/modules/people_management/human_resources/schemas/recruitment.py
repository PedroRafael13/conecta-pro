"""
Re-exportacao de schemas do modulo de Recrutamento.

Permite acesso aos schemas de recrutamento a partir do modulo
de Recursos Humanos, mantendo compatibilidade com imports existentes.
"""

try:
    from modules.recruitment.schemas.candidate import (
        CandidateBlock,
        CandidateCreate,
        CandidateFilter,
        CandidateImport,
        CandidateListResponse,
        CandidateResponse,
        CandidateStats,
        CandidateUpdate,
    )
except ImportError:
    CandidateCreate = None  # type: ignore[assignment, misc]
    CandidateUpdate = None  # type: ignore[assignment, misc]
    CandidateResponse = None  # type: ignore[assignment, misc]
    CandidateListResponse = None  # type: ignore[assignment, misc]
    CandidateFilter = None  # type: ignore[assignment, misc]
    CandidateStats = None  # type: ignore[assignment, misc]
    CandidateBlock = None  # type: ignore[assignment, misc]
    CandidateImport = None  # type: ignore[assignment, misc]

try:
    from modules.recruitment.schemas.job_position import (
        JobPositionCreate,
        JobPositionListResponse,
        JobPositionResponse,
        JobPositionUpdate,
    )
except ImportError:
    JobPositionCreate = None  # type: ignore[assignment, misc]
    JobPositionUpdate = None  # type: ignore[assignment, misc]
    JobPositionResponse = None  # type: ignore[assignment, misc]
    JobPositionListResponse = None  # type: ignore[assignment, misc]

try:
    from modules.recruitment.schemas.application import (
        ApplicationCreate,
        ApplicationListResponse,
        ApplicationResponse,
        ApplicationUpdate,
    )
except ImportError:
    ApplicationCreate = None  # type: ignore[assignment, misc]
    ApplicationUpdate = None  # type: ignore[assignment, misc]
    ApplicationResponse = None  # type: ignore[assignment, misc]
    ApplicationListResponse = None  # type: ignore[assignment, misc]

try:
    from modules.recruitment.schemas.interview import (
        InterviewCreate,
        InterviewListResponse,
        InterviewResponse,
        InterviewUpdate,
    )
except ImportError:
    InterviewCreate = None  # type: ignore[assignment, misc]
    InterviewUpdate = None  # type: ignore[assignment, misc]
    InterviewResponse = None  # type: ignore[assignment, misc]
    InterviewListResponse = None  # type: ignore[assignment, misc]

__all__ = [
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateResponse",
    "CandidateListResponse",
    "CandidateFilter",
    "CandidateStats",
    "CandidateBlock",
    "CandidateImport",
    "JobPositionCreate",
    "JobPositionUpdate",
    "JobPositionResponse",
    "JobPositionListResponse",
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationResponse",
    "ApplicationListResponse",
    "InterviewCreate",
    "InterviewUpdate",
    "InterviewResponse",
    "InterviewListResponse",
]
