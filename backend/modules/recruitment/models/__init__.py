"""Models do módulo Recruitment."""

from .job_position import (
    JobPosition,
    PositionType,
    PositionLevel,
    PositionStatus,
    WorkModel,
    Department,
)
from .candidate import (
    Candidate,
    CandidateStatus,
    CandidateSource,
    Gender,
    MaritalStatus,
)
from .application import (
    Application,
    ApplicationStatus,
    RejectionReason,
)
from .interview import (
    Interview,
    InterviewType,
    InterviewStatus,
    InterviewResult,
)
from .candidate_skill import (
    CandidateSkill,
    SkillCategory,
    SkillLevel,
)
from .candidate_experience import (
    CandidateExperience,
    EmploymentType,
    ExperienceLevel,
)
from .candidate_education import (
    CandidateEducation,
    EducationLevel,
    EducationStatus,
    StudyPeriod,
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
