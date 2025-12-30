"""Testes para ResidentPet Model."""

import pytest
from datetime import date, datetime, timedelta
from uuid import uuid4

from modules.residents.models.pet import (
    ResidentPet,
    PetType,
    PetSize,
    PetStatus,
)


class TestResidentPetModel:
    """Testes para o modelo ResidentPet."""

    def test_create_pet(self):
        """Testa criação de pet."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
            breed="Labrador",
            color="Caramelo",
            size=PetSize.GRANDE,
        )

        assert pet.name == "Rex"
        assert pet.pet_type == PetType.CACHORRO
        assert pet.status == PetStatus.ATIVO
        assert pet.is_vaccinated is False

    def test_pet_is_active(self):
        """Testa propriedade is_active."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
        )

        assert pet.is_active is True

        pet.status = PetStatus.INATIVO
        assert pet.is_active is False

    def test_pet_age(self):
        """Testa cálculo de idade."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
            birth_date=date.today() - timedelta(days=365 * 3),
        )

        assert pet.age == 3

    def test_pet_age_months(self):
        """Testa cálculo de idade em meses."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
            birth_date=date.today() - timedelta(days=180),
        )

        assert pet.age_months == 6

    def test_pet_age_none(self):
        """Testa idade quando sem data de nascimento."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
        )

        assert pet.age is None
        assert pet.age_months is None

    def test_pet_update_vaccination(self):
        """Testa atualização de vacinação."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
        )

        vaccination_date = date.today()
        expiry_date = date.today() + timedelta(days=365)

        pet.update_vaccination(vaccination_date, expiry_date)

        assert pet.is_vaccinated is True
        assert pet.vaccination_date == vaccination_date
        assert pet.vaccination_expiry == expiry_date

    def test_pet_vaccination_status_not_vaccinated(self):
        """Testa status de vacinação - não vacinado."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
            is_vaccinated=False,
        )

        assert pet.vaccination_status == "Não vacinado"

    def test_pet_vaccination_status_valid(self):
        """Testa status de vacinação - válido."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
            is_vaccinated=True,
            vaccination_expiry=date.today() + timedelta(days=100),
        )

        assert pet.vaccination_status == "Em dia"

    def test_pet_vaccination_status_expiring(self):
        """Testa status de vacinação - expirando."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
            is_vaccinated=True,
            vaccination_expiry=date.today() + timedelta(days=20),
        )

        assert pet.vaccination_status == "Expirando"

    def test_pet_vaccination_status_expired(self):
        """Testa status de vacinação - expirado."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
            is_vaccinated=True,
            vaccination_expiry=date.today() - timedelta(days=10),
        )

        assert pet.vaccination_status == "Vencida"

    def test_pet_restrict_areas(self):
        """Testa restrição de áreas."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
            can_use_common_areas=True,
            allowed_areas=["piscina", "quadra", "jardim"],
        )

        pet.restrict_areas(["piscina", "quadra"])

        assert "piscina" not in pet.allowed_areas
        assert "quadra" not in pet.allowed_areas
        assert "jardim" in pet.allowed_areas

    def test_pet_allow_areas(self):
        """Testa permissão de áreas."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
            allowed_areas=["jardim"],
        )

        pet.allow_areas(["piscina", "quadra"])

        assert "piscina" in pet.allowed_areas
        assert "quadra" in pet.allowed_areas
        assert "jardim" in pet.allowed_areas

    def test_pet_deactivate(self):
        """Testa desativação."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
        )

        pet.deactivate()

        assert pet.status == PetStatus.INATIVO
        assert pet.deactivation_date is not None

    def test_pet_mark_as_deceased(self):
        """Testa marcação como falecido."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
        )

        pet.mark_as_deceased()

        assert pet.status == PetStatus.FALECIDO
        assert pet.deactivation_date is not None

    def test_pet_mark_as_donated(self):
        """Testa marcação como doado."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
        )

        pet.mark_as_donated()

        assert pet.status == PetStatus.DOADO
        assert pet.deactivation_date is not None

    def test_pet_mark_as_lost(self):
        """Testa marcação como perdido."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
        )

        pet.mark_as_lost()

        assert pet.status == PetStatus.PERDIDO

    def test_pet_full_description(self):
        """Testa descrição completa."""
        pet = ResidentPet(
            resident_id=uuid4(),
            condominium_id=str(uuid4()),
            name="Rex",
            pet_type=PetType.CACHORRO,
            breed="Labrador",
            color="Caramelo",
            size=PetSize.GRANDE,
        )

        description = pet.full_description
        assert "Rex" in description
        assert "Cachorro" in description
        assert "Labrador" in description


class TestPetEnums:
    """Testes para enums de Pet."""

    def test_pet_type_values(self):
        """Testa valores de PetType."""
        assert PetType.CACHORRO.value == "cachorro"
        assert PetType.GATO.value == "gato"
        assert PetType.PASSARO.value == "passaro"
        assert PetType.PEIXE.value == "peixe"
        assert PetType.ROEDOR.value == "roedor"
        assert PetType.REPTIL.value == "reptil"
        assert PetType.COELHO.value == "coelho"
        assert PetType.TARTARUGA.value == "tartaruga"
        assert PetType.OUTRO.value == "outro"

    def test_pet_size_values(self):
        """Testa valores de PetSize."""
        assert PetSize.MINI.value == "mini"
        assert PetSize.PEQUENO.value == "pequeno"
        assert PetSize.MEDIO.value == "medio"
        assert PetSize.GRANDE.value == "grande"
        assert PetSize.GIGANTE.value == "gigante"

    def test_pet_status_values(self):
        """Testa valores de PetStatus."""
        assert PetStatus.ATIVO.value == "ativo"
        assert PetStatus.INATIVO.value == "inativo"
        assert PetStatus.FALECIDO.value == "falecido"
        assert PetStatus.DOADO.value == "doado"
        assert PetStatus.PERDIDO.value == "perdido"
