"""Skill IA: Smart Notifier — Sistema inteligente de notificações."""

import logging
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class NotifierSkill:
    """Skill IA para notificações inteligentes e contextuais."""

    SKILL_NAME = "smart_notifier"
    DESCRIPTION = "Notificações inteligentes baseadas em eventos e prazos"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def send_notification(
        self, employee_id: str, title: str, message: str, notification_type: str = "info"
    ) -> dict:
        """Envia notificação ao funcionário via portal."""
        try:
            from modules.people_management.employee_portal.models.notification import PortalNotification

            notification = PortalNotification(
                id=uuid4(),
                employee_id=employee_id,
                title=title,
                message=message,
                type=notification_type,
                is_read=False,
            )
            self.db.add(notification)
            await self.db.flush()
            return {"status": "sent", "notification_id": str(notification.id)}
        except Exception as e:
            logger.warning("Falha ao enviar notificação: %s", e)
            return {"status": "failed", "error": str(e)}

    async def check_pending_alerts(self) -> dict:
        """Verifica alertas pendentes: vencimentos, prazos, compliance."""
        alerts = []

        try:
            from modules.people_management.human_resources.models.training import CertificateStatus, TrainingCertificate

            cutoff = datetime.utcnow() + timedelta(days=30)
            result = await self.db.execute(
                select(TrainingCertificate).where(
                    TrainingCertificate.status == CertificateStatus.VALID,
                    TrainingCertificate.expires_at is not None,
                    TrainingCertificate.expires_at <= cutoff,
                )
            )
            for cert in result.scalars().all():
                alerts.append(
                    {
                        "type": "certificate_expiring",
                        "severity": "warning",
                        "employee_id": str(cert.employee_id),
                        "message": f"Certificado {cert.certificate_number} vence em breve",
                    }
                )
        except Exception as e:
            logger.debug("Erro ao verificar certificados: %s", e)

        try:
            from modules.people_management.hr.models.contract import EmploymentContract

            cutoff_date = (datetime.utcnow() + timedelta(days=30)).date()
            result = await self.db.execute(
                select(EmploymentContract).where(
                    EmploymentContract.status == "active",
                    EmploymentContract.contract_type == "experience",
                    EmploymentContract.end_date is not None,
                    EmploymentContract.end_date <= cutoff_date,
                )
            )
            for c in result.scalars().all():
                alerts.append(
                    {
                        "type": "contract_expiring",
                        "severity": "warning",
                        "employee_id": str(c.employee_id),
                        "message": f"Contrato de experiência vence em {c.end_date}",
                    }
                )
        except Exception as e:
            logger.debug("Erro ao verificar contratos: %s", e)

        return {
            "total_alerts": len(alerts),
            "alerts": alerts,
            "checked_at": datetime.utcnow().isoformat(),
        }
