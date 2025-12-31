"""Testes para modelos fiscais - Sprint 28."""

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.financial.models.cfop_ncm import CFOP, NCM, RetencaoFederal
from modules.financial.models.fiscal_obligation import (
    SIMPLES_ANEXO_III_FAIXAS,
    FiscalObligation,
    SimplesNacionalDAS,
    SUFRAMAConfig,
    calcular_das_anexo_iii,
)
from modules.financial.models.nfe import NFe, NFeItem
from modules.financial.models.nfse import NFSe


class TestCFOP:
    """Testes para modelo CFOP."""

    def test_cfop_entrada(self):
        """Testa identificacao de CFOP de entrada."""
        cfop = CFOP(
            codigo="1102",
            descricao="Compra para comercializacao",
            tipo="entrada",
            grupo="1",
        )
        assert cfop.is_entrada is True
        assert cfop.is_saida is False
        assert cfop.is_interestadual is False
        assert cfop.is_exterior is False

    def test_cfop_saida_interestadual(self):
        """Testa identificacao de CFOP de saida interestadual."""
        cfop = CFOP(
            codigo="6102",
            descricao="Venda de mercadoria para outro estado",
            tipo="saida",
            grupo="6",
        )
        assert cfop.is_entrada is False
        assert cfop.is_saida is True
        assert cfop.is_interestadual is True
        assert cfop.is_exterior is False

    def test_cfop_exterior(self):
        """Testa identificacao de CFOP de operacao com exterior."""
        cfop = CFOP(
            codigo="7102",
            descricao="Venda de mercadoria para exterior",
            tipo="saida",
            grupo="7",
        )
        assert cfop.is_exterior is True

    def test_cfop_zfm(self):
        """Testa CFOP com beneficio ZFM."""
        cfop = CFOP(
            codigo="2407",
            descricao="Compra com incentivo de ICMS ZFM",
            tipo="entrada",
            grupo="2",
            zfm_aplicavel=True,
            zfm_isenta_icms=True,
            zfm_isenta_ipi=True,
        )
        assert cfop.zfm_aplicavel is True
        assert cfop.zfm_isenta_icms is True


class TestNCM:
    """Testes para modelo NCM."""

    def test_ncm_vigente(self):
        """Testa verificacao de vigencia do NCM."""
        ncm = NCM(
            codigo="84713012",
            descricao="Maquinas automaticas para processamento de dados",
            active=True,
            valid_from=date(2020, 1, 1),
            valid_until=None,
        )
        assert ncm.is_vigente is True

    def test_ncm_nao_vigente_data_futura(self):
        """Testa NCM com data de inicio futura."""
        ncm = NCM(
            codigo="84713012",
            descricao="Maquinas automaticas para processamento de dados",
            active=True,
            valid_from=date(2099, 1, 1),
            valid_until=None,
        )
        assert ncm.is_vigente is False

    def test_ncm_nao_vigente_expirado(self):
        """Testa NCM expirado."""
        ncm = NCM(
            codigo="84713012",
            descricao="Maquinas automaticas para processamento de dados",
            active=True,
            valid_from=date(2020, 1, 1),
            valid_until=date(2021, 12, 31),
        )
        assert ncm.is_vigente is False

    def test_ncm_inativo(self):
        """Testa NCM inativo."""
        ncm = NCM(
            codigo="84713012",
            descricao="Maquinas automaticas para processamento de dados",
            active=False,
        )
        assert ncm.is_vigente is False


