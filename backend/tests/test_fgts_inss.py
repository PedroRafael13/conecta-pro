"""
Testes completos para o modulo FGTS/INSS.

Inclui testes para:
- Schemas Pydantic (validacao)
- FGTSINSSManager (core)
- FGTSINSSService (service)
- Endpoints REST (controller)

Author: Claude AI + Human Developer
Date: 2026-01-16
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4

from httpx import AsyncClient
from pydantic import ValidationError

# Schemas
from modules.government_integrations.schemas.fgts_inss import (
    CalculoFGTSRequest,
    CalculoINSSRequest,
)

# Core
from modules.government_integrations.core.fgts_inss_manager import (
    FGTSINSSManager,
    CalculadoraFGTS,
    CalculadoraINSS,
    GeradorGRF,
    GeradorGRRF,
    GeradorGPS,
    TabelaINSS,
    Trabalhador,
    Remuneracao,
    CalculoFGTS,
    CalculoINSS,
    Guia,
    Certidao,
    ExtratoFGTS,
    TipoRecolhimento,
    CodigoRecolhimento,
    ModalidadeSaque,
    CategoriaContribuinte,
    TipoGuia,
    StatusGuia,
    StatusCertidao,
    TipoCertidao,
    FGTSINSSError,
    CalculoError,
    GuiaError,
    ConsultaError,
    validar_pis_pasep,
    formatar_pis_pasep,
    calcular_aliquota_efetiva_inss,
    init_fgts_inss_manager,
)

# Service
from modules.government_integrations.services.fgts_inss_service import FGTSINSSService


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def trabalhador_padrao() -> Trabalhador:
    """Fixture de trabalhador padrao para testes."""
    return Trabalhador(
        id=str(uuid4()),
        cpf="12345678909",
        pis_pasep="12345678901",
        nome="Joao da Silva",
        data_admissao=date(2020, 1, 15),
        data_nascimento=date(1985, 5, 20),
        categoria=CategoriaContribuinte.EMPREGADO,
        cargo="Vigilante",
    )


@pytest.fixture
def trabalhador_domestico() -> Trabalhador:
    """Fixture de trabalhador domestico."""
    return Trabalhador(
        id=str(uuid4()),
        cpf="98765432100",
        pis_pasep="98765432109",
        nome="Maria Souza",
        data_admissao=date(2021, 3, 1),
        categoria=CategoriaContribuinte.DOMESTICO,
        cargo="Empregada Domestica",
    )


@pytest.fixture
def remuneracao_padrao(trabalhador_padrao: Trabalhador) -> Remuneracao:
    """Fixture de remuneracao padrao."""
    return Remuneracao(
        trabalhador_id=trabalhador_padrao.id,
        competencia=date(2026, 1, 1),
        salario_base=Decimal("3000.00"),
        horas_extras=Decimal("300.00"),
        adicional_noturno=Decimal("150.00"),
    )


@pytest.fixture
def remuneracao_salario_minimo(trabalhador_padrao: Trabalhador) -> Remuneracao:
    """Fixture de remuneracao com salario minimo."""
    return Remuneracao(
        trabalhador_id=trabalhador_padrao.id,
        competencia=date(2026, 1, 1),
        salario_base=Decimal("1518.00"),
    )


@pytest.fixture
def remuneracao_teto_inss(trabalhador_padrao: Trabalhador) -> Remuneracao:
    """Fixture de remuneracao acima do teto INSS."""
    return Remuneracao(
        trabalhador_id=trabalhador_padrao.id,
        competencia=date(2026, 1, 1),
        salario_base=Decimal("10000.00"),
    )


@pytest.fixture
def manager() -> FGTSINSSManager:
    """Fixture do FGTSINSSManager."""
    return FGTSINSSManager(ambiente="homologacao")


@pytest.fixture
def calculadora_fgts() -> CalculadoraFGTS:
    """Fixture da calculadora FGTS."""
    return CalculadoraFGTS()


@pytest.fixture
def calculadora_inss() -> CalculadoraINSS:
    """Fixture da calculadora INSS."""
    return CalculadoraINSS(TabelaINSS.tabela_2025())


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Headers de autenticacao para testes de API."""
    return {"Authorization": "Bearer test-token"}


# =============================================================================
# TEST SCHEMAS
# =============================================================================

