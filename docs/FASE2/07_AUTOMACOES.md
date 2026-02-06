# AUTOMACOES DO SISTEMA
## ERP Conecta Mais - Fase 2

**Versao:** 1.0
**Data:** Janeiro 2026
**Executor:** Claude Opus 4.5

---

## INDICE

1. [Visao Geral](#1-visao-geral)
2. [Jobs Agendados](#2-jobs-agendados)
3. [Triggers de Evento](#3-triggers-de-evento)
4. [Workflows Automaticos](#4-workflows-automaticos)
5. [Notificacoes Automaticas](#5-notificacoes-automaticas)
6. [Integracao Continua](#6-integracao-continua)
7. [Monitoramento e Alertas](#7-monitoramento-e-alertas)
8. [Backup e Recuperacao](#8-backup-e-recuperacao)

---

## 1. VISAO GERAL

### 1.1 Arquitetura de Automacoes

```
SISTEMA DE AUTOMACOES
=====================

                    ┌─────────────────┐
                    │   SCHEDULER     │
                    │   (Celery Beat) │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  JOBS CRON      │ │  TRIGGERS       │ │  WORKFLOWS      │
│                 │ │                 │ │                 │
│ - Faturamento   │ │ - Evento DB     │ │ - Aprovacao     │
│ - Cobranca      │ │ - Webhook       │ │ - Onboarding    │
│ - Relatorios    │ │ - API Call      │ │ - Cobranca      │
│ - Backups       │ │ - Schedule      │ │ - Notificacoes  │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  CELERY WORKER  │
                    │   (Redis Queue) │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   DATABASE      │ │   EXTERNAL      │ │  NOTIFICATIONS  │
│                 │ │   SERVICES      │ │                 │
│ - PostgreSQL    │ │ - Open Banking  │ │ - Email         │
│ - Redis         │ │ - WhatsApp      │ │ - SMS           │
│ - S3            │ │ - NF-e          │ │ - Push          │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 1.2 Stack de Automacoes

```python
# Tecnologias utilizadas
AUTOMATION_STACK = {
    "task_queue": "Celery 5.3+",
    "broker": "Redis 7",
    "scheduler": "Celery Beat",
    "monitoring": "Flower + Prometheus",
    "storage": "PostgreSQL + S3",
    "notifications": "Firebase + SendGrid + Twilio",
}
```

### 1.3 Configuracao Base

```python
# core/celery/config.py
"""
Configuracao do Celery para automacoes.

Define filas, schedules e retry policies.
"""

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

# Instancia Celery
celery_app = Celery(
    "erp_conecta_mais",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

# Configuracoes
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="America/Sao_Paulo",
    enable_utc=True,

    # Task settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hora max
    task_soft_time_limit=3300,  # Warning em 55 min
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Retry policy
    task_default_retry_delay=60,  # 1 minuto
    task_max_retries=3,

    # Result backend
    result_expires=86400,  # 24 horas

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,

    # Rate limiting
    task_annotations={
        "tasks.send_email": {"rate_limit": "30/m"},
        "tasks.send_whatsapp": {"rate_limit": "60/m"},
        "tasks.call_external_api": {"rate_limit": "100/m"},
    },
)

# Filas
celery_app.conf.task_queues = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("high_priority", Exchange("high_priority"), routing_key="high"),
    Queue("low_priority", Exchange("low_priority"), routing_key="low"),
    Queue("notifications", Exchange("notifications"), routing_key="notify"),
    Queue("reports", Exchange("reports"), routing_key="report"),
    Queue("integrations", Exchange("integrations"), routing_key="integration"),
)

# Roteamento
celery_app.conf.task_routes = {
    "tasks.notifications.*": {"queue": "notifications"},
    "tasks.reports.*": {"queue": "reports"},
    "tasks.integrations.*": {"queue": "integrations"},
    "tasks.billing.*": {"queue": "high_priority"},
}
```

---

## 2. JOBS AGENDADOS

### 2.1 Schedule de Jobs

```python
# core/celery/schedules.py
"""
Schedules de jobs automaticos.

Define todos os jobs agendados do sistema.
"""

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # =====================
    # FINANCEIRO - DIARIO
    # =====================
    "gerar-boletos-diario": {
        "task": "tasks.billing.generate_daily_invoices",
        "schedule": crontab(hour=6, minute=0),
        "options": {"queue": "high_priority"},
    },
    "processar-retorno-bancario": {
        "task": "tasks.billing.process_bank_returns",
        "schedule": crontab(hour="*/2", minute=30),  # A cada 2h
        "options": {"queue": "high_priority"},
    },
    "enviar-cobranca-automatica": {
        "task": "tasks.billing.send_collection_reminders",
        "schedule": crontab(hour=9, minute=0),
        "options": {"queue": "notifications"},
    },
    "atualizar-inadimplencia": {
        "task": "tasks.billing.update_delinquency_status",
        "schedule": crontab(hour=7, minute=0),
        "options": {"queue": "default"},
    },

    # =====================
    # FINANCEIRO - MENSAL
    # =====================
    "gerar-faturamento-mensal": {
        "task": "tasks.billing.generate_monthly_billing",
        "schedule": crontab(day_of_month=1, hour=2, minute=0),
        "options": {"queue": "high_priority"},
    },
    "calcular-comissoes": {
        "task": "tasks.hr.calculate_commissions",
        "schedule": crontab(day_of_month=5, hour=6, minute=0),
        "options": {"queue": "default"},
    },
    "fechar-folha-pagamento": {
        "task": "tasks.hr.close_payroll",
        "schedule": crontab(day_of_month=25, hour=18, minute=0),
        "options": {"queue": "high_priority"},
    },

    # =====================
    # RH - DIARIO
    # =====================
    "verificar-ponto-colaboradores": {
        "task": "tasks.hr.check_attendance",
        "schedule": crontab(hour=22, minute=0),
        "options": {"queue": "default"},
    },
    "enviar-alertas-escala": {
        "task": "tasks.hr.send_schedule_alerts",
        "schedule": crontab(hour=7, minute=0),
        "options": {"queue": "notifications"},
    },
    "processar-banco-horas": {
        "task": "tasks.hr.process_time_bank",
        "schedule": crontab(hour=23, minute=30),
        "options": {"queue": "default"},
    },

    # =====================
    # OPERACIONAL - DIARIO
    # =====================
    "verificar-sla-contratos": {
        "task": "tasks.operations.check_contract_sla",
        "schedule": crontab(hour="*/4", minute=0),  # A cada 4h
        "options": {"queue": "default"},
    },
    "gerar-ordens-servico-preventiva": {
        "task": "tasks.operations.generate_preventive_os",
        "schedule": crontab(hour=5, minute=0),
        "options": {"queue": "default"},
    },
    "atualizar-status-contratos": {
        "task": "tasks.operations.update_contract_status",
        "schedule": crontab(hour=0, minute=30),
        "options": {"queue": "default"},
    },

    # =====================
    # CRM - DIARIO
    # =====================
    "atualizar-score-leads": {
        "task": "tasks.crm.update_lead_scores",
        "schedule": crontab(hour=4, minute=0),
        "options": {"queue": "default"},
    },
    "enviar-follow-up-automatico": {
        "task": "tasks.crm.send_auto_follow_ups",
        "schedule": crontab(hour=9, minute=30),
        "options": {"queue": "notifications"},
    },
    "verificar-propostas-expiradas": {
        "task": "tasks.crm.check_expired_proposals",
        "schedule": crontab(hour=8, minute=0),
        "options": {"queue": "default"},
    },

    # =====================
    # BI/ANALYTICS - DIARIO
    # =====================
    "calcular-kpis-diarios": {
        "task": "tasks.analytics.calculate_daily_kpis",
        "schedule": crontab(hour=1, minute=0),
        "options": {"queue": "reports"},
    },
    "gerar-relatorios-automaticos": {
        "task": "tasks.analytics.generate_scheduled_reports",
        "schedule": crontab(hour=6, minute=30),
        "options": {"queue": "reports"},
    },
    "atualizar-dashboards-cache": {
        "task": "tasks.analytics.refresh_dashboard_cache",
        "schedule": crontab(minute="*/15"),  # A cada 15 min
        "options": {"queue": "low_priority"},
    },

    # =====================
    # INTEGRACOES
    # =====================
    "sincronizar-open-banking": {
        "task": "tasks.integrations.sync_open_banking",
        "schedule": crontab(hour="*/6", minute=0),  # A cada 6h
        "options": {"queue": "integrations"},
    },
    "verificar-webhooks-pendentes": {
        "task": "tasks.integrations.retry_failed_webhooks",
        "schedule": crontab(minute="*/30"),  # A cada 30 min
        "options": {"queue": "integrations"},
    },
    "sincronizar-esocial": {
        "task": "tasks.integrations.sync_esocial",
        "schedule": crontab(hour=3, minute=0),
        "options": {"queue": "integrations"},
    },

    # =====================
    # COMPLIANCE
    # =====================
    "executar-retencao-dados": {
        "task": "tasks.compliance.execute_retention_policies",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),  # Domingo 2h
        "options": {"queue": "low_priority"},
    },
    "gerar-relatorio-auditoria": {
        "task": "tasks.compliance.generate_audit_report",
        "schedule": crontab(hour=5, minute=0, day_of_month=1),  # Dia 1
        "options": {"queue": "reports"},
    },
    "verificar-consentimentos-expirados": {
        "task": "tasks.compliance.check_expired_consents",
        "schedule": crontab(hour=4, minute=0),
        "options": {"queue": "default"},
    },

    # =====================
    # SISTEMA
    # =====================
    "backup-database": {
        "task": "tasks.system.backup_database",
        "schedule": crontab(hour=3, minute=0),
        "options": {"queue": "low_priority"},
    },
    "limpar-arquivos-temporarios": {
        "task": "tasks.system.cleanup_temp_files",
        "schedule": crontab(hour=4, minute=30),
        "options": {"queue": "low_priority"},
    },
    "verificar-saude-sistema": {
        "task": "tasks.system.health_check",
        "schedule": crontab(minute="*/5"),  # A cada 5 min
        "options": {"queue": "high_priority"},
    },
    "atualizar-cache-global": {
        "task": "tasks.system.refresh_global_cache",
        "schedule": crontab(hour="*/1", minute=0),  # A cada hora
        "options": {"queue": "default"},
    },
}
```

### 2.2 Implementacao de Tasks

```python
# tasks/billing/invoices.py
"""
Tasks de faturamento automatico.

Gera boletos e processa cobrancas.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List
from uuid import UUID

from celery import shared_task
from sqlalchemy.orm import Session

from core.celery.config import celery_app
from core.database import SessionLocal
from core.logging import logger
from modules.financial.services.billing_service import BillingService
from modules.financial.services.collection_service import CollectionService


@celery_app.task(
    bind=True,
    name="tasks.billing.generate_daily_invoices",
    max_retries=3,
    default_retry_delay=300,
)
def generate_daily_invoices(self) -> dict:
    """
    Gera boletos para faturas do dia.

    Returns:
        Estatisticas de geracao
    """
    logger.info("Iniciando geracao de boletos diarios")

    db = SessionLocal()
    try:
        service = BillingService(db)

        # Buscar faturas para faturar
        invoices = service.get_invoices_for_billing()

        generated = 0
        errors = []

        for invoice in invoices:
            try:
                service.generate_boleto(invoice.id)
                generated += 1
            except Exception as e:
                logger.error(
                    "Erro ao gerar boleto",
                    invoice_id=str(invoice.id),
                    error=str(e),
                )
                errors.append({
                    "invoice_id": str(invoice.id),
                    "error": str(e),
                })

        result = {
            "date": datetime.utcnow().isoformat(),
            "total_invoices": len(invoices),
            "generated": generated,
            "errors": len(errors),
            "error_details": errors,
        }

        logger.info(
            "Geracao de boletos concluida",
            generated=generated,
            errors=len(errors),
        )

        return result

    except Exception as e:
        logger.error("Erro na task de geracao de boletos", error=str(e))
        self.retry(exc=e)

    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="tasks.billing.process_bank_returns",
    max_retries=3,
    default_retry_delay=600,
)
def process_bank_returns(self) -> dict:
    """
    Processa arquivos de retorno bancario.

    Returns:
        Estatisticas de processamento
    """
    logger.info("Iniciando processamento de retornos bancarios")

    db = SessionLocal()
    try:
        service = BillingService(db)

        # Processar retornos pendentes
        result = service.process_pending_returns()

        logger.info(
            "Processamento de retornos concluido",
            processed=result["processed"],
            payments=result["payments_confirmed"],
        )

        return result

    except Exception as e:
        logger.error("Erro no processamento de retornos", error=str(e))
        self.retry(exc=e)

    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="tasks.billing.send_collection_reminders",
    max_retries=2,
    default_retry_delay=300,
)
def send_collection_reminders(self) -> dict:
    """
    Envia lembretes de cobranca.

    Returns:
        Estatisticas de envio
    """
    logger.info("Iniciando envio de lembretes de cobranca")

    db = SessionLocal()
    try:
        service = CollectionService(db)

        # Lembretes de vencimento proximo (3 dias)
        upcoming = service.send_upcoming_reminders(days_ahead=3)

        # Lembretes de atraso
        overdue = service.send_overdue_reminders()

        result = {
            "date": datetime.utcnow().isoformat(),
            "upcoming_sent": upcoming["sent"],
            "overdue_sent": overdue["sent"],
            "errors": upcoming["errors"] + overdue["errors"],
        }

        logger.info(
            "Lembretes de cobranca enviados",
            upcoming=upcoming["sent"],
            overdue=overdue["sent"],
        )

        return result

    except Exception as e:
        logger.error("Erro no envio de lembretes", error=str(e))
        self.retry(exc=e)

    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="tasks.billing.generate_monthly_billing",
    max_retries=5,
    default_retry_delay=900,
)
def generate_monthly_billing(self) -> dict:
    """
    Gera faturamento mensal de contratos.

    Executado no dia 1 de cada mes.

    Returns:
        Estatisticas do faturamento
    """
    logger.info("Iniciando faturamento mensal")

    db = SessionLocal()
    try:
        service = BillingService(db)

        # Periodo de referencia (mes anterior)
        today = datetime.utcnow()
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)

        # Gerar faturas para todos os contratos ativos
        result = service.generate_monthly_invoices(
            start_date=first_day_last_month,
            end_date=last_day_last_month,
        )

        logger.info(
            "Faturamento mensal concluido",
            contracts=result["contracts_billed"],
            total_value=str(result["total_value"]),
        )

        return result

    except Exception as e:
        logger.error("Erro no faturamento mensal", error=str(e))
        self.retry(exc=e)

    finally:
        db.close()
```

### 2.3 Tasks de RH

```python
# tasks/hr/attendance.py
"""
Tasks de controle de ponto.

Verifica presenca e processa banco de horas.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict

from celery import shared_task

from core.celery.config import celery_app
from core.database import SessionLocal
from core.logging import logger
from modules.hr.services.attendance_service import AttendanceService
from modules.hr.services.timebank_service import TimeBankService


@celery_app.task(
    bind=True,
    name="tasks.hr.check_attendance",
    max_retries=2,
)
def check_attendance(self) -> dict:
    """
    Verifica presenca dos colaboradores.

    Identifica faltas e atrasos nao justificados.

    Returns:
        Estatisticas de presenca
    """
    logger.info("Verificando presenca do dia")

    db = SessionLocal()
    try:
        service = AttendanceService(db)
        today = date.today()

        # Verificar colaboradores que deveriam ter trabalhado
        result = service.check_daily_attendance(today)

        # Enviar alertas para gestores
        if result["absences"] > 0:
            from tasks.notifications.email import send_absence_alert
            send_absence_alert.delay(
                date=today.isoformat(),
                absences=result["absence_details"],
            )

        logger.info(
            "Verificacao de presenca concluida",
            expected=result["expected"],
            present=result["present"],
            absences=result["absences"],
            late=result["late"],
        )

        return result

    except Exception as e:
        logger.error("Erro na verificacao de presenca", error=str(e))
        self.retry(exc=e)

    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="tasks.hr.process_time_bank",
    max_retries=3,
)
def process_time_bank(self) -> dict:
    """
    Processa banco de horas do dia.

    Calcula horas extras e debitos.

    Returns:
        Estatisticas do processamento
    """
    logger.info("Processando banco de horas")

    db = SessionLocal()
    try:
        service = TimeBankService(db)
        today = date.today()

        result = service.process_daily_time_bank(today)

        logger.info(
            "Banco de horas processado",
            employees=result["employees_processed"],
            total_credit=str(result["total_credit_hours"]),
            total_debit=str(result["total_debit_hours"]),
        )

        return result

    except Exception as e:
        logger.error("Erro no processamento do banco de horas", error=str(e))
        self.retry(exc=e)

    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="tasks.hr.send_schedule_alerts",
    max_retries=2,
)
def send_schedule_alerts(self) -> dict:
    """
    Envia alertas de escala para colaboradores.

    Notifica sobre turnos do dia e alteracoes.

    Returns:
        Estatisticas de envio
    """
    logger.info("Enviando alertas de escala")

    db = SessionLocal()
    try:
        service = AttendanceService(db)
        today = date.today()

        # Alertas de turno do dia
        daily_alerts = service.send_daily_schedule_alerts(today)

        # Alertas de alteracoes pendentes
        change_alerts = service.send_schedule_change_alerts()

        result = {
            "date": today.isoformat(),
            "daily_alerts_sent": daily_alerts["sent"],
            "change_alerts_sent": change_alerts["sent"],
            "errors": daily_alerts["errors"] + change_alerts["errors"],
        }

        logger.info(
            "Alertas de escala enviados",
            daily=daily_alerts["sent"],
            changes=change_alerts["sent"],
        )

        return result

    except Exception as e:
        logger.error("Erro no envio de alertas de escala", error=str(e))
        self.retry(exc=e)

    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="tasks.hr.calculate_commissions",
)
def calculate_commissions(self) -> dict:
    """
    Calcula comissoes do mes anterior.

    Executado no dia 5 de cada mes.

    Returns:
        Estatisticas de comissoes
    """
    logger.info("Calculando comissoes")

    db = SessionLocal()
    try:
        from modules.hr.services.commission_service import CommissionService
        service = CommissionService(db)

        # Mes de referencia
        today = datetime.utcnow()
        reference_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)

        result = service.calculate_monthly_commissions(
            month=reference_month.month,
            year=reference_month.year,
        )

        logger.info(
            "Comissoes calculadas",
            employees=result["employees"],
            total_value=str(result["total_commission"]),
        )

        return result

    except Exception as e:
        logger.error("Erro no calculo de comissoes", error=str(e))
        raise

    finally:
        db.close()
```

---

## 3. TRIGGERS DE EVENTO

### 3.1 Event Handlers

```python
# core/events/handlers.py
"""
Handlers de eventos do sistema.

Processa eventos de dominio e dispara acoes automaticas.
"""

from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio

from core.logging import logger


class EventType(str, Enum):
    """Tipos de eventos do sistema."""

    # Financeiro
    INVOICE_CREATED = "invoice.created"
    INVOICE_PAID = "invoice.paid"
    INVOICE_OVERDUE = "invoice.overdue"
    PAYMENT_RECEIVED = "payment.received"
    PAYMENT_FAILED = "payment.failed"

    # CRM
    LEAD_CREATED = "lead.created"
    LEAD_CONVERTED = "lead.converted"
    OPPORTUNITY_CREATED = "opportunity.created"
    OPPORTUNITY_WON = "opportunity.won"
    OPPORTUNITY_LOST = "opportunity.lost"
    PROPOSAL_SENT = "proposal.sent"
    PROPOSAL_ACCEPTED = "proposal.accepted"
    PROPOSAL_REJECTED = "proposal.rejected"

    # RH
    EMPLOYEE_HIRED = "employee.hired"
    EMPLOYEE_TERMINATED = "employee.terminated"
    CLOCK_IN = "attendance.clock_in"
    CLOCK_OUT = "attendance.clock_out"
    ABSENCE_DETECTED = "attendance.absence"
    VACATION_REQUESTED = "vacation.requested"
    VACATION_APPROVED = "vacation.approved"

    # Operacional
    CONTRACT_CREATED = "contract.created"
    CONTRACT_ACTIVATED = "contract.activated"
    CONTRACT_EXPIRED = "contract.expired"
    SERVICE_ORDER_CREATED = "service_order.created"
    SERVICE_ORDER_COMPLETED = "service_order.completed"
    SLA_BREACH = "sla.breach"

    # Sistema
    USER_CREATED = "user.created"
    USER_LOGGED_IN = "user.logged_in"
    USER_LOGGED_OUT = "user.logged_out"
    PASSWORD_CHANGED = "user.password_changed"
    SECURITY_ALERT = "security.alert"


@dataclass
class Event:
    """Representa um evento do sistema."""

    type: EventType
    data: Dict[str, Any]
    timestamp: datetime = None
    user_id: str = None
    correlation_id: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class EventBus:
    """
    Barramento de eventos.

    Gerencia publicacao e subscricao de eventos.
    """

    _instance = None
    _handlers: Dict[EventType, List[Callable]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._handlers = {}
        return cls._instance

    def subscribe(
        self,
        event_type: EventType,
        handler: Callable,
    ) -> None:
        """
        Registra handler para tipo de evento.

        Args:
            event_type: Tipo de evento
            handler: Funcao handler
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

        logger.debug(
            "Handler registrado",
            event_type=event_type.value,
            handler=handler.__name__,
        )

    def publish(self, event: Event) -> None:
        """
        Publica evento para handlers.

        Args:
            event: Evento a publicar
        """
        handlers = self._handlers.get(event.type, [])

        logger.info(
            "Evento publicado",
            event_type=event.type.value,
            handlers_count=len(handlers),
        )

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(event))
                else:
                    handler(event)
            except Exception as e:
                logger.error(
                    "Erro ao executar handler",
                    event_type=event.type.value,
                    handler=handler.__name__,
                    error=str(e),
                )

    def publish_async(self, event: Event) -> None:
        """
        Publica evento de forma assincrona via Celery.

        Args:
            event: Evento a publicar
        """
        from tasks.events.process import process_event
        process_event.delay(
            event_type=event.type.value,
            event_data=event.data,
            user_id=event.user_id,
            correlation_id=event.correlation_id,
        )


# Instancia global
event_bus = EventBus()
```

### 3.2 Handlers de Eventos

```python
# core/events/billing_handlers.py
"""
Handlers de eventos financeiros.

Processa eventos relacionados a faturamento e pagamentos.
"""

from core.events.handlers import Event, EventType, event_bus
from core.logging import logger


def on_invoice_created(event: Event) -> None:
    """
    Handler para criacao de fatura.

    Args:
        event: Evento de fatura criada
    """
    invoice_id = event.data.get("invoice_id")
    customer_id = event.data.get("customer_id")
    amount = event.data.get("amount")

    logger.info(
        "Processando criacao de fatura",
        invoice_id=invoice_id,
    )

    # Enviar notificacao ao cliente
    from tasks.notifications.email import send_invoice_notification
    send_invoice_notification.delay(
        invoice_id=invoice_id,
        customer_id=customer_id,
    )

    # Agendar lembrete de vencimento
    from tasks.billing.reminders import schedule_due_date_reminder
    schedule_due_date_reminder.delay(invoice_id=invoice_id)


def on_invoice_paid(event: Event) -> None:
    """
    Handler para pagamento de fatura.

    Args:
        event: Evento de pagamento
    """
    invoice_id = event.data.get("invoice_id")
    payment_id = event.data.get("payment_id")
    amount = event.data.get("amount")

    logger.info(
        "Processando pagamento de fatura",
        invoice_id=invoice_id,
        payment_id=payment_id,
    )

    # Enviar recibo
    from tasks.notifications.email import send_payment_receipt
    send_payment_receipt.delay(
        invoice_id=invoice_id,
        payment_id=payment_id,
    )

    # Atualizar CRM se for cliente novo
    from tasks.crm.customer import update_customer_payment_status
    update_customer_payment_status.delay(
        invoice_id=invoice_id,
        status="paid",
    )

    # Cancelar lembretes de cobranca
    from tasks.billing.reminders import cancel_collection_reminders
    cancel_collection_reminders.delay(invoice_id=invoice_id)


def on_invoice_overdue(event: Event) -> None:
    """
    Handler para fatura em atraso.

    Args:
        event: Evento de atraso
    """
    invoice_id = event.data.get("invoice_id")
    days_overdue = event.data.get("days_overdue")

    logger.info(
        "Processando fatura em atraso",
        invoice_id=invoice_id,
        days_overdue=days_overdue,
    )

    # Escalar cobranca
    from tasks.billing.collection import escalate_collection
    escalate_collection.delay(
        invoice_id=invoice_id,
        days_overdue=days_overdue,
    )

    # Notificar gestor financeiro
    from tasks.notifications.internal import notify_finance_manager
    notify_finance_manager.delay(
        type="invoice_overdue",
        invoice_id=invoice_id,
        days_overdue=days_overdue,
    )


def on_payment_failed(event: Event) -> None:
    """
    Handler para falha de pagamento.

    Args:
        event: Evento de falha
    """
    payment_id = event.data.get("payment_id")
    invoice_id = event.data.get("invoice_id")
    reason = event.data.get("reason")

    logger.warning(
        "Processando falha de pagamento",
        payment_id=payment_id,
        invoice_id=invoice_id,
        reason=reason,
    )

    # Notificar cliente
    from tasks.notifications.email import send_payment_failed_notification
    send_payment_failed_notification.delay(
        invoice_id=invoice_id,
        reason=reason,
    )

    # Registrar tentativa
    from tasks.billing.collection import record_payment_attempt
    record_payment_attempt.delay(
        invoice_id=invoice_id,
        payment_id=payment_id,
        status="failed",
        reason=reason,
    )


# Registrar handlers
event_bus.subscribe(EventType.INVOICE_CREATED, on_invoice_created)
event_bus.subscribe(EventType.INVOICE_PAID, on_invoice_paid)
event_bus.subscribe(EventType.INVOICE_OVERDUE, on_invoice_overdue)
event_bus.subscribe(EventType.PAYMENT_FAILED, on_payment_failed)
```

```python
# core/events/crm_handlers.py
"""
Handlers de eventos CRM.

Processa eventos relacionados a vendas e clientes.
"""

from core.events.handlers import Event, EventType, event_bus
from core.logging import logger


def on_lead_created(event: Event) -> None:
    """
    Handler para criacao de lead.

    Args:
        event: Evento de lead criado
    """
    lead_id = event.data.get("lead_id")
    source = event.data.get("source")

    logger.info("Processando novo lead", lead_id=lead_id, source=source)

    # Calcular score inicial
    from tasks.crm.scoring import calculate_lead_score
    calculate_lead_score.delay(lead_id=lead_id)

    # Atribuir a vendedor
    from tasks.crm.assignment import auto_assign_lead
    auto_assign_lead.delay(lead_id=lead_id)

    # Enviar email de boas-vindas
    from tasks.notifications.email import send_lead_welcome
    send_lead_welcome.delay(lead_id=lead_id)


def on_opportunity_won(event: Event) -> None:
    """
    Handler para oportunidade ganha.

    Args:
        event: Evento de venda
    """
    opportunity_id = event.data.get("opportunity_id")
    seller_id = event.data.get("seller_id")
    value = event.data.get("value")

    logger.info(
        "Processando oportunidade ganha",
        opportunity_id=opportunity_id,
        value=value,
    )

    # Criar contrato
    from tasks.operations.contracts import create_contract_from_opportunity
    create_contract_from_opportunity.delay(opportunity_id=opportunity_id)

    # Registrar comissao
    from tasks.hr.commissions import register_sale_commission
    register_sale_commission.delay(
        seller_id=seller_id,
        opportunity_id=opportunity_id,
        value=value,
    )

    # Notificar equipe
    from tasks.notifications.internal import notify_sale_closed
    notify_sale_closed.delay(
        opportunity_id=opportunity_id,
        seller_id=seller_id,
    )

    # Atualizar metricas
    from tasks.analytics.metrics import update_sales_metrics
    update_sales_metrics.delay()


def on_proposal_sent(event: Event) -> None:
    """
    Handler para proposta enviada.

    Args:
        event: Evento de envio
    """
    proposal_id = event.data.get("proposal_id")
    customer_email = event.data.get("customer_email")

    logger.info("Processando proposta enviada", proposal_id=proposal_id)

    # Agendar follow-up
    from tasks.crm.follow_up import schedule_proposal_follow_up
    schedule_proposal_follow_up.delay(
        proposal_id=proposal_id,
        days_to_follow_up=3,
    )

    # Rastrear abertura
    from tasks.crm.tracking import track_proposal_view
    track_proposal_view.delay(proposal_id=proposal_id)


def on_proposal_accepted(event: Event) -> None:
    """
    Handler para proposta aceita.

    Args:
        event: Evento de aceite
    """
    proposal_id = event.data.get("proposal_id")
    opportunity_id = event.data.get("opportunity_id")

    logger.info("Processando proposta aceita", proposal_id=proposal_id)

    # Converter oportunidade
    from tasks.crm.opportunity import convert_to_won
    convert_to_won.delay(opportunity_id=opportunity_id)

    # Cancelar follow-ups
    from tasks.crm.follow_up import cancel_follow_ups
    cancel_follow_ups.delay(proposal_id=proposal_id)


# Registrar handlers
event_bus.subscribe(EventType.LEAD_CREATED, on_lead_created)
event_bus.subscribe(EventType.OPPORTUNITY_WON, on_opportunity_won)
event_bus.subscribe(EventType.PROPOSAL_SENT, on_proposal_sent)
event_bus.subscribe(EventType.PROPOSAL_ACCEPTED, on_proposal_accepted)
```

---

## 4. WORKFLOWS AUTOMATICOS

### 4.1 Engine de Workflow

```python
# core/workflow/engine.py
"""
Engine de workflows automaticos.

Gerencia execucao de workflows multi-step.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID, uuid4
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from core.database import SessionLocal
from core.logging import logger


class WorkflowStatus(str, Enum):
    """Status de execucao do workflow."""

    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(str, Enum):
    """Tipos de step."""

    ACTION = "action"
    CONDITION = "condition"
    WAIT = "wait"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"


@dataclass
class WorkflowStep:
    """Representa um step do workflow."""

    id: str
    name: str
    type: StepType
    config: Dict[str, Any]
    next_steps: List[str] = field(default_factory=list)
    on_error: Optional[str] = None


@dataclass
class WorkflowDefinition:
    """Definicao de workflow."""

    id: str
    name: str
    description: str
    trigger: str
    steps: List[WorkflowStep]
    start_step: str
    timeout_hours: int = 72


@dataclass
class WorkflowExecution:
    """Execucao de workflow."""

    id: UUID
    definition_id: str
    status: WorkflowStatus
    current_step: str
    context: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class WorkflowEngine:
    """
    Engine de execucao de workflows.

    Gerencia definicoes e execucoes de workflows.
    """

    def __init__(self, db: Session):
        """
        Inicializa engine.

        Args:
            db: Sessao do banco
        """
        self.db = db
        self._definitions: Dict[str, WorkflowDefinition] = {}
        self._step_handlers: Dict[StepType, Callable] = {}
        self._register_default_handlers()

    def register_workflow(self, definition: WorkflowDefinition) -> None:
        """
        Registra definicao de workflow.

        Args:
            definition: Definicao do workflow
        """
        self._definitions[definition.id] = definition
        logger.info(
            "Workflow registrado",
            workflow_id=definition.id,
            name=definition.name,
        )

    def start_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any],
    ) -> WorkflowExecution:
        """
        Inicia execucao de workflow.

        Args:
            workflow_id: ID do workflow
            context: Contexto inicial

        Returns:
            Execucao criada

        Raises:
            ValueError: Se workflow nao encontrado
        """
        definition = self._definitions.get(workflow_id)
        if not definition:
            raise ValueError(f"Workflow {workflow_id} nao encontrado")

        execution = WorkflowExecution(
            id=uuid4(),
            definition_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            current_step=definition.start_step,
            context=context,
            started_at=datetime.utcnow(),
        )

        # Persistir execucao
        self._save_execution(execution)

        logger.info(
            "Workflow iniciado",
            execution_id=str(execution.id),
            workflow_id=workflow_id,
        )

        # Executar primeiro step
        self._execute_step(execution)

        return execution

    def _execute_step(self, execution: WorkflowExecution) -> None:
        """
        Executa step atual do workflow.

        Args:
            execution: Execucao em andamento
        """
        definition = self._definitions[execution.definition_id]
        step = self._find_step(definition, execution.current_step)

        if not step:
            self._complete_workflow(execution, "Step nao encontrado")
            return

        logger.info(
            "Executando step",
            execution_id=str(execution.id),
            step=step.name,
            type=step.type.value,
        )

        try:
            handler = self._step_handlers.get(step.type)
            if not handler:
                raise ValueError(f"Handler nao encontrado para {step.type}")

            result = handler(step, execution)

            if result.get("wait"):
                # Step requer aguardar (aprovacao, timer, etc)
                execution.status = WorkflowStatus.WAITING
                self._save_execution(execution)
            elif result.get("next_step"):
                # Continuar para proximo step
                execution.current_step = result["next_step"]
                execution.context.update(result.get("context", {}))
                self._save_execution(execution)
                self._execute_step(execution)
            else:
                # Workflow concluido
                self._complete_workflow(execution)

        except Exception as e:
            logger.error(
                "Erro no step do workflow",
                execution_id=str(execution.id),
                step=step.name,
                error=str(e),
            )
            if step.on_error:
                execution.current_step = step.on_error
                self._execute_step(execution)
            else:
                self._fail_workflow(execution, str(e))

    def _register_default_handlers(self) -> None:
        """Registra handlers padrao."""
        self._step_handlers[StepType.ACTION] = self._handle_action
        self._step_handlers[StepType.CONDITION] = self._handle_condition
        self._step_handlers[StepType.WAIT] = self._handle_wait
        self._step_handlers[StepType.APPROVAL] = self._handle_approval
        self._step_handlers[StepType.NOTIFICATION] = self._handle_notification
        self._step_handlers[StepType.INTEGRATION] = self._handle_integration

    def _handle_action(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
    ) -> Dict[str, Any]:
        """Handler para steps de acao."""
        action = step.config.get("action")
        params = step.config.get("params", {})

        # Executar acao configurada
        # ...

        return {
            "next_step": step.next_steps[0] if step.next_steps else None,
        }

    def _handle_condition(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
    ) -> Dict[str, Any]:
        """Handler para steps condicionais."""
        condition = step.config.get("condition")
        true_step = step.config.get("true_step")
        false_step = step.config.get("false_step")

        # Avaliar condicao
        result = self._evaluate_condition(condition, execution.context)

        return {
            "next_step": true_step if result else false_step,
        }

    def _handle_wait(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
    ) -> Dict[str, Any]:
        """Handler para steps de espera."""
        wait_type = step.config.get("wait_type")  # duration, until_date, event

        if wait_type == "duration":
            hours = step.config.get("hours", 24)
            # Agendar retomada
            from tasks.workflow.resume import schedule_workflow_resume
            schedule_workflow_resume.apply_async(
                args=[str(execution.id)],
                countdown=hours * 3600,
            )
            return {"wait": True}

        return {"next_step": step.next_steps[0] if step.next_steps else None}

    def _handle_approval(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
    ) -> Dict[str, Any]:
        """Handler para steps de aprovacao."""
        approvers = step.config.get("approvers", [])
        approval_type = step.config.get("type", "any")  # any, all

        # Criar solicitacao de aprovacao
        from tasks.workflow.approval import create_approval_request
        create_approval_request.delay(
            execution_id=str(execution.id),
            step_id=step.id,
            approvers=approvers,
            approval_type=approval_type,
        )

        return {"wait": True}

    def _handle_notification(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
    ) -> Dict[str, Any]:
        """Handler para steps de notificacao."""
        channel = step.config.get("channel", "email")
        template = step.config.get("template")
        recipients = step.config.get("recipients", [])

        # Enviar notificacao
        from tasks.notifications.send import send_notification
        send_notification.delay(
            channel=channel,
            template=template,
            recipients=recipients,
            context=execution.context,
        )

        return {"next_step": step.next_steps[0] if step.next_steps else None}

    def _handle_integration(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
    ) -> Dict[str, Any]:
        """Handler para steps de integracao."""
        integration = step.config.get("integration")
        action = step.config.get("action")
        params = step.config.get("params", {})

        # Executar integracao
        from tasks.integrations.execute import execute_integration
        result = execute_integration.delay(
            integration=integration,
            action=action,
            params=params,
            context=execution.context,
        )

        return {
            "next_step": step.next_steps[0] if step.next_steps else None,
            "context": {"integration_result": result.get()},
        }

    def _find_step(
        self,
        definition: WorkflowDefinition,
        step_id: str,
    ) -> Optional[WorkflowStep]:
        """Encontra step por ID."""
        for step in definition.steps:
            if step.id == step_id:
                return step
        return None

    def _evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any],
    ) -> bool:
        """Avalia condicao com contexto."""
        # Implementar avaliacao segura
        return True

    def _complete_workflow(
        self,
        execution: WorkflowExecution,
        error: Optional[str] = None,
    ) -> None:
        """Marca workflow como concluido."""
        execution.status = WorkflowStatus.COMPLETED
        execution.completed_at = datetime.utcnow()
        if error:
            execution.error = error
        self._save_execution(execution)

        logger.info(
            "Workflow concluido",
            execution_id=str(execution.id),
        )

    def _fail_workflow(
        self,
        execution: WorkflowExecution,
        error: str,
    ) -> None:
        """Marca workflow como falho."""
        execution.status = WorkflowStatus.FAILED
        execution.completed_at = datetime.utcnow()
        execution.error = error
        self._save_execution(execution)

        logger.error(
            "Workflow falhou",
            execution_id=str(execution.id),
            error=error,
        )

    def _save_execution(self, execution: WorkflowExecution) -> None:
        """Persiste execucao no banco."""
        # Implementar persistencia
        pass
