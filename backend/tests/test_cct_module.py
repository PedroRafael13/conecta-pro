"""
Testes do modulo CCT 2026 — SINDECOMPRESTS/SINDICOND-AM.

Cobre: tabela salarial, validacoes, beneficios, jornadas, rescisao,
ferias, 13o, feriados, estabilidade, adicionais.
"""

import pytest

# ========================================================================
# TABELA SALARIAL
# ========================================================================


class TestTabelaSalarial:
    """Testes da tabela salarial CCT 2026."""

    def test_tabela_tem_51_cargos(self):
        from modules.cct.models.salary_table import TABELA_SALARIAL_CCT_2026

        assert len(TABELA_SALARIAL_CCT_2026) == 52

    def test_piso_geral(self):
        from decimal import Decimal

        from modules.cct.models.salary_table import SALARIO_PISO

        assert Decimal("1670.00") == SALARIO_PISO

    def test_reajuste_piso(self):
        from decimal import Decimal

        from modules.cct.models.salary_table import REAJUSTE_PISO

        assert Decimal("7.1") == REAJUSTE_PISO

    def test_reajuste_acima_piso(self):
        from decimal import Decimal

        from modules.cct.models.salary_table import REAJUSTE_ACIMA_PISO

        assert Decimal("4.5") == REAJUSTE_ACIMA_PISO

    def test_cargo_administrador(self):
        from decimal import Decimal

        from modules.cct.models.salary_table import get_piso_by_cargo

        entry = get_piso_by_cargo("ADMINISTRADOR (BACHAREL)")
        assert entry is not None
        assert entry.piso == Decimal("5854.04")

    def test_cargo_analista_sistema(self):
        from decimal import Decimal

        from modules.cct.models.salary_table import get_piso_by_cargo

        entry = get_piso_by_cargo("ANALISTA DE SISTEMA")
        assert entry is not None
        assert entry.piso == Decimal("6639.18")

    def test_cargo_porteiro(self):
        from decimal import Decimal

        from modules.cct.models.salary_table import get_piso_by_cargo

        entry = get_piso_by_cargo("PORTEIROS AGENTE DE PORTARIA GUARDETE")
        assert entry is not None
        assert entry.piso == Decimal("1670.00")

    def test_cargo_vigia_com_periculosidade(self):
        from modules.cct.models.salary_table import CargoAdditional, get_piso_by_cargo

        entry = get_piso_by_cargo("VIGIA")
        assert entry is not None
        assert entry.adicional == CargoAdditional.PERICULOSIDADE_30

    def test_cargo_piscineiro_com_insalubridade(self):
        from modules.cct.models.salary_table import CargoAdditional, get_piso_by_cargo

        entry = get_piso_by_cargo("PISCINEIRO")
        assert entry is not None
        assert entry.adicional == CargoAdditional.INSALUBRIDADE_10

    def test_cargo_inexistente(self):
        from modules.cct.models.salary_table import get_piso_by_cargo

        assert get_piso_by_cargo("CARGO INEXISTENTE") is None

    def test_case_insensitive_search(self):
        from modules.cct.models.salary_table import get_piso_by_cargo

        entry = get_piso_by_cargo("vigia")
        assert entry is not None

    def test_get_all_cargos(self):
        from modules.cct.models.salary_table import get_all_cargos

        cargos = get_all_cargos()
        assert len(cargos) == 52
        assert "VIGIA" in cargos

    def test_zelador_residente(self):
        from decimal import Decimal

        from modules.cct.models.salary_table import get_piso_by_cargo

        entry = get_piso_by_cargo("ZELADOR RESIDENTE CONDOMINIOS")
        assert entry is not None
        assert entry.piso == Decimal("2777.46")


# ========================================================================
# VALIDADOR DE SALARIOS
# ========================================================================