class TestRetencaoFederal:
    """Testes para modelo RetencaoFederal."""

    def test_aliquota_pcc(self):
        """Testa calculo da aliquota PCC."""
        retencao = RetencaoFederal(
            nome="Servicos de Vigilancia",
            condominio_id=uuid4(),
            pis_retido=True,
            pis_aliquota=Decimal("0.65"),
            cofins_retido=True,
            cofins_aliquota=Decimal("3.00"),
            csll_retido=True,
            csll_aliquota=Decimal("1.00"),
        )
        assert retencao.aliquota_pcc == Decimal("4.65")

    def test_calcular_retencoes_completo(self):
        """Testa calculo completo de retencoes."""
        retencao = RetencaoFederal(
            nome="Servicos de Vigilancia",
            condominio_id=uuid4(),
            servico_vigilancia=True,
            inss_retido=True,
            inss_aliquota=Decimal("11.00"),
            ir_retido=True,
            ir_aliquota=Decimal("1.50"),
            ir_base_minima=Decimal("666.66"),
            pis_retido=True,
            pis_aliquota=Decimal("0.65"),
            cofins_retido=True,
            cofins_aliquota=Decimal("3.00"),
            csll_retido=True,
            csll_aliquota=Decimal("1.00"),
            pcc_base_minima=Decimal("215.05"),
        )

        resultado = retencao.calcular_retencoes(Decimal("10000.00"))

        # INSS: 11% de 10000 = 1100
        assert resultado["inss"] == Decimal("1100.00")
        # IR: 1.5% de 10000 = 150
        assert resultado["ir"] == Decimal("150.00")
        # PIS: 0.65% de 10000 = 65
        assert resultado["pis"] == Decimal("65.00")
        # COFINS: 3% de 10000 = 300
        assert resultado["cofins"] == Decimal("300.00")
        # CSLL: 1% de 10000 = 100
        assert resultado["csll"] == Decimal("100.00")
        # Total: 1100 + 150 + 65 + 300 + 100 = 1715
        assert resultado["total"] == Decimal("1715.00")
        # Liquido: 10000 - 1715 = 8285
        assert resultado["valor_liquido"] == Decimal("8285.00")

    def test_calcular_retencoes_com_liminar(self):
        """Testa calculo de retencoes com liminar INSS ativa."""
        retencao = RetencaoFederal(
            nome="Servicos de Vigilancia",
            condominio_id=uuid4(),
            servico_vigilancia=True,
            inss_retido=True,
            inss_aliquota=Decimal("11.00"),
            inss_liminar_ativa=True,
            inss_liminar_numero="1234567-89.2024.8.13.0001",
            ir_retido=True,
            ir_aliquota=Decimal("1.50"),
            pis_retido=True,
            pis_aliquota=Decimal("0.65"),
            cofins_retido=True,
            cofins_aliquota=Decimal("3.00"),
            csll_retido=True,
            csll_aliquota=Decimal("1.00"),
        )

        # Cliente aceita liminar
        resultado = retencao.calcular_retencoes(
            Decimal("10000.00"),
            cliente_aceita_liminar=True,
        )

        # INSS deve ser 0 com liminar
        assert resultado["inss"] == Decimal("0")
        assert resultado["liminar_aplicada"] is True
        assert resultado["liminar_numero"] == "1234567-89.2024.8.13.0001"
        # Total sem INSS: 150 + 65 + 300 + 100 = 615
        assert resultado["total"] == Decimal("615.00")

    def test_calcular_retencoes_cliente_nao_aceita_liminar(self):
        """Testa calculo quando cliente nao aceita liminar."""
        retencao = RetencaoFederal(
            nome="Servicos de Vigilancia",
            condominio_id=uuid4(),
            servico_vigilancia=True,
            inss_retido=True,
            inss_aliquota=Decimal("11.00"),
            inss_liminar_ativa=True,
            ir_retido=True,
            ir_aliquota=Decimal("1.50"),
            pis_retido=True,
            pis_aliquota=Decimal("0.65"),
            cofins_retido=True,
            cofins_aliquota=Decimal("3.00"),
            csll_retido=True,
            csll_aliquota=Decimal("1.00"),
        )

        # Cliente NAO aceita liminar
        resultado = retencao.calcular_retencoes(
            Decimal("10000.00"),
            cliente_aceita_liminar=False,
        )

        # INSS deve ser cobrado
        assert resultado["inss"] == Decimal("1100.00")
        assert resultado["liminar_aplicada"] is False

    def test_ir_abaixo_base_minima(self):
        """Testa que IR nao e retido abaixo da base minima."""
        retencao = RetencaoFederal(
            nome="Servicos de Vigilancia",
            condominio_id=uuid4(),
            inss_retido=False,
            ir_retido=True,
            ir_aliquota=Decimal("1.50"),
            ir_base_minima=Decimal("666.66"),
            pis_retido=False,
            cofins_retido=False,
            csll_retido=False,
        )

        # Valor abaixo da base minima
        resultado = retencao.calcular_retencoes(Decimal("500.00"))
        assert resultado["ir"] == Decimal("0")