```

### 4.2 Workflows Pre-definidos

```python
# workflows/definitions/onboarding.py
"""
Workflow de onboarding de cliente.

Automatiza processo de ativacao de novo cliente.
"""

from core.workflow.engine import (
    StepType,
    WorkflowDefinition,
    WorkflowStep,
)

ONBOARDING_WORKFLOW = WorkflowDefinition(
    id="customer_onboarding",
    name="Onboarding de Cliente",
    description="Processo de ativacao de novo cliente",
    trigger="contract.activated",
    timeout_hours=168,  # 7 dias
    start_step="welcome",
    steps=[
        WorkflowStep(
            id="welcome",
            name="Enviar boas-vindas",
            type=StepType.NOTIFICATION,
            config={
                "channel": "email",
                "template": "customer_welcome",
                "recipients": ["{{ customer.email }}"],
            },
            next_steps=["create_access"],
        ),
        WorkflowStep(
            id="create_access",
            name="Criar acessos",
            type=StepType.ACTION,
            config={
                "action": "create_customer_portal_access",
                "params": {
                    "customer_id": "{{ customer.id }}",
                    "contract_id": "{{ contract.id }}",
                },
            },
            next_steps=["send_credentials"],
        ),
        WorkflowStep(
            id="send_credentials",
            name="Enviar credenciais",
            type=StepType.NOTIFICATION,
            config={
                "channel": "email",
                "template": "portal_credentials",
                "recipients": ["{{ customer.email }}"],
            },
            next_steps=["schedule_kickoff"],
        ),
        WorkflowStep(
            id="schedule_kickoff",
            name="Agendar kickoff",
            type=StepType.ACTION,
            config={
                "action": "schedule_meeting",
                "params": {
                    "type": "kickoff",
                    "participants": [
                        "{{ customer.email }}",
                        "{{ account_manager.email }}",
                    ],
                    "duration_minutes": 60,
                },
            },
            next_steps=["wait_kickoff"],
        ),
        WorkflowStep(
            id="wait_kickoff",
            name="Aguardar kickoff",
            type=StepType.WAIT,
            config={
                "wait_type": "event",
                "event": "meeting.completed",
                "timeout_hours": 72,
            },
            next_steps=["setup_services"],
            on_error="kickoff_reminder",
        ),
        WorkflowStep(
            id="kickoff_reminder",
            name="Lembrete de kickoff",
            type=StepType.NOTIFICATION,
            config={
                "channel": "email",
                "template": "kickoff_reminder",
                "recipients": ["{{ customer.email }}"],
            },
            next_steps=["wait_kickoff"],
        ),
        WorkflowStep(
            id="setup_services",
            name="Configurar servicos",
            type=StepType.ACTION,
            config={
                "action": "setup_contracted_services",
                "params": {
                    "contract_id": "{{ contract.id }}",
                },
            },
            next_steps=["training_check"],
        ),
        WorkflowStep(
            id="training_check",
            name="Verificar necessidade de treinamento",
            type=StepType.CONDITION,
            config={
                "condition": "contract.requires_training == true",
                "true_step": "schedule_training",
                "false_step": "send_guide",
            },
        ),
        WorkflowStep(
            id="schedule_training",
            name="Agendar treinamento",
            type=StepType.ACTION,
            config={
                "action": "schedule_training",
                "params": {
                    "contract_id": "{{ contract.id }}",
                    "training_type": "{{ contract.training_type }}",
                },
            },
            next_steps=["send_guide"],
        ),
        WorkflowStep(
            id="send_guide",
            name="Enviar guia de uso",
            type=StepType.NOTIFICATION,
            config={
                "channel": "email",
                "template": "usage_guide",
                "recipients": ["{{ customer.email }}"],
            },
            next_steps=["satisfaction_survey"],
        ),
        WorkflowStep(
            id="satisfaction_survey",
            name="Pesquisa de satisfacao",
            type=StepType.WAIT,
            config={
                "wait_type": "duration",
                "hours": 168,  # 7 dias
            },
            next_steps=["send_survey"],
        ),
        WorkflowStep(
            id="send_survey",
            name="Enviar pesquisa NPS",
            type=StepType.NOTIFICATION,
            config={
                "channel": "email",
                "template": "nps_survey",
                "recipients": ["{{ customer.email }}"],
            },
            next_steps=[],  # Fim do workflow
        ),
    ],
)
```

---

## 5. NOTIFICACOES AUTOMATICAS

### 5.1 Servico de Notificacoes

```python
# tasks/notifications/service.py
"""
Servico de envio de notificacoes.

Gerencia envio multicanal de notificacoes.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from core.celery.config import celery_app
from core.logging import logger


class NotificationChannel(str, Enum):
    """Canais de notificacao."""

    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationPriority(str, Enum):
    """Prioridade de notificacao."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@celery_app.task(
    bind=True,
    name="tasks.notifications.send",
    max_retries=3,
    default_retry_delay=60,
)
def send_notification(
    self,
    channel: str,
    template: str,
    recipients: List[str],
    context: Dict[str, Any],
    priority: str = "normal",
    scheduled_at: Optional[str] = None,
) -> dict:
    """
    Envia notificacao multicanal.

    Args:
        channel: Canal de envio
        template: Template da mensagem
        recipients: Lista de destinatarios
        context: Contexto para renderizacao
        priority: Prioridade
        scheduled_at: Agendamento (ISO format)

    Returns:
        Resultado do envio
    """
    logger.info(
        "Enviando notificacao",
        channel=channel,
        template=template,
        recipients_count=len(recipients),
    )

    try:
        # Renderizar template
        message = render_template(template, context)

        # Enviar por canal
        if channel == NotificationChannel.EMAIL.value:
            result = send_email(recipients, message)
        elif channel == NotificationChannel.SMS.value:
            result = send_sms(recipients, message)
        elif channel == NotificationChannel.WHATSAPP.value:
            result = send_whatsapp(recipients, message)
        elif channel == NotificationChannel.PUSH.value:
            result = send_push(recipients, message)
        elif channel == NotificationChannel.IN_APP.value:
            result = create_in_app_notification(recipients, message)
        else:
            raise ValueError(f"Canal desconhecido: {channel}")

        logger.info(
            "Notificacao enviada",
            channel=channel,
            sent=result["sent"],
            failed=result["failed"],
        )

        return result

    except Exception as e:
        logger.error(
            "Erro ao enviar notificacao",
            channel=channel,
            error=str(e),
        )
        self.retry(exc=e)


