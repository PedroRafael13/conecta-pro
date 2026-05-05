"""Notification Triggers - Triggers automáticos de notificações do módulo operacional.

Sprint: Módulo Operacional - Sistema de Notificações Push
"""

import logging
from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from core.database import get_db
from modules.config.models.tenant import Tenant
from modules.notifications.models import QueuePriority
from modules.notifications.services.push_service import PushNotificationService
from modules.operacional.models.employee import Employee
from modules.operacional.models.post import Post
from modules.operacional.models.scale import Scale
from modules.operacional.models.shift import Shift, ShiftStatus
from modules.operacional.models.substitution import Substitution, SubstitutionStatus

logger = logging.getLogger(__name__)

# Tolerância de atraso em minutos
LATE_TOLERANCE_MINUTES = 15
# Tempo limite para aprovações pendentes (horas)
PENDING_APPROVAL_HOURS = 24


def _get_active_tenants(db: Session) -> list[UUID]:
    """Busca todos os tenant_ids ativos.

    Returns:
        Lista de UUIDs dos tenants ativos.
    """
    rows = (
        db.query(Tenant.id)
        .filter(
            Tenant.status == "active",
            Tenant.ativo.is_(True),
        )
        .all()
    )
    return [row[0] for row in rows]


class OperacionalNotificationTriggers:
    """Triggers de notificações automáticas para o módulo operacional."""

    def __init__(self, db: Session, tenant_id: UUID):
        """Inicializa triggers.

        Args:
            db: Sessão do banco de dados
            tenant_id: ID do tenant
        """
        self.db = db
        self.tenant_id = tenant_id
        self.push_service = PushNotificationService(db, tenant_id)

    def check_late_employees(self) -> dict:
        """Verifica colaboradores atrasados e envia notificações.

        Busca shifts agendados para hoje cujo horário planejado já passou
        (com tolerância) e que ainda não tiveram check-in.

        Returns:
            Dicionário com resultado da verificação
        """
        try:
            logger.info(f"Verificando colaboradores atrasados para tenant {self.tenant_id}...")

            today = date.today()
            now = datetime.now()
            threshold_time = (now - timedelta(minutes=LATE_TOLERANCE_MINUTES)).time()

            # Busca shifts atrasados: agendados para hoje, sem check-in,
            # cujo horário planejado + tolerância já passou
            late_shifts = (
                self.db.query(Shift, Employee, Post)
                .join(Scale, Shift.scale_id == Scale.id)
                .join(Post, Shift.post_id == Post.id)
                .join(Employee, Shift.employee_id == Employee.id)
                .filter(
                    Post.client_id == str(self.tenant_id),
                    Shift.shift_date == today,
                    Shift.status == ShiftStatus.SCHEDULED.value,
                    Shift.actual_start_time.is_(None),
                    Shift.planned_start_time <= threshold_time,
                    Shift.is_active.is_(True),
                )
                .all()
            )

            notifications_sent = 0
            details = []

            for shift, employee, post in late_shifts:
                # Notifica o gestor do colaborador, se existir
                gestor_id = getattr(employee, "gestor_id", None)
                if not gestor_id:
                    logger.debug(f"Colaborador {employee.nome} sem gestor_id, pulando notificação")
                    continue

                planned = shift.planned_start_time
                minutes_late = int((now - datetime.combine(today, planned)).total_seconds() / 60)

                result = self.push_service.send_push_notification(
                    user_id=UUID(str(gestor_id)),
                    title="Colaborador Atrasado",
                    body=(f"{employee.nome} está {minutes_late}min atrasado(a) para o posto {post.name}"),
                    data={
                        "type": "late_employee",
                        "employee_id": str(employee.id),
                        "shift_id": str(shift.id),
                        "post_id": str(post.id),
                        "minutes_late": minutes_late,
                    },
                    priority=QueuePriority.HIGH,
                    action_url=f"/modulos/operacional/escalas?shift={shift.id}",
                )

                if result.get("success"):
                    notifications_sent += 1

                details.append(
                    {
                        "employee": employee.nome,
                        "post": post.name,
                        "minutes_late": minutes_late,
                        "notified_gestor": str(gestor_id),
                    }
                )

            logger.info(
                f"Tenant {self.tenant_id}: {len(late_shifts)} atrasados, {notifications_sent} notificações enviadas"
            )

            return {
                "success": True,
                "late_employees": len(late_shifts),
                "notifications_sent": notifications_sent,
                "details": details,
            }

        except Exception as e:
            logger.error(f"Erro ao verificar atrasos (tenant {self.tenant_id}): {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def check_pending_approvals(self) -> dict:
        """Verifica aprovações de substituição pendentes e envia notificações.

        Busca substituições com status PENDING há mais de 24 horas
        e notifica quem solicitou.

        Returns:
            Dicionário com resultado da verificação
        """
        try:
            logger.info(f"Verificando aprovações pendentes para tenant {self.tenant_id}...")

            cutoff = datetime.now() - timedelta(hours=PENDING_APPROVAL_HOURS)

            # Busca substituições pendentes há mais de 24h
            pending_subs = (
                self.db.query(Substitution, Post)
                .join(Post, Substitution.post_id == Post.id)
                .filter(
                    Post.client_id == str(self.tenant_id),
                    Substitution.status == SubstitutionStatus.PENDING.value,
                    Substitution.requested_at <= cutoff,
                    Substitution.is_active.is_(True),
                )
                .all()
            )

            notifications_sent = 0
            details = []

            for sub, post in pending_subs:
                if not sub.requested_by:
                    continue

                hours_pending = int((datetime.now() - sub.requested_at).total_seconds() / 3600)

                result = self.push_service.send_push_notification(
                    user_id=UUID(str(sub.requested_by)),
                    title="Substituição Pendente",
                    body=(f"Sua solicitação de substituição no posto {post.name} está pendente há {hours_pending}h"),
                    data={
                        "type": "pending_substitution",
                        "substitution_id": str(sub.id),
                        "post_id": str(post.id),
                        "hours_pending": hours_pending,
                    },
                    priority=QueuePriority.NORMAL,
                    action_url=f"/modulos/operacional/substituicoes?id={sub.id}",
                )

                if result.get("success"):
                    notifications_sent += 1

                details.append(
                    {
                        "substitution_id": str(sub.id),
                        "post": post.name,
                        "hours_pending": hours_pending,
                        "requested_by": str(sub.requested_by),
                    }
                )

            logger.info(
                f"Tenant {self.tenant_id}: {len(pending_subs)} pendentes, {notifications_sent} notificações enviadas"
            )

            return {
                "success": True,
                "pending_approvals": len(pending_subs),
                "notifications_sent": notifications_sent,
                "details": details,
            }

        except Exception as e:
            logger.error(f"Erro ao verificar aprovações (tenant {self.tenant_id}): {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def notify_scale_change(
        self,
        scale_id: UUID,
        change_type: str,
        user_id: UUID,
    ) -> dict:
        """Notifica sobre alteração em escala.

        Args:
            scale_id: ID da escala
            change_type: Tipo de alteração (created, updated, cancelled)
            user_id: ID do usuário para notificar

        Returns:
            Dicionário com resultado
        """
        try:
            messages = {
                "created": {
                    "title": "Nova Escala",
                    "body": "Uma nova escala foi criada",
                },
                "updated": {
                    "title": "Escala Alterada",
                    "body": "Uma escala foi alterada",
                },
                "cancelled": {
                    "title": "Escala Cancelada",
                    "body": "Uma escala foi cancelada",
                },
            }

            message = messages.get(change_type, messages["updated"])

            result = self.push_service.send_push_notification(
                user_id=user_id,
                title=message["title"],
                body=message["body"],
                data={
                    "type": "scale_change",
                    "change_type": change_type,
                    "scale_id": str(scale_id),
                },
                priority=QueuePriority.HIGH,
                action_url=f"/modulos/operacional/escalas/{scale_id}",
            )

            return result

        except Exception as e:
            logger.error(f"Erro ao notificar alteração de escala: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def notify_emergency(
        self,
        post_id: UUID,
        emergency_type: str,
        description: str,
        user_id: UUID,
    ) -> dict:
        """Notifica sobre emergência em posto.

        Args:
            post_id: ID do posto
            emergency_type: Tipo de emergência
            description: Descrição da emergência
            user_id: ID do usuário para notificar

        Returns:
            Dicionário com resultado
        """
        try:
            result = self.push_service.send_push_notification(
                user_id=user_id,
                title=f"EMERGÊNCIA: {emergency_type}",
                body=description,
                data={
                    "type": "emergency",
                    "emergency_type": emergency_type,
                    "post_id": str(post_id),
                },
                priority=QueuePriority.CRITICAL,
                action_url=f"/modulos/operacional/postos/{post_id}",
            )

            return result

        except Exception as e:
            logger.error(f"Erro ao notificar emergência: {e}")
            return {
                "success": False,
                "error": str(e),
            }


def run_late_employees_check():
    """Executa verificação de colaboradores atrasados para todos os tenants (cronjob)."""
    db = next(get_db())
    try:
        tenant_ids = _get_active_tenants(db)
        logger.info(f"Cronjob atrasos: processando {len(tenant_ids)} tenants")

        results = []
        for tenant_id in tenant_ids:
            try:
                triggers = OperacionalNotificationTriggers(db, tenant_id)
                result = triggers.check_late_employees()
                results.append({"tenant_id": str(tenant_id), **result})
            except Exception as e:
                logger.error(f"Cronjob atrasos falhou para tenant {tenant_id}: {e}")
                results.append({"tenant_id": str(tenant_id), "success": False, "error": str(e)})

        logger.info(f"Cronjob atrasos concluído: {len(results)} tenants processados")
    finally:
        db.close()


def run_pending_approvals_check():
    """Executa verificação de aprovações pendentes para todos os tenants (cronjob)."""
    db = next(get_db())
    try:
        tenant_ids = _get_active_tenants(db)
        logger.info(f"Cronjob aprovações: processando {len(tenant_ids)} tenants")

        results = []
        for tenant_id in tenant_ids:
            try:
                triggers = OperacionalNotificationTriggers(db, tenant_id)
                result = triggers.check_pending_approvals()
                results.append({"tenant_id": str(tenant_id), **result})
            except Exception as e:
                logger.error(f"Cronjob aprovações falhou para tenant {tenant_id}: {e}")
                results.append({"tenant_id": str(tenant_id), "success": False, "error": str(e)})

        logger.info(f"Cronjob aprovações concluído: {len(results)} tenants processados")
    finally:
        db.close()
