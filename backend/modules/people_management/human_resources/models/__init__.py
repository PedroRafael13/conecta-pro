"""
Models do modulo de Recursos Humanos.

Re-exporta models existentes e expoe novos models de
Treinamento, Avaliacao de Desempenho e Plano de Carreira.
"""

# Novos models do modulo RH
from modules.people_management.human_resources.models.career import (
    CareerLevel,
    CareerPlan,
    CareerPlanStatus,
)
from modules.people_management.human_resources.models.performance import (
    PerformanceReview,
    ReviewStatus,
    ReviewType,
)
from modules.people_management.human_resources.models.training import (
    CertificateStatus,
    EnrollmentStatus,
    Training,
    TrainingCategoryCourse,
    TrainingCertificate,
    TrainingCourse,
    TrainingEnrollment,
    TrainingStatus,
)

# Re-exportar models existentes com try/except
try:
    from modules.recruitment.models.candidate import Candidate, CandidateStatus
except ImportError:
    Candidate = None  # type: ignore[assignment, misc]
    CandidateStatus = None  # type: ignore[assignment, misc]

try:
    from modules.recruitment.models.job_position import JobPosition
except ImportError:
    JobPosition = None  # type: ignore[assignment, misc]

try:
    from modules.retention.climate.models.climate_models import ClimateSurvey
except ImportError:
    ClimateSurvey = None  # type: ignore[assignment, misc]

try:
    from modules.retention.turnover.models.turnover_models import TurnoverPrediction
except ImportError:
    TurnoverPrediction = None  # type: ignore[assignment, misc]

try:
    from modules.retention.onboarding.models import OnboardingChecklist
except ImportError:
    OnboardingChecklist = None  # type: ignore[assignment, misc]

__all__ = [
    # Training
    "TrainingCourse",
    "Training",
    "TrainingEnrollment",
    "TrainingCertificate",
    "TrainingCategoryCourse",
    "TrainingStatus",
    "EnrollmentStatus",
    "CertificateStatus",
    # Performance
    "PerformanceReview",
    "ReviewType",
    "ReviewStatus",
    # Career
    "CareerPlan",
    "CareerLevel",
    "CareerPlanStatus",
    # Re-exports
    "Candidate",
    "CandidateStatus",
    "JobPosition",
    "ClimateSurvey",
    "TurnoverPrediction",
    "OnboardingChecklist",
]