def render_template(template: str, context: Dict[str, Any]) -> Dict[str, str]:
    """
    Renderiza template de notificacao.

    Args:
        template: Nome do template
        context: Contexto de dados

    Returns:
        Mensagem renderizada (subject, body, etc)
    """
    from jinja2 import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader("templates/notifications"),
    )

    template_obj = env.get_template(f"{template}.html")
    body = template_obj.render(**context)

    # Carregar subject do template
    subject_template = env.get_template(f"{template}_subject.txt")
    subject = subject_template.render(**context).strip()

    return {
        "subject": subject,
        "body": body,
    }


def send_email(recipients: List[str], message: Dict[str, str]) -> dict:
    """Envia email via SendGrid."""
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    sg = SendGridAPIClient()
    sent = 0
    failed = 0
    errors = []

    for recipient in recipients:
        try:
            mail = Mail(
                from_email="noreply@conectamais.com.br",
                to_emails=recipient,
                subject=message["subject"],
                html_content=message["body"],
            )
            sg.send(mail)
            sent += 1
        except Exception as e:
            failed += 1
            errors.append({"recipient": recipient, "error": str(e)})

    return {"sent": sent, "failed": failed, "errors": errors}


def send_sms(recipients: List[str], message: Dict[str, str]) -> dict:
    """Envia SMS via Twilio."""
    from twilio.rest import Client

    client = Client()
    sent = 0
    failed = 0
    errors = []

    body = message.get("sms_body", message["body"][:160])

    for recipient in recipients:
        try:
            client.messages.create(
                body=body,
                from_="+551199999999",
                to=recipient,
            )
            sent += 1
        except Exception as e:
            failed += 1
            errors.append({"recipient": recipient, "error": str(e)})

    return {"sent": sent, "failed": failed, "errors": errors}


