"""
Models SQLAlchemy para sincronização Sólides.
Sprint 33: Integration Framework

Tabelas para rastreamento de sincronização, conflitos e logs.
"""

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.database import Base


class SyncDirection(StrEnum):
    """Direção da sincronização."""

    SOLIDES_TO_CONECTA = "solides_to_conecta"
    CONECTA_TO_SOLIDES = "conecta_to_solides"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(StrEnum):
    """Status da sincronização."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class ConflictStatus(StrEnum):
    """Status do conflito."""

    PENDING = "pending"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class ConflictStrategy(StrEnum):
    """Estratégia de resolução de conflito."""

    SOLIDES_WINS = "solides_wins"
    CONECTA_WINS = "conecta_wins"
    MOST_RECENT = "most_recent"
    MANUAL = "manual"


class SyncSource(StrEnum):
    """Fonte da última alteração."""

    SOLIDES = "solides"
    CONECTA = "conecta"
    MANUAL = "manual"
    WEBHOOK = "webhook"


class SolidesSyncState(Base):
    """
    Estado de sincronização por entidade/empresa.
    Rastreia última sincronização e cursor.
    """

    __tablename__ = "solides_sync_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Tipo de entidade sendo sincronizada
    entity_type = Column(String(50), nullable=False)  # colaboradores, departamentos, etc.

    # Estado da sincronização
    status = Column(SQLEnum(SyncStatus), default=SyncStatus.PENDING)
    direction = Column(SQLEnum(SyncDirection), default=SyncDirection.SOLIDES_TO_CONECTA)

    # Cursores e contadores
    last_cursor = Column(String(255))  # Cursor da última página
    last_sync_at = Column(DateTime)  # Última sincronização incremental
    last_full_sync_at = Column(DateTime)  # Última sincronização completa
    last_sync_count = Column(Integer, default=0)  # Registros na última sincronização
    total_synced = Column(Integer, default=0)  # Total sincronizado

    # Erro (se houver)
    last_error = Column(Text)
    last_error_at = Column(DateTime)
    error_count = Column(Integer, default=0)

    # Metadados
    config = Column(JSONB, default=dict)  # Configurações específicas
    metadata_extra = Column(JSONB, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("condominio_id", "entity_type", name="uq_solides_sync_entity"),
        Index("ix_solides_sync_status", "status"),
    )


class SolidesSyncLog(Base):
    """
    Log de cada operação de sincronização.
    """

    __tablename__ = "solides_sync_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Tipo de sincronização
    sync_type = Column(String(20), nullable=False)  # full, incremental, webhook
    entity_type = Column(String(50), nullable=False)
    direction = Column(SQLEnum(SyncDirection))

    # Resultados
    status = Column(SQLEnum(SyncStatus), nullable=False)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)

    # Contadores
    total_processed = Column(Integer, default=0)
    created_count = Column(Integer, default=0)
    updated_count = Column(Integer, default=0)
    deleted_count = Column(Integer, default=0)
    skipped_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    conflict_count = Column(Integer, default=0)

    # Erros
    errors = Column(JSONB, default=list)  # Lista de erros [{entity_id, error, details}]

    # Metadados
    triggered_by = Column(String(50))  # user, scheduler, webhook
    trigger_info = Column(JSONB, default=dict)  # {user_id, job_id, webhook_event}

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_solides_sync_log_date", "started_at"),
        Index("ix_solides_sync_log_entity", "entity_type", "started_at"),
    )


class SolidesSyncConflict(Base):
    """
    Conflitos de sincronização detectados.
    """

    __tablename__ = "solides_sync_conflict"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    sync_log_id = Column(UUID(as_uuid=True), ForeignKey("solides_sync_log.id"))

    # Entidade em conflito
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(100), nullable=False)  # ID local
    solides_id = Column(String(100), nullable=False)  # ID no Sólides

    # Status
    status = Column(SQLEnum(ConflictStatus), default=ConflictStatus.PENDING)
    strategy = Column(SQLEnum(ConflictStrategy))

    # Dados do conflito
    solides_data = Column(JSONB, nullable=False)  # Dados do Sólides
    conecta_data = Column(JSONB, nullable=False)  # Dados do Conecta
    changed_fields = Column(JSONB, default=list)  # Campos com diferença
    solides_updated_at = Column(DateTime)  # Data alteração no Sólides
    conecta_updated_at = Column(DateTime)  # Data alteração no Conecta

    # Resolução
    resolved_at = Column(DateTime)
    resolved_by = Column(UUID(as_uuid=True))  # User ID
    resolution_strategy = Column(SQLEnum(ConflictStrategy))
    resolution_data = Column(JSONB)  # Dados finais após resolução
    resolution_notes = Column(Text)

    # Metadados
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_solides_conflict_status", "status"),
        Index("ix_solides_conflict_entity", "entity_type", "solides_id"),
    )


class SolidesEntityMapping(Base):
    """
    Mapeamento de IDs entre Sólides e Conecta PRO.
    Permite lookup rápido de entidades sincronizadas.
    """

    __tablename__ = "solides_entity_mapping"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Tipo e IDs
    entity_type = Column(String(50), nullable=False)
    solides_id = Column(String(100), nullable=False)  # ID no Sólides
    conecta_id = Column(UUID(as_uuid=True), nullable=False)  # ID local

    # Tracking de alterações
    sync_source = Column(SQLEnum(SyncSource), default=SyncSource.SOLIDES)
    last_synced_at = Column(DateTime, default=datetime.utcnow)
    solides_updated_at = Column(DateTime)  # updated_at do Sólides
    conecta_updated_at = Column(DateTime)  # updated_at local
    data_hash = Column(String(32))  # Hash dos dados para detectar mudanças

    # Status
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime)

    # Metadados
    extra_data = Column(JSONB, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("condominio_id", "entity_type", "solides_id", name="uq_solides_mapping_solides"),
        UniqueConstraint("condominio_id", "entity_type", "conecta_id", name="uq_solides_mapping_conecta"),
        Index("ix_solides_mapping_lookup", "entity_type", "solides_id"),
    )


class SolidesWebhookLog(Base):
    """
    Log de webhooks recebidos do Sólides.
    """

    __tablename__ = "solides_webhook_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), index=True)

    # Evento
    event_type = Column(String(100), nullable=False)

    # Payload
    payload = Column(JSONB, nullable=False)
    headers = Column(JSONB, default=dict)

    # Rastreamento
    request_id = Column(String(100))
    ip_address = Column(String(45))

    # Status do processamento
    status = Column(String(50), default="received")
    error = Column(Text)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime)
    processing_time_ms = Column(Integer)

    # Retry
    retry_count = Column(Integer, default=0)
    next_retry_at = Column(DateTime)

    # Auditoria
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SolidesIntegrationConfig(Base):
    """
    Configuração da integração Sólides por condomínio.
    Espelha a tabela existente no banco de dados.
    """

    __tablename__ = "solides_integration_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, unique=True)

    # Configurações de API
    api_version = Column(String(10), default="v1", nullable=False)
    base_url_v1 = Column(String(500))
    base_url_v3 = Column(String(500))

    # Configurações de sincronização
    sync_interval_minutes = Column(Integer, default=15, nullable=False)
    sync_entities = Column(JSONB)
    conflict_strategy = Column(String(50), default="most_recent", nullable=False)
    auto_create_departments = Column(Boolean, default=True, nullable=False)
    auto_create_positions = Column(Boolean, default=True, nullable=False)

    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60, nullable=False)

    # Webhooks
    webhook_secret = Column(String(200))
    webhook_url = Column(String(500))

    # Status geral
    is_enabled = Column(Boolean, default=False, nullable=False)
    is_connected = Column(Boolean, default=False, nullable=False)

    # Último health check
    last_health_check_at = Column(DateTime)
    last_health_check_status = Column(Boolean)
    last_health_check_message = Column(Text)

    # Sync status
    last_full_sync_at = Column(DateTime)
    last_incremental_sync_at = Column(DateTime)
    next_sync_at = Column(DateTime)

    # Metadados
    extra_config = Column(JSONB)

    # Auditoria
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))


class SolidesCredential(Base):
    """
    Credenciais de acesso à API Sólides (armazenadas de forma segura).
    """

    __tablename__ = "solides_credential"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, unique=True)

    # Token de acesso (criptografado)
    api_token_encrypted = Column(Text, nullable=False)

    # Metadados do token
    token_name = Column(String(100))  # Nome/descrição do token
    token_created_at = Column(DateTime)  # Quando o token foi criado no Sólides
    token_expires_at = Column(DateTime)  # Se tiver expiração

    # Validação
    last_validated_at = Column(DateTime)
    is_valid = Column(Boolean, default=True)

    # Auditoria
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== HELPERS ====================


def get_or_create_sync_state(db, condominio_id, entity_type: str) -> SolidesSyncState:
    """
    Obtém ou cria estado de sincronização para entidade.
    """
    state = (
        db.query(SolidesSyncState)
        .filter(SolidesSyncState.condominio_id == condominio_id, SolidesSyncState.entity_type == entity_type)
        .first()
    )

    if not state:
        state = SolidesSyncState(condominio_id=condominio_id, entity_type=entity_type, status=SyncStatus.PENDING)
        db.add(state)
        db.commit()
        db.refresh(state)

    return state


def get_entity_mapping(
    db, condominio_id, entity_type: str, solides_id: str = None, conecta_id: str = None
) -> SolidesEntityMapping | None:
    """
    Busca mapeamento de entidade por solides_id ou conecta_id.
    """
    query = db.query(SolidesEntityMapping).filter(
        SolidesEntityMapping.condominio_id == condominio_id,
        SolidesEntityMapping.entity_type == entity_type,
        SolidesEntityMapping.is_active,
    )

    if solides_id:
        query = query.filter(SolidesEntityMapping.solides_id == str(solides_id))
    elif conecta_id:
        query = query.filter(SolidesEntityMapping.conecta_id == conecta_id)
    else:
        return None

    return query.first()


def create_or_update_mapping(
    db,
    condominio_id,
    entity_type: str,
    solides_id: str,
    conecta_id,
    sync_source: SyncSource = SyncSource.SOLIDES,
    data_hash: str = None,
    extra_data: dict = None,
) -> SolidesEntityMapping:
    """
    Cria ou atualiza mapeamento de entidade.
    """
    mapping = get_entity_mapping(db, condominio_id, entity_type, solides_id=solides_id)

    if mapping:
        mapping.conecta_id = conecta_id
        mapping.sync_source = sync_source
        mapping.last_synced_at = datetime.utcnow()
        mapping.data_hash = data_hash
        if extra_data:
            mapping.extra_data = extra_data
    else:
        mapping = SolidesEntityMapping(
            condominio_id=condominio_id,
            entity_type=entity_type,
            solides_id=str(solides_id),
            conecta_id=conecta_id,
            sync_source=sync_source,
            data_hash=data_hash,
            extra_data=extra_data or {},
        )
        db.add(mapping)

    db.commit()
    db.refresh(mapping)
    return mapping


def log_sync_operation(
    db,
    condominio_id,
    sync_type: str,
    entity_type: str,
    status: SyncStatus,
    direction: SyncDirection = None,
    triggered_by: str = "system",
    **kwargs,
) -> SolidesSyncLog:
    """
    Registra log de operação de sincronização.
    """
    log = SolidesSyncLog(
        condominio_id=condominio_id,
        sync_type=sync_type,
        entity_type=entity_type,
        status=status,
        direction=direction,
        triggered_by=triggered_by,
        started_at=datetime.utcnow(),
        **kwargs,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def log_webhook(
    db,
    event_type: str,
    payload: dict,
    condominio_id=None,
    headers: dict = None,
    request_id: str = None,
    ip_address: str = None,
) -> SolidesWebhookLog:
    """
    Registra log de webhook recebido (síncrono).
    """
    log = SolidesWebhookLog(
        condominio_id=condominio_id,
        event_type=event_type,
        payload=payload,
        headers=headers or {},
        request_id=request_id,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


async def log_webhook_async(
    db,
    event_type: str,
    payload: dict,
    condominio_id=None,
    headers: dict = None,
    request_id: str = None,
    ip_address: str = None,
) -> SolidesWebhookLog:
    """
    Registra log de webhook recebido (assíncrono).
    """
    log = SolidesWebhookLog(
        condominio_id=condominio_id,
        event_type=event_type,
        payload=payload,
        headers=headers or {},
        request_id=request_id,
        ip_address=ip_address,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


def create_conflict(
    db,
    condominio_id,
    entity_type: str,
    entity_id: str,
    solides_id: str,
    solides_data: dict,
    conecta_data: dict,
    changed_fields: list[str],
    sync_log_id=None,
    solides_updated_at: datetime = None,
    conecta_updated_at: datetime = None,
) -> SolidesSyncConflict:
    """
    Registra conflito de sincronização.
    """
    conflict = SolidesSyncConflict(
        condominio_id=condominio_id,
        sync_log_id=sync_log_id,
        entity_type=entity_type,
        entity_id=str(entity_id),
        solides_id=str(solides_id),
        solides_data=solides_data,
        conecta_data=conecta_data,
        changed_fields=changed_fields,
        solides_updated_at=solides_updated_at,
        conecta_updated_at=conecta_updated_at,
        status=ConflictStatus.PENDING,
    )
    db.add(conflict)
    db.commit()
    db.refresh(conflict)
    return conflict


# ==================== TABELAS DE DADOS IMPORTADOS ====================


class SolidesEmployee(Base):
    """
    Colaboradores importados do Sólides.
    Tabela de staging com todos os dados históricos sincronizados.
    """

    __tablename__ = "solides_employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    solides_id = Column(String(50), nullable=False)

    # Dados pessoais
    nome = Column(String(255), nullable=False)
    email = Column(String(255))
    cpf = Column(String(14))
    rg = Column(String(20))
    data_nascimento = Column(DateTime)
    sexo = Column(String(10))
    estado_civil = Column(String(50))
    telefone = Column(String(20))
    celular = Column(String(20))

    # Endereço (JSON para flexibilidade)
    endereco = Column(JSONB, default=dict)

    # Dados profissionais
    matricula = Column(String(50))
    cargo_id = Column(String(50))
    cargo_nome = Column(String(255))
    departamento_id = Column(String(50))
    departamento_nome = Column(String(255))
    unidade_id = Column(String(50))
    unidade_nome = Column(String(255))
    gestor_id = Column(String(50))
    gestor_nome = Column(String(255))

    # Contrato
    data_admissao = Column(DateTime)
    data_demissao = Column(DateTime)
    tipo_contrato = Column(String(50))
    regime_trabalho = Column(String(50))
    jornada_trabalho = Column(String(100))
    carga_horaria_semanal = Column(Integer)
    salario = Column(String(50))  # String para preservar formato original

    # Dados DP
    ctps_numero = Column(String(50))
    ctps_serie = Column(String(20))
    ctps_uf = Column(String(2))
    pis = Column(String(20))
    titulo_eleitor = Column(String(20))
    certificado_reservista = Column(String(20))

    # Dependentes (JSON)
    dependentes = Column(JSONB, default=list)

    # Status
    situacao = Column(String(50))  # ativo, inativo, ferias, afastado, demitido

    # Perfil comportamental (JSON)
    perfil_disc = Column(JSONB)
    perfil_profiler = Column(JSONB)

    # Foto
    foto_url = Column(String(500))

    # Dados extras do Sólides
    dados_adicionais = Column(JSONB, default=dict)

    # Metadados de sincronização
    data_hash = Column(String(32))
    first_synced_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow)
    sync_source = Column(String(50), default="solides")

    # Auditoria
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("condominio_id", "solides_id", name="uq_solides_employee_id"),
        Index("ix_solides_employee_cpf", "cpf"),
        Index("ix_solides_employee_email", "email"),
        Index("ix_solides_employee_matricula", "matricula"),
        Index("ix_solides_employee_situacao", "situacao"),
    )


class SolidesDepartment(Base):
    """
    Departamentos importados do Sólides.
    """

    __tablename__ = "solides_departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    solides_id = Column(String(50), nullable=False)

    nome = Column(String(255), nullable=False)
    codigo = Column(String(50))
    departamento_pai_id = Column(String(50))
    gestor_id = Column(String(50))
    unidade_id = Column(String(50))
    ativo = Column(Boolean, default=True)

    # Metadados
    data_hash = Column(String(32))
    first_synced_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("condominio_id", "solides_id", name="uq_solides_department_id"),)


class SolidesPosition(Base):
    """
    Cargos importados do Sólides.
    """

    __tablename__ = "solides_positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    solides_id = Column(String(50), nullable=False)

    nome = Column(String(255), nullable=False)
    codigo = Column(String(50))
    descricao = Column(Text)
    departamento_id = Column(String(50))
    cbo_id = Column(String(50))
    cbo_codigo = Column(String(20))
    nivel = Column(String(50))
    faixa_salarial_min = Column(String(50))
    faixa_salarial_max = Column(String(50))
    ativo = Column(Boolean, default=True)

    # Metadados
    data_hash = Column(String(32))
    first_synced_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("condominio_id", "solides_id", name="uq_solides_position_id"),)


class SolidesOccurrence(Base):
    """
    Ocorrências importadas do Sólides.
    """

    __tablename__ = "solides_occurrences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    solides_id = Column(String(50), nullable=False)

    colaborador_id = Column(String(50), nullable=False, index=True)
    colaborador_nome = Column(String(255))
    tipo = Column(String(100), nullable=False)  # advertencia_verbal, suspensao, elogio, etc.
    descricao = Column(Text)
    data = Column(DateTime, nullable=False)
    data_vigencia = Column(DateTime)

    # Detalhes específicos
    duracao_dias = Column(Integer)
    valor_aumento = Column(String(50))
    percentual_aumento = Column(String(20))
    novo_cargo_id = Column(String(50))
    novo_cargo_nome = Column(String(255))

    # Responsável
    registrado_por_id = Column(String(50))
    registrado_por_nome = Column(String(255))

    # Anexos (JSON)
    anexos = Column(JSONB, default=list)

    observacoes = Column(Text)
    dados_adicionais = Column(JSONB, default=dict)

    # Metadados
    data_hash = Column(String(32))
    first_synced_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("condominio_id", "solides_id", name="uq_solides_occurrence_id"),
        Index("ix_solides_occurrence_colaborador", "colaborador_id"),
        Index("ix_solides_occurrence_tipo", "tipo"),
        Index("ix_solides_occurrence_data", "data"),
    )


class SolidesAbsence(Base):
    """
    Absenteísmos/Afastamentos importados do Sólides.
    """

    __tablename__ = "solides_absences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    solides_id = Column(String(50), nullable=False)

    colaborador_id = Column(String(50), nullable=False, index=True)
    colaborador_nome = Column(String(255))
    tipo = Column(String(100), nullable=False)  # falta, atraso, atestado, ferias, etc.
    motivo = Column(Text)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime)
    horas = Column(String(20))
    minutos_atraso = Column(Integer)

    # Justificativa
    justificado = Column(Boolean, default=False)
    documento_anexo = Column(String(500))
    cid = Column(String(20))

    # Impacto
    desconto_em_folha = Column(Boolean, default=True)
    dias_descontados = Column(Integer)

    # INSS
    numero_beneficio_inss = Column(String(50))
    data_inicio_inss = Column(DateTime)
    data_fim_inss = Column(DateTime)

    # Responsável
    registrado_por_id = Column(String(50))
    registrado_por_nome = Column(String(255))

    observacoes = Column(Text)
    dados_adicionais = Column(JSONB, default=dict)

    # Metadados
    data_hash = Column(String(32))
    first_synced_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("condominio_id", "solides_id", name="uq_solides_absence_id"),
        Index("ix_solides_absence_colaborador", "colaborador_id"),
        Index("ix_solides_absence_tipo", "tipo"),
        Index("ix_solides_absence_data", "data_inicio"),
    )


class SolidesWorkplace(Base):
    """
    Locais de trabalho/Unidades importados do Sólides.
    """

    __tablename__ = "solides_workplaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    solides_id = Column(String(50), nullable=False)

    nome = Column(String(255), nullable=False)
    codigo = Column(String(50))
    cnpj = Column(String(20))
    endereco = Column(JSONB, default=dict)
    telefone = Column(String(20))
    email = Column(String(255))
    ativo = Column(Boolean, default=True)

    # Metadados
    data_hash = Column(String(32))
    first_synced_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("condominio_id", "solides_id", name="uq_solides_workplace_id"),)


class SolidesWorkSchedule(Base):
    """
    Escalas de trabalho importadas do Sólides.
    """

    __tablename__ = "solides_work_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    solides_id = Column(String(50), nullable=False)

    nome = Column(String(255), nullable=False)
    codigo = Column(String(50))
    tipo = Column(String(50))  # diurno, noturno, etc.
    carga_horaria_semanal = Column(Integer)

    # Horários (JSON para flexibilidade)
    horarios = Column(JSONB, default=dict)

    ativo = Column(Boolean, default=True)

    # Metadados
    data_hash = Column(String(32))
    first_synced_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("condominio_id", "solides_id", name="uq_solides_work_schedule_id"),)


class SolidesCostCenter(Base):
    """
    Centros de custo importados do Sólides.
    """

    __tablename__ = "solides_cost_centers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    solides_id = Column(String(50), nullable=False)

    nome = Column(String(255), nullable=False)
    codigo = Column(String(50))
    descricao = Column(Text)
    ativo = Column(Boolean, default=True)

    # Metadados
    data_hash = Column(String(32))
    first_synced_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("condominio_id", "solides_id", name="uq_solides_cost_center_id"),)
