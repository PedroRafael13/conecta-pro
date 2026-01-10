"""
tests/modules/fase5/test_cct_compliance.py - CCT Compliance Tests
==================================================================
Testes de integracao para CCT Compliance SINDCOND 2026
"""

import pytest
from decimal import Decimal
from uuid import uuid4

from modules.fase5.cct_compliance.service import CCTComplianceService
from modules.fase5.cct_compliance.enums import (
    TipoCargo,
    TipoJornada,
    TipoBeneficio,
    StatusValidacao
)
from modules.fase5.cct_compliance.models import (
    TABELA_PISOS_SINDCOND_2026,
    BENEFICIOS_CCT_2026,
    ValidacaoCCT
)


class TestCCTComplianceService:
    """Testes para CCTComplianceService."""

    @pytest.fixture
    def service(self):
        """Fixture do servico CCT."""
        return CCTComplianceService()

    # =========================================================================
    # Testes de Listagem de Cargos
    # =========================================================================

    def test_listar_cargos_retorna_todos(self, service):
        """Deve listar todos os 35 cargos."""
        cargos = service.listar_cargos()
        assert len(cargos) == 35
        assert all("cargo" in c for c in cargos)
        assert all("piso_salarial" in c for c in cargos)

    def test_listar_cargos_valores_corretos(self, service):
        """Deve retornar valores corretos dos pisos."""
        cargos = service.listar_cargos()
        porteiro = next(c for c in cargos if c["cargo"] == "porteiro")
        assert Decimal(porteiro["piso_salarial"]) == Decimal("1847.12")

    # =========================================================================
    # Testes de Piso Salarial
    # =========================================================================

    def test_obter_piso_porteiro(self, service):
        """Deve retornar piso correto para porteiro."""
        piso = service.obter_piso_salarial(TipoCargo.PORTEIRO)
        assert piso == Decimal("1847.12")

    def test_obter_piso_sindico_profissional(self, service):
        """Deve retornar piso correto para sindico profissional."""
        piso = service.obter_piso_salarial(TipoCargo.SINDICO_PROFISSIONAL)
        assert piso == Decimal("4500.00")

    def test_obter_piso_eletricista(self, service):
        """Deve retornar piso correto para eletricista."""
        piso = service.obter_piso_salarial(TipoCargo.ELETRICISTA)
        assert piso == Decimal("2370.41")

    def test_obter_piso_todos_cargos(self, service):
        """Deve retornar piso para todos os cargos."""
        for cargo in TipoCargo:
            piso = service.obter_piso_salarial(cargo)
            assert piso is not None
            assert piso > Decimal("0")

    # =========================================================================
    # Testes de Validacao de Salario
    # =========================================================================

    def test_validar_salario_conforme(self, service):
        """Salario acima do piso deve ser conforme."""
        resultado = service.validar_salario(
            TipoCargo.PORTEIRO,
            Decimal("2000.00")
        )
        assert resultado["valido"] is True
        assert resultado["alerta"] is None

    def test_validar_salario_nao_conforme(self, service):
        """Salario abaixo do piso deve ser nao conforme."""
        resultado = service.validar_salario(
            TipoCargo.PORTEIRO,
            Decimal("1500.00")
        )
        assert resultado["valido"] is False
        assert "abaixo" in resultado["alerta"].lower()

    def test_validar_salario_igual_piso(self, service):
        """Salario igual ao piso deve ser conforme."""
        piso = service.obter_piso_salarial(TipoCargo.PORTEIRO)
        resultado = service.validar_salario(TipoCargo.PORTEIRO, piso)
        assert resultado["valido"] is True

    def test_validar_salario_diferenca_calculada(self, service):
        """Deve calcular diferenca corretamente."""
        resultado = service.validar_salario(
            TipoCargo.PORTEIRO,
            Decimal("1800.00")
        )
        # Piso: 1847.12, Informado: 1800.00, Diferenca: -47.12
        assert Decimal(resultado["diferenca"]) == Decimal("-47.12")

    # =========================================================================
    # Testes de Validacao Completa
    # =========================================================================

    def test_validar_completo_conforme(self, service):
        """Validacao completa com todos requisitos atendidos."""
        validacao = service.validar_completo(
            cargo=TipoCargo.PORTEIRO,
            salario=Decimal("2000.00"),
            jornada=TipoJornada.JORNADA_44H,
            beneficios=[
                TipoBeneficio.VALE_ALIMENTACAO,
                TipoBeneficio.CESTA_BASICA,
                TipoBeneficio.VALE_TRANSPORTE,
                TipoBeneficio.SEGURO_VIDA
            ]
        )
        assert validacao.salario_conforme is True
        assert validacao.jornada_conforme is True
        assert validacao.beneficios_conformes is True
        assert validacao.status == StatusValidacao.CONFORME

    def test_validar_completo_salario_nao_conforme(self, service):
        """Validacao com salario abaixo do piso."""
        validacao = service.validar_completo(
            cargo=TipoCargo.PORTEIRO,
            salario=Decimal("1500.00"),
            jornada=TipoJornada.JORNADA_44H,
            beneficios=[
                TipoBeneficio.VALE_ALIMENTACAO,
                TipoBeneficio.CESTA_BASICA,
                TipoBeneficio.VALE_TRANSPORTE,
                TipoBeneficio.SEGURO_VIDA
            ]
        )
        assert validacao.salario_conforme is False
        assert validacao.status in [StatusValidacao.NAO_CONFORME, StatusValidacao.ALERTA]

    def test_validar_completo_beneficios_faltantes(self, service):
        """Validacao com beneficios faltantes."""
        validacao = service.validar_completo(
            cargo=TipoCargo.PORTEIRO,
            salario=Decimal("2000.00"),
            jornada=TipoJornada.JORNADA_44H,
            beneficios=[TipoBeneficio.VALE_ALIMENTACAO]  # Faltam outros
        )
        assert validacao.beneficios_conformes is False
        assert len(validacao.beneficios_faltantes) > 0

    def test_validar_completo_score_calculado(self, service):
        """Deve calcular score corretamente."""
        validacao = service.validar_completo(
            cargo=TipoCargo.PORTEIRO,
            salario=Decimal("2000.00"),
            jornada=TipoJornada.JORNADA_44H,
            beneficios=[
                TipoBeneficio.VALE_ALIMENTACAO,
                TipoBeneficio.CESTA_BASICA,
                TipoBeneficio.VALE_TRANSPORTE,
                TipoBeneficio.SEGURO_VIDA
            ]
        )
        # Score maximo: 100 (40 salario + 30 jornada + 30 beneficios)
        assert validacao.score == Decimal("100")

    # =========================================================================
    # Testes de Calculo de Custo
    # =========================================================================

    def test_calcular_custo_com_encargos(self, service):
        """Deve calcular custo total com encargos."""
        resultado = service.calcular_custo_funcionario(
            cargo=TipoCargo.PORTEIRO,
            incluir_encargos=True
        )
        assert "custo_total_mensal" in resultado
        assert "encargos" in resultado
        assert resultado["encargos"]["incluido"] is True
        custo = Decimal(resultado["custo_total_mensal"])
        assert custo > Decimal("1847.12")  # Deve ser maior que o piso

    def test_calcular_custo_sem_encargos(self, service):
        """Deve calcular custo sem encargos."""
        resultado = service.calcular_custo_funcionario(
            cargo=TipoCargo.PORTEIRO,
            incluir_encargos=False
        )
        assert resultado["encargos"]["incluido"] is False

    def test_calcular_custo_salario_customizado(self, service):
        """Deve usar salario customizado quando informado."""
        resultado = service.calcular_custo_funcionario(
            cargo=TipoCargo.PORTEIRO,
            salario_base=Decimal("2500.00"),
            incluir_encargos=True
        )
        assert Decimal(resultado["salario_base"]) == Decimal("2500.00")

    def test_calcular_custo_beneficios_incluidos(self, service):
        """Deve incluir beneficios no calculo."""
        resultado = service.calcular_custo_funcionario(
            cargo=TipoCargo.PORTEIRO,
            incluir_encargos=True
        )
        assert "beneficios" in resultado
        assert Decimal(resultado["beneficios"]["total"]) > Decimal("0")

    def test_calcular_custo_anual(self, service):
        """Deve calcular custo anual corretamente."""
        resultado = service.calcular_custo_funcionario(
            cargo=TipoCargo.PORTEIRO,
            incluir_encargos=True
        )
        mensal = Decimal(resultado["custo_total_mensal"])
        anual = Decimal(resultado["custo_total_anual"])
        assert anual == mensal * 12

    # =========================================================================
    # Testes de Proposta Comercial
    # =========================================================================

    def test_gerar_proposta_simples(self, service):
        """Deve gerar proposta com um cargo."""
        resultado = service.gerar_proposta_comercial(
            cargos=[{"cargo": "porteiro", "quantidade": 2}],
            margem_lucro_percentual=Decimal("15")
        )
        assert "proposta_id" in resultado
        assert "itens" in resultado
        assert "total_mensal" in resultado
        assert "margem_aplicada" in resultado

    def test_gerar_proposta_multiplos_cargos(self, service):
        """Deve gerar proposta com multiplos cargos."""
        resultado = service.gerar_proposta_comercial(
            cargos=[
                {"cargo": "porteiro", "quantidade": 4},
                {"cargo": "zelador", "quantidade": 1},
                {"cargo": "faxineiro", "quantidade": 2}
            ],
            margem_lucro_percentual=Decimal("20")
        )
        assert len(resultado["itens"]) == 3
        assert Decimal(resultado["margem_aplicada"]) == Decimal("20")

    def test_gerar_proposta_margem_aplicada(self, service):
        """Deve aplicar margem de lucro corretamente."""
        resultado = service.gerar_proposta_comercial(
            cargos=[{"cargo": "porteiro", "quantidade": 1}],
            margem_lucro_percentual=Decimal("10")
        )
        custo = Decimal(resultado["custo_total_mensal"])
        preco = Decimal(resultado["total_mensal"])
        margem_esperada = custo * Decimal("0.10")
        assert preco == custo + margem_esperada


