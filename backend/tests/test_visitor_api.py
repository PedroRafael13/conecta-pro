"""Testes de API para o módulo Visitors."""

import pytest
from datetime import datetime, timedelta, date, time
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from modules.visitors.models.visitor import (
    Visitor,
    VisitorType,
    VisitorStatus,
    DocumentType,
)
from modules.visitors.models.authorization import (
    VisitorAuthorization,
    AuthorizationType,
    AuthorizationStatus,
)
from modules.visitors.models.log import (
    VisitorLog,
    AccessType,
    AccessMethod,
    AccessPoint,
)
from modules.visitors.models.schedule import (
    VisitorSchedule,
    ScheduleStatus,
    SchedulePriority,
)
from modules.visitors.schemas.visitor import (
    VisitorCreate,
    VisitorUpdate,
    VisitorFilter,
    VisitorBlock,
)
from modules.visitors.schemas.authorization import (
    AuthorizationCreate,
    AuthorizationApprove,
    AuthorizationReject,
    AuthorizationValidate,
)
from modules.visitors.schemas.log import (
    LogEntry,
    LogExit,
    LogDeny,
    LogFilter,
)
from modules.visitors.schemas.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleConfirm,
    ScheduleCancel,
)
from modules.visitors.services.visitor_service import VisitorService
from modules.visitors.services.authorization_service import AuthorizationService
from modules.visitors.services.log_service import LogService
from modules.visitors.services.schedule_service import ScheduleService
from modules.visitors.services.visitor_ai_service import VisitorAIService


