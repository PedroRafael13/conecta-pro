"""Schemas do modulo Recruitment."""

from .application import (
    ApplicationAdvance,
    ApplicationBulkAction,
    ApplicationCreate,
    ApplicationFilter,
    ApplicationHire,
    ApplicationListResponse,
    ApplicationProposal,
    ApplicationReject,
    ApplicationResponse,
    ApplicationStats,
    ApplicationUpdate,
)
from .candidate import (
    CandidateBlock,
    CandidateCreate,
    CandidateFilter,
    CandidateImport,
    CandidateListResponse,
    CandidateResponse,
    CandidateStats,
    CandidateUpdate,
)
from .candidate_education import (
    CandidateEducationCreate,
    CandidateEducationResponse,
    CandidateEducationUpdate,
)
from .candidate_experience import (
    CandidateExperienceCreate,
    CandidateExperienceResponse,
    CandidateExperienceUpdate,
)
from .candidate_skill import (
    CandidateSkillCreate,
    CandidateSkillResponse,
    CandidateSkillUpdate,
)
from .interview import (
    InterviewCalendar,
    InterviewCancel,
    InterviewComplete,
    InterviewCreate,
    InterviewEvaluation,
    InterviewFilter,
    InterviewListResponse,
    InterviewReschedule,
    InterviewResponse,
    InterviewSlot,
    InterviewStats,
    InterviewUpdate,
)
from .job_position import (
    JobPositionCreate,
    JobPositionFilter,
    JobPositionListResponse,
    JobPositionPublish,
    JobPositionResponse,
    JobPositionStats,
    JobPositionUpdate,
)

__all__ = [
    # JobPosition
    "JobPositionCreate",
    "JobPositionUpdate",
    "JobPositionResponse",
    "JobPositionListResponse",
    "JobPositionFilter",
    "JobPositionStats",
    "JobPositionPublish",
    # Candidate
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateResponse",
    "CandidateListResponse",
    "CandidateFilter",
    "CandidateStats",
    "CandidateBlock",
    "CandidateImport",
    # Application
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationResponse",
    "ApplicationListResponse",
    "ApplicationFilter",
    "ApplicationStats",
    "ApplicationAdvance",
    "ApplicationReject",
    "ApplicationProposal",
    "ApplicationHire",
    "ApplicationBulkAction",
    # Interview
    "InterviewCreate",
    "InterviewUpdate",
    "InterviewResponse",
    "InterviewListResponse",
    "InterviewFilter",
    "InterviewStats",
    "InterviewComplete",
    "InterviewReschedule",
    "InterviewCancel",
    "InterviewEvaluation",
    "InterviewSlot",
    "InterviewCalendar",
    # CandidateSkill
    "CandidateSkillCreate",
    "CandidateSkillUpdate",
    "CandidateSkillResponse",
    # CandidateExperience
    "CandidateExperienceCreate",
    "CandidateExperienceUpdate",
    "CandidateExperienceResponse",
    # CandidateEducation
    "CandidateEducationCreate",
    "CandidateEducationUpdate",
    "CandidateEducationResponse",
]
