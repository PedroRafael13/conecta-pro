"""
Módulo de Integração Sólides - Gestão de Pessoas (RH + DP)
Sprint 33: Integration Framework

Integração bidirecional completa com Sólides via API V1/V3.

Componentes:
- SolidesConnector: Conector principal para API Sólides
- SolidesSyncService: Serviço de sincronização bidirecional
- SolidesWebhookHandler: Processador de webhooks
- ConflictResolver: Resolvedor de conflitos de sincronização

Uso:
    from modules.integrations.connectors.solides import (
        SolidesConnector,
        get_sync_service,
        SolidesWebhookHandler,
    )

    # Criar conector
    connector = SolidesConnector(credentials={"api_token": "xxx"})

    # Sincronização
    sync_service = get_sync_service(db, condominio_id)
    result = await sync_service.full_sync()

Configuração (variáveis de ambiente):
    SOLIDES_API_TOKEN=<token>
    SOLIDES_WEBHOOK_SECRET=<secret>
    SOLIDES_SYNC_INTERVAL_MINUTES=15
    SOLIDES_CONFLICT_STRATEGY=most_recent
    SOLIDES_AUTO_CREATE_DEPARTMENTS=true
    SOLIDES_RATE_LIMIT_PER_MINUTE=60
"""

# Connector principal
# Conflict resolver
from modules.integrations.connectors.solides.conflict_resolver import (
    ConflictResolver,
    get_department_conflict_resolver,
    get_employee_conflict_resolver,
    get_occurrence_conflict_resolver,
    get_resolver_for_entity,
)
from modules.integrations.connectors.solides.connector import (
    SolidesConnector,
    SolidesTokenAuth,
)

# Integration Service (Funcionarios)
from modules.integrations.connectors.solides.integration_service import (
    SolidesIntegrationService,
    SyncAction,
    SyncEmployeeResult,
    SyncSummary,
    get_integration_service,
    sync_employees_from_solides,
)

# Mappers
from modules.integrations.connectors.solides.mappers import (
    absence_to_solides_absenteismo,
    candidate_to_solides_candidato,
    # Utils
    compute_solides_entity_hash,
    department_to_solides_departamento,
    detect_changes,
    employee_to_solides_colaborador,
    occurrence_to_solides_ocorrencia,
    # Absenteísmos
    solides_absenteismo_to_absence,
    # Candidato/Vaga
    solides_candidato_to_candidate,
    solides_cargo_to_position,
    # Colaborador
    solides_colaborador_to_employee,
    # Departamento/Cargo
    solides_departamento_to_department,
    solides_inscricao_to_application,
    # Ocorrências
    solides_ocorrencia_to_occurrence,
    # Passaporte
    solides_passaporte_to_behavioral_profile,
    solides_vaga_to_job_position,
)

# Models de banco
from modules.integrations.connectors.solides.models import (
    ConflictStatus,
    ConflictStrategy,
    SolidesAbsence,
    SolidesCostCenter,
    SolidesCredential,
    SolidesDepartment,
    # Models SQLAlchemy - Dados Importados
    SolidesEmployee,
    SolidesEntityMapping,
    SolidesIntegrationConfig,
    SolidesOccurrence,
    SolidesPosition,
    SolidesSyncConflict,
    SolidesSyncLog,
    # Models SQLAlchemy - Controle de Sincronização
    SolidesSyncState,
    SolidesWebhookLog,
    SolidesWorkplace,
    SolidesWorkSchedule,
    # Enums
    SyncDirection,
    SyncSource,
    SyncStatus,
    create_conflict,
    create_or_update_mapping,
    get_entity_mapping,
    # Helpers
    get_or_create_sync_state,
    log_sync_operation,
    log_webhook,
)

# Schemas Pydantic
from modules.integrations.connectors.solides.schemas import (
    PerfilDISC,
    # Enums
    SituacaoColaborador,
    SolidesAbsenteismo,
    SolidesAbsenteismoCreate,
    SolidesAvaliacao,
    SolidesCandidato,
    SolidesCargo,
    SolidesCBO,
    # Entidades principais
    SolidesColaborador,
    SolidesColaboradorCreate,
    SolidesColaboradorUpdate,
    SolidesCompetencia,
    SolidesDepartamento,
    SolidesEndereco,
    SolidesErrorResponse,
    SolidesInscricao,
    # Ocorrências e Absenteísmos
    SolidesOcorrencia,
    SolidesOcorrenciaCreate,
    # Responses
    SolidesPaginatedResponse,
    # Passaporte Comportamental
    SolidesPassaporte,
    SolidesPerfilDISC,
    SolidesPesquisaClima,
    SolidesSingleResponse,
    SolidesSyncStatus,
    SolidesUnidade,
    # Recrutamento
    SolidesVaga,
    # Webhooks
    SolidesWebhookEvent,
    SolidesWebhookEventType,
    StatusCandidato,
    StatusVaga,
    TipoAbsenteismo,
    TipoContrato,
    TipoOcorrencia,
)

