"""Testes para o modelo Equipment."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Adicionar path do backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.equipment_management.models.equipment import (
    Equipment,
    EquipmentCategory,
    EquipmentStatus,
    EquipmentType,
)


class TestEquipmentModel:
    """Testes para o modelo Equipment."""

    def test_create_equipment(self):
        """Testa criação de equipamento."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="DS-2CD2143G2-IS",
            name="Câmera IP 4MP",
        )

        assert equipment.equipment_type == EquipmentType.CAMERA_IP
        assert equipment.category == EquipmentCategory.ELETRONICO
        assert equipment.brand == "Hikvision"
        assert equipment.status == EquipmentStatus.NOVO
        assert equipment.is_active is True

    def test_equipment_code_generation(self):
        """Testa geração de código do equipamento."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="DS-2CD2143G2-IS",
            name="Câmera IP 4MP",
        )

        assert equipment.equipment_code is not None
        assert equipment.equipment_code.startswith("EQ-")

    def test_install_equipment(self):
        """Testa instalação de equipamento."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="Test",
            name="Test Camera",
        )

        equipment.install(
            client_id="client-001",
            client_name="Cliente Teste",
            location="Entrada Principal",
            latitude=-23.5505,
            longitude=-46.6333,
        )

        assert equipment.status == EquipmentStatus.NOVO
        assert equipment.client_id == "client-001"
        assert equipment.installed_at is not None
        assert equipment.is_installed is True

    def test_uninstall_equipment(self):
        """Testa desinstalação de equipamento."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="Test",
            name="Test Camera",
        )

        equipment.install(client_id="client-001", client_name="Cliente Teste")
        equipment.uninstall()

        assert equipment.status == EquipmentStatus.NOVO
        assert equipment.client_id is None
        assert equipment.is_installed is False

    def test_set_online_offline(self):
        """Testa atualização de status online/offline."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="Test",
            name="Test Camera",
        )

        equipment.set_online()
        assert equipment.is_online is True
        assert equipment.last_online_at is not None

        equipment.set_offline()
        assert equipment.is_online is False
        assert equipment.last_offline_at is not None

    def test_send_to_maintenance(self):
        """Testa envio para manutenção."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="Test",
            name="Test Camera",
        )

        equipment.send_to_maintenance()
        assert equipment.status == EquipmentStatus.MANUTENCAO

    def test_return_from_maintenance(self):
        """Testa retorno de manutenção."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="Test",
            name="Test Camera",
        )

        equipment.send_to_maintenance()
        equipment.return_from_maintenance()

        assert equipment.status == EquipmentStatus.NOVO

    def test_mark_defective(self):
        """Testa marcação como defeituoso."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="Test",
            name="Test Camera",
        )

        equipment.mark_defective()
        assert equipment.status == EquipmentStatus.NOVO

    def test_decommission(self):
        """Testa baixa de equipamento."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="Test",
            name="Test Camera",
        )

        equipment.decommission()

        assert equipment.status == EquipmentStatus.NOVO
        assert equipment.is_active is False

    def test_is_in_warranty(self):
        """Testa verificação de garantia."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="Test",
            name="Test Camera",
            warranty_end=datetime.utcnow() + timedelta(days=365),
        )

        assert equipment.is_in_warranty is True

        # Garantia expirada
        equipment.warranty_end = datetime.utcnow() - timedelta(days=1)
        assert equipment.is_in_warranty is False

    def test_needs_maintenance(self):
        """Testa verificação de necessidade de manutenção."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="Test",
            name="Test Camera",
            next_maintenance_at=datetime.utcnow() - timedelta(days=1),
        )

        assert equipment.needs_maintenance is True

        # Manutenção futura
        equipment.next_maintenance_at = datetime.utcnow() + timedelta(days=30)
        assert equipment.needs_maintenance is False

    def test_calculate_depreciation(self):
        """Testa cálculo de depreciação."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="Test",
            name="Test Camera",
            purchase_date=datetime.utcnow() - timedelta(days=365),
            purchase_value=1000.0,
            depreciation_rate=20.0,
        )

        current_value = equipment.calculate_depreciation()

        assert current_value is not None
        assert current_value < 1000.0
        assert current_value == equipment.current_value

    def test_days_until_warranty_end(self):
        """Testa dias até fim da garantia."""
        equipment = Equipment(
            equipment_type=EquipmentType.CAMERA_IP,
            category=EquipmentCategory.ELETRONICO,
            brand="Hikvision",
            model="Test",
            name="Test Camera",
            warranty_end=datetime.utcnow() + timedelta(days=30),
        )

        days = equipment.days_until_warranty_end
        assert days is not None
        assert 29 <= days <= 31

    def test_all_equipment_types(self):
        """Testa todos os tipos de equipamento."""
        types = [
            EquipmentType.CAMERA_IP,
            EquipmentType.DVR,
            EquipmentType.NVR,
            EquipmentType.ALARME_CENTRAL,
            EquipmentType.SENSOR_MOVIMENTO,
            EquipmentType.CAMERA_IP,
            EquipmentType.SENSOR_FUMACA,
            EquipmentType.CATRACA,
            EquipmentType.PORTAO_AUTOMATICO,
            EquipmentType.LEITOR_BIOMETRICO,
            EquipmentType.CAMERA_IP,
            EquipmentType.CAMERA_IP,
            EquipmentType.CAMERA_IP,
            EquipmentType.CAMERA_IP,
            EquipmentType.CERCA_ELETRICA,
            EquipmentType.CONCERTINA,
            EquipmentType.CAMERA_IP,
            EquipmentType.INTERFONE,
            EquipmentType.VIDEOPORTEIRO,
            EquipmentType.CAMERA_IP,
            EquipmentType.ROTEADOR,
            EquipmentType.NOBREAK,
            EquipmentType.OUTRO,
        ]

        for eq_type in types:
            equipment = Equipment(
                equipment_type=eq_type,
                category=EquipmentCategory.ELETRONICO,
                brand="Test",
                model="Test",
                name=f"Equipment {eq_type.value}",
            )
            assert equipment.equipment_type == eq_type

    def test_all_categories(self):
        """Testa todas as categorias."""
        categories = [
            EquipmentCategory.ELETRONICO,
            EquipmentCategory.ELETRONICO,
            EquipmentCategory.ELETRONICO,
            EquipmentCategory.ELETRONICO,
            EquipmentCategory.ELETRONICO,
            EquipmentCategory.COMUNICACAO,
            EquipmentCategory.ELETRONICO,
        ]

        for category in categories:
            equipment = Equipment(
                equipment_type=EquipmentType.OUTRO,
                category=category,
                brand="Test",
                model="Test",
                name=f"Equipment {category.value}",
            )
            assert equipment.category == category