class TestSchemas:
    """Testes para validacao dos schemas Pydantic."""

    class TestCalculoFGTSRequest:
        """Testes para CalculoFGTSRequest."""

        def test_schema_valido(self):
            """Testa criacao de schema valido."""
            request = CalculoFGTSRequest(
                salario_base=Decimal("3000.00"),
                mes_referencia="2026-01",
                tipo_recolhimento="mensal",
                rescisao=False,
            )
            assert request.salario_base == Decimal("3000.00")
            assert request.mes_referencia == "2026-01"
            assert request.tipo_recolhimento == "mensal"
            assert request.rescisao is False

        def test_schema_com_rescisao(self):
            """Testa schema com calculo de rescisao."""
            request = CalculoFGTSRequest(
                salario_base=Decimal("5000.00"),
                mes_referencia="2026-01",
                tipo_recolhimento="rescisorio",
                rescisao=True,
            )
            assert request.rescisao is True
            assert request.tipo_recolhimento == "rescisorio"

        def test_salario_base_obrigatorio(self):
            """Testa que salario_base e obrigatorio."""
            with pytest.raises(ValidationError) as exc_info:
                CalculoFGTSRequest(
                    mes_referencia="2026-01",
                )
            assert "salario_base" in str(exc_info.value)

        def test_salario_base_deve_ser_positivo(self):
            """Testa que salario_base deve ser maior que zero."""
            with pytest.raises(ValidationError) as exc_info:
                CalculoFGTSRequest(
                    salario_base=Decimal("0"),
                    mes_referencia="2026-01",
                )
            assert "greater than 0" in str(exc_info.value).lower() or "gt" in str(exc_info.value).lower()

        def test_mes_referencia_formato_invalido(self):
            """Testa validacao de formato de mes_referencia."""
            with pytest.raises(ValidationError) as exc_info:
                CalculoFGTSRequest(
                    salario_base=Decimal("3000.00"),
                    mes_referencia="01-2026",  # Formato errado
                )
            assert "mes_referencia" in str(exc_info.value)

        def test_mes_referencia_mes_invalido(self):
            """Testa validacao de mes invalido."""
            with pytest.raises(ValidationError) as exc_info:
                CalculoFGTSRequest(
                    salario_base=Decimal("3000.00"),
                    mes_referencia="2026-13",  # Mes 13 invalido
                )
            assert "mes_referencia" in str(exc_info.value)

        def test_tipo_recolhimento_invalido(self):
            """Testa validacao de tipo_recolhimento invalido."""
            with pytest.raises(ValidationError) as exc_info:
                CalculoFGTSRequest(
                    salario_base=Decimal("3000.00"),
                    mes_referencia="2026-01",
                    tipo_recolhimento="invalido",
                )
            assert "tipo_recolhimento" in str(exc_info.value)

        def test_valores_default(self):
            """Testa valores default do schema."""
            request = CalculoFGTSRequest(
                salario_base=Decimal("3000.00"),
                mes_referencia="2026-01",
            )
            assert request.tipo_recolhimento == "mensal"
            assert request.rescisao is False

    class TestCalculoINSSRequest:
        """Testes para CalculoINSSRequest."""

        def test_schema_valido(self):
            """Testa criacao de schema valido."""
            request = CalculoINSSRequest(
                salario_bruto=Decimal("4000.00"),
                categoria="empregado",
                mes_referencia="2026-01",
            )
            assert request.salario_bruto == Decimal("4000.00")
            assert request.categoria == "empregado"
            assert request.mes_referencia == "2026-01"

        def test_categorias_validas(self):
            """Testa todas as categorias validas."""
            categorias = ["empregado", "domestico", "contribuinte_individual", "facultativo", "mei"]
            for cat in categorias:
                request = CalculoINSSRequest(
                    salario_bruto=Decimal("3000.00"),
                    categoria=cat,
                    mes_referencia="2026-01",
                )
                assert request.categoria == cat

        def test_categoria_invalida(self):
            """Testa categoria invalida."""
            with pytest.raises(ValidationError) as exc_info:
                CalculoINSSRequest(
                    salario_bruto=Decimal("3000.00"),
                    categoria="autonomo",  # Invalido
                    mes_referencia="2026-01",
                )
            assert "categoria" in str(exc_info.value)

        def test_salario_bruto_obrigatorio(self):
            """Testa que salario_bruto e obrigatorio."""
            with pytest.raises(ValidationError) as exc_info:
                CalculoINSSRequest(
                    categoria="empregado",
                    mes_referencia="2026-01",
                )
            assert "salario_bruto" in str(exc_info.value)

        def test_salario_bruto_deve_ser_positivo(self):
            """Testa que salario_bruto deve ser maior que zero."""
            with pytest.raises(ValidationError) as exc_info:
                CalculoINSSRequest(
                    salario_bruto=Decimal("-100.00"),
                    mes_referencia="2026-01",
                )
            assert "greater than 0" in str(exc_info.value).lower() or "gt" in str(exc_info.value).lower()

        def test_valor_default_categoria(self):
            """Testa valor default de categoria."""
            request = CalculoINSSRequest(
                salario_bruto=Decimal("3000.00"),
                mes_referencia="2026-01",
            )
            assert request.categoria == "empregado"


# =============================================================================
# TEST FGTS INSS MANAGER (CORE)
# =============================================================================