def send_whatsapp(recipients: List[str], message: Dict[str, str]) -> dict:
    """Envia WhatsApp via API Business."""
    from modules.integrations.services.whatsapp_service import WhatsAppService

    service = WhatsAppService()
    sent = 0
    failed = 0
    errors = []

    for recipient in recipients:
        try:
            service.send_template_message(
                phone=recipient,
                template=message.get("whatsapp_template", "generic"),
                params=message.get("whatsapp_params", []),
            )
            sent += 1
        except Exception as e:
            failed += 1
            errors.append({"recipient": recipient, "error": str(e)})

    return {"sent": sent, "failed": failed, "errors": errors}


def send_push(recipients: List[str], message: Dict[str, str]) -> dict:
    """Envia push notification via Firebase."""
    from firebase_admin import messaging

    sent = 0
    failed = 0
    errors = []

    for recipient in recipients:
        try:
            notification = messaging.Message(
                notification=messaging.Notification(
                    title=message["subject"],
                    body=message.get("push_body", message["body"][:200]),
                ),
                token=recipient,
            )
            messaging.send(notification)
            sent += 1
        except Exception as e:
            failed += 1
            errors.append({"recipient": recipient, "error": str(e)})

    return {"sent": sent, "failed": failed, "errors": errors}


def create_in_app_notification(
    recipients: List[str],
    message: Dict[str, str],
) -> dict:
    """Cria notificacao in-app no banco."""
    from core.database import SessionLocal
    from modules.notifications.models import InAppNotification

    db = SessionLocal()
    sent = 0

    try:
        for recipient in recipients:
            notification = InAppNotification(
                user_id=recipient,
                title=message["subject"],
                body=message.get("in_app_body", message["body"]),
                type=message.get("type", "info"),
                action_url=message.get("action_url"),
            )
            db.add(notification)
            sent += 1

        db.commit()
    finally:
        db.close()

    return {"sent": sent, "failed": 0, "errors": []}