class TestSalaryValidator:
    """Testes do validador de salarios."""

    def test_salario_conforme(self):
        from modules.cct.validators.salary_validator import SalaryValidator

        resultado = SalaryValidator.validar_salario("VIGIA", 1700.00)
        assert resultado["conforme"] is True

    def test_salario_abaixo_piso(self):
        from modules.cct.validators.salary_validator import SalaryValidator

        resultado = SalaryValidator.validar_salario("VIGIA", 1500.00)
        assert resultado["conforme"] is False
        assert resultado["alerta"] is not None

    def test_salario_exatamente_no_piso(self):
        from modules.cct.validators.salary_validator import SalaryValidator

        resultado = SalaryValidator.validar_salario("VIGIA", 1670.00)
        assert resultado["conforme"] is True

    def test_salario_cargo_inexistente(self):
        from modules.cct.validators.salary_validator import SalaryValidator

        resultado = SalaryValidator.validar_salario("CARGO FAKE", 5000.00)
        assert resultado["conforme"] is False
        assert "nao encontrado" in resultado["alerta"]

    def test_reajuste_piso(self):
        from modules.cct.validators.salary_validator import SalaryValidator

        resultado = SalaryValidator.calcular_reajuste(1670.00, "VIGIA")
        assert resultado["tipo_reajuste"] == "piso"
        assert resultado["percentual_reajuste"] == 7.1

    def test_reajuste_acima_piso(self):
        from modules.cct.validators.salary_validator import SalaryValidator

        resultado = SalaryValidator.calcular_reajuste(2000.00, "VIGIA")
        assert resultado["tipo_reajuste"] == "acima_do_piso"
        assert resultado["percentual_reajuste"] == 4.5

    def test_reajuste_sem_cargo(self):
        from modules.cct.validators.salary_validator import SalaryValidator

        resultado = SalaryValidator.calcular_reajuste(3000.00)
        assert resultado["tipo_reajuste"] == "acima_do_piso"

    def test_adicional_periculosidade_vigia(self):
        from modules.cct.validators.salary_validator import SalaryValidator

        resultado = SalaryValidator.validar_salario("VIGIA", 1670.00)
        assert resultado["adicional_tipo"] == "periculosidade_30"
        assert resultado["adicional_valor"] == 501.0


# ========================================================================
# BENEFICIOS
# ========================================================================


class TestBenefits:
    """Testes de beneficios CCT."""

    def test_total_beneficios(self):
        from modules.cct.models.benefits import BENEFICIOS_OBRIGATORIOS_CCT

        assert len(BENEFICIOS_OBRIGATORIOS_CCT) == 8

    def test_obrigatorios(self):
        from modules.cct.models.benefits import get_beneficios_obrigatorios

        obrig = get_beneficios_obrigatorios()
        assert len(obrig) == 6

    def test_vr_valor_minimo(self):
        from decimal import Decimal

        from modules.cct.models.benefits import TipoBeneficioCCT, get_beneficio_by_tipo

        vr = get_beneficio_by_tipo(TipoBeneficioCCT.VALE_REFEICAO)
        assert vr is not None
        assert vr.valor_total == Decimal("22.00")

    def test_seguro_vida_valores(self):
        from decimal import Decimal

        from modules.cct.models.benefits import TipoBeneficioCCT, get_beneficio_by_tipo

        sv = get_beneficio_by_tipo(TipoBeneficioCCT.SEGURO_VIDA)
        assert sv is not None
        assert sv.valor_total == Decimal("6.00")
        assert sv.valor_empresa == Decimal("4.00")
        assert sv.desconto_maximo_empregado == Decimal("2.00")

    def test_taxa_negocial(self):
        from decimal import Decimal

        from modules.cct.models.benefits import TAXA_NEGOCIAL_2026

        assert TAXA_NEGOCIAL_2026.valor == Decimal("22.00")
        assert TAXA_NEGOCIAL_2026.meses == (1, 3, 5, 7, 9, 11)
        assert TAXA_NEGOCIAL_2026.prazo_oposicao_dia == 20


# ========================================================================
# VALIDADOR DE BENEFICIOS
# ========================================================================