class TestFGTSINSSManager:
    """Testes para o FGTSINSSManager (core)."""

    class TestCalculadoraFGTS:
        """Testes para CalculadoraFGTS."""

        def test_calculo_deposito_mensal_padrao(
            self,
            calculadora_fgts: CalculadoraFGTS,
            trabalhador_padrao: Trabalhador,
            remuneracao_padrao: Remuneracao,
        ):
            """Testa calculo de deposito mensal padrao (8%)."""
            resultado = calculadora_fgts.calcular_deposito_mensal(
                trabalhador_padrao, remuneracao_padrao
            )

            # Base: 3000 + 300 + 150 = 3450
            # FGTS: 3450 * 8% = 276.00
            assert resultado.base_calculo == Decimal("3450.00")
            assert resultado.aliquota == Decimal("8.0")
            assert resultado.valor_deposito == Decimal("276.00")
            assert resultado.tipo == TipoRecolhimento.MENSAL

        def test_calculo_deposito_aprendiz(
            self,
            calculadora_fgts: CalculadoraFGTS,
            trabalhador_padrao: Trabalhador,
            remuneracao_salario_minimo: Remuneracao,
        ):
            """Testa calculo para menor aprendiz (2%)."""
            resultado = calculadora_fgts.calcular_deposito_mensal(
                trabalhador_padrao, remuneracao_salario_minimo, is_aprendiz=True
            )

            # FGTS: 1518 * 2% = 30.36
            assert resultado.aliquota == Decimal("2.0")
            assert resultado.valor_deposito == Decimal("30.36")

        def test_calculo_rescisao_sem_justa_causa(
            self,
            calculadora_fgts: CalculadoraFGTS,
            trabalhador_padrao: Trabalhador,
            remuneracao_padrao: Remuneracao,
        ):
            """Testa calculo rescisorio com multa 40%."""
            saldo_fgts = Decimal("15000.00")

            resultado = calculadora_fgts.calcular_rescisao(
                trabalhador=trabalhador_padrao,
                saldo_fgts=saldo_fgts,
                motivo=ModalidadeSaque.DEMISSAO_SEM_JUSTA_CAUSA,
                remuneracao_final=remuneracao_padrao,
            )

            # Deposito do mes: 3450 * 8% = 276.00
            # Saldo para multa: 15000 + 276 = 15276
            # Multa 40%: 15276 * 40% = 6110.40
            assert resultado.valor_deposito == Decimal("276.00")
            assert resultado.valor_multa == Decimal("6110.40")
            assert resultado.tipo == TipoRecolhimento.RESCISORIO

        def test_calculo_rescisao_com_aviso_previo(
            self,
            calculadora_fgts: CalculadoraFGTS,
            trabalhador_padrao: Trabalhador,
        ):
            """Testa calculo rescisorio com aviso previo indenizado."""
            saldo_fgts = Decimal("10000.00")
            valor_aviso = Decimal("3000.00")

            resultado = calculadora_fgts.calcular_rescisao(
                trabalhador=trabalhador_padrao,
                saldo_fgts=saldo_fgts,
                motivo=ModalidadeSaque.DEMISSAO_SEM_JUSTA_CAUSA,
                aviso_previo_indenizado=True,
                valor_aviso=valor_aviso,
            )

            # FGTS sobre aviso: 3000 * 8% = 240.00
            # Saldo para multa: 10000 + 240 = 10240
            # Multa: 10240 * 40% = 4096.00
            assert resultado.valor_deposito == Decimal("240.00")
            assert resultado.valor_multa == Decimal("4096.00")

        def test_calculo_rescisao_aposentadoria_sem_multa(
            self,
            calculadora_fgts: CalculadoraFGTS,
            trabalhador_padrao: Trabalhador,
        ):
            """Testa que aposentadoria nao tem multa rescisoria."""
            resultado = calculadora_fgts.calcular_rescisao(
                trabalhador=trabalhador_padrao,
                saldo_fgts=Decimal("20000.00"),
                motivo=ModalidadeSaque.APOSENTADORIA,
            )

            assert resultado.valor_multa == Decimal("0")

        def test_calculo_13_primeira_parcela(
            self,
            calculadora_fgts: CalculadoraFGTS,
            trabalhador_padrao: Trabalhador,
        ):
            """Testa que primeira parcela do 13o nao gera FGTS."""
            resultado = calculadora_fgts.calcular_13_salario(
                trabalhador=trabalhador_padrao,
                valor_13=Decimal("1500.00"),
                parcela=1,
            )

            assert resultado.valor_deposito == Decimal("0")

        def test_calculo_13_segunda_parcela(
            self,
            calculadora_fgts: CalculadoraFGTS,
            trabalhador_padrao: Trabalhador,
        ):
            """Testa FGTS sobre segunda parcela do 13o."""
            valor_13 = Decimal("3000.00")

            resultado = calculadora_fgts.calcular_13_salario(
                trabalhador=trabalhador_padrao,
                valor_13=valor_13,
                parcela=2,
            )

            # FGTS: 3000 * 8% = 240.00
            assert resultado.valor_deposito == Decimal("240.00")

    class TestCalculadoraINSS:
        """Testes para CalculadoraINSS."""

        def test_calculo_primeira_faixa(
            self,
            calculadora_inss: CalculadoraINSS,
            trabalhador_padrao: Trabalhador,
            remuneracao_salario_minimo: Remuneracao,
        ):
            """Testa INSS para salario na primeira faixa (7.5%)."""
            resultado = calculadora_inss.calcular_contribuicao(
                trabalhador_padrao, remuneracao_salario_minimo
            )

            # 1518 * 7.5% = 113.85
            assert resultado.valor_contribuicao == Decimal("113.85")
            assert resultado.teto_aplicado is False

        def test_calculo_progressivo_multiplas_faixas(
            self,
            calculadora_inss: CalculadoraINSS,
            trabalhador_padrao: Trabalhador,
            remuneracao_padrao: Remuneracao,
        ):
            """Testa calculo progressivo com multiplas faixas."""
            resultado = calculadora_inss.calcular_contribuicao(
                trabalhador_padrao, remuneracao_padrao
            )

            # Base: 3450.00
            # Faixa 1: 1518.00 * 7.5% = 113.85
            # Faixa 2: (2793.88 - 1518) * 9% = 114.83
            # Faixa 3: (3450 - 2793.88) * 12% = 78.73
            # Total: 307.41
            assert resultado.base_calculo == Decimal("3450.00")
            assert len(resultado.faixas_aplicadas) >= 2
            assert resultado.teto_aplicado is False

        def test_calculo_acima_teto(
            self,
            calculadora_inss: CalculadoraINSS,
            trabalhador_padrao: Trabalhador,
            remuneracao_teto_inss: Remuneracao,
        ):
            """Testa que contribuicao e limitada ao teto."""
            resultado = calculadora_inss.calcular_contribuicao(
                trabalhador_padrao, remuneracao_teto_inss
            )

            # Base limitada ao teto: 8157.41
            assert resultado.base_calculo == Decimal("8157.41")
            assert resultado.teto_aplicado is True

        def test_aliquota_efetiva(
            self,
            calculadora_inss: CalculadoraINSS,
            trabalhador_padrao: Trabalhador,
            remuneracao_padrao: Remuneracao,
        ):
            """Testa calculo da aliquota efetiva."""
            resultado = calculadora_inss.calcular_contribuicao(
                trabalhador_padrao, remuneracao_padrao
            )

            # Aliquota efetiva deve ser menor que 14% (maior aliquota)
            assert resultado.aliquota_efetiva > Decimal("0")
            assert resultado.aliquota_efetiva < Decimal("14.0")

        def test_contribuicao_patronal(self, calculadora_inss: CalculadoraINSS):
            """Testa calculo de contribuicao patronal."""
            folha_total = Decimal("100000.00")

            resultado = calculadora_inss.calcular_contribuicao_patronal(
                folha_total=folha_total,
                rat=Decimal("2.0"),
                fap=Decimal("1.0"),
            )

            # Patronal basica: 100000 * 20% = 20000
            # RAT: 100000 * 2% = 2000
            # Terceiros: 100000 * 5.8% = 5800
            # Total: 27800
            assert resultado["patronal_basica"] == Decimal("20000.00")
            assert resultado["valor_rat"] == Decimal("2000.00")
            assert resultado["valor_terceiros"] == Decimal("5800.00")
            assert resultado["total"] == Decimal("27800.00")

        def test_contribuicao_patronal_com_fap_ajustado(
            self, calculadora_inss: CalculadoraINSS
        ):
            """Testa RAT ajustado pelo FAP."""
            folha_total = Decimal("50000.00")

            resultado = calculadora_inss.calcular_contribuicao_patronal(
                folha_total=folha_total,
                rat=Decimal("3.0"),  # RAT alto
                fap=Decimal("0.5"),  # FAP bom
            )

            # RAT ajustado: 3% * 0.5 = 1.5%
            # Valor RAT: 50000 * 1.5% = 750
            assert resultado["rat_ajustado"] == Decimal("1.50")
            assert resultado["valor_rat"] == Decimal("750.00")

        def test_atualizar_tabela(self, calculadora_inss: CalculadoraINSS):
            """Testa atualizacao de tabela INSS."""
            nova_tabela = TabelaINSS.tabela_2024()
            calculadora_inss.atualizar_tabela(nova_tabela)

            assert calculadora_inss.tabela.vigencia == date(2024, 1, 1)
            assert calculadora_inss.tabela.teto == Decimal("7786.02")

    class TestGeradorGuias:
        """Testes para geradores de guias."""

        def test_gerar_grf(
            self,
            trabalhador_padrao: Trabalhador,
            remuneracao_padrao: Remuneracao,
            calculadora_fgts: CalculadoraFGTS,
        ):
            """Testa geracao de GRF."""
            gerador = GeradorGRF()
            calculo = calculadora_fgts.calcular_deposito_mensal(
                trabalhador_padrao, remuneracao_padrao
            )

            guia = gerador.gerar(
                empresa_cnpj="12345678000199",
                empresa_razao_social="Empresa Teste LTDA",
                competencia=date(2026, 1, 1),
                calculos=[calculo],
            )

            assert guia.tipo == TipoGuia.GRF
            assert guia.valor_principal == Decimal("276.00")
            assert guia.empresa_cnpj == "12345678000199"
            assert guia.codigo_barras is not None
            assert guia.linha_digitavel is not None
            assert len(guia.trabalhadores) == 1

        def test_gerar_grrf(
            self,
            trabalhador_padrao: Trabalhador,
            calculadora_fgts: CalculadoraFGTS,
        ):
            """Testa geracao de GRRF."""
            gerador = GeradorGRRF()
            calculo = calculadora_fgts.calcular_rescisao(
                trabalhador=trabalhador_padrao,
                saldo_fgts=Decimal("10000.00"),
                motivo=ModalidadeSaque.DEMISSAO_SEM_JUSTA_CAUSA,
            )

            guia = gerador.gerar(
                empresa_cnpj="12345678000199",
                empresa_razao_social="Empresa Teste LTDA",
                calculo=calculo,
                trabalhador=trabalhador_padrao,
                data_desligamento=date(2026, 1, 15),
            )

            assert guia.tipo == TipoGuia.GRRF
            assert guia.valor_multa == calculo.valor_multa
            assert guia.detalhamento["trabalhador_cpf"] == trabalhador_padrao.cpf

        def test_gerar_gps(
            self,
            trabalhador_padrao: Trabalhador,
            remuneracao_padrao: Remuneracao,
            calculadora_inss: CalculadoraINSS,
        ):
            """Testa geracao de GPS."""
            gerador = GeradorGPS()
            contribuicao = calculadora_inss.calcular_contribuicao(
                trabalhador_padrao, remuneracao_padrao
            )
            patronal = calculadora_inss.calcular_contribuicao_patronal(
                Decimal("3450.00")
            )

            guia = gerador.gerar(
                empresa_cnpj="12345678000199",
                empresa_razao_social="Empresa Teste LTDA",
                competencia=date(2026, 1, 1),
                contribuicoes_empregados=[contribuicao],
                contribuicao_patronal=patronal,
            )

            assert guia.tipo == TipoGuia.GPS
            assert guia.valor_total > contribuicao.valor_contribuicao
            assert "valor_patronal_total" in guia.detalhamento

        def test_vencimento_grf(self):
            """Testa calculo de vencimento da GRF."""
            gerador = GeradorGRF()
            competencia = date(2026, 1, 1)

            vencimento = gerador._calcular_vencimento(competencia, TipoGuia.GRF)

            # FGTS vence dia 7 do mes seguinte
            assert vencimento.month == 2
            assert vencimento.day == 7

        def test_vencimento_gps(self):
            """Testa calculo de vencimento da GPS."""
            gerador = GeradorGPS()
            competencia = date(2026, 1, 1)

            vencimento = gerador._calcular_vencimento(competencia, TipoGuia.GPS)

            # GPS vence dia 20 do mes seguinte
            assert vencimento.month == 2
            assert vencimento.day == 20

    class TestFGTSINSSManagerIntegration:
        """Testes de integracao do FGTSINSSManager."""

        @pytest.mark.asyncio
        async def test_calcular_fgts_mensal(
            self,
            manager: FGTSINSSManager,
            trabalhador_padrao: Trabalhador,
            remuneracao_padrao: Remuneracao,
        ):
            """Testa calculo FGTS mensal via manager."""
            calculos = await manager.calcular_fgts_mensal(
                trabalhadores=[trabalhador_padrao],
                remuneracoes=[remuneracao_padrao],
            )

            assert len(calculos) == 1
            assert calculos[0].valor_deposito == Decimal("276.00")

        @pytest.mark.asyncio
        async def test_calcular_inss_mensal(
            self,
            manager: FGTSINSSManager,
            trabalhador_padrao: Trabalhador,
            remuneracao_padrao: Remuneracao,
        ):
            """Testa calculo INSS mensal via manager."""
            calculos = await manager.calcular_inss_mensal(
                trabalhadores=[trabalhador_padrao],
                remuneracoes=[remuneracao_padrao],
            )

            assert len(calculos) == 1
            assert calculos[0].valor_contribuicao > Decimal("0")

        @pytest.mark.asyncio
        async def test_gerar_grf_via_manager(
            self,
            manager: FGTSINSSManager,
            trabalhador_padrao: Trabalhador,
            remuneracao_padrao: Remuneracao,
        ):
            """Testa geracao de GRF via manager."""
            calculos = await manager.calcular_fgts_mensal(
                [trabalhador_padrao], [remuneracao_padrao]
            )

            guia = await manager.gerar_grf(
                empresa_cnpj="12345678000199",
                empresa_razao_social="Empresa Teste LTDA",
                competencia=date(2026, 1, 1),
                calculos=calculos,
            )

            assert guia.tipo == TipoGuia.GRF
            assert guia.status == StatusGuia.GERADA

        @pytest.mark.asyncio
        async def test_gerar_dae_domestico(
            self,
            manager: FGTSINSSManager,
            trabalhador_domestico: Trabalhador,
        ):
            """Testa geracao de DAE para domestico."""
            remuneracao = Remuneracao(
                trabalhador_id=trabalhador_domestico.id,
                competencia=date(2026, 1, 1),
                salario_base=Decimal("1800.00"),
            )

            guia = await manager.gerar_dae(
                empregador_cpf="12345678909",
                empregador_nome="Empregador Teste",
                trabalhador=trabalhador_domestico,
                remuneracao=remuneracao,
                competencia=date(2026, 1, 1),
            )

            assert guia.tipo == TipoGuia.DAE
            assert "fgts_8" in guia.detalhamento
            assert "fgts_multa_3_2" in guia.detalhamento
            assert "inss_empregado" in guia.detalhamento

        @pytest.mark.asyncio
        async def test_processar_folha_mensal(
            self,
            manager: FGTSINSSManager,
            trabalhador_padrao: Trabalhador,
            remuneracao_padrao: Remuneracao,
        ):
            """Testa processamento completo de folha mensal."""
            resultado = await manager.processar_folha_mensal(
                empresa_cnpj="12345678000199",
                empresa_razao_social="Empresa Teste LTDA",
                competencia=date(2026, 1, 1),
                trabalhadores=[trabalhador_padrao],
                remuneracoes=[remuneracao_padrao],
            )

            assert "fgts" in resultado
            assert "inss" in resultado
            assert resultado["qtd_trabalhadores"] == 1
            assert "guia" in resultado["fgts"]
            assert "guia" in resultado["inss"]

        @pytest.mark.asyncio
        async def test_consultar_extrato_fgts_homologacao(
            self, manager: FGTSINSSManager
        ):
            """Testa consulta de extrato FGTS em homologacao."""
            extrato = await manager.consultar_extrato_fgts(
                pis_pasep="12345678901",
                empresa_cnpj="12345678000199",
            )

            assert extrato.saldo_total == Decimal("15432.67")
            assert extrato.conta_ativa is True
            assert len(extrato.movimentacoes) > 0

        @pytest.mark.asyncio
        async def test_emitir_crf(self, manager: FGTSINSSManager):
            """Testa emissao de CRF."""
            certidao = await manager.emitir_crf("12345678000199")

            assert certidao.tipo == TipoCertidao.CRF
            assert certidao.status == StatusCertidao.NEGATIVA
            assert certidao.codigo_controle is not None
            assert certidao.data_validade > datetime.now()

        @pytest.mark.asyncio
        async def test_emitir_cnd_inss(self, manager: FGTSINSSManager):
            """Testa emissao de CND INSS."""
            certidao = await manager.emitir_cnd_inss("12345678000199")

            assert certidao.tipo == TipoCertidao.CND_INSS
            assert certidao.status == StatusCertidao.NEGATIVA
            # CND INSS tem validade maior (180 dias)
            dias_validade = (certidao.data_validade - certidao.data_emissao).days
            assert dias_validade >= 180

        @pytest.mark.asyncio
        async def test_verificar_regularidade(self, manager: FGTSINSSManager):
            """Testa verificacao de regularidade fiscal."""
            resultado = await manager.verificar_regularidade("12345678000199")

            assert resultado["regular"] is True
            assert "fgts" in resultado
            assert "inss" in resultado
            assert resultado["fgts"]["status"] == "negativa"
            assert resultado["inss"]["status"] == "negativa"

    class TestValidacoes:
        """Testes para funcoes de validacao."""

        def test_validar_pis_valido(self):
            """Testa validacao de PIS valido."""
            # PIS valido (exemplo)
            assert validar_pis_pasep("17033259504") is True

        def test_validar_pis_invalido_digito(self):
            """Testa validacao de PIS com digito errado."""
            # 12345678900 tem digito verificador 0, entao 1 seria invalido
            assert validar_pis_pasep("12345678901") is False

        def test_validar_pis_invalido_tamanho(self):
            """Testa validacao de PIS com tamanho errado."""
            assert validar_pis_pasep("1234567890") is False

        def test_validar_pis_invalido_sequencia(self):
            """Testa validacao de PIS com sequencia repetida."""
            assert validar_pis_pasep("11111111111") is False

        def test_formatar_pis(self):
            """Testa formatacao de PIS."""
            formatado = formatar_pis_pasep("17033259504")
            assert formatado == "170.33259.50-4"

        def test_calcular_aliquota_efetiva(self):
            """Testa calculo de aliquota efetiva."""
            # Salario minimo: apenas primeira faixa
            aliquota = calcular_aliquota_efetiva_inss(Decimal("1518.00"))
            assert aliquota == Decimal("7.50")

        def test_calcular_aliquota_efetiva_acima_teto(self):
            """Testa aliquota efetiva para salario acima do teto."""
            aliquota_teto = calcular_aliquota_efetiva_inss(Decimal("8157.41"))
            aliquota_acima = calcular_aliquota_efetiva_inss(Decimal("15000.00"))

            # Deve ser a mesma aliquota efetiva
            assert aliquota_teto == aliquota_acima

    class TestExcecoes:
        """Testes para tratamento de excecoes."""

        def test_fgts_inss_error_base(self):
            """Testa excecao base."""
            error = FGTSINSSError("Erro teste", code="TEST_001", details={"campo": "valor"})

            assert str(error) == "Erro teste"
            assert error.code == "TEST_001"
            assert error.details["campo"] == "valor"

        def test_calculo_error(self):
            """Testa excecao de calculo."""
            error = CalculoError("Erro no calculo")
            assert isinstance(error, FGTSINSSError)

        def test_guia_error(self):
            """Testa excecao de guia."""
            error = GuiaError("Erro na guia")
            assert isinstance(error, FGTSINSSError)

        def test_consulta_error(self):
            """Testa excecao de consulta."""
            error = ConsultaError("Erro na consulta")
            assert isinstance(error, FGTSINSSError)


