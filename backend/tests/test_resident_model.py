"""Testes para Resident Model."""

import pytest
from datetime import date, datetime
from uuid import uuid4

from modules.residents.models.resident import (
    Resident,
    ResidentStatus,
    ResidentType,
    DocumentType,
    Gender,
    MaritalStatus,
    AccessMethod,
)


class TestResidentModel:
    """Testes para o modelo Resident."""

    def test_create_resident(self):
        """Testa criação de morador."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
            cpf="12345678901",
            email="joao@email.com",
            phone="11999999999",
        )

        assert resident.name == "João Silva"
        assert resident.status == ResidentStatus.ATIVO
        assert resident.resident_type == ResidentType.PROPRIETARIO
        assert resident.is_blocked is False
        assert resident.is_defaulter is False

    def test_resident_is_active(self):
        """Testa propriedade is_active."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        assert resident.is_active is True

        resident.status = ResidentStatus.INATIVO
        assert resident.is_active is False

        resident.status = ResidentStatus.ATIVO
        resident.deleted_at = datetime.utcnow()
        assert resident.is_active is False

    def test_resident_block(self):
        """Testa bloqueio de morador."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        resident.block("Inadimplência", "admin")

        assert resident.is_blocked is True
        assert resident.block_reason == "Inadimplência"
        assert resident.blocked_by == "admin"
        assert resident.blocked_at is not None

    def test_resident_unblock(self):
        """Testa desbloqueio de morador."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        resident.block("Teste", "admin")
        resident.unblock()

        assert resident.is_blocked is False
        assert resident.block_reason is None
        assert resident.blocked_by is None
        assert resident.blocked_at is None

    def test_resident_set_defaulter(self):
        """Testa marcação de inadimplência."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        resident.set_defaulter(1500.00)

        assert resident.is_defaulter is True
        assert resident.debt_amount == 1500.00
        assert resident.defaulter_since is not None

    def test_resident_clear_defaulter(self):
        """Testa remoção de inadimplência."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        resident.set_defaulter(1500.00)
        resident.clear_defaulter()

        assert resident.is_defaulter is False
        assert resident.debt_amount == 0.0
        assert resident.defaulter_since is None

    def test_resident_move_out(self):
        """Testa mudança de morador."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        move_date = date(2024, 12, 31)
        resident.move_out(move_date)

        assert resident.status == ResidentStatus.MUDANCA
        assert resident.move_out_date == move_date

    def test_resident_age(self):
        """Testa cálculo de idade."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
            birth_date=date(1990, 1, 15),
        )

        age = resident.age
        assert age is not None
        assert age >= 34  # Considerando data atual

    def test_resident_age_none(self):
        """Testa idade quando sem data de nascimento."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        assert resident.age is None

    def test_resident_has_biometric(self):
        """Testa propriedade has_biometric."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        assert resident.has_biometric is False

        resident.fingerprint_id = "FP123"
        assert resident.has_biometric is True

    def test_resident_has_access_card(self):
        """Testa propriedade has_access_card."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        assert resident.has_access_card is False

        resident.access_card_number = "CARD123"
        assert resident.has_access_card is True

    def test_resident_display_name(self):
        """Testa display_name."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        assert resident.display_name == "João Silva"

        resident.social_name = "João S."
        assert resident.display_name == "João S."

    def test_resident_full_address(self):
        """Testa full_address."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
            block="A",
            street="Rua das Flores",
            number="100",
            complement="Apto 101",
            neighborhood="Centro",
            city="São Paulo",
            state="SP",
            zip_code="01234-567",
        )

        address = resident.full_address
        assert "Rua das Flores" in address
        assert "100" in address
        assert "São Paulo" in address

    def test_resident_enable_access_method(self):
        """Testa habilitação de método de acesso."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        resident.enable_access_method(AccessMethod.BIOMETRIA, "FP123")
        assert resident.fingerprint_id == "FP123"

        resident.enable_access_method(AccessMethod.CARTAO, "CARD123")
        assert resident.access_card_number == "CARD123"

        resident.enable_access_method(AccessMethod.FACIAL, "FACE123")
        assert resident.facial_id == "FACE123"

    def test_resident_disable_access_method(self):
        """Testa desabilitação de método de acesso."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
            fingerprint_id="FP123",
            access_card_number="CARD123",
        )

        resident.disable_access_method(AccessMethod.BIOMETRIA)
        assert resident.fingerprint_id is None

        resident.disable_access_method(AccessMethod.CARTAO)
        assert resident.access_card_number is None

    def test_resident_generate_qr_code(self):
        """Testa geração de QR Code."""
        resident = Resident(
            id=uuid4(),
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        qr_code = resident.generate_qr_code()
        assert qr_code is not None
        assert len(qr_code) > 0
        assert resident.qr_code == qr_code

    def test_resident_contract_status(self):
        """Testa status do contrato."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        # Sem contrato
        assert resident.contract_status == "sem_contrato"

        # Contrato ativo
        resident.contract_start_date = date(2024, 1, 1)
        resident.contract_end_date = date(2025, 12, 31)
        assert resident.contract_status == "ativo"

        # Contrato expirado
        resident.contract_end_date = date(2023, 12, 31)
        assert resident.contract_status == "expirado"

    def test_resident_is_valid(self):
        """Testa validação de morador."""
        resident = Resident(
            condominium_id=str(uuid4()),
            unit_id=str(uuid4()),
            unit_number="101",
            name="João Silva",
        )

        # Morador válido
        assert resident.is_valid is True

        # Morador bloqueado
        resident.is_blocked = True
        assert resident.is_valid is False

        # Morador inativo
        resident.is_blocked = False
        resident.status = ResidentStatus.INATIVO
        assert resident.is_valid is False


class TestResidentEnums:
    """Testes para enums de Resident."""

    def test_resident_status_values(self):
        """Testa valores de ResidentStatus."""
        assert ResidentStatus.ATIVO.value == "ativo"
        assert ResidentStatus.INATIVO.value == "inativo"
        assert ResidentStatus.SUSPENSO.value == "suspenso"
        assert ResidentStatus.PENDENTE.value == "pendente"
        assert ResidentStatus.BLOQUEADO.value == "bloqueado"
        assert ResidentStatus.MUDANCA.value == "mudanca"

    def test_resident_type_values(self):
        """Testa valores de ResidentType."""
        assert ResidentType.PROPRIETARIO.value == "proprietario"
        assert ResidentType.INQUILINO.value == "inquilino"
        assert ResidentType.COMODATARIO.value == "comodatario"
        assert ResidentType.FAMILIAR.value == "familiar"
        assert ResidentType.FUNCIONARIO_DOMESTICO.value == "funcionario_domestico"
        assert ResidentType.TEMPORARIO.value == "temporario"

    def test_access_method_values(self):
        """Testa valores de AccessMethod."""
        assert AccessMethod.BIOMETRIA.value == "biometria"
        assert AccessMethod.CARTAO.value == "cartao"
        assert AccessMethod.SENHA.value == "senha"
        assert AccessMethod.QR_CODE.value == "qr_code"
        assert AccessMethod.FACIAL.value == "facial"
        assert AccessMethod.CONTROLE.value == "controle"
        assert AccessMethod.APP.value == "app"
        assert AccessMethod.TAG_RFID.value == "tag_rfid"