class TestBenefitsValidator:
    """Testes do validador de beneficios."""

    def test_todos_beneficios_presentes(self):
        from modules.cct.validators.benefits_validator import BenefitsValidator

        resultado = BenefitsValidator.validar_beneficios(
            employee_id="test-id",
            salario_base=1670.00,
            beneficios_ativos=[
                "vale_transporte",
                "vale_refeicao",
                "plano_odontologico",
                "seguro_vida",
                "auxilio_funeral",
                "ajuda_medicamento",
            ],
        )
        assert resultado["conforme"] is True
        assert resultado["faltantes"] == 0

    def test_beneficio_faltante(self):
        from modules.cct.validators.benefits_validator import BenefitsValidator

        resultado = BenefitsValidator.validar_beneficios(
            employee_id="test-id",
            salario_base=1670.00,
            beneficios_ativos=["vale_transporte"],
        )
        assert resultado["conforme"] is False
        assert resultado["faltantes"] > 0

    def test_vr_abaixo_minimo(self):
        from modules.cct.validators.benefits_validator import BenefitsValidator

        resultado = BenefitsValidator.validar_beneficios(
            employee_id="test-id",
            salario_base=1670.00,
            beneficios_ativos=[
                "vale_transporte",
                "vale_refeicao",
                "plano_odontologico",
                "seguro_vida",
                "auxilio_funeral",
                "ajuda_medicamento",
            ],
            valor_vr_dia=15.00,
        )
        assert resultado["conforme"] is False

    def test_taxa_negocial_mes_janeiro(self):
        from modules.cct.validators.benefits_validator import BenefitsValidator

        resultado = BenefitsValidator.verificar_taxa_negocial(mes=1)
        assert resultado["mes_atual_aplicavel"] is True

    def test_taxa_negocial_mes_fevereiro(self):
        from modules.cct.validators.benefits_validator import BenefitsValidator

        resultado = BenefitsValidator.verificar_taxa_negocial(mes=2)
        assert resultado["mes_atual_aplicavel"] is False


# ========================================================================
# JORNADAS
# ========================================================================


class TestSchedule:
    """Testes de jornadas CCT."""

    def test_jornadas_permitidas(self):
        from modules.cct.models.schedule import JORNADAS_PERMITIDAS

        assert len(JORNADAS_PERMITIDAS) == 3

    def test_jornada_12x36_divisor_180(self):
        from modules.cct.models.schedule import TipoJornadaCCT, get_divisor_mensal

        assert get_divisor_mensal(TipoJornadaCCT.ESCALA_12X36) == 180

    def test_jornada_44h_divisor_220(self):
        from modules.cct.models.schedule import TipoJornadaCCT, get_divisor_mensal

        assert get_divisor_mensal(TipoJornadaCCT.PADRAO_44H) == 220

    def test_adicionais_constantes(self):
        from decimal import Decimal

        from modules.cct.models.schedule import ADICIONAIS

        assert ADICIONAIS.hora_noturna_minutos == Decimal("52.5")
        assert ADICIONAIS.adicional_noturno_percentual == Decimal("20.0")
        assert ADICIONAIS.hora_extra_normal_percentual == Decimal("50.0")
        assert ADICIONAIS.hora_extra_feriado_percentual == Decimal("100.0")
        assert ADICIONAIS.ronda_permanente_percentual == Decimal("15.0")
        assert ADICIONAIS.ronda_permanente_pre_2020_percentual == Decimal("30.0")
        assert ADICIONAIS.acumulo_funcao_percentual == Decimal("30.0")
        assert ADICIONAIS.periculosidade_percentual == Decimal("30.0")
        assert ADICIONAIS.insalubridade_minimo_percentual == Decimal("10.0")


# ========================================================================
# VALIDADOR DE JORNADA
# ========================================================================