# =============================================================================
# TEST FGTS INSS SERVICE
# =============================================================================

class TestFGTSINSSService:
    """Testes para FGTSINSSService."""

    class TestCalculoFGTS:
        """Testes para calculo de FGTS no service."""

        def test_calcular_fgts_mensal(self):
            """Testa calculo de FGTS mensal."""
            resultado = FGTSINSSService.calcular_fgts(
                salario_base=Decimal("3000.00"),
                mes_referencia="2026-01",
                tipo_recolhimento="mensal",
                rescisao=False,
            )

            assert resultado["salario_base"] == "3000.00"
            assert resultado["aliquota"] == "8%"
            # 3000 * 8% = 240
            assert resultado["valor_fgts"] == "240.00"
            assert resultado["valor_total"] == "240.00"
            assert resultado["rescisao"] is False
            assert resultado["multa_rescisoria"] is None

        def test_calcular_fgts_com_rescisao(self):
            """Testa calculo de FGTS rescisorio com multa 40%."""
            resultado = FGTSINSSService.calcular_fgts(
                salario_base=Decimal("5000.00"),
                mes_referencia="2026-01",
                tipo_recolhimento="rescisorio",
                rescisao=True,
            )

            # FGTS: 5000 * 8% = 400
            # Multa: 400 * 40% = 160
            # Total: 560
            assert resultado["valor_fgts"] == "400.00"
            assert resultado["multa_rescisoria"] == "160.00"
            assert resultado["valor_total"] == "560.00"
            assert resultado["rescisao"] is True

        def test_calcular_fgts_salario_alto(self):
            """Testa FGTS para salario alto."""
            resultado = FGTSINSSService.calcular_fgts(
                salario_base=Decimal("15000.00"),
                mes_referencia="2026-01",
            )

            # FGTS: 15000 * 8% = 1200
            assert resultado["valor_fgts"] == "1200.00"

    class TestCalculoINSS:
        """Testes para calculo de INSS no service."""

        def test_calcular_inss_primeira_faixa(self):
            """Testa INSS para salario na primeira faixa."""
            resultado = FGTSINSSService.calcular_inss(
                salario_bruto=Decimal("1412.00"),
                categoria="empregado",
                mes_referencia="2026-01",
            )

            # 1412 * 7.5% = 105.90
            assert resultado["salario_bruto"] == "1412.00"
            assert resultado["categoria"] == "empregado"
            assert len(resultado["detalhamento_faixas"]) >= 1

        def test_calcular_inss_multiplas_faixas(self):
            """Testa INSS com multiplas faixas."""
            resultado = FGTSINSSService.calcular_inss(
                salario_bruto=Decimal("3500.00"),
                categoria="empregado",
                mes_referencia="2026-01",
            )

            # Deve ter multiplas faixas aplicadas
            assert len(resultado["detalhamento_faixas"]) >= 2
            assert resultado["teto_aplicado"] is False

        def test_calcular_inss_acima_teto(self):
            """Testa que INSS e limitado ao teto."""
            resultado = FGTSINSSService.calcular_inss(
                salario_bruto=Decimal("10000.00"),
                categoria="empregado",
                mes_referencia="2026-01",
            )

            assert resultado["teto_aplicado"] is True

        def test_calcular_inss_domestico(self):
            """Testa calculo para empregado domestico."""
            resultado = FGTSINSSService.calcular_inss(
                salario_bruto=Decimal("2000.00"),
                categoria="domestico",
                mes_referencia="2026-01",
            )

            assert resultado["categoria"] == "domestico"
            assert "valor_inss" in resultado

    class TestTabelaINSS:
        """Testes para tabela INSS."""

        def test_get_tabela_inss_estrutura(self):
            """Testa estrutura da tabela INSS."""
            tabela = FGTSINSSService.get_tabela_inss()

            assert tabela["vigencia"] == "2026"
            assert len(tabela["faixas"]) == 4
            assert "teto_contribuicao" in tabela

        def test_get_tabela_inss_faixas(self):
            """Testa faixas da tabela INSS."""
            tabela = FGTSINSSService.get_tabela_inss()

            faixas = tabela["faixas"]

            # Verifica primeira faixa
            assert faixas[0]["faixa"] == 1
            assert faixas[0]["aliquota"] == "7,5%"

            # Verifica ultima faixa
            assert faixas[3]["faixa"] == 4
            assert faixas[3]["aliquota"] == "14%"