```

---

## 6. INTEGRACAO CONTINUA

### 6.1 Pipeline CI/CD

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.12"
  NODE_VERSION: "20"

jobs:
  # ==================
  # BACKEND TESTS
  # ==================
  backend-test:
    name: Backend Tests
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          cd backend
          pylint --rcfile=.pylintrc modules/ core/ --fail-under=99

      - name: Run type checking
        run: |
          cd backend
          mypy modules/ core/ --ignore-missing-imports

      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest tests/ -v --cov=modules --cov=core --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
          fail_ci_if_error: true

  # ==================
  # FRONTEND TESTS
  # ==================
  frontend-test:
    name: Frontend Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run linting
        run: |
          cd frontend
          npm run lint

      - name: Run type checking
        run: |
          cd frontend
          npm run type-check

      - name: Run tests
        run: |
          cd frontend
          npm run test -- --coverage

      - name: Build
        run: |
          cd frontend
          npm run build

  # ==================
  # SECURITY SCAN
  # ==================
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          ignore-unfixed: true
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run Bandit security linter
        run: |
          pip install bandit
          cd backend
          bandit -r modules/ core/ -ll -f json -o bandit-report.json || true

  # ==================
  # DEPLOY STAGING
  # ==================
  deploy-staging:
    name: Deploy to Staging
    needs: [backend-test, frontend-test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to staging
        run: |
          echo "Deploying to staging..."
          # Implementar deploy

  # ==================
  # DEPLOY PRODUCTION
  # ==================
  deploy-production:
    name: Deploy to Production
    needs: [backend-test, frontend-test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # Implementar deploy
```