class TestScheduleValidator:
    """Testes do validador de jornada."""

    def test_jornada_12x36_valida(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.validar_jornada("12x36", 36)
        assert resultado["conforme"] is True
        assert resultado["divisor_mensal"] == 180

    def test_jornada_44h_valida(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.validar_jornada("44h_semanais", 44)
        assert resultado["conforme"] is True

    def test_jornada_carga_excedente(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.validar_jornada("44h_semanais", 48)
        assert resultado["conforme"] is False

    def test_escala_2x1_proibida(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.validar_jornada("2x1", 36)
        assert resultado["conforme"] is False
        assert any("PROIBIDA" in a for a in resultado["alertas"])

    def test_hora_extra_normal(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.calcular_hora_extra(
            salario_base=1670.00,
            jornada_tipo="12x36",
            horas_extras_normais=10,
            horas_extras_feriado=0,
        )
        assert resultado["divisor_mensal"] == 180
        hora_normal = round(1670.00 / 180, 2)
        assert resultado["valor_hora_normal"] == hora_normal
        assert resultado["total_horas_extras_normais"] == round(10 * hora_normal * 1.5, 2)

    def test_hora_extra_feriado_100(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.calcular_hora_extra(
            salario_base=1670.00,
            jornada_tipo="12x36",
            horas_extras_normais=0,
            horas_extras_feriado=8,
        )
        hora_normal = round(1670.00 / 180, 2)
        assert resultado["total_horas_extras_feriado"] == round(8 * hora_normal * 2.0, 2)

    def test_intrajornada_nao_concedida(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.calcular_hora_extra(
            salario_base=1670.00,
            jornada_tipo="12x36",
            intrajornada_nao_concedida=True,
        )
        assert resultado["valor_intrajornada"] > 0

    def test_adicional_noturno_hora_reduzida(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.calcular_adicional_noturno(
            salario_base=1670.00,
            jornada_tipo="12x36",
            horas_noturnas=7,
        )
        assert resultado["hora_noturna_minutos"] == 52.5
        assert resultado["horas_noturnas_reduzidas"] > 7  # hora reduzida gera mais horas
        assert resultado["valor_adicional_noturno"] > 0

    def test_adicionais_ronda_permanente(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.calcular_adicionais(
            salario_base=1670.00,
            ronda_permanente=True,
        )
        assert resultado["adicional_ronda"] == round(1670.00 * 0.15, 2)

    def test_adicionais_ronda_pre_2020(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.calcular_adicionais(
            salario_base=1670.00,
            ronda_permanente=True,
            ronda_pre_2020=True,
        )
        assert resultado["adicional_ronda"] == round(1670.00 * 0.30, 2)

    def test_adicionais_periculosidade(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.calcular_adicionais(
            salario_base=1670.00,
            periculosidade=True,
        )
        assert resultado["adicional_periculosidade"] == round(1670.00 * 0.30, 2)

    def test_adicionais_insalubridade(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.calcular_adicionais(
            salario_base=2000.00,
            insalubridade=True,
        )
        assert resultado["adicional_insalubridade"] == round(1670.00 * 0.10, 2)

    def test_adicionais_acumulo_funcao(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.calcular_adicionais(
            salario_base=1670.00,
            acumulo_funcao=True,
        )
        assert resultado["adicional_acumulo_funcao"] == round(1670.00 * 0.30, 2)

    def test_adicionais_jardinagem_piscina(self):
        from modules.cct.validators.schedule_validator import ScheduleValidator

        resultado = ScheduleValidator.calcular_adicionais(
            salario_base=1670.00,
            servicos_jardinagem_piscina=True,
        )
        assert resultado["adicional_jardinagem_piscina"] == round(1670.00 * 0.10, 2)


# ========================================================================
# RESCISAO
# ========================================================================


class TestTerminationValidator:
    """Testes do validador de rescisao."""

    def test_homologacao_obrigatoria_mais_1_ano(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.validar_rescisao(
            employee_id="test-id",
            data_admissao="2024-01-01",
            data_demissao="2026-03-15",
            salario_base=1670.00,
            motivo="sem_justa_causa",
        )
        assert resultado["homologacao_obrigatoria"] is True
        assert "SINDECOMPRESTS" in resultado["sindicato_homologacao"]

    def test_sem_homologacao_menos_1_ano(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.validar_rescisao(
            employee_id="test-id",
            data_admissao="2025-06-01",
            data_demissao="2026-03-15",
            salario_base=1670.00,
            motivo="sem_justa_causa",
        )
        assert resultado["homologacao_obrigatoria"] is False

    def test_prazo_pagamento_10_dias(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.validar_rescisao(
            employee_id="test-id",
            data_admissao="2024-01-01",
            data_demissao="2026-03-15",
            salario_base=1670.00,
            motivo="sem_justa_causa",
        )
        assert resultado["prazo_pagamento_dias"] == 10

    def test_multa_demissao_pre_database(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.validar_rescisao(
            employee_id="test-id",
            data_admissao="2024-01-01",
            data_demissao="2026-12-10",
            salario_base=2000.00,
            motivo="sem_justa_causa",
        )
        assert resultado["multa_demissao_pre_database"] == 2000.00


# ========================================================================
# FERIAS
# ========================================================================


class TestVacation:
    """Testes de ferias proporcionais CCT."""

    def test_ferias_0_faltas_30_dias(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.calcular_ferias_proporcionais(
            salario_base=1670.00,
            faltas_periodo=0,
            meses_trabalhados=12,
        )
        assert resultado["dias_direito"] == 30

    def test_ferias_6_faltas_24_dias(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.calcular_ferias_proporcionais(
            salario_base=1670.00,
            faltas_periodo=6,
            meses_trabalhados=12,
        )
        assert resultado["dias_direito"] == 24

    def test_ferias_15_faltas_18_dias(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.calcular_ferias_proporcionais(
            salario_base=1670.00,
            faltas_periodo=15,
            meses_trabalhados=12,
        )
        assert resultado["dias_direito"] == 18

    def test_ferias_24_faltas_12_dias(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.calcular_ferias_proporcionais(
            salario_base=1670.00,
            faltas_periodo=24,
            meses_trabalhados=12,
        )
        assert resultado["dias_direito"] == 12

    def test_ferias_33_faltas_sem_direito(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.calcular_ferias_proporcionais(
            salario_base=1670.00,
            faltas_periodo=33,
            meses_trabalhados=12,
        )
        assert resultado["dias_direito"] == 0

    def test_ferias_proporcional_6_meses(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.calcular_ferias_proporcionais(
            salario_base=1670.00,
            faltas_periodo=0,
            meses_trabalhados=6,
        )
        assert resultado["dias_proporcionais"] == 15.0

    def test_terco_constitucional(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.calcular_ferias_proporcionais(
            salario_base=1670.00,
            faltas_periodo=0,
            meses_trabalhados=12,
        )
        assert resultado["terco_constitucional"] == round(resultado["valor_ferias"] / 3, 2)


# ========================================================================
# 13o SALARIO
# ========================================================================


class TestThirteenthSalary:
    """Testes do 13o salario."""

    def test_13_integral(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.calcular_decimo_terceiro(
            salario_base=1670.00,
            meses_trabalhados=12,
        )
        assert resultado["valor_proporcional"] == 1670.00
        assert resultado["primeira_parcela"] == round(1670.00 / 2, 2)

    def test_13_proporcional_6_meses(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.calcular_decimo_terceiro(
            salario_base=1670.00,
            meses_trabalhados=6,
        )
        assert resultado["valor_proporcional"] == round(1670.00 * 6 / 12, 2)

    def test_13_com_adicionais(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.calcular_decimo_terceiro(
            salario_base=1670.00,
            meses_trabalhados=12,
            adicionais_mensais=500.00,
        )
        assert resultado["valor_proporcional"] == 2170.00

    def test_prazo_segunda_parcela(self):
        from modules.cct.validators.termination_validator import TerminationValidator

        resultado = TerminationValidator.calcular_decimo_terceiro(
            salario_base=1670.00,
            meses_trabalhados=12,
        )
        assert "20 de dezembro" in resultado["prazo_segunda_parcela"]


# ========================================================================
# FERIADOS
# ========================================================================


class TestFeriados:
    """Testes dos feriados Manaus/AM 2026."""

    def test_total_16_feriados(self):
        from modules.cct.models.holidays import FERIADOS_MANAUS_2026

        assert len(FERIADOS_MANAUS_2026) == 16

    def test_ano_novo(self):
        from datetime import date

        from modules.cct.models.holidays import is_feriado

        f = is_feriado(date(2026, 1, 1))
        assert f is not None
        assert f.nome == "Confraternizacao Universal"

    def test_aniversario_manaus(self):
        from datetime import date

        from modules.cct.models.holidays import is_feriado

        f = is_feriado(date(2026, 10, 24))
        assert f is not None
        assert f.tipo == "municipal"

    def test_elevacao_amazonas(self):
        from datetime import date

        from modules.cct.models.holidays import is_feriado

        f = is_feriado(date(2026, 9, 5))
        assert f is not None
        assert f.tipo == "estadual"

    def test_dia_normal(self):
        from datetime import date

        from modules.cct.models.holidays import is_feriado

        assert is_feriado(date(2026, 3, 15)) is None

    def test_feriados_mes_dezembro(self):
        from modules.cct.models.holidays import get_feriados_mes

        feriados = get_feriados_mes(12)
        assert len(feriados) == 2  # 08/dez (AM) + 25/dez

    def test_consciencia_negra(self):
        from datetime import date

        from modules.cct.models.holidays import is_feriado

        f = is_feriado(date(2026, 11, 20))
        assert f is not None
        assert f.tipo == "municipal"


# ========================================================================
# ESTABILIDADE
# ========================================================================


class TestStability:
    """Testes do validador de estabilidade."""

    def test_gestante_estavel(self):
        from modules.cct.validators.stability_validator import StabilityValidator

        resultado = StabilityValidator.verificar_estabilidade(
            employee_id="test-id",
            data_admissao="2024-01-01",
            gestante=True,
        )
        assert resultado["estavel"] is True
        assert any("Gestante" in m for m in resultado["motivos"])

    def test_acidente_trabalho_estavel(self):
        from modules.cct.validators.stability_validator import StabilityValidator

        resultado = StabilityValidator.verificar_estabilidade(
            employee_id="test-id",
            data_admissao="2024-01-01",
            acidente_trabalho=True,
            data_alta_inss="2026-01-01",
        )
        assert resultado["estavel"] is True

    def test_sem_estabilidade(self):
        from modules.cct.validators.stability_validator import StabilityValidator

        resultado = StabilityValidator.verificar_estabilidade(
            employee_id="test-id",
            data_admissao="2025-01-01",
        )
        assert resultado["estavel"] is False


# ========================================================================
# METADATA CCT
# ========================================================================


class TestMetadata:
    """Testes dos metadados da CCT."""

    def test_registro_mte(self):
        from modules.cct.models.cct_metadata import CCT_METADATA

        assert CCT_METADATA.registro_mte == "AM000613/2025"

    def test_sindicato_laboral(self):
        from modules.cct.models.cct_metadata import CCT_METADATA

        assert CCT_METADATA.sindicato_laboral == "SINDECOMPRESTS"
        assert CCT_METADATA.sindicato_laboral_cnpj == "00.444.514/0001-36"

    def test_sindicato_patronal(self):
        from modules.cct.models.cct_metadata import CCT_METADATA

        assert CCT_METADATA.sindicato_patronal == "SINDICOND-AM"
        assert CCT_METADATA.sindicato_patronal_cnpj == "52.753.671/0001-27"

    def test_vigencia(self):
        from modules.cct.models.cct_metadata import CCT_METADATA

        assert CCT_METADATA.vigencia_inicio == "2026-01-01"
        assert CCT_METADATA.vigencia_fim == "2026-12-31"