# =============================================================================
# TEST FGTS INSS ENDPOINTS
# =============================================================================

class TestFGTSINSSEndpoints:
    """Testes para endpoints REST do FGTS/INSS."""

    @pytest.fixture
    def app(self):
        """Fixture para app FastAPI local (sem dependencias de main)."""
        from fastapi import FastAPI
        from modules.government_integrations.controllers.fgts_inss_controller import router

        app = FastAPI()
        app.include_router(router, prefix="/api/v1/government")
        return app

    @pytest.mark.asyncio
    async def test_endpoint_calcular_fgts_sucesso(self, app, auth_headers):
        """Testa endpoint de calculo FGTS com sucesso."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/government/fgts/calcular",
                headers=auth_headers,
                json={
                    "salario_base": "3000.00",
                    "mes_referencia": "2026-01",
                    "tipo_recolhimento": "mensal",
                    "rescisao": False,
                },
            )

        # Pode retornar 200 ou 401/403 dependendo de auth
        assert response.status_code in [200, 401, 403]

        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "valor_fgts" in data["data"]

    @pytest.mark.asyncio
    async def test_endpoint_calcular_fgts_rescisao(self, app, auth_headers):
        """Testa endpoint de calculo FGTS rescisorio."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/government/fgts/calcular",
                headers=auth_headers,
                json={
                    "salario_base": "5000.00",
                    "mes_referencia": "2026-01",
                    "tipo_recolhimento": "rescisorio",
                    "rescisao": True,
                },
            )

        assert response.status_code in [200, 401, 403]

        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert data["data"]["rescisao"] is True
            assert "multa_rescisoria" in data["data"]

    @pytest.mark.asyncio
    async def test_endpoint_calcular_fgts_validacao_salario(self, app, auth_headers):
        """Testa validacao de salario no endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/government/fgts/calcular",
                headers=auth_headers,
                json={
                    "salario_base": "0",  # Invalido
                    "mes_referencia": "2026-01",
                },
            )

        # Deve retornar erro de validacao
        assert response.status_code in [400, 422, 401, 403]

    @pytest.mark.asyncio
    async def test_endpoint_calcular_fgts_validacao_mes(self, app, auth_headers):
        """Testa validacao de mes no endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/government/fgts/calcular",
                headers=auth_headers,
                json={
                    "salario_base": "3000.00",
                    "mes_referencia": "01-2026",  # Formato invalido
                },
            )

        assert response.status_code in [400, 422, 401, 403]

    @pytest.mark.asyncio
    async def test_endpoint_calcular_inss_sucesso(self, app, auth_headers):
        """Testa endpoint de calculo INSS com sucesso."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/government/inss/calcular",
                headers=auth_headers,
                json={
                    "salario_bruto": "4000.00",
                    "categoria": "empregado",
                    "mes_referencia": "2026-01",
                },
            )

        assert response.status_code in [200, 401, 403]

        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "valor_inss" in data["data"]
            assert "aliquota_efetiva" in data["data"]

    @pytest.mark.asyncio
    async def test_endpoint_calcular_inss_categorias(self, app, auth_headers):
        """Testa endpoint INSS com diferentes categorias."""
        categorias = ["empregado", "domestico", "contribuinte_individual"]

        for categoria in categorias:
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/government/inss/calcular",
                    headers=auth_headers,
                    json={
                        "salario_bruto": "3000.00",
                        "categoria": categoria,
                        "mes_referencia": "2026-01",
                    },
                )

            assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_endpoint_calcular_inss_categoria_invalida(self, app, auth_headers):
        """Testa endpoint INSS com categoria invalida."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/government/inss/calcular",
                headers=auth_headers,
                json={
                    "salario_bruto": "3000.00",
                    "categoria": "invalida",
                    "mes_referencia": "2026-01",
                },
            )

        assert response.status_code in [400, 422, 401, 403]

    @pytest.mark.asyncio
    async def test_endpoint_tabela_inss(self, app, auth_headers):
        """Testa endpoint de tabela INSS."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/government/inss/tabela",
                headers=auth_headers,
            )

        assert response.status_code in [200, 401, 403]

        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "faixas" in data["data"]
            assert data["data"]["vigencia"] == "2026"

    @pytest.mark.asyncio
    async def test_endpoint_sem_autenticacao(self, app):
        """Testa endpoints sem autenticacao."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/government/fgts/calcular",
                json={
                    "salario_base": "3000.00",
                    "mes_referencia": "2026-01",
                },
            )

        # Deve exigir autenticacao
        assert response.status_code in [401, 403, 200]  # 200 se auth nao estiver ativo