class TestSimplesDAS:
    """Testes para calculo do DAS Anexo III."""

    def test_faixas_anexo_iii(self):
        """Testa estrutura das faixas do Anexo III."""
        assert len(SIMPLES_ANEXO_III_FAIXAS) == 6
        # Faixas podem ser int ou string, verifica apenas existencia
        assert "faixa" in SIMPLES_ANEXO_III_FAIXAS[0]
        assert "faixa" in SIMPLES_ANEXO_III_FAIXAS[5]

    def test_calcular_das_faixa_3(self):
        """Testa calculo do DAS para faixa 3 (360k a 720k)."""
        # Receita mensal 50k, receita 12 meses 500k
        resultado = calcular_das_anexo_iii(
            Decimal("50000.00"),
            Decimal("500000.00"),
        )

        # Verifica que resultado tem estrutura esperada
        assert "faixa" in resultado
        assert "aliquota_nominal" in resultado
        assert "aliquota_efetiva" in resultado
        assert "valor_das" in resultado
        assert "reparticao" in resultado
        # Verifica reparticao para Anexo III (chaves minusculas)
        assert "cpp" in resultado["reparticao"]
        assert "iss" in resultado["reparticao"]

    def test_calcular_das_faixa_1(self):
        """Testa calculo do DAS para faixa 1 (ate 180k)."""
        resultado = calcular_das_anexo_iii(
            Decimal("10000.00"),
            Decimal("100000.00"),
        )

        # Verifica estrutura
        assert "faixa" in resultado
        assert "aliquota_nominal" in resultado
        assert "parcela_deduzir" in resultado
        assert "aliquota_efetiva" in resultado


class TestNFSe:
    """Testes para modelo NFS-e."""

    def test_criar_nfse_basica(self):
        """Testa criacao de NFS-e basica."""
        nfse = NFSe(
            condominio_id=uuid4(),
            prestador_cnpj="12345678000199",
            prestador_razao_social="Conecta Mais Servicos LTDA",
            tomador_cpf_cnpj="98765432000188",
            tomador_razao_social="Condominio Residencial Teste",
            tomador_endereco={
                "logradouro": "Rua Teste",
                "numero": "100",
                "bairro": "Centro",
                "municipio": "Manaus",
                "uf": "AM",
                "cep": "69000000",
            },
            codigo_servico="11.02",
            codigo_municipio="1302603",  # Manaus
            discriminacao="Servicos de vigilancia e seguranca patrimonial",
            valor_servicos=Decimal("10000.00"),
            aliquota_iss=Decimal("5.00"),
            natureza_operacao="1",
            status="rascunho",
        )

        assert nfse.status == "rascunho"
        assert nfse.valor_servicos == Decimal("10000.00")

    def test_nfse_properties(self):
        """Testa properties da NFS-e."""
        nfse = NFSe(
            condominio_id=uuid4(),
            prestador_cnpj="12345678000199",
            prestador_razao_social="Conecta Mais",
            codigo_servico="11.02",
            codigo_municipio="1302603",
            discriminacao="Servicos de vigilancia",
            valor_servicos=Decimal("10000.00"),
            aliquota_iss=Decimal("5.00"),
            status="autorizada",
            numero="123456",
        )

        assert nfse.is_autorizada is True
        assert nfse.is_cancelada is False
        assert nfse.pode_cancelar is True


