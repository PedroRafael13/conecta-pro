"""
Testes do modulo SST — Saude e Seguranca do Trabalho.

Cobre: models, service, controller imports, CCT integration.
"""


class TestSSTModels:
    """Testes dos modelos SST."""

    def test_afastamento_model_import(self):
        from modules.people_management.sst.models.afastamento import (
            Afastamento,
            StatusAfastamento,
            TipoAfastamento,
        )

        assert Afastamento.__tablename__ == "sst_afastamentos"
        assert TipoAfastamento.DOENCA == "doenca"
        assert TipoAfastamento.ACIDENTE_TRABALHO == "acidente_trabalho"
        assert StatusAfastamento.ATIVO == "ativo"
        assert StatusAfastamento.ENCERRADO == "encerrado"

    def test_aso_model_import(self):
        from modules.people_management.sst.models.aso import ASOModel, ASOStatus, ASOType

        assert ASOModel.__tablename__ == "gp_asos"
        assert ASOType.ADMISSIONAL == "admissional"
        assert ASOType.PERIODICO == "periodico"
        assert ASOStatus.AGENDADO == "agendado"

    def test_cat_model_import(self):
        from modules.people_management.sst.models.cat import CATModel

        assert CATModel.__tablename__ == "gp_cats"

    def test_epi_model_import(self):
        from modules.people_management.sst.models.epi import EPIDeliveryModel

        assert EPIDeliveryModel.__tablename__ == "gp_epi_deliveries"

    def test_risk_model_import(self):
        from modules.people_management.sst.models.risk import RiskModel

        assert RiskModel.__tablename__ == "gp_risks"


class TestSSTSchemas:
    """Testes dos schemas SST."""

    def test_aso_create(self):
        from modules.people_management.sst.schemas.sst_schemas import ASOCreate

        aso = ASOCreate(employee_id="emp-uuid-1", tipo="periodico", data_agendamento="2026-04-01")
        assert aso.tipo == "periodico"

    def test_cat_create(self):
        from modules.people_management.sst.schemas.sst_schemas import CATCreate

        cat = CATCreate(
            employee_id="emp-uuid-1",
            tipo_acidente="tipico",
            data_acidente="2026-03-15",
            local="Posto A",
            descricao="Queda no piso escorregadio do hall",
        )
        assert cat.gravidade == "leve"

    def test_epi_create(self):
        from modules.people_management.sst.schemas.sst_schemas import EPIDeliveryCreate

        epi = EPIDeliveryCreate(employee_id="emp-uuid-1", epi_nome="Luva termica")
        assert epi.quantidade == 1

    def test_risk_create(self):
        from modules.people_management.sst.schemas.sst_schemas import RiskCreate

        risk = RiskCreate(posto_id="posto-uuid-1", categoria="ergonomico", descricao="Postura inadequada")
        assert risk.nivel == "medio"


class TestSSTService:
    """Testes da logica do service SST."""

    def test_service_import(self):
        from modules.people_management.sst.services.sst_service import SSTService

        assert SSTService is not None

    def test_cct_constants(self):
        from modules.people_management.sst.services.sst_service import (
            CCT_AJUDA_MEDICAMENTO_VALOR,
            CCT_ESTABILIDADE_MESES,
        )

        assert CCT_AJUDA_MEDICAMENTO_VALOR == 300.00
        assert CCT_ESTABILIDADE_MESES == 12


class TestSSTController:
    """Testes de importacao e rotas do controller."""

    def test_controller_import(self):
        from modules.people_management.sst.controllers.sst_controller import router

        assert router is not None

    def test_controller_has_all_routes(self):
        from modules.people_management.sst.controllers.sst_controller import router

        paths = [r.path for r in router.routes]
        # Dashboard e afastamentos
        assert "/sst/dashboard" in paths
        assert "/sst/afastamentos" in paths
        # NR-1
        assert "/sst/nr1/dashboard" in paths
        assert "/sst/nr1/colaboradores-risco" in paths
        # PCMSO/PPRA
        assert "/sst/pcmso/status" in paths
        assert "/sst/ppra/status" in paths
        # ASOs
        assert "/sst/asos/vencendo" in paths
        assert "/sst/asos/sem-aso" in paths
        assert "/sst/aso" in paths
        # CAT
        assert "/sst/cat" in paths
        assert "/sst/cat/taxa-acidente" in paths
        # CCT
        assert "/sst/estabilidade/ativos" in paths
        assert "/sst/ajuda-medicamento/ativos" in paths
        # CRUD originais preservados
        assert "/sst/epi" in paths
        assert "/sst/risco" in paths
        assert "/sst/riscos" in paths


class TestSSTCCTIntegration:
    """Testes de integracao CCT com SST."""

    def test_cct_estabilidade_validator(self):
        from modules.cct.validators.stability_validator import StabilityValidator

        result = StabilityValidator.verificar_estabilidade(
            employee_id="test",
            data_admissao="2024-01-01",
            acidente_trabalho=True,
            data_alta_inss="2026-01-01",
        )
        assert result["estavel"] is True
        assert any("Acidente" in m for m in result["motivos"])

    def test_cct_ajuda_medicamento_rule(self):
        from decimal import Decimal

        from modules.cct.models.benefits import TipoBeneficioCCT, get_beneficio_by_tipo

        ajuda = get_beneficio_by_tipo(TipoBeneficioCCT.AJUDA_MEDICAMENTO)
        assert ajuda is not None
        assert ajuda.valor_total == Decimal("300.00")
        assert ajuda.obrigatorio is True

    def test_afastamento_types(self):
        from modules.people_management.sst.models.afastamento import TipoAfastamento

        assert TipoAfastamento.ACIDENTE_TRABALHO == "acidente_trabalho"
        assert TipoAfastamento.DOENCA == "doenca"
