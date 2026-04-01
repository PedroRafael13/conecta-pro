"""Models do modulo Recruitment."""

from .application import Application, ApplicationStatus, RejectionReason
from .candidate import (
    Candidate,
    CandidateSource,
    CandidateStatus,
    Gender,
    MaritalStatus,
)
from .candidate_education import CandidateEducation
from .candidate_experience import CandidateExperience
from .candidate_skill import CandidateSkill, SkillCategory, SkillLevel

# Interview MUST be imported before Application (Application has relationship to Interview)
from .interview import Interview, InterviewResult, InterviewStatus, InterviewType
from .job_position import (
    Department,
    JobPosition,
    PositionLevel,
    PositionStatus,
    PositionType,
    WorkModel,
)

__all__ = [
    "JobPosition",
    "PositionType",
    "PositionLevel",
    "PositionStatus",
    "WorkModel",
    "Department",
    "Candidate",
    "CandidateStatus",
    "CandidateSource",
    "Gender",
    "MaritalStatus",
    "Application",
    "ApplicationStatus",
    "RejectionReason",
    "Interview",
    "InterviewType",
    "InterviewStatus",
    "InterviewResult",
    "CandidateSkill",
    "SkillCategory",
    "SkillLevel",
    "CandidateExperience",
    "CandidateEducation",
]