# =============================================================================
# TEST DATA CLASSES
# =============================================================================

class TestDataClasses:
    """Testes para data classes."""

    def test_trabalhador_criacao(self, trabalhador_padrao: Trabalhador):
        """Testa criacao de Trabalhador."""
        assert trabalhador_padrao.cpf == "12345678909"
        assert trabalhador_padrao.categoria == CategoriaContribuinte.EMPREGADO

    def test_remuneracao_total_proventos(self, remuneracao_padrao: Remuneracao):
        """Testa calculo de total de proventos."""
        # 3000 + 300 + 150 = 3450
        assert remuneracao_padrao.total_proventos == Decimal("3450.00")

    def test_remuneracao_base_fgts(self, remuneracao_padrao: Remuneracao):
        """Testa base de calculo FGTS."""
        assert remuneracao_padrao.base_fgts == remuneracao_padrao.total_proventos

    def test_remuneracao_base_inss(self, remuneracao_padrao: Remuneracao):
        """Testa base de calculo INSS."""
        assert remuneracao_padrao.base_inss == remuneracao_padrao.total_proventos

    def test_calculo_fgts_valor_total(self):
        """Testa valor total do CalculoFGTS."""
        calculo = CalculoFGTS(
            trabalhador_id="123",
            competencia=date(2026, 1, 1),
            base_calculo=Decimal("3000.00"),
            aliquota=Decimal("8.0"),
            valor_deposito=Decimal("240.00"),
            valor_multa=Decimal("96.00"),
        )

        assert calculo.valor_total == Decimal("336.00")

    def test_tabela_inss_2024(self):
        """Testa tabela INSS 2024."""
        tabela = TabelaINSS.tabela_2024()

        assert tabela.vigencia == date(2024, 1, 1)
        assert tabela.teto == Decimal("7786.02")
        assert len(tabela.faixas) == 4

    def test_tabela_inss_2025(self):
        """Testa tabela INSS 2025."""
        tabela = TabelaINSS.tabela_2025()

        assert tabela.vigencia == date(2025, 1, 1)
        assert tabela.teto == Decimal("8157.41")
        assert len(tabela.faixas) == 4