class TestVisitorService:
    """Testes para VisitorService."""

    @pytest.fixture
    def mock_session(self):
        """Mock de sessão do banco."""
        session = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Fixture para VisitorService."""
        return VisitorService(mock_session)

    @pytest.mark.asyncio
    async def test_create_visitor(self, service):
        """Testa criação de visitante."""
        data = VisitorCreate(
            name="João Silva",
            document_type=DocumentType.CPF,
            document_number="12345678901",
            phone="11999999999",
            visitor_type=VisitorType.VISITANTE,
        )

        with patch.object(
            service.repository, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_visitor = Visitor(
                id=uuid4(),
                name=data.name,
                document_type=data.document_type,
                document_number=data.document_number,
                phone=data.phone,
                visitor_type=data.visitor_type,
            )
            mock_create.return_value = mock_visitor

            result = await service.create(data)

            assert result is not None
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_visitor_by_id(self, service):
        """Testa busca por ID."""
        visitor_id = uuid4()

        with patch.object(
            service.repository, "get_by_id", new_callable=AsyncMock
        ) as mock_get:
            mock_visitor = Visitor(
                id=visitor_id,
                name="Maria Santos",
                document_type=DocumentType.CPF,
                document_number="98765432100",
                visitor_type=VisitorType.VISITANTE,
            )
            mock_get.return_value = mock_visitor

            result = await service.get_by_id(visitor_id)

            assert result is not None
            assert result.name == "Maria Santos"
            mock_get.assert_called_once_with(visitor_id)

    @pytest.mark.asyncio
    async def test_get_visitor_not_found(self, service):
        """Testa busca de visitante não encontrado."""
        with patch.object(
            service.repository, "get_by_id", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None

            result = await service.get_by_id(uuid4())

            assert result is None

    @pytest.mark.asyncio
    async def test_update_visitor(self, service):
        """Testa atualização de visitante."""
        visitor_id = uuid4()
        data = VisitorUpdate(phone="11888888888")

        with patch.object(
            service.repository, "update", new_callable=AsyncMock
        ) as mock_update:
            mock_visitor = Visitor(
                id=visitor_id,
                name="Pedro Costa",
                document_type=DocumentType.CPF,
                document_number="11122233344",
                phone="11888888888",
                visitor_type=VisitorType.VISITANTE,
            )
            mock_update.return_value = mock_visitor

            result = await service.update(visitor_id, data)

            assert result is not None
            assert result.phone == "11888888888"

    @pytest.mark.asyncio
    async def test_delete_visitor(self, service):
        """Testa deleção de visitante."""
        visitor_id = uuid4()

        with patch.object(
            service.repository, "soft_delete", new_callable=AsyncMock
        ) as mock_delete:
            mock_delete.return_value = True

            result = await service.delete(visitor_id)

            assert result is True
            mock_delete.assert_called_once_with(visitor_id)

    @pytest.mark.asyncio
    async def test_block_visitor(self, service):
        """Testa bloqueio de visitante."""
        visitor_id = uuid4()
        data = VisitorBlock(reason="Comportamento inadequado", blocked_by="admin_001")

        with patch.object(
            service.repository, "block", new_callable=AsyncMock
        ) as mock_block:
            mock_visitor = Visitor(
                id=visitor_id,
                name="Carlos Lima",
                document_type=DocumentType.CPF,
                document_number="55566677788",
                visitor_type=VisitorType.VISITANTE,
                is_blocked=True,
                status=VisitorStatus.BLOQUEADO,
            )
            mock_block.return_value = mock_visitor

            result = await service.block(visitor_id, data)

            assert result is not None
            assert result.is_blocked is True

    @pytest.mark.asyncio
    async def test_search_visitors(self, service):
        """Testa busca de visitantes."""
        with patch.object(
            service.repository, "search", new_callable=AsyncMock
        ) as mock_search:
            mock_search.return_value = [
                Visitor(
                    id=uuid4(),
                    name="João Silva",
                    document_type=DocumentType.CPF,
                    document_number="12345678901",
                    visitor_type=VisitorType.VISITANTE,
                )
            ]

            result = await service.search("João", None, 10)

            assert len(result) == 1
            assert result[0].name == "João Silva"


class TestAuthorizationService:
    """Testes para AuthorizationService."""

    @pytest.fixture
    def mock_session(self):
        """Mock de sessão do banco."""
        session = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Fixture para AuthorizationService."""
        return AuthorizationService(mock_session)

    @pytest.mark.asyncio
    async def test_create_authorization(self, service):
        """Testa criação de autorização."""
        data = AuthorizationCreate(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            unit_id="unit_101",
            resident_id="resident_001",
            authorization_type=AuthorizationType.UNICA,
        )

        with patch.object(
            service.repository, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_auth = VisitorAuthorization(
                id=uuid4(),
                visitor_id=data.visitor_id,
                condominium_id=data.condominium_id,
                unit_id=data.unit_id,
                authorization_type=data.authorization_type,
            )
            mock_create.return_value = mock_auth

            result = await service.create(data)

            assert result is not None
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_authorization(self, service):
        """Testa aprovação de autorização."""
        auth_id = uuid4()
        data = AuthorizationApprove(
            approved_by_id="admin_001", approved_by_name="Administrador"
        )

        with patch.object(
            service.repository, "approve", new_callable=AsyncMock
        ) as mock_approve:
            mock_auth = VisitorAuthorization(
                id=auth_id,
                visitor_id=uuid4(),
                condominium_id="condo_001",
                authorization_type=AuthorizationType.UNICA,
                status=AuthorizationStatus.APROVADA,
            )
            mock_approve.return_value = mock_auth

            result = await service.approve(auth_id, data)

            assert result is not None
            assert result.status == AuthorizationStatus.APROVADA

    @pytest.mark.asyncio
    async def test_reject_authorization(self, service):
        """Testa rejeição de autorização."""
        auth_id = uuid4()
        data = AuthorizationReject(
            rejected_by_id="admin_001",
            rejected_by_name="Administrador",
            reason="Documentação incompleta",
        )

        with patch.object(
            service.repository, "reject", new_callable=AsyncMock
        ) as mock_reject:
            mock_auth = VisitorAuthorization(
                id=auth_id,
                visitor_id=uuid4(),
                condominium_id="condo_001",
                authorization_type=AuthorizationType.UNICA,
                status=AuthorizationStatus.REJEITADA,
            )
            mock_reject.return_value = mock_auth

            result = await service.reject(auth_id, data)

            assert result is not None
            assert result.status == AuthorizationStatus.REJEITADA

    @pytest.mark.asyncio
    async def test_validate_authorization(self, service):
        """Testa validação de autorização."""
        data = AuthorizationValidate(
            authorization_code="AUTH123",
            condominium_id="condo_001",
        )

        with patch.object(
            service.repository, "validate_access", new_callable=AsyncMock
        ) as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "authorization_id": str(uuid4()),
                "visitor_name": "João Silva",
                "authorization_type": "unica",
            }

            result = await service.validate(data)

            assert result is not None
            assert result.valid is True


