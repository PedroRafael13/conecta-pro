"""Testes do dashboard_service do Ponto Eletronico — todas funcoes com DB mockado."""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from modules.people_management.ponto.services.dashboard_service import (
    ADICIONAL_NOTURNO_PCT,
    BANCO_HORAS_PRAZO_MESES,
    HORA_EXTRA_50_PCT,
    HORA_EXTRA_100_PCT,
    HORA_NOTURNA_MINUTOS,
    INTRAJORNADA_MINIMA_HORAS,
    JORNADA_MAXIMA_12X36_HORAS,
    get_banco_horas,
    get_colaboradores_sem_escala,
    get_dashboard,
    get_inconsistencias,
    registrar_ajuste,
    sync_solides_ponto,
)

# ========================================================================
# FIXTURES
# ========================================================================


@pytest.fixture
def mock_db():
    """Mock de Session sincrono."""
    db = MagicMock()
    return db


def _mock_execute_factory(values_map: dict):
    """Cria side_effect para db.execute que retorna valores diferentes por query."""
    call_count = [0]

    def side_effect(query, params=None):
        call_count[0] += 1
        result = MagicMock()
        key = call_count[0]
        if key in values_map:
            val = values_map[key]
            if isinstance(val, list):
                result.fetchall.return_value = val
                result.scalar.return_value = len(val)
            elif val is None:
                result.scalar.return_value = None
                result.first.return_value = None
                result.fetchall.return_value = []
            else:
                result.scalar.return_value = val
                result.first.return_value = val
                result.fetchall.return_value = []
        else:
            result.scalar.return_value = 0
            result.first.return_value = None
            result.fetchall.return_value = []
        return result

    return side_effect


# ========================================================================
# CONSTANTES CCT
# ========================================================================


class TestConstantesCCT:
    """Verificar constantes da CCT 2026 SINDECOMPRESTS."""

    def test_hora_noturna(self):
        assert HORA_NOTURNA_MINUTOS == 52.5

    def test_adicional_noturno(self):
        assert ADICIONAL_NOTURNO_PCT == 0.20

    def test_hora_extra_50(self):
        assert HORA_EXTRA_50_PCT == 0.50

    def test_hora_extra_100(self):
        assert HORA_EXTRA_100_PCT == 1.00

    def test_intrajornada_minima(self):
        assert INTRAJORNADA_MINIMA_HORAS == 1.0

    def test_jornada_maxima_12x36(self):
        assert JORNADA_MAXIMA_12X36_HORAS == 12.0

    def test_banco_horas_prazo(self):
        assert BANCO_HORAS_PRAZO_MESES == 6


# ========================================================================
# GET DASHBOARD
# ========================================================================


class TestGetDashboard:
    def test_dashboard_basico(self, mock_db):
        # Setup: total=44, sem_escala=5, presentes=30, em_aberto=3, afastados=2,
        # escalas, ultima_sync, _contar_inconsistencias
        mock_db.execute = MagicMock(
            side_effect=_mock_execute_factory(
                {
                    1: 44,  # total colaboradores
                    2: 5,  # sem escala
                    3: 30,  # presentes hoje
                    4: 3,  # em aberto
                    5: 2,  # afastados
                    6: [("12x36", 20), ("5x2", 15), ("sem_escala", 9)],  # escalas
                    7: None,  # ultima_sync (None)
                    # _contar_inconsistencias faz 2 queries:
                    8: 5,  # sem escala (no contar)
                    9: 3,  # abertos (no contar)
                }
            )
        )

        result = get_dashboard(mock_db)
        assert result["total_colaboradores"] == 44
        assert result["presentes_hoje"] == 30
        assert result["afastados"] == 2
        assert result["sem_escala"] == 5
        assert result["pontos_em_aberto"] == 3
        assert result["ultima_sync_solides"] is None

    def test_dashboard_vazio(self, mock_db):
        mock_db.execute = MagicMock(side_effect=_mock_execute_factory({}))
        result = get_dashboard(mock_db)
        assert result["total_colaboradores"] == 0
        assert result["presentes_hoje"] == 0

    def test_dashboard_com_sync(self, mock_db):
        sync_time = datetime(2026, 3, 13, 10, 0, 0)
        mock_db.execute = MagicMock(
            side_effect=_mock_execute_factory(
                {
                    1: 10,
                    2: 0,
                    3: 8,
                    4: 0,
                    5: 1,
                    6: [],
                    7: sync_time,
                    8: 0,
                    9: 0,
                }
            )
        )
        result = get_dashboard(mock_db)
        assert result["ultima_sync_solides"] == "2026-03-13T10:00:00"


