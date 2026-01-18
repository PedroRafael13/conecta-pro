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
from modules.integrations.connectors.solides.connector import (
    SolidesConnector,
    SolidesTokenAuth,
)

# Schemas Pydantic
from modules.integrations.connectors.solides.schemas import (
    # Enums
    SituacaoColaborador,
    TipoContrato,
    TipoOcorrencia,
    TipoAbsenteismo,
    PerfilDISC,
    StatusVaga,
    StatusCandidato,
    SolidesWebhookEventType,
    # Entidades principais
    SolidesColaborador,
    SolidesColaboradorCreate,
    SolidesColaboradorUpdate,
    SolidesDepartamento,
    SolidesCargo,
    SolidesUnidade,
    SolidesCBO,
    SolidesEndereco,
    # Ocorrências e Absenteísmos
    SolidesOcorrencia,
    SolidesOcorrenciaCreate,
    SolidesAbsenteismo,
    SolidesAbsenteismoCreate,
    # Passaporte Comportamental
    SolidesPassaporte,
    SolidesPerfilDISC,
    SolidesCompetencia,
    # Recrutamento
    SolidesVaga,
    SolidesCandidato,
    SolidesInscricao,
    SolidesAvaliacao,
    SolidesPesquisaClima,
    # Webhooks
    SolidesWebhookEvent,
    # Responses
    SolidesPaginatedResponse,
    SolidesSingleResponse,
    SolidesErrorResponse,
    SolidesSyncStatus,
)

# Mappers
from modules.integrations.connectors.solides.mappers import (
    # Colaborador
    solides_colaborador_to_employee,
    employee_to_solides_colaborador,
    # Departamento/Cargo
    solides_departamento_to_department,
    department_to_solides_departamento,
    solides_cargo_to_position,
    # Ocorrências
    solides_ocorrencia_to_occurrence,
    occurrence_to_solides_ocorrencia,
    # Absenteísmos
    solides_absenteismo_to_absence,
    absence_to_solides_absenteismo,
    # Passaporte
    solides_passaporte_to_behavioral_profile,
    # Candidato/Vaga
    solides_candidato_to_candidate,
    candidate_to_solides_candidato,
    solides_vaga_to_job_position,
    solides_inscricao_to_application,
    # Utils
    compute_solides_entity_hash,
    detect_changes,
)

# Models de banco
from modules.integrations.connectors.solides.models import (
    # Enums
    SyncDirection,
    SyncStatus,
    SyncSource,
    ConflictStatus,
    ConflictStrategy,
    # Models SQLAlchemy
    SolidesSyncState,
    SolidesSyncLog,
    SolidesSyncConflict,
    SolidesEntityMapping,
    SolidesWebhookLog,
    SolidesIntegrationConfig,
    SolidesCredential,
    # Helpers
    get_or_create_sync_state,
    get_entity_mapping,
    create_or_update_mapping,
    log_sync_operation,
    log_webhook,
    create_conflict,
)

# Serviço de sincronização
from modules.integrations.connectors.solides.sync_service import (
    SolidesSyncService,
    get_sync_service,
    SyncStats,
    SyncResult,
)

# Webhook handler
from modules.integrations.connectors.solides.webhook_handler import (
    SolidesWebhookHandler,
    process_webhook_queue,
)

# Conflict resolver
from modules.integrations.connectors.solides.conflict_resolver import (
    ConflictResolver,
    get_employee_conflict_resolver,
    get_department_conflict_resolver,
    get_occurrence_conflict_resolver,
    get_resolver_for_entity,
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

# Celery tasks
from modules.integrations.connectors.solides.tasks import (
    sync_solides_full,
    sync_solides_incremental,
    sync_all_condominios_incremental,
    sync_single_entity,
    check_solides_health,
    check_all_solides_health,
    process_webhooks,
    retry_failed_webhooks,
    cleanup_old_sync_logs,
    cleanup_old_webhook_logs,
    # Helpers
    schedule_full_sync,
    schedule_incremental_sync,
    schedule_entity_sync,
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
    # Models - SQLAlchemy
    "SolidesSyncState",
    "SolidesSyncLog",
    "SolidesSyncConflict",
    "SolidesEntityMapping",
    "SolidesWebhookLog",
    "SolidesIntegrationConfig",
    "SolidesCredential",
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
