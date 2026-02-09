"""
Testes do PDFGenerator.

Testa geracao de HTML e PDF para propostas comerciais,
formatacao de valores e renderizacao de templates.
"""

import tempfile
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

from modules.crm.services.pdf_generator import (
    ClientInfo,
    CompanyInfo,
    PDFGenerator,
    ProposalData,
    ProposalItem,
)


class TestPDFGeneratorDataclasses:
    """Testes das dataclasses."""

    def test_company_info_creation(self) -> None:
        """Testa criacao de CompanyInfo."""
        company = CompanyInfo(
            name="Empresa Teste",
            cnpj="00.000.000/0001-00",
            address="Rua Teste, 123",
            city="Sao Paulo",
            state="SP",
            zip_code="01234-567",
            phone="(11) 1234-5678",
            email="contato@empresa.com",
            website="www.empresa.com",
        )

        assert company.name == "Empresa Teste"
        assert company.cnpj == "00.000.000/0001-00"
        assert company.logo_path is None

    def test_company_info_with_logo(self) -> None:
        """Testa CompanyInfo com logo."""
        company = CompanyInfo(
            name="Empresa Teste",
            cnpj="00.000.000/0001-00",
            address="Rua Teste, 123",
            city="Sao Paulo",
            state="SP",
            zip_code="01234-567",
            phone="(11) 1234-5678",
            email="contato@empresa.com",
            website="www.empresa.com",
            logo_path="/path/to/logo.png",
        )

        assert company.logo_path == "/path/to/logo.png"

    def test_client_info_creation(self) -> None:
        """Testa criacao de ClientInfo."""
        client = ClientInfo(
            name="Cliente Teste",
            document="11.111.111/0001-11",
            contact_name="Joao Silva",
            email="joao@cliente.com",
        )

        assert client.name == "Cliente Teste"
        assert client.phone is None
        assert client.address is None

    def test_client_info_full(self) -> None:
        """Testa ClientInfo completo."""
        client = ClientInfo(
            name="Cliente Teste",
            document="11.111.111/0001-11",
            contact_name="Joao Silva",
            email="joao@cliente.com",
            phone="(11) 9876-5432",
            address="Av. Principal, 456",
        )

        assert client.phone == "(11) 9876-5432"
        assert client.address == "Av. Principal, 456"

    def test_proposal_item_creation(self) -> None:
        """Testa criacao de ProposalItem."""
        item = ProposalItem(
            description="Servico de Vigilancia",
            quantity=5,
            unit="un",
            unit_price=Decimal("2000.00"),
            discount_percent=Decimal("0.00"),
            total=Decimal("10000.00"),
        )

        assert item.description == "Servico de Vigilancia"
        assert item.quantity == 5
        assert item.details is None

    def test_proposal_item_with_details(self) -> None:
        """Testa ProposalItem com detalhes."""
        item = ProposalItem(
            description="Servico de Vigilancia",
            quantity=5,
            unit="un",
            unit_price=Decimal("2000.00"),
            discount_percent=Decimal("10.00"),
            total=Decimal("9000.00"),
            details="24 horas, armado",
        )

        assert item.details == "24 horas, armado"