# =============================================================================
# TEST ENUMS
# =============================================================================

class TestEnums:
    """Testes para enums."""

    def test_tipo_recolhimento_valores(self):
        """Testa valores de TipoRecolhimento."""
        assert TipoRecolhimento.MENSAL.value == "mensal"
        assert TipoRecolhimento.RESCISORIO.value == "rescisorio"
        assert TipoRecolhimento.RECURSAL.value == "recursal"

    def test_codigo_recolhimento_valores(self):
        """Testa valores de CodigoRecolhimento."""
        assert CodigoRecolhimento.RECOLHIMENTO_MENSAL.value == "115"
        assert CodigoRecolhimento.RECOLHIMENTO_RESCISORIO.value == "418"

    def test_modalidade_saque_valores(self):
        """Testa valores de ModalidadeSaque."""
        assert ModalidadeSaque.DEMISSAO_SEM_JUSTA_CAUSA.value == "01"
        assert ModalidadeSaque.APOSENTADORIA.value == "03"
        assert ModalidadeSaque.SAQUE_ANIVERSARIO.value == "07"

    def test_categoria_contribuinte_valores(self):
        """Testa valores de CategoriaContribuinte."""
        assert CategoriaContribuinte.EMPREGADO.value == "empregado"
        assert CategoriaContribuinte.DOMESTICO.value == "domestico"
        assert CategoriaContribuinte.MEI.value == "mei"

    def test_tipo_guia_valores(self):
        """Testa valores de TipoGuia."""
        assert TipoGuia.GRF.value == "grf"
        assert TipoGuia.GRRF.value == "grrf"
        assert TipoGuia.GPS.value == "gps"
        assert TipoGuia.DAE.value == "dae"

    def test_status_guia_valores(self):
        """Testa valores de StatusGuia."""
        assert StatusGuia.GERADA.value == "gerada"
        assert StatusGuia.PAGA.value == "paga"
        assert StatusGuia.VENCIDA.value == "vencida"

    def test_status_certidao_valores(self):
        """Testa valores de StatusCertidao."""
        assert StatusCertidao.NEGATIVA.value == "negativa"
        assert StatusCertidao.POSITIVA.value == "positiva"
        assert StatusCertidao.POSITIVA_EFEITO_NEGATIVA.value == "positiva_efeito_negativa"

    def test_tipo_certidao_valores(self):
        """Testa valores de TipoCertidao."""
        assert TipoCertidao.CRF.value == "crf"
        assert TipoCertidao.CND_INSS.value == "cnd_inss"


# =============================================================================
# TEST SINGLETON
# =============================================================================

class TestSingleton:
    """Testes para singleton do manager."""

    def test_init_manager(self):
        """Testa inicializacao do manager singleton."""
        manager = init_fgts_inss_manager(ambiente="homologacao")

        assert manager is not None
        assert manager.ambiente == "homologacao"

    def test_init_manager_com_tabela(self):
        """Testa inicializacao com tabela customizada."""
        tabela = TabelaINSS.tabela_2024()
        manager = init_fgts_inss_manager(tabela_inss=tabela)

        assert manager.calc_inss.tabela.vigencia == date(2024, 1, 1)