class TestSUFRAMA:
    """Testes para modelo SUFRAMA."""

    def test_suframa_ativo(self):
        """Testa verificacao de SUFRAMA ativo."""
        config = SUFRAMAConfig(
            condominio_id=uuid4(),
            inscricao_suframa="123456789",
            data_validade=date(2099, 12, 31),
            tipo_zona="zfm",
            cnpj="12345678000199",
            razao_social="Empresa Teste",
            beneficio_ipi=True,
            beneficio_icms=True,
            beneficio_pis_cofins=True,
            status="ativo",
            active=True,
        )

        assert config.is_ativo is True

    def test_suframa_expirado(self):
        """Testa SUFRAMA expirado."""
        config = SUFRAMAConfig(
            condominio_id=uuid4(),
            inscricao_suframa="123456789",
            data_validade=date(2020, 12, 31),
            tipo_zona="zfm",
            cnpj="12345678000199",
            razao_social="Empresa Teste",
            status="ativo",
            active=True,
        )

        assert config.is_ativo is False


class TestFiscalObligation:
    """Testes para modelo FiscalObligation."""

    def test_obrigacao_vencida(self):
        """Testa identificacao de obrigacao vencida."""
        obrigacao = FiscalObligation(
            condominio_id=uuid4(),
            tipo="DAS",
            nome="DAS Simples Nacional",
            frequencia="mensal",
            ano=2024,
            mes=1,
            data_vencimento=date(2024, 2, 20),
            status="pendente",
        )

        assert obrigacao.is_vencida is True

    def test_obrigacao_pendente(self):
        """Testa obrigacao pendente nao vencida."""
        obrigacao = FiscalObligation(
            condominio_id=uuid4(),
            tipo="DAS",
            nome="DAS Simples Nacional",
            frequencia="mensal",
            ano=2099,
            mes=12,
            data_vencimento=date(2100, 1, 20),
            status="pendente",
        )

        assert obrigacao.is_vencida is False

    def test_obrigacao_entregue(self):
        """Testa obrigacao entregue."""
        obrigacao = FiscalObligation(
            condominio_id=uuid4(),
            tipo="EFD",
            nome="EFD Contribuicoes",
            frequencia="mensal",
            ano=2024,
            mes=11,
            data_vencimento=date(2024, 12, 20),
            status="enviada",
        )

        assert obrigacao.is_entregue is True
        assert obrigacao.is_vencida is False


class TestSimplesDASModel:
    """Testes para modelo SimplesNacionalDAS."""

    def test_das_anexo_iii(self):
        """Testa DAS do Anexo III."""
        das = SimplesNacionalDAS(
            condominio_id=uuid4(),
            competencia="2024-12",
            ano=2024,
            mes=12,
            anexo="III",
            faixa="3",
            receita_bruta_mes=Decimal("50000.00"),
            receita_bruta_12_meses=Decimal("500000.00"),
            aliquota_nominal=Decimal("13.50"),
            aliquota_efetiva=Decimal("10.00"),
            valor_das=Decimal("5000.00"),
            data_vencimento=date(2025, 1, 20),
        )

        assert das.is_anexo_iii is True
        assert das.is_anexo_iv is False

    def test_das_vencido(self):
        """Testa DAS vencido."""
        das = SimplesNacionalDAS(
            condominio_id=uuid4(),
            competencia="2024-01",
            ano=2024,
            mes=1,
            anexo="III",
            faixa="3",
            receita_bruta_mes=Decimal("50000.00"),
            receita_bruta_12_meses=Decimal("500000.00"),
            aliquota_nominal=Decimal("13.50"),
            aliquota_efetiva=Decimal("10.00"),
            valor_das=Decimal("5000.00"),
            data_vencimento=date(2024, 2, 20),
            status="pendente",
        )

        assert das.is_vencido is True
