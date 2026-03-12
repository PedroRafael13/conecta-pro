"""
Schemas Pydantic do modulo de Recursos Humanos.

Exporta todos os schemas de treinamento, desempenho, carreira
e re-exporta schemas de recrutamento.
"""

from modules.people_management.human_resources.schemas.career import (
    CareerPlanCreate,
    CareerPlanListResponse,
    CareerPlanResponse,
    CareerPlanUpdate,
    MilestoneCreate,
    MilestoneUpdate,
)
from modules.people_management.human_resources.schemas.performance import (
    PerformanceReviewCreate,
    PerformanceReviewListResponse,
    PerformanceReviewResponse,
    PerformanceReviewUpdate,
    ScoresBreakdown,
)
from modules.people_management.human_resources.schemas.training import (
    TrainingCertificateResponse,
    TrainingCourseCreate,
    TrainingCourseListResponse,
    TrainingCourseResponse,
    TrainingCourseUpdate,
    TrainingCreate,
    TrainingEnrollmentCreate,
    TrainingEnrollmentListResponse,
    TrainingEnrollmentResponse,
    TrainingEnrollmentUpdate,
    TrainingListResponse,
    TrainingResponse,
    TrainingUpdate,
)

__all__ = [
    # Training
    "TrainingCourseCreate",
    "TrainingCourseUpdate",
    "TrainingCourseResponse",
    "TrainingCourseListResponse",
    "TrainingCreate",
    "TrainingUpdate",
    "TrainingResponse",
    "TrainingListResponse",
    "TrainingEnrollmentCreate",
    "TrainingEnrollmentUpdate",
    "TrainingEnrollmentResponse",
    "TrainingEnrollmentListResponse",
    "TrainingCertificateResponse",
    # Performance
    "PerformanceReviewCreate",
    "PerformanceReviewUpdate",
    "PerformanceReviewResponse",
    "PerformanceReviewListResponse",
    "ScoresBreakdown",
    # Career
    "CareerPlanCreate",
    "CareerPlanUpdate",
    "CareerPlanResponse",
    "CareerPlanListResponse",
    "MilestoneCreate",
    "MilestoneUpdate",
]