---

## 7. MONITORAMENTO E ALERTAS

### 7.1 Configuracao Prometheus

```yaml
# monitoring/prometheus/alerts.yml
groups:
  - name: erp_conecta_mais
    rules:
      # ==================
      # APLICACAO
      # ==================
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Taxa de erros alta"
          description: "Taxa de erros HTTP 5xx acima de 5% nos ultimos 5 minutos"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Latencia alta"
          description: "P95 de latencia acima de 2 segundos"

      - alert: LowAvailability
        expr: up{job="erp-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Servico indisponivel"
          description: "Backend ERP esta fora do ar"

      # ==================
      # CELERY
      # ==================
      - alert: CeleryWorkerDown
        expr: flower_workers_count < 2
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Workers Celery insuficientes"
          description: "Menos de 2 workers Celery ativos"

      - alert: CeleryQueueBacklog
        expr: celery_queue_length > 1000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Fila Celery congestionada"
          description: "Mais de 1000 tasks na fila"

      - alert: CeleryTaskFailures
        expr: rate(celery_task_failed_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Falhas em tasks Celery"
          description: "Mais de 10 falhas por minuto"

      # ==================
      # DATABASE
      # ==================
      - alert: DatabaseConnectionsHigh
        expr: pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Conexoes PostgreSQL altas"
          description: "Mais de 80 conexoes ativas"

      - alert: DatabaseReplicationLag
        expr: pg_replication_lag_seconds > 30
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Lag de replicacao alto"
          description: "Replicacao PostgreSQL com mais de 30s de atraso"

      # ==================
      # REDIS
      # ==================
      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Memoria Redis alta"
          description: "Redis usando mais de 80% da memoria"

      # ==================
      # NEGOCIO
      # ==================
      - alert: BillingFailures
        expr: sum(rate(billing_generation_errors_total[1h])) > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Falhas no faturamento"
          description: "Mais de 10 erros de faturamento na ultima hora"

      - alert: HighDelinquencyRate
        expr: delinquency_rate > 0.15
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Inadimplencia alta"
          description: "Taxa de inadimplencia acima de 15%"
```