# ========================================================================
# GET INCONSISTENCIAS
# ========================================================================


class TestGetInconsistencias:
    def test_sem_inconsistencias(self, mock_db):
        mock_db.execute = MagicMock(
            side_effect=_mock_execute_factory(
                {
                    1: [],  # sem escala
                    2: [],  # abertos
                    3: [],  # jornadas excedidas
                    4: [],  # intervalos < 1h
                }
            )
        )
        result = get_inconsistencias(mock_db)
        assert result["total_inconsistencias"] == 0
        assert result["items"] == []

    def test_com_sem_escala(self, mock_db):
        mock_db.execute = MagicMock(
            side_effect=_mock_execute_factory(
                {
                    1: [(1, "Joao Silva", "Vigilante")],
                    2: [],
                    3: [],
                    4: [],
                }
            )
        )
        result = get_inconsistencias(mock_db)
        assert result["total_inconsistencias"] == 1
        assert result["items"][0]["tipo"] == "escala_nao_cadastrada"
        assert result["items"][0]["gravidade"] == "alta"

    def test_com_ponto_aberto(self, mock_db):
        mock_db.execute = MagicMock(
            side_effect=_mock_execute_factory(
                {
                    1: [],
                    2: [(1, "2026-03-13")],
                    3: [],
                    4: [],
                }
            )
        )
        result = get_inconsistencias(mock_db)
        assert result["total_inconsistencias"] == 1
        assert result["items"][0]["tipo"] == "ponto_em_aberto"

    def test_com_jornada_excedida(self, mock_db):
        mock_db.execute = MagicMock(
            side_effect=_mock_execute_factory(
                {
                    1: [],
                    2: [],
                    3: [(1, "2026-03-13", 14.5)],
                    4: [],
                }
            )
        )
        result = get_inconsistencias(mock_db)
        assert result["total_inconsistencias"] == 1
        assert result["items"][0]["tipo"] == "jornada_excedida"
        assert "14.5h" in result["items"][0]["descricao"]

    def test_com_intrajornada_curta(self, mock_db):
        mock_db.execute = MagicMock(
            side_effect=_mock_execute_factory(
                {
                    1: [],
                    2: [],
                    3: [],
                    4: [(1, "2026-03-13", 30)],  # 30 min < 60 min
                }
            )
        )
        result = get_inconsistencias(mock_db)
        assert result["total_inconsistencias"] == 1
        assert result["items"][0]["tipo"] == "intrajornada_nao_concedida"

    def test_com_periodo_customizado(self, mock_db):
        mock_db.execute = MagicMock(side_effect=_mock_execute_factory({1: [], 2: [], 3: [], 4: []}))
        result = get_inconsistencias(mock_db, "2026-01-01", "2026-01-31")
        assert result["periodo_inicio"] == "2026-01-01"
        assert result["periodo_fim"] == "2026-01-31"

    def test_sumarizacao_por_tipo_e_gravidade(self, mock_db):
        mock_db.execute = MagicMock(
            side_effect=_mock_execute_factory(
                {
                    1: [(1, "A", "Vig"), (2, "B", "Port")],  # 2 sem escala
                    2: [(3, "2026-03-13")],  # 1 ponto aberto
                    3: [],
                    4: [],
                }
            )
        )
        result = get_inconsistencias(mock_db)
        assert result["total_inconsistencias"] == 3
        assert result["por_tipo"]["escala_nao_cadastrada"] == 2
        assert result["por_tipo"]["ponto_em_aberto"] == 1
        assert result["por_gravidade"]["alta"] == 3


# ========================================================================
# GET BANCO HORAS
# ========================================================================


