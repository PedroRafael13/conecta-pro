"""
Testes unitários para os models do módulo Facilities.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from modules.facilities.models.area import Area, AreaStatus, AreaType
from modules.facilities.models.checklist import (
    Checklist,
    ChecklistItem,
    ChecklistStatus,
    ItemStatus,
)
from modules.facilities.models.inspection import (
    Inspection,
    InspectionResult,
    InspectionStatus,
    InspectionType,
)
from modules.facilities.models.maintenance import (
    Maintenance,
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
)
from modules.facilities.models.service_request import (
    ServiceRequest,
    ServiceRequestCategory,
    ServiceRequestPriority,
    ServiceRequestStatus,
)


class TestAreaModel:
    """Testes para o model Area."""

    def test_create_area(self):
        """Testa criação de área."""
        area = Area(
            name="Hall de Entrada",
            code="HALL-001",
            area_type=AreaType.COMMON_AREA,
            status=AreaStatus.ACTIVE,
            floor="Térreo",
            size_m2=Decimal("150.5"),
        )

        assert area.name == "Hall de Entrada"
        assert area.code == "HALL-001"
        assert area.area_type == AreaType.COMMON_AREA
        assert area.status == AreaStatus.ACTIVE
        assert area.size_m2 == Decimal("150.5")

    def test_area_type_enum(self):
        """Testa valores do enum AreaType."""
        assert AreaType.BUILDING.value == "building"
        assert AreaType.FLOOR.value == "floor"
        assert AreaType.APARTMENT.value == "apartment"
        assert AreaType.COMMON_AREA.value == "common_area"
        assert AreaType.PARKING.value == "parking"
        assert AreaType.TECHNICAL.value == "technical"
        assert AreaType.EXTERNAL.value == "external"
        assert AreaType.OTHER.value == "other"

    def test_area_status_enum(self):
        """Testa valores do enum AreaStatus."""
        assert AreaStatus.ACTIVE.value == "active"
        assert AreaStatus.INACTIVE.value == "inactive"
        assert AreaStatus.UNDER_MAINTENANCE.value == "under_maintenance"
        assert AreaStatus.RESTRICTED.value == "restricted"


class TestMaintenanceModel:
    """Testes para o model Maintenance."""

    def test_create_maintenance(self):
        """Testa criação de manutenção."""
        maintenance = Maintenance(
            title="Troca de lâmpadas",
            description="Substituir lâmpadas queimadas no corredor",
            maintenance_type=MaintenanceType.CORRECTIVE,
            priority=MaintenancePriority.MEDIUM,
            status=MaintenanceStatus.PENDING,
            scheduled_date=date.today() + timedelta(days=7),
            estimated_hours=Decimal("2.0"),
            estimated_cost=Decimal("500.00"),
        )

        assert maintenance.title == "Troca de lâmpadas"
        assert maintenance.maintenance_type == MaintenanceType.CORRECTIVE
        assert maintenance.priority == MaintenancePriority.MEDIUM
        assert maintenance.status == MaintenanceStatus.PENDING

    def test_maintenance_type_enum(self):
        """Testa valores do enum MaintenanceType."""
        assert MaintenanceType.PREVENTIVE.value == "preventive"
        assert MaintenanceType.CORRECTIVE.value == "corrective"
        assert MaintenanceType.PREDICTIVE.value == "predictive"
        assert MaintenanceType.EMERGENCY.value == "emergency"

    def test_maintenance_priority_enum(self):
        """Testa valores do enum MaintenancePriority."""
        assert MaintenancePriority.LOW.value == "low"
        assert MaintenancePriority.MEDIUM.value == "medium"
        assert MaintenancePriority.HIGH.value == "high"
        assert MaintenancePriority.CRITICAL.value == "critical"

    def test_maintenance_status_enum(self):
        """Testa valores do enum MaintenanceStatus."""
        assert MaintenanceStatus.PENDING.value == "pending"
        assert MaintenanceStatus.SCHEDULED.value == "scheduled"
        assert MaintenanceStatus.IN_PROGRESS.value == "in_progress"
        assert MaintenanceStatus.COMPLETED.value == "completed"
        assert MaintenanceStatus.CANCELLED.value == "cancelled"


class TestInspectionModel:
    """Testes para o model Inspection."""

    def test_create_inspection(self):
        """Testa criação de inspeção."""
        inspection = Inspection(
            title="Vistoria Mensal - Elevadores",
            description="Inspeção mensal dos elevadores",
            inspection_type=InspectionType.ROUTINE,
            status=InspectionStatus.SCHEDULED,
            scheduled_date=date.today() + timedelta(days=3),
            inspector_name="João Silva",
        )

        assert inspection.title == "Vistoria Mensal - Elevadores"
        assert inspection.inspection_type == InspectionType.ROUTINE
        assert inspection.status == InspectionStatus.SCHEDULED

    def test_inspection_type_enum(self):
        """Testa valores do enum InspectionType."""
        assert InspectionType.ROUTINE.value == "routine"
        assert InspectionType.PERIODIC.value == "periodic"
        assert InspectionType.SPECIAL.value == "special"
        assert InspectionType.COMPLIANCE.value == "compliance"
        assert InspectionType.SAFETY.value == "safety"
        assert InspectionType.HANDOVER.value == "handover"

    def test_inspection_result_enum(self):
        """Testa valores do enum InspectionResult."""
        assert InspectionResult.APPROVED.value == "approved"
        assert InspectionResult.APPROVED_WITH_OBSERVATIONS.value == "approved_with_observations"
        assert InspectionResult.REJECTED.value == "rejected"
        assert InspectionResult.PENDING_REVIEW.value == "pending_review"


class TestChecklistModel:
    """Testes para os models Checklist e ChecklistItem."""

    def test_create_checklist(self):
        """Testa criação de checklist."""
        checklist = Checklist(
            name="Checklist de Limpeza",
            description="Verificação diária de limpeza",
            category="cleaning",
            is_template=True,
            status=ChecklistStatus.DRAFT,
        )

        assert checklist.name == "Checklist de Limpeza"
        assert checklist.is_template is True
        assert checklist.status == ChecklistStatus.DRAFT

    def test_create_checklist_item(self):
        """Testa criação de item de checklist."""
        item = ChecklistItem(
            question="Piso limpo e sem manchas?",
            category="floor",
            is_required=True,
            order=1,
            status=ItemStatus.PENDING,
            weight=Decimal("1.0"),
        )

        assert item.question == "Piso limpo e sem manchas?"
        assert item.is_required is True
        assert item.status == ItemStatus.PENDING

    def test_checklist_status_enum(self):
        """Testa valores do enum ChecklistStatus."""
        assert ChecklistStatus.DRAFT.value == "draft"
        assert ChecklistStatus.IN_PROGRESS.value == "in_progress"
        assert ChecklistStatus.COMPLETED.value == "completed"
        assert ChecklistStatus.CANCELLED.value == "cancelled"

    def test_item_status_enum(self):
        """Testa valores do enum ItemStatus."""
        assert ItemStatus.PENDING.value == "pending"
        assert ItemStatus.OK.value == "ok"
        assert ItemStatus.WARNING.value == "warning"
        assert ItemStatus.CRITICAL.value == "critical"
        assert ItemStatus.NOT_APPLICABLE.value == "not_applicable"


class TestServiceRequestModel:
    """Testes para o model ServiceRequest."""

    def test_create_service_request(self):
        """Testa criação de solicitação de serviço."""
        request = ServiceRequest(
            title="Vazamento no apartamento 101",
            description="Vazamento na pia da cozinha",
            category=ServiceRequestCategory.PLUMBING,
            priority=ServiceRequestPriority.HIGH,
            status=ServiceRequestStatus.OPEN,
            requester_name="Maria Santos",
            requester_email="maria@email.com",
            requester_phone="11999999999",
        )

        assert request.title == "Vazamento no apartamento 101"
        assert request.category == ServiceRequestCategory.PLUMBING
        assert request.priority == ServiceRequestPriority.HIGH
        assert request.status == ServiceRequestStatus.OPEN

    def test_service_request_category_enum(self):
        """Testa valores do enum ServiceRequestCategory."""
        assert ServiceRequestCategory.ELECTRICAL.value == "electrical"
        assert ServiceRequestCategory.PLUMBING.value == "plumbing"
        assert ServiceRequestCategory.HVAC.value == "hvac"
        assert ServiceRequestCategory.CLEANING.value == "cleaning"
        assert ServiceRequestCategory.SECURITY.value == "security"
        assert ServiceRequestCategory.LANDSCAPING.value == "landscaping"
        assert ServiceRequestCategory.GENERAL.value == "general"
        assert ServiceRequestCategory.OTHER.value == "other"

    def test_service_request_priority_enum(self):
        """Testa valores do enum ServiceRequestPriority."""
        assert ServiceRequestPriority.LOW.value == "low"
        assert ServiceRequestPriority.MEDIUM.value == "medium"
        assert ServiceRequestPriority.HIGH.value == "high"
        assert ServiceRequestPriority.URGENT.value == "urgent"

    def test_service_request_status_enum(self):
        """Testa valores do enum ServiceRequestStatus."""
        assert ServiceRequestStatus.OPEN.value == "open"
        assert ServiceRequestStatus.ACKNOWLEDGED.value == "acknowledged"
        assert ServiceRequestStatus.ASSIGNED.value == "assigned"
        assert ServiceRequestStatus.IN_PROGRESS.value == "in_progress"
        assert ServiceRequestStatus.ON_HOLD.value == "on_hold"
        assert ServiceRequestStatus.COMPLETED.value == "completed"
        assert ServiceRequestStatus.REJECTED.value == "rejected"
        assert ServiceRequestStatus.CANCELLED.value == "cancelled"
