"""Testes para o modelo Supplier."""

import uuid
from datetime import datetime

import pytest

from modules.financial.models.supplier import (
    PaymentTerms,
    Supplier,
    SupplierCategory,
    SupplierStatus,
    SupplierType,
)


class TestSupplierModel:
    """Testes para o modelo Supplier."""

    def test_create_supplier_pessoa_juridica(self):
        """Testa criação de fornecedor PJ."""
        supplier = Supplier(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="12.345.678/0001-90",
            name="Empresa Teste LTDA",
            trade_name="Empresa Teste",
            supplier_type=SupplierType.PESSOA_JURIDICA.value,
            category=SupplierCategory.MANUTENCAO.value,
            email="contato@empresa.com.br",
            status=SupplierStatus.ATIVO.value,
            ativo=True,
            is_blocked=False,
            is_qualified=False,
        )

        assert supplier.name == "Empresa Teste LTDA"
        assert supplier.supplier_type == SupplierType.PESSOA_JURIDICA.value
        assert supplier.status == SupplierStatus.ATIVO.value
        assert supplier.ativo is True
        assert supplier.is_blocked is False
        assert supplier.is_qualified is False

    def test_create_supplier_pessoa_fisica(self):
        """Testa criação de fornecedor PF."""
        supplier = Supplier(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="123.456.789-00",
            name="João da Silva",
            supplier_type=SupplierType.PESSOA_FISICA.value,
            category=SupplierCategory.SERVICOS.value,
        )

        assert supplier.name == "João da Silva"
        assert supplier.supplier_type == SupplierType.PESSOA_FISICA.value

    def test_block_supplier(self):
        """Testa bloqueio de fornecedor."""
        supplier = Supplier(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="12.345.678/0001-90",
            name="Empresa Teste LTDA",
            status=SupplierStatus.ATIVO.value,
            is_blocked=False,
            is_qualified=False,
            ativo=True,
        )
        user_id = uuid.uuid4()

        assert supplier.is_blocked is False

        supplier.block("Inadimplência", user_id)

        assert supplier.is_blocked is True
        assert supplier.blocked_reason == "Inadimplência"
        assert supplier.blocked_by == user_id
        assert supplier.blocked_at is not None
        assert supplier.status == SupplierStatus.BLOQUEADO.value

    def test_unblock_supplier(self):
        """Testa desbloqueio de fornecedor."""
        supplier = Supplier(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="12.345.678/0001-90",
            name="Empresa Teste LTDA",
            is_blocked=True,
            blocked_reason="Inadimplência",
            status=SupplierStatus.BLOQUEADO.value,
        )

        supplier.unblock()

        assert supplier.is_blocked is False
        assert supplier.blocked_reason is None
        assert supplier.blocked_by is None
        assert supplier.blocked_at is None
        assert supplier.status == SupplierStatus.ATIVO.value

    def test_qualify_supplier(self):
        """Testa qualificação de fornecedor."""
        supplier = Supplier(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="12.345.678/0001-90",
            name="Empresa Teste LTDA",
            status=SupplierStatus.ATIVO.value,
            is_blocked=False,
            is_qualified=False,
            ativo=True,
        )
        user_id = uuid.uuid4()

        assert supplier.is_qualified is False

        supplier.qualify(user_id)

        assert supplier.is_qualified is True
        assert supplier.qualified_by == user_id
        assert supplier.qualified_at is not None

    def test_supplier_payment_terms(self):
        """Testa condições de pagamento."""
        supplier = Supplier(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="12.345.678/0001-90",
            name="Empresa Teste LTDA",
            payment_terms=PaymentTerms.DIAS_30.value,
        )

        assert supplier.payment_terms == PaymentTerms.DIAS_30.value

    def test_supplier_bank_data(self):
        """Testa dados bancários do fornecedor."""
        supplier = Supplier(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="12.345.678/0001-90",
            name="Empresa Teste LTDA",
            bank_code="001",
            bank_name="Banco do Brasil",
            bank_agency="1234",
            bank_account="12345678",
            bank_account_type="corrente",
        )

        assert supplier.bank_code == "001"
        assert supplier.bank_name == "Banco do Brasil"
        assert supplier.bank_agency == "1234"
        assert supplier.bank_account == "12345678"

    def test_supplier_pix_data(self):
        """Testa dados PIX do fornecedor."""
        supplier = Supplier(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="12.345.678/0001-90",
            name="Empresa Teste LTDA",
            pix_key="12345678000190",
            pix_key_type="cnpj",
        )

        assert supplier.pix_key == "12345678000190"
        assert supplier.pix_key_type == "cnpj"

    def test_supplier_withholdings(self):
        """Testa configurações de retenções fiscais."""
        supplier = Supplier(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="12.345.678/0001-90",
            name="Empresa Teste LTDA",
            withhold_iss=True,
            withhold_ir=True,
        )

        assert supplier.withhold_iss is True
        assert supplier.withhold_ir is True

    def test_supplier_categories(self):
        """Testa todas as categorias de fornecedor."""
        categories = [
            SupplierCategory.MANUTENCAO,
            SupplierCategory.SEGURANCA,
            SupplierCategory.LIMPEZA,
            SupplierCategory.SERVICOS,
            SupplierCategory.MATERIAIS,
            SupplierCategory.TECNOLOGIA,
        ]

        for cat in categories:
            supplier = Supplier(
                condominio_id=uuid.uuid4(),
                cpf_cnpj="12.345.678/0001-90",
                name="Empresa Teste",
                category=cat.value,
            )
            assert supplier.category == cat.value

    def test_supplier_types(self):
        """Testa todos os tipos de fornecedor."""
        types = [
            SupplierType.PESSOA_FISICA,
            SupplierType.PESSOA_JURIDICA,
            SupplierType.MEI,
            SupplierType.EIRELI,
        ]

        for t in types:
            supplier = Supplier(
                condominio_id=uuid.uuid4(),
                cpf_cnpj="12.345.678/0001-90",
                name="Fornecedor Teste",
                supplier_type=t.value,
            )
            assert supplier.supplier_type == t.value

    def test_supplier_statuses(self):
        """Testa todos os status de fornecedor."""
        statuses = [
            SupplierStatus.ATIVO,
            SupplierStatus.INATIVO,
            SupplierStatus.BLOQUEADO,
            SupplierStatus.PENDENTE,
        ]

        for s in statuses:
            supplier = Supplier(
                condominio_id=uuid.uuid4(),
                cpf_cnpj="12.345.678/0001-90",
                name="Fornecedor Teste",
                status=s.value,
            )
            assert supplier.status == s.value