class TestGetBancoHoras:
    def test_colaborador_nao_encontrado(self, mock_db):
        mock_db.execute = MagicMock(side_effect=_mock_execute_factory({1: None}))
        result = get_banco_horas(mock_db, "999")
        assert "error" in result
        assert "nao encontrado" in result["error"]

    def test_colaborador_sem_horas_extras(self, mock_db):
        call_count = [0]

        def side_effect(query, params=None):
            call_count[0] += 1
            result = MagicMock()
            if call_count[0] == 1:
                result.first.return_value = (1, "Maria Silva")
            else:
                result.scalar.return_value = 0.0
            return result

        mock_db.execute = MagicMock(side_effect=side_effect)

        result = get_banco_horas(mock_db, "1")
        assert result["employee_nome"] == "Maria Silva"
        assert result["saldo_horas"] == 0.0
        assert result["creditos"] == 0.0

    def test_colaborador_com_horas_extras(self, mock_db):
        call_count = [0]

        def side_effect(query, params=None):
            call_count[0] += 1
            result = MagicMock()
            if call_count[0] == 1:
                result.first.return_value = (1, "Pedro Santos")
            else:
                result.scalar.return_value = 12.5
            return result

        mock_db.execute = MagicMock(side_effect=side_effect)

        result = get_banco_horas(mock_db, "1")
        assert result["saldo_horas"] == 12.5
        assert result["creditos"] == 12.5
        assert result["vencimento_proximo"] is not None


# ========================================================================
# COLABORADORES SEM ESCALA
# ========================================================================


class TestColaboradoresSemEscala:
    def test_lista_vazia(self, mock_db):
        mock_db.execute.return_value.fetchall.return_value = []
        result = get_colaboradores_sem_escala(mock_db)
        assert result == []

    def test_com_colaboradores(self, mock_db):
        mock_db.execute.return_value.fetchall.return_value = [
            (1, "Joao", "Vigilante", date(2025, 1, 15)),
            (2, "Maria", "Porteiro", None),
        ]
        result = get_colaboradores_sem_escala(mock_db)
        assert len(result) == 2
        assert result[0]["nome"] == "Joao"
        assert result[0]["data_admissao"] == "2025-01-15"
        assert result[1]["data_admissao"] is None


# ========================================================================
# SYNC SOLIDES
# ========================================================================


class TestSyncSolides:
    def test_sync_sem_token_retorna_stub(self, mock_db):
        """Sem SOLIDES_API_TOKEN configurado, retorna stub com total_importados=0."""
        result_mock = MagicMock()
        result_mock.scalar.return_value = 0
        result_mock.fetchall.return_value = []
        mock_db.execute = MagicMock(return_value=result_mock)

        import os

        os.environ.pop("SOLIDES_API_TOKEN", None)

        result = sync_solides_ponto(mock_db, None, None)
        assert result["success"] is True
        assert result["total_importados"] == 0
        assert "erros" in result

    def test_sync_com_token_chama_api(self, mock_db):
        """Com SOLIDES_API_TOKEN configurado, tenta chamar API Tangerino."""

        result_mock = MagicMock()
        result_mock.scalar.return_value = 0
        result_mock.fetchall.return_value = []
        mock_db.execute = MagicMock(return_value=result_mock)

        with (
            patch.dict("os.environ", {"SOLIDES_API_TOKEN": "fake-token-123"}),
            patch(
                "modules.people_management.ponto.services.dashboard_service._fetch_solides_entities",
                return_value=[],
            ) as mock_fetch,
        ):
            result = sync_solides_ponto(mock_db, "2026-03-01", "2026-03-31")
            assert result["success"] is True
            # Deve ter chamado a API para absences e occurrences
            assert mock_fetch.call_count == 2


# ========================================================================
# REGISTRAR AJUSTE
# ========================================================================


class TestRegistrarAjuste:
    def test_ajuste_basico(self, mock_db):
        ajuste = {
            "employee_id": "emp-1",
            "data": "2026-03-13",
            "punch_type": "entrada",
            "timestamp": "2026-03-13T08:00:00",
            "motivo": "Esqueceu de bater ponto",
            "ajustado_por": "admin-1",
        }
        result = registrar_ajuste(mock_db, ajuste)
        assert result["success"] is True
        assert "punch_id" in result
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
