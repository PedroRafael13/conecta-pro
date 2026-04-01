"""Skill IA: Training Advisor — Gestão inteligente de treinamentos."""

import logging
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.people_management.human_resources.models.training import (
    CertificateStatus,
    EnrollmentStatus,
    Training,
    TrainingCertificate,
    TrainingCourse,
    TrainingEnrollment,
)

logger = logging.getLogger(__name__)


class TrainerSkill:
    """Skill IA para gestão e análise de treinamentos."""

    SKILL_NAME = "training_advisor"
    DESCRIPTION = "Análise de necessidades de treinamento e compliance"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def training_dashboard(self) -> dict:
        """Dashboard geral de treinamentos."""
        courses_result = await self.db.execute(
            select(func.count()).select_from(TrainingCourse).where(TrainingCourse.is_active)
        )
        total_courses = courses_result.scalar() or 0

        status_result = await self.db.execute(
            select(Training.status, func.count(Training.id)).group_by(Training.status)
        )
        by_status = {str(row[0]): row[1] for row in status_result.all()}

        enrollments_result = await self.db.execute(
            select(func.count())
            .select_from(TrainingEnrollment)
            .where(TrainingEnrollment.status.in_([EnrollmentStatus.ENROLLED, EnrollmentStatus.CONFIRMED]))
        )
        active_enrollments = enrollments_result.scalar() or 0

        certs_result = await self.db.execute(
            select(func.count())
            .select_from(TrainingCertificate)
            .where(TrainingCertificate.status == CertificateStatus.VALID)
        )
        valid_certs = certs_result.scalar() or 0

        return {
            "total_active_courses": total_courses,
            "trainings_by_status": by_status,
            "active_enrollments": active_enrollments,
            "valid_certificates": valid_certs,
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def expiring_certificates(self, days_ahead: int = 30) -> dict:
        """Lista certificados próximos do vencimento."""
        cutoff = datetime.utcnow() + timedelta(days=days_ahead)

        result = await self.db.execute(
            select(TrainingCertificate).where(
                TrainingCertificate.status == CertificateStatus.VALID,
                TrainingCertificate.expires_at is not None,
                TrainingCertificate.expires_at <= cutoff,
            )
        )
        certs = result.scalars().all()

        return {
            "days_ahead": days_ahead,
            "expiring_count": len(certs),
            "certificates": [
                {
                    "id": str(c.id),
                    "employee_id": str(c.employee_id),
                    "certificate_number": c.certificate_number,
                    "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                }
                for c in certs
            ],
        }