class TestLogService:
    """Testes para LogService."""

    @pytest.fixture
    def mock_session(self):
        """Mock de sessão do banco."""
        session = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Fixture para LogService."""
        return LogService(mock_session)

    @pytest.mark.asyncio
    async def test_register_entry(self, service):
        """Testa registro de entrada."""
        data = LogEntry(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            unit_id="unit_101",
            access_method=AccessMethod.PORTARIA,
            access_point=AccessPoint.PORTARIA_PRINCIPAL,
            operator_id="op_001",
        )

        with patch.object(
            service.repository, "create_entry", new_callable=AsyncMock
        ) as mock_entry:
            mock_log = VisitorLog(
                id=uuid4(),
                visitor_id=data.visitor_id,
                condominium_id=data.condominium_id,
                access_type=AccessType.ENTRADA,
                access_method=data.access_method,
                access_point=data.access_point,
            )
            mock_entry.return_value = mock_log

            result = await service.register_entry(data)

            assert result is not None
            mock_entry.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_exit(self, service):
        """Testa registro de saída."""
        data = LogExit(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            access_point=AccessPoint.PORTARIA_PRINCIPAL,
        )

        with patch.object(
            service.repository, "create_exit", new_callable=AsyncMock
        ) as mock_exit:
            mock_log = VisitorLog(
                id=uuid4(),
                visitor_id=data.visitor_id,
                condominium_id=data.condominium_id,
                access_type=AccessType.SAIDA,
            )
            mock_exit.return_value = mock_log

            result = await service.register_exit(data)

            assert result is not None

    @pytest.mark.asyncio
    async def test_get_inside(self, service):
        """Testa listagem de visitantes dentro."""
        with patch.object(
            service.repository, "get_inside", new_callable=AsyncMock
        ) as mock_inside:
            mock_inside.return_value = [
                {
                    "visitor_id": str(uuid4()),
                    "visitor_name": "João Silva",
                    "entry_timestamp": datetime.utcnow(),
                    "duration_minutes": 30,
                }
            ]

            result = await service.get_inside("condo_001", 1, 100)

            assert len(result) >= 0


class TestScheduleService:
    """Testes para ScheduleService."""

    @pytest.fixture
    def mock_session(self):
        """Mock de sessão do banco."""
        session = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Fixture para ScheduleService."""
        return ScheduleService(mock_session)

    @pytest.mark.asyncio
    async def test_create_schedule(self, service):
        """Testa criação de agendamento."""
        data = ScheduleCreate(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            unit_id="unit_101",
            resident_id="resident_001",
            scheduled_date=date.today() + timedelta(days=1),
            scheduled_time_from=time(14, 0),
            purpose="Visita social",
        )

        with patch.object(
            service.repository, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_schedule = VisitorSchedule(
                id=uuid4(),
                visitor_id=data.visitor_id,
                condominium_id=data.condominium_id,
                scheduled_date=data.scheduled_date,
                scheduled_time_from=data.scheduled_time_from,
            )
            mock_create.return_value = mock_schedule

            result = await service.create(data)

            assert result is not None
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_schedule(self, service):
        """Testa confirmação de agendamento."""
        schedule_id = uuid4()
        data = ScheduleConfirm(
            confirmed_by_id="admin_001", confirmed_by_name="Administrador"
        )

        with patch.object(
            service.repository, "confirm", new_callable=AsyncMock
        ) as mock_confirm:
            mock_schedule = VisitorSchedule(
                id=schedule_id,
                visitor_id=uuid4(),
                condominium_id="condo_001",
                scheduled_date=date.today() + timedelta(days=1),
                scheduled_time_from=time(14, 0),
                status=ScheduleStatus.CONFIRMADO,
            )
            mock_confirm.return_value = mock_schedule

            result = await service.confirm(schedule_id, data)

            assert result is not None
            assert result.status == ScheduleStatus.CONFIRMADO

    @pytest.mark.asyncio
    async def test_cancel_schedule(self, service):
        """Testa cancelamento de agendamento."""
        schedule_id = uuid4()
        data = ScheduleCancel(
            reason="Visitante cancelou",
            cancelled_by_id="op_001",
            cancelled_by_name="Operador",
        )

        with patch.object(
            service.repository, "cancel", new_callable=AsyncMock
        ) as mock_cancel:
            mock_schedule = VisitorSchedule(
                id=schedule_id,
                visitor_id=uuid4(),
                condominium_id="condo_001",
                scheduled_date=date.today() + timedelta(days=1),
                scheduled_time_from=time(14, 0),
                status=ScheduleStatus.CANCELADO,
            )
            mock_cancel.return_value = mock_schedule

            result = await service.cancel(schedule_id, data)

            assert result is not None
            assert result.status == ScheduleStatus.CANCELADO

    @pytest.mark.asyncio
    async def test_get_today(self, service):
        """Testa listagem de agendamentos de hoje."""
        with patch.object(
            service.repository, "get_today", new_callable=AsyncMock
        ) as mock_today:
            mock_today.return_value = [
                VisitorSchedule(
                    id=uuid4(),
                    visitor_id=uuid4(),
                    condominium_id="condo_001",
                    scheduled_date=date.today(),
                    scheduled_time_from=time(14, 0),
                )
            ]

            result = await service.get_today("condo_001", 1, 50)

            assert result.items is not None


class TestVisitorAIService:
    """Testes para VisitorAIService."""

    @pytest.fixture
    def mock_session(self):
        """Mock de sessão do banco."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Fixture para VisitorAIService."""
        return VisitorAIService(mock_session)

    @pytest.mark.asyncio
    async def test_analyze_visitor_pattern(self, service):
        """Testa análise de padrão de visitante."""
        visitor_id = uuid4()

        with patch.object(
            service, "analyze_visitor_pattern", new_callable=AsyncMock
        ) as mock_analyze:
            mock_analyze.return_value = {
                "visitor_id": str(visitor_id),
                "total_visits": 15,
                "frequency_category": "frequente",
                "average_duration_minutes": 45,
                "preferred_days": ["segunda", "quarta"],
                "preferred_hours": [14, 15, 16],
                "trend": "estavel",
                "recommendations": ["Considerar autorização periódica"],
            }

            result = await service.analyze_visitor_pattern(visitor_id, 90)

            assert result is not None
            assert "total_visits" in result

    @pytest.mark.asyncio
    async def test_detect_anomalies(self, service):
        """Testa detecção de anomalias."""
        with patch.object(
            service, "detect_anomalies", new_callable=AsyncMock
        ) as mock_detect:
            mock_detect.return_value = [
                {
                    "type": "multiple_entries",
                    "severity": "medium",
                    "visitor_id": str(uuid4()),
                    "description": "Visitante com múltiplas entradas",
                }
            ]

            result = await service.detect_anomalies("condo_001", 24)

            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_suggest_authorization_type(self, service):
        """Testa sugestão de tipo de autorização."""
        visitor_id = uuid4()

        with patch.object(
            service, "suggest_authorization_type", new_callable=AsyncMock
        ) as mock_suggest:
            mock_suggest.return_value = {
                "suggested_type": "periodo",
                "confidence": 0.85,
                "reasoning": "Visitante frequente com padrão regular",
                "suggested_duration_days": 30,
            }

            result = await service.suggest_authorization_type(visitor_id, "condo_001")

            assert result is not None
            assert "suggested_type" in result

    @pytest.mark.asyncio
    async def test_get_peak_hours(self, service):
        """Testa horários de pico."""
        with patch.object(
            service, "get_peak_hours", new_callable=AsyncMock
        ) as mock_peak:
            mock_peak.return_value = {
                "peak_hours": [
                    {"hour": 14, "count": 45},
                    {"hour": 15, "count": 42},
                    {"hour": 10, "count": 38},
                ],
                "busiest_day": "sexta",
                "quietest_day": "domingo",
            }

            result = await service.get_peak_hours("condo_001", 30)

            assert result is not None
            assert "peak_hours" in result


class TestSchemaValidation:
    """Testes de validação de schemas."""

    def test_visitor_create_valid(self):
        """Testa schema de criação válido."""
        data = VisitorCreate(
            name="João Silva",
            document_type=DocumentType.CPF,
            document_number="12345678901",
            phone="11999999999",
            visitor_type=VisitorType.VISITANTE,
        )

        assert data.name == "João Silva"
        assert data.document_type == DocumentType.CPF

    def test_visitor_create_minimal(self):
        """Testa schema de criação mínimo."""
        data = VisitorCreate(
            name="Maria Santos",
            document_type=DocumentType.RG,
            document_number="123456789",
            visitor_type=VisitorType.PRESTADOR,
        )

        assert data.name == "Maria Santos"
        assert data.phone is None

    def test_authorization_create_valid(self):
        """Testa schema de autorização válido."""
        data = AuthorizationCreate(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            unit_id="unit_101",
            resident_id="resident_001",
            authorization_type=AuthorizationType.UNICA,
        )

        assert data.authorization_type == AuthorizationType.UNICA

    def test_log_entry_valid(self):
        """Testa schema de entrada válido."""
        data = LogEntry(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            access_method=AccessMethod.PORTARIA,
            access_point=AccessPoint.PORTARIA_PRINCIPAL,
        )

        assert data.access_method == AccessMethod.PORTARIA

    def test_schedule_create_valid(self):
        """Testa schema de agendamento válido."""
        data = ScheduleCreate(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            unit_id="unit_101",
            resident_id="resident_001",
            scheduled_date=date.today() + timedelta(days=1),
            scheduled_time_from=time(14, 0),
            purpose="Visita social",
        )

        assert data.scheduled_date > date.today()


class TestEdgeCases:
    """Testes de casos de borda."""

    def test_visitor_block_already_blocked(self):
        """Testa bloqueio de visitante já bloqueado."""
        visitor = Visitor(
            name="Pedro Costa",
            document_type=DocumentType.CPF,
            document_number="99988877766",
            visitor_type=VisitorType.VISITANTE,
            is_blocked=True,
            status=VisitorStatus.BLOQUEADO,
        )

        # Deve funcionar sem erro
        visitor.block("Nova razão", "admin_002")
        assert visitor.is_blocked is True

    def test_authorization_use_exceeded(self):
        """Testa uso de autorização com limite excedido."""
        auth = VisitorAuthorization(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            authorization_type=AuthorizationType.UNICA,
            status=AuthorizationStatus.APROVADA,
            max_uses=1,
            uses_count=1,
        )

        result = auth.use()

        assert result is False

    def test_schedule_check_in_not_today(self):
        """Testa check-in em agendamento não de hoje."""
        schedule = VisitorSchedule(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            scheduled_date=date.today() + timedelta(days=5),
            scheduled_time_from=time(14, 0),
            status=ScheduleStatus.CONFIRMADO,
        )

        assert schedule.can_check_in is False

    def test_log_duration_without_exit(self):
        """Testa duração sem saída."""
        log = VisitorLog(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            access_type=AccessType.ENTRADA,
            entry_timestamp=datetime.utcnow(),
            exit_timestamp=None,
        )

        assert log.formatted_duration is None
