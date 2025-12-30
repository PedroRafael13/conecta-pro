"""Testes para ResidentVehicle Model."""

import pytest
from datetime import datetime
from uuid import uuid4

from modules.residents.models.vehicle import (
    ResidentVehicle,
    VehicleType,
    VehicleStatus,
    FuelType,
)


class TestResidentVehicleModel:
    """Testes para o modelo ResidentVehicle."""

    def test_create_vehicle(self):
        """Testa criação de veículo."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            brand="Toyota",
            model="Corolla",
            color="Prata",
            plate="ABC1234",
            year=2022,
        )

        assert vehicle.brand == "Toyota"
        assert vehicle.model == "Corolla"
        assert vehicle.status == VehicleStatus.ATIVO
        assert vehicle.is_blocked is False

    def test_vehicle_formatted_plate(self):
        """Testa formatação de placa."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            plate="ABC1D23",
        )

        formatted = vehicle.formatted_plate
        assert formatted == "ABC-1D23"

    def test_vehicle_formatted_plate_old_format(self):
        """Testa formatação de placa formato antigo."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            plate="ABC1234",
        )

        formatted = vehicle.formatted_plate
        assert formatted == "ABC-1234"

    def test_vehicle_is_active(self):
        """Testa propriedade is_active."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            plate="ABC1234",
        )

        assert vehicle.is_active is True

        vehicle.status = VehicleStatus.INATIVO
        assert vehicle.is_active is False

    def test_vehicle_is_valid_for_access(self):
        """Testa validação para acesso."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            plate="ABC1234",
        )

        assert vehicle.is_valid_for_access is True

        vehicle.is_blocked = True
        assert vehicle.is_valid_for_access is False

        vehicle.is_blocked = False
        vehicle.status = VehicleStatus.INATIVO
        assert vehicle.is_valid_for_access is False

    def test_vehicle_block(self):
        """Testa bloqueio de veículo."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            plate="ABC1234",
        )

        vehicle.block("Documentação irregular", "admin")

        assert vehicle.is_blocked is True
        assert vehicle.block_reason == "Documentação irregular"
        assert vehicle.blocked_by == "admin"
        assert vehicle.blocked_at is not None

    def test_vehicle_unblock(self):
        """Testa desbloqueio de veículo."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            plate="ABC1234",
        )

        vehicle.block("Teste", "admin")
        vehicle.unblock()

        assert vehicle.is_blocked is False
        assert vehicle.block_reason is None

    def test_vehicle_assign_parking_spot(self):
        """Testa atribuição de vaga."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            plate="ABC1234",
        )

        vehicle.assign_parking_spot("A-15")

        assert vehicle.parking_spot == "A-15"

    def test_vehicle_remove_parking_spot(self):
        """Testa remoção de vaga."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            plate="ABC1234",
            parking_spot="A-15",
        )

        vehicle.remove_parking_spot()

        assert vehicle.parking_spot is None

    def test_vehicle_mark_as_sold(self):
        """Testa marcação como vendido."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            plate="ABC1234",
            parking_spot="A-15",
        )

        vehicle.mark_as_sold()

        assert vehicle.status == VehicleStatus.VENDIDO
        assert vehicle.parking_spot is None
        assert vehicle.deactivation_date is not None

    def test_vehicle_mark_as_stolen(self):
        """Testa marcação como roubado."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            plate="ABC1234",
        )

        vehicle.mark_as_stolen("BO-12345")

        assert vehicle.status == VehicleStatus.ROUBADO
        assert vehicle.is_blocked is True
        assert "BO-12345" in vehicle.block_reason

    def test_vehicle_full_description(self):
        """Testa descrição completa."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            brand="Toyota",
            model="Corolla",
            color="Prata",
            plate="ABC1234",
            year=2022,
        )

        description = vehicle.full_description
        assert "Toyota" in description
        assert "Corolla" in description
        assert "Prata" in description
        assert "2022" in description

    def test_vehicle_deactivate(self):
        """Testa desativação."""
        vehicle = ResidentVehicle(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            vehicle_type=VehicleType.CARRO,
            plate="ABC1234",
        )

        vehicle.deactivate()

        assert vehicle.status == VehicleStatus.INATIVO
        assert vehicle.deactivation_date is not None


class TestVehicleEnums:
    """Testes para enums de Vehicle."""

    def test_vehicle_type_values(self):
        """Testa valores de VehicleType."""
        assert VehicleType.CARRO.value == "carro"
        assert VehicleType.MOTO.value == "moto"
        assert VehicleType.CAMINHONETE.value == "caminhonete"
        assert VehicleType.SUV.value == "suv"
        assert VehicleType.VAN.value == "van"
        assert VehicleType.BICICLETA.value == "bicicleta"
        assert VehicleType.PATINETE.value == "patinete"
        assert VehicleType.OUTRO.value == "outro"

    def test_vehicle_status_values(self):
        """Testa valores de VehicleStatus."""
        assert VehicleStatus.ATIVO.value == "ativo"
        assert VehicleStatus.INATIVO.value == "inativo"
        assert VehicleStatus.MANUTENCAO.value == "manutencao"
        assert VehicleStatus.VENDIDO.value == "vendido"
        assert VehicleStatus.ROUBADO.value == "roubado"

    def test_fuel_type_values(self):
        """Testa valores de FuelType."""
        assert FuelType.GASOLINA.value == "gasolina"
        assert FuelType.ETANOL.value == "etanol"
        assert FuelType.FLEX.value == "flex"
        assert FuelType.DIESEL.value == "diesel"
        assert FuelType.ELETRICO.value == "eletrico"
        assert FuelType.HIBRIDO.value == "hibrido"
        assert FuelType.GNV.value == "gnv"
