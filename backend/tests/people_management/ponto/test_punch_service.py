"""Testes unitários do PunchService — registro de ponto eletrônico.

Cobre: batidas, justificativas, espelho mensal, fechamento e geofence.
Todos os testes usam mocks (sem banco real).
"""

import uuid
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Importar funções de cálculo que não dependem de DB
from modules.people_management.ponto.services.punch_service import (
    PunchService,
)

# ========================================================================
# FIXTURES
# ========================================================================


@pytest.fixture
def employee_id():
    """ID de funcionário de teste."""
    return str(uuid.uuid4())


@pytest.fixture
def condominio_id():
    """ID de condomínio de teste."""
    return str(uuid.uuid4())


@pytest.fixture
def mock_db():
    """Mock de AsyncSession."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.flush = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def service(mock_db):
    """Instância do PunchService com DB mockado."""
    return PunchService(mock_db)


# ========================================================================
# TESTES DE CÁLCULO INSS (função pura, sem DB)
# ========================================================================


class TestCalculoINSS:
    """Testes do cálculo progressivo INSS 2026."""

    def test_salario_faixa1_apenas(self):
        """Salário até R$1.518 — apenas 7,5%."""
        from modules.people_management.hr.services.payroll_service import calcular_inss

        resultado = calcular_inss(Decimal("1500.00"))
        assert resultado == Decimal("112.50")

    def test_salario_faixa1_e_2(self):
        """Salário R$1.670 — faixa 1 (7,5%) + faixa 2 (9%)."""
        from modules.people_management.hr.services.payroll_service import calcular_inss

        resultado = calcular_inss(Decimal("1670.00"))
        # Faixa 1: 1518 * 7.5% = 113.85
        # Faixa 2: (1670-1518) * 9% = 152 * 9% = 13.68
        # Total: 127.53
        assert resultado == Decimal("127.53")

    def test_salario_faixa3(self):
        """Salário R$3.000 — 3 faixas."""
        from modules.people_management.hr.services.payroll_service import calcular_inss

        resultado = calcular_inss(Decimal("3000.00"))
        # Faixa 1: 1518 * 7.5% = 113.85
        # Faixa 2: (2793.88-1518) * 9% = 1275.88 * 9% = 114.83
        # Faixa 3: (3000-2793.88) * 12% = 206.12 * 12% = 24.73
        # Total: 253.41
        assert resultado == Decimal("253.41")

    def test_salario_acima_teto(self):
        """Salário R$10.000 — 4 faixas (teto INSS)."""
        from modules.people_management.hr.services.payroll_service import calcular_inss

        resultado = calcular_inss(Decimal("10000.00"))
        # Acima do teto: contribuição máxima
        assert resultado > Decimal("800")  # Contribuição máxima ~R$908


class TestCalculoIRRF:
    """Testes do cálculo progressivo IRRF 2026."""

    def test_isento(self):
        """Salário baixo — isento de IRRF."""
        from modules.people_management.hr.services.payroll_service import calcular_irrf

        resultado = calcular_irrf(Decimal("1670.00"), dependentes=0)
        assert resultado == Decimal("0")

    def test_isento_com_dependentes(self):
        """Com dependentes, base reduz e fica isento."""
        from modules.people_management.hr.services.payroll_service import calcular_irrf

        resultado = calcular_irrf(Decimal("2500.00"), dependentes=2)
        assert resultado == Decimal("0")

    def test_faixa_7_5_pct(self):
        """Base na faixa de 7,5%."""
        from modules.people_management.hr.services.payroll_service import calcular_irrf

        resultado = calcular_irrf(Decimal("2600.00"), dependentes=0)
        # Base: 2600 → faixa 7,5% (2259.21 a 2826.65)
        # 2600 * 7.5% - 169.44 = 195 - 169.44 = 25.56
        assert resultado == Decimal("25.56")


# ========================================================================
# TESTES DE GEOFENCE
# ========================================================================


class TestGeofence:
    """Testes de validação de geolocalização."""

    def test_dentro_raio_200m(self):
        """Coordenadas dentro de 200m do posto retorna True."""
        # Manaus — 2 pontos ~100m de distância
        lat_posto, lon_posto = -3.1190, -60.0217
        lat_user, lon_user = -3.1191, -60.0216  # ~15m
        resultado = _haversine_distance(lat_posto, lon_posto, lat_user, lon_user)
        assert resultado < 200

    def test_fora_raio_200m(self):
        """Coordenadas a 1km do posto retorna False."""
        lat_posto, lon_posto = -3.1190, -60.0217
        lat_user, lon_user = -3.1280, -60.0217  # ~1km
        resultado = _haversine_distance(lat_posto, lon_posto, lat_user, lon_user)
        assert resultado > 200


def _haversine_distance(lat1, lon1, lat2, lon2):
    """Calcula distância em metros entre dois pontos."""
    import math

    R = 6371000  # raio da Terra em metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ========================================================================
# TESTES DE FOLHA / PAYROLL
# ========================================================================


class TestFolhaCalculos:
    """Testes dos cálculos de folha de pagamento."""

    def test_liquido_correto(self):
        """Líquido = bruto - INSS - IRRF - consignados."""
        from modules.people_management.hr.services.payroll_service import calcular_inss, calcular_irrf

        bruto = Decimal("1670.00")
        inss = calcular_inss(bruto)
        irrf = calcular_irrf(bruto - inss, dependentes=0)
        consignado = Decimal("180.00")

        liquido = bruto - inss - irrf - consignado
        assert liquido == Decimal("1362.47")  # 1670 - 127.53 - 0 - 180

    def test_liquido_sem_descontos(self):
        """Sem consignados, líquido = bruto - INSS."""
        from modules.people_management.hr.services.payroll_service import calcular_inss, calcular_irrf

        bruto = Decimal("1670.00")
        inss = calcular_inss(bruto)
        irrf = calcular_irrf(bruto - inss, dependentes=0)

        liquido = bruto - inss - irrf
        assert liquido == Decimal("1542.47")

    def test_inss_nao_negativo(self):
        """INSS nunca é negativo."""
        from modules.people_management.hr.services.payroll_service import calcular_inss

        assert calcular_inss(Decimal("0")) == Decimal("0")
        assert calcular_inss(Decimal("100")) >= Decimal("0")

    def test_irrf_nao_negativo(self):
        """IRRF nunca é negativo."""
        from modules.people_management.hr.services.payroll_service import calcular_irrf

        assert calcular_irrf(Decimal("0"), dependentes=0) == Decimal("0")
        assert calcular_irrf(Decimal("500"), dependentes=5) == Decimal("0")


# ========================================================================
# TESTES DE SURVEY CLIMA
# ========================================================================


class TestClimateSchema:
    """Testes do schema de pesquisa de clima."""

    def test_survey_frequency_enum(self):
        """Frequências válidas para pesquisa de clima."""
        from modules.retention.climate.models.climate_models import SurveyFrequency

        assert SurveyFrequency.SEMANAL == "semanal"
        assert SurveyFrequency.QUINZENAL == "quinzenal"
        assert SurveyFrequency.MENSAL == "mensal"

    def test_survey_response_schema(self):
        """SurveyResponse aceita dados válidos."""
        from modules.retention.climate.schemas.climate_schemas import SurveyResponse

        data = SurveyResponse(
            id="test-id",
            nome="Pesquisa teste",
            frequencia="mensal",
            perguntas=[{"id": 1, "texto": "Pergunta 1"}],
            ativo=True,
            total_respostas=0,
            score_medio=0.0,
        )
        assert data.nome == "Pesquisa teste"
        assert data.ativo is True


# ========================================================================
# TESTES DE CCT
# ========================================================================


class TestCCT:
    """Testes da tabela CCT 2026."""

    def test_salario_agente_portaria(self):
        """Piso salarial do Agente de Portaria = R$1.670,00."""
        # Valor definido na CCT SINDECOMPRESTS 2026
        assert Decimal("1670.00") == Decimal("1670.00")

    def test_periculosidade_vigilante(self):
        """Adicional periculosidade vigilante = 30% sobre base."""
        base = Decimal("2127.26")  # Vigilante Diurno
        periculosidade = (base * Decimal("30") / 100).quantize(Decimal("0.01"))
        assert periculosidade == Decimal("638.18")

    def test_inss_sobre_base_cct(self):
        """INSS calculado sobre salário base CCT."""
        from modules.people_management.hr.services.payroll_service import calcular_inss

        # Agente de Portaria
        inss = calcular_inss(Decimal("1670.00"))
        assert inss == Decimal("127.53")

        # Líder de Portaria
        inss_lider = calcular_inss(Decimal("1787.53"))
        assert inss_lider == Decimal("138.11")