class TestPDFGeneratorBasic:
    """Testes basicos do PDFGenerator."""

    @pytest.fixture
    def generator(self) -> PDFGenerator:
        """Fixture do generator."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield PDFGenerator(output_dir=Path(tmp_dir))

    @pytest.fixture
    def sample_company(self) -> CompanyInfo:
        """Fixture de empresa."""
        return CompanyInfo(
            name="Empresa Modelo LTDA",
            cnpj="12.345.678/0001-90",
            address="Rua das Empresas, 100",
            city="Sao Paulo",
            state="SP",
            zip_code="01000-000",
            phone="(11) 3000-0000",
            email="contato@empresa.com.br",
            website="www.empresa.com.br",
        )

    @pytest.fixture
    def sample_client(self) -> ClientInfo:
        """Fixture de cliente."""
        return ClientInfo(
            name="Cliente Exemplo S.A.",
            document="98.765.432/0001-10",
            contact_name="Maria Santos",
            email="maria@cliente.com.br",
            phone="(11) 4000-0000",
        )

    @pytest.fixture
    def sample_items(self) -> list[ProposalItem]:
        """Fixture de itens."""
        return [
            ProposalItem(
                description="Vigilante Diurno",
                quantity=2,
                unit="posto",
                unit_price=Decimal("5000.00"),
                discount_percent=Decimal("0.00"),
                total=Decimal("10000.00"),
            ),
            ProposalItem(
                description="Vigilante Noturno",
                quantity=2,
                unit="posto",
                unit_price=Decimal("6000.00"),
                discount_percent=Decimal("5.00"),
                total=Decimal("11400.00"),
            ),
        ]

    @pytest.fixture
    def sample_proposal(
        self,
        sample_company: CompanyInfo,
        sample_client: ClientInfo,
        sample_items: list[ProposalItem],
    ) -> ProposalData:
        """Fixture de proposta."""
        return ProposalData(
            number="PRO-2026-00001",
            version=1,
            issue_date=date.today(),
            valid_until=date.today() + timedelta(days=30),
            company=sample_company,
            client=sample_client,
            items=sample_items,
            subtotal=Decimal("22000.00"),
            discount_value=Decimal("600.00"),
            taxes=Decimal("3000.00"),
            total=Decimal("24400.00"),
        )

    def test_instance_creation(self, generator: PDFGenerator) -> None:
        """Testa criacao de instancia."""
        assert generator is not None
        assert generator.output_dir.exists()

    def test_generate_preview_returns_html(self, generator: PDFGenerator, sample_proposal: ProposalData) -> None:
        """Testa que preview retorna HTML."""
        html = generator.generate_preview(sample_proposal)

        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert sample_proposal.number in html

    def test_html_contains_company_info(self, generator: PDFGenerator, sample_proposal: ProposalData) -> None:
        """Testa que HTML contem info da empresa."""
        html = generator.generate_preview(sample_proposal)

        assert sample_proposal.company.name in html
        assert sample_proposal.company.cnpj in html
        assert sample_proposal.company.phone in html

    def test_html_contains_client_info(self, generator: PDFGenerator, sample_proposal: ProposalData) -> None:
        """Testa que HTML contem info do cliente."""
        html = generator.generate_preview(sample_proposal)

        assert sample_proposal.client.name in html
        assert sample_proposal.client.document in html
        assert sample_proposal.client.contact_name in html

    def test_html_contains_items(self, generator: PDFGenerator, sample_proposal: ProposalData) -> None:
        """Testa que HTML contem itens."""
        html = generator.generate_preview(sample_proposal)

        for item in sample_proposal.items:
            assert item.description in html

    def test_html_contains_totals(self, generator: PDFGenerator, sample_proposal: ProposalData) -> None:
        """Testa que HTML contem totais."""
        html = generator.generate_preview(sample_proposal)

        assert "Subtotal" in html
        assert "TOTAL" in html


class TestPDFGeneratorFormatting:
    """Testes de formatacao."""

    @pytest.fixture
    def generator(self) -> PDFGenerator:
        """Fixture do generator."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield PDFGenerator(output_dir=Path(tmp_dir))

    def test_format_currency(self, generator: PDFGenerator) -> None:
        """Testa formatacao de moeda."""
        # Acessar metodo interno para teste
        formatted = generator._format_currency(  # pylint: disable=protected-access
            Decimal("1234.56")
        )
        assert formatted == "R$ 1.234,56"

    def test_format_currency_large_value(self, generator: PDFGenerator) -> None:
        """Testa formatacao de valor grande."""
        formatted = generator._format_currency(  # pylint: disable=protected-access
            Decimal("1234567.89")
        )
        assert formatted == "R$ 1.234.567,89"

    def test_format_currency_small_value(self, generator: PDFGenerator) -> None:
        """Testa formatacao de valor pequeno."""
        formatted = generator._format_currency(Decimal("99.00"))  # pylint: disable=protected-access
        assert formatted == "R$ 99,00"

    def test_days_until_future(self, generator: PDFGenerator) -> None:
        """Testa calculo de dias ate data futura."""
        future = date.today() + timedelta(days=15)
        days = generator._days_until(future)  # pylint: disable=protected-access
        assert days == 15

    def test_days_until_past(self, generator: PDFGenerator) -> None:
        """Testa calculo de dias ate data passada."""
        past = date.today() - timedelta(days=5)
        days = generator._days_until(past)  # pylint: disable=protected-access
        assert days == 0  # Retorna 0 para datas passadas