# Serviço de sincronização
from modules.integrations.connectors.solides.sync_service import (
    SolidesSyncService,
    SyncResult,
    SyncStats,
    get_sync_service,
)

# Celery tasks
from modules.integrations.connectors.solides.tasks import (
    check_all_solides_health,
    check_solides_health,
    cleanup_old_sync_logs,
    cleanup_old_webhook_logs,
    process_webhooks,
    retry_failed_webhooks,
    schedule_entity_sync,
    # Helpers
    schedule_full_sync,
    schedule_incremental_sync,
    sync_all_condominios_incremental,
    sync_single_entity,
    sync_solides_full,
    sync_solides_incremental,
)

# Webhook handler
from modules.integrations.connectors.solides.webhook_handler import (
    SolidesWebhookHandler,
    process_webhook_queue,
)

__all__ = [
    # Connector
    "SolidesConnector",
    "SolidesTokenAuth",
    # Schemas - Enums
    "SituacaoColaborador",
    "TipoContrato",
    "TipoOcorrencia",
    "TipoAbsenteismo",
    "PerfilDISC",
    "StatusVaga",
    "StatusCandidato",
    "SolidesWebhookEventType",
    # Schemas - Entidades
    "SolidesColaborador",
    "SolidesColaboradorCreate",
    "SolidesColaboradorUpdate",
    "SolidesDepartamento",
    "SolidesCargo",
    "SolidesUnidade",
    "SolidesCBO",
    "SolidesEndereco",
    "SolidesOcorrencia",
    "SolidesOcorrenciaCreate",
    "SolidesAbsenteismo",
    "SolidesAbsenteismoCreate",
    "SolidesPassaporte",
    "SolidesPerfilDISC",
    "SolidesCompetencia",
    "SolidesVaga",
    "SolidesCandidato",
    "SolidesInscricao",
    "SolidesAvaliacao",
    "SolidesPesquisaClima",
    "SolidesWebhookEvent",
    "SolidesPaginatedResponse",
    "SolidesSingleResponse",
    "SolidesErrorResponse",
    "SolidesSyncStatus",
    # Mappers
    "solides_colaborador_to_employee",
    "employee_to_solides_colaborador",
    "solides_departamento_to_department",
    "department_to_solides_departamento",
    "solides_cargo_to_position",
    "solides_ocorrencia_to_occurrence",
    "occurrence_to_solides_ocorrencia",
    "solides_absenteismo_to_absence",
    "absence_to_solides_absenteismo",
    "solides_passaporte_to_behavioral_profile",
    "solides_candidato_to_candidate",
    "candidate_to_solides_candidato",
    "solides_vaga_to_job_position",
    "solides_inscricao_to_application",
    "compute_solides_entity_hash",
    "detect_changes",
    # Models - Enums
    "SyncDirection",
    "SyncStatus",
    "SyncSource",
    "ConflictStatus",
    "ConflictStrategy",
    # Models - SQLAlchemy - Controle
    "SolidesSyncState",
    "SolidesSyncLog",
    "SolidesSyncConflict",
    "SolidesEntityMapping",
    "SolidesWebhookLog",
    "SolidesIntegrationConfig",
    "SolidesCredential",
    # Models - SQLAlchemy - Dados Importados
    "SolidesEmployee",
    "SolidesDepartment",
    "SolidesPosition",
    "SolidesOccurrence",
    "SolidesAbsence",
    "SolidesWorkplace",
    "SolidesWorkSchedule",
    "SolidesCostCenter",
    # Models - Helpers
    "get_or_create_sync_state",
    "get_entity_mapping",
    "create_or_update_mapping",
    "log_sync_operation",
    "log_webhook",
    "create_conflict",
    # Sync Service
    "SolidesSyncService",
    "get_sync_service",
    "SyncStats",
    "SyncResult",
    # Webhook Handler
    "SolidesWebhookHandler",
    "process_webhook_queue",
    # Conflict Resolver
    "ConflictResolver",
    "get_employee_conflict_resolver",
    "get_department_conflict_resolver",
    "get_occurrence_conflict_resolver",
    "get_resolver_for_entity",
    # Celery Tasks
    "sync_solides_full",
    "sync_solides_incremental",
    "sync_all_condominios_incremental",
    "sync_single_entity",
    "check_solides_health",
    "check_all_solides_health",
    "process_webhooks",
    "retry_failed_webhooks",
    "cleanup_old_sync_logs",
    "cleanup_old_webhook_logs",
    "schedule_full_sync",
    "schedule_incremental_sync",
    "schedule_entity_sync",
    # Integration Service
    "SolidesIntegrationService",
    "SyncAction",
    "SyncEmployeeResult",
    "SyncSummary",
    "get_integration_service",
    "sync_employees_from_solides",
]

__version__ = "2.0.0"