---

## 8. BACKUP E RECUPERACAO

### 8.1 Task de Backup

```python
# tasks/system/backup.py
"""
Tasks de backup automatico.

Realiza backups de banco, arquivos e configuracoes.
"""

from datetime import datetime
import subprocess
import boto3
from pathlib import Path

from core.celery.config import celery_app
from core.logging import logger


@celery_app.task(
    bind=True,
    name="tasks.system.backup_database",
    max_retries=3,
)
def backup_database(self) -> dict:
    """
    Realiza backup do banco de dados.

    Returns:
        Informacoes do backup
    """
    logger.info("Iniciando backup do banco de dados")

    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/tmp/backup_db_{timestamp}.sql.gz"

        # Executar pg_dump
        result = subprocess.run(
            [
                "pg_dump",
                "-h", "localhost",
                "-U", "conecta_user",
                "-d", "conecta_db",
                "-F", "c",
                "-f", backup_file.replace(".gz", ""),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Comprimir
        subprocess.run(
            ["gzip", backup_file.replace(".gz", "")],
            check=True,
        )

        # Upload para S3
        s3 = boto3.client("s3")
        s3_key = f"backups/database/{timestamp}/backup.sql.gz"

        s3.upload_file(
            backup_file,
            "conecta-mais-backups",
            s3_key,
        )

        # Limpar arquivo local
        Path(backup_file).unlink()

        # Registrar backup
        size_mb = Path(backup_file).stat().st_size / (1024 * 1024) if Path(backup_file).exists() else 0

        logger.info(
            "Backup concluido",
            s3_key=s3_key,
            size_mb=round(size_mb, 2),
        )

        return {
            "status": "success",
            "timestamp": timestamp,
            "s3_key": s3_key,
            "size_mb": round(size_mb, 2),
        }

    except Exception as e:
        logger.error("Erro no backup", error=str(e))
        self.retry(exc=e)


@celery_app.task(
    bind=True,
    name="tasks.system.cleanup_temp_files",
)
def cleanup_temp_files(self) -> dict:
    """
    Limpa arquivos temporarios antigos.

    Returns:
        Estatisticas de limpeza
    """
    logger.info("Limpando arquivos temporarios")

    from datetime import timedelta
    import os

    temp_dirs = [
        "/tmp/uploads",
        "/tmp/exports",
        "/tmp/reports",
    ]

    cutoff = datetime.utcnow() - timedelta(days=7)
    deleted = 0
    freed_bytes = 0

    for temp_dir in temp_dirs:
        if not os.path.exists(temp_dir):
            continue

        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    stat = os.stat(filepath)
                    if datetime.fromtimestamp(stat.st_mtime) < cutoff:
                        freed_bytes += stat.st_size
                        os.remove(filepath)
                        deleted += 1
                except Exception as e:
                    logger.warning(f"Erro ao remover {filepath}: {e}")

    logger.info(
        "Limpeza concluida",
        deleted=deleted,
        freed_mb=round(freed_bytes / (1024 * 1024), 2),
    )

    return {
        "deleted_files": deleted,
        "freed_mb": round(freed_bytes / (1024 * 1024), 2),
    }


@celery_app.task(
    bind=True,
    name="tasks.system.health_check",
)
def health_check(self) -> dict:
    """
    Verifica saude do sistema.

    Returns:
        Status dos componentes
    """
    import redis
    import psycopg2

    status = {
        "timestamp": datetime.utcnow().isoformat(),
        "components": {},
    }

    # PostgreSQL
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="conecta_db",
            user="conecta_user",
            password="secret",
        )
        conn.close()
        status["components"]["postgresql"] = "healthy"
    except Exception as e:
        status["components"]["postgresql"] = f"unhealthy: {e}"

    # Redis
    try:
        r = redis.Redis(host="localhost", port=6379)
        r.ping()
        status["components"]["redis"] = "healthy"
    except Exception as e:
        status["components"]["redis"] = f"unhealthy: {e}"

    # Celery workers
    try:
        from celery import current_app
        inspect = current_app.control.inspect()
        active = inspect.active()
        if active:
            status["components"]["celery"] = f"healthy ({len(active)} workers)"
        else:
            status["components"]["celery"] = "unhealthy: no workers"
    except Exception as e:
        status["components"]["celery"] = f"unhealthy: {e}"

    # Verificar alertas
    unhealthy = [k for k, v in status["components"].items() if "unhealthy" in v]
    if unhealthy:
        from tasks.notifications.internal import send_health_alert
        send_health_alert.delay(
            unhealthy_components=unhealthy,
            details=status["components"],
        )

    return status
```

---

## RESUMO DE AUTOMACOES

```
AUTOMACOES DO SISTEMA
=====================

JOBS AGENDADOS (Celery Beat)
- Faturamento diario e mensal
- Cobranca automatica
- Verificacao de ponto
- Calculo de comissoes
- Sincronizacao de integracoes
- Backups automaticos
- Limpeza de arquivos
- Health checks

TRIGGERS DE EVENTO
- Invoice created/paid/overdue
- Lead created/converted
- Opportunity won/lost
- Contract activated/expired
- SLA breach
- Security alerts

WORKFLOWS AUTOMATICOS
- Onboarding de cliente
- Aprovacao de ferias
- Fluxo de cobranca
- Processo de vendas
- Renovacao de contratos

NOTIFICACOES
- Email (SendGrid)
- SMS (Twilio)
- WhatsApp Business
- Push (Firebase)
- In-App

MONITORAMENTO
- Prometheus metrics
- Alertas automaticos
- Health checks
- Performance tracking
```

---

*Automacoes do Sistema - ERP Conecta Mais Fase 2*
*"Automatizar para escalar"*
