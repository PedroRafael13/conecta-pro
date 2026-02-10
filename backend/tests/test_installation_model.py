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
            installation_code="INST-001",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow() + timedelta(days=1),
            equipment_count=2,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
        )

        assert installation.client_id == "client-001"
        assert installation.status == InstallationStatus.SCHEDULED
        assert installation.equipment_count == 2
        assert installation.is_active is True

    def test_installation_code_generation(self):
        """Testa código da instalação (obrigatório no construtor)."""
        installation = EquipmentInstallation(
            installation_code="INST-TEST-001",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_count=1,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
        )

        assert installation.installation_code is not None
        assert installation.installation_code == "INST-TEST-001"

    def test_start_installation(self):
        """Testa início de instalação."""
        installation = EquipmentInstallation(
            installation_code="INST-002",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_count=1,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
        )

        installation.start(technician_id="tech-001", technician_name="João Técnico")

        assert installation.status == InstallationStatus.IN_PROGRESS
        assert installation.started_at is not None

    def test_complete_installation(self):
        """Testa conclusão de instalação."""
        installation = EquipmentInstallation(
            installation_code="INST-003",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_count=1,
            status=InstallationStatus.IN_PROGRESS,
            is_active=True,
        )

        installation.complete(technical_report="Instalação realizada com sucesso")

        assert installation.status == InstallationStatus.COMPLETED
        assert installation.completed_at is not None
        assert installation.technical_report == "Instalação realizada com sucesso"

    def test_cancel_installation(self):
        """Testa cancelamento de instalação."""
        installation = EquipmentInstallation(
            installation_code="INST-004",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_count=1,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
        )

        installation.cancel(reason="Cliente desistiu", cancelled_by="admin-001")

        assert installation.status == InstallationStatus.CANCELLED

    def test_reschedule_installation(self):
        """Testa reagendamento de instalação."""
        original_date = datetime.utcnow() + timedelta(days=1)
        installation = EquipmentInstallation(
            installation_code="INST-005",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=original_date,
            equipment_count=1,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
            rescheduled_count=0,
        )

        new_date = datetime.utcnow() + timedelta(days=3)
        installation.reschedule(new_date=new_date, reason="Cliente indisponível")

        assert installation.status == InstallationStatus.RESCHEDULED
        assert installation.scheduled_date == new_date

    def test_multiple_reschedules(self):
        """Testa múltiplos reagendamentos."""
        installation = EquipmentInstallation(
            installation_code="INST-006",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow() + timedelta(days=1),
            equipment_count=1,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
            rescheduled_count=0,
        )

        installation.reschedule(new_date=datetime.utcnow() + timedelta(days=2), reason="Primeiro reagendamento")
        installation.reschedule(new_date=datetime.utcnow() + timedelta(days=3), reason="Segundo reagendamento")

        assert installation.status == InstallationStatus.RESCHEDULED

    def test_accept_by_client(self):
        """Testa aceite pelo cliente."""
        installation = EquipmentInstallation(
            installation_code="INST-007",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_count=1,
            status=InstallationStatus.COMPLETED,
            is_active=True,
        )

        installation.accept_by_client(accepted_by="João Silva")

        assert installation.status == InstallationStatus.COMPLETED

    def test_add_photo(self):
        """Testa adição de fotos."""
        installation = EquipmentInstallation(
            installation_code="INST-008",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_count=1,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
        )

        installation.add_photo(photo_type="before", photo_url="/photos/before1.jpg")
        installation.add_photo(photo_type="after", photo_url="/photos/after1.jpg")

        assert len(installation.photos_before) == 1
        assert len(installation.photos_after) == 1

    def test_calculate_total_cost(self):
        """Testa cálculo de custo total."""
        installation = EquipmentInstallation(
            installation_code="INST-009",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_count=1,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
            labor_cost=300.0,
            transport_cost=100.0,
        )

        total = installation.calculate_total_cost()

        assert total == 400.0
        assert installation.total_cost == 400.0

    def test_is_overdue(self):
        """Testa verificação de atraso."""
        # Instalação atrasada
        installation = EquipmentInstallation(
            installation_code="INST-010",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow() - timedelta(days=1),
            equipment_count=1,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
        )

        assert installation.is_overdue is True

        # Instalação futura
        installation.scheduled_date = datetime.utcnow() + timedelta(days=1)
        assert installation.is_overdue is False

    def test_days_overdue(self):
        """Testa cálculo de dias de atraso."""
        installation = EquipmentInstallation(
            installation_code="INST-011",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow() - timedelta(days=5),
            equipment_count=1,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
        )

        assert installation.days_overdue >= 4  # Pode variar dependendo da hora

    def test_actual_duration_calculation(self):
        """Testa cálculo de duração real."""
        installation = EquipmentInstallation(
            installation_code="INST-012",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_count=1,
            status=InstallationStatus.IN_PROGRESS,
            is_active=True,
        )

        installation.complete()

        assert installation.completed_at is not None

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
                installation_code=f"INST-{status.name}",
                client_id="client-001",
                client_name="Cliente Teste",
                address="Rua das Flores, 100",
                scheduled_date=datetime.utcnow(),
                equipment_count=1,
                status=status,
                is_active=True,
            )
            assert installation.status == status

    def test_equipment_count(self):
        """Testa contagem de equipamentos."""
        installation = EquipmentInstallation(
            installation_code="INST-COUNT",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_count=3,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
        )

        assert installation.equipment_count == 3

    def test_location_with_coordinates(self):
        """Testa localização com coordenadas GPS."""
        installation = EquipmentInstallation(
            installation_code="INST-GPS",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            city="São Paulo",
            state="SP",
            zip_code="01310-100",
            gps_latitude=-23.5505,
            gps_longitude=-46.6333,
            scheduled_date=datetime.utcnow(),
            equipment_count=1,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
        )

        assert installation.gps_latitude == -23.5505
        assert installation.gps_longitude == -46.6333
        assert installation.city == "São Paulo"
        assert installation.state == "SP"

    def test_technician_assignment(self):
        """Testa atribuição de técnico."""
        installation = EquipmentInstallation(
            installation_code="INST-TECH",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_count=1,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
            technician_id="tech-001",
            technician_name="José Técnico",
        )

        assert installation.technician_id == "tech-001"
        assert installation.technician_name == "José Técnico"

    def test_team_members(self):
        """Testa membros da equipe."""
        installation = EquipmentInstallation(
            installation_code="INST-TEAM",
            client_id="client-001",
            client_name="Cliente Teste",
            address="Rua das Flores, 100",
            scheduled_date=datetime.utcnow(),
            equipment_count=1,
            status=InstallationStatus.SCHEDULED,
            is_active=True,
            team_members=["tech-001", "tech-002"],
        )

        assert len(installation.team_members) == 2
