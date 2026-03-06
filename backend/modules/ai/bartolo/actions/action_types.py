"""
Enums e tipos para o sistema de ações executivas do Bartolo.
"""

from enum import StrEnum


class ActionType(StrEnum):
    """Tipos de ações operacionais que o Bartolo pode executar."""

    # Escalas
    CREATE_SCALE = "create_scale"
    APPROVE_SCALE = "approve_scale"
    PUBLISH_SCALE = "publish_scale"

    # Alocações
    ALLOCATE_EMPLOYEE = "allocate_employee"
    TERMINATE_ALLOCATION = "terminate_allocation"
    TRANSFER_EMPLOYEE = "transfer_employee"

    # Turnos
    CREATE_SHIFT = "create_shift"
    REGISTER_CHECKIN = "register_checkin"
    REGISTER_CHECKOUT = "register_checkout"
    MARK_ABSENCE = "mark_absence"

    # Substituições
    CREATE_SUBSTITUTION = "create_substitution"

    # Ocorrências
    CREATE_OCCURRENCE = "create_occurrence"
    RESOLVE_OCCURRENCE = "resolve_occurrence"
    UPDATE_OCCURRENCE = "update_occurrence"

    # Disciplinares
    CREATE_DISCIPLINARY = "create_disciplinary"
    APPROVE_DISCIPLINARY = "approve_disciplinary"
    REJECT_DISCIPLINARY = "reject_disciplinary"

    # Rondas de Inspeção
    CREATE_ROUND = "create_round"
    START_ROUND = "start_round"
    COMPLETE_ROUND = "complete_round"

    # Diaristas
    CREATE_DIARIST = "create_diarist"
    SCHEDULE_DIARIST = "schedule_diarist"

    # Comunicados
    CREATE_ANNOUNCEMENT = "create_announcement"
    PUBLISH_ANNOUNCEMENT = "publish_announcement"

    # Notificações
    SEND_NOTIFICATION = "send_notification"

    # Banco de Horas
    APPROVE_OVERTIME = "approve_overtime"
    REQUEST_COMPENSATION = "request_compensation"
    VIEW_BALANCE = "view_balance"

    # Postos
    CREATE_POST = "create_post"
    UPDATE_POST = "update_post"
    DELETE_POST = "delete_post"
    GET_POST_STATS = "get_post_stats"

    # Escalas (avançado)
    AUTO_GENERATE_SCALE = "auto_generate_scale"
    OPTIMIZE_SCALE = "optimize_scale"
    CREATE_SCALE_TEMPLATE = "create_scale_template"
    APPLY_SCALE_TEMPLATE = "apply_scale_template"

    # Diaristas (avançado)
    EVALUATE_DIARIST = "evaluate_diarist"
    APPROVE_DIARIST_PAYMENT = "approve_diarist_payment"
    GENERATE_DIARIST_PAYMENT = "generate_diarist_payment"

    # Rondas (avançado)
    REGISTER_CHECKPOINT = "register_checkpoint"
    PAUSE_ROUND = "pause_round"
    RESUME_ROUND = "resume_round"

    # Relatórios
    GENERATE_REPORT = "generate_report"


class ActionCategory(StrEnum):
    """Categorias de ações."""

    OPERATIONAL = "operational"
    ADMINISTRATIVE = "administrative"
    NOTIFICATION = "notification"
    REPORT = "report"


class ActionStatus(StrEnum):
    """Status de uma ação."""

    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