class TestTabelaPisos:
    """Testes para tabela de pisos salariais."""

    def test_tabela_tem_35_cargos(self):
        """Tabela deve ter 35 cargos."""
        assert len(TABELA_PISOS_SINDCOND_2026) == 35

    def test_todos_valores_positivos(self):
        """Todos os pisos devem ser positivos."""
        for cargo, piso in TABELA_PISOS_SINDCOND_2026.items():
            assert piso > Decimal("0"), f"Piso de {cargo} deve ser positivo"

    def test_piso_minimo_acima_salario_minimo(self):
        """Todos os pisos devem ser >= salario minimo 2026."""
        salario_minimo_2026 = Decimal("1518.00")
        for cargo, piso in TABELA_PISOS_SINDCOND_2026.items():
            assert piso >= salario_minimo_2026, f"Piso de {cargo} abaixo do minimo"

    def test_cargos_supervisao_maiores(self):
        """Cargos de supervisao devem ter pisos maiores."""
        piso_porteiro = TABELA_PISOS_SINDCOND_2026[TipoCargo.PORTEIRO]
        piso_supervisor = TABELA_PISOS_SINDCOND_2026[TipoCargo.SUPERVISOR_PORTARIA]
        assert piso_supervisor > piso_porteiro


class TestBeneficiosCCT:
    """Testes para beneficios CCT."""

    def test_beneficios_obrigatorios(self):
        """Deve ter 4 beneficios obrigatorios."""
        assert len(BENEFICIOS_CCT_2026) == 4

    def test_vale_alimentacao_valor(self):
        """Vale alimentacao deve ter valor diario correto."""
        va = BENEFICIOS_CCT_2026[TipoBeneficio.VALE_ALIMENTACAO]
        assert va.valor_diario == Decimal("22.00")

    def test_cesta_basica_valor(self):
        """Cesta basica deve ter valor mensal correto."""
        cb = BENEFICIOS_CCT_2026[TipoBeneficio.CESTA_BASICA]
        assert cb.valor_mensal == Decimal("18.00")

    def test_todos_obrigatorios(self):
        """Todos os beneficios devem ser obrigatorios."""
        for beneficio in BENEFICIOS_CCT_2026.values():
            assert beneficio.obrigatorio is True


