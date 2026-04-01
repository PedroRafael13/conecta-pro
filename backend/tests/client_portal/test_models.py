"""
Testes para models do Client Portal.

Cobertura: ClientPortalSession, ClientTicket, ClientTicketMessage
Testa enums, tablenames, colunas — sem instanciar models (requer DB).
"""

import pytest


class TestClientPortalSessionModel:
    """Testes do model ClientPortalSession."""

    def test_session_tablename(self):
        from modules.client_portal.models.session import ClientPortalSession

        assert ClientPortalSession.__tablename__ == "client_portal_sessions"

    def test_session_columns(self):
        from modules.client_portal.models.session import ClientPortalSession

        columns = [c.name for c in ClientPortalSession.__table__.columns]
        required = ["id", "client_id", "token", "ip_address", "user_agent", "expires_at", "is_active"]
        for col in required:
            assert col in columns, f"Column {col} missing from client_portal_sessions"

    def test_session_has_timestamps(self):
        from modules.client_portal.models.session import ClientPortalSession

        columns = [c.name for c in ClientPortalSession.__table__.columns]
        assert "created_at" in columns
        assert "updated_at" in columns


class TestClientTicketModel:
    """Testes do model ClientTicket."""

    def test_ticket_tablename(self):
        from modules.client_portal.models.ticket import ClientTicket

        assert ClientTicket.__tablename__ == "client_portal_tickets"

    def test_ticket_status_enum(self):
        from modules.client_portal.models.ticket import TicketStatus

        statuses = [s.value for s in TicketStatus]
        assert "ABERTO" in statuses
        assert "EM_ANDAMENTO" in statuses
        assert "RESPONDIDO" in statuses
        assert "FECHADO" in statuses

    def test_ticket_priority_enum(self):
        from modules.client_portal.models.ticket import TicketPriority

        priorities = [p.value for p in TicketPriority]
        assert "BAIXA" in priorities
        assert "NORMAL" in priorities
        assert "ALTA" in priorities
        assert "URGENTE" in priorities

    def test_ticket_columns(self):
        from modules.client_portal.models.ticket import ClientTicket

        columns = [c.name for c in ClientTicket.__table__.columns]
        required = [
            "id",
            "client_id",
            "kit_id",
            "subject",
            "description",
            "status",
            "priority",
            "closed_at",
            "created_at",
            "updated_at",
        ]
        for col in required:
            assert col in columns, f"Column {col} missing from client_portal_tickets"

    def test_ticket_status_count(self):
        from modules.client_portal.models.ticket import TicketStatus

        assert len(TicketStatus) == 4

    def test_ticket_priority_count(self):
        from modules.client_portal.models.ticket import TicketPriority

        assert len(TicketPriority) == 4

    def test_ticket_has_relationship_to_messages(self):
        from modules.client_portal.models.ticket import ClientTicket

        assert hasattr(ClientTicket, "messages")


class TestClientTicketMessageModel:
    """Testes do model ClientTicketMessage."""

    def test_message_tablename(self):
        from modules.client_portal.models.ticket_message import ClientTicketMessage

        assert ClientTicketMessage.__tablename__ == "client_portal_ticket_messages"

    def test_sender_type_enum(self):
        from modules.client_portal.models.ticket_message import SenderType

        assert SenderType.CLIENT.value == "CLIENT"
        assert SenderType.INTERNAL.value == "INTERNAL"

    def test_sender_type_count(self):
        from modules.client_portal.models.ticket_message import SenderType

        assert len(SenderType) == 2

    def test_message_columns(self):
        from modules.client_portal.models.ticket_message import ClientTicketMessage

        columns = [c.name for c in ClientTicketMessage.__table__.columns]
        required = [
            "id",
            "ticket_id",
            "sender_type",
            "sender_id",
            "sender_name",
            "message",
            "attachments",
            "created_at",
        ]
        for col in required:
            assert col in columns, f"Column {col} missing from client_portal_ticket_messages"

    def test_message_has_relationship_to_ticket(self):
        from modules.client_portal.models.ticket_message import ClientTicketMessage

        assert hasattr(ClientTicketMessage, "ticket")


class TestClientPortalServiceImports:
    """Testa que todos os services importam corretamente."""

    def test_import_auth_service(self):
        from modules.client_portal.services.auth_service import PortalAuthService

        assert PortalAuthService is not None

    def test_import_kit_access_service(self):
        from modules.client_portal.services.kit_access_service import PortalKitAccessService

        assert PortalKitAccessService is not None

    def test_import_ticket_service(self):
        from modules.client_portal.services.ticket_service import PortalTicketService

        assert PortalTicketService is not None


class TestClientPortalSchemaImports:
    """Testa que todos os schemas importam corretamente."""

    def test_import_auth_schemas(self):
        from modules.client_portal.schemas.auth import PortalLoginRequest, PortalLoginResponse

        assert PortalLoginRequest is not None
        assert PortalLoginResponse is not None

    def test_import_ticket_schemas(self):
        from modules.client_portal.schemas.ticket import TicketCreate, TicketResponse

        assert TicketCreate is not None
        assert TicketResponse is not None

    def test_import_kit_schemas(self):
        from modules.client_portal.schemas.kit import PortalKitResponse

        assert PortalKitResponse is not None


class TestClientPortalControllerImports:
    """Testa importacao dos controllers e contagem de rotas."""

    def test_auth_controller_routes(self):
        from modules.client_portal.controllers.auth_controller import router

        assert len(router.routes) >= 3

    def test_kit_controller_routes(self):
        from modules.client_portal.controllers.kit_controller import router

        assert len(router.routes) >= 4

    def test_ticket_controller_routes(self):
        from modules.client_portal.controllers.ticket_controller import router

        assert len(router.routes) >= 5

    def test_aggregator_total_routes(self):
        from modules.client_portal import router

        assert len(router.routes) >= 12


class TestClientPortalServiceInstantiation:
    """Testa que todos os services podem ser instanciados."""

    def test_auth_service_init(self):
        from unittest.mock import AsyncMock

        from modules.client_portal.services.auth_service import PortalAuthService

        service = PortalAuthService(db=AsyncMock())
        assert service is not None

    def test_kit_access_service_init(self):
        from unittest.mock import AsyncMock

        from modules.client_portal.services.kit_access_service import PortalKitAccessService

        service = PortalKitAccessService(db=AsyncMock())
        assert service is not None

    def test_ticket_service_init(self):
        from unittest.mock import AsyncMock

        from modules.client_portal.services.ticket_service import PortalTicketService

        service = PortalTicketService(db=AsyncMock())
        assert service is not None


class TestClientPortalMiddleware:
    """Testa middleware de autenticacao."""

    def test_middleware_import(self):
        from modules.client_portal.middleware.portal_auth import get_current_portal_client

        assert callable(get_current_portal_client)
