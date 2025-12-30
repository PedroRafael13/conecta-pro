"""Testes para o modelo EquipmentInstallation."""

from datetime import datetime, timedelta

import pytest

from modules.equipment_management.models.installation import (
    EquipmentInstallation,
    InstallationStatus,
)


class TestInstallationModel:
    """Testes para o modelo EquipmentInstallation."""

    def test_create_installation(self):
        """Testa criação de instalação."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow() + timedelta(days=1),
            equipment_ids=["eq-001", "eq-002"],
        )

        assert installation.client_id == "client-001"
        assert installation.status == InstallationStatus.SCHEDULED
        assert installation.equipment_count == 2
        assert installation.is_active is True

    def test_installation_code_generation(self):
        """Testa geração de código da instalação."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_ids=["eq-001"],
        )

        assert installation.installation_code is not None
        assert installation.installation_code.startswith("INST-")

    def test_start_installation(self):
        """Testa início de instalação."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_ids=["eq-001"],
        )

        installation.start()

        assert installation.status == InstallationStatus.IN_PROGRESS
        assert installation.started_at is not None

    def test_complete_installation(self):
        """Testa conclusão de instalação."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_ids=["eq-001"],
        )

        installation.start()
        installation.complete(technical_report="Instalação realizada com sucesso")

        assert installation.status == InstallationStatus.PENDING_APPROVAL
        assert installation.completed_at is not None
        assert installation.technical_report == "Instalação realizada com sucesso"
        assert installation.is_completed is True

    def test_cancel_installation(self):
        """Testa cancelamento de instalação."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_ids=["eq-001"],
        )

        installation.cancel(reason="Cliente desistiu")

        assert installation.status == InstallationStatus.CANCELLED
        assert installation.cancelled_at is not None
        assert installation.cancellation_reason == "Cliente desistiu"

    def test_reschedule_installation(self):
        """Testa reagendamento de instalação."""
        original_date = datetime.utcnow() + timedelta(days=1)
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=original_date,
            equipment_ids=["eq-001"],
        )

        new_date = datetime.utcnow() + timedelta(days=3)
        installation.reschedule(new_date=new_date, reason="Cliente indisponível")

        assert installation.status == InstallationStatus.RESCHEDULED
        assert installation.scheduled_date == new_date
        assert installation.rescheduled_count == 1
        assert installation.original_date == original_date
        assert installation.rescheduled_reason == "Cliente indisponível"

    def test_multiple_reschedules(self):
        """Testa múltiplos reagendamentos."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow() + timedelta(days=1),
            equipment_ids=["eq-001"],
        )

        installation.reschedule(new_date=datetime.utcnow() + timedelta(days=2))
        installation.reschedule(new_date=datetime.utcnow() + timedelta(days=3))

        assert installation.rescheduled_count == 2

    def test_accept_by_client(self):
        """Testa aceite pelo cliente."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_ids=["eq-001"],
        )

        installation.start()
        installation.complete()
        installation.accept_by_client(accepted_by="João Silva")

        assert installation.status == InstallationStatus.COMPLETED
        assert installation.client_accepted is True
        assert installation.client_accepted_by == "João Silva"
        assert installation.client_accepted_at is not None
        assert installation.has_client_acceptance is True

    def test_add_photo(self):
        """Testa adição de fotos."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_ids=["eq-001"],
        )

        installation.add_photo(url="/photos/before1.jpg", photo_type="before")
        installation.add_photo(url="/photos/after1.jpg", photo_type="after")
        installation.add_photo(url="/photos/equipment1.jpg", photo_type="equipment")

        assert len(installation.photos_before) == 1
        assert len(installation.photos_after) == 1
        assert len(installation.photos_equipment) == 1

    def test_calculate_total_cost(self):
        """Testa cálculo de custo total."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_ids=["eq-001"],
            labor_cost=300.0,
            transport_cost=100.0,
            total_materials_value=200.0,
        )

        total = installation.calculate_total_cost()

        assert total == 600.0
        assert installation.total_cost == 600.0

    def test_is_overdue(self):
        """Testa verificação de atraso."""
        # Instalação atrasada
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow() - timedelta(days=1),
            equipment_ids=["eq-001"],
        )

        assert installation.is_overdue is True

        # Instalação futura
        installation.scheduled_date = datetime.utcnow() + timedelta(days=1)
        assert installation.is_overdue is False

    def test_days_overdue(self):
        """Testa cálculo de dias de atraso."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow() - timedelta(days=5),
            equipment_ids=["eq-001"],
        )

        assert installation.days_overdue == 5

    def test_actual_duration_calculation(self):
        """Testa cálculo de duração real."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_ids=["eq-001"],
        )

        installation.started_at = datetime.utcnow() - timedelta(hours=3)
        installation.start()
        installation.complete()

        assert installation.actual_duration_hours is not None

    def test_all_statuses(self):
        """Testa todos os status."""
        statuses = [
            InstallationStatus.SCHEDULED,
            InstallationStatus.IN_PROGRESS,
            InstallationStatus.COMPLETED,
            InstallationStatus.CANCELLED,
            InstallationStatus.RESCHEDULED,
            InstallationStatus.PENDING_APPROVAL,
            InstallationStatus.PARTIAL,
        ]

        for status in statuses:
            installation = EquipmentInstallation(
                client_id="client-001",
                client_name="Cliente Teste",
                address="Rua das Flores, 100",
                scheduled_date=datetime.utcnow(),
                equipment_ids=["eq-001"],
            )
            installation.status = status
            assert installation.status == status

    def test_equipment_count(self):
        """Testa contagem de equipamentos."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_ids=["eq-001", "eq-002", "eq-003"],
        )

        assert installation.equipment_count == 3

    def test_location_with_coordinates(self):
        """Testa localização com coordenadas GPS."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            city="São Paulo",
            state="SP",
            zip_code="01310-100",
            gps_latitude=-23.5505,
            gps_longitude=-46.6333,
            scheduled_date=datetime.utcnow(),
            equipment_ids=["eq-001"],
        )

        assert installation.gps_latitude == -23.5505
        assert installation.gps_longitude == -46.6333
        assert installation.city == "São Paulo"
        assert installation.state == "SP"

    def test_technician_assignment(self):
        """Testa atribuição de técnico."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_ids=["eq-001"],
            technician_id="tech-001",
            technician_name="José Técnico",
        )

        assert installation.technician_id == "tech-001"
        assert installation.technician_name == "José Técnico"

    def test_team_members(self):
        """Testa membros da equipe."""
        installation = EquipmentInstallation(
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_ids=["eq-001"],
            team_members=["tech-001", "tech-002"],
        )

        assert len(installation.team_members) == 2