class TestValidacaoCCT:
    """Testes para modelo ValidacaoCCT."""

    def test_calcular_score_maximo(self):
        """Score maximo deve ser 100."""
        validacao = ValidacaoCCT(
            cargo=TipoCargo.PORTEIRO,
            salario_conforme=True,
            jornada_conforme=True,
            beneficios_conformes=True
        )
        validacao.calcular_score()
        assert validacao.score == Decimal("100")
        assert validacao.status == StatusValidacao.CONFORME

    def test_calcular_score_parcial(self):
        """Score parcial deve refletir itens conformes."""
        validacao = ValidacaoCCT(
            cargo=TipoCargo.PORTEIRO,
            salario_conforme=True,
            jornada_conforme=True,
            beneficios_conformes=False
        )
        validacao.calcular_score()
        assert validacao.score == Decimal("70")  # 40 + 30
        assert validacao.status == StatusValidacao.ALERTA

    def test_calcular_score_minimo(self):
        """Score minimo quando nada conforme."""
        validacao = ValidacaoCCT(
            cargo=TipoCargo.PORTEIRO,
            salario_conforme=False,
            jornada_conforme=False,
            beneficios_conformes=False
        )
        validacao.calcular_score()
        assert validacao.score == Decimal("0")
        assert validacao.status == StatusValidacao.NAO_CONFORME
