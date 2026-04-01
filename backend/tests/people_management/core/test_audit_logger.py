"""Testes do Audit Logger de Gestao de Pessoas."""

import pytest

from modules.people_management.core.audit import (
    AuditAction,
    AuditActor,
    AuditChange,
    AuditContext,
    AuditLog,
    AuditLogger,
)


@pytest.fixture
def audit_logger():
    return AuditLogger()


@pytest.fixture
def sample_actor():
    return AuditActor(
        user_id="user-1",
        user_name="Joao Silva",
        user_role="supervisor",
        user_module="OPS",
    )


@pytest.fixture
def sample_context():
    return AuditContext(
        ip_address="10.0.0.1",
        user_agent="Chrome/120",
        device_type="web",
        session_id="sess-abc",
    )


class TestAuditAction:
    def test_all_actions_exist(self):
        assert AuditAction.CREATE == "create"
        assert AuditAction.READ == "read"
        assert AuditAction.UPDATE == "update"
        assert AuditAction.DELETE == "delete"
        assert AuditAction.SIGN == "sign"
        assert AuditAction.CLOCK_PUNCH == "clock_punch"
        assert AuditAction.SYNC == "sync"

    def test_action_count(self):
        assert len(AuditAction) >= 13


class TestAuditLog:
    def test_log_creation(self, sample_actor, sample_context):
        log = AuditLog(
            action=AuditAction.CREATE,
            entity="documento",
            entity_id="doc-123",
            description="Criou documento",
            source_module="DP",
            actor=sample_actor,
            context=sample_context,
        )
        assert log.id is not None
        assert log.timestamp is not None
        assert log.changes == []
        assert log.affected_modules == []

    def test_log_to_dict(self, sample_actor, sample_context):
        log = AuditLog(
            action=AuditAction.UPDATE,
            entity="funcionario",
            entity_id="func-456",
            description="Atualizou salario",
            source_module="DP",
            actor=sample_actor,
            context=sample_context,
            changes=[AuditChange("salario", 3000.0, 3500.0)],
        )
        data = log.to_dict()
        assert data["action"] == "update"
        assert data["entity"] == "funcionario"
        assert len(data["changes"]) == 1
        assert data["changes"][0]["field"] == "salario"

    def test_log_with_related_ids(self, sample_actor, sample_context):
        log = AuditLog(
            action=AuditAction.SIGN,
            entity="documento",
            entity_id="doc-789",
            description="Assinou documento",
            source_module="PORTAL",
            actor=sample_actor,
            context=sample_context,
            related_funcionario_id="func-1",
            related_documento_id="doc-789",
        )
        assert log.related_funcionario_id == "func-1"
        assert log.related_documento_id == "doc-789"


class TestAuditLogger:
    @pytest.mark.asyncio
    async def test_log_creates_entry(self, audit_logger, sample_actor, sample_context):
        result = await audit_logger.log(
            action=AuditAction.CREATE,
            entity="documento",
            entity_id="doc-1",
            description="Criou documento",
            source_module="DP",
            actor=sample_actor,
            context=sample_context,
        )
        assert isinstance(result, AuditLog)
        assert result.action == AuditAction.CREATE
        assert audit_logger.buffer_size == 1

    @pytest.mark.asyncio
    async def test_log_multiple_entries(self, audit_logger, sample_actor, sample_context):
        for i in range(5):
            await audit_logger.log(
                action=AuditAction.READ,
                entity="funcionario",
                entity_id=f"func-{i}",
                description=f"Leu funcionario {i}",
                source_module="PORTAL",
                actor=sample_actor,
                context=sample_context,
            )
        assert audit_logger.buffer_size == 5

    @pytest.mark.asyncio
    async def test_query_by_entity(self, audit_logger, sample_actor, sample_context):
        await audit_logger.log(
            action=AuditAction.CREATE,
            entity="documento",
            entity_id="d1",
            description="doc",
            source_module="DP",
            actor=sample_actor,
            context=sample_context,
        )
        await audit_logger.log(
            action=AuditAction.CREATE,
            entity="funcionario",
            entity_id="f1",
            description="func",
            source_module="DP",
            actor=sample_actor,
            context=sample_context,
        )
        results = await audit_logger.query(entity="documento")
        assert len(results) == 1
        assert results[0].entity == "documento"

    @pytest.mark.asyncio
    async def test_query_by_action(self, audit_logger, sample_actor, sample_context):
        await audit_logger.log(
            action=AuditAction.CREATE,
            entity="doc",
            entity_id="1",
            description="c",
            source_module="DP",
            actor=sample_actor,
            context=sample_context,
        )
        await audit_logger.log(
            action=AuditAction.DELETE,
            entity="doc",
            entity_id="2",
            description="d",
            source_module="DP",
            actor=sample_actor,
            context=sample_context,
        )
        results = await audit_logger.query(action=AuditAction.DELETE)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_query_by_source_module(self, audit_logger, sample_actor, sample_context):
        await audit_logger.log(
            action=AuditAction.CREATE,
            entity="doc",
            entity_id="1",
            description="c",
            source_module="DP",
            actor=sample_actor,
            context=sample_context,
        )
        await audit_logger.log(
            action=AuditAction.CREATE,
            entity="doc",
            entity_id="2",
            description="c",
            source_module="OPS",
            actor=sample_actor,
            context=sample_context,
        )
        results = await audit_logger.query(source_module="OPS")
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_query_with_limit(self, audit_logger, sample_actor, sample_context):
        for i in range(10):
            await audit_logger.log(
                action=AuditAction.READ,
                entity="x",
                entity_id=str(i),
                description="x",
                source_module="DP",
                actor=sample_actor,
                context=sample_context,
            )
        results = await audit_logger.query(limit=3)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_log_with_extra_data(self, audit_logger, sample_actor, sample_context):
        result = await audit_logger.log(
            action=AuditAction.CLOCK_PUNCH,
            entity="ponto",
            entity_id="p-1",
            description="Bateu ponto",
            source_module="PONTO",
            actor=sample_actor,
            context=sample_context,
            extra_data={"facial_match": 0.95, "dentro_geofence": True},
        )
        assert result.extra_data["facial_match"] == 0.95
