"""Testes para o modelo EquipmentMaintenance."""

from datetime import datetime, timedelta

import pytest

from modules.equipment_management.models.maintenance import (
    EquipmentMaintenance,
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
)


class TestMaintenanceModel:
    """Testes para o modelo EquipmentMaintenance."""

    def test_create_maintenance(self):
        """Testa criação de manutenção."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.PREVENTIVA,
            priority=MaintenancePriority.MEDIUM,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Manutenção Preventiva Trimestral",
        )

        assert maintenance.maintenance_type == MaintenanceType.PREVENTIVA
        assert maintenance.priority == MaintenancePriority.MEDIUM
        assert maintenance.status == MaintenanceStatus.SCHEDULED
        assert maintenance.is_active is True

    def test_maintenance_code_generation(self):
        """Testa geração de código da manutenção."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo de câmera",
        )

        assert maintenance.maintenance_code is not None
        assert maintenance.maintenance_code.startswith("MNT-")

    def test_start_maintenance(self):
        """Testa início de manutenção."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
        )

        maintenance.start()

        assert maintenance.status == MaintenanceStatus.IN_PROGRESS
        assert maintenance.started_at is not None

    def test_complete_maintenance(self):
        """Testa conclusão de manutenção."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
        )

        maintenance.start()
        maintenance.complete(problem_resolved=True)

        assert maintenance.status == MaintenanceStatus.COMPLETED
        assert maintenance.completed_at is not None
        assert maintenance.problem_resolved is True
        assert maintenance.is_completed is True

    def test_cancel_maintenance(self):
        """Testa cancelamento de manutenção."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.PREVENTIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Manutenção Preventiva",
        )

        maintenance.cancel()

        assert maintenance.status == MaintenanceStatus.CANCELLED

    def test_mark_waiting_parts(self):
        """Testa marcação aguardando peças."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
        )

        maintenance.start()
        maintenance.mark_waiting_parts(parts_requested=["Lente 2.8mm", "Cabo RJ45"])

        assert maintenance.status == MaintenanceStatus.WAITING_PARTS
        assert len(maintenance.parts_requested) == 2

    def test_mark_failed(self):
        """Testa marcação como falha."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
        )

        maintenance.start()
        maintenance.mark_failed()

        assert maintenance.status == MaintenanceStatus.FAILED

    def test_add_part_replaced(self):
        """Testa adição de peça substituída."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
        )

        maintenance.add_part_replaced(
            part_name="Lente 2.8mm",
            part_code="LNS-28MM",
            quantity=1,
            unit_cost=150.0,
        )

        assert len(maintenance.parts_replaced) == 1
        assert maintenance.parts_replaced[0]["part_name"] == "Lente 2.8mm"
        assert maintenance.parts_replaced[0]["total_cost"] == 150.0

    def test_calculate_total_cost(self):
        """Testa cálculo de custo total."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
            labor_cost=200.0,
            parts_cost=150.0,
            transport_cost=50.0,
            other_costs=30.0,
        )

        total = maintenance.calculate_total_cost()

        assert total == 430.0
        assert maintenance.total_cost == 430.0

    def test_sign_by_client(self):
        """Testa assinatura pelo cliente."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
        )

        maintenance.complete()
        maintenance.sign_by_client(signed_by="João Silva", signature="base64signature")

        assert maintenance.signed_by == "João Silva"
        assert maintenance.client_signature == "base64signature"
        assert maintenance.signed_at is not None

    def test_schedule_followup(self):
        """Testa agendamento de follow-up."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
        )

        followup_date = datetime.utcnow() + timedelta(days=7)
        maintenance.schedule_followup(
            followup_date=followup_date,
            notes="Verificar se problema persistiu",
        )

        assert maintenance.needs_followup is True
        assert maintenance.followup_date == followup_date
        assert maintenance.followup_notes == "Verificar se problema persistiu"

    def test_is_overdue(self):
        """Testa verificação de atraso."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
            sla_deadline=datetime.utcnow() - timedelta(hours=1),
        )

        assert maintenance.is_overdue is True

    def test_is_preventive_corrective(self):
        """Testa flags de tipo."""
        preventive = EquipmentMaintenance(
            maintenance_type=MaintenanceType.PREVENTIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Preventiva",
        )

        assert preventive.is_preventive is True
        assert preventive.is_corrective is False

        corrective = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Corretiva",
        )

        assert corrective.is_preventive is False
        assert corrective.is_corrective is True

    def test_recurring_maintenance(self):
        """Testa manutenção recorrente."""
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.PREVENTIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Manutenção Preventiva",
            is_recurring=True,
            recurrence_interval_days=90,
        )

        maintenance.complete()

        assert maintenance.next_maintenance_date is not None
        days_diff = (maintenance.next_maintenance_date - datetime.utcnow()).days
        assert 89 <= days_diff <= 91

    def test_all_maintenance_types(self):
        """Testa todos os tipos de manutenção."""
        types = [
            MaintenanceType.PREVENTIVA,
            MaintenanceType.CORRETIVA,
            MaintenanceType.PREDITIVA,
            MaintenanceType.INSTALACAO,
            MaintenanceType.ATUALIZACAO,
            MaintenanceType.CALIBRACAO,
        ]

        for m_type in types:
            maintenance = EquipmentMaintenance(
                maintenance_type=m_type,
                equipment_id="eq-001",
                equipment_code="EQ-001",
                equipment_name="Equipamento",
                equipment_type="camera_ip",
                title=f"Manutenção {m_type.value}",
            )
            assert maintenance.maintenance_type == m_type

    def test_all_priorities(self):
        """Testa todas as prioridades."""
        priorities = [
            MaintenancePriority.LOW,
            MaintenancePriority.MEDIUM,
            MaintenancePriority.HIGH,
            MaintenancePriority.URGENT,
            MaintenancePriority.CRITICAL,
        ]

        for priority in priorities:
            maintenance = EquipmentMaintenance(
                maintenance_type=MaintenanceType.CORRETIVA,
                priority=priority,
                equipment_id="eq-001",
                equipment_code="EQ-001",
                equipment_name="Equipamento",
                equipment_type="camera_ip",
                title="Manutenção",
            )
            assert maintenance.priority == priority

    def test_response_time_calculation(self):
        """Testa cálculo de tempo de resposta."""
        now = datetime.utcnow()
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
            reported_at=now - timedelta(hours=2),
        )

        maintenance.start()

        assert maintenance.response_time_hours is not None
        assert 1.9 <= maintenance.response_time_hours <= 2.1

    def test_resolution_time_calculation(self):
        """Testa cálculo de tempo de resolução."""
        now = datetime.utcnow()
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
            started_at=now - timedelta(hours=3),
        )
        maintenance.status = MaintenanceStatus.IN_PROGRESS

        maintenance.complete()

        assert maintenance.resolution_time_hours is not None
        assert 2.9 <= maintenance.resolution_time_hours <= 3.1

    def test_sla_met(self):
        """Testa verificação de SLA."""
        now = datetime.utcnow()

        # SLA cumprido
        maintenance = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
            sla_deadline=now + timedelta(hours=4),
        )

        maintenance.start()
        maintenance.complete()

        assert maintenance.sla_met is True

        # SLA não cumprido
        maintenance2 = EquipmentMaintenance(
            maintenance_type=MaintenanceType.CORRETIVA,
            equipment_id="eq-001",
            equipment_code="EQ-001",
            equipment_name="Câmera IP",
            equipment_type="camera_ip",
            title="Reparo",
            sla_deadline=now - timedelta(hours=1),
        )

        maintenance2.start()
        maintenance2.complete()

        assert maintenance2.sla_met is False
