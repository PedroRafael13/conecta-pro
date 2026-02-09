"""Models do módulo Recruitment."""

from .application import (
    Application,
    ApplicationStatus,
    RejectionReason,
)
from .candidate import (
    Candidate,
    CandidateSource,
    CandidateStatus,
    Gender,
    MaritalStatus,
)
from .candidate_education import (
    CandidateEducation,
    EducationLevel,
    EducationStatus,
    StudyPeriod,
)
from .candidate_experience import (
    CandidateExperience,
    EmploymentType,
    ExperienceLevel,
)
from .candidate_skill import (
    CandidateSkill,
    SkillCategory,
    SkillLevel,
)
from .interview import (
    Interview,
    InterviewResult,
    InterviewStatus,
    InterviewType,
)
from .job_position import (
    Department,
    JobPosition,
    PositionLevel,
    PositionStatus,
    PositionType,
    WorkModel,
)

__all__ = [
    # JobPosition
    "JobPosition",
    "PositionType",
    "PositionLevel",
    "PositionStatus",
    "WorkModel",
    "Department",
    # Candidate
    "Candidate",
    "CandidateStatus",
    "CandidateSource",
    "Gender",
    "MaritalStatus",
    # Application
    "Application",
    "ApplicationStatus",
    "RejectionReason",
    # Interview
    "Interview",
    "InterviewType",
    "InterviewStatus",
    "InterviewResult",
    # CandidateSkill
    "CandidateSkill",
    "SkillCategory",
    "SkillLevel",
    # CandidateExperience
    "CandidateExperience",
    "EmploymentType",
    "ExperienceLevel",
    # CandidateEducation
    "CandidateEducation",
    "EducationLevel",
    "EducationStatus",
    "StudyPeriod",
]