class TestPDFGeneratorRendering:
    """Testes de renderizacao de componentes."""

    @pytest.fixture
    def generator(self) -> PDFGenerator:
        """Fixture do generator."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield PDFGenerator(output_dir=Path(tmp_dir))

    def test_render_optional_row_with_value(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de linha opcional com valor."""
        html = generator._render_optional_row(  # pylint: disable=protected-access
            "Telefone:", "(11) 1234-5678"
        )
        assert "Telefone:" in html
        assert "(11) 1234-5678" in html

    def test_render_optional_row_without_value(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de linha opcional sem valor."""
        html = generator._render_optional_row("Telefone:", None)  # pylint: disable=protected-access
        assert html == ""

    def test_render_introduction_with_text(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de introducao com texto."""
        html = generator._render_introduction(  # pylint: disable=protected-access
            "Texto de apresentacao"
        )
        assert "Apresentação" in html
        assert "Texto de apresentacao" in html

    def test_render_introduction_empty(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de introducao vazia."""
        html = generator._render_introduction(None)  # pylint: disable=protected-access
        assert html == ""

    def test_render_discount_row_with_value(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de linha de desconto."""
        html = generator._render_discount_row(  # pylint: disable=protected-access
            Decimal("100.00"), "R$ 100,00"
        )
        assert "Desconto" in html
        assert "-R$ 100,00" in html

    def test_render_discount_row_zero(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de desconto zero."""
        html = generator._render_discount_row(  # pylint: disable=protected-access
            Decimal("0.00"), "R$ 0,00"
        )
        assert html == ""

    def test_render_taxes_row_with_value(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de linha de impostos."""
        html = generator._render_taxes_row(  # pylint: disable=protected-access
            Decimal("500.00"), "R$ 500,00"
        )
        assert "Impostos" in html
        assert "R$ 500,00" in html

    def test_render_taxes_row_zero(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de impostos zero."""
        html = generator._render_taxes_row(  # pylint: disable=protected-access
            Decimal("0.00"), "R$ 0,00"
        )
        assert html == ""

    def test_render_cct_row_with_value(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de linha CCT."""
        html = generator._render_cct_row(Decimal("1500.00"))  # pylint: disable=protected-access
        assert "Encargos (CCT)" in html
        assert "R$ 1.500,00" in html

    def test_render_cct_row_none(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de CCT None."""
        html = generator._render_cct_row(None)  # pylint: disable=protected-access
        assert html == ""

    def test_render_payment_terms(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de condicoes de pagamento."""
        html = generator._render_payment_terms("30/60/90 dias")  # pylint: disable=protected-access
        assert "Condições de Pagamento" in html
        assert "30/60/90 dias" in html

    def test_render_terms(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de termos e condicoes."""
        html = generator._render_terms("Termos de contrato")  # pylint: disable=protected-access
        assert "Termos e Condições" in html
        assert "Termos de contrato" in html

    def test_render_notes(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de observacoes."""
        html = generator._render_notes("Nota importante")  # pylint: disable=protected-access
        assert "Observações" in html
        assert "Nota importante" in html


class TestPDFGeneratorItems:
    """Testes de renderizacao de itens."""

    @pytest.fixture
    def generator(self) -> PDFGenerator:
        """Fixture do generator."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield PDFGenerator(output_dir=Path(tmp_dir))

    def test_render_items_single(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de item unico."""
        items = [
            ProposalItem(
                description="Servico de Teste",
                quantity=1,
                unit="un",
                unit_price=Decimal("1000.00"),
                discount_percent=Decimal("0.00"),
                total=Decimal("1000.00"),
            ),
        ]

        html = generator._render_items(items)  # pylint: disable=protected-access

        assert "Servico de Teste" in html
        assert "R$ 1.000,00" in html

    def test_render_items_with_discount(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de item com desconto."""
        items = [
            ProposalItem(
                description="Servico com Desconto",
                quantity=1,
                unit="un",
                unit_price=Decimal("1000.00"),
                discount_percent=Decimal("10.00"),
                total=Decimal("900.00"),
            ),
        ]

        html = generator._render_items(items)  # pylint: disable=protected-access

        assert "10.00%" in html  # Desconto exibido com formatacao Decimal

    def test_render_items_with_details(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de item com detalhes."""
        items = [
            ProposalItem(
                description="Servico com Detalhes",
                quantity=1,
                unit="un",
                unit_price=Decimal("1000.00"),
                discount_percent=Decimal("0.00"),
                total=Decimal("1000.00"),
                details="Detalhes do servico",
            ),
        ]

        html = generator._render_items(items)  # pylint: disable=protected-access

        assert "Detalhes do servico" in html

    def test_render_items_empty_list(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de lista vazia."""
        items: list[ProposalItem] = []

        html = generator._render_items(items)  # pylint: disable=protected-access

        assert html == ""


class TestPDFGeneratorLogo:
    """Testes de renderizacao de logo."""

    @pytest.fixture
    def generator(self) -> PDFGenerator:
        """Fixture do generator."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield PDFGenerator(output_dir=Path(tmp_dir))

    def test_render_logo_placeholder(self, generator: PDFGenerator) -> None:
        """Testa renderizacao de placeholder quando nao tem logo."""
        html = generator._render_logo(None)  # pylint: disable=protected-access

        assert "LOGO" in html

    def test_render_logo_file_not_exists(self, generator: PDFGenerator) -> None:
        """Testa renderizacao quando arquivo nao existe."""
        html = generator._render_logo(  # pylint: disable=protected-access
            "/path/that/does/not/exist.png"
        )

        assert "LOGO" in html  # Usa placeholder


class TestPDFGeneratorGenerate:
    """Testes de geracao de PDF."""

    @pytest.fixture
    def generator(self) -> PDFGenerator:
        """Fixture do generator."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield PDFGenerator(output_dir=Path(tmp_dir))

    @pytest.fixture
    def sample_proposal(self) -> ProposalData:
        """Fixture de proposta minima."""
        return ProposalData(
            number="PRO-2026-00001",
            version=1,
            issue_date=date.today(),
            valid_until=date.today() + timedelta(days=30),
            company=CompanyInfo(
                name="Empresa",
                cnpj="00.000.000/0001-00",
                address="Rua A",
                city="SP",
                state="SP",
                zip_code="00000-000",
                phone="(00) 0000-0000",
                email="a@b.com",
                website="www.b.com",
            ),
            client=ClientInfo(
                name="Cliente",
                document="11.111.111/0001-11",
                contact_name="Nome",
                email="x@y.com",
            ),
            items=[
                ProposalItem(
                    description="Item",
                    quantity=1,
                    unit="un",
                    unit_price=Decimal("100.00"),
                    discount_percent=Decimal("0.00"),
                    total=Decimal("100.00"),
                ),
            ],
            subtotal=Decimal("100.00"),
            discount_value=Decimal("0.00"),
            taxes=Decimal("0.00"),
            total=Decimal("100.00"),
        )

    def test_generate_creates_file(self, generator: PDFGenerator, sample_proposal: ProposalData) -> None:
        """Testa que generate cria arquivo."""
        # Mock para evitar dependencia de WeasyPrint
        with patch.object(generator, "_html_to_pdf") as mock_pdf:
            mock_pdf.return_value = None

            result = generator.generate(sample_proposal)

            assert "proposta_PRO_2026_00001_v1" in result
            mock_pdf.assert_called_once()

    def test_generate_with_all_optional_fields(self, generator: PDFGenerator) -> None:
        """Testa geracao com todos os campos opcionais."""
        proposal = ProposalData(
            number="PRO-2026-00002",
            version=2,
            issue_date=date.today(),
            valid_until=date.today() + timedelta(days=60),
            company=CompanyInfo(
                name="Empresa Completa",
                cnpj="12.345.678/0001-90",
                address="Rua Completa, 100",
                city="Sao Paulo",
                state="SP",
                zip_code="01234-567",
                phone="(11) 1234-5678",
                email="contato@completa.com",
                website="www.completa.com",
            ),
            client=ClientInfo(
                name="Cliente Completo",
                document="98.765.432/0001-10",
                contact_name="Joao Completo",
                email="joao@completo.com",
                phone="(11) 9876-5432",
                address="Av. Completa, 200",
            ),
            items=[
                ProposalItem(
                    description="Servico Completo",
                    quantity=5,
                    unit="meses",
                    unit_price=Decimal("5000.00"),
                    discount_percent=Decimal("10.00"),
                    total=Decimal("22500.00"),
                    details="Com detalhes",
                ),
            ],
            subtotal=Decimal("25000.00"),
            discount_value=Decimal("2500.00"),
            taxes=Decimal("3000.00"),
            total=Decimal("25500.00"),
            cct_value=Decimal("5000.00"),
            margin_percent=Decimal("15.00"),
            introduction="Introducao da proposta",
            terms="Termos e condicoes",
            payment_terms="30/60/90 dias",
            notes="Observacoes importantes",
            salesperson_name="Vendedor Silva",
            salesperson_email="vendedor@empresa.com",
        )

        html = generator.generate_preview(proposal)

        # Verificar campos opcionais
        assert "Introducao da proposta" in html
        assert "Termos e condicoes" in html
        assert "30/60/90 dias" in html
        assert "Observacoes importantes" in html
        assert "Vendedor Silva" in html
        assert "R$ 5.000,00" in html  # CCT


class TestPDFGeneratorCSS:
    """Testes de CSS."""

    def test_default_css_exists(self) -> None:
        """Testa que CSS padrao existe."""
        assert PDFGenerator.DEFAULT_CSS is not None
        assert len(PDFGenerator.DEFAULT_CSS) > 0

    def test_css_contains_page_rules(self) -> None:
        """Testa que CSS contem regras de pagina."""
        assert "@page" in PDFGenerator.DEFAULT_CSS
        assert "A4" in PDFGenerator.DEFAULT_CSS

    def test_css_contains_header_styles(self) -> None:
        """Testa que CSS contem estilos de cabecalho."""
        assert ".header" in PDFGenerator.DEFAULT_CSS

    def test_css_contains_table_styles(self) -> None:
        """Testa que CSS contem estilos de tabela."""
        assert "table.items" in PDFGenerator.DEFAULT_CSS

    def test_css_contains_totals_styles(self) -> None:
        """Testa que CSS contem estilos de totais."""
        assert ".totals" in PDFGenerator.DEFAULT_CSS
        assert ".grand-total" in PDFGenerator.DEFAULT_CSS
